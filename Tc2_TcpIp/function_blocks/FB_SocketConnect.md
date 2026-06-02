# FB_SocketConnect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84141451.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketConnect.TcPOU`](../examples/P_Demo_FB_SocketConnect.TcPOU) |

---

## 1. 功能简述

TCP/IP 主动建连功能块：让本机 PLC 作为客户端，向远端服务器（IP + 端口）发起一条 TCP 连接。`bExecute` 上升沿触发一次握手，成功后从 `hSocket` 输出一个连接句柄（`T_HSOCKET`），后续 `FB_SocketSend` / `FB_SocketReceive` 用此句柄收发数据；不再需要时用 `FB_SocketClose` 关闭。一个 FB 实例对应一条连接；要建多条同时连同一服务器的并发链路，只需多实例化几个 `FB_SocketConnect`，TwinCAT TCP/IP Connection Server 会为每条连接分配独立的本地端口。

底层走 ADS：PLC ↔ TwinCAT TCP/IP Connection Server ↔ Berkeley socket。运行需要 TF6310 license。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId   : T_AmsNetId := '';
    sRemoteHost : T_IPv4Addr := '';
    nRemotePort : UDINT;
    bExecute    : BOOL;
    tTimeout    : TIME := T#45s;(*!!!*)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TwinCAT TCP/IP Connection Server 的 AMS NetID。本机可用空串 `''` 或 `'127.0.0.1'` |
| `sRemoteHost` | `T_IPv4Addr` | `''` | 远端服务器 IPv4 字符串（例如 `'172.33.5.1'`）。若服务器在本机可用空串 |
| `nRemotePort` | `UDINT` | — | 远端服务器 IP 端口号（例如 `200`） |
| `bExecute` | `BOOL` | — | 上升沿触发一次建连请求 |
| `tTimeout` | `TIME` | `T#45s` | 单次建连允许的最长时间。**不要设得太小**：网络中断时握手可能 > 30 秒，太短会被 ADS 内部以错误 1861（timeout）截断，而不是返回 Winsock 错误 WSAETIMEDOUT |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy      : BOOL;
    bError     : BOOL;
    nErrId     : UDINT;
    hSocket    : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块正在执行（等待 TCP 握手完成）。完成后自动回落 |
| `bError` | `BOOL` | `bBusy` 落回时若发生错误置 `TRUE`，下一次 `bExecute` 上升沿前保持 |
| `nErrId` | `UDINT` | 错误码：TwinCAT TCP/IP Connection Server 错误号（包含 ADS 系统错误 + Server 内部 32768–33023 + Win32 Socket 0x80070000–0x8007FFFF 三大区段） |
| `hSocket` | `T_HSOCKET` | 新建立连接的句柄。结构含 `handle : UDINT`、`localAddr`、`remoteAddr` 三字段。仅在 `bBusy=FALSE` 且 `bError=FALSE` 时有效 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：仅 `bExecute` 由 `FALSE → TRUE` 上升沿触发一次建连。电平为 `TRUE` 不会反复重连；要重连必须先把 `bExecute` 拉回 `FALSE` 再上升一次。

**状态机**：

1. 上升沿到 → `bBusy := TRUE`，FB 通过 ADS 调用 Connection Server 发起 `connect()`
2. Server 完成 TCP 三次握手（或因超时/拒绝/不可达而失败）
3. 握手成功 → `bBusy := FALSE`、`bError := FALSE`、`hSocket` 输出有效句柄
4. 握手失败 → `bBusy := FALSE`、`bError := TRUE`、`nErrId` 含错误码、`hSocket` 内容无效（不要使用）

**调用周期**：连接尚未完成时（`bBusy = TRUE`），调用方必须在每个 PLC 任务周期继续调用本 FB 实例（不需要再次给 `bExecute`），让内部 ADS 状态机推进。这一点和 `FB_WriteWatchdog` 等 ADS 异步 FB 一致。

**并发实例**：要同时与同一远端服务器建多条连接，实例化多个 `FB_SocketConnect`，每个独立 `bExecute` 上升沿；TCP/IP Connection Server 会为每条新连接分配独立的本地端口号（在 `hSocket.localAddr.nPort` 中可见）。

**句柄寿命**：得到的 `hSocket` 是 OS 级紧缺资源。**每次成功 connect 必须配一次 `FB_SocketClose`**，否则 PLC 重启时旧句柄会残留（PLC 程序对句柄已失忆，Server 仍持有），此时需在 PLC 启动用 `FB_SocketCloseAll` 一次性清空本运行时打开过的全部句柄。

**典型陷阱**：

- 用 `tTimeout := T#1s` 这种短值：在 WAN/不稳定网络上几乎必报 1861 假超时
- 把 `bExecute` 接到电平信号（如 `bConnect`）：电平 `TRUE` 持续期间 FB 只触发一次（首次上升沿），不会自动重连；如果对端断开后想自动重连，需要外部检测 `bError=TRUE` 后把 `bExecute` 复位再触发
- 在 `bBusy=TRUE` 期间读取 `hSocket`：内容未定，必须等 `bBusy=FALSE` 再读

## 4. 错误码 / 返回值

错误号 `nErrId` 含义按取值范围分段（参考 PDF §7.3.1）：

| 范围（hex） | 范围（dec） | 来源 | 含义 |
|---|---|---|---|
| `0x00000000`–`0x00007800` | 0–30720 | TwinCAT 系统错误 / ADS 错误码 | 例 `1861` = ADS timeout、`1808` = 找不到符号、`6/7` = 路由/目标不可达 |
| `0x00008000`–`0x000080FF` | 32768–33023 | TCP/IP Connection Server 内部错误码 | 见下表 |
| `0x80070000`–`0x8007FFFF` | 2147942400–2148007935 | Win32 / Winsock 错误码 | 真实错误号 = `nErrId - 0x80070000`，按 `E_WinsockError` 枚举映射 |

`FB_SocketConnect` 常见 Server 内部错误（PDF §7.3.2）：

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008001` | `TCPADSERROR_NOMOREENTRIES` | TCP/IP Connection Server 已无空闲 socket 槽位（系统并发连接数上限） |
| `0x00008006` | `TCPADSERROR_HOST_NOT_FOUND` | 远端服务器不可达（IP 错或路由不通） |

常见 Winsock 错误（`nErrId - 0x80070000` 后查 `E_WinsockError`）：

| Winsock 码 | 符号 | 含义 |
|---|---|---|
| 10060 | `WSAETIMEDOUT` | 远端在限定时间未响应（最常见的真正"对端不在线"错误） |
| 10061 | `WSAECONNREFUSED` | 远端机器存在但目标端口无服务监听 |
| 10065 | `WSAEHOSTUNREACH` | 路由层判定不可达 |

## 5. 使用注意 / 常见坑

- **TF6310 license 必装**：未装时 Server 无法启动，`bError` 立刻置 `TRUE` 且 `nErrId` 指向 license 错误。
- **PLC 重启留下"幽灵句柄"**：PLC Reset / Download 后旧 `hSocket` 在 PLC 程序里没了，但 Server 仍持有 OS socket。**强制在 PLC 启动阶段调用一次 `FB_SocketCloseAll`**（PDF §5.1.3 明确建议）。
- **不要在一个 PLC 周期内拉高 `bExecute` 又立刻拉低**：FB 内部依赖电平稳定的上升沿，过短的脉冲可能错过。建议保持 `bExecute := TRUE` 直到看到 `bBusy = FALSE`，然后再决定何时复位。
- **句柄不能在不同 PLC 任务间共享读写**：`T_HSOCKET` 是值类型结构，跨任务复制后 Server 端识别不到第二份"克隆"句柄的所有权。如要跨任务收发，把 `FB_SocketSend` / `FB_SocketReceive` 也放到产生 `hSocket` 的同一任务里。（工程经验补充）
- **想"长连接 + 断线自动重连"**：典型做法是外面包一层状态机——握手成功后保持连接，每周期调 `FB_SocketReceive` 拿心跳；一旦 `nErrId` 报 `WSAECONNRESET` / `WSAESHUTDOWN`，先 `FB_SocketClose` 再 `bExecute` 上升沿重连。或直接用 `FB_ClientServerConnection`（PDF §5.1.20.1）把这套自动化好的版本。
- **`'127.0.0.1'` 不等于 `''`**：空串走默认 Server NetID，回环 IP 走显式 IP；多网卡机器在 0.0.0.0 / 127.0.0.1 路由切换时这两者表现可能不同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketConnect.TcPOU`](../examples/P_Demo_FB_SocketConnect.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：PLC 作为 MES 客户端，连到 MES 服务器（172.16.6.180:2404），上电后建连一次，
//       一次完整的"建连 → 发一条订单查询 → 收回 → 关闭"演示。
PROGRAM P_Demo_FB_SocketConnect
VAR
    fbConnectToMes      : FB_SocketConnect;
    fbCloseMesSocket    : FB_SocketClose;
    fbSendQuery         : FB_SocketSend;

    bRequestConnect     : BOOL := FALSE;        // 在线置 TRUE 触发建连
    bConnectBusy        : BOOL;
    bConnectError       : BOOL;
    nConnectErrId       : UDINT;
    hMesSocket          : T_HSOCKET;            // 建连成功后填充

    bRequestClose       : BOOL;
    sQueryPayload       : STRING(80) := 'GET /order/status HTTP/1.0$R$L$R$L';
    bSendDone           : BOOL;
END_VAR

// ---- 阶段 1：建连（bRequestConnect 上升沿触发一次） ----
fbConnectToMes(
    sSrvNetId   := '',
    sRemoteHost := '172.16.6.180',
    nRemotePort := 2404,
    bExecute    := bRequestConnect,
    tTimeout    := T#45S,
    bBusy       => bConnectBusy,
    bError      => bConnectError,
    nErrId      => nConnectErrId,
    hSocket     => hMesSocket
);

// ---- 阶段 2：连接成功后发一条查询 ----
fbSendQuery(
    sSrvNetId := '',
    hSocket   := hMesSocket,
    cbLen     := TO_UDINT(LEN(sQueryPayload)),
    pSrc      := ADR(sQueryPayload),
    bExecute  := NOT bConnectBusy AND NOT bConnectError AND bRequestConnect,
    tTimeout  := T#5S,
    bBusy     => ,
    bError    => ,
    nErrId    => ,
    bDone     := bSendDone
);

// ---- 阶段 3：关闭（bRequestClose 上升沿触发） ----
fbCloseMesSocket(
    sSrvNetId := '',
    hSocket   := hMesSocket,
    bExecute  := bRequestClose,
    tTimeout  := T#5S
);
```

> 注：`FB_SocketSend` 实际没有 `bDone` 输出；此处例程把它压缩为单次发送演示。完整收发对照 `FB_SocketSend.md` / `FB_SocketReceive.md` 文档。

## 7. 业务场景与实际价值

- **场景**：PLC ↔ MES 系统（TCP 1414/2404/9000…端口报工/查询）；PLC ↔ 条码扫描枪（TCP 23/9100）；PLC ↔ 打印机 / IoT 网关 / 视觉服务器。凡是对端跑在 **非 TwinCAT** 的服务器上、需要 PLC 主动建连的，都用本 FB。
- **价值**：把"PLC 内部 ADS 调用 Connection Server → Server 调 Berkeley socket → 三次握手 → 错误码翻译"这套全封装为 4 输入 4 输出。业务代码不再 care 底层 socket，只关心 IP/端口/时序。
- **替代方案对比**：
  - 自己用 EL6601 / EL6614 等串口/以太网模块：硬件成本高、协议自实现
  - 用 ADS：仅适合 TwinCAT ↔ TwinCAT；不能与第三方系统通讯
  - 用 OPC UA（Tc3_PLCopen_OpcUa）：协议重，需对端也实现 OPC UA
  - **本 FB**：纯 TCP 流，与任何符合 socket 的对端互通，但需 TF6310 license

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84141451.html
- **相关**：`FB_SocketClose`（必须配对）、`FB_SocketCloseAll`（启动清理）、`FB_SocketSend` / `FB_SocketReceive`（收发）、`FB_TlsSocketConnect`（TLS 加密版）、`FB_ClientServerConnection`（封装了自动重连的 helper）、`E_WinsockError`、`T_HSOCKET`
