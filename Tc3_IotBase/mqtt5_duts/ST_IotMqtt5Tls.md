# ST_IotMqtt5Tls

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `STRUCT` (DUT) |
| Category | `MQTT5` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12567830411.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ST_IotMqtt5Tls.TcPOU`](../examples/P_Demo_ST_IotMqtt5Tls.TcPOU) |

---

## 1. 功能简述

`ST_IotMqtt5Tls` 是 MQTT 5 客户端的 **TLS 加密设置**结构体——与 MQTT 3 版 `ST_IotMqttTls` 字段几乎完全一致，唯一差异是**少了 MQTT 3 版的 `sCAPath` 字段**（MQTT 3 该字段也是 "for future use"，本来就不该用——所以实际差异为零）。

支持两种鉴权路径：① CA + 客户端证书（标准 X.509，mTLS）；② PSK 预共享密钥。详细说明同 `ST_IotMqttTLS.md` §1。

赋给 `FB_IotMqtt5Client.stTLS` 或 `FB_IotMqtt5ClientBase.stTLS` 后启用 TLS 加密链路（典型端口 8883）。

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致）。

### STRUCT 成员

```iecst
TYPE ST_IotMqtt5Tls :
STRUCT
    sCA                : STRING(255); // certificate authority as filename (PEM or DER format) or as string (PEM)
    sCert              : STRING(255); // client certificate as filename (PEM or DER format) or as string (PEM)
    sKeyFile           : STRING(255);
    sKeyPwd            : STRING(255);
    sCrl               : STRING(255); // Certificate Revocation List as filename (PEM or DER format) or as string (PEM)
    sCiphers           : STRING(255);
    sVersion           : STRING(80) := 'tlsv1.2'; // TLS version
    bNoServerCertCheck : BOOL := FALSE;
    sPskIdentity       : STRING(255);
    aPskKey            : ARRAY[1..64] OF BYTE;
    nPskKeyLen         : USINT;
    sAzureSas          : STRING(511);
END_STRUCT
END_TYPE
```

### 成员说明

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sCA` | `STRING(255)` | — | CA 证书：文件名（PEM/DER）或 PEM 字符串 |
| `sCert` | `STRING(255)` | — | 客户端证书：文件名或 PEM 字符串 |
| `sKeyFile` | `STRING(255)` | — | 客户端私钥：文件名或 PEM 字符串 |
| `sKeyPwd` | `STRING(255)` | — | 私钥密码（若加密） |
| `sCrl` | `STRING(255)` | — | CRL：PEM/DER 文件路径 |
| `sCiphers` | `STRING(255)` | — | OpenSSL 风格加密套件优先级字符串 |
| `sVersion` | `STRING(80)` | `'tlsv1.2'` | TLS 协议版本 |
| `bNoServerCertCheck` | `BOOL` | `FALSE` | **生产严禁置 TRUE**——跳过服务端证书校验等于"任何人可冒充 broker" |
| `sPskIdentity` | `STRING(255)` | — | TLS PSK identity |
| `aPskKey` | `ARRAY[1..64] OF BYTE` | — | TLS PSK key 字节数组 |
| `nPskKeyLen` | `USINT` | — | PSK 字节数 |
| `sAzureSas` | `STRING(511)` | — | Azure IoT Hub SAS token |

## 3. 行为说明

行为与 MQTT 3 版完全一致——TLS 握手在 `Execute(bConnect := TRUE)` 第一次调用时进行；失败原因细分到 `FB_IotMqtt5Client.eConnectionState` 的 `MQTT_ERR_TLS_*` 系列码。详细见 `ST_IotMqttTLS.md` §3 — 同样的两条路径、同样的字段语义、同样的故障排查方式。

**与 MQTT 3 版唯一差异**：`sCAPath` 字段被去掉了。MQTT 3 版本里 `sCAPath` 注释也是 "for future use"——本来就不该用——所以实际工程行为完全相同。

**TLS 握手时序**：相比明文连接，TLS 握手要 几百 ms ~ 几秒（取决于 CA 链长度、TLS 版本、网络 RTT）；调试时 `bConnected` 短暂为 FALSE 不是错——继续等。

**broker 能力探测**：MQTT 5 引入 CONNACK properties——TLS 握手成功且 MQTT CONNECT 也通过后，从 `fbClient.fbConnAckProps` 读 broker 能力。但**注意**：CONNACK 还在 TLS 隧道里——TLS 失败就根本到不了 CONNECT 这一步，所以 TLS 错先通过 `eConnectionState` 看，连上之后再读 properties。

## 4. 错误码 / 返回值

错误反映在父 FB `FB_IotMqtt5Client.bError` / `hrErrorCode` / `eConnectionState`。`MQTT_ERR_TLS_*` 系列码与 MQTT 3 版完全一致：见 `ST_IotMqttTLS.md` §4 错误码表。

| eConnectionState | 含义 |
|---|---|
| `MQTT_ERR_TLS_CA_NOTFOUND` (17) | CA 文件没找到 |
| `MQTT_ERR_TLS_CERT_NOTFOUND` (18) | 客户端证书没找到 |
| `MQTT_ERR_TLS_KEY_NOTFOUND` (19) | 私钥没找到 |
| `MQTT_ERR_TLS_CA_INVALID` (20) | CA 文件格式错 |
| `MQTT_ERR_TLS_CERT_INVALID` (21) | 客户端证书无效 |
| `MQTT_ERR_TLS_KEY_INVALID` (22) | 私钥无效 |
| `MQTT_ERR_TLS_VERIFY_FAIL` (23) | 服务端证书校验失败 |
| `MQTT_ERR_TLS_SETUP` (24) | TLS 上下文初始化失败 |
| `MQTT_ERR_TLS_HANDSHAKE_FAIL` (25) | TLS 握手失败 |
| `MQTT_ERR_TLS_CIPHER_INVALID` (26) | 加密套件不可用 |
| `MQTT_ERR_TLS_VERSION_INVALID` (27) | TLS 版本不支持 |
| `MQTT_ERR_TLS_PSK_INVALID` (28) | PSK 无效 |
| `MQTT_ERR_TLS_CRL_NOTFOUND` (29) | CRL 文件没找到 |
| `MQTT_ERR_TLS_CRL_INVALID` (30) | CRL 文件无效 |
| `MQTT_ERR_TLS_CERT_EXPIRED` (40) | 服务端证书过期 |
| `MQTT_ERR_TLS_CN_MISMATCH` (41) | 服务端证书 CN/SAN 不匹配 |

## 5. 使用注意 / 常见坑

与 MQTT 3 版 `ST_IotMqttTLS.md` §5 完全一致——`bNoServerCertCheck` 严禁生产 TRUE、CN/SAN 必须匹配 `sHostName`、AWS IoT / Azure IoT 各自的配置约定。MQTT 5 额外的注意点：

- **broker 必须支持 MQTT 5 over TLS**：少数老 broker 只支持 MQTT 3 over TLS——TLS 握手成功但 MQTT CONNECT 报"Unsupported Protocol Version" `nReasonCode = 0x84`；换 MQTT 3 客户端（`FB_IotMqttClient + ST_IotMqttTls`）或升级 broker。
- **`fbConnAckProps.nMaxPackateSize` 自适应**：连上后读 broker 能力——若 broker 限制 max packet 比预期小，要分片或换 topic。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ST_IotMqtt5Tls.TcPOU`](../examples/P_Demo_ST_IotMqtt5Tls.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_ST_IotMqtt5Tls
VAR
    fbMqtt5 : FB_IotMqtt5Client := (sClientId := 'PLC5-TLS', sHostName := 'mqtt.factory.local', nHostPort := 8883);
    bRun    : BOOL := TRUE;
    bTlsSet : BOOL;
END_VAR
IF NOT bTlsSet THEN
    fbMqtt5.stTLS.sCA                := 'C:\TwinCAT\Boot\Certs\factory_ca.pem';
    fbMqtt5.stTLS.sCert              := 'C:\TwinCAT\Boot\Certs\plc.pem';
    fbMqtt5.stTLS.sKeyFile           := 'C:\TwinCAT\Boot\Certs\plc.key';
    fbMqtt5.stTLS.sVersion           := 'tlsv1.2';
    fbMqtt5.stTLS.bNoServerCertCheck := FALSE;
    bTlsSet := TRUE;
END_IF
fbMqtt5.Execute(bConnect := bRun);
```

## 7. 业务场景与实际价值

- **场景**：MQTT 5 边缘 PLC 跨公网连云端 broker——必须 TLS 加密。新项目应优选 MQTT 5（更细的错误诊断、自适应、user properties）+ TLS。
- **价值**：与 MQTT 3 `ST_IotMqttTLS` 等效——配 PDF 列出的 MQTT 3 + MQTT 5 共用的错误码集合，错误细分到 17 种 TLS 子错。少了 MQTT 3 的 `sCAPath` 字段（本来就 "for future use"），结构更干净。
- **替代方案对比**：见 MQTT 3 版 `ST_IotMqttTLS.md` §7 —— 同样适用。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12567830411.html
- **相关 DUT / FB**：`FB_IotMqtt5Client`（消费 `stTLS`）、`FB_IotMqtt5ClientBase`、`ETcIotMqttClientState`、`ST_IotMqttTLS`（MQTT 3 版）
