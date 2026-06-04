# FB_IotMqttMessage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT3` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392642699.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqttMessage.TcPOU`](../examples/P_Demo_FB_IotMqttMessage.TcPOU) |

---

## 1. 功能简述

`FB_IotMqttMessage` 是 MQTT 3.1.1 客户端**收到的一条消息**的容器功能块（FB）。

不直接实例化使用——而是声明一个 `FB_IotMqttMessage` 类型的局部变量，传给 `FB_IotMqttMessageQueue.Dequeue(fbMessage := fbMsg)`，由队列把消息内容填进该实例；接着用 `GetTopic()` / `GetPayload()` / `CompareTopic()` 等方法读出 topic 与 payload。

属性区暴露 `eQoS` / `nPayloadSize` / `nTopicSize` 直接可读；方法区做拷贝和比对。

## 2. 接口定义

本 FB 没有 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；交互全部通过 **Property** 和 **Method**。

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### Property（只读属性）

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `eQoS` | `TcIotMqttQos` | Get | 该消息的 QoS（broker 实际投递时使用的等级，不一定等于发布者声明的） |
| `nPayloadSize` | `UDINT` | Get | payload 字节数 |
| `nTopicSize` | `UINT` | Get | topic 字节数 |

### METHOD CompareTopic

判断本消息的 topic 是否与传入字符串相等（大小写敏感）。

```iecst
METHOD CompareTopic : BOOL
VAR_IN_OUT CONSTANT
    sTopic : STRING; // topic string with any length (attend that MQTT topics are case sensitive)
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT CONSTANT | `STRING` | 期望比对的 topic 字符串 |

返回值：`BOOL`——`TRUE` 表示 topic 完全相等。

### METHOD GetTopic

把消息的 topic 拷贝到调用方提供的 STRING 缓冲。

```iecst
METHOD GetTopic : BOOL
VAR_INPUT
    pTopic     : POINTER TO STRING; // topic buffer
    nTopicSize : UINT; // maximum size of topic buffer in bytes
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pTopic` | `POINTER TO STRING` | 目标缓冲起始地址（`ADR(sLocalTopic)`） |
| `nTopicSize` | `UINT` | 缓冲最大字节数（`SIZEOF(sLocalTopic)`） |

返回值：`BOOL`——`TRUE` 表示拷贝成功。

### METHOD GetPayload

把 payload 拷贝到调用方提供的内存缓冲。

```iecst
METHOD GetPayload : BOOL
VAR_INPUT
    pPayload           : PVOID; // payload buffer
    nPayloadSize       : UDINT; // maximum size of payload buffer in bytes
    bSetNullTermination: BOOL; // The publisher specifies the kind of payload. If it is a string, it could be null terminated or not. Setting this input to TRUE will force a null termination. One more byte is required for that.
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pPayload` | `PVOID` | 目标缓冲起始地址 |
| `nPayloadSize` | `UDINT` | 缓冲最大字节数 |
| `bSetNullTermination` | `BOOL` | `TRUE` 时拷贝完追加一个 `\0`（缓冲必须比 `nPayloadSize` 多预留 1 字节）。用于把 payload 当 C 字符串处理 |

返回值：`BOOL`——`TRUE` 表示拷贝成功。

## 3. 行为说明

**典型使用流**：① 在 PROGRAM 里声明 `fbMsg : FB_IotMqttMessage;`；② 业务出队循环里 `fbQueue.Dequeue(fbMessage := fbMsg)`——成功则 `fbMsg` 当前持有刚出队的消息；③ 立即用 `fbMsg.CompareTopic(sTopic := sExpected)` 分发，或用 `fbMsg.GetTopic(...)` 拷出 topic 字符串看；④ 用 `fbMsg.GetPayload(...)` 拷 payload，根据 `nPayloadSize` 决定怎么解析。

**寿命短**：`fbMsg` 的内容**只在本次 `Dequeue()` 后到下次 `Dequeue()` 之间有效**。下一次出队会把 `fbMsg` 内部重新初始化覆盖。业务侧必须当周期就拷走想要的内容。

**`bSetNullTermination` 的两种语义**：① payload 是 UTF-8 字符串且发布者已加 `\0`——`bSetNullTermination := FALSE` + 缓冲大小恰好 `nPayloadSize`；② payload 不带 `\0`（C 字符串习惯但 publisher 是裸字节）——`bSetNullTermination := TRUE`，本方法替它补 `\0`，缓冲必须 ≥ `nPayloadSize + 1`。多数 publisher 不会主动 null-terminate，所以**保险做法是开 `TRUE` 加 1 字节缓冲**。

**`CompareTopic` vs `GetTopic + 字符串比较`**：`CompareTopic()` 更高效——内部直接比对内存而不拷贝；只有不知道期望 topic 时才用 `GetTopic` 拷出来。

**`eQoS` 的来源**：是 broker 实际投递时使用的 QoS。MQTT 协议规定订阅者的 `eQoS` 是"最大可接受值"，broker 用 min(publisher_qos, subscriber_qos) 实际投递。所以这里读到的可能比 `Subscribe()` 时声明的低。

**多 topic 分发模式**：建议先用 `CompareTopic(sTopic := <精确串>)` 走最常见的几条 topic 分支；都不匹配时再 `GetTopic()` 拷出来用 `FB_StringFind` 等做通配/正则匹配。

## 4. 错误码 / 返回值

各方法以 `BOOL` 返回成功/失败：

| 方法 | `TRUE` 含义 | `FALSE` 含义 |
|---|---|---|
| `CompareTopic()` | topic 完全相等 | topic 不同 / 输入串无效 |
| `GetTopic()` | 拷贝成功 | 缓冲不够 / 内部错 |
| `GetPayload()` | 拷贝成功 | 缓冲不够 / 内部错 |

属性 Get 不可能失败，直接返回最新值。

## 5. 使用注意 / 常见坑

- **`fbMsg` 不能跨周期保留内容**：下一次 `Dequeue()` 会覆盖。要保留就立刻 `GetTopic()` / `GetPayload()` 拷出来。
- **缓冲必须够大**：`STRING(80)` 接 100 字节 topic 会被截。安全的做法是 `STRING(255)` 接 topic、按业务最大 payload 估缓冲（10 KB 以上推荐放全局 `ARRAY[1..N] OF BYTE`）。
- **`GetTopic(nTopicSize := SIZEOF(s))` 而不是 `LEN(s)`**：`SIZEOF` 给出整段缓冲，`LEN` 只算到 `\0` 前——刚声明的空字符串 `LEN` 是 0，会让 `GetTopic` 写 0 字节后返回 `FALSE`。
- **`bSetNullTermination := TRUE` + 缓冲长度要 +1**：忘加 1 字节会让 `\0` 写到下一变量里腐蚀内存。（工程经验补充）
- **不要直接读 `eQoS` 当 publisher 声明**：那是 broker 投递时的实际 QoS，不一定等于 publisher 原始 QoS。
- **`CompareTopic` 大小写敏感**：`'plc/Heartbeat'` 和 `'plc/heartbeat'` 是两条不同 topic（MQTT 协议规定）。
- **payload 非 UTF-8 字符串的处理**：若 payload 是二进制（如 Protobuf / 自定义结构体），用 `pPayload := ADR(stRecv)` 直接拷进结构体；不要尝试 STRING 转换。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqttMessage.TcPOU`](../examples/P_Demo_FB_IotMqttMessage.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示 Dequeue 后用 CompareTopic 分发、GetPayload 拷字符串
PROGRAM P_Demo_FB_IotMqttMessage
VAR
    fbMqtt   : FB_IotMqttClient;
    fbQueue  : FB_IotMqttMessageQueue;
    fbMsg    : FB_IotMqttMessage;
    sCmdTopic: STRING := 'plc/cmd';
    sPayload : STRING(255);
END_VAR
fbMqtt.ipMessageQueue := fbQueue;
fbMqtt.Execute(bConnect := TRUE);
WHILE fbQueue.nQueuedMessages > 0 DO
    IF NOT fbQueue.Dequeue(fbMessage := fbMsg) THEN EXIT; END_IF
    IF fbMsg.CompareTopic(sTopic := sCmdTopic) THEN
        fbMsg.GetPayload(pPayload := ADR(sPayload),
                         nPayloadSize := SIZEOF(sPayload),
                         bSetNullTermination := TRUE);
        // sPayload 现在含命令字串，做业务判定
    END_IF
END_WHILE
```

## 7. 业务场景与实际价值

- **场景**：PLC 订阅 MES 下发命令的 topic `factory/line1/cmd`，每条命令是简短 ASCII 串（"START" / "STOP" / "PAUSE" / "RESET"）；同时订阅一个二进制配方下发 topic 携带 JSON 或 Protobuf。一个 FB 用于命令解析、另一个用于配方解析，按 topic 分发。
- **价值**：在队列模式下用本 FB 作"消息访问 API"——CompareTopic 做 topic 路由（O(1) 内存比较）、GetPayload 用一次 `ADR + SIZEOF` 拷到自己缓冲。业务代码看起来跟"普通对象方法调用"完全一致，不用碰任何 MQTT 协议字段。
- **替代方案对比**：
  - 自己维护 ARRAY[STRING] + ARRAY[POINTER]——要管理消息生命周期、内存释放、并发，容易出错；
  - 重写 `OnMqttMessage()` 回调——直接拿到 PVOID + UDINT，但回调上下文不能做长耗时操作；
  - **本 FB**：和队列联用——业务侧周期拉、按 topic 分发，干净直接。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392642699.html
- **相关 FB / GVL**：`FB_IotMqttMessageQueue`（产出本 FB 实例的 FIFO）、`FB_IotMqttClient`（消息来源）、`FB_IotMqtt5Message`（MQTT 5 版本，多了 UserProperty / Subscription ID / Correlation Data 等属性）
