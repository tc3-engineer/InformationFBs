# FB_SocketUdpCreate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84152203.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketUdpCreate.xml`](../examples/P_Demo_FB_SocketUdpCreate.xml) |

---

## 1. 功能简述

UDP socket 创建功能块：在本机指定网卡 IP + 端口上创建一个 UDP socket，返回句柄 `hSocket`。此句柄给 `FB_SocketUdpSendTo` 发包、给 `FB_SocketUdpReceiveFrom` 收包用；不再需要时调 `FB_SocketClose` 关闭。和 TCP 不同，UDP 是无连接的：一个 socket 句柄就能与多个对端通信（每次 send/receive 各自带 IP+Port）。`sLocalHost := ''` 在多网卡机器上可能导致 socket 绑到回环 IP `127.0.0.1`，建议生产环境显式指定网卡 IP 或 `0.0.0.0`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId  : T_AmsNetId := '';
    sLocalHost : T_IPv4Addr := '';
    nLocalPort : UDINT;
    bExecute   : BOOL;
    tTimeout   : TIME:= T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server 的 AMS NetID。本机用空串 |
| `sLocalHost` | `T_IPv4Addr` | `''` | 要绑定的本地网卡 IPv4 字符串。空串走默认网卡，多网卡机器结果不确定 |
| `nLocalPort` | `UDINT` | — | 要绑定的本地 UDP 端口号 |
| `bExecute` | `BOOL` | — | 上升沿触发一次创建 |
| `tTimeout` | `TIME` | `T#5s` | 创建超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    hSocket   : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在创建 |
| `bError` | `BOOL` | 失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |
| `hSocket` | `T_HSOCKET` | 新建 UDP socket 句柄，仅 `bBusy=FALSE` 且 `bError=FALSE` 时有效 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿创建一次。一个 FB 实例只产生一个 UDP socket。

**状态机**：上升沿 → `bBusy := TRUE`；Server 调 `socket(AF_INET, SOCK_DGRAM) + bind()`；成功 → `bBusy := FALSE`、`bError := FALSE`、`hSocket` 输出；失败 → `bError := TRUE`、`nErrId` 含码。

**`sLocalHost` 解析行为**（PDF §5.1.8 警告）：

1. 空串 + 单网卡：绑到该网卡 IP
2. 空串 + 多网卡 + 默认网卡连网：绑到默认网卡 IP
3. 空串 + 默认网卡断网 + 备用网卡在线：绑到备用网卡 IP（**行为变化**）
4. 空串 + PC 完全断网：绑到 `127.0.0.1`（回环，外部完全不可见）
5. 显式 `'0.0.0.0'`：监听所有网卡（推荐用法）
6. 显式具体 IP：绑到该网卡，找不到则报 `WSAEADDRNOTAVAIL`

为避免（3）（4）的不可预测行为，**生产环境强烈建议显式填 `'0.0.0.0'` 或具体网卡 IP**。或者创建完后检查 `hSocket.localAddr.sAddr` 看实际绑到哪儿，不符合预期就关闭重建。

**与 TCP 的差异**：UDP socket 同时支持收和发，且 send 不会建立"对端 IP+Port"关系——每次 `FB_SocketUdpSendTo` 都指定目标。一个 UDP socket 可同时被一个 SendTo + 一个 ReceiveFrom 配对使用。

**典型陷阱**：`nLocalPort := 0` 在 PDF 没明确说，但 Berkeley 语义是"OS 自动分配端口"——服务器场景下应该明确指定端口；客户端纯发送可填 0。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008001` | `TCPADSERROR_NOMOREENTRIES` | Server socket 槽位已满 |
| `0x80072740` | `WSAEADDRINUSE` (10048) | 端口被占 |
| `0x80072741` | `WSAEADDRNOTAVAIL` (10049) | 指定 IP 在本机不存在 |
| ADS `6/7/1861` | — | 同常规 socket FB |

## 5. 使用注意 / 常见坑

- **生产环境显式 `'0.0.0.0'`**：避免上述（3）（4）行为陷阱。
- **缓冲区上限默认 8192 字节**：UDP 单包最大 `TCPADS_MAXUDP_BUFFSIZE = 16#2000` (8192)。如要支持更大需在 TwinCAT 3 PLC 参数列表里改这个全局常量（PDF §5.4.2）。但注意：以太网 MTU 通常 1500，超过 1472 的 UDP payload 会触发 IP 分片，跨网段传输容易丢包。
- **`hSocket` 不能用 FB_SocketSend / FB_SocketReceive** ：UDP 句柄必须用 `FB_SocketUdpSendTo` / `FB_SocketUdpReceiveFrom`，类型 token 在 Server 端不同。
- **关闭仍用 `FB_SocketClose`**：UDP 和 TCP 共用同一个 Close FB。
- **多播加入**：要收多播包，还要在 Create 之后调一次 `FB_SocketUdpAddMulticastAddress`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketUdpCreate.xml`](../examples/P_Demo_FB_SocketUdpCreate.xml)

```iecst
// 场景：在 0.0.0.0:5005 绑一个 UDP socket 用作设备发现的接收端。
PROGRAM P_Demo_FB_SocketUdpCreate
VAR
    fbCreateDiscoverySocket : FB_SocketUdpCreate;
    bRequestCreate          : BOOL;
    bCreateBusy             : BOOL;
    bCreateError            : BOOL;
    nCreateErrId            : UDINT;
    hDiscoverySocket        : T_HSOCKET;
END_VAR

fbCreateDiscoverySocket(
    sSrvNetId  := '',
    sLocalHost := '0.0.0.0',
    nLocalPort := 5005,
    bExecute   := bRequestCreate,
    tTimeout   := T#5S,
    bBusy      => bCreateBusy,
    bError     => bCreateError,
    nErrId     => nCreateErrId,
    hSocket    => hDiscoverySocket
);
```

## 7. 业务场景与实际价值

- **场景**：设备发现广播 / 多播（如 PLC 在网段内"喊一嗓子"等所有 HMI 回应）、低延迟周期数据（实时控制信号无连接握手开销）、组播录像 / 监控流。**注意**：PLC ↔ TwinCAT 之间走 ADS 即可，无需 UDP。
- **价值**：把 UDP socket 创建 + 端口绑定 + ADS 异步状态机一套封装。
- **替代方案对比**：
  - TCP：可靠但延迟 + 握手成本高，不适合广播
  - EtherCAT：内网实时但不能跨网段
  - 用本 FB + UdpSendTo / UdpReceiveFrom：标准 UDP 协议，跨网段、与第三方互通

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84152203.html
- **相关**：`FB_SocketUdpSendTo` / `FB_SocketUdpReceiveFrom`（必须配对）、`FB_SocketUdpAddMulticastAddress`（加入多播组）、`FB_SocketClose`、`FB_ConnectionlessSocket`（helper 封装版）
