# FB_IotMqttClient

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT3` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3391835403.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqttClient.TcPOU`](../examples/P_Demo_FB_IotMqttClient.TcPOU) |

---

## 1. 功能简述

`FB_IotMqttClient` 是 Tc3_IotBase 库基于 **MQTT 协议 3.1.1 版本**的客户端功能块（FB），把 PLC 与一台 MQTT 消息代理（broker，例如 Mosquitto / EMQX / HiveMQ / AWS IoT Core / Azure IoT Hub）的全部交互——TCP 建链、CONNECT/CONNACK 握手、订阅 / 取消订阅、publish 发送、订阅消息回调、保活心跳、TLS 加密、断线重连——封装成一个 FB 实例 + 一系列方法调用。

**一个实例只能连一个 broker**：要同时连多个 broker（典型场景：本地工厂数采 + 云端云平台双链路）就实例化多份；每份必须由独立的 PLC 任务调用其 `Execute()` 方法（**禁止多个任务共用同一实例**，会出现不可预期的行为）。

接收消息有两种范式可选：① 在 VAR_INPUT 的 `ipMessageQueue` 接一个 `FB_IotMqttMessageQueue` 实例，订阅到的消息自动进 FIFO 队列，业务侧轮询出队即可；② 派生本 FB 并重写 `OnMqttMessage()` 回调方法，在回调里就地处理。两者只能选一种：当回调方法被重写后（即被派生子类覆盖），无论 `ipMessageQueue` 是否赋值都不会再走队列分发。

底层依赖 TwinCAT 的 MQTT 驱动；需要 **TF6701 license** 才能正常 publish/subscribe。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sClientId        : STRING(255);     // default is generated during initialization
    sHostName        : STRING(255) := '127.0.0.1'; // default is local host
    nHostPort        : UINT := 1883;    // default is 1883
    sTopicPrefix     : STRING(255);     // topic prefix for pub and sub of this client (handled internally)
    nKeepAlive       : UINT := 60;      // in seconds
    sUserName        : STRING(255);     // optional parameter
    sUserPassword    : STRING(255);     // optional parameter
    stWill           : ST_IotMqttWill;  // optional parameter
    stTLS            : ST_IotMqttTls;   // optional parameter
    ipMessageQueue   : I_IotMqttMessageQueue; // if received messages should be queued during call of Execute()
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sClientId` | `STRING(255)` | — | 客户端 ID。多数 broker 要求**唯一**，留空则 TwinCAT 驱动按 PLC 工程名自动生成 |
| `sHostName` | `STRING(255)` | `'127.0.0.1'` | broker 的主机名或 IP；不填走本机回环 |
| `nHostPort` | `UINT` | `1883` | broker 监听端口（明文 MQTT 默认 1883；TLS 一般 8883 — 但端口本身只跟 broker 配置走，并不强制使用 TLS） |
| `sTopicPrefix` | `STRING(255)` | — | 自动追加到本实例所有 publish/subscribe topic 前的前缀，由驱动内部处理；同一台 PLC 跑多实例分到不同 topic 空间时用 |
| `nKeepAlive` | `UINT` | `60` | 保活看门狗周期（秒）：超过 `nKeepAlive × 1.5` 没消息发出，broker 判客户端掉线（见 §3） |
| `sUserName` | `STRING(255)` | — | 可选的 broker 用户名 |
| `sUserPassword` | `STRING(255)` | — | 可选的 broker 密码 |
| `stWill` | `ST_IotMqttWill` | — | 可选的"遗嘱消息"：客户端异常掉线时由 broker 替它向 will-topic 发的最后一条消息（结构体见 `ST_IotMqttWill.md`） |
| `stTLS` | `ST_IotMqttTls` | — | 可选的 TLS 安全设置；要走 TLS 加密链路就填（结构体见 `ST_IotMqttTLS.md`） |
| `ipMessageQueue` | `I_IotMqttMessageQueue` | — | 可选的消息队列接口：传入一个 `FB_IotMqttMessageQueue` 实例后，订阅到的消息自动进队列；只在不打算重写 `OnMqttMessage()` 回调时使用（见 §3） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError           : BOOL;
    hrErrorCode      : HRESULT;
    eConnectionState : ETcIotMqttClientState;
    bConnected       : BOOL; // TRUE if connection to host is established
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出现错误时置 `TRUE`；与 `hrErrorCode` 配合查具体错误 |
| `hrErrorCode` | `HRESULT` | `bError = TRUE` 时给出 HRESULT 错误码（参考 PDF §7.2 ADS Return Codes） |
| `eConnectionState` | `ETcIotMqttClientState` | 客户端与 broker 的连接状态枚举（见 `ETcIotMqttClientState.md`），包括 `MQTT_ERR_SUCCESS` / `MQTT_ERR_NO_CONN` / `MQTT_ERR_TLS_*` 等具体细分原因 |
| `bConnected` | `BOOL` | TCP + CONNACK 全部完成、连接已建立时为 `TRUE`；这是判断"现在可以 publish / subscribe 了"的最直接信号 |

### VAR_IN_OUT

无。

### METHOD Execute

后台通信推进方法，**必须周期调用**。否则订阅消息收不到、连接也不会建。

```iecst
METHOD Execute
VAR_INPUT
    bConnect : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConnect` | `BOOL` | 置 `TRUE` 时驱动会维持/建立到 broker 的连接；置 `FALSE` 时主动断开。**必须保持高电平才能保连接**——拉低即断 |

### METHOD Publish

向 broker 发一条 MQTT 消息（一次调用对应一次 publish）。

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
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 目标 topic（UTF-8，大小写敏感） |
| `pPayload` | IN | `PVOID` | payload 起始地址（用 `ADR(变量)`） |
| `nPayloadSize` | IN | `UDINT` | payload 字节数（字符串用 `LEN()`；结构体用 `SIZEOF()`） |
| `eQoS` | IN | `TcIotMqttQos` | QoS 等级：`AtMostOnceDelivery`(0) / `AtLeastOnceDelivery`(1) / `ExactlyOnceDelivery`(2) |
| `bRetain` | IN | `BOOL` | `TRUE` 时 broker 把这条消息留作 retain，新订阅者订阅该 topic 时立即收到这条 |
| `bQueue` | IN | `BOOL` | 保留参数，固定填 `FALSE` |

返回值：`BOOL`——`TRUE` 调用成功（发送已进入驱动），可能的错误在 FB 实例的 `bError` / `hrErrorCode` 输出反馈。

### METHOD Subscribe

订阅一个 topic（同一实例可订阅多个 topic，多次调用即可）。

```iecst
METHOD Subscribe : BOOL
VAR_IN_OUT
    sTopic       : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
VAR_INPUT
    eQoS         : TcIotMqttQos; // quality of service between the publishing client and the broker
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 要订阅的 topic |
| `eQoS` | IN | `TcIotMqttQos` | 订阅时希望的最大 QoS |

返回值：`BOOL`——`TRUE` 表示订阅请求已交给驱动；不代表已完成 SUBACK（完成时由 broker 异步确认）。

### METHOD Unsubscribe

取消订阅指定 topic。

```iecst
METHOD Unsubscribe : BOOL
VAR_IN_OUT
    sTopic       : STRING; // topic string (UTF-8) with any length (attend that MQTT topics are case sensitive)
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `sTopic` | IN_OUT | `STRING` | 要取消订阅的 topic |

返回值：`BOOL`——`TRUE` 表示取消请求已交给驱动。

### METHOD OnMqttMessage（回调方法）

**用户不要直接调用**——重写它即可。`Execute()` 内部由 TwinCAT 驱动在收到消息时回调本方法，每条消息一次回调；同一 PLC 周期里有多条消息时多次回调，实现要考虑可重入。

```iecst
METHOD OnMqttMessage : HRESULT
VAR_IN_OUT CONSTANT
    topic    : STRING;
END_VAR
VAR_INPUT
    payload  : PVOID;
    length   : UDINT;
    qos      : TcIotMqttQos;
    repeated : BOOL;
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `topic` | IN_OUT CONSTANT | `STRING` | 收到消息的 topic |
| `payload` | IN | `PVOID` | payload 起始地址 |
| `length` | IN | `UDINT` | payload 字节数 |
| `qos` | IN | `TcIotMqttQos` | 该消息的 QoS |
| `repeated` | IN | `BOOL` | `TRUE` 表示这条消息上次回调时返回了 `S_FALSE`，本次重传——业务逻辑要做幂等防重 |

返回值：`HRESULT`——`S_OK` 表示接受；`S_FALSE` 表示要求 broker 在下次 `Execute()` 时把这条消息再发一遍（典型用法：用本周期内来不及处理）。

### METHOD ActivateExponentialBackoff

开启"指数退避"重连节流：连续重连失败时，重连间隔从 `tMqttBackoffMinTime` 每次翻倍，封顶到 `tMqttBackoffMaxTime`，连上一次后立刻复位回最小值。

```iecst
METHOD ActivateExponentialBackoff
VAR_INPUT
    tMqttBackoffMinTime: TIME;
    tMqttBackoffMaxTime: TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `tMqttBackoffMinTime` | `TIME` | 第一次重连失败后的初始等待 |
| `tMqttBackoffMaxTime` | `TIME` | 翻倍后的封顶等待——再多失败也按这个间隔重试 |

### METHOD DeactivateExponentialBackoff

关闭指数退避——回到默认的固定周期重连。

```iecst
METHOD DeactivateExponentialBackoff
```

无参数；无返回值。

### METHOD GetTimeSinceLastBrokerMessage

返回自上一条 broker 消息（包括 ping）到现在过去的毫秒数。每收到一条新消息（包括 ping）即清零。

```iecst
METHOD GetTimeSinceLastBrokerMessage : UDINT
```

无参数；返回 `UDINT`——距上次 broker 消息的毫秒数。

应用场景：MQTT 规范让客户端自己决定超时阈值；本方法是 PLC 侧的判定依据（与 broker 侧 `nKeepAlive × 1.5` 不同：那个是 broker 判客户端掉线，而本方法是客户端自己判 broker 安静多久算异常）。

## 3. 行为说明

**生命周期五步**：① 实例化时 VAR_INPUT 已被取值，但还没建链；② 业务任务里**每周期**调一次 `Execute(bConnect := TRUE)`，驱动后台启动 TCP + CONNECT；③ 几十毫秒后 `bConnected` 变 `TRUE`、`eConnectionState = MQTT_ERR_SUCCESS`，此时才可以 `Publish()` / `Subscribe()`；④ 业务期间继续每周期 `Execute()`，期间可任意次 `Publish()` / `Subscribe()` / `Unsubscribe()`；⑤ 停机前把 `bConnect` 拉 `FALSE`，再调一次 `Execute()` 完成 DISCONNECT。

**收消息两种模式**：默认走回调——派生 FB 并重写 `OnMqttMessage()`；或在 VAR_INPUT 给 `ipMessageQueue` 接一个 `FB_IotMqttMessageQueue` 实例，订阅消息进 FIFO，业务代码用 `fbQueue.Dequeue(REF=> fbMsg)` 出队。InfoSys 明确说：**回调一旦被重写就吃掉队列**——同时配两种不会"双发"。

**触发语义**：所有 publish / subscribe / unsubscribe 方法是"调用即执行"（不是上升沿），多次调用就多次执行；典型做法是用 `R_TRIG` 把按钮信号转一次上升沿后再调，避免每周期反复发同一条。

**保活机制**：`nKeepAlive` 秒内 PLC 没主动发消息，驱动会替它发 MQTT PINGREQ 让连接保活；broker 等 `nKeepAlive × 1.5` 还没收到消息则判客户端死亡，触发本客户端配置的 `stWill` 遗嘱消息发给订阅者。`nKeepAlive = 0` 表示不启用，仅当 broker 也支持 0 时可用。

**错误观测**：`bError` 立刻置位，`hrErrorCode` 给出 HRESULT；`eConnectionState` 进一步细分到 `MQTT_ERR_NO_CONN`（还没连上）/ `MQTT_ERR_CONN_LOST`（连过又断了）/ `MQTT_ERR_TLS_VERIFY_FAIL`（TLS 证书验证失败）/ `MQTT_ERR_AUTH`（用户名密码错）等具体语义。诊断时 `eConnectionState` 比 `hrErrorCode` 更直观。

**指数退避典型用法**：跨广域网到云端 broker 时启用——连接抖动时不让 PLC 每秒都重试给 broker 增负，又不至于断连后等几分钟才恢复。本地局域网 broker 通常用不上。

## 4. 错误码 / 返回值

错误以两路输出：① `bError` + `hrErrorCode`（HRESULT 形式）；② `eConnectionState`（细分枚举）。详细 `hrErrorCode` 取值参 PDF §7.2 ADS Return Codes 一节。

`eConnectionState` 关键取值（完整列表见 `ETcIotMqttClientState.md`）：

| 取值 | 含义 | 排查方向 |
|---|---|---|
| `MQTT_ERR_SUCCESS` | 连接正常 | — |
| `MQTT_ERR_NO_CONN` | 还没连上 broker | 检查 `sHostName` / `nHostPort` / 防火墙 / broker 是否启动 |
| `MQTT_ERR_CONN_REFUSED` | broker 主动拒绝连接 | 多半是用户名/密码、客户端 ACL、客户端 ID 已被占用 |
| `MQTT_ERR_CONN_LOST` | 连接被对端中断 | 网络抖动、broker 重启、`nKeepAlive` 设得太短 |
| `MQTT_ERR_TLS_VERIFY_FAIL` | TLS 证书验证失败 | 检查 `stTLS.sCA` 是不是真正签发服务端证书的 CA；服务端证书是否过期 |
| `MQTT_ERR_AUTH` | 认证失败 | 用户名/密码错或 broker 不允许该 ClientId |
| `MQTT_ERR_PAYLOAD_SIZE` | publish 的 payload 超过限制 | 调整 `cMaxSizeOfMqttMessage`（参数表）或减小消息 |

各方法的 `BOOL` 返回值含义：`TRUE` 表示**调用本身**成功（请求已交给驱动）；不等于"消息已确认送达"——异步确认仍要看 `bError`/`hrErrorCode`。

## 5. 使用注意 / 常见坑

- **`Execute()` 必须周期调用**：漏调一次都会丢消息或导致连接判定异常。建议放在 PLC 任务的固定位置（不要藏在条件分支里）。
- **单实例单任务**：PDF 明确警告"每个实例同时只能由一个任务调用"。多任务并发调用会出现 race condition。
- **`bConnect` 必须保持电平**：不是上升沿触发——一拉低就触发 DISCONNECT。要"建一次连一直保"就写常值 `TRUE`。
- **payload 内存寿命**：传给 `Publish()` 的 `pPayload` 指针指向的变量必须在 publish 真正发完之前保持有效；最稳妥的做法是用全局变量或 FB 内部 `VAR` 持有。
- **遗嘱消息要先填好**：`stWill.sTopic` / `stWill.pPayload` 必须在 `Execute(bConnect := TRUE)` 第一次连上前就设好；建立连接后再改不会生效（will 是 CONNECT 报文的一部分）。
- **TLS 默认要校验服务端证书**：`stTLS.bNoServerCertCheck` 默认是 `FALSE`，禁止在生产环境改成 `TRUE`（中间人攻击窗口）。仅调试连内部测试 broker 时临时打开。
- **回调里别做长耗时操作**：`OnMqttMessage()` 是在 `Execute()` 调用栈里同步执行的，长耗时会拖慢 PLC 任务周期。重操作（写库、ADS 远程读写）走异步消息队列。（工程经验补充）
- **不要在 `bConnected = FALSE` 时调 `Publish` / `Subscribe`**：调用会失败，浪费 PLC 周期；先用 `bConnected` 作 enable 门控。（工程经验补充）
- **`sClientId` 不唯一会被踢**：多数 broker（含 AWS IoT Core / Azure IoT Hub）规定同 ClientId 第二次连上会把第一次踢下线。多 PLC 上线时 ClientId 要带机器序列号。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqttClient.TcPOU`](../examples/P_Demo_FB_IotMqttClient.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行例程见上述 .TcPOU 文件；下面给出最小调用骨架以便快速理解：

```iecst
// 演示：连本地 Mosquitto broker 1883，订阅 plc/heartbeat，每 5 秒 publish 一次心跳
PROGRAM P_Demo_FB_IotMqttClient
VAR
    fbMqtt           : FB_IotMqttClient := (sClientId := 'PLC001', sHostName := '127.0.0.1', nHostPort := 1883);
    fbHeartbeatQueue : FB_IotMqttMessageQueue;
    sHeartbeatTopic  : STRING := 'plc/heartbeat';
    sPayload         : STRING(80) := 'alive';
    tonHeartbeat     : TON := (PT := T#5S);
    bStartConnect    : BOOL := TRUE;
END_VAR

// 把队列接到 FB 输入（订阅消息进 FIFO；不重写 OnMqttMessage 时用这种方式）
fbMqtt.ipMessageQueue := fbHeartbeatQueue;

// 周期调用：维持连接
fbMqtt.Execute(bConnect := bStartConnect);

// 连上后：先订阅、再定时 publish
IF fbMqtt.bConnected THEN
    fbMqtt.Subscribe(sTopic := sHeartbeatTopic, eQoS := TcIotMqttQos.AtMostOnceDelivery);
    tonHeartbeat(IN := TRUE);
    IF tonHeartbeat.Q THEN
        tonHeartbeat(IN := FALSE);
        fbMqtt.Publish(sTopic := sHeartbeatTopic,
                       pPayload := ADR(sPayload), nPayloadSize := TO_UDINT(LEN(sPayload)),
                       eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := FALSE, bQueue := FALSE);
    END_IF
END_IF
```

## 7. 业务场景与实际价值

- **场景**：CX 工控机做边缘网关，向云端（AWS IoT / Azure IoT / 自建 Mosquitto / 工厂级 EMQX）实时上报产线状态、订阅来自 MES / SCADA 的下行命令；典型工况包括：每秒上报温度、扭矩等遥测；OEE 看板每分钟更新；HMI 按钮触发 publish 启停命令；远端配方下发到 PLC 等。
- **价值**：把"建 TCP/TLS → 写 MQTT CONNECT → 维持心跳 → 编解码 publish / subscribe → 异常重连"这套 MQTT 客户端协议栈，全收进一个 FB 实例 + 5 个方法。业务代码只需关心 broker 地址、topic、payload；不必处理 MQTT 报文格式、不必自己写心跳定时器、不必自己写 TLS handshake。和走 ADS / 自定义 TCP / FTP 上传相比，MQTT 的发布订阅模型天然支持"一对多分发"和"多对一汇聚"，云端 broker 上千个 PLC 也能聚合。
- **替代方案对比**：
  - 自己用 `FB_SocketConnect`（Tc2_TcpIp）裸 socket 实现 MQTT 协议——必须自己写 CONNECT/CONNACK/PUBLISH/SUBSCRIBE 报文打包、QoS 1/2 确认逻辑、PINGREQ 心跳，工作量数千行；
  - 用 OPC UA（Tc3_PLCopen_OpcUa）——协议重，需对端也实现 OPC UA，云平台支持不如 MQTT 广；
  - 用 Tc3_IotCommunicator（专用于和 TwinCAT IoT Communicator app 配对的协议）——仅对接 Beckhoff 自家产品；
  - 用 HTTP REST（`FB_IotHttpClient` 在 Tc3_IotBase_Http）——请求响应模式，没法订阅推送，下行命令必须 PLC 轮询；
  - 用 MQTT 5（本库 §5.1.2 `FB_IotMqtt5Client`）——MQTT 5 引入 user properties / topic alias / reason code / request-response 等高级特性，但要求 broker 支持 5.0；老 broker 只支持 3.1.1 时仍要走本 FB。
- **本 FB 适用边界**：必须装 TF6701 license；payload 默认上限 100 KB；多 MB 大文件不适合走 MQTT（用 HTTP / SFTP 更合适）。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.1.1（含子节 5.1.1.1.1 – 5.1.1.1.8 全部 8 个方法）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3391835403.html
- **相关 FB / DUT**：`ST_IotMqttWill`（遗嘱消息）、`ST_IotMqttTls`（TLS 设置）、`FB_IotMqttMessageQueue`（消息队列）、`FB_IotMqttMessage`（消息容器）、`ETcIotMqttClientState`（连接状态枚举）、`FB_IotMqtt5Client`（MQTT 5 版本，本库 §5.1.2.1）
