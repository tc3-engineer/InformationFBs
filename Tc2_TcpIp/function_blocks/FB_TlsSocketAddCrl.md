# FB_TlsSocketAddCrl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511092619.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketAddCrl.TcPOU`](../examples/P_Demo_FB_TlsSocketAddCrl.TcPOU) |

---

## 1. 功能简述

把 CRL（Certificate Revocation List，证书吊销列表）文件加入到指定 TLS socket 的验证链。CRL 由 CA 签发，列出已被吊销但还未到期的证书序列号；本 FB 加载后，TLS 握手时如果对端证书在 CRL 中即视为校验失败（`TLS_CERT_REVOKED`）。文件必须 PEM 格式。需要 TF6310 v3.3.15.0 或更高版本。必须在 `FB_TlsSocketConnect` / `FB_TlsSocketListen` 之前调用，可与 `FB_TlsSocketAddCa` 同时使用，是 PKI 完整性方案的可选环节。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId : T_AmsNetId:='';
    hSocket   : T_HSOCKET;
    sCrlPath  : STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE):='';
    bExecute  : BOOL;
    tTimeout  : TIME:=T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 由 `FB_TlsSocketCreate` 创建的 socket 句柄 |
| `sCrlPath` | `STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE)` | `''` | CRL PEM 文件绝对路径（最长 255 字节） |
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
| `bBusy` | `BOOL` | 正在加载 CRL |
| `bError` | `BOOL` | 加载失败 |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次加载。

**单次加载状态机**：上升沿 → `bBusy := TRUE`；Server 读 CRL PEM 文件并解析（X.509 CRL）；追加到 socket 的 verify store；完成 → `bBusy := FALSE`、`bError := FALSE`。后续 TLS 握手时若对端证书 SN 命中 CRL，立刻报 `TLS_CERT_REVOKED`。

**CRL 更新**：CRL 是周期性发布的（典型 1 天 / 1 周一次）。生产环境需要有外部脚本定期把最新 CRL 拉到 PLC 文件系统，并在合适时机让 PLC 重新加载（通常意味着重新 Create socket + AddCa + AddCrl，然后重连）。本 FB 不提供"运行时热更新"机制。

**何时需要 CRL**：高安全场景（金融、医疗、关键基础设施）。一般工厂场景常省略 CRL，只靠证书有效期 + CA 签发管控；想严格点可启用。

**典型陷阱**：CRL 文件格式错（DER 或损坏）→ `TLS_CRL_INVALID`；CRL 过期（CRL 自己也有有效期，nextUpdate 过了就被认为是"陈旧 CRL"）→ 部分 TLS 库可能直接报错或忽略——具体行为视 Beckhoff 底层实现而异。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x00008080` | `TLS_INVALID_STATE` | 已 Connect/Listen 后才调 |
| `0x0000808C` | `TLS_CRL_INVALID` | CRL 文件读取或解析失败 |

## 5. 使用注意 / 常见坑

- **没有 CRL 不等于"无吊销保护"**：可以通过短有效期证书（如 90 天）+ 频繁滚动证书来替代 CRL。
- **CRL 文件大小**：吊销证书多的 CA 的 CRL 可能很大（几 MB）；CX 磁盘紧的话需注意。
- **OCSP 不在本 FB 范围**：Beckhoff 当前 TF6310 暂不支持 OCSP（在线证书状态协议），只能用静态 CRL。
- **CRL 与 CA 必须匹配**：CRL 由签发该证书的 CA 签出，跨 CA 的 CRL 无效。
- **顺序**：Create → AddCa → AddCrl → Connect/Listen。AddCrl 之前必须先 AddCa（CRL 验证依赖 CA 公钥）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketAddCrl.TcPOU`](../examples/P_Demo_FB_TlsSocketAddCrl.TcPOU)

```iecst
// 场景：TLS 客户端 socket 已 Create + AddCa，现在追加 CRL 增强校验。
PROGRAM P_Demo_FB_TlsSocketAddCrl
VAR
    fbAddCrl       : FB_TlsSocketAddCrl;
    hSocket        : T_HSOCKET;
    sCrlPath       : STRING(255) := 'C:\TwinCAT\3.1\Boot\Plc\TcpIpServer\corp_ca.crl.pem';
    bRequestAddCrl : BOOL;
    bAddCrlBusy    : BOOL;
    bAddCrlError   : BOOL;
    nAddCrlErrId   : UDINT;
END_VAR

fbAddCrl(
    sSrvNetId := '',
    hSocket   := hSocket,
    sCrlPath  := sCrlPath,
    bExecute  := bRequestAddCrl,
    tTimeout  := T#5S,
    bBusy     => bAddCrlBusy,
    bError    => bAddCrlError,
    nErrId    => nAddCrlErrId
);
```

## 7. 业务场景与实际价值

- **场景**：高安全场景（药企生产、能源行业、关键基础设施）需要满足合规要求（如 IEC 62443），证书吊销跟进必须做。
- **价值**：标准 X.509 CRL 支持；一行 FB 即可启用吊销校验。
- **替代方案对比**：
  - 短有效期证书 + 频繁滚动：简单可靠，常见 IoT 做法
  - OCSP：实时但 TF6310 暂不支持
  - **本 FB**：静态 CRL，需运维定期更新，但与 OS / OpenSSL 标准做法对齐

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511092619.html
- **相关**：`FB_TlsSocketCreate` / `FB_TlsSocketAddCa`（前置）、`FB_TlsSocketConnect` / `FB_TlsSocketListen`（后续）
