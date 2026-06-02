# FB_SocketReceive

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84150667.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketReceive.TcPOU`](../examples/P_Demo_FB_SocketReceive.TcPOU) |

---

## 1. 功能简述

TCP/IP 数据接收功能块：从指定 socket 句柄读取已到达的字节，写入 `pDest` 指向的接收缓冲区。**必须周期性 polling**：因为 TCP 是流，数据可能分多片到达，单次调用不一定取完；上层要循环调用直到拿到约定的报文终止符（如 `\0`、`\r\n` 或自定义长度头里写的字节数）。`nRecBytes` 输出本次实际收到的字节数；为 0 表示当前没新数据（不算错误）。本 FB 不实现协议解析——拿到字节后业务自己拼包。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId  : T_AmsNetId := '';
    hSocket    : T_HSOCKET;
    cbLen      : UDINT;
    pDest      : POINTER TO BYTE;
    bExecute   : BOOL;
    tTimeout   : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 已建立连接的句柄（Connect 或 Accept 出来） |
| `cbLen` | `UDINT` | — | 接收缓冲区可写入的最大字节数。FB 不会写超过此值，多余的数据留在 TCP 接收队列等下次 |
| `pDest` | `POINTER TO BYTE` | — | 接收缓冲区起始地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次 polling（典型每 100 ms） |
| `tTimeout` | `TIME` | `T#5s` | 单次 polling 操作的 ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    nRecBytes : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在 polling |
| `bError` | `BOOL` | 失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |
| `nRecBytes` | `UDINT` | 本次实际写入 `pDest` 的字节数。`0` 表示无新数据，不算错误 |

### VAR_IN_OUT

无（缓冲区通过指针传入）。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次 polling；电平不持续 polling。典型部署是用 TON 每 100 ms / 1 s 生成脉冲驱动。

**单次 polling 状态机**：上升沿 → `bBusy := TRUE`；Server 调 OS `recv()`：如果接收缓冲有数据，复制最多 `cbLen` 字节到 `pDest`，`nRecBytes` 记实际字节数；如果接收缓冲空，立即返回 `nRecBytes := 0`、`bError := FALSE`（**注意：没数据不是错误**）。`bBusy := FALSE`。

**字节流语义重要点**：TCP 不保留消息边界。发送方 send 一次 100 字节，接收方可能 receive 到 `[40, 60]` 两段、`[100]` 一段、或 `[20, 30, 50]` 三段——具体由网络条件决定。因此**应用层必须自定义分帧**（PDF §5.1.7 明确）。常见三种方案：
1. **定长报文**：每个报文恰好 N 字节。Receive 后累计计数，凑够 N 字节就处理一帧
2. **分隔符**：例如 `\r\n` / `\0` 结束。每次 Receive 把新字节追加进暂存区，扫描分隔符切包
3. **长度前缀**：前 2 或 4 字节是后续 payload 字节数。先收头再收体

**对端断开但本机未感知**（PDF 重点警告）：远端机断网时本机 TCP 协议栈不会主动通知，`FB_SocketReceive` 会一直返回 `nRecBytes := 0`、`bError := FALSE`，应用层会"等不到数据"。务必在 PLC 里实现"超时未收到完整帧就主动断"的兜底——例如约定 10 秒未拼出一帧就关闭并重连。

**典型陷阱**：把 "`nRecBytes := 0` 视为错误" 是错的；这是正常无数据情况。把 `pDest` 接收缓冲做小（如 64 字节）会一次取不完上游的大包，下次 polling 才能拿剩下的，吞吐率下降。多个 Receive 实例对同一 `hSocket` 抢读会造成字节乱序——**一条连接对应一个 Receive 实例**。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | 句柄无效 |
| `0x00008004` | `TCPADSERROR_NOTCONNECTED` | 连接已断（远端正常关闭，对端发 FIN） |
| `0x80072746` | `WSAECONNRESET` (10054) | 对端 RST 强制关闭 |
| `0x8007274A` | `WSAESHUTDOWN` (10058) | 该方向已 shutdown |
| ADS `1861` | — | tTimeout 太短或 Server 卡 |

## 5. 使用注意 / 常见坑

- **必须周期 polling**：典型 100 ms 一次。频率太低（如 1 秒）会让对端 TCP 接收窗口积压满进而堵住对端 send。
- **应用层超时**：PDF 明确建议在 PLC 里另设一个超时计时器，比如 10 秒未收齐完整帧就主动关连接 + 重连。本 FB 自己的 `tTimeout` 不能解决"对端死掉但 TCP 未感知"问题。
- **缓冲区大小**：建议 ≥ 一帧最大长度；如果协议帧最大 1500 字节，做 `cbLen := 2048` 以上。
- **`nRecBytes` 用法**：`nRecBytes = 0` → 没数据，继续等；`nRecBytes > 0` → 把 `pDest[0..nRecBytes-1]` 追加进上层暂存区，继续按协议解析。
- **不要假设单次 receive 拿到完整帧**：写应用层时永远按"流式累积 + 扫分隔符 / 凑长度"的模式。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketReceive.TcPOU`](../examples/P_Demo_FB_SocketReceive.TcPOU)

```iecst
// 场景：连接已建立，持续 polling 接收对端发来的字节流，演示按 LF 切包。
PROGRAM P_Demo_FB_SocketReceive
VAR
    fbReceiveFromPeer : FB_SocketReceive;
    hRemote           : T_HSOCKET;
    abRxBuffer        : ARRAY[0..1499] OF BYTE;     // 单次最多 1500 字节
    bPollPulse        : BOOL;                       // 外部 TON 给 100ms 上升沿
    bRxBusy           : BOOL;
    bRxError          : BOOL;
    nRxErrId          : UDINT;
    nRecBytes         : UDINT;
END_VAR

fbReceiveFromPeer(
    sSrvNetId := '',
    hSocket   := hRemote,
    cbLen     := SIZEOF(abRxBuffer),
    pDest     := ADR(abRxBuffer),
    bExecute  := bPollPulse,
    tTimeout  := T#5S,
    bBusy     => bRxBusy,
    bError    => bRxError,
    nErrId    => nRxErrId,
    nRecBytes => nRecBytes
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 接 MES 下发的指令（订单、配方）、接扫码枪上送的条码、接 SCADA 控制命令、接打印机回执。所有"对端 → PLC"的字节流业务必经此 FB。
- **价值**：把 ADS 异步 `recv()` 状态机封装为单次调用；自动处理"没数据不算错误"、缓冲区上限自动截断。
- **替代方案对比**：
  - `FB_ClientServerConnection` / `FB_ServerClientConnection` 仍依赖本 FB 接收数据，只是把连接管理封装了
  - 用 ADS：仅 TwinCAT ↔ TwinCAT
  - 用 OPC UA：协议重，需对端配合

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84150667.html
- **相关**：`FB_SocketSend`（配对）、`FB_SocketConnect` / `FB_SocketAccept`（提供 `hSocket`）、`FB_SocketUdpReceiveFrom`（UDP 版）、`E_WinsockError`
