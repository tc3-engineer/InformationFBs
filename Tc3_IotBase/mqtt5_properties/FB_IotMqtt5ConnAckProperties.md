# FB_IotMqtt5ConnAckProperties

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5 Properties` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13964180235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5ConnAckProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5ConnAckProperties.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5ConnAckProperties` 是 MQTT 5 客户端收到 broker **CONNACK** 后用于读取 broker 返回的 properties 的功能块。`EXTENDS FB_IotMqtt5UserProperties`——所以同时具有 user properties 的访问能力。

`FB_IotMqtt5Client` 在 VAR_OUTPUT 区已经内嵌一个本 FB 实例（字段名 `fbConnAckProps`），业务侧**直接访问** `fbClient.fbConnAckProps.<属性>` 即可，不需要单独实例化。

通过本 FB 读到的 broker 信息包括："broker 支持的最大包大小"、"broker 是否支持 retain"、"broker 是否支持 wildcard 订阅"、"broker 实际给的 session expire 时长"、"broker 自动分配的 ClientId"、"broker 推荐的 server reference 地址"等。客户端**必须**在连接建立后读这些字段做自适应——若 broker 限制比客户端预期严，要降低 publish 频率 / 缩短消息 / 禁用 wildcard 订阅。

存在性指示：`bPropertiesAvailable = TRUE` 时本 FB 持有有效数据。

## 2. 接口定义

### VAR_INPUT

无（仅有从 `FB_IotMqtt5UserProperties` 继承的接口）。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError           : BOOL;
    hrErrorCode      : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错置 `TRUE` |
| `hrErrorCode` | `HRESULT` | HRESULT 错误码 |

### VAR_IN_OUT

无。

### Property（只读属性）

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `bPropertiesAvailable` | `BOOL` | Get | 本 FB 是否持有有效数据。`TRUE` = 已收到 CONNACK 且 broker 给了 properties |
| `bRetainAvailable` | `BOOL` | Get | broker 是否支持 retain 消息 |
| `bServerKeepAlive` | `BOOL` | Get | broker 是否用了与客户端声明不同的 keepalive 值 |
| `bSessionPresent` | `BOOL` | Get | 客户端是否已有 session 存在（断后重连恢复 session） |
| `bSharedSubAvailable` | `BOOL` | Get | broker 是否支持 shared subscriptions |
| `bSubIdAvailable` | `BOOL` | Get | broker 是否支持 Subscription Identifiers |
| `bWildcardSubAvailable` | `BOOL` | Get | broker 是否支持 wildcard (`+` / `#`) 订阅 |
| `nAuthDataSize` | `UINT` | Get | broker 返回的鉴权数据字节数 |
| `nMaxPackateSize` | `UDINT` | Get | broker 支持的最大 control packet 字节数。**注意 PDF 拼写 `nMaxPackateSize` 含字母颠倒——是 typo，但是 API 真实名字** |
| `nMaxQoS` | `BYTE` | Get | broker 支持的最大 QoS 等级（部分简化 broker 不支持 QoS 2） |
| `nReasonCode` | `BYTE` | Get | broker 在 CONNACK 里给的 reason code（`0` = 成功；非 0 表示拒绝原因） |
| `nReceiveMax` | `UINT` | Get | broker 同时能处理的 QoS 1+2 publish 数 |
| `nResponseInfoSize` | `UINT` | Get | response info 字节数 |
| `nSessionExpiryInterval` | `UDINT` | Get | broker 实际给的 session expire 秒数（与客户端 `stConnect.nSessionExpire` 声明协商后的结果） |
| `nTopicAliasMax` | `UINT` | Get | broker 支持的最大 topic alias 数 |
| `sAssignedClientId` | `STRING` | Get | 若客户端没指定 ClientId，broker 自动分配的 ID |
| `sAuthMethod` | `STRING` | Get | broker 返回的鉴权方法名 |
| `sReasonString` | `STRING` | Get | reason code 的可读说明 |
| `sServerReference` | `STRING` | Get | broker 推荐切换的服务器地址（用于 reason code 0x9C "Use Another Server" / 0x9D "Server moved"） |

### Method（PDF 列在 Methods 表里）

| 方法 | 用途 |
|---|---|
| `GetAuthData` | 返回 broker 鉴权数据（按 method 不同含义不同） |
| `GetResponseInfo` | 取 response info——broker 推荐给客户端用作 response topic 基础 |
| `SetConnAckProperties` | 设置本 FB 持有的 ConnAck properties（一般供 driver 内部用） |

InfoSys 未提供 §5.1.2.9.1 之外这些方法的完整签名；具体参数查 InfoSys topic 13964180235 或 IntelliSense。

## 3. 行为说明

**生命周期**：① PLC 调 `fbClient.Execute(bConnect := TRUE)` 第一次连上时，broker 在 CONNACK 报文里携带一组 properties；② driver 把 properties 解到内嵌的 `fbConnAckProps` 实例；③ 业务侧在 `bConnected = TRUE` 之后立即读 `fbClient.fbConnAckProps.<属性>` 做自适应；④ 之后若客户端 DISCONNECT 后再 CONNECT，新的 CONNACK 内容会覆盖旧值。

**关键自适应字段**：① `nMaxPackateSize`——决定 publish 单条上限；② `bRetainAvailable`——若 `FALSE` 业务侧的 `bRetain := TRUE` 会被 broker 拒绝；③ `bWildcardSubAvailable`——若 `FALSE` 不能用 `+` / `#` 订阅；④ `nMaxQoS`——若 broker 给 `1`，业务侧用 `QoS 2` publish 会失败；⑤ `bSessionPresent`——`TRUE` 表示 broker 找到了上次的 session，客户端不需要重新 SUBSCRIBE。

**broker 推荐切换地址**：当 `nReasonCode = 0x9C` (Use Another Server) 或 `0x9D` (Server moved) 时，`sServerReference` 给出 broker 推荐的新地址；客户端应该断开当前连接并连那个新地址。常用于 broker 集群的负载均衡和迁移。

**PDF 拼写错误**：`nMaxPackateSize` 字段名含字母颠倒（应该是 `nMaxPacketSize`），但 InfoSys 和 PLC 工程里的实际 API 名字就是这个含 typo 的版本——必须按这个拼写访问。

**`EXTENDS FB_IotMqtt5UserProperties`**：本 FB 同时持有 broker 在 CONNACK 里附带的 user properties——用 `fbConnAckProps.nUserPropertyCnt` 和 `GetUserPropertyByIdx(...)` 访问（参考 `FB_IotMqtt5UserProperties.md`）。

## 4. 错误码 / 返回值

输出 `bError` / `hrErrorCode`：本 FB 本身极少出错；错误一般是 driver 解析 CONNACK 失败（broker 报文格式异常等）。

`nReasonCode` 是**协议级** reason code（来自 broker）：
- `0x00` = Success
- `0x80` = Unspecified Error
- `0x81` = Malformed Packet
- `0x82` = Protocol Error
- `0x83` = Implementation Specific Error
- `0x84` = Unsupported Protocol Version
- `0x85` = Client Identifier Not Valid
- `0x86` = Bad UserName or Password
- `0x87` = Not Authorized
- `0x88` = Server Unavailable
- `0x89` = Server Busy
- `0x8A` = Banned
- `0x8C` = Bad Authentication Method
- `0x95` = Packet Too Large
- `0x97` = Quota Exceeded
- `0x9C` = Use Another Server
- `0x9D` = Server Moved

完整列表见 MQTT 5 规范 §3.2.2.2。

## 5. 使用注意 / 常见坑

- **API 名字含 typo**：`nMaxPackateSize`（实际拼写）——别按"标准"`nMaxPacketSize` 写。
- **`bPropertiesAvailable = FALSE` 时其他字段无效**：CONNACK 还没收到或 broker 没给 properties。先判断 `bPropertiesAvailable` 再读其他字段。
- **`nMaxPackateSize = 0` 表示"不限制"**：不是字面"0 字节"。
- **`bWildcardSubAvailable = FALSE` 时调 Subscribe 用通配符会失败**：`fbClient.Subscribe(sTopic := 'plc/+/cmd')` 返回 `TRUE` 但 broker 在 SUBACK 里给 reason code = 0xA2 Wildcard Subscriptions Not Supported；业务侧要为非通配模式准备 fallback。
- **`bSessionPresent` 反映 broker 端 session 状态**：`TRUE` = broker 找到了之前的 session（client 用同 ClientId 连过且 session 没过期）；`FALSE` = 新建 session。业务侧据此决定是否要重新 SUBSCRIBE。
- **`nReasonCode = 0x9C / 0x9D` 必须实现 server-switch 逻辑**：broker 集群升级或迁移会发这个；不实现的话 PLC 一直连旧地址会断连。生产代码必须读 `sServerReference` 后重连。
- **属性值由 driver 解析的字段长度限制**：`sReasonString` / `sServerReference` 等受 GVL `cSizeOfMqtt5ReasonString` / `cSizeOfMqtt5ServerReference`（默认 256）限制——超长会截断，要查全文用 method 拷到自己的大缓冲。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5ConnAckProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5ConnAckProperties.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示读取 CONNACK properties 做自适应
PROGRAM P_Demo_FB_IotMqtt5ConnAckProperties
VAR
    fbClient : FB_IotMqtt5Client := (sClientId := 'PLC5', sHostName := '127.0.0.1');
    fbTrig   : R_TRIG;
    nMaxPkt  : UDINT;
    bRetain  : BOOL;
    bWild    : BOOL;
    nMaxQoS  : BYTE;
    bSessOld : BOOL;
END_VAR
fbClient.Execute(bConnect := TRUE);
fbTrig(CLK := fbClient.bConnected);
IF fbTrig.Q THEN
    IF fbClient.fbConnAckProps.bPropertiesAvailable THEN
        nMaxPkt  := fbClient.fbConnAckProps.nMaxPackateSize;     // 注意 typo
        bRetain  := fbClient.fbConnAckProps.bRetainAvailable;
        bWild    := fbClient.fbConnAckProps.bWildcardSubAvailable;
        nMaxQoS  := fbClient.fbConnAckProps.nMaxQoS;
        bSessOld := fbClient.fbConnAckProps.bSessionPresent;
        // 根据上述能力调整业务策略
    END_IF
END_IF
```

## 7. 业务场景与实际价值

- **场景**：PLC 连 broker 集群——集群中部分节点支持 retain + wildcard、部分极简节点只支持基本 publish/subscribe。PLC 用 CONNACK properties 知道连到的是哪种节点，自适应调用 API（极简节点上不调 `bRetain := TRUE`、不订阅 wildcard）。
- **价值**：MQTT 5 把 broker 能力从"全局假设"变成"协议运行时声明"——客户端可以**自适应**而不是写死。`bSessionPresent` 告诉业务侧是否要重新 SUBSCRIBE；`nMaxPackateSize` 决定 publish 上限；`nReasonCode = 0x9C/0x9D` 触发 server-switch。
- **替代方案对比**：
  - MQTT 3——broker 能力靠经验 / 文档假设，不一致 broker 间不可移植；
  - 用 admin API 查 broker 能力——增加运维成本，运行时不一定及时；
  - **本 FB**：协议级声明，运行时拿到准确能力。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.9.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13964180235.html
- **相关 FB**：`FB_IotMqtt5Client`（持有本 FB 作为输出 `fbConnAckProps`）、`FB_IotMqtt5UserProperties`（基类）、`FB_IotMqtt5DisconnectProperties`（DISCONNECT 时的对偶）
