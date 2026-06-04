# FB_IotMqtt5MessageQueue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/14021292811.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5MessageQueue.TcPOU`](../examples/P_Demo_FB_IotMqtt5MessageQueue.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5MessageQueue` 是 MQTT 5 客户端用的**先进先出（FIFO）消息队列**功能块。与 MQTT 3 版本 `FB_IotMqttMessageQueue` 不同的是——它**不是用户自己声明并赋给 client**，而是**已经内嵌在 `FB_IotMqtt5Client` 的 VAR_OUTPUT** 里（字段名 `fbMessageQueue`）。业务侧直接访问 `fbClient.fbMessageQueue.Dequeue(...)` 即可。

属性比 MQTT 3 版本更丰富：除了 `nQueuedMessages` 外还多了 `nLostMessages`（被丢的消息数）和 `nMaxSizeOfMessage`（接收过的最大消息字节数）——便于运行时观测溢出和容量规划。

队列容量上限同样受 GVL 参数 `cMaxEntriesInMqttMessageQueue`（1000 条）/ `cMaxSizeOfMqttMessageQueue`（1 MB）/ `cMaxSizeOfMqttMessage`（100 KB）限制。

## 2. 接口定义

本 FB 没有 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；状态通过 **Property** 暴露，操作通过两个 **Method** 完成。

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### Property（属性）

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `bOverwriteOldestEntry` | `BOOL` | Get / Set | 队列满后行为：`TRUE` 用新消息覆盖最老消息；`FALSE`（默认）让新消息等队列腾位（与 MQTT 3 版的"直接丢新"略不同——见 §3） |
| `nLostMessages` | `UDINT` | Get | 累计因队列溢出 / 单条消息过大被**完全丢弃**的消息数。运行时观测溢出 |
| `nMaxSizeOfMessage` | `UDINT` | Get | 历史接收过的最大消息字节数。若超过 `ParameterList.cMaxSizeOfMqttMessage`（默认 100 KB），队列会先尝试去掉 user properties 再保存；若仍超限就丢弃 |
| `nQueuedMessages` | `UDINT` | Get | 当前待出队消息数。最大值受 `cMaxEntriesInMqttMessageQueue`（默认 1000）限制 |

### METHOD Dequeue

出队一条消息到调用方提供的 `FB_IotMqtt5Message` 实例。

```iecst
METHOD Dequeue : BOOL
VAR_INPUT
    fbMessage : REFERENCE TO FB_IotMqtt5Message;
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `fbMessage` | IN | `REFERENCE TO FB_IotMqtt5Message` | 接收出队消息的 `FB_IotMqtt5Message` 实例引用 |

返回值：`BOOL`——`TRUE` 成功出队；`FALSE` 队列为空。

### METHOD ResetQueue

清空整个队列。

```iecst
METHOD ResetQueue : BOOL
```

无参数；返回 `BOOL`——`TRUE` 调用成功。

## 3. 行为说明

**访问路径**：用户**不直接实例化**本 FB；它是 `FB_IotMqtt5Client.fbMessageQueue` 输出，业务侧直接访问 `fbClient.fbMessageQueue.Dequeue(REF=> fbMsg5)` 即可。也可以直接读 `fbClient.fbMessageQueue.nQueuedMessages` / `.nLostMessages` 做观测。

**与 MQTT 3 版本的差异**：MQTT 3 的 `FB_IotMqttMessageQueue` 是用户**自己声明并赋给 `FB_IotMqttClient.ipMessageQueue`** 的；MQTT 5 反过来——是 client 自带的 VAR_OUTPUT，用户**直接读**就行。

**`bOverwriteOldestEntry` 语义微差**：
- MQTT 3 版本：`FALSE` = 队列满后**直接丢新消息**；
- MQTT 5 版本（本 FB）：`FALSE` = 队列满后**接收等待**（block 接收），直到队列出现空位才接新消息。

后者对命令流场景更安全——不会"静默丢命令"，但会让 driver 接收背压（broker 端可能因此触发流控）。

**`nLostMessages` 何时增长**：① 单条消息超过 `cMaxSizeOfMqttMessage` 且去掉 user properties 后仍超限——整条丢；② `bOverwriteOldestEntry = TRUE` 时队列满覆盖老消息——计入丢老消息。运行时 `nLostMessages > 0` 是预警信号，说明业务处理速度跟不上 broker 推送速度，或单条消息过大。

**`nMaxSizeOfMessage` 用法**：历史峰值——上线初期跑一段时间看，根据 max 大小调整 `cMaxSizeOfMqttMessage` 参数和缓冲尺寸。生产中也可以告警监控。

**出队后的消息生命**：与 MQTT 3 一致——`Dequeue()` 成功后 `fbMessage` 内容**只在当周期有效**，下次 `Dequeue()` 覆盖。要保留就立即拷出 topic / payload / properties。

**全部消息都进队**：单 client 实例所有订阅 topic 都共用本队列；业务侧用 `CompareTopic` 路由。

## 4. 错误码 / 返回值

各方法以 `BOOL` 返回成功/失败；丢消息事件通过 `nLostMessages` 属性反映：

| 调用 / 属性 | 含义 |
|---|---|
| `Dequeue() = TRUE` | 成功出队一条 |
| `Dequeue() = FALSE` | 队列为空 |
| `ResetQueue() = TRUE` | 队列已清空 |
| `nLostMessages > 0` | 历史有丢消息（溢出或单条过大） |

## 5. 使用注意 / 常见坑

- **不要自己声明本 FB**：MQTT 5 范式是访问 `fbClient.fbMessageQueue.Dequeue(...)`——如果声明独立实例并尝试 `fbClient.ipMessageQueue := ...`（MQTT 3 写法），编译会失败因为 MQTT 5 主类没有 `ipMessageQueue` 输入。
- **`bOverwriteOldestEntry` 默认对命令流安全**：默认 `FALSE` = 等空位，命令不会丢但接收会背压。遥测场景显式置 `TRUE` 让老消息被覆盖以保证最新数据可达。
- **`nLostMessages` 不会自动复位**：是累计计数器；只有 `ResetQueue()` 不会清它（PDF 没明示，但 InfoSys 说 ResetQueue 只清队列本身）。运行时观测看增量。
- **`nMaxSizeOfMessage` 反映 GVL 限制**：超过 `cMaxSizeOfMqttMessage` 时驱动会先尝试丢 user properties 救回 payload；若 payload 本身就超限就整条丢。生产中要么把 GVL 参数调大、要么让上游分片发。
- **出队循环要限速**：消息洪水时一周期出空 1000 条会拖慢 PLC 周期。设上限 `i < cMaxPerCycle`。
- **多 client 不能共用本 FB**：MQTT 5 模型是 1 client = 1 内嵌 queue，强绑定。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5MessageQueue.TcPOU`](../examples/P_Demo_FB_IotMqtt5MessageQueue.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_IotMqtt5MessageQueue
VAR
    fbClient : FB_IotMqtt5Client := (sClientId := 'PLC5-Q', sHostName := '127.0.0.1');
    fbMsg    : FB_IotMqtt5Message;
    nQueued  : UDINT;
    nLost    : UDINT;
END_VAR
fbClient.Execute(bConnect := TRUE);
fbClient.fbMessageQueue.bOverwriteOldestEntry := TRUE;            // 遥测：丢老留新
IF fbClient.bConnected THEN
    fbClient.Subscribe(sTopic := 'plc/v5/+/telemetry',
                       eQoS   := TcIotMqttQos.AtMostOnceDelivery,
                       pProps := 0);
END_IF
nQueued := fbClient.fbMessageQueue.nQueuedMessages;
nLost   := fbClient.fbMessageQueue.nLostMessages;
WHILE fbClient.fbMessageQueue.nQueuedMessages > 0 DO
    IF NOT fbClient.fbMessageQueue.Dequeue(fbMessage := fbMsg) THEN EXIT; END_IF
    // 处理消息
END_WHILE
```

## 7. 业务场景与实际价值

- **场景**：MQTT 5 边缘节点订阅多个产线的遥测流，业务任务每周期出队处理。配 `nLostMessages` 做溢出监控——一旦增长就告警让运维加资源。
- **价值**：内嵌队列免去用户自己 wire——少一处可能出错的赋值；多了 `nLostMessages` / `nMaxSizeOfMessage` 让运维可观测；`bOverwriteOldestEntry := FALSE` 的"等空位"行为更适合命令流的"宁可背压不丢消息"模式。
- **替代方案对比**：
  - 用 `FB_IotMqtt5ClientBase` + 重写 `OnMqtt5Message` 回调——更细控制、更低延迟，但失去 driver 自带的丢消息观测；
  - 用 MQTT 3 模型（外置 queue）——失去 nLostMessages 观测，配置更繁琐；
  - **本 FB（内嵌路径）**：开箱即用，可观测，与主类强绑定。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/14021292811.html
- **相关 FB / GVL**：`FB_IotMqtt5Client`（持有本 FB 实例作为输出）、`FB_IotMqtt5Message`（出队载体）、`ParameterList`（队列容量上限的 GVL 参数）、`FB_IotMqttMessageQueue`（MQTT 3 版本，由用户自己实例化挂到 ipMessageQueue）
