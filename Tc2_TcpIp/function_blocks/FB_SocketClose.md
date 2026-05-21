# FB_SocketClose

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84142987.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketClose.xml`](../examples/P_Demo_FB_SocketClose.xml) |

---

## 1. 功能简述

通用 socket 关闭功能块：把一个之前由 `FB_SocketConnect`（本地客户端）、`FB_SocketAccept`（远端客户端）、`FB_SocketListen`（监听）或 `FB_SocketUdpCreate`（UDP）打开的句柄关闭。无论 TCP 还是 UDP，都用这一个 FB；它通过句柄内部信息自动识别 socket 类型。每个成功打开的 socket **必须** 配一次 `FB_SocketClose`，否则句柄会在 TwinCAT TCP/IP Connection Server 中残留，导致下次 PLC Reset 或 Download 后旧句柄无法清理（这种情况下需要在 PLC 启动用 `FB_SocketCloseAll` 兜底）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId   : T_AmsNetId := '';
    hSocket     : T_HSOCKET;
    bExecute    : BOOL;
    tTimeout    : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TwinCAT TCP/IP Connection Server 的 AMS NetID。本机用默认空串 |
| `hSocket` | `T_HSOCKET` | — | 要关闭的 socket 句柄。可以是 TCP 监听 / 远端客户端 / 本地客户端 / UDP 任一种 |
| `bExecute` | `BOOL` | — | 上升沿触发一次关闭 |
| `tTimeout` | `TIME` | `T#5s` | 单次关闭允许的最长时间。关闭通常 < 1 秒，5 秒是安全余量 |

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
| `bBusy` | `BOOL` | 正在执行关闭。`FALSE` = 完成（成功或失败） |
| `bError` | `BOOL` | `bBusy` 落回时若发生错误置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号；详细分段见 §4 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿触发一次关闭，电平不重复。

**单次关闭流程**：

1. 上升沿 → `bBusy := TRUE`，FB 通过 ADS 让 Server 执行 `closesocket()`
2. 关闭完成 → `bBusy := FALSE`、`bError := FALSE`：句柄从 Server 表中删除，对应 TCP 连接进入 FIN/TIME_WAIT；UDP 直接销毁
3. 关闭失败 → `bBusy := FALSE`、`bError := TRUE`、`nErrId` 含错误码（最常见是 `TCPADSERROR_NOTFOUND` = 句柄已无效或被关过）

**重复关闭**：对同一 `hSocket` 调用两次 `FB_SocketClose`，第二次会报 `0x00008002` (`TCPADSERROR_NOTFOUND`)。这是 Beckhoff Server 的设计，不是 bug：每次成功关闭后请把上层状态机里的"socket 有效"标记清零，避免误重关。

**TCP vs UDP 行为差异**：

- TCP 监听 socket（来自 `FB_SocketListen`）：关闭后不再接受新连接，但已 `Accept` 出来的子连接句柄仍然有效，必须各自单独关
- TCP 客户端 socket（来自 `FB_Connect` 或 `Accept`）：关闭即发 FIN，进入 TCP 关闭握手
- UDP socket（来自 `FB_SocketUdpCreate`）：关闭即释放本地端口绑定

**典型陷阱**：

- 忘记关 Accept 出来的远端客户端句柄——只关监听 socket 不会自动关已建立的子连接
- 在 `bBusy=TRUE` 期间又给 `bExecute` 上升沿——FB 会忽略该次触发
- 用错的 NetID 调用——`nErrId` 会报"找不到"，但本地 PLC 程序无法判断是 NetID 错还是句柄错，建议日志记录 NetID

## 4. 错误码 / 返回值

按 `nErrId` 范围分段（PDF §7.3.1）：`0–30720` 为 ADS / TwinCAT 系统错误，`32768–33023` 为 Server 内部错误，`0x80070000–0x8007FFFF` 为 Win32 / Winsock。

`FB_SocketClose` 主要可能返回的 Server 内部错误（PDF §7.3.2）：

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | 句柄无效（典型场景：重复关闭、句柄从未存在、用错了 Server NetID） |

ADS 类常见：

| `nErrId` (dec) | 含义 |
|---|---|
| `6` | Target port not found — Server 没在跑 |
| `7` | Target machine not found — NetID 写错 |
| `1861` | ADS timeout — Server 卡死 |

## 5. 使用注意 / 常见坑

- **关闭后立刻清空本地缓存的 `hSocket`**：成功 `bBusy=FALSE` 且 `bError=FALSE` 之后，把上层引用此句柄的所有 FB 实例的 `hSocket` 清零或在状态机里置位"已关闭"，否则下次错用同一句柄会失败。
- **监听 socket 关闭不会自动关子连接**：开发者必须维护一张"`Accept` 出来的句柄"列表，遍历逐一关。
- **`FB_SocketClose` 不能跨 PLC 重启工作**：重启后 PLC 不再持有 `hSocket`，必须靠 `FB_SocketCloseAll`。
- **`tTimeout` 不建议低于 1 秒**：极端拥塞场景 `closesocket` 也可能慢，过短超时会让上层误以为关闭失败而再关一次，触发 `NOTFOUND`。
- **优雅关闭 vs 强制关闭**：PDF 未区分 graceful / abortive close 接口；本 FB 走默认 `closesocket()`，TCP 会发 FIN 走优雅关闭。如果对端没响应 FIN，操作系统会保持 TIME_WAIT 一段时间（典型 60 秒），期间同 IP:port 不能立刻被新建连复用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketClose.xml`](../examples/P_Demo_FB_SocketClose.xml)

```iecst
// 场景：已有一条由 FB_SocketConnect 建立的 hClientSocket，业务流程结束需要释放它。
PROGRAM P_Demo_FB_SocketClose
VAR
    fbCloseClientSocket : FB_SocketClose;
    hClientSocket       : T_HSOCKET;          // 由上游建连得到的句柄
    bRequestClose       : BOOL;               // 上升沿触发关闭
    bClosing            : BOOL;
    bCloseFailed        : BOOL;
    nCloseErrId         : UDINT;
END_VAR

fbCloseClientSocket(
    sSrvNetId := '',
    hSocket   := hClientSocket,
    bExecute  := bRequestClose,
    tTimeout  := T#5S,
    bBusy     => bClosing,
    bError    => bCloseFailed,
    nErrId    => nCloseErrId
);
```

## 7. 业务场景与实际价值

- **场景**：TCP 客户端业务结束（如 MES 查询完毕）、TCP 监听服务下线、UDP 信令切换网卡前释放旧 socket。任何 socket 资源回收路径必经此 FB。
- **价值**：把"通过 ADS 调用 Connection Server 关闭 socket + 处理错误"一行调用搞定。封装了 ADS 异步状态机；业务代码不用关心 `WSACleanup`、`shutdown` 这些底层细节。
- **替代方案对比**：
  - 不调本 FB，靠 OS 在 PLC 退出时自动清理——错。PLC Reset / Download 时 PLC 程序没机会清，Server 端仍持有句柄，必须靠 `FB_SocketCloseAll` 兜底；正常运行期更要主动关，避免句柄上限耗尽
  - 使用 `FB_ClientServerConnection` / `FB_ServerClientConnection` helper：内部已封装好"`bEnable := FALSE` 时自动关"，业务上更省心，但灵活性差一点

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84142987.html
- **相关**：`FB_SocketConnect` / `FB_SocketListen` / `FB_SocketAccept` / `FB_SocketUdpCreate`（开句柄的四个 FB）、`FB_SocketCloseAll`（启动期兜底）、`T_HSOCKET`、`E_WinsockError`
