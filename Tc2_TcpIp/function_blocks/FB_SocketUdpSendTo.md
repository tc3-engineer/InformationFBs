# FB_SocketUdpSendTo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84153739.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketUdpSendTo.TcPOU`](../examples/P_Demo_FB_SocketUdpSendTo.TcPOU) |

---

## 1. 功能简述

UDP 数据包发送功能块：从已创建的 UDP socket（来自 `FB_SocketUdpCreate`）向任意远端 IP + Port 发送一个 UDP 数据报。`bExecute` 上升沿触发一次发送，FB 内部走 ADS 异步。UDP 是无连接的，因此每次发送都要带目标 `sRemoteHost` + `nRemotePort`——同一 socket 可以发给不同对端。单次发送字节上限受 `TCPADS_MAXUDP_BUFFSIZE` 限制，默认 8192 字节（PDF §5.4.2）。**注意**：超过 1472 字节的 UDP payload 会触发 IP 分片，跨网段传输容易丢包，建议每包 ≤ 1400 字节。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId   : T_AmsNetId := '';
    hSocket     : T_HSOCKET;
    sRemoteHost : T_IPv4Addr;
    nRemotePort : UDINT;
    cbLen       : UDINT;
    pSrc        : POINTER TO BYTE;
    bExecute    : BOOL;
    tTimeout    : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 由 `FB_SocketUdpCreate` 创建的 UDP socket 句柄 |
| `sRemoteHost` | `T_IPv4Addr` | — | 远端目标 IPv4 字符串（例 `'172.33.5.1'`）。本机回环可用空串。**广播用 `'255.255.255.255'` 或子网广播如 `'192.168.1.255'`；多播用 224.0.0.0–239.255.255.255 范围内的 IP** |
| `nRemotePort` | `UDINT` | — | 远端目标端口号 |
| `cbLen` | `UDINT` | — | 要发送的字节数。最大 `TCPADS_MAXUDP_BUFFSIZE` = 8192 字节 |
| `pSrc` | `POINTER TO BYTE` | — | 发送缓冲区起始地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次发送 |
| `tTimeout` | `TIME` | `T#5s` | 单次发送 ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在发送 |
| `bError` | `BOOL` | 发送失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次发送。UDP 是 fire-and-forget：socket 把数据报交给网卡就返回 `bError := FALSE`，**不保证对端收到**——和 TCP 不同。

**单次发送状态机**：上升沿 → `bBusy := TRUE`；Server 调 `sendto()` 把数据报交给 OS；OS 立刻返回 → `bBusy := FALSE`、`bError := FALSE`（典型 < 1 ms）。和 TCP 的关键差异：**UDP 没有 ACK，本 FB 永远不会因"对端不响应"超时**。失败只发生在 OS 层（如本地路由表没有去往目标的路径、广播被网卡禁用、`cbLen` 超过 buffer 上限等）。

**广播发送**：要发广播包，需要事先在 socket 上开启 `SO_BROADCAST`——但 PDF 没暴露 setsockopt 接口；实际测试 TwinCAT TCP/IP Connection Server 创建的 UDP socket 默认就允许广播（**工程经验补充**：可发 `'255.255.255.255'` 或子网广播，对端用同 socket 的 `FB_SocketUdpReceiveFrom` 可收）。

**多播发送**：直接把 `sRemoteHost` 设成 224–239.x.x.x，OS 会按多播路由表发出去。**发送方不需要 `FB_SocketUdpAddMulticastAddress`**——加入多播组只在"接收"那一端是必须的。

**字节数限制**：`cbLen > 8192` 会被 Connection Server 截断或报错。一定要在调用前检查 `cbLen`。

**典型陷阱**：用 `LEN(s)` 当 `cbLen` 漏算 `$00` 终止符（同 TCP `FB_SocketSend`）。把 `tTimeout := T#1ms` 想"提高发包速率"——FB 不会阻塞，5 秒只是 ADS 故障兜底，不影响吞吐率。在 `bBusy=TRUE` 期间修改 `pSrc` 内容会让对端收到混合数据。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 / 已关闭 |
| `0x80072751` | `WSAEHOSTUNREACH` (10065) | 目的 IP 路由不可达 |
| `0x80072747` | `WSAENETDOWN` (10050) | 本机网卡未启用 |
| `0x80072738` | `WSAEMSGSIZE` (10040) | `cbLen` 超过 UDP 数据报上限（一般 65507 字节是理论上限，本库限 8192） |
| ADS `6/7/1861` | — | 路由 / 系统级错误 |

## 5. 使用注意 / 常见坑

- **跨网段 MTU**：单包 ≤ 1400 字节最稳；超过会 IP 分片，丢包率上升。
- **`cbLen` 一次最多 8192**：要改这个上限需在 PLC 库参数列表里改 `TCPADS_MAXUDP_BUFFSIZE`。但跨网段不要超 MTU。
- **没有 ACK 不等于不能写"可靠 UDP"**：业务层可以加序号 + 重发，但要自己实现。
- **广播包的网卡选择**：依赖创建 socket 时的 `sLocalHost`。`'0.0.0.0'` 会从默认网卡发出，不一定是你想要的网段；需要指定具体网卡 IP 时务必显式 `sLocalHost`。
- **多播 TTL**：默认通常 1，只在本地子网传播。跨路由需要 OS 层提高 TTL，但 PDF 未暴露 setsockopt——跨子网多播需用其他途径。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketUdpSendTo.TcPOU`](../examples/P_Demo_FB_SocketUdpSendTo.TcPOU)

```iecst
// 场景：UDP socket 已建好，向广播地址 192.168.1.255:5005 发设备发现 hello。
PROGRAM P_Demo_FB_SocketUdpSendTo
VAR
    fbBroadcastHello : FB_SocketUdpSendTo;
    hUdpSocket       : T_HSOCKET;
    sPayload         : STRING(64) := 'HELLO,PLC_DISCOVER,V1';
    bSendNow         : BOOL;
    bSendBusy        : BOOL;
    bSendError       : BOOL;
    nSendErrId       : UDINT;
END_VAR

fbBroadcastHello(
    sSrvNetId   := '',
    hSocket     := hUdpSocket,
    sRemoteHost := '192.168.1.255',
    nRemotePort := 5005,
    cbLen       := TO_UDINT(LEN(sPayload) + 1),
    pSrc        := ADR(sPayload),
    bExecute    := bSendNow,
    tTimeout    := T#5S,
    bBusy       => bSendBusy,
    bError      => bSendError,
    nErrId      => nSendErrId
);
```

## 7. 业务场景与实际价值

- **场景**：设备发现广播（PLC 喊一声让网段内所有 HMI/PC 回应）、低延迟周期信号（如 1ms 实时控制流，不用握手）、组播视频流 / 监控录像、Syslog 上报。
- **价值**：把 OS 级 `sendto()` 异步封装；UDP 一次调用即可，不需要 Connect / Accept 三段式。
- **替代方案对比**：
  - `FB_SocketSend`（TCP）：可靠送达但有连接开销、不能广播
  - EtherCAT 总线：实时高但仅同段
  - 用本 FB：协议级标准 UDP，跨网段、能广播 / 多播、低延迟

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84153739.html
- **相关**：`FB_SocketUdpCreate`（提供 socket）、`FB_SocketUdpReceiveFrom`（配对收）、`FB_SocketUdpAddMulticastAddress`（多播收方需用）、`FB_SocketClose`
