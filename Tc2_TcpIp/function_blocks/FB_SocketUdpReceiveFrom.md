# FB_SocketUdpReceiveFrom

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84155275.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketUdpReceiveFrom.xml`](../examples/P_Demo_FB_SocketUdpReceiveFrom.xml) |

---

## 1. 功能简述

UDP 数据包接收功能块：从已创建的 UDP socket（来自 `FB_SocketUdpCreate`）取出一个收到的数据报，写入 `pDest` 指向的缓冲区，并同时输出对端 IP 与端口 `sRemoteHost` + `nRemotePort`。**必须周期 polling**——每 100 ms 触发一次上升沿；队列空时 `nRecBytes := 0`、不报错。和 TCP `FB_SocketReceive` 的关键差别：**UDP 保留消息边界**，一次 receive 完整拿到一整个 UDP 包（要么完整要么空），不会拼半个；缓冲区必须 ≥ 单包最大长度（≥ MTU 1500 字节最安全），否则单包数据可能被截断。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId : T_AmsNetId := '';
    hSocket   : T_HSOCKET;
    cbLen     : UDINT; 
    pDest     : POINTER TO BYTE;
    bExecute  : BOOL;
    tTimeout  : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 由 `FB_SocketUdpCreate` 创建的 UDP socket 句柄 |
| `cbLen` | `UDINT` | — | 接收缓冲区最大字节数。**必须 ≥ 期望的单包最大长度**，否则单包会被截断 |
| `pDest` | `POINTER TO BYTE` | — | 接收缓冲区起始地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次 polling |
| `tTimeout` | `TIME` | `T#5s` | 单次 ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrId      : UDINT;
    sRemoteHost : T_IPv4Addr := '';
    nRemotePort : UDINT;
    nRecBytes   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在 polling |
| `bError` | `BOOL` | 失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |
| `sRemoteHost` | `T_IPv4Addr` | 收到该 UDP 包的发送端 IPv4 字符串（仅 `nRecBytes > 0` 时有效） |
| `nRemotePort` | `UDINT` | 收到该 UDP 包的发送端端口（仅 `nRecBytes > 0` 时有效） |
| `nRecBytes` | `UDINT` | 本次实际写入 `pDest` 的字节数；`0` = 无数据，不算错误 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次 polling。用 TON 自激产生 100 ms 周期是典型做法。

**单次 polling 状态机**：上升沿 → `bBusy := TRUE`；Server 调 `recvfrom()`：队列里有数据报就取出一整个写入 `pDest`，同时填 `sRemoteHost` + `nRemotePort`、`nRecBytes := 实际字节数`；队列空就 `nRecBytes := 0`、不报错。`bBusy := FALSE`。

**消息边界保留**：和 TCP 流截然不同——UDP 每次 receive 拿到的就是 sender 当初一次 `sendto` 的完整内容。**绝不会把两个 sendto 拼起来**，也**绝不会把一个 sendto 拆成两次 receive**。但**如果 `cbLen` < 包长，超出部分被丢弃**（不像 TCP 留在队列等下次）。**因此 `cbLen` 必须够大**。

**`sRemoteHost` / `nRemotePort` 用法**：每个包带源地址。**对端是动态变化的**（同一 socket 可能先收到 192.168.1.5 的包，再收到 192.168.1.7 的包），这是 UDP 与 TCP 的根本区别。要回包给同一对端，把这两个字段保存下来，再用 `FB_SocketUdpSendTo` 指定即可。

**典型陷阱**：`cbLen := 64` 这种小缓冲区在 UDP 上是大坑——只要对端发了大于 64 的包，超出部分立刻被丢，无法补救。务必 ≥ 1500。多个 UDP receive 实例对同一 `hSocket` polling 会抢包导致部分丢失——一个 socket 一个 Receive 实例。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x80072747` | `WSAENETDOWN` (10050) | 网卡未启用 |
| ADS `1861` | — | tTimeout 太短或 Server 卡 |

UDP receive 几乎没有逻辑错误——网络丢包不算"错误"。

## 5. 使用注意 / 常见坑

- **`cbLen` 务必 ≥ 1500**：以太网 MTU 是 1500，含 IP/UDP 头共 28 字节，UDP payload 最多 1472。但有些应用层（如视频流）会做 IP 分片发更大，建议 2048 或 4096 字节缓冲。
- **可调全局上限**：PLC 库参数列表 `TCPADS_MAXUDP_BUFFSIZE` 默认 8192；要扩可改，但跨子网不要超 MTU 否则丢包率飙升。
- **轮询周期**：100 ms 平衡延迟和 CPU。要求 < 10 ms 延迟时改 10 ms PLC 任务 + 每周期 polling。
- **`sRemoteHost` 一定要在 `nRecBytes > 0` 时才用**：否则是上一次的旧值。
- **OS 接收队列**：默认通常 64 KB。如果 polling 间隔太长，多个包到达会撑爆队列导致后到的丢——所以 polling 越频繁越好。
- **广播 / 多播包过滤**：本机发的广播包**自己也会收到**（除非 OS 禁了 `IP_MULTICAST_LOOP`）。需要按 `sRemoteHost != 本机 IP` 过滤。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketUdpReceiveFrom.xml`](../examples/P_Demo_FB_SocketUdpReceiveFrom.xml)

```iecst
// 场景：UDP socket 已建好，持续 polling 收发现包并记录对端 IP/Port。
PROGRAM P_Demo_FB_SocketUdpReceiveFrom
VAR
    fbReceiveUdpHello : FB_SocketUdpReceiveFrom;
    hUdpSocket        : T_HSOCKET;
    abRxBuffer        : ARRAY[0..1499] OF BYTE;       // 一整个 MTU
    bPollPulse        : BOOL;
    bRxBusy           : BOOL;
    bRxError          : BOOL;
    nRxErrId          : UDINT;
    sLastSenderHost   : T_IPv4Addr;
    nLastSenderPort   : UDINT;
    nRecBytes         : UDINT;
END_VAR

fbReceiveUdpHello(
    sSrvNetId := '',
    hSocket   := hUdpSocket,
    cbLen     := SIZEOF(abRxBuffer),
    pDest     := ADR(abRxBuffer),
    bExecute  := bPollPulse,
    tTimeout  := T#5S,
    bBusy       => bRxBusy,
    bError      => bRxError,
    nErrId      => nRxErrId,
    sRemoteHost => sLastSenderHost,
    nRemotePort => nLastSenderPort,
    nRecBytes   => nRecBytes
);
```

## 7. 业务场景与实际价值

- **场景**：UDP 收设备发现请求 / 心跳 / 实时控制信号 / SCADA UDP 推送、组播流接收（如视频监控、组播配方下发）、Syslog 收集。
- **价值**：把 OS `recvfrom()` 异步化、自动拿到 source IP/Port；上层完全不用关心底层 socket 状态。
- **替代方案对比**：
  - `FB_SocketReceive`（TCP）：可靠送达但有连接开销且不保留消息边界
  - 用 ADS Notification 替代：仅 TwinCAT ↔ TwinCAT
  - 用本 FB：标准 UDP，跨任何对端，能做广播/多播/单播

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84155275.html
- **相关**：`FB_SocketUdpCreate`（提供 socket）、`FB_SocketUdpSendTo`（配对发）、`FB_SocketUdpAddMulticastAddress`（要收多播包必须先加入组）
