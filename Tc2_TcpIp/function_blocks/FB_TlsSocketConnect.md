# FB_TlsSocketConnect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12510273547.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketConnect.TcPOU`](../examples/P_Demo_FB_TlsSocketConnect.TcPOU) |

---

## 1. 功能简述

TLS 加密 TCP 建连功能块：本机作为客户端，向远端服务器（IP + 端口）发起一条经过 TLS 握手的安全 TCP 连接。和 `FB_SocketConnect` 不同，本 FB 假设外部**已经创建好 socket 句柄**（通过 `FB_TlsSocketCreate`，并可选地通过 `FB_TlsSocketAddCa` / `FB_TlsSocketAddCrl` / `FB_TlsSocketSetCert` / `FB_TlsSocketSetPsk` 配置好 TLS 凭证），本 FB 只负责"用这个已配置 socket 跑一次 TLS 握手 + TCP 建连"。需要 TF6310 v3.3.15.0 或更高版本。后续收发仍用普通 `FB_SocketSend` / `FB_SocketReceive`（TLS 加密由 Server 透明处理）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId   : T_AmsNetId:='';
    sRemoteHost : STRING(TCPADS_TLS_HOSTNAME_SIZE):='';
    nRemotePort : UDINT:=0;
    flags       : ST_TlsConnectFlags:=DEFAULT_TLSCONNECTFLAGS;
    bExecute    : BOOL;
    tTimeout    : TIME:=T#45s;(*!!!*)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串或 `'127.0.0.1'` |
| `sRemoteHost` | `STRING(TCPADS_TLS_HOSTNAME_SIZE)` | `''` | 远端服务器 IPv4 / 主机名字符串（最长 `TCPADS_TLS_HOSTNAME_SIZE = 255` 字节）。**会用于 TLS 证书的 CommonName 校验**——所以这里写 IP 时若证书 CN 是域名，需要在 `flags.bIgnoreCnMismatch := TRUE` 或重新签证书 |
| `nRemotePort` | `UDINT` | `0` | 远端 TLS 服务端口（典型 443、8883 MQTT-TLS） |
| `flags` | `ST_TlsConnectFlags` | `DEFAULT_TLSCONNECTFLAGS` | TLS 客户端可选项：`bNoServerCertCheck`（禁用证书校验）/ `bIgnoreCnMismatch`（忽略 CN 不匹配）。详见 `ST_TlsConnectFlags` |
| `bExecute` | `BOOL` | — | 上升沿触发一次 TLS 建连 |
| `tTimeout` | `TIME` | `T#45s` | 单次握手 + 建连超时。TLS 握手往返多次，**不要短于 30 秒** |

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
| `bBusy` | `BOOL` | 正在执行 TLS 握手 |
| `bError` | `BOOL` | 建连或握手失败 |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号（含 TLS 专有错误码 `0x80h` 段） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hSocket : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hSocket` | `T_HSOCKET` | 已通过 `FB_TlsSocketCreate(bListener := FALSE)` 创建并配置好 TLS 凭证的 socket 句柄。本 FB 完成握手后该句柄即可用于 `FB_SocketSend` / `FB_SocketReceive` |

## 3. 行为说明

**前置步骤**：本 FB **不创建 socket**——必须先：
1. `FB_TlsSocketCreate(bListener := FALSE)` 拿到 `hSocket`
2. 可选：`FB_TlsSocketAddCa` 配置 CA 证书路径（验对端证书用）
3. 可选：`FB_TlsSocketAddCrl` 配置 CRL（吊销列表）
4. 可选：`FB_TlsSocketSetCert` 配置客户端证书（双向 TLS 时）
5. 可选：`FB_TlsSocketSetPsk` 配置预共享密钥（PSK 模式）
6. 现在才能调本 FB

**TLS 握手时序**：上升沿 → `bBusy := TRUE`；底层先做 TCP 三次握手，再做 TLS 握手（ClientHello → ServerHello + Cert → 密钥协商 → Finished）。整个过程典型 100 ms–1 s，慢网或慢 CPU 上可能几秒。完成 → `bBusy := FALSE`、`bError := FALSE`，`hSocket` 现在指向已加密的安全连接。

**证书校验逻辑**：默认行为是严格校验——服务器证书必须由本机配置的 CA 链签发、未在 CRL、CN 匹配 `sRemoteHost`、未过期、未吊销。任一条失败 → `bError := TRUE`、`nErrId` 对应 TLS 错误码（如 `0x00008087` `TLS_VERIFY_FAIL`、`0x0000808F` `TLS_CN_MISMATCH`、`0x00008090` `TLS_CERT_EXPIRED`、`0x00008091` `TLS_CERT_REVOKED`）。开发期可用 `flags.bNoServerCertCheck := TRUE` 跳过校验调通后再开严格；生产环境务必关回。

**典型陷阱**：`tTimeout` 太短（< 30 s）导致 TLS 握手没跑完就超时；忘了先 `Create` 直接 Connect 报 `NOTFOUND`；用 IP 当 `sRemoteHost` 但证书 CN 是域名导致 `CN_MISMATCH`；忘 Add CA → 服务端证书没法验 → `VERIFY_FAIL`。

## 4. 错误码 / 返回值

TLS 专有错误（PDF §7.3.2）：

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008080` | `TLS_INVALID_STATE` | TLS 设置在 Connect 后调（顺序错） |
| `0x00008087` | `TLS_VERIFY_FAIL` | 对端证书校验失败 |
| `0x00008088` | `TLS_SETUP` | TLS 设置出错 |
| `0x00008089` | `TLS_HANDSHAKE_FAIL` | TLS 握手出错 |
| `0x0000808A` | `TLS_CIPHER_INVALID` | 算法套件无效 |
| `0x0000808B` | `TLS_VERSION_INVALID` | TLS 版本无效 |
| `0x0000808F` | `TLS_CN_MISMATCH` | 证书 CN 与 `sRemoteHost` 不符 |
| `0x00008090` | `TLS_CERT_EXPIRED` | 证书过期 |
| `0x00008091` | `TLS_CERT_REVOKED` | 证书被吊销 |
| `0x00008092` | `TLS_CERT_MISSING` | 对端未递交证书 |

外加 ADS `1861` (timeout) 和常规 socket 错误。

## 5. 使用注意 / 常见坑

- **顺序敏感**：Create → (AddCa / AddCrl / SetCert / SetPsk 任意子集) → Connect。**TLS 设置必须在 Connect 之前**，否则报 `TLS_INVALID_STATE`。
- **证书路径**：`FB_TlsSocketAddCa` / `SetCert` 用的是 PEM 文件**绝对路径**（在目标 PLC 主机上）。开发期建议放 `C:\TwinCAT\3.1\Boot\<x>\` 之类标准位置。
- **`flags` 用法**：开发期 `bNoServerCertCheck := TRUE` + `bIgnoreCnMismatch := TRUE` 可快速调通；生产必须关回，**否则 TLS 退化为只加密不认证，等同 SSL stripping 易被中间人攻击**。
- **PSK 模式不需要证书**：用 `FB_TlsSocketSetPsk` 代替 `AddCa + SetCert`，适合 IoT 场景。
- **建连成功后 socket 句柄继续走普通 Send/Receive**：TLS 加解密对应用层透明，业务代码与 `FB_SocketConnect` 路径完全一致。
- **TF6310 v3.3.15.0 起支持**：旧版本没有 TLS 系列 FB。检查目标 PLC 上的 TF6310 版本。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketConnect.TcPOU`](../examples/P_Demo_FB_TlsSocketConnect.TcPOU)

```iecst
// 场景：PLC 连云端 MQTT-TLS broker（mqtt.example.com:8883）做安全遥测。
PROGRAM P_Demo_FB_TlsSocketConnect
VAR
    fbCreateTls    : FB_TlsSocketCreate;
    fbAddCa        : FB_TlsSocketAddCa;
    fbTlsConnect   : FB_TlsSocketConnect;
    hCloudSocket   : T_HSOCKET;
    bCreateReq     : BOOL;
    bAddCaReq      : BOOL;
    bConnectReq    : BOOL;
    stConnFlags    : ST_TlsConnectFlags := (bNoServerCertCheck := FALSE, bIgnoreCnMismatch := FALSE);
    bConnBusy      : BOOL;
    bConnError     : BOOL;
    nConnErrId     : UDINT;
END_VAR

// 阶段 A 由 Create / AddCa 完成后再触发本 FB（详见示例文件）
fbTlsConnect(
    sSrvNetId   := '',
    sRemoteHost := 'mqtt.example.com',
    nRemotePort := 8883,
    flags       := stConnFlags,
    bExecute    := bConnectReq,
    tTimeout    := T#45S,
    hSocket     := hCloudSocket,
    bBusy       => bConnBusy,
    bError      => bConnError,
    nErrId      => nConnErrId
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 连云端 MQTT-TLS / HTTPS API / 安全 IoT 网关；机房 ↔ 现场跨公网的 SCADA 通讯；PLC 上送数据到 Azure / AWS IoT。所有"出工厂网"的连接都建议走 TLS。
- **价值**：把 TLS 握手 / 证书校验 / 密钥协商封装在 Connection Server 里，PLC 业务代码与明文 TCP 几乎一致。
- **替代方案对比**：
  - 明文 TCP + VPN：管 IT 同事得部署 VPN；TLS 直连更简单
  - HTTPS 库（如自定义）：协议级要重写
  - **本 FB**：标准 TLS 1.2/1.3，由 Beckhoff 维护底层 OpenSSL/mbedTLS

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12510273547.html
- **相关**：`FB_TlsSocketCreate`（前置必须）、`FB_TlsSocketAddCa` / `AddCrl` / `SetCert` / `SetPsk`（配置）、`FB_SocketSend` / `FB_SocketReceive`（建连后收发）、`ST_TlsConnectFlags`
