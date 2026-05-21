# FB_TlsSocketListen

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12510319755.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketListen.xml`](../examples/P_Demo_FB_TlsSocketListen.xml) |

---

## 1. 功能简述

TLS 加密 TCP 监听 socket 启动功能块：把一个已 `FB_TlsSocketCreate(bListener := TRUE)` 创建并配置好服务端证书的 socket 转为 TLS 监听状态。本 FB 完成 `bind() + listen()` 之后，使用普通的 `FB_SocketAccept` 接受 incoming 客户端连接——但每条 accept 出来的子连接句柄已经携带 TLS 上下文，对应用层透明加密。需要 TF6310 v3.3.15.0 或更高版本。监听端口在同机器必须唯一。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId  : T_AmsNetId:='';
    sLocalHost : T_IPv4Addr:='';
    nLocalPort : UDINT:=0;
    flags      : ST_TlsListenFlags:=DEFAULT_TLSLISTENFLAGS;
    bExecute   : BOOL;
    tTimeout   : TIME:=T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `sLocalHost` | `T_IPv4Addr` | `''` | 监听 IPv4 字符串。生产环境显式 `'0.0.0.0'` 监听所有网卡 |
| `nLocalPort` | `UDINT` | `0` | 本地服务端口（如 8443 HTTPS） |
| `flags` | `ST_TlsListenFlags` | `DEFAULT_TLSLISTENFLAGS` | TLS 服务端可选项：`bNoClientCert`（不要求客户端证书，即单向 TLS） |
| `bExecute` | `BOOL` | — | 上升沿触发一次"开监听" |
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
| `bBusy` | `BOOL` | 正在开 listener |
| `bError` | `BOOL` | 失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hListener : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hListener` | `T_HSOCKET` | 由 `FB_TlsSocketCreate(bListener := TRUE)` 创建并 SetCert / AddCa 配置好的 socket 句柄；本 FB 把它转为监听状态 |

## 3. 行为说明

**前置步骤**（顺序固定）：
1. `FB_TlsSocketCreate(bListener := TRUE)` 拿 `hListener`
2. **必须**：`FB_TlsSocketSetCert` 配置服务端证书 + 私钥（PEM 格式）
3. 可选：`FB_TlsSocketAddCa` 配置 CA（双向 TLS 时验客户端证书用）
4. 可选：`FB_TlsSocketAddCrl` 配置吊销列表
5. 可选：`FB_TlsSocketSetPsk`（PSK 模式无需证书）
6. 现在才能调本 FB

**单次开监听状态机**：上升沿 → `bBusy := TRUE`；Server `bind() + listen()`；完成 → `bBusy := FALSE`、`bError := FALSE`、`hListener` 现处于监听状态。

**`flags.bNoClientCert` 用法**：`TRUE` = 不要求客户端递交证书（单向 TLS，浏览器 / 大多数 HTTPS 场景）；`FALSE` = 要求双向 TLS（mTLS），客户端必须出示证书，此时**必须**调 `FB_TlsSocketAddCa` 配置受信任 CA。

**Accept 子连接**：listener 开好后用 **普通 `FB_SocketAccept`** 接 incoming，accept 出来的客户端句柄已带 TLS 上下文。subsequent `FB_SocketSend` / `FB_SocketReceive` 自动加解密。

**典型陷阱**：忘 `SetCert` 直接 Listen → `bError`，握手时所有客户端都拒绝；端口被占 → `WSAEADDRINUSE`；同端口已开 listener → `ALREADYEXISTS`；listener socket 在 Listen 后再做 TLS 设置 → `TLS_INVALID_STATE`。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008003` | `TCPADSERROR_ALREADYEXISTS` | 同端口已有 listener |
| `0x00008080` | `TLS_INVALID_STATE` | TLS 设置在 Listen 后调 |
| `0x00008082` | `TLS_CERT_NOTFOUND` | 服务端证书未配置或路径错 |
| `0x80072740` | `WSAEADDRINUSE` (10048) | 端口被 OS 上其他服务占 |
| `0x80072741` | `WSAEADDRNOTAVAIL` (10049) | 指定 IP 在本机不存在 |

外加常规 socket 错误。

## 5. 使用注意 / 常见坑

- **必须 SetCert**：没有服务端证书的 TLS listener 等于无意义（客户端必然拒绝），TF6310 也会直接报错。
- **`flags.bNoClientCert := TRUE` 是 HTTPS 风格的默认**：客户端单向认证服务端。仅当需要 mTLS（如工业 IoT 双向认证）才设 `FALSE` 并 `AddCa`。
- **TF6310 v3.3.15.0+ 支持**：旧版没 TLS。
- **证书私钥保护**：`FB_TlsSocketSetCert` 的 `sKeyPwd` 字段——生产环境务必使用加密的私钥，明文私钥放磁盘等于裸奔。
- **不要混 TLS / 非 TLS listener 在同端口**：一个端口要么纯 TLS 要么纯明文，不能同时支持两种。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketListen.xml`](../examples/P_Demo_FB_TlsSocketListen.xml)

```iecst
// 场景：PLC 在 8443 端口启 HTTPS-like 监听（单向 TLS）。
PROGRAM P_Demo_FB_TlsSocketListen
VAR
    fbCreateTlsListener : FB_TlsSocketCreate;
    fbSetServerCert     : FB_TlsSocketSetCert;
    fbStartTlsListen    : FB_TlsSocketListen;
    hListener           : T_HSOCKET;
    stListenFlags       : ST_TlsListenFlags := (bNoClientCert := TRUE);
    bRequestListen      : BOOL;
    bListenBusy         : BOOL;
    bListenError        : BOOL;
    nListenErrId        : UDINT;
END_VAR

// 阶段 A 由 Create / SetCert 完成后再触发本 FB
fbStartTlsListen(
    sSrvNetId  := '',
    sLocalHost := '0.0.0.0',
    nLocalPort := 8443,
    flags      := stListenFlags,
    bExecute   := bRequestListen,
    tTimeout   := T#5S,
    hListener  := hListener,
    bBusy      => bListenBusy,
    bError     => bListenError,
    nErrId     => nListenErrId
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 在车间提供 HTTPS 风格的 REST 接口给上位机查询、提供 OPC UA over TLS 服务、给手持终端提供加密接入。任何"PLC 暴露端口给外部"的场景都建议 TLS。
- **价值**：单一 FB 把 TLS 监听 + TCP listen 一并完成；服务端 ↔ 客户端的应用层代码完全不用动。
- **替代方案对比**：
  - 反向代理（Nginx 代收 TLS）：架构更重，需要额外机器；本 FB 让 PLC 自己卷起袖子做
  - 直跑明文 `FB_SocketListen`：纯内网 OK，跨网或出公网必加密

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12510319755.html
- **相关**：`FB_TlsSocketCreate`（前置）、`FB_TlsSocketSetCert`（必须）、`FB_TlsSocketAddCa` / `AddCrl`（mTLS 用）、`FB_SocketAccept`（接受 incoming）、`ST_TlsListenFlags`
