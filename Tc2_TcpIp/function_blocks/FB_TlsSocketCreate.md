# FB_TlsSocketCreate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511004043.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketCreate.TcPOU`](../examples/P_Demo_FB_TlsSocketCreate.TcPOU) |

---

## 1. 功能简述

TLS socket 创建功能块：创建一个新的、尚未配置 TLS 凭证、尚未发起握手或监听的 TLS 上下文 socket，由 `bListener` 输入决定其后用作客户端（`FALSE`）还是服务端（`TRUE`）。**这是 TLS 工作流的入口**——`FB_TlsSocketConnect` / `FB_TlsSocketListen` 不能凭空创建 socket，必须先用本 FB 拿到 `hSocket`，再用 `AddCa` / `SetCert` / `SetPsk` / `AddCrl` 系列填证书 / 密钥，最后才能 Connect 或 Listen。需要 TF6310 v3.3.15.0 或更高版本。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId : T_AmsNetId:='';
    bListener : BOOL:=FALSE;
    bExecute  : BOOL;
    tTimeout  : TIME:=T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `bListener` | `BOOL` | `FALSE` | `TRUE` = 创建服务端 listener socket（之后给 `FB_TlsSocketListen` 用）；`FALSE` = 创建客户端 socket（之后给 `FB_TlsSocketConnect` 用） |
| `bExecute` | `BOOL` | — | 上升沿触发一次创建 |
| `tTimeout` | `TIME` | `T#5s` | ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy   : BOOL;
    bError  : BOOL;
    nErrId  : UDINT;
    hSocket : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在创建 |
| `bError` | `BOOL` | 失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |
| `hSocket` | `T_HSOCKET` | 新创建的 TLS socket 句柄，仅 `bBusy=FALSE` 且 `bError=FALSE` 时有效 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次创建。

**单次创建状态机**：上升沿 → `bBusy := TRUE`；Server 内部分配 TLS context（OpenSSL/mbedTLS SSL_CTX 之类）+ 底层 TCP socket，但**还没 bind / connect / listen**；完成 → `bBusy := FALSE`、`bError := FALSE`、`hSocket` 输出。

**`bListener` 的影响**：仅设置内部"用作客户端 / 服务端"状态机标记，影响 TLS 握手时本端是 client_hello 发起方还是接收方。**创建后还能调 SetCert / AddCa 等设置**（这些不区分客户端/服务端，只是装填凭证）。

**与非 TLS Create 的差别**：普通 `FB_SocketUdpCreate` 把 socket bind 到本地端口；本 FB **不绑定端口**，因为：客户端模式下端口由 OS 在 Connect 时自动分配；服务端模式下端口由 `FB_TlsSocketListen` 的 `nLocalPort` 决定。

**典型陷阱**：把 client 用的 socket 错传给 `FB_TlsSocketListen`（或反之）——内部状态不一致，握手失败；忘了 Create 直接 SetCert / Connect / Listen——所有都报 `NOTFOUND`；同一句柄被 Create 多次而前一次未 Close——句柄泄漏。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008001` | `TCPADSERROR_NOMOREENTRIES` | Server socket / TLS context 槽位已满 |
| `0x00008088` | `TLS_SETUP` | TLS 上下文初始化失败（OpenSSL/mbedTLS 内部错） |
| `0x0000808D` | `TLS_INTERNAL_ERROR` | TLS 内部错误 |

## 5. 使用注意 / 常见坑

- **客户端 vs 服务端 socket 不能混用**：创建时 `bListener` 决定身份，后续 Connect/Listen 必须匹配。
- **创建后立刻配置凭证再 Connect/Listen**：顺序 Create → SetCert/AddCa/AddCrl/SetPsk → Connect/Listen 是硬性要求。Listen 后再 SetCert 会报 `TLS_INVALID_STATE`。
- **关闭仍用 `FB_SocketClose`**：TLS socket 和普通 socket 共用同一个 Close FB。
- **同时建多个 TLS socket**：多实例本 FB，每个独立 `hSocket`，互不影响。
- **句柄泄漏**：失败时 `bError=TRUE`，`hSocket` 没有有效值，不需要 Close；成功的句柄必须配 Close。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketCreate.TcPOU`](../examples/P_Demo_FB_TlsSocketCreate.TcPOU)

```iecst
// 场景：开两个 TLS socket，一个客户端连云，一个服务端在本机端口 8443 监听。
PROGRAM P_Demo_FB_TlsSocketCreate
VAR
    fbCreateClient : FB_TlsSocketCreate;
    fbCreateServer : FB_TlsSocketCreate;
    hClientSocket  : T_HSOCKET;
    hServerSocket  : T_HSOCKET;
    bRequestClient : BOOL;
    bRequestServer : BOOL;
    bClientBusy    : BOOL; bClientError : BOOL; nClientErr : UDINT;
    bServerBusy    : BOOL; bServerError : BOOL; nServerErr : UDINT;
END_VAR

fbCreateClient(sSrvNetId := '', bListener := FALSE,
               bExecute := bRequestClient, tTimeout := T#5S,
               bBusy => bClientBusy, bError => bClientError, nErrId => nClientErr,
               hSocket => hClientSocket);

fbCreateServer(sSrvNetId := '', bListener := TRUE,
               bExecute := bRequestServer, tTimeout := T#5S,
               bBusy => bServerBusy, bError => bServerError, nErrId => nServerErr,
               hSocket => hServerSocket);
```

## 7. 业务场景与实际价值

- **场景**：所有 TLS 通讯（出云、安全监控、加密 SCADA、mTLS 服务）都从此 FB 开始。
- **价值**：把 TLS context 初始化（涉及 SSL_CTX_new、密码套件协商表分配等）封装成一行调用，业务侧只关心 client/server 角色。
- **替代方案对比**：无替代——TLS 工作流的入口就是它。

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511004043.html
- **相关**：`FB_TlsSocketConnect` / `FB_TlsSocketListen`（终态）、`FB_TlsSocketAddCa` / `AddCrl` / `SetCert` / `SetPsk`（凭证配置）、`FB_SocketClose`（关闭仍用此 FB）
