# FB_IotMqtt5Client

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13990483211.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5Client.TcPOU`](../examples/P_Demo_FB_IotMqtt5Client.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5Client` 是 Tc3_IotBase 库基于 **MQTT 协议 5.0 版本**的客户端功能块（FB），把 PLC 与一台 MQTT 5 broker 的全部交互封装成一个 FB 实例 + 多个方法调用。

与 MQTT 3.1.1 版本 `FB_IotMqttClient` 相比，本 FB 引入 MQTT 5 的高级特性：① **CONNACK / DISCONNECT properties** 通过 FB 实例自带的 `fbConnAckProps` / `fbDisconnectProps` 输出暴露；② 内嵌一个 `fbMessageQueue` 输出供出队；③ 支持 **Request/Response 模式**——通过 `Request()` / `Response()` 方法搭配 CorrelationData 实现"一对一请求-应答"；④ Publish/Subscribe/Unsubscribe 都额外支持透传 user-properties / topic-alias 等 MQTT 5 properties；⑤ 支持 `stAuth` 扩展鉴权 + `stConnect` 高级连接参数。

**两种范式区别**：本 FB 使用**内嵌队列**收消息——业务侧出队即可；如果要重写回调方法（`OnMqtt5Message` / `OnMqtt5ConnAck` / `OnMqtt5Disconnected`）就改用 `FB_IotMqtt5ClientBase`（本 FB 的基类，不暴露内嵌队列、由用户派生重写）。

**TwinCAT 版本要求**：要求 TwinCAT v3.1.4026.0 以上、Tc3_IotBase 库版本 ≥ 3.4.2.0。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    {attribute 'TcEncoding':='UTF-8'}
    sClientId        : STRING(255);        // default is generated during initialization
    {attribute 'TcEncoding':='UTF-8'}
    sHostName        : STRING(255) := '127.0.0.1'; // default is local host
    nHostPort        : UINT := 1883;       // default is 1883
    {attribute 'TcEncoding':='UTF-8'}
    sTopicPrefix     : STRING(255);        // topic prefix for pub and sub of this client (handled internally)
    nKeepAlive       : UINT := 60;         // in seconds
    {attribute 'TcEncoding':='UTF-8'}
    sUserName        : STRING(255);        // optional parameter
    {attribute 'TcEncoding':='UTF-8'}
    sUserPassword    : STRING(255);        // optional parameter
    stWill           : ST_IotMqtt5Will;    // optional parameter
    stTLS            : ST_IotMqtt5Tls;     // optional parameter
    stAuth           : ST_IotMqtt5Auth;    // optional parameter
    stConnect        : ST_IotMqtt5Connect; // optional parameter
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sClientId` | `STRING(255)` | — | 客户端 ID，多数 broker 要求**唯一**；留空由驱动按 PLC 工程名生成。带 `TcEncoding:='UTF-8'` 属性 |
| `sHostName` | `STRING(255)` | `'127.0.0.1'` | broker 主机名或 IP |
| `nHostPort` | `UINT` | `1883` | broker 端口（TLS 一般 8883） |
| `sTopicPrefix` | `STRING(255)` | — | 自动追加到本实例所有 publish/subscribe topic 前的前缀 |
| `nKeepAlive` | `UINT` | `60` | 保活看门狗周期（秒）；broker 在 `nKeepAlive × 1.5` 内没消息判客户端死亡 |
| `sUserName` | `STRING(255)` | — | 可选 broker 用户名 |
| `sUserPassword` | `STRING(255)` | — | 可选密码 |
| `stWill` | `ST_IotMqtt5Will` | — | 可选遗嘱消息（MQTT 5 扩充版结构体，含 user properties / expiry / delay） |
| `stTLS` | `ST_IotMqtt5Tls` | — | 可选 TLS 安全设置 |
| `stAuth` | `ST_IotMqtt5Auth` | — | 可选扩展认证设置（MQTT 5 新增） |
| `stConnect` | `ST_IotMqtt5Connect` | — | 可选高级连接参数（session expiry / max packet size / topic alias max 等） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError            : BOOL;
    hrErrorCode       : HRESULT;
    eConnectionState  : ETcIotMqttClientState;
    bConnected        : BOOL; // TRUE if connection to host is established
    fbMessageQueue    : FB_IotMqtt5MessageQueue;         // received messages are queued during call of Execute()
    fbConnAckProps    : FB_IotMqtt5ConnAckProperties;    // info is set when a connection is acknowledged
    fbDisconnectProps : FB_IotMqtt5DisconnectProperties; // info is set after disconnection
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出现错误置 `TRUE` |
| `hrErrorCode` | `HRESULT` | HRESULT 错误码 |
| `eConnectionState` | `ETcIotMqttClientState` | 细分连接状态 |
| `bConnected` | `BOOL` | 已连上时 `TRUE` |
| `fbMessageQueue` | `FB_IotMqtt5MessageQueue` | 内嵌接收队列；业务侧直接访问该输出做 `Dequeue()` |
| `fbConnAckProps` | `FB_IotMqtt5ConnAckProperties` | broker 在 CONNACK 时返回的 properties（最大包大小、retain 支持、wildcard 支持、Assigned ClientId 等） |
| `fbDisconnectProps` | `FB_IotMqtt5DisconnectProperties` | 断连时收到的 DISCONNECT properties（Reason Code、Reason String、Server Reference 等） |

### VAR_IN_OUT

无。

### METHOD Execute

后台通信推进，**必须周期调用**。

```iecst
METHOD Execute
VAR_INPUT
    bConnect : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConnect` | `BOOL` | 电平 `TRUE` 维持/建立连接；`FALSE` 主动 DISCONNECT |

### METHOD Publish

发送一条 publish。比 MQTT 3 版多了 `pProps` 透传 MQTT 5 properties。

```iecst
METHOD Publish : BOOL
VAR_IN_OUT
    sTopic       : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
VAR_INPUT
    pPayload     : PVOID;
    nPayloadSize : UDINT;
    eQoS         : TcIotMqttQos; // quality of service between the publishing client and the broker
    bRetain      : BOOL; // if TRUE the broker stores the message in order to send it to new subscribers
    bQueue       : BOOL; // for future extension
    pProps       : POINTER TO MqttPublishProperties; // optional
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 目标 topic（UTF-8） |
| `pPayload` | IN | `PVOID` | payload 起始地址 |
| `nPayloadSize` | IN | `UDINT` | payload 字节数 |
| `eQoS` | IN | `TcIotMqttQos` | QoS 等级 |
| `bRetain` | IN | `BOOL` | retain 标志 |
| `bQueue` | IN | `BOOL` | 保留参数，固定 `FALSE` |
| `pProps` | IN | `POINTER TO MqttPublishProperties` | 可选 publish properties 指针；用 `ADR(fbPublishProps.pPublishProperties^)` 之类的形式传 `FB_IotMqtt5PublishProperties` 内部结构地址 |

返回值：`BOOL`——`TRUE` 调用成功。

### METHOD Subscribe

订阅 topic。

```iecst
METHOD Subscribe : BOOL
VAR_IN_OUT
    sTopic    : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
VAR_INPUT
    eQoS      : TcIotMqttQos; // quality of service between the publishing client and the broker
    pProps    : POINTER TO MqttSubscribeProperties; // optional
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 要订阅的 topic |
| `eQoS` | IN | `TcIotMqttQos` | 最大可接受 QoS |
| `pProps` | IN | `POINTER TO MqttSubscribeProperties` | 可选 subscribe properties（NoLocal / RetainAsPublished / RetainHandling / SubscriptionId 等） |

返回值：`BOOL`。

### METHOD Unsubscribe

取消订阅。

```iecst
METHOD Unsubscribe : BOOL
VAR_IN_OUT
    sTopic    : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
VAR_INPUT
    pProps    : POINTER TO MqttUnsubscribeProperties; // optional
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 要取消订阅的 topic |
| `pProps` | IN | `POINTER TO MqttUnsubscribeProperties` | 可选 unsubscribe properties（一般用 user properties） |

返回值：`BOOL`。

### METHOD ActivateExponentialBackoff

启用指数退避重连。

```iecst
METHOD ActivateExponentialBackoff
VAR_INPUT
    tMqttBackoffMinTime: TIME;
    tMqttBackoffMaxTime: TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `tMqttBackoffMinTime` | `TIME` | 初始等待 |
| `tMqttBackoffMaxTime` | `TIME` | 翻倍封顶 |

### METHOD DeactivateExponentialBackoff

关闭指数退避。

```iecst
METHOD DeactivateExponentialBackoff
```

无参数。

### METHOD Request

发出一条 MQTT 5 的 **Request**（带 Response Topic + CorrelationData），用于请求-应答模式。

```iecst
METHOD Request : BOOL
VAR_IN_OUT
    sTopic              : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
    sResponseTopic      : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
VAR_INPUT
    pPayload            : PVOID;
    nPayloadSize        : UDINT;
    eQoS                : TcIotMqttQos; // quality of service between the publishing client and the broker
    bRetain             : BOOL; // if TRUE the broker stores the message in order to send it to new subscribers
    bQueue              : BOOL; // for future extension
    pProps              : POINTER TO MqttPublishProperties;
    pCorrelationData    : POINTER TO BYTE;
    nCorrelationDataSize: UINT;
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 请求 topic |
| `sResponseTopic` | IN_OUT | `STRING` | 期望对端把响应发到哪个 topic |
| `pPayload` | IN | `PVOID` | 请求 payload |
| `nPayloadSize` | IN | `UDINT` | payload 字节数 |
| `eQoS` | IN | `TcIotMqttQos` | QoS |
| `bRetain` | IN | `BOOL` | retain 标志 |
| `bQueue` | IN | `BOOL` | 保留参数，固定 `FALSE` |
| `pProps` | IN | `POINTER TO MqttPublishProperties` | 可选 publish properties |
| `pCorrelationData` | IN | `POINTER TO BYTE` | 关联数据起始地址——用于把响应跟请求对应起来（例如填一个 UUID） |
| `nCorrelationDataSize` | IN | `UINT` | 关联数据字节数 |

返回值：`BOOL`。

### METHOD Response

发出一条对 Request 的 **Response**。

```iecst
METHOD Response : BOOL
VAR_IN_OUT
    sResponseTopic       : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
VAR_INPUT
    pPayload            : PVOID;
    nPayloadSize        : UDINT;
    eQoS                : TcIotMqttQos; // quality of service between the publishing client and the broker
    bRetain             : BOOL; // if TRUE the broker stores the message in order to send it to new subscribers
    bQueue              : BOOL; // for future extension
    pProps              : POINTER TO MqttPublishProperties;
    pCorrelationData    : POINTER TO BYTE;
    nCorrelationDataSize: UINT;
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sResponseTopic` | IN_OUT | `STRING` | 响应发到哪个 topic（与 Request 里的对应） |
| `pPayload` | IN | `PVOID` | 响应 payload |
| `nPayloadSize` | IN | `UDINT` | 字节数 |
| `eQoS` | IN | `TcIotMqttQos` | QoS |
| `bRetain` | IN | `BOOL` | retain |
| `bQueue` | IN | `BOOL` | 固定 `FALSE` |
| `pProps` | IN | `POINTER TO MqttPublishProperties` | 可选 publish properties |
| `pCorrelationData` | IN | `POINTER TO BYTE` | 关联数据——必须与对应 Request 的 CorrelationData 一致才能让对端配对 |
| `nCorrelationDataSize` | IN | `UINT` | 关联数据字节数 |

返回值：`BOOL`。

### METHOD GetTimeSinceLastBrokerMessage

返回距上一条 broker 消息的毫秒数。

```iecst
METHOD GetTimeSinceLastBrokerMessage : UDINT
```

无参数；返回 `UDINT`。

## 3. 行为说明

**与 MQTT 3 客户端相比的关键差异**：① 接收消息通过 `fbMessageQueue` 输出（已经内嵌一个队列实例），业务侧直接 `fbClient.fbMessageQueue.Dequeue(...)` 即可，无需在 VAR_INPUT 接 `ipMessageQueue`；② 多了 `Request` / `Response` 方法支持请求-应答模式；③ 所有 publish / subscribe / unsubscribe 都可选透传 MQTT 5 properties——用 `FB_IotMqtt5PublishProperties` 等辅助 FB 构造好 properties 后传 `pProps`；④ broker 在 CONNACK / DISCONNECT 时携带的 properties 通过 `fbConnAckProps` / `fbDisconnectProps` 暴露——业务侧可读取 broker 的能力限制（max packet size、retain 支持等）做自适应。

**生命周期与 MQTT 3 一致**：实例化 → 每周期 `Execute(bConnect := TRUE)` → 连上后 publish / subscribe / Request → 业务结束时 `bConnect := FALSE` → DISCONNECT。

**Request/Response 模式**：① Client A 调 `Request(sTopic := 'svc/calc', sResponseTopic := 'svc/calc/resp/A', pPayload := ..., pCorrelationData := ADR(uuidA), nCorrelationDataSize := 16)`——broker 把请求转给订阅 `svc/calc` 的 Client B；② Client B 收到后用 `Response(sResponseTopic := <从 Request properties 里取>, pCorrelationData := <从 Request properties 里取>, ...)`——broker 把响应发到 Client A 订阅的 response topic；③ Client A 出队收到响应，用 CorrelationData 关联回原 Request。MQTT 5 协议原生支持，本 FB 的 `Request`/`Response` 是协议级 API。

**CONNACK properties 用法**：连上后立刻读 `fbConnAckProps.nMaxPackateSize`（broker 最大支持包大小）、`fbConnAckProps.bRetainAvailable`、`fbConnAckProps.bWildcardSubAvailable` 等，决定后续 publish 是否要分片、能否用 retain、能否用 wildcard 订阅。AWS IoT Core 等云 broker 经常限制最大包大小为 128 KB；不读就发可能直接断连。

**DISCONNECT properties 用法**：异常断连后 broker 可能在 DISCONNECT 报文里携带 Reason Code（0x82 = Protocol Error / 0x95 = Packet Too Large 等）和 Reason String（人类可读说明）；从 `fbDisconnectProps.nReasonCode` / `sReasonString` 读出来诊断。

**Properties 透传**：业务代码先实例化 `FB_IotMqtt5PublishProperties fbPubProps`、用 `fbPubProps.SetPublishProperties(...)` 设字段、然后 `fbClient.Publish(..., pProps := fbPubProps.pPublishProperties)` 把内部 properties 结构地址传过去。Subscribe / Unsubscribe 同理。

## 4. 错误码 / 返回值

错误以 `bError` + `hrErrorCode`（HRESULT）+ `eConnectionState`（细分枚举）三路输出，与 MQTT 3 客户端的错误体系一致。详细 HRESULT 列表参 PDF §7.2 ADS Return Codes。

MQTT 5 特有的错误诊断主要在 `fbConnAckProps` / `fbDisconnectProps`：

- `fbConnAckProps.nReasonCode` ≠ 0 表示 broker 拒绝连接（典型 0x82 Protocol Error / 0x86 Bad UserName/Password / 0x87 Not Authorized / 0x95 Packet Too Large）
- `fbDisconnectProps.nReasonCode` 表示对端主动断连的原因（0x80 Unspecified / 0x82 Protocol Error / 0x9C Use Another Server）
- 配合 `fbDisconnectProps.sServerReference` 读到 broker 要求"换 server"时给出的新地址

方法 `BOOL` 返回值：`TRUE` 表示调用本身成功（请求已交给驱动）；不等于"消息已确认送达"。

## 5. 使用注意 / 常见坑

- **TwinCAT 版本**：要求 ≥3.1.4026.0；老版本运行时找不到 MQTT 5 driver。
- **`Execute()` 必须周期调用**：与 MQTT 3 一致。
- **`fbMessageQueue` 是 VAR_OUTPUT 不是 VAR_INPUT**：直接访问 `fbClient.fbMessageQueue.Dequeue(...)`；不要再声明独立队列。
- **`pCorrelationData` 的内存寿命**：发出 `Request()` 后，broker 真正转发前指针必须有效。用全局变量或长生命周期 VAR 持有。
- **Properties 指针写法**：`pProps := fbPubProps.pPublishProperties`——是 `FB_IotMqtt5PublishProperties` 的属性（property），不是 method；它内部把 `MqttPublishProperties` 结构封装好。
- **CONNACK properties 必读**：连上后立即读 `fbConnAckProps.nMaxPackateSize`，避免发超大 publish 后被 broker 强断。（工程经验补充）
- **`sClientId` UTF-8 编码限制**：MQTT 5 规定 ClientId 最长 23 字符（ASCII），broker 可宽容到 65535；含非 ASCII 字符要确认 broker 支持。
- **Request/Response 配对靠 CorrelationData**：CorrelationData 同 = 同一对请求-响应；多并发 Request 共用同一 client 时务必每次填唯一 UUID 区分。
- **断连原因**：`bConnected` 落回 `FALSE` 时先看 `fbDisconnectProps.nReasonCode` 给具体原因；MQTT 5 broker 给的诊断信息比 MQTT 3 详细很多。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5Client.TcPOU`](../examples/P_Demo_FB_IotMqtt5Client.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行例程见上述 .TcPOU 文件；下面给出最小调用骨架以便快速理解：

```iecst
// 演示 MQTT5 客户端连本地 broker，订阅 + 定时 publish + 读 CONNACK properties
PROGRAM P_Demo_FB_IotMqtt5Client
VAR
    fbMqtt5 : FB_IotMqtt5Client := (sClientId := 'PLC5-001', sHostName := '127.0.0.1', nHostPort := 1883);
    fbMsg   : FB_IotMqtt5Message;
    sTopic  : STRING := 'plc/v5/telemetry';
    sPay    : STRING(80) := '{"t":42}';
    bRun    : BOOL := TRUE;
END_VAR
fbMqtt5.Execute(bConnect := bRun);
IF fbMqtt5.bConnected THEN
    // 自适应：读 broker 最大包大小、retain 支持
    IF fbMqtt5.fbConnAckProps.nMaxPackateSize > 0 AND TO_UDINT(LEN(sPay)) > fbMqtt5.fbConnAckProps.nMaxPackateSize THEN
        // payload 太大——分片或换 topic
    END_IF
    fbMqtt5.Publish(sTopic := sTopic,
                    pPayload := ADR(sPay), nPayloadSize := TO_UDINT(LEN(sPay)),
                    eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := FALSE, bQueue := FALSE,
                    pProps := 0);
    WHILE fbMqtt5.fbMessageQueue.nQueuedMessages > 0 DO
        IF NOT fbMqtt5.fbMessageQueue.Dequeue(fbMessage := fbMsg) THEN EXIT; END_IF
        // 处理消息
    END_WHILE
END_IF
```

## 7. 业务场景与实际价值

- **场景**：现代云平台（AWS IoT Core / Azure IoT Hub / EMQX / HiveMQ Cloud）多数已经支持 MQTT 5；新项目应直接走 MQTT 5——request/response 模式让 PLC 可以"主动查询某个云服务"，user-properties 让消息带任意键值元数据（如 trace-id、版本号），CONNACK properties 让客户端能自适应 broker 能力。
- **价值**：相比 MQTT 3 客户端：① request/response 不用自己写 correlation 逻辑（双 topic 订阅 + 自定义关联 ID）；② broker 把限制（最大包大小、wildcard 支持）暴露给客户端，运行时自适应而不是写死；③ 断连原因细分（reason code + reason string）；④ user-properties 让消息天然带元数据，对接 OpenTelemetry / 分布式追踪很自然。
- **替代方案对比**：
  - 继续用 MQTT 3 `FB_IotMqttClient`——cloud broker 仍兼容，但失去自适应/请求响应/user-properties 这些 MQTT 5 引入的关键能力；
  - 用 `FB_IotMqtt5ClientBase` 自己写回调——更细粒度控制，但要自己处理队列、消息生命周期、并发安全；
  - 走 HTTP REST + WebSocket——协议混杂、自己写状态机；
  - **本 FB**：MQTT 5 全特性的"开箱即用"客户端，业务侧只关心 topic / payload / properties。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.1（含子节 5.1.2.1.1 – 5.1.2.1.9 全部 9 个方法）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13990483211.html
- **相关 FB / DUT**：`FB_IotMqtt5ClientBase`（基类，重写回调用）、`ST_IotMqtt5Will`、`ST_IotMqtt5Tls`、`ST_IotMqtt5Auth`、`ST_IotMqtt5Connect`、`FB_IotMqtt5MessageQueue`（内嵌输出）、`FB_IotMqtt5Message`、`FB_IotMqtt5ConnAckProperties`、`FB_IotMqtt5DisconnectProperties`、`FB_IotMqtt5PublishProperties`、`FB_IotMqtt5SubscribeProperties`、`FB_IotMqtt5UnsubscribeProperties`、`FB_IotMqtt5UserProperties`、`ETcIotMqttClientState`
