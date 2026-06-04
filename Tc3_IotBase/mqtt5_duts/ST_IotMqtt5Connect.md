# ST_IotMqtt5Connect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `STRUCT` (DUT) |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12564928395.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ST_IotMqtt5Connect.TcPOU`](../examples/P_Demo_ST_IotMqtt5Connect.TcPOU) |

---

## 1. 功能简述

`ST_IotMqtt5Connect` 是 MQTT 5 客户端的**高级连接参数**结构体，赋给 `FB_IotMqtt5Client.stConnect` 或 `FB_IotMqtt5ClientBase.stConnect` 后，客户端在 CONNECT 报文里向 broker 声明它的能力限制和偏好——例如能接收的最大包大小、session 过期时间、能同时处理的 QoS 1/2 消息数、最多接受多少 topic alias、是否请求 broker 返回 response info / problem info。

这些字段对接 broker 时是"客户端→broker"方向的能力声明；broker 看到声明后会按客户端能力调整投递策略（例如不发超过 `nMaxPacketSize` 的消息），并在 CONNACK properties 里回报自己的对应限制（参考 `FB_IotMqtt5ConnAckProperties`）。

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致）。

### STRUCT 成员

```iecst
TYPE ST_IotMqtt5Connect :
STRUCT
    nSessionExpire     : UDINT;
    nMaxPacketSize     : UDINT;
    nReceiveMax        : UINT;
    nTopicAliasMax     : UINT;
    bReqResponseInfo   : BOOL;
    bIgnoreProblemInfo : BOOL;
END_STRUCT
END_TYPE
```

### 成员说明

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nSessionExpire` | `UDINT` | — | session 过期秒数——客户端断开后 broker 保留 session（订阅 / 未确认 QoS 1+2 消息）的时长。`0` = 客户端断开即清除（"clean session"）；非 0 = "persistent session"，重连后能拿回未确认消息 |
| `nMaxPacketSize` | `UDINT` | — | 客户端最大可接收的 control packet 字节数——broker 看到这个声明后不会发超过此大小的消息给客户端。`0` 表示不限制 |
| `nReceiveMax` | `UINT` | — | 客户端能**同时处理**的 QoS 1 / 2 消息数（即处于 publish-handshake 中的消息上限）——broker 不会让超过这个数的 QoS 1/2 publish 同时进行 |
| `nTopicAliasMax` | `UINT` | — | 客户端能接受的最大 topic alias 数——broker 不会发超过此数的不同 alias 给客户端。`0` 表示客户端不接受 topic alias |
| `bReqResponseInfo` | `BOOL` | — | `TRUE` 时请求 broker 在 CONNACK 里返回 response info（典型用法：broker 告诉客户端"你的 response topic 应该叫 xxx"） |
| `bIgnoreProblemInfo` | `BOOL` | — | `TRUE` 时表示客户端能处理 broker 在 publish / disconnect 时发的 Reason String / User Properties（PDF 描述被截断；按 MQTT 5 规范，`FALSE` = broker 可以发 problem info） |

## 3. 行为说明

**session 持久化（`nSessionExpire`）**：
- `0` = clean session——断开后 broker 立即清除该 client 的订阅、未确认消息、订阅 ID 等。重新 CONNECT 要重新 SUBSCRIBE。适合"无状态遥测上报"PLC。
- 非 0 = persistent session——broker 保留 N 秒。这 N 秒内若 PLC 重连，恢复所有订阅和未投递的 QoS 1+2 消息。适合"短时网络抖动后要拿回丢的命令"场景。
- 实际 session expire 由客户端和 broker 协商——broker 可能在 CONNACK 里给个更小的值（broker 自己有上限）。运行时从 `fbConnAckProps.nSessionExpiryInterval` 读实际值。

**`nMaxPacketSize` 的实际作用**：客户端声明"我最大能接 N 字节"——broker 不会发更大的。但 broker 也有自己的限制（`fbConnAckProps.nMaxPackateSize`），实际投递上限 = `min(客户端声明, broker 限制)`。`0` 表示不限制（典型云 broker 仍有几 MB 上限）。

**`nReceiveMax` 用作流控**：QoS 1 和 QoS 2 需要 PUBACK / PUBREC-PUBREL-PUBCOMP 握手——握手中的消息占客户端内部缓冲。`nReceiveMax := 10` 让 broker 知道客户端最多同时 hold 10 条 QoS 1/2 消息；超出 broker 会延迟发后续 publish。资源受限 PLC（小 CX）应该设小一点（5-10）；大 IPC 可以设 100+。

**topic alias 节带宽**：MQTT 5 引入 topic alias——用 2 字节数字代替长 topic 字符串。`nTopicAliasMax := 100` 让 broker 知道客户端最多接受 100 个 alias 映射；之后 broker 给"重复 topic"的消息可以用 alias 节省带宽。`0` 关闭——broker 全用原 topic（兼容老消息）。

**`bReqResponseInfo`**：MQTT 5 引入的"broker 告诉客户端怎么命名 response topic"机制。典型用法：客户端开 `bReqResponseInfo := TRUE`，broker 在 CONNACK properties 里返回 `'$resp/PLC-001'`（broker 已经为该客户端分配好的私有响应空间）；之后 PLC 用 `Request(...)` 时填这个 response topic，broker 端拓扑天然支持请求-响应。

**`bIgnoreProblemInfo` 的歧义**：PDF 文字描述被截断（句子末尾的 "may" 后内容丢失）；按 MQTT 5 规范 (3.1.2.11.7)：`FALSE` = broker 可以在 PUBLISH / DISCONNECT 里附加 Reason String 和 User Properties 给客户端；`TRUE` = broker 不应附加这些（除非协议必需）。诊断信息丰富推荐 `FALSE`；带宽极度受限场景才 `TRUE`。

## 4. 错误码 / 返回值

本结构体是数据载体，无返回值。配置错误（极少）反映在父 FB `bError` / `hrErrorCode` / `fbConnAckProps.nReasonCode`。

## 5. 使用注意 / 常见坑

- **`nSessionExpire := 0` 是 "clean session"**：与 MQTT 3 的 cleanSession 标志等效——遥测 PLC 用这个；命令接收 PLC 用非 0 值以保 QoS 1+2 命令不丢。
- **`nMaxPacketSize` 与缓冲大小一致**：声明 N 字节就意味着客户端业务侧 payload 缓冲也得至少 N 字节；声明大但实际缓冲小，broker 发的大消息会溢出。
- **session 实际过期看 CONNACK**：客户端声明 `nSessionExpire := 3600`（1 小时），broker 可能在 CONNACK 里给 `nSessionExpiryInterval := 600`（10 分钟，broker 自己上限）；运行时按 broker 给的实际值算 session 有效期。
- **`nReceiveMax := 0` 是非法值**：MQTT 5 协议规定不能填 0；填 0 broker 一般会断连。`1` 是最小有效值。
- **topic alias 客户端不接受时**：`nTopicAliasMax := 0`——broker 不能给本客户端发 topic alias 类消息。
- **broker 不支持某字段时**：`fbConnAckProps` 里 broker 给出实际支持的值——按那个为准。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ST_IotMqtt5Connect.TcPOU`](../examples/P_Demo_ST_IotMqtt5Connect.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示 persistent session + 中等流控 + 接受 topic alias
PROGRAM P_Demo_ST_IotMqtt5Connect
VAR
    fbMqtt5 : FB_IotMqtt5Client := (sClientId := 'PLC5-Cmd', sHostName := '127.0.0.1');
    bRun    : BOOL := TRUE;
    bConnInit : BOOL;
END_VAR
IF NOT bConnInit THEN
    fbMqtt5.stConnect.nSessionExpire     := 3600;   // 1 小时——拿回断网期间的 QoS 1+2 命令
    fbMqtt5.stConnect.nMaxPacketSize     := 64000;  // 接 64 KB 上限
    fbMqtt5.stConnect.nReceiveMax        := 10;     // 同时处理 10 条 QoS 1+2
    fbMqtt5.stConnect.nTopicAliasMax     := 50;     // 接受最多 50 个 topic alias
    fbMqtt5.stConnect.bReqResponseInfo   := FALSE;
    fbMqtt5.stConnect.bIgnoreProblemInfo := FALSE;  // 接收 broker 诊断信息
    bConnInit := TRUE;
END_IF
fbMqtt5.Execute(bConnect := bRun);
```

## 7. 业务场景与实际价值

- **场景**：MQTT 5 PLC 订阅 MES 下发命令（QoS 1）+ 配方更新（QoS 2）。要求短暂断网（< 1 小时）后重连能拿回丢的命令——配 `nSessionExpire := 3600` + 持久化 session。同时声明 `nReceiveMax := 10` 限制 broker 同时推送的命令数，避免命令洪水拖死 PLC。
- **价值**：把"客户端能力声明 / 偏好"集中到一个结构体——broker 自适应客户端能力，而不是写死成全局参数。`nSessionExpire` 解决"短时断网命令丢失"；`nMaxPacketSize` 让 PLC 避免接到爆大消息；`nReceiveMax` 防 QoS 1+2 洪水拥塞。
- **替代方案对比**：
  - 不配 `stConnect`——broker 用默认上限发，PLC 可能被超大消息或洪水拖死；
  - 用 MQTT 3 + cleanSession=FALSE——能 persistent session 但没有 `nMaxPacketSize` / `nReceiveMax` 细粒度声明；
  - **本结构体**：MQTT 5 协议级声明，broker 自适应。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12564928395.html
- **相关 DUT / FB**：`FB_IotMqtt5Client`（消费 `stConnect`）、`FB_IotMqtt5ClientBase`、`FB_IotMqtt5ConnAckProperties`（broker 返回的实际限制）
