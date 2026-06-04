# ST_IotMqttTLS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `STRUCT` (DUT) |
| Category | `MQTT3` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392077451.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ST_IotMqttTLS.TcPOU`](../examples/P_Demo_ST_IotMqttTLS.TcPOU) |

---

## 1. 功能简述

`ST_IotMqttTLS` 是 MQTT 3.1.1 客户端的 **TLS 加密设置**结构体，赋给 `FB_IotMqttClient.stTLS` 后，客户端用 TLS 加密通道（典型 8883 端口）连接 broker。

支持两种鉴权路径，**二选一**：

- **CA + 客户端证书**：标准 X.509 体系。配置 `sCA`（信任的根 CA）+ `sCert`（客户端证书）+ `sKeyFile`（客户端私钥），broker 端用 mTLS 校验客户端身份。AWS IoT Core、Azure IoT Hub（X.509 路径）、HiveMQ Cloud 等都走这一种。
- **PSK 预共享密钥**：轻量级，没有证书概念，双方用同一个对称密钥 + identity。配置 `sPskIdentity` + `aPskKey` + `nPskKeyLen`。适用于嵌入式设备或封闭工厂网络。

注意：**InfoSys 文档**比 PDF 多了一条 `sCAPath` 字段（PDF 也列出，但标为 "for future use"），文档以 PDF 字段为准——目前不使用。

PDF 中类型声明拼写为 `ST_IotMqttTls`（小写 ls），但 PDF/InfoSys 章节标题与 InfoSys topic 文件名均拼写为 `ST_IotMqttTLS`（大写 TLS），文档保留 PDF 标题原拼写作为文件名。在 IEC 代码中类型名遵循 PDF 声明 `ST_IotMqttTls`。

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致）。

### STRUCT 成员

```iecst
TYPE ST_IotMqttTls :
STRUCT
    sCA                : STRING(255); // certificate authority as filename (PEM or DER format) or as string (PEM)
    sCAPath            : STRING(255); // for future use
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
| `sCA` | `STRING(255)` | — | CA 证书：可填**文件名**（PEM 或 DER 格式，broker 信任的根 CA）或**直接填证书 PEM 字符串**。AWS IoT Core 用 `AmazonRootCA1.pem` |
| `sCAPath` | `STRING(255)` | — | 预留——PDF 标 "for future use"。不要使用 |
| `sCert` | `STRING(255)` | — | 客户端证书：文件名或 PEM 字符串，用于客户端向 broker 证明身份（mTLS 必填） |
| `sKeyFile` | `STRING(255)` | — | 客户端**私钥**：文件名或 PEM 字符串。若 broker 不做 mTLS（仅 server-side TLS）可空 |
| `sKeyPwd` | `STRING(255)` | — | 私钥文件的密码（若私钥被密码加密）。无密码私钥留空 |
| `sCrl` | `STRING(255)` | — | 证书吊销列表（CRL）：PEM 或 DER 文件路径。可选——多数生产 broker 不强制 |
| `sCiphers` | `STRING(255)` | — | OpenSSL 风格的加密套件优先级字符串（如 `'ECDHE-RSA-AES256-GCM-SHA384'`）。不填走默认套件 |
| `sVersion` | `STRING(80)` | `'tlsv1.2'` | TLS 协议版本字符串。可填 `'tlsv1.2'` / `'tlsv1.3'` |
| `bNoServerCertCheck` | `BOOL` | `FALSE` | **关闭**服务端证书校验。**生产环境严禁开启**，仅调试连内部测试 broker 时临时打开 |
| `sPskIdentity` | `STRING(255)` | — | TLS PSK 模式的 identity 字符串（双方约定） |
| `aPskKey` | `ARRAY[1..64] OF BYTE` | — | TLS PSK 模式的预共享密钥字节数组（最多 64 字节） |
| `nPskKeyLen` | `USINT` | — | PSK 的实际字节数（≤64） |
| `sAzureSas` | `STRING(511)` | — | 连接 Microsoft Azure IoT Hub 时用的 **SAS token** 字符串。Azure 不用客户端证书时填它 |

## 3. 行为说明

**两种路径互斥**：① CA + Cert + Key（X.509 路径）；② PSK identity + Key（PSK 路径）。同时填两边时驱动按 broker 协商结果选其中一条；建议清楚地只填一种以减少出错面。

**证书来源两种写法**：① 文件名——把证书拷到 PLC boot 目录或绝对路径，broker 启动时按路径读；② 直接填 PEM 字符串（含 `-----BEGIN CERTIFICATE-----` / `-----END CERTIFICATE-----` 行），适用于把证书内嵌进 PLC 工程便于版本管理。PEM 字符串长度受 `STRING(255)` 限制，常用 CA 可能塞不下——超出走文件名路径。

**`bNoServerCertCheck := TRUE` 的危险**：跳过服务端证书校验等于"任何人都可以冒充 broker"——中间人可以截取所有 publish 数据并伪造下行命令。仅在调试连**自签 CA**的内部 broker 且无中间人风险时临时打开；上生产前必须置回 `FALSE` 并配 `sCA`。

**Azure SAS 路径**：连 Azure IoT Hub 时若用 SAS token 鉴权（非 X.509），把 token 字符串填到 `sAzureSas`，同时 `sUserName` 填设备名、`sUserPassword` 留空（SAS 当密码用）；broker 端口仍是 8883。详细机制看 Azure IoT 文档。

**TLS 版本选择**：`'tlsv1.2'` 默认值满足绝大多数 broker；要求 1.3 时改 `'tlsv1.3'`。1.0 / 1.1 已被弃用，OpenSSL 新版可能直接拒绝。

**端口约定**：本结构体本身不影响 `FB_IotMqttClient.nHostPort`——加密端口（典型 8883）要单独在父 FB 上设。

## 4. 错误码 / 返回值

本结构体是数据载体，无返回值。TLS 失败由父 FB `FB_IotMqttClient.bError` / `hrErrorCode` / `eConnectionState` 反映：

| eConnectionState | 含义 | 排查方向 |
|---|---|---|
| `MQTT_ERR_TLS_CA_NOTFOUND` (17) | CA 文件没找到 | 检查 `sCA` 文件路径或 PEM 字符串完整性 |
| `MQTT_ERR_TLS_CERT_NOTFOUND` (18) | 客户端证书没找到 | 检查 `sCert` |
| `MQTT_ERR_TLS_KEY_NOTFOUND` (19) | 私钥没找到 | 检查 `sKeyFile` |
| `MQTT_ERR_TLS_CA_INVALID` (20) | CA 文件格式错 | 通常是 PEM / DER 头尾被截，或文件不是真正的 CA |
| `MQTT_ERR_TLS_CERT_INVALID` (21) | 客户端证书无效 | 文件损坏或不是 X.509 |
| `MQTT_ERR_TLS_KEY_INVALID` (22) | 私钥无效 | 密码错、加密格式不支持、与证书不配对 |
| `MQTT_ERR_TLS_VERIFY_FAIL` (23) | 服务端证书校验失败 | 服务端证书不是本 CA 签的、过期、CN 不匹配 |
| `MQTT_ERR_TLS_SETUP` (24) | TLS 上下文初始化失败 | 通常配置组合非法 |
| `MQTT_ERR_TLS_HANDSHAKE_FAIL` (25) | TLS 握手失败 | broker 拒绝、网络问题、协议版本不匹配 |
| `MQTT_ERR_TLS_CIPHER_INVALID` (26) | 加密套件不可用 | `sCiphers` 配置的套件 OpenSSL 不支持 |
| `MQTT_ERR_TLS_VERSION_INVALID` (27) | TLS 版本不支持 | `sVersion` 字符串错或 broker 端不支持 |
| `MQTT_ERR_TLS_PSK_INVALID` (28) | PSK 无效 | identity / key 与 broker 不匹配 |
| `MQTT_ERR_TLS_CRL_NOTFOUND` (29) | CRL 文件没找到 | 检查 `sCrl` |
| `MQTT_ERR_TLS_CRL_INVALID` (30) | CRL 文件无效 | 文件损坏 |
| `MQTT_ERR_TLS_CERT_EXPIRED` (40) | 服务端证书过期 | 续签 broker 证书 |
| `MQTT_ERR_TLS_CN_MISMATCH` (41) | 服务端证书 CN 不匹配 | broker 证书的 CN / SAN 与 `sHostName` 不一致 |

## 5. 使用注意 / 常见坑

- **生产环境禁止 `bNoServerCertCheck := TRUE`**——重要到值得在 code review 加自动扫描。
- **私钥安全**：`sKeyFile` 若填 PEM 字符串嵌在 PLC 工程里，源码就泄露了私钥。生产推荐文件路径方式 + PLC 启动盘加密。
- **证书 SAN/CN 必须包含 `sHostName`**：`sHostName := '192.168.10.5'` 时 broker 证书的 SAN 必须列 IP；`sHostName := 'mqtt.example.com'` 时证书 CN 或 SAN 必须含该域名。否则 `MQTT_ERR_TLS_CN_MISMATCH`。
- **AWS IoT Core**：用 `AmazonRootCA1.pem` 作 `sCA`、给每个 PLC 单独签发证书 + 私钥作 `sCert` / `sKeyFile`，端口 8883；`sUserName` / `sUserPassword` 留空（AWS 用 mTLS 鉴权不用密码）。
- **Azure IoT Hub**：① X.509 路径 — `sCA` 填微软 IoT Hub root、`sCert` / `sKeyFile` 填设备证书、`sUserName := '<iothub>/<deviceId>/?api-version=2021-04-12'`；② SAS 路径 — `sAzureSas` 填 token、`sUserName := '<iothub>/<deviceId>/?api-version=...'`、`sUserPassword` 留空。
- **TLS 协议版本不匹配最常见**：OpenSSL 较新版本拒绝 TLS 1.0/1.1，老 broker 又只支持 1.2 以下——升级 broker 或换库。
- **PSK 不需要 CA 字段**：PSK 路径下 `sCA` / `sCert` / `sKeyFile` 全留空，只填 `sPskIdentity` / `aPskKey` / `nPskKeyLen` / `sVersion`。
- **`sCiphers` 写法和优先顺序**：OpenSSL cipher list 风格，分号或冒号分隔——`'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ST_IotMqttTLS.TcPOU`](../examples/P_Demo_ST_IotMqttTLS.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示走 TLS 1.2 + CA 文件连本地 Mosquitto:8883（自签 CA）
PROGRAM P_Demo_ST_IotMqttTLS
VAR
    stTls : ST_IotMqttTls := (
        sCA                := 'C:\TwinCAT\Boot\Certs\my_ca.pem',
        sCert              := 'C:\TwinCAT\Boot\Certs\plc_client.pem',
        sKeyFile           := 'C:\TwinCAT\Boot\Certs\plc_client.key',
        sVersion           := 'tlsv1.2',
        bNoServerCertCheck := FALSE                       // 生产必须 FALSE
    );
    fbMqtt : FB_IotMqttClient := (
        sClientId  := 'PLC-TLS-Demo',
        sHostName  := 'mqtt.factory.local',               // 必须与 broker 证书 CN/SAN 一致
        nHostPort  := 8883                                // TLS 端口
    );
    bEnable : BOOL := TRUE;
END_VAR
fbMqtt.stTLS := stTls;
fbMqtt.Execute(bConnect := bEnable);
```

## 7. 业务场景与实际价值

- **场景**：工厂 PLC 向云端 broker（AWS IoT Core / Azure IoT Hub / 自建 EMQX over Internet）上报数据，必须走 TLS 加密；或厂区内 MQTT 网关用 mTLS 鉴权阻止未授权设备接入。
- **价值**：把 OpenSSL 配置、证书加载、握手协商、错误细分这一整套 TLS 客户端实现全包到一个结构体里。业务代码只需要决定填 CA 文件路径还是 PEM 字符串、用 X.509 还是 PSK；不需要碰任何 OpenSSL API、也不需要自己实现证书校验逻辑。
- **替代方案对比**：
  - 走明文 1883——只能在物理隔离的车间内网用，跨公网或共享网络都不允许；
  - 自己写 OpenSSL 集成——需 C/C++ 扩展 PLC 运行时、维护证书生命周期，工作量巨大；
  - 走 OPC UA 加密——是 OPC UA 协议，不能直接对接 MQTT 云平台；
  - **本结构体**：MQTT 协议原生 TLS 支持，所有云平台默认支持。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392077451.html
- **相关 DUT / FB**：`FB_IotMqttClient`（在 `stTLS` 引脚消费本结构体）、`ETcIotMqttClientState`（错误细分枚举）、`ST_IotMqtt5Tls`（MQTT 5 版本，去掉了 `sCAPath` 字段）
