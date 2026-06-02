# FB_SocketSend

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84149131.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketSend.TcPOU`](../examples/P_Demo_FB_SocketSend.TcPOU) |

---

## 1. 功能简述

TCP/IP 数据发送功能块：把 `pSrc` 指向的内存缓冲区里 `cbLen` 字节通过指定 socket 句柄发送给对端。句柄可以是 `FB_SocketConnect` 出来的客户端连接，也可以是 `FB_SocketAccept` 出来的远端客户端连接。`bExecute` 上升沿触发一次发送；FB 内部走 ADS 异步模式，`bBusy=TRUE` 期间不要修改 `pSrc` 指向的缓冲区。发送成功后 `bError=FALSE`；若对端缓冲区已满 / 网络拥塞，FB 会等到 `tTimeout` 后报 ADS timeout 1861，此时应增大 `tTimeout`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId  : T_AmsNetId := '';
    hSocket    : T_HSOCKET;
    cbLen      : UDINT;
    pSrc       : POINTER TO BYTE;
    bExecute   : BOOL;
    tTimeout   : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server 的 AMS NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 已建立连接的句柄（Connect 或 Accept 出来的） |
| `cbLen` | `UDINT` | — | 要发送的字节数 |
| `pSrc` | `POINTER TO BYTE` | — | 发送缓冲区起始地址（用 `ADR(变量)` 取） |
| `bExecute` | `BOOL` | — | 上升沿触发一次发送 |
| `tTimeout` | `TIME` | `T#5s` | 单次发送超时。**对端处理慢或大数据量时务必加大**（否则报 1861） |

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

无（缓冲区通过 `pSrc` 指针传入，不是 VAR_IN_OUT）。

## 3. 行为说明

**触发**：`bExecute` 上升沿触发一次"把 `pSrc[0..cbLen-1]` 这段字节交给 Server 发"操作。FB 不持有缓冲区拷贝，因此 `bBusy=TRUE` 期间外部修改 `pSrc` 内容会造成对端收到一半旧一半新的混合数据——这是用指针的代价。

**单次发送状态机**：上升沿进入 `bBusy := TRUE`；Server 通过 OS `send()` 把字节推入 TCP 发送窗口；底层 ACK 完成后 `bBusy := FALSE`、`bError := FALSE`。发送窗口已满（对端 receive 缓冲满）时 Server 会阻塞重试直到 `tTimeout` 计时到，然后返回 `bError := TRUE`、`nErrId := 1861`（ADS timeout，**注意这里不是 Winsock 10060**，而是 ADS 层 timeout）。PDF 明确：发送大块数据或对端慢时必须把 `tTimeout` 增大。

**字节流语义**：TCP 是流，本 FB 把 `cbLen` 字节全部发完才算 `bError=FALSE`，不存在"只发了一半"的成功返回。FB 内部已处理 OS `send()` 可能的部分写入；上层不需要写循环。

**典型用法**：发送固定长度二进制报文（如自定义协议头 8 字节 + 载荷 N 字节）一次调用即可。发送以 `\0` 或 `\r\n` 终止的字符串协议时，记得把终止符也算进 `cbLen`，对端用 `FB_SocketReceive` 才能正确判断结束。

**典型陷阱**：用 `LEN(s)` 当 `cbLen` 漏算 `\0`（IEC `STRING` 是 C 风格 null-terminated，`LEN` 不含 `\0`，若对端按 null 判结尾必须 `cbLen := TO_UDINT(LEN(s) + 1)`）。`bBusy=TRUE` 时改 `pSrc` 缓冲区会造成对端收到错位数据。多个 `FB_SocketSend` 实例并发往同一 `hSocket` 发送，TCP 字节流会交叉错乱——同一 socket 应当用同一个 Send 实例。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | 句柄无效（被关 / 从未存在 / 对端断开后句柄失效） |
| `0x00008004` | `TCPADSERROR_NOTCONNECTED` | 连接已断（对端 RST 或 FIN） |
| ADS `1861` | — | tTimeout 太短或对端不接收（**ADS timeout，非 Winsock 10060**） |
| `0x80072746` | `WSAECONNRESET` (10054) | 对端强制关闭连接 |
| `0x8007274A` | `WSAESHUTDOWN` (10058) | 该方向已 shutdown |

## 5. 使用注意 / 常见坑

- **`tTimeout` 设置**：默认 `T#5s` 适合小报文（< 1 KB）。发送 100 KB 以上或低速链路必须设 `T#30s` 以上，否则频繁假超时。
- **缓冲区生命期**：`pSrc` 指向的变量必须在 `bBusy=TRUE` 整个期间保持不变。最简单的做法是把发送缓冲区做成全局或局部 `STRING` / `ARRAY`，发送期间不让 PLC 别的逻辑改它。
- **错误后清理**：`bError=TRUE` + `NOTCONNECTED` 或 `CONNRESET` 时，对端连接已死，本 FB 不能恢复——上层必须关闭句柄并重新 Connect。
- **不能保证"发完就到"**：TCP 字节流送达对端 receive buffer 即算成功，**不代表对端应用层已读**；要确认应用层消息送达，必须自定义应用层 ACK 协议。
- **`cbLen := 0` 调用**：FB 允许，但发送 0 字节在 TCP 上是无意义的 no-op；建议上层先判断 `IF cbLen > 0 THEN`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketSend.TcPOU`](../examples/P_Demo_FB_SocketSend.TcPOU)

```iecst
// 场景：连接已建立（hRemote），现在向对端发一段固定字符串。
PROGRAM P_Demo_FB_SocketSend
VAR
    fbSendOrderResp : FB_SocketSend;
    hRemote         : T_HSOCKET;            // 由上游 Connect/Accept 提供
    sResponse       : STRING(128) := 'OK,ORDER_ACCEPTED$N';
    bSendNow        : BOOL;
    bSendBusy       : BOOL;
    bSendError      : BOOL;
    nSendErrId      : UDINT;
END_VAR

fbSendOrderResp(
    sSrvNetId := '',
    hSocket   := hRemote,
    cbLen     := TO_UDINT(LEN(sResponse) + 1),   // +1 算 $00 终止符
    pSrc      := ADR(sResponse),
    bExecute  := bSendNow,
    tTimeout  := T#5S,
    bBusy     => bSendBusy,
    bError    => bSendError,
    nErrId    => nSendErrId
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 给 MES 回送报工确认、给 SCADA 推送报警、给打印机喂 ZPL 标签、给扫码枪发触发指令。所有"PLC → 对端"的字节流业务必经此 FB。
- **价值**：把 ADS 异步 `send()` 状态机封装为 6 输入 3 输出。业务侧不用关心 OS `send()` 的部分写入、不用关心 ADS 异步推进。
- **替代方案对比**：
  - `FB_ClientServerConnection` 提供更高层的 helper，但底层数据收发仍要 `FB_SocketSend` / `FB_SocketReceive`
  - 用 ADS：仅 TwinCAT ↔ TwinCAT
  - OPC UA：协议重，需对端支持

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84149131.html
- **相关**：`FB_SocketReceive`（配对收数据）、`FB_SocketConnect` / `FB_SocketAccept`（提供 `hSocket`）、`FB_SocketUdpSendTo`（UDP 版）、`E_WinsockError`
