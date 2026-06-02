# FB_TlsSocketAddCa

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511048331.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketAddCa.TcPOU`](../examples/P_Demo_FB_TlsSocketAddCa.TcPOU) |

---

## 1. 功能简述

把一个 CA（Certificate Authority）证书文件路径加入到指定 TLS socket 的信任链。客户端模式下，本 FB 加入的 CA 用来校验对端服务器证书的签发链；服务端模式下（双向 TLS / mTLS），用来校验客户端递交的证书。证书文件必须是 PEM 格式（`-----BEGIN CERTIFICATE-----` 开头），文件路径是目标 PLC 主机上的本地绝对路径。同一 socket 可以多次调本 FB 加多个 CA，构成完整信任链。需要 TF6310 v3.3.15.0 或更高版本。**必须在 `FB_TlsSocketConnect` / `FB_TlsSocketListen` 之前调用**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId : T_AmsNetId:='';
    hSocket   : T_HSOCKET;
    sCaPath   : STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE):='';
    bExecute  : BOOL;
    tTimeout  : TIME:=T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 由 `FB_TlsSocketCreate` 创建的 socket 句柄。**必须在 Connect/Listen 之前调本 FB** |
| `sCaPath` | `STRING(TCPADS_TLS_CERTIFICATE_PATH_SIZE)` | `''` | CA 证书 PEM 文件绝对路径（最长 `TCPADS_TLS_CERTIFICATE_PATH_SIZE = 255` 字节） |
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

**单次加载状态机**：上升沿 → `bBusy := TRUE`；Server 读 `sCaPath` 指向的 PEM 文件，解析 X.509 证书，追加到该 TLS socket 的 CA store；完成 → `bBusy := FALSE`、`bError := FALSE`。失败常见原因：文件不存在 → `TLS_CA_NOTFOUND`、文件存在但格式错或不是证书 → `TLS_CA_INVALID`、socket 已 Connect / Listen → `TLS_INVALID_STATE`。

**多 CA 加载**：同一 socket 多次调本 FB（用不同 `sCaPath`）会逐个追加到信任链，常用于"既信内部 CA 又信公共 CA"场景。

**何时不需要 CA**：

- 用 PSK 模式（`FB_TlsSocketSetPsk`）：完全跳过证书体系
- 客户端禁用了对端校验（`flags.bNoServerCertCheck := TRUE`）：开发期可这么调；生产**不要**
- 服务端单向 TLS 且 `flags.bNoClientCert := TRUE`：服务端不需要 CA

**典型陷阱**：路径写错（如反斜杠未转义、相对路径）→ `CA_NOTFOUND`；用 DER 二进制证书 → `CA_INVALID`，需要先用 OpenSSL 转 PEM；在 Connect/Listen 后才 AddCa → `TLS_INVALID_STATE`。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x00008080` | `TLS_INVALID_STATE` | 已 Connect/Listen，太晚 |
| `0x00008081` | `TLS_CA_NOTFOUND` | CA 证书文件不存在 |
| `0x00008084` | `TLS_CA_INVALID` | CA 证书文件读取或解析失败 |

## 5. 使用注意 / 常见坑

- **绝对路径**：用 `'C:\TwinCAT\3.1\Boot\Plc\TcpIpServer\ca.pem'` 之类完全限定路径；IEC ST 中反斜杠需要写两次或用正斜杠。
- **PEM 文件可包含多个证书**：完整证书链（root + intermediate）可拼到一个 PEM，一次 AddCa 即可。
- **证书更新策略**：服务端证书到期后客户端 AddCa 仍按旧 CA 验，若新签由新 CA 颁发，必须更新 CA 文件 + PLC 重启 TLS。
- **CA 撤销**：CA 自己撤销另说，需配合 CRL（`FB_TlsSocketAddCrl`）使用。
- **Windows CE / Arm 主机的路径**：用对应 OS 的路径风格，CE 上是 `'\Hard Disk\...'` 这种。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketAddCa.TcPOU`](../examples/P_Demo_FB_TlsSocketAddCa.TcPOU)

```iecst
// 场景：客户端 TLS socket 已创建，加载企业内部 CA 准备 Connect。
PROGRAM P_Demo_FB_TlsSocketAddCa
VAR
    fbAddCa        : FB_TlsSocketAddCa;
    hSocket        : T_HSOCKET;
    sCaPath        : STRING(255) := 'C:\TwinCAT\3.1\Boot\Plc\TcpIpServer\corp_ca.pem';
    bRequestAddCa  : BOOL;
    bAddCaBusy     : BOOL;
    bAddCaError    : BOOL;
    nAddCaErrId    : UDINT;
END_VAR

fbAddCa(
    sSrvNetId := '',
    hSocket   := hSocket,
    sCaPath   := sCaPath,
    bExecute  := bRequestAddCa,
    tTimeout  := T#5S,
    bBusy     => bAddCaBusy,
    bError    => bAddCaError,
    nErrId    => nAddCaErrId
);
```

## 7. 业务场景与实际价值

- **场景**：客户端：连企业内部 HTTPS API、连私有 MQTT broker，需要信任企业 CA；服务端：mTLS 接客户端时需要信任客户 CA 签发的客户端证书。
- **价值**：标准 X.509 PEM 装载，跨 OpenSSL / mbedTLS 兼容。
- **替代方案对比**：
  - 跳过校验（`bNoServerCertCheck := TRUE`）：开发期可以，生产严禁——等同 SSL stripping
  - 用系统 CA 库：本 FB 是显式装载用户自己的 CA，比依赖 OS root store 更可控

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.16
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511048331.html
- **相关**：`FB_TlsSocketCreate`（前置）、`FB_TlsSocketAddCrl`（吊销列表）、`FB_TlsSocketSetCert`（本端证书）、`FB_TlsSocketConnect` / `FB_TlsSocketListen`（后续）
