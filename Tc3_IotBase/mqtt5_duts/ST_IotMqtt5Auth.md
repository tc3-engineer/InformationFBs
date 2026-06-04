# ST_IotMqtt5Auth

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `STRUCT` (DUT) |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12565490699.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ST_IotMqtt5Auth.TcPOU`](../examples/P_Demo_ST_IotMqtt5Auth.TcPOU) |

---

## 1. 功能简述

`ST_IotMqtt5Auth` 是 MQTT 5 客户端的**扩展认证**（Enhanced Authentication）结构体——MQTT 5 协议新增能力，让客户端在 CONNECT 报文里携带任意"鉴权方法 + 鉴权数据"对，broker 可以用 SCRAM / OAuth2 / Kerberos / 自定义企业 SSO 等高级机制鉴权——不再局限于简单的用户名 / 密码。

赋给 `FB_IotMqtt5Client.stAuth` 或 `FB_IotMqtt5ClientBase.stAuth` 后启用。多步鉴权（broker 收到 CONNECT 后回 AUTH 报文要求第二轮挑战）需要派生 `FB_IotMqtt5ClientBase` 并重写 `OnMqtt5Authentication` 回调。

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致）。

### STRUCT 成员

```iecst
TYPE ST_IotMqtt5Auth :
STRUCT
    {attribute 'TcEncoding':='UTF-8'}
    sAuthMethod        : STRING(255);
    aAuthData          : ARRAY[0..4095] OF BYTE;
    nAuthDataSize      : UINT;
END_STRUCT
END_TYPE
```

### 成员说明

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sAuthMethod` | `STRING(255)` | — | 扩展鉴权方法名（UTF-8）——按双方约定，典型如 `'SCRAM-SHA-256'` / `'OAUTH2'` / `'GS2-KRB5'` / 自定义 |
| `aAuthData` | `ARRAY[0..4095] OF BYTE` | — | 鉴权数据字节数组——内容随方法不同，最多 4096 字节 |
| `nAuthDataSize` | `UINT` | — | 鉴权数据有效字节数 |

## 3. 行为说明

**典型工作流**：① PLC 在 `Execute(bConnect := TRUE)` 第一次连上时，CONNECT 报文里附 `sAuthMethod` + `aAuthData`（前 `nAuthDataSize` 字节有效）；② broker 按 method 校验：单步鉴权直接 CONNACK 成功 / 拒绝；多步鉴权则回 AUTH 报文要求二次挑战；③ 多步路径在客户端侧由 `FB_IotMqtt5ClientBase.OnMqtt5Authentication` 回调驱动——重写该 method，按业务计算回应字节后调 broker 提供的下一步流程。

**单步 vs 多步**：① 单步 = 一个 CONNECT 报文就完成鉴权（如 OAuth2 Bearer Token 直传）——本结构体填好就完事；② 多步 = SCRAM 等挑战-响应协议——客户端要派生 ClientBase 重写 `OnMqtt5Authentication`，按 broker 给的 challenge 算 response。本库的 ClientBase 提供了多步鉴权钩子，但具体协议（如 SCRAM-SHA-256 的 RFC 5802）要业务侧自己实现。

**鉴权数据格式**：完全由 method 决定。常见示例：
- `'OAUTH2'`：`aAuthData` 填 `b'<Bearer Token>'`；
- `'SCRAM-SHA-256'`：按 RFC 5802 填 client-first-message；
- `'GS2-KRB5'`：填 GSSAPI 鉴权 token。

具体格式查 broker 文档（EMQX / HiveMQ / 自建 broker 各有约定）。

**与 sUserName / sUserPassword 的关系**：MQTT 5 协议允许 enhanced auth 与 username/password **同时**存在——多数 broker 把 username/password 当做"主鉴权"，enhanced auth 用作"二次鉴权"或"延伸鉴权"。具体优先级由 broker 决定。

**鉴权失败诊断**：`FB_IotMqtt5Client.fbConnAckProps.nReasonCode` = `0x86` (Bad UserName/Password) / `0x87` (Not Authorized) / `0x8C` (Bad Authentication Method) / `0x8D` (Not Authorized for ClientId 等)；`fbDisconnectProps.sReasonString` 给人类可读说明。

**`nAuthDataSize` 必填**：`aAuthData` 数组的"实际有效字节数"——不写或填 0 等于不带鉴权数据，broker 会直接拒绝。

## 4. 错误码 / 返回值

本结构体是数据载体，无返回值。鉴权失败由父 FB 输出反映：

| 来源 | 含义 |
|---|---|
| `fbClient.bError = TRUE` | 出错 |
| `fbClient.eConnectionState = MQTT_ERR_AUTH` (11) | 鉴权失败 |
| `fbClient.fbConnAckProps.nReasonCode` | broker 在 CONNACK 里给的细分原因（0x86/0x87/0x8C/0x8D 等） |
| `fbClient.fbConnAckProps.sReasonString` | 人类可读说明 |

## 5. 使用注意 / 常见坑

- **method 名要与 broker 完全一致**：大小写敏感——`'SCRAM-SHA-256'` 与 `'scram-sha-256'` 是不同的 method 标识。typo 直接 `nReasonCode = 0x8C`。
- **`aAuthData` 是二进制**：不要塞 STRING 直转——多数 method 的 auth data 是 base64 / 自定义二进制，不是 UTF-8 文本。
- **多步鉴权需要 ClientBase 派生**：单步可用 `FB_IotMqtt5Client`；多步必须 `FB_IotMqtt5ClientBase` 派生重写 `OnMqtt5Authentication`。
- **`aAuthData` 上限 4096 字节**：超长 token（罕见的 SAML 大块 token）放不下——拆段或换 method。
- **broker 必须支持指定 method**：rfc 没规定哪些 method 必须支持；broker 各自实现一套子集。上线前确认。
- **运行时不能改**：与 will / TLS 一样，本结构体在 CONNECT 报文里发送一次；建链后改不会生效，要 DISCONNECT 再 CONNECT。
- **`OAuth2` 类 token 过期**：典型 OAuth2 Bearer token 有 expires_in；PLC 要在 token 过期前主动 DISCONNECT + 拿新 token + 重 CONNECT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ST_IotMqtt5Auth.TcPOU`](../examples/P_Demo_ST_IotMqtt5Auth.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示 OAuth2 Bearer Token 鉴权（broker 必须支持 'OAUTH2' method）
PROGRAM P_Demo_ST_IotMqtt5Auth
VAR
    fbMqtt5     : FB_IotMqtt5Client := (sClientId := 'PLC5-OAuth', sHostName := 'mqtt.example.com', nHostPort := 8883);
    sToken      : STRING(255) := 'eyJhbGciOiJSUzI1NiIs...';   // OAuth2 Bearer Token
    bRun        : BOOL := TRUE;
    bAuthInited : BOOL;
    i           : UINT;
END_VAR
IF NOT bAuthInited THEN
    fbMqtt5.stAuth.sAuthMethod := 'OAUTH2';
    // token 字符串拷到字节数组
    FOR i := 0 TO TO_UINT(LEN(sToken)) - 1 DO
        fbMqtt5.stAuth.aAuthData[i] := sToken[i + 1];
    END_FOR
    fbMqtt5.stAuth.nAuthDataSize := TO_UINT(LEN(sToken));
    bAuthInited := TRUE;
END_IF
fbMqtt5.Execute(bConnect := bRun);
```

## 7. 业务场景与实际价值

- **场景**：工厂使用企业 SSO（Azure AD / Okta / Keycloak），每个 PLC 通过 OAuth2 Client Credentials Flow 拿 Bearer Token 连 broker——broker 在 token 里读 PLC 身份信息和权限范围，而不是为每个 PLC 单独管理证书或用户名/密码。
- **价值**：MQTT 5 把"鉴权机制"从协议里彻底解耦——本结构体只负责"method 名 + 数据字节"，具体协议（OAuth2 / SCRAM / Kerberos）由双方约定。比 MQTT 3 时代只能用 username/password 灵活得多——支持企业级 SSO、零信任架构、短期 token 撤销、按权限范围授权。
- **替代方案对比**：
  - 用 username/password——长期凭据轮换困难、撤销慢、无权限范围；
  - 用 TLS mTLS——证书签发 / 吊销 / 续期工作量大、PLC 端要保管私钥；
  - **本结构体**：与 SSO / OAuth2 / 短期 token 体系无缝衔接，运维成本最低。
- **何时仍用 username/password**：内网 broker、不接入企业 SSO 的工厂——`stAuth` 留空、用 `sUserName` / `sUserPassword` 即可。
- **何时仍用 mTLS**：极高安全要求场景（金融 / 关键基础设施）、broker 不支持 enhanced auth——`stTLS` 配 mTLS、`stAuth` 留空。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12565490699.html
- **相关 DUT / FB**：`FB_IotMqtt5Client`（消费 `stAuth`）、`FB_IotMqtt5ClientBase`（多步鉴权需重写 OnMqtt5Authentication）、`ETcIotMqttClientState`、`FB_IotMqtt5ConnAckProperties`（broker 鉴权结果细分）
