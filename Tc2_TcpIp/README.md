# Tc2_TcpIp（TF6310 TCP/UDP Server）

> Beckhoff TwinCAT 3 TCP/IP / UDP / TLS socket 客户端 + 服务器 PLC API。
> 这是 TF6310 TwinCAT TCP/UDP Server 的 PLC 库——运行时需要 TF6310 license。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.5.2` |
| 来源 PDF | [TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/ |
| 文档进度 | 24 / 24 (FB + FC + GVL，DUT 仅作引用) |

**与 ADS 的区别**：Tc2_TcpIp 走标准 Berkeley socket 模型，用于 PLC ↔ **非 TwinCAT** 对端（Linux / Windows server、嵌入式扫描枪、IoT 网关、云服务）。TwinCAT ↔ TwinCAT 之间用 ADS 即可（`Tc2_DataExchange`、`Tc2_Utilities` 等）更高效，不必用本库。

## 典型部署模板

### TCP 客户端
`FB_SocketCloseAll`（启动期一次） → `FB_SocketConnect` → `FB_SocketSend` / `FB_SocketReceive`（周期收发） → `FB_SocketClose`

### TCP 服务器
`FB_SocketCloseAll`（启动期） → `FB_SocketListen` → `FB_SocketAccept`（周期 polling） → 每客户端一对 `FB_SocketSend` + `FB_SocketReceive` → `FB_SocketClose`（每子连接 + 最后 listener）

### UDP 收发
`FB_SocketUdpCreate` → `FB_SocketUdpSendTo` / `FB_SocketUdpReceiveFrom` → `FB_SocketClose`

### UDP 多播接收
`FB_SocketUdpCreate` → `FB_SocketUdpAddMulticastAddress` → `FB_SocketUdpReceiveFrom` → `FB_SocketUdpDropMulticastAddress` → `FB_SocketClose`

### TLS 客户端
`FB_TlsSocketCreate(bListener := FALSE)` → `FB_TlsSocketAddCa`（+ 可选 `AddCrl` / `SetCert` 双向认证 / `SetPsk` 替代证书） → `FB_TlsSocketConnect` → 普通 `FB_SocketSend` / `FB_SocketReceive` → `FB_SocketClose`

### TLS 服务器
`FB_TlsSocketCreate(bListener := TRUE)` → `FB_TlsSocketSetCert`（必须） → 可选 `AddCa` / `AddCrl` → `FB_TlsSocketListen` → 普通 `FB_SocketAccept` → 普通 `FB_SocketSend` / `FB_SocketReceive`

## Function Blocks（19）

### TCP / 通用 socket 管理（7）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_SocketConnect` | 客户端建连 | [function_blocks/FB_SocketConnect.md](function_blocks/FB_SocketConnect.md) |
| `FB_SocketClose` | 关闭单个 socket（TCP / UDP 通用） | [function_blocks/FB_SocketClose.md](function_blocks/FB_SocketClose.md) |
| `FB_SocketCloseAll` | 启动期一次性清掉本 runtime 全部遗留 socket | [function_blocks/FB_SocketCloseAll.md](function_blocks/FB_SocketCloseAll.md) |
| `FB_SocketListen` | 服务端开监听 | [function_blocks/FB_SocketListen.md](function_blocks/FB_SocketListen.md) |
| `FB_SocketAccept` | 接受 incoming 客户端连接 | [function_blocks/FB_SocketAccept.md](function_blocks/FB_SocketAccept.md) |
| `FB_SocketSend` | 通过句柄发字节流 | [function_blocks/FB_SocketSend.md](function_blocks/FB_SocketSend.md) |
| `FB_SocketReceive` | 通过句柄收字节流 | [function_blocks/FB_SocketReceive.md](function_blocks/FB_SocketReceive.md) |

### UDP（5）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_SocketUdpCreate` | 创建 UDP socket | [function_blocks/FB_SocketUdpCreate.md](function_blocks/FB_SocketUdpCreate.md) |
| `FB_SocketUdpSendTo` | 发 UDP 数据报到任意对端 | [function_blocks/FB_SocketUdpSendTo.md](function_blocks/FB_SocketUdpSendTo.md) |
| `FB_SocketUdpReceiveFrom` | 收 UDP 数据报（含来源 IP/Port） | [function_blocks/FB_SocketUdpReceiveFrom.md](function_blocks/FB_SocketUdpReceiveFrom.md) |
| `FB_SocketUdpAddMulticastAddress` | UDP socket 加入多播组 | [function_blocks/FB_SocketUdpAddMulticastAddress.md](function_blocks/FB_SocketUdpAddMulticastAddress.md) |
| `FB_SocketUdpDropMulticastAddress` | UDP socket 退出多播组 | [function_blocks/FB_SocketUdpDropMulticastAddress.md](function_blocks/FB_SocketUdpDropMulticastAddress.md) |

### TLS（7）—— 需 TF6310 v3.3.15.0+

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_TlsSocketCreate` | 创建 TLS context socket（client 或 server） | [function_blocks/FB_TlsSocketCreate.md](function_blocks/FB_TlsSocketCreate.md) |
| `FB_TlsSocketConnect` | 客户端 TLS 握手 + 建连 | [function_blocks/FB_TlsSocketConnect.md](function_blocks/FB_TlsSocketConnect.md) |
| `FB_TlsSocketListen` | 服务端 TLS 监听 | [function_blocks/FB_TlsSocketListen.md](function_blocks/FB_TlsSocketListen.md) |
| `FB_TlsSocketAddCa` | 加载 CA 证书（验对端） | [function_blocks/FB_TlsSocketAddCa.md](function_blocks/FB_TlsSocketAddCa.md) |
| `FB_TlsSocketAddCrl` | 加载 CRL（吊销列表） | [function_blocks/FB_TlsSocketAddCrl.md](function_blocks/FB_TlsSocketAddCrl.md) |
| `FB_TlsSocketSetCert` | 加载本端证书 + 私钥 | [function_blocks/FB_TlsSocketSetCert.md](function_blocks/FB_TlsSocketSetCert.md) |
| `FB_TlsSocketSetPsk` | 加载 PSK 预共享密钥（替代证书） | [function_blocks/FB_TlsSocketSetPsk.md](function_blocks/FB_TlsSocketSetPsk.md) |

> §5.1.20 "Helper" 部分（`FB_ClientServerConnection` / `FB_ServerClientConnection` / `FB_ConnectionlessSocket`）在 PDF 中是上述基本 FB 的封装；本仓库 24 篇覆盖了独立可用的基本 FB，helper 在后续 PR 中考虑补充。

## Functions（4）

| 名称 | 用途 | 文档 |
|---|---|---|
| `F_CreateServerHnd` | 初始化 `T_HSERVER`（给 `FB_ServerClientConnection` 用） | [functions/F_CreateServerHnd.md](functions/F_CreateServerHnd.md) |
| `HSOCKET_TO_STRING` | `T_HSOCKET` → 字串（含 Handle / Local / Remote） | [functions/HSOCKET_TO_STRING.md](functions/HSOCKET_TO_STRING.md) |
| `HSOCKET_TO_STRINGEX` | `T_HSOCKET` → 字串（可选 Local / Remote） | [functions/HSOCKET_TO_STRINGEX.md](functions/HSOCKET_TO_STRINGEX.md) |
| `SOCKETADDR_TO_STRING` | `ST_SockAddr` → 字串（仅地址） | [functions/SOCKETADDR_TO_STRING.md](functions/SOCKETADDR_TO_STRING.md) |

## Global Constants（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `stLibVersion_Tc2_TcpIp` | 库版本结构（运行时版本检查用） | [global_constants/stLibVersion_Tc2_TcpIp.md](global_constants/stLibVersion_Tc2_TcpIp.md) |

## DUTs（9，未单独成文档）

以下数据类型在 §5.3 出现，作为上述 FB / FC 的参数 / 返回类型使用；不为单独条目生成 .md（按 CLAUDE.md 流程 DUT 在父 FB / FC 文档中按需引用）：

| 名称 | 类型 | 用途 |
|---|---|---|
| `E_SocketAcceptMode` | ENUM | `FB_ServerClientConnection.eMode` —— `eACCEPT_ALL` / `eACCEPT_SEL_HOST` / `eACCEPT_SEL_PORT` / `eACCEPT_SEL_HOST_PORT` |
| `E_SocketConnectionState` | ENUM | `FB_ClientServerConnection.eState` —— `eSOCKET_DISCONNECTED` / `eSOCKET_CONNECTED` / `eSOCKET_SUSPENDED` |
| `E_SocketConnectionlessState` | ENUM | `FB_ConnectionlessSocket.eState` —— `eSOCKET_CLOSED` / `eSOCKET_CREATED` / `eSOCKET_TRANSIENT` |
| `E_WinsockError` | ENUM | Winsock 错误码符号表（WSAEINTR=10004 … WSANO_DATA=11004），见 PDF §5.3.4 |
| `ST_SockAddr` | STRUCT | `nPort : UDINT` + `sAddr : STRING(15)`；含在 `T_HSOCKET.localAddr` / `remoteAddr` |
| `ST_TlsConnectFlags` | STRUCT | TLS 客户端可选项：`bNoServerCertCheck` / `bIgnoreCnMismatch` |
| `ST_TlsListenFlags` | STRUCT | TLS 服务端可选项：`bNoClientCert`（单向 TLS 时设 TRUE） |
| `T_HSERVER` | STRUCT | 不透明服务器句柄，仅给 `FB_ServerClientConnection` 用，必须经 `F_CreateServerHnd` 初始化 |
| `T_HSOCKET` | STRUCT | 连接句柄：`handle : UDINT` + `localAddr : ST_SockAddr` + `remoteAddr : ST_SockAddr` |

## 错误码概览

`nErrId` 输出按取值范围分三段（PDF §7.3.1）：

| 范围（hex） | 来源 | 含义 |
|---|---|---|
| `0x00000000`–`0x00007800` | ADS / TwinCAT 系统错误 | 例 `6` Port not found、`7` Machine not found、`1861` ADS timeout、`1808` Symbol not found |
| `0x00008000`–`0x000080FF` | Server 内部错误（含 TLS） | `8001` NOMOREENTRIES、`8002` NOTFOUND、`8003` ALREADYEXISTS、`8004` NOTCONNECTED、`8005` NOTLISTENING、`8006` HOST_NOT_FOUND、`8080`–`8092` TLS 系列 |
| `0x80070000`–`0x8007FFFF` | Win32 / Winsock | 真值 = `nErrId - 0x80070000`，按 `E_WinsockError` 枚举映射 |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 编译 → 登录 → 运行
4. 按文档 §6 / §7 中的"验证步骤"在线观察输入输出

## 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf)
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/
- **Beckhoff 官方示例代码**：https://github.com/Beckhoff/TF6310_Samples
