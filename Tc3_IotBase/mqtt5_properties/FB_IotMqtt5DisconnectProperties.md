# FB_IotMqtt5DisconnectProperties

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5 Properties` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13964069515.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5DisconnectProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5DisconnectProperties.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5DisconnectProperties` 是 MQTT 5 客户端**收到 broker 主动 DISCONNECT 报文**时用于读取 broker 给的 properties 的功能块。`EXTENDS FB_IotMqtt5UserProperties`——同时持有 user properties。

`FB_IotMqtt5Client` 已在 VAR_OUTPUT 内嵌一个本 FB 实例（字段 `fbDisconnectProps`）。业务侧直接读 `fbClient.fbDisconnectProps.<属性>` 诊断 broker 主动断连的原因。

MQTT 5 的 DISCONNECT 报文是双向的——客户端断时可以发，broker 也可以主动发（带 reason code 告诉客户端"我为什么踢你"）。本 FB 持有的是**收到 broker 发来的 DISCONNECT** 的 properties——客户端**自己发**的 DISCONNECT properties 不在这里。

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

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错置 `TRUE` |
| `hrErrorCode` | `HRESULT` | HRESULT 错误码 |

### VAR_IN_OUT

无。

### Property（只读属性）

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `bPropertiesAvailable` | `BOOL` | Get | 本 FB 是否持有有效 DISCONNECT properties（broker 主动断且带了 properties） |
| `nReasonCode` | `BYTE` | Get | broker 给的断连 reason code |
| `nSessionExpire` | `UDINT` | Get | broker 在 DISCONNECT 报文里更新 / 确认的 session expire 秒数 |
| `sReasonString` | `STRING` | Get | 人类可读的断连原因 |
| `sServerReference` | `STRING` | Get | broker 推荐切换的服务器地址（仅当 `nReasonCode = 0x9C` Use Another Server / `0x9D` Server moved 时有效） |

### Method

| 方法 | 用途 |
|---|---|
| `SetDisconnectProperties` | 设置本 FB 持有的 disconnect properties（一般供 driver 内部用） |

InfoSys 未提供完整方法签名；查 InfoSys topic 13964069515 或 IntelliSense。

## 3. 行为说明

**触发条件**：① broker 主动 DISCONNECT 客户端（broker 配置触发、运维强踢、broker 升级等）；② 客户端在 `Execute(bConnect := FALSE)` 后短暂自检异常 → driver 调 disconnect 流程。注意：客户端主动 `Execute(bConnect := FALSE)` 引起的 DISCONNECT **不会**填充本 FB——本 FB 只在 broker 主动发 DISCONNECT 时被填。

**读取时机**：`fbClient.bConnected` 从 `TRUE` 落回 `FALSE` 时立即读 `fbDisconnectProps.bPropertiesAvailable`——`TRUE` 则后续字段有效；`FALSE` 表示是网络层断（broker 没机会发 DISCONNECT 报文）。

**reason code 常见值**（MQTT 5 规范 §3.14.2.1）：
- `0x00` = Normal disconnection（客户端主动断的回应）
- `0x04` = Disconnect with Will Message（异常断且需要 broker 发 will）
- `0x80` = Unspecified Error
- `0x81` = Malformed Packet
- `0x82` = Protocol Error
- `0x83` = Implementation Specific Error
- `0x87` = Not Authorized
- `0x89` = Server Busy
- `0x8B` = Server Shutting Down
- `0x8D` = Keep Alive Timeout
- `0x8E` = Session Taken Over（同 ClientId 又被人连了）
- `0x8F` = Topic Filter Invalid
- `0x90` = Topic Name Invalid
- `0x93` = Receive Maximum Exceeded
- `0x95` = Packet Too Large
- `0x97` = Quota Exceeded
- `0x98` = Administrative Action
- `0x99` = Payload Format Invalid
- `0x9A` = Retain Not Supported
- `0x9B` = QoS Not Supported
- `0x9C` = Use Another Server
- `0x9D` = Server Moved
- `0x9E` = Shared Subscriptions Not Supported
- `0xA0` = Maximum Connect Time
- `0xA1` = Subscription Identifiers Not Supported
- `0xA2` = Wildcard Subscriptions Not Supported

**`nSessionExpire` 的用途**：broker 在 DISCONNECT 时可以**更新** session expire——例如客户端原本声明 1 小时，broker 临时缩减到 5 分钟（即将维护重启），客户端可据此决定要不要快速重连。

**重连决策**：根据 reason code 决定下一步：
- `0x00` = 正常断（多数是自己请求的）—— 业务侧 `bConnect` 拉回 `TRUE` 时自动重连；
- `0x8D` Keep Alive Timeout —— 网络问题，立即指数退避重连；
- `0x8E` Session Taken Over —— ClientId 被抢，**别重连**——否则两端 PLC 互相踢；改 ClientId；
- `0x9C` / `0x9D` —— 切换到 `sServerReference` 地址；
- `0x8B` Server Shutting Down —— 等几秒再重连（broker 可能切到备用节点）；
- `0x98` Administrative Action —— 运维强踢，停业务（可能要换鉴权 / 升级软件）。

**`EXTENDS FB_IotMqtt5UserProperties`**：broker 在 DISCONNECT 里可能附带 user properties——typical 用法：诊断信息（trace-id）、备用服务器列表、临时维护说明。

## 4. 错误码 / 返回值

输出 `bError` / `hrErrorCode` 反映本 FB 自身错误（极少出现）。

`nReasonCode` 是**协议级** broker 给的断连原因——见 §3 列表。

## 5. 使用注意 / 常见坑

- **`bPropertiesAvailable = FALSE` 时其他字段无效**：典型情况是 TCP 层断了（RST / 网线拔了），broker 根本没机会发 DISCONNECT 报文。
- **`nReasonCode = 0x8E` Session Taken Over** 不能盲目重连——会和另一个 PLC 互相踢。多数情况下是 ClientId 配重了；要么改 ClientId 要么停业务。
- **`0x9C / 0x9D` 必须实现 server-switch**：broker 集群升级时会发；不响应会一直连旧地址。
- **`0x98` Administrative Action** 一般要等运维人工解除——业务侧应该停 publish 进入维护模式。
- **`0x8B` Server Shutting Down** 要等几秒——broker 正在切到备用节点，立刻重连只会再被踢；等 broker 切完再连。
- **`sServerReference` 长度限制**：受 GVL `cSizeOfMqtt5ServerReference`（默认 256）限制——超长会截断。生产中 broker 给的 server reference 一般是单个 hostname，不会超。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5DisconnectProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5DisconnectProperties.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_IotMqtt5DisconnectProperties
VAR
    fbClient : FB_IotMqtt5Client := (sClientId := 'PLC5', sHostName := '127.0.0.1');
    fbTrig   : F_TRIG;
    nReason  : BYTE;
    sReason  : STRING;
    bSwitchSrv : BOOL;
    bDontReconnect : BOOL;
END_VAR
fbClient.Execute(bConnect := TRUE);
fbTrig(CLK := fbClient.bConnected);     // 下降沿——刚刚断开
IF fbTrig.Q THEN
    IF fbClient.fbDisconnectProps.bPropertiesAvailable THEN
        nReason := fbClient.fbDisconnectProps.nReasonCode;
        sReason := fbClient.fbDisconnectProps.sReasonString;
        CASE nReason OF
            16#9C, 16#9D: bSwitchSrv     := TRUE;     // 切到 sServerReference
            16#8E:        bDontReconnect := TRUE;     // Session taken over
            16#98:        bDontReconnect := TRUE;     // Administrative action
        END_CASE
    END_IF
END_IF
```

## 7. 业务场景与实际价值

- **场景**：broker 集群运维：负载均衡迁移、版本升级、节点撤池。MQTT 5 让 broker 主动告诉客户端"我要关了，去 mqtt-cluster-2:1883"——客户端按提示自动切换。同时也帮诊断"为什么 PLC 突然断了"——是网络抖动（无 DISCONNECT properties）、还是 broker 主动断（有 reason code + reason string）。
- **价值**：MQTT 3 时代客户端断了不知道原因——网络问题 vs broker 主动踢，PLC 看起来都一样；MQTT 5 通过 DISCONNECT properties 给出细分。Session Taken Over（ClientId 重复）这种生产事故能立即定位。
- **替代方案对比**：
  - MQTT 3——只能盲目重连，遇到 ClientId 冲突会两端互踢，最后定位是查日志；
  - 用 broker admin API 看断连事件——增加运维成本、运行时延；
  - **本 FB**：协议级原生支持，断连原因实时可读。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.9.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13964069515.html
- **相关 FB**：`FB_IotMqtt5Client`（持有本 FB 作为输出 `fbDisconnectProps`）、`FB_IotMqtt5UserProperties`（基类）、`FB_IotMqtt5ConnAckProperties`（CONNACK 时的对偶）
