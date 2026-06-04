# FB_IotMqtt5PublishProperties

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5 Properties` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13961526539.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5PublishProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5PublishProperties.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5PublishProperties` 是 MQTT 5 客户端**发送 publish / request / response 消息时附带 properties** 的容器功能块。`EXTENDS FB_IotMqtt5UserProperties`——同时承担 user properties 的管理职能。

业务侧的典型用法：
1. 声明 `fbPubProps : FB_IotMqtt5PublishProperties;` 实例
2. 设字段（content type / topic alias / message expiry / payload UTF-8 indicator / user properties）
3. 调 `fbPubProps.SetPublishProperties(...)` 把字段固化
4. 把 `fbPubProps.pPublishProperties`（属性，不是 method）作为 `pProps` 参数传给 `fbClient.Publish` / `Request` / `Response`

支持的 publish properties 字段（MQTT 5 协议级）：Content Type、Topic Alias、Subscription Identifier、Message Expiry Interval、Payload UTF-8 Indicator、User Properties。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError           : BOOL;
    hrErrorCode      : HRESULT;
END_VAR
```

### VAR_IN_OUT

无。

### Property

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `bPayloadUtf8` | `BOOL` | Get / Set | 声明 payload 是不是 UTF-8 文本 |
| `bTopicAlias` | `BOOL` | Get / Set | 是否使用 topic alias |
| `nMsgExpiryInterval` | `UDINT` | Get / Set | 消息过期秒数——超过 broker 不再投递 |
| `nSubIdCnt` | `UINT` | Get | subscription identifier 个数（用 GetSubIds 取） |
| `pPublishProperties` | `POINTER TO MqttPublishProperties` | Get | 内部 properties 结构指针——传给 `fbClient.Publish/Request/Response` 的 `pProps` 参数 |
| `sContentType` | `STRING` | Get / Set | content type 字符串（如 `'application/json'` / `'text/plain'`） |

### Method

| 方法 | 用途 |
|---|---|
| `GetSubIds` | 取 subscription identifier 列表 |
| `SetPublishProperties` | 把当前各 Set 属性写入内部 `MqttPublishProperties` 结构 |

PDF 仅列方法名 / 用途，签名详情见 InfoSys topic 13961526539 或 IntelliSense。

## 3. 行为说明

**典型使用流**：
1. `fbPubProps.bPayloadUtf8 := TRUE;`（payload 是 UTF-8 文本）
2. `fbPubProps.sContentType := 'application/json';`
3. `fbPubProps.nMsgExpiryInterval := 300;`（消息 5 分钟内有效）
4. `fbPubProps.AddUserProperty(sName := 'trace-id', sValue := 'abc-123');`（继承自 `FB_IotMqtt5UserProperties` 的方法）
5. `fbPubProps.SetPublishProperties();`（固化）
6. `fbClient.Publish(..., pProps := fbPubProps.pPublishProperties);`

**`pPublishProperties` 是属性不是方法**：访问时不带括号——`fbPubProps.pPublishProperties`。返回内部结构地址。

**topic alias 用法**：先在 `fbClient.stConnect.nTopicAliasMax` 申请支持 N 个 alias，发布时调 `fbPubProps.bTopicAlias := TRUE;`——driver 自动给 topic 分 alias，第二次发同 topic 用 alias 代替字符串节省带宽。具体 alias 编号由 driver 内部管理。

**Subscription Identifier**：MQTT 5 让 subscribe 时声明一个数字 ID（`FB_IotMqtt5SubscribeProperties.nSubId`），broker 在转发匹配该订阅的消息时回带这个 ID。`GetSubIds` 让 publish 侧知道本消息要进哪些订阅——多 publisher 共享一个订阅但要按 sub ID 路由时用。

**`nMsgExpiryInterval` 适合临时数据**：例如下发一条"5 秒内有效"的 setpoint——超时 broker 不再投递，避免给短暂掉线后恢复的客户端发陈旧数据。

**`bPayloadUtf8` 是声明不是强制**：publisher 声明 payload 是 UTF-8——subscriber 通过 `fbMsg5.bPayloadUtf8` 读到这个声明决定怎么解析。不影响 broker 转发。

## 4. 错误码 / 返回值

输出 `bError` / `hrErrorCode`：本 FB 自身极少出错；`SetPublishProperties` 可能因 properties 结构内存不够返回失败。

## 5. 使用注意 / 常见坑

- **`pPublishProperties` 不带括号**：是 property，不是 method 调用。写 `fbProps.pPublishProperties()` 编译器会报错。
- **`SetPublishProperties` 要在每次 publish 前调**：如果改了 properties 但忘了 SetPublishProperties，driver 拿到的还是上次固化的版本。安全做法是 publish 前必跑。
- **`bTopicAlias := TRUE` 但客户端没声明 nTopicAliasMax**：`stConnect.nTopicAliasMax = 0` 时 broker 不接受 alias 类 publish。
- **`nMsgExpiryInterval` 单位是秒**：不是毫秒。
- **添加太多 user properties 会拖慢**：MQTT 协议层串行化每个 user property 都要时间；推荐 ≤ 5 个 user property，最多受 GVL `cMaxMqtt5UserProps`（20）限制。
- **content type 受 GVL 字符串长度限制**：`cSizeOfMqtt5ContentType`（默认 256 字节）；超长会被截断。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5PublishProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5PublishProperties.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示 publish JSON 时附 content-type + trace-id user property
PROGRAM P_Demo_FB_IotMqtt5PublishProperties
VAR
    fbClient   : FB_IotMqtt5Client := (sClientId := 'PLC5', sHostName := '127.0.0.1');
    fbPubProps : FB_IotMqtt5PublishProperties;
    sPayload   : STRING(80) := '{"sensor":"L1","value":42.0}';
    sTopic     : STRING := 'plc/v5/L1/telemetry';
    bPubInit   : BOOL;
END_VAR
fbClient.Execute(bConnect := TRUE);
IF fbClient.bConnected THEN
    IF NOT bPubInit THEN
        fbPubProps.bPayloadUtf8       := TRUE;
        fbPubProps.sContentType       := 'application/json';
        fbPubProps.nMsgExpiryInterval := 60;
        fbPubProps.SetPublishProperties();
        bPubInit := TRUE;
    END_IF
    fbClient.Publish(sTopic := sTopic,
                     pPayload := ADR(sPayload), nPayloadSize := TO_UDINT(LEN(sPayload)),
                     eQoS := TcIotMqttQos.AtMostOnceDelivery, bRetain := FALSE, bQueue := FALSE,
                     pProps := fbPubProps.pPublishProperties);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：PLC 上报遥测时带分布式追踪元数据——每条消息带 trace-id user property（MES 端能追踪从 PLC 到看板的整条链路）+ content-type 让消费者知道 payload 是 JSON；同时设 `nMsgExpiryInterval := 60` 让 broker 5 分钟后丢弃过期遥测——避免发给临时掉线后恢复的订阅者过时数据。
- **价值**：MQTT 3 时代元数据只能塞 payload（耦合应用协议），现在用 properties 与 payload 分离——业务代码读 / 写 properties 像调对象方法，与 payload 编码细节解耦。trace-id / content-type / expiry 是分布式追踪、链路诊断、临时数据控制的标配。
- **替代方案对比**：
  - 把元数据塞 payload JSON——破坏 publish/subscribe 解耦原则；
  - 把元数据塞 topic 字符串——topic 爆炸，broker 路由表撑大；
  - **本 FB**：协议级原生支持，properties / payload 完全分离。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.9.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13961526539.html
- **相关 FB**：`FB_IotMqtt5Client.Publish / Request / Response`（消费 `pProps`）、`FB_IotMqtt5UserProperties`（基类）、`FB_IotMqtt5SubscribeProperties`（订阅侧对偶）
