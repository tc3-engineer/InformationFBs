# FB_IotMqtt5ClientBase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12560546699.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5ClientBase.TcPOU`](../examples/P_Demo_FB_IotMqtt5ClientBase.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5ClientBase` 是 MQTT 5 客户端的**基类 FB**，行为与 `FB_IotMqtt5Client` 基本一致，区别在于**收消息的范式**：本 FB 不暴露内嵌的 `fbMessageQueue` 输出；取而代之，**派生本 FB** 并重写四个 callback 方法：① `OnMqtt5Message`（每收到一条消息回调一次）；② `OnMqtt5ConnAck`（broker 在 CONNACK 时回调一次）；③ `OnMqtt5Disconnected`（broker 主动断连时回调一次）；④ `OnMqtt5Authentication`（broker 在 AUTH 报文时回调，扩展鉴权用）。

要点：**回调直接在 `Execute()` 调用栈里同步执行**——长耗时操作（写库、ADS 远程读写）会拖慢 PLC 任务周期；需要异步化时改用 `FB_IotMqtt5Client` + 内嵌队列范式。

> **⚠️ PDF 印刷错误**：PDF §5.1.2.2 的 Syntax 块声明的是 `FUNCTION_BLOCK FB_IotMqtt5Client`（少了后缀 `Base`），但章节标题 `5.1.2.2 FB_IotMqtt5ClientBase` 和上下文说明都明确指出本基类的名字是 `FB_IotMqtt5ClientBase`。实际类型名以**章节标题**为准。

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

VAR_INPUT 字段与 `FB_IotMqtt5Client` 完全一致，含义和默认值参 `FB_IotMqtt5Client.md` §2。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError           : BOOL;
    hrErrorCode      : HRESULT;
    eConnectionState : ETcIotMqttClientState;
    bConnected       : BOOL; // TRUE if connection to host is established
END_VAR
```

**关键差异**：与 `FB_IotMqtt5Client` 相比少了 `fbMessageQueue` / `fbConnAckProps` / `fbDisconnectProps` 三个输出——因为基类期望子类在 callback 里就地处理消息和 properties。

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错置 `TRUE` |
| `hrErrorCode` | `HRESULT` | HRESULT 错误码 |
| `eConnectionState` | `ETcIotMqttClientState` | 细分连接状态 |
| `bConnected` | `BOOL` | 已连上时 `TRUE` |

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
| `bConnect` | `BOOL` | 电平 `TRUE` 维持/建立连接 |

### METHOD Publish

发送一条 publish。与 `FB_IotMqtt5Client.Publish` 一致。

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

### METHOD OnMqtt5ConnAck（回调，重写）

broker 在 CONNACK 时回调。重写后通过 `pProps` 拿到 CONNACK 携带的 MQTT 5 properties——读取 broker 能力（最大包大小、retain 支持、wildcard 支持等）。

```iecst
METHOD OnMqtt5Disconnected : HRESULT
VAR_INPUT
    pProps : POINTER TO MqttConnAckProperties;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pProps` | `POINTER TO MqttConnAckProperties` | CONNACK 携带的 MQTT 5 properties |

返回值：`HRESULT`。

**⚠️ PDF 印刷错误**：PDF §5.1.2.2.5 的方法签名行写成 `METHOD OnMqtt5Disconnected : HRESULT`（与方法名 `OnMqtt5ConnAck` 不一致）。InfoSys 网页同样保留此印刷错误。实际方法名以章节标题 `OnMqtt5ConnAck` 为准——这就是用户应该重写的方法名。

### METHOD OnMqtt5Disconnected（回调，重写）

broker 主动断连时回调。

```iecst
METHOD OnMqtt5Disconnected : HRESULT
VAR_INPUT
    pProps : POINTER TO MqttDisconnectProperties;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pProps` | `POINTER TO MqttDisconnectProperties` | DISCONNECT 携带的 MQTT 5 properties（Reason Code、Reason String、Server Reference 等） |

返回值：`HRESULT`。

### METHOD OnMqtt5Message（回调，重写）

每收到一条 MQTT 消息回调一次。

```iecst
METHOD OnMqtt5Message : HRESULT
VAR_IN_OUT CONSTANT
    topic    : STRING;
END_VAR
VAR_INPUT
    payload  : PVOID;
    length   : UDINT;
    qos      : TcIotMqttQos;
    pProps   : POINTER TO MqttPublishProperties;
    pReq     : POINTER TO MqttRequestProperties;
    repeated : BOOL;
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `topic` | IN_OUT CONSTANT | `STRING` | 消息 topic |
| `payload` | IN | `PVOID` | payload 起始地址 |
| `length` | IN | `UDINT` | payload 字节数 |
| `qos` | IN | `TcIotMqttQos` | 投递 QoS |
| `pProps` | IN | `POINTER TO MqttPublishProperties` | publish properties（user properties / message expiry / topic alias 等） |
| `pReq` | IN | `POINTER TO MqttRequestProperties` | 若消息是请求（带 Response Topic + CorrelationData），通过本指针拿到 |
| `repeated` | IN | `BOOL` | 上次回调返回 `S_FALSE` 重试时为 `TRUE` |

返回值：`HRESULT`——`S_OK` 接受；`S_FALSE` 下次再试。

### METHOD ActivateExponentialBackoff

启用指数退避重连。

```iecst
METHOD ActivateExponentialBackoff
VAR_INPUT
    tMqttBackoffMinTime: TIME;
    tMqttBackoffMaxTime: TIME;
END_VAR
```

### METHOD DeactivateExponentialBackoff

关闭指数退避。

```iecst
METHOD DeactivateExponentialBackoff
```

### METHOD Request

发起 MQTT 5 请求-响应模式的 Request。

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

### METHOD Response

回应 MQTT 5 请求-响应模式的 Response。

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

### METHOD GetTimeSinceLastBrokerMessage

返回距上一条 broker 消息的毫秒数。

```iecst
METHOD GetTimeSinceLastBrokerMessage : UDINT
```

## 3. 行为说明

**派生与重写**：本 FB 是基类——业务侧必须**派生**它（用 `FUNCTION_BLOCK fbMyMqttClient EXTENDS FB_IotMqtt5ClientBase`），然后重写 `OnMqtt5Message` / `OnMqtt5ConnAck` / `OnMqtt5Disconnected`（必要时再加 `OnMqtt5Authentication`）。重写后调用方实例化的是 `fbMyMqttClient`，业务代码在被覆盖的方法体里。

**回调上下文**：回调由 TwinCAT 驱动在 `Execute()` 内部同步调用——回调里的业务代码占用的就是 PLC 任务周期。一周期内多条消息会触发多次回调（每条一次），且**回调函数必须是可重入的**——若业务代码访问共享状态，要自己加互斥（实际上 PLC 任务单线程，一般不需要 mutex，但要注意中断重入）。

**回调与队列范式互斥**：本基类不带内嵌队列；要队列就用 `FB_IotMqtt5Client`。两者底层是同一 driver，差异只在"消息出口"——回调直发 vs 队列暂存。

**`OnMqtt5Message` 的 `repeated` 标志**：上次回调返回 `S_FALSE` → 驱动把该消息保留在 driver 内部缓冲，下次 `Execute()` 时再次回调，`repeated := TRUE`。业务逻辑要做幂等防重（典型用法：上次处理失败、本次重试；或上次因临时资源不足无法处理）。

**Request/Response 模式**：与 `FB_IotMqtt5Client` 一致——`Request()` 发请求 + CorrelationData，对端在 `OnMqtt5Message` 回调里通过 `pReq` 拿到 Request Properties（包含 Response Topic 和 CorrelationData），然后调 `Response()` 回应。

**何时选基类 vs 主类**：
- 选 `FB_IotMqtt5Client`（主类）——业务任务和消息处理在时间上要解耦；不打算改 driver 行为；消息处理耗时较长可能影响周期；
- 选 `FB_IotMqtt5ClientBase`（基类）——要把消息处理直接做到 driver 同步上下文里（最低延迟、最少一次拷贝）；或要在 connect/disconnect 时执行自定义逻辑；或要做扩展鉴权 `OnMqtt5Authentication`。

## 4. 错误码 / 返回值

错误体系与 `FB_IotMqtt5Client` 相同（`bError` + `hrErrorCode` + `eConnectionState`）。

callback 方法返回 `HRESULT`：① `OnMqtt5Message` —— `S_OK` 接受 / `S_FALSE` 下次重试；② `OnMqtt5ConnAck` —— InfoSys 未规定具体返回值含义，惯例填 `S_OK`；③ `OnMqtt5Disconnected` —— 惯例填 `S_OK`。

publish / subscribe / unsubscribe / request / response 返回 `BOOL`：调用本身是否成功（≠消息是否送达）。

## 5. 使用注意 / 常见坑

- **必须派生才能用**：直接实例化 `FB_IotMqtt5ClientBase` 本身的消息会被丢弃（基类默认 callback 是空实现）。生产代码必须 EXTENDS。
- **回调里不要做长耗时操作**：阻塞 ADS 调用、文件 IO、网络访问都会拖慢 PLC 周期。重操作把数据塞到自己维护的队列里，让另一个任务异步处理。
- **回调可重入**：一周期多消息会多次回调；共享状态要小心。
- **`OnMqtt5Message.repeated` 必须处理**：忽略它 = 消息可能被重复处理多次；业务需幂等。
- **PDF Syntax 块印刷错误**：5.1.2.2 段的 Syntax 块声明的是 `FUNCTION_BLOCK FB_IotMqtt5Client`（无 `Base`），但实际类型名是 `FB_IotMqtt5ClientBase`。InfoSys 同样保留此 typo。XAE 编译器以实际类型为准。
- **`OnMqtt5ConnAck` 方法签名印刷错误**：PDF 写成 `METHOD OnMqtt5Disconnected : HRESULT`——是排版错。实际方法名以章节标题 `OnMqtt5ConnAck` 为准。
- **基类没有 `fbConnAckProps` 输出**：要读 broker 能力（最大包大小等），重写 `OnMqtt5ConnAck` 在回调里通过 `pProps` 取——若用主类直接读输出即可。
- **`bConnect` 必须保持电平**：与所有 MQTT 客户端一致——电平 `TRUE` 维持连接，`FALSE` 触发 DISCONNECT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5ClientBase.TcPOU`](../examples/P_Demo_FB_IotMqtt5ClientBase.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

> 注：完整派生需要在 PLC 工程里新建一个 `FUNCTION_BLOCK MyMqttHandler EXTENDS FB_IotMqtt5ClientBase` 并重写 `OnMqtt5Message`；本 .TcPOU 演示文件直接实例化基类作为"快速骨架"（实际收到消息会被默认空实现丢弃），便于先验证连接行为。生产代码必须派生。

```iecst
// 演示基类骨架——实际使用必须派生并重写 OnMqtt5Message
PROGRAM P_Demo_FB_IotMqtt5ClientBase
VAR
    fbBase : FB_IotMqtt5ClientBase := (sClientId := 'PLC-Base', sHostName := '127.0.0.1');
    bRun   : BOOL := TRUE;
END_VAR
fbBase.Execute(bConnect := bRun);
// 直接实例化基类时 OnMqtt5Message 是空实现——消息全部丢弃
// 生产代码要：DECLARE fbDerived : MyMqttHandler;  且 MyMqttHandler 重写 OnMqtt5Message
```

## 7. 业务场景与实际价值

- **场景**：极致低延迟的边缘控制场景——例如自动光学检测（AOI）拍片后，上位机通过 MQTT 发"缺陷坐标"消息给 PLC，PLC 必须在 1-2 ms 内做出剔除/标记动作。回调直接执行业务代码可以省掉队列的一次入队 + 出队（约几十微秒），且保证消息处理与 driver 调用栈同步。
- **价值**：用户拿到对 MQTT 客户端行为的**最细粒度控制权**——可以在 connect 时跑自定义初始化（订阅一组动态计算的 topic）、disconnect 时跑清理逻辑（回滚未确认的状态）、auth 时实现 SASL/SCRAM 等扩展鉴权。`FB_IotMqtt5Client` 用方便但是黑盒；本基类用麻烦但可定制。
- **替代方案对比**：
  - 用 `FB_IotMqtt5Client` + 内嵌队列——开发简单、业务任务异步，但回调链路上多了一次入队-出队拷贝；
  - 自己包一层 wrapper 在外面同步——白白多一层，没必要；
  - **本 FB**：直接重写 callback——最低延迟、最大灵活度，但回调代码必须短小不阻塞。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.2（含子节 5.1.2.2.1 – 5.1.2.2.12 全部 12 个方法）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12560546699.html
- **相关 FB / DUT**：`FB_IotMqtt5Client`（带队列输出的主类）、`ST_IotMqtt5Will`、`ST_IotMqtt5Tls`、`ST_IotMqtt5Auth`、`ST_IotMqtt5Connect`、`FB_IotMqtt5ConnAckProperties`、`FB_IotMqtt5DisconnectProperties`、`FB_IotMqtt5PublishProperties`
