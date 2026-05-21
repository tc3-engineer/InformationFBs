# FB_TlsSocketSetCert

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511128075.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketSetCert.xml`](../examples/P_Demo_FB_TlsSocketSetCert.xml) |

---

## 1. 功能简述

把本端 TLS 证书 + 私钥加载到指定 TLS socket。**服务端**用此 FB 装"我自己的服务端证书"（必须，否则 Listen 时报错或所有客户端拒绝握手）；**客户端**仅在双向 TLS（mTLS）场景需要装客户端证书。证书和私钥都是 PEM 格式，私钥若加密则用 `sKeyPwd` 提供解密口令。需要 TF6310 v3.3.15.0 或更高版本。**必须在 Connect/Listen 之前调用**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId : T_AmsNetId:='';
    hSocket   : T_HSOCKET;
    sCertPath : STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE):='';
    sKeyPath  : STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE):='';
    sKeyPwd   : STRING(TCPADS_TLS_KEY_PASSWORD_SIZE):='';
    bExecute  : BOOL;
    tTimeout  : TIME:=T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 由 `FB_TlsSocketCreate` 创建的 socket 句柄 |
| `sCertPath` | `STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE)` | `''` | 本端证书 PEM 文件绝对路径（255 字节上限） |
| `sKeyPath` | `STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE)` | `''` | 配套私钥 PEM 文件绝对路径 |
| `sKeyPwd` | `STRING(TCPADS_TLS_KEY_PASSWORD_SIZE)` | `''` | 私钥加密口令（私钥未加密时填空串）。最长 `TCPADS_TLS_KEY_PASSWORD_SIZE = 255` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次加载 |
| `tTimeout` | `TIME` | `T#5s` | ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在加载 |
| `bError` | `BOOL` | 加载失败 |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次加载。

**单次加载状态机**：上升沿 → `bBusy := TRUE`；Server 读 `sCertPath` 解析 X.509 证书 + 读 `sKeyPath` 解析私钥 + 用 `sKeyPwd`（若有）解密 + 校验证书 ↔ 私钥配对 + 装到 TLS context；完成 → `bBusy := FALSE`、`bError := FALSE`。

**证书 vs 私钥不匹配**：上传的证书公钥必须能用上传的私钥对应——这个校验在加载时做，失败报 `TLS_KEY_INVALID` 或 `TLS_CERT_INVALID`。常见原因：换证书时只换了证书没换私钥。

**多证书装载**：本 FB 同一 socket 通常只装一对（证书 + 私钥）。如果调多次本 FB 是否覆盖前一份还是追加，PDF 未明说——⚠️ 建议只装一次，多个 socket 角色用多个 socket 实例。

**私钥保护**：

- 未加密私钥：`sKeyPwd := ''` 即可。便于自动化，但磁盘文件等于裸密钥
- 加密私钥（PEM 头含 `Proc-Type: 4,ENCRYPTED`）：必须 `sKeyPwd` 提供口令，否则 `TLS_KEY_INVALID`
- 生产环境强烈建议加密私钥 + 口令通过环境变量或安全存储获取

**典型陷阱**：证书 / 私钥文件路径错 → `CERT_NOTFOUND` / `KEY_NOTFOUND`；证书格式错或损坏 → `CERT_INVALID`；私钥口令错 → `KEY_INVALID`；在 Connect/Listen 后调 → `TLS_INVALID_STATE`；证书已过期 → 加载本身可能成功，但握手时被对端拒（或自己拒，取决于校验流程）。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x00008080` | `TLS_INVALID_STATE` | 已 Connect/Listen 后才调 |
| `0x00008082` | `TLS_CERT_NOTFOUND` | 证书文件不存在 |
| `0x00008083` | `TLS_KEY_NOTFOUND` | 私钥文件不存在 |
| `0x00008085` | `TLS_CERT_INVALID` | 证书读取或解析失败 |
| `0x00008086` | `TLS_KEY_INVALID` | 私钥读取 / 解密 / 配对校验失败 |
| `0x00008090` | `TLS_CERT_EXPIRED` | 证书已过期 |

## 5. 使用注意 / 常见坑

- **服务端必装**：Listen 之前不调本 FB → TLS 握手必失败。
- **客户端可选**：单向 TLS（HTTPS 默认）客户端不需要装本端证书；mTLS 才需要。
- **证书有效期监控**：本 FB 不主动报"证书即将过期"——业务侧应自己计划证书滚动机制。
- **私钥泄露 = 安全失守**：磁盘上的私钥文件权限设最严；定期轮换。
- **PKCS#12 (.pfx) 不支持**：必须 PEM。如果证书源是 PKCS#12，先用 OpenSSL 拆为 cert.pem + key.pem。
- **证书链中间证书**：把中间证书 cat 进 server.pem（按"叶子证书 + 中间证书"顺序拼），同一文件可含多条证书。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketSetCert.xml`](../examples/P_Demo_FB_TlsSocketSetCert.xml)

```iecst
// 场景：服务端 TLS socket 已 Create(bListener:=TRUE)，加载本机证书 + 加密私钥。
PROGRAM P_Demo_FB_TlsSocketSetCert
VAR
    fbSetCert      : FB_TlsSocketSetCert;
    hSocket        : T_HSOCKET;
    sCertPath      : STRING(255) := 'C:\TwinCAT\3.1\Boot\Plc\TcpIpServer\server.pem';
    sKeyPath       : STRING(255) := 'C:\TwinCAT\3.1\Boot\Plc\TcpIpServer\server.key';
    sKeyPwd        : STRING(255) := 'mySecretPassphrase';
    bRequestSetCert: BOOL;
    bSetCertBusy   : BOOL;
    bSetCertError  : BOOL;
    nSetCertErrId  : UDINT;
END_VAR

fbSetCert(
    sSrvNetId := '',
    hSocket   := hSocket,
    sCertPath := sCertPath,
    sKeyPath  := sKeyPath,
    sKeyPwd   := sKeyPwd,
    bExecute  := bRequestSetCert,
    tTimeout  := T#5S,
    bBusy     => bSetCertBusy,
    bError    => bSetCertError,
    nErrId    => nSetCertErrId
);
```

## 7. 业务场景与实际价值

- **场景**：
  - 服务端：PLC 提供 HTTPS-like API、TLS 化的 OPC UA、加密 MQTT broker
  - 客户端 mTLS：PLC 连云端 IoT Hub（AWS / Azure），云端要求客户端证书
- **价值**：标准 X.509 + PEM 加载；与 OpenSSL / mbedTLS 完全兼容；私钥加密支持开箱即用。
- **替代方案对比**：
  - 用 PSK（`FB_TlsSocketSetPsk`）：不用证书，配置简单，但密钥分发是个问题
  - 关闭 TLS：内网可，跨网严禁

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511128075.html
- **相关**：`FB_TlsSocketCreate`（前置）、`FB_TlsSocketAddCa`（验对端用）、`FB_TlsSocketConnect` / `FB_TlsSocketListen`（后续）、`FB_TlsSocketSetPsk`（替代方案）
