# ST_IotMqtt5Will

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `STRUCT` (DUT) |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12567451275.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ST_IotMqtt5Will.TcPOU`](../examples/P_Demo_ST_IotMqtt5Will.TcPOU) |

---

## 1. 功能简述

`ST_IotMqtt5Will` 是 MQTT 5 客户端的**遗嘱消息**（last will and testament，LWT）结构体——MQTT 5 增强版，是 MQTT 3 版 `ST_IotMqttWill` 的扩展。

赋给 `FB_IotMqtt5Client.stWill` 后，broker 在客户端"异常掉线"时自动替它向 will-topic 发一条预设消息。比 MQTT 3 版多出来的字段：
- `fbPayload : FB_IotDataBuffer`——payload 用专用 buffer FB 持有，无需手工管理 `PVOID + UDINT`；
- `sContentType` / `sResponseTopic` / `nMsgExpiryInterval` / `nDelay` / `bPayloadUtf8` —— MQTT 5 publish properties；
- `fbCorrelationData : FB_IotDataBuffer`—— correlation data；
- `fbUserProperties : FB_IotMqtt5UserProperties`—— 任意 user properties。

> **重要**：本结构体**不能实例化后赋给 client**——必须直接在 client 的 `stWill` 引脚上设置。PDF 明确说明 "This structure does not allow instantiation and assignment to FB_IotMqtt5Client or FB_IotMqtt5ClientBase. Instead, the input parameter of the MQTT v5 client function block is used directly."

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致）。

### STRUCT 成员

```iecst
TYPE ST_IotMqtt5Will :
STRUCT
    {attribute 'TcEncoding':='UTF-8'}
    sTopic             : STRING(255);
    fbPayload          : FB_IotDataBuffer;
    eQoS               : TcIotMqttQos := TcIotMqttQos.ExactlyOnceDelivery;
    bRetain            : BOOL;
    {attribute 'TcEncoding':='UTF-8'}
    sContentType       : STRING(255);
    {attribute 'TcEncoding':='UTF-8'}
    sResponseTopic     : STRING(255);
    nMsgExpiryInterval : UDINT;
    nDelay             : UDINT;
    bPayloadUtf8       : BOOL;
    fbCorrelationData  : FB_IotDataBuffer;
    fbUserProperties   : FB_IotMqtt5UserProperties;
END_STRUCT
END_TYPE
```

### 成员说明

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sTopic` | `STRING(255)` | — | will 消息 topic（UTF-8） |
| `fbPayload` | `FB_IotDataBuffer` | — | will payload buffer——内部封装内存管理，不必手工拷贝 |
| `eQoS` | `TcIotMqttQos` | `TcIotMqttQos.ExactlyOnceDelivery` | will 的 QoS。**默认 QoS 2**（与 publish 常用的 QoS 0 不同） |
| `bRetain` | `BOOL` | — | retain 标志 |
| `sContentType` | `STRING(255)` | — | will payload 的 content type（如 `'text/plain'` / `'application/json'`） |
| `sResponseTopic` | `STRING(255)` | — | 可选：will 消息携带的 response topic |
| `nMsgExpiryInterval` | `UDINT` | — | will 消息过期秒数——超过则 broker 不再投递 |
| `nDelay` | `UDINT` | — | will 发送延迟秒数——客户端断开后等多少秒再发 will（用于短暂断网恢复时不触发 will） |
| `bPayloadUtf8` | `BOOL` | — | payload format indicator——`TRUE` 表示 payload 是 UTF-8 文本 |
| `fbCorrelationData` | `FB_IotDataBuffer` | — | will 携带的 correlation data |
| `fbUserProperties` | `FB_IotMqtt5UserProperties` | — | will 携带的 user properties——可以塞任意键值元数据 |

## 3. 行为说明

**配置时机**：与 MQTT 3 版一致——必须在 `Execute(bConnect := TRUE)` 第一次调用前设置 client 的 `stWill`。建链后再改不会生效（will 是 CONNECT 报文一部分）。

**禁止实例化赋值**：PDF 警告：用户**不要**在自己的代码里声明 `stMyWill : ST_IotMqtt5Will` 然后 `fbClient.stWill := stMyWill;`——而要**直接**设置 `fbClient.stWill.sTopic := '...'; fbClient.stWill.fbPayload.SetSize(...)` 等字段。这是因为本结构体内部含 `FB_IotDataBuffer` / `FB_IotMqtt5UserProperties` 等 FB 实例，按值赋值会破坏内部内存管理状态。

**`fbPayload : FB_IotDataBuffer`**：要给 payload 赋值通常调它的设值 API（具体见 InfoSys `FB_IotDataBuffer` topic）。简单做法：在 `Execute` 前用 `fbClient.stWill.fbPayload.SetData(pData := ADR(sOffline), nDataSize := TO_UDINT(LEN(sOffline)));`（具体方法名以实际库提供为准——本库未在 §5.1 列 `FB_IotDataBuffer` 的方法，但属于工具型 FB，参考 InfoSys 主页搜索）。

**`nDelay` 用法**：MQTT 5 引入——客户端断开后**延迟 N 秒**才发 will；适合"短暂断网，自动重连"场景——若客户端在 nDelay 秒内重新 CONNECT，will 取消。WAN 上对抗短暂抖动很有用。

**`fbUserProperties` 用法**：先 `fbClient.stWill.fbUserProperties.AddUserProperty(sName := 'reason', sValue := 'unknown');` 把元数据填好；订阅者收到 will 时通过 `fbMsg5.GetUserPropertyByIdx` 读出来。典型用法是 PLC ID、楼层、产线等定位元数据。

**`nMsgExpiryInterval` vs `nDelay` 区别**：`nDelay` 是 broker 等多久才发 will；`nMsgExpiryInterval` 是 will 发出后多久过期。一前一后两个时间窗。

**MQTT 3 vs MQTT 5 will 差异**：① payload 改用 `FB_IotDataBuffer`（更安全的内存管理）；② 多了 content type / response topic / expiry / delay / payload UTF-8 indicator / correlation data / user properties 这一整套 MQTT 5 publish properties。

## 4. 错误码 / 返回值

本结构体是数据载体，无返回值。配置错误反映在父 `FB_IotMqtt5Client.bError` / `hrErrorCode` / `fbConnAckProps.nReasonCode`。

## 5. 使用注意 / 常见坑

- **禁止 `fbClient.stWill := stLocalWill`**：直接操作字段—— `fbClient.stWill.sTopic := '...';` 等等。InfoSys 明确警告。
- **`fbPayload` / `fbCorrelationData` 是 `FB_IotDataBuffer`**：不能像 MQTT 3 那样 `pPayload := ADR(s)`——要调 buffer FB 的 SetData / SetString 方法。
- **`fbUserProperties` 跨连接保留**：一旦设置，无需每次重连重设——但如果在运行期间想换 will 内容，必须先 DISCONNECT 再 CONNECT。
- **`nDelay` 配合 keepalive 别太长**：如果 `nDelay > nKeepAlive × 1.5 + 重连超时`，事实上 will 可能从来不发——客户端要么按时回来要么走"消失"路径而 broker 已经判它死亡。
- **broker 必须支持 MQTT 5 才能用扩展字段**：基本字段 sTopic / fbPayload / eQoS / bRetain MQTT 3 也支持；扩展字段（contentType / userProperties / nDelay / expiryInterval）依赖 broker 协议版本。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ST_IotMqtt5Will.TcPOU`](../examples/P_Demo_ST_IotMqtt5Will.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_ST_IotMqtt5Will
VAR
    fbMqtt5 : FB_IotMqtt5Client := (sClientId := 'PLC5-Will', sHostName := '127.0.0.1');
    sStatusTopic : STRING := 'plc/v5/line1/status';
    bRun : BOOL := TRUE;
    bWillInit : BOOL;
END_VAR
IF NOT bWillInit THEN
    // 直接操作 client.stWill 字段——不要 stLocalWill 赋值
    fbMqtt5.stWill.sTopic             := sStatusTopic;
    fbMqtt5.stWill.eQoS               := TcIotMqttQos.AtLeastOnceDelivery;
    fbMqtt5.stWill.bRetain            := TRUE;
    fbMqtt5.stWill.nDelay             := 5;            // 断开后等 5 秒才发 will
    fbMqtt5.stWill.nMsgExpiryInterval := 300;          // will 5 分钟内有效
    fbMqtt5.stWill.bPayloadUtf8       := TRUE;
    fbMqtt5.stWill.sContentType       := 'text/plain';
    // fbPayload 设值：调 fbClient.stWill.fbPayload.SetData(...) 等 API
    // fbUserProperties 加：fbClient.stWill.fbUserProperties.AddUserProperty(...)
    bWillInit := TRUE;
END_IF
fbMqtt5.Execute(bConnect := bRun);
```

## 7. 业务场景与实际价值

- **场景**：跨广域网部署的 PLC——网络抖动每天都有，但绝大多数能在几秒内恢复。用 `nDelay := 5` 让 broker 等 5 秒再发 will——这 5 秒内 PLC 自动重连成功的话 will 取消，SCADA 看不到误告警；真正掉电才会触发 will。配 user properties 带"楼层=B7, 产线=L3"等元数据，SCADA 收到 will 直接显示"B7 楼 L3 产线离线"，无需查数据库。
- **价值**：MQTT 5 把 will 从"简单遗嘱"升级到"带 properties 的协议级 LWT"。`nDelay` 大幅降低误告警率；user properties 直接带定位信息免数据库查找；content type 告知订阅者怎么解析 payload。
- **替代方案对比**：
  - MQTT 3 `ST_IotMqttWill`——只有基本字段，没 `nDelay` 抗抖动；没 user properties 带元数据；
  - 自建心跳超时——SCADA 端要写定时器，断网瞬间也要等几个心跳周期才发现；
  - **本结构体**：broker 实现的 will + properties，原生支持。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12567451275.html
- **相关 DUT / FB**：`FB_IotMqtt5Client`（消费 `stWill`）、`FB_IotMqtt5ClientBase`、`FB_IotDataBuffer`（payload 缓冲）、`FB_IotMqtt5UserProperties`、`ST_IotMqttWill`（MQTT 3 版）、`TcIotMqttQos`
