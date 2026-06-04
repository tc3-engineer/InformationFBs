# FB_IotMqtt5SubscribeProperties

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5 Properties` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13963958795.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5SubscribeProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5SubscribeProperties.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5SubscribeProperties` 是 MQTT 5 客户端**调 Subscribe 时附带 properties** 的容器功能块。`EXTENDS FB_IotMqtt5UserProperties`——同时承担 user properties 的管理职能。

支持的 MQTT 5 subscribe properties：
- **No Local**：订阅者不接收自己发的消息（同 client 同时既 publish 又 subscribe 同一 topic 时避免回环）
- **Retain As Published**：保留 publisher 原始 retain 标志（不是 broker 把所有非 retain 收到的都置 FALSE）
- **Retain Handling**：控制 broker 发送 retain 消息的策略（0 = 总发 / 1 = 仅新订阅时发 / 2 = 不发）
- **Subscription Identifier**：订阅 ID——broker 在转发匹配该订阅的消息时回带，便于业务侧路由

业务侧的典型用法：声明 `fbSubProps : FB_IotMqtt5SubscribeProperties;` 实例 → 设字段 → `SetSubscribeProperties()` → `pProps := fbSubProps.pSubscribeProperties` 传给 `fbClient.Subscribe(..., pProps := ...)`。

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
| `bNoLocal` | `BOOL` | Get / Set | `TRUE` 让 broker 不要把本 client 发的 publish 投递回本 client 的订阅 |
| `bRetainAsPublished` | `BOOL` | Get / Set | `TRUE` 保留 publisher 原始 retain 标志；`FALSE` broker 投递时把所有非 retain 收到的 retain 标志清掉 |
| `nRetainHandling` | `BYTE` | Get / Set | retain 消息发送策略：`0` = subscribe 时立即发（MQTT 3 默认行为）；`1` = 仅当订阅是**新订阅**时发（之前订阅过同 topic 不发）；`2` = 不发 retain 消息 |
| `nSubId` | `UDINT` | Get / Set | 订阅标识符——broker 在转发匹配本订阅的消息时回带，让业务侧能路由 |
| `pSubscribeProperties` | `POINTER TO MqttSubscribeProperties` | Get | 内部 properties 结构指针——传给 `fbClient.Subscribe` 的 `pProps` 参数 |

### Method

| 方法 | 用途 |
|---|---|
| `SetSubscribeProperties` | 把当前各 Set 属性写入内部 `MqttSubscribeProperties` 结构 |

PDF 仅列方法名 / 用途，具体签名见 InfoSys topic 13963958795 或 IntelliSense。

## 3. 行为说明

**典型使用流**：
1. `fbSubProps.bNoLocal := TRUE;`
2. `fbSubProps.nSubId := 100;`（业务侧自定义订阅 ID）
3. `fbSubProps.SetSubscribeProperties();`
4. `fbClient.Subscribe(sTopic := ..., eQoS := ..., pProps := fbSubProps.pSubscribeProperties);`

**`bNoLocal` 用法**：同一个 client 既订阅 `plc/cmd` 又向 `plc/cmd` publish 时——若不开 noLocal，自己 publish 的消息会被自己订阅收到，造成回环。`bNoLocal := TRUE` 让 broker 把"本 client 发的消息"过滤掉再投递。

**`bRetainAsPublished` 用法**：默认 broker 投递 retain 消息时把 retain 标志清掉（这是 MQTT 3 兼容行为）。`bRetainAsPublished := TRUE` 让 broker 保留 publisher 原始 retain 标志——subscriber 收到时通过 `fbMsg5.bTopicAlias`（或类似途径）能区分"这是 retain 消息" vs "这是新消息"。SCADA 启动时拉取 retain 状态恢复需要这个。

**`nRetainHandling` 三个值的实际差异**：
- `0` = 总发——每次 SUBSCRIBE 都把现存 retain 发一次。重连后会重新收到（典型 SCADA 重启拉状态）；
- `1` = 仅新订阅时发——同 ClientId 之前订阅过的 topic 不再发 retain。配 persistent session 用，避免每次重连都"刷屏"；
- `2` = 不发——纯订阅新消息流。适合"只关心今后"的实时报警场景。

**`nSubId` 用法**：业务侧给本 SUBSCRIBE 编号——broker 在每条匹配本订阅的转发消息里回带 `MqttPublishProperties.aSubIds`。`FB_IotMqtt5Message.nSubIdCnt` + `GetSubIds()` 能让接收侧知道"本消息匹配了哪个订阅 ID"。多 SUBSCRIBE 后业务侧用 ID 做 O(1) 路由（比 `CompareTopic` 一组字符串还快）。

**broker 必须支持**：`bSubIdAvailable = FALSE` 时 broker 拒绝带 SubId 的 SUBSCRIBE；`bRetainAsPublished` / `bNoLocal` 可能也不一定支持——`fbConnAckProps` 没明确暴露这两项的支持位，但若 broker 收到不认识的 property 会回错。

**与 `pSubscribeProperties` 的访问**：和 `FB_IotMqtt5PublishProperties` 一样——`pSubscribeProperties` 是 property（不带括号），返回内部结构地址。

## 4. 错误码 / 返回值

输出 `bError` / `hrErrorCode`：本 FB 自身错误极少；broker 拒绝 SUBSCRIBE 时通过 `fbClient.bError` / SUBACK 的 reason code 反映。

## 5. 使用注意 / 常见坑

- **`nRetainHandling = 1` 配 persistent session 才有意义**：clean session 的话所有 SUBSCRIBE 都是"新"的，效果同 `0`。
- **`bNoLocal` 对 shared subscription 不适用**：MQTT 5 规范明确禁止（防 shared sub 内部混乱）。
- **`nSubId = 0` 与未设置等效**：0 是 protocol 的"无 SubId"标记；要用 SubId 路由必须 ≥ 1。
- **subscribe properties 不适合每次 SUBSCRIBE 改**：同一 client 多次 SUBSCRIBE 不同 topic 但同一组 properties——`SetSubscribeProperties()` 后可以多次复用 `pSubscribeProperties` 指针。
- **`pSubscribeProperties` 不带括号**：和 publish 版本一致——property，不是 method。
- **broker 不支持某 property 时的行为**：MQTT 5 规范说不认识就忽略；但部分严格 broker 直接拒 SUBSCRIBE。生产侧要 fallback。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5SubscribeProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5SubscribeProperties.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_IotMqtt5SubscribeProperties
VAR
    fbClient   : FB_IotMqtt5Client := (sClientId := 'PLC5', sHostName := '127.0.0.1');
    fbSubProps : FB_IotMqtt5SubscribeProperties;
    fbTrig     : R_TRIG;
END_VAR
fbClient.Execute(bConnect := TRUE);
fbTrig(CLK := fbClient.bConnected);
IF fbTrig.Q THEN
    fbSubProps.bNoLocal           := TRUE;        // 不收自己 publish 的回环
    fbSubProps.bRetainAsPublished := TRUE;        // 保留 publisher 原 retain
    fbSubProps.nRetainHandling    := 1;           // 仅新订阅发 retain
    fbSubProps.nSubId             := 42;          // 业务自定义订阅 ID
    fbSubProps.SetSubscribeProperties();
    fbClient.Subscribe(sTopic := 'plc/v5/cmd',
                       eQoS   := TcIotMqttQos.AtLeastOnceDelivery,
                       pProps := fbSubProps.pSubscribeProperties);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：PLC 同时订阅 `plc/v5/cmd`（id=42）和 `plc/v5/recipe`（id=43），消息到达后用 `fbMsg5.GetSubIds()` 直接知道是哪个订阅——业务侧不需要再 `CompareTopic` 字符串比较，O(1) 路由分发。
- **价值**：`nSubId` 是 MQTT 5 引入的"业务路由 ID"——比 topic 字符串比较快、抗 topic 改名（业务订阅 ID 不变，topic 可以重新映射）；`bNoLocal` 避免同 client 自 publish-self-subscribe 回环；`bRetainAsPublished` + `nRetainHandling = 1` 让 SCADA 启动时只拉一次 retain 状态而不是每次断网重连都收一波。
- **替代方案对比**：
  - MQTT 3——没有 SubId 路由、没有 noLocal、retain 行为不可配；
  - 业务侧自己维护 topic→handlerID 映射表——映射变更要改代码；
  - **本 FB**：properties 在协议层声明，broker 端配合实现。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.9.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13963958795.html
- **相关 FB**：`FB_IotMqtt5Client.Subscribe`（消费 `pProps`）、`FB_IotMqtt5UserProperties`（基类）、`FB_IotMqtt5PublishProperties`（publish 侧对偶）、`FB_IotMqtt5Message`（GetSubIds 读 SubId）
