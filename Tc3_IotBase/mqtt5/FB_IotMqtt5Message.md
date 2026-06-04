# FB_IotMqtt5Message

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/14629604107.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5Message.TcPOU`](../examples/P_Demo_FB_IotMqtt5Message.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5Message` 是 MQTT 5 客户端**收到的一条消息**的容器功能块（FB）。与 MQTT 3 版本 `FB_IotMqttMessage` 相比多了**所有 MQTT 5 properties** 的访问能力：
- `bPayloadUtf8` / `bTopicAlias` / `nMsgExpiryInterval` / `nSubIdCnt` / `sContentType` 等 publish properties；
- `nUserPropertyCnt` + `GetUserPropertyByIdx()` / `GetUserPropertyValueByName()` 访问 user properties；
- `nCorrelationDataSize` + `GetCorrelationData()` 访问 correlation data（请求响应配对用）；
- `GetResponseTopic()` 拿到 broker 转发请求里的 response topic（请求响应模式接收方用）；
- `GetContentType()` 拿到完整 content type 字符串（property 缓冲不够时用）；
- `GetSubIds()` 拿到 subscription identifiers（高级订阅路由用）。

使用模式与 MQTT 3 版本一致：声明 `fbMsg5 : FB_IotMqtt5Message;` 局部变量，传给 `fbClient.fbMessageQueue.Dequeue(fbMessage := fbMsg5)`，再用方法读出内容。

## 2. 接口定义

本 FB 没有 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；交互通过 **Property** 和 **Method**。

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### Property（只读属性）

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `bPayloadUtf8` | `BOOL` | Get | `TRUE` 表示 payload 是 UTF-8 文本（publisher 在 PublishProperties 里声明的） |
| `bTopicAlias` | `BOOL` | Get | `TRUE` 表示本消息走 topic alias 收发（数字代号代替长字符串 topic） |
| `eQoS` | `TcIotMqttQos` | Get | 投递 QoS（broker 实际投递使用的等级） |
| `nCorrelationDataSize` | `UINT` | Get | correlation data 字节数（请求响应模式） |
| `nMsgExpiryInterval` | `UDINT` | Get | 消息过期时间（秒）——超过则 broker 不再转发 |
| `nPayloadSize` | `UDINT` | Get | payload 字节数 |
| `nSubIdCnt` | `UINT` | Get | 本消息匹配到的 subscription identifier 数量 |
| `nUserPropertyCnt` | `UINT` | Get | user properties 个数 |
| `nUserPropertyCntLost` | `UINT` | Get | 因接收时超限丢弃的 user properties 数 |
| `nTopicSize` | `UINT` | Get | topic 字节数 |
| `sContentType` | `STRING` | Get | content type（如 `'application/json'`）；过长时用 `GetContentType()` 取完整版 |

### METHOD CompareTopic

判断 topic 是否相等。

```iecst
METHOD CompareTopic : BOOL
VAR_IN_OUT CONSTANT
    sTopic : STRING; // topic string with any length (attend that MQTT topics are case sensitive)
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT CONSTANT | `STRING` | 期望比对的 topic 字符串 |

返回值：`BOOL`——topic 完全相等。

### METHOD GetTopic

把消息 topic 拷贝到调用方缓冲。

```iecst
METHOD GetTopic : BOOL
VAR_INPUT
    pTopic     : POINTER TO STRING; // topic buffer
    nTopicSize : UINT; // maximum size of topic buffer in bytes
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pTopic` | `POINTER TO STRING` | 目标缓冲起始地址 |
| `nTopicSize` | `UINT` | 缓冲最大字节数 |

返回值：`BOOL`。

### METHOD GetPayload

把 payload 拷贝到调用方缓冲。

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
| `bSetNullTermination` | `BOOL` | `TRUE` 时拷贝完追加 `\0`（缓冲必须比 `nPayloadSize` 多 1） |

返回值：`BOOL`。

### 其他方法（PDF 列在 Methods 表里，签名详见 InfoSys）

| 方法 | 用途 |
|---|---|
| `GetContentType()` | 取完整 content type 字符串 |
| `GetCorrelationData()` | 取 correlation data 字节数组 |
| `GetResponseTopic()` | 取 response topic（请求响应模式接收方用） |
| `GetSubIds()` | 取本消息匹配到的 subscription identifier 列表 |
| `GetUserPropertyByIdx()` | 按 index 取 user property 的 name + value |
| `GetUserPropertyValueByName()` | 按 name 取 user property 的 value |

InfoSys 未提供 PDF §5.1.2.8 之外这些方法的完整签名详情；PDF 表格只列了 "用途"。需要具体签名时查 InfoSys topic 14629604107 或 PLC 工程里 IntelliSense。

## 3. 行为说明

**典型使用流**：① 声明 `fbMsg5 : FB_IotMqtt5Message;`；② 业务循环里 `fbClient.fbMessageQueue.Dequeue(fbMessage := fbMsg5)`；③ 用 `CompareTopic` 或 `GetTopic` 决定路由；④ 用 `GetPayload` 拷出 payload；⑤ 必要时用 `GetUserPropertyByIdx` / `GetUserPropertyValueByName` 拿元数据。

**消息寿命**：与 MQTT 3 版本一致——只在本次 `Dequeue()` 后到下次 `Dequeue()` 之间有效。

**user properties 访问**：`nUserPropertyCnt` 给出个数，按 `for i := 0 to nUserPropertyCnt - 1 do GetUserPropertyByIdx(i, REF=> name, REF=> value)` 遍历；或按 `GetUserPropertyValueByName(REF=> 'trace-id', REF=> value)` 按名取值。`nUserPropertyCntLost > 0` 表示接收时超过 `cMaxMqtt5UserProps`（默认 20）被丢——这是接收侧的限制。

**`bPayloadUtf8` 用法**：publisher 在 PublishProperties 里声明 payload 是不是 UTF-8 文本；接收方读这个布尔判断是不是可以当字符串显示。`FALSE` 时一般是二进制 payload，不要尝试 STRING 转换。

**topic alias**：MQTT 5 引入的"短编号代替长 topic"机制。`bTopicAlias = TRUE` 时本消息原 topic 字符串可能为空——alias 编号映射逻辑在 publisher 和 broker 之间约定，接收方一般直接看 `GetTopic` 返回值（broker 通常会解 alias 回原 topic）。

**Request/Response 接收方用法**：若本消息是 Request（带 Response Topic + CorrelationData），从 `pReq` 拿到 `MqttRequestProperties` 后调 `fbClient.Response(...)`；接收方典型流程是用 `GetResponseTopic` 取响应 topic、用 `GetCorrelationData` 取 correlation data，构造响应后调 `fbClient.Response(sResponseTopic := ..., pCorrelationData := ..., nCorrelationDataSize := ...)`。

**`sContentType` 长度限制**：受 GVL 参数 `cSizeOfMqtt5ContentType`（默认 256 字节）限制。若 broker 实际传过来的 content type 超长，`sContentType` 属性给的是截断版；用 `GetContentType()` 拿完整版到自己的缓冲。

## 4. 错误码 / 返回值

各方法以 `BOOL` 返回成功 / 失败；具体错误极少出现，多数失败原因是缓冲不够大或队列状态异常。

| 调用 | `TRUE` 含义 | `FALSE` 含义 |
|---|---|---|
| `CompareTopic()` | topic 完全相等 | topic 不同 |
| `GetTopic()` / `GetPayload()` / `GetContentType()` / `GetCorrelationData()` / `GetResponseTopic()` | 拷贝成功 | 缓冲不够 / 内部错 |

属性 Get 不可能失败。

## 5. 使用注意 / 常见坑

- **属性返回字符串截断**：`sContentType` 等属性受 GVL 参数 size 限制——超长用 `GetContentType()` 取全。
- **`nUserPropertyCntLost > 0` 要警惕**：接收侧丢了 user property——可能丢的是 trace-id 这种关键元数据。要么调大 `cMaxMqtt5UserProps`，要么 publisher 别带这么多 user property。
- **`bPayloadUtf8` 不是 broker 强制**：是 publisher 的声明；接收方仍要做防御性校验（不信任）。
- **topic alias 解析**：多数 broker 会替接收方解 alias 回原 topic；某些极简 broker 可能直接传 alias 编号——`bTopicAlias = TRUE` + `GetTopic()` 拿到 `'<n>'` 这种数字编号时，要查约定映射表。
- **`GetUserPropertyByIdx` 的 index 从 0 开始**：循环写 `for i := 0 TO nUserPropertyCnt - 1`，不要写 `1 TO nUserPropertyCnt`。
- **消息引用不能跨周期保留**：下次 `Dequeue()` 覆盖；要保留就当周期拷出来。
- **Request/Response 接收方必须用 `pReq`**：MQTT 5 收到 Request 时驱动会在 callback 的 `pReq` 参数里传 `MqttRequestProperties`；要响应必须用其中的 ResponseTopic + CorrelationData，不能用接收方自己定。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5Message.TcPOU`](../examples/P_Demo_FB_IotMqtt5Message.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示出队 MQTT 5 消息后读取 user properties
PROGRAM P_Demo_FB_IotMqtt5Message
VAR
    fbClient : FB_IotMqtt5Client := (sClientId := 'PLC5-Msg', sHostName := '127.0.0.1');
    fbMsg5   : FB_IotMqtt5Message;
    sTopic   : STRING(255);
    sPay     : STRING(255);
    bIsUtf8  : BOOL;
    nUserProps: UINT;
END_VAR
fbClient.Execute(bConnect := TRUE);
WHILE fbClient.fbMessageQueue.nQueuedMessages > 0 DO
    IF NOT fbClient.fbMessageQueue.Dequeue(fbMessage := fbMsg5) THEN EXIT; END_IF
    fbMsg5.GetTopic(pTopic := ADR(sTopic), nTopicSize := SIZEOF(sTopic));
    fbMsg5.GetPayload(pPayload := ADR(sPay), nPayloadSize := SIZEOF(sPay), bSetNullTermination := TRUE);
    bIsUtf8    := fbMsg5.bPayloadUtf8;
    nUserProps := fbMsg5.nUserPropertyCnt;
END_WHILE
```

## 7. 业务场景与实际价值

- **场景**：PLC 订阅带 trace-id user property 的命令消息——MES 在每条命令里加 `trace-id=<uuid>` 用于分布式追踪。PLC 用 `GetUserPropertyValueByName('trace-id', ...)` 取出 trace-id 写到本地日志，便于事后跨系统追溯命令链路。
- **价值**：把 MQTT 5 协议级 properties 抽象成属性 + getter API——业务代码不必碰 MqttPublishProperties 原始结构，直接读 `nUserPropertyCnt` 和 `GetUserPropertyByIdx`。content type / correlation data / response topic 等 MQTT 5 特性同样以 API 暴露，与 OpenTelemetry / 分布式追踪框架天然衔接。
- **替代方案对比**：
  - 自己解析 MqttPublishProperties 二进制结构——和协议绑死，broker 升级可能要重写；
  - 把 trace-id 塞 payload 里走 JSON——耦合应用协议，违反"元数据放 properties / 业务数据放 payload"的 MQTT 5 设计原则；
  - **本 FB**：API 化访问，业务代码与 properties 编码细节解耦。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/14629604107.html
- **相关 FB / GVL**：`FB_IotMqtt5MessageQueue`（产出本 FB 实例的内嵌队列）、`FB_IotMqtt5Client`（消息来源）、`FB_IotMqtt5UserProperties`（user properties 容器）、`FB_IotMqtt5PublishProperties`（publish properties 容器）、`ParameterList`（多个 size 参数）
