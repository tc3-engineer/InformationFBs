# FB_SocketAccept

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84147595.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketAccept.xml`](../examples/P_Demo_FB_SocketAccept.xml) |

---

## 1. 功能简述

TCP/IP 接受连入功能块：从指定 listener（来自 `FB_SocketListen`）取出一个待处理的 incoming 连接，返回新建立的远端客户端连接句柄 `hSocket`。本 FB 是 PLC 服务器实现的核心：**周期性 polling**——每个 PLC 周期给 `bExecute` 上升沿，若 listener 队列有连接请求则 `bAccepted := TRUE` 并返回新句柄，若队列为空则无错误地返回（`bAccepted = FALSE`）。每条新 incoming 连接只能被 Accept 一次；建议把所有 Accept 出来的句柄存到数组里集中管理，连接断开时移除。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId     : T_AmsNetId := '';
    hListener     : T_HSOCKET;
    bExecute      : BOOL;
    tTimeout      : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server 的 AMS NetID。本机用空串 |
| `hListener` | `T_HSOCKET` | — | listener 句柄，由 `FB_SocketListen` 提供 |
| `bExecute` | `BOOL` | — | 上升沿触发一次 polling。建议每 5 秒一脉冲；轻负载下也可每周期 |
| `tTimeout` | `TIME` | `T#5s` | 单次 polling 操作的超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bAccepted : BOOL;
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    hSocket   : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bAccepted` | `BOOL` | 本次 polling 成功接受一条新连接时为 `TRUE`，否则 `FALSE`（队列为空也算成功，但 `bAccepted=FALSE`） |
| `bBusy` | `BOOL` | 正在执行 polling |
| `bError` | `BOOL` | 失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |
| `hSocket` | `T_HSOCKET` | 新接受的远端客户端句柄，仅 `bAccepted=TRUE` 时有效 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿触发一次"取队列"。Listener 内部有 incoming 连接请求队列（OS backlog），本 FB 一次取一个。

**状态机**：

1. 上升沿 → `bBusy := TRUE`
2. Server 检查 listener 队列：
   - 队列非空 → 取一个，握手完成 → `bAccepted := TRUE`、`hSocket` 输出新句柄
   - 队列为空 → `bAccepted := FALSE`、`hSocket` 内容不可用、**不报错**
   - 出错 → `bError := TRUE`、`nErrId` 含码
3. `bBusy := FALSE`

**周期 polling 模式**：服务器要持续接受连接，所以本 FB 必须周期性上升沿。常见做法：

```iecst
fbTriggerAccept(IN := TRUE, PT := T#5S);    // TON 自动取反触发
IF NOT fbTriggerAccept.Q AND fbLastAccept.Q THEN  // 边沿检测
    bPollNow := TRUE;
END_IF
```

或用 R_TRIG + 计时器。

**多客户端处理**：来 3 个客户端就需要 3 次 Accept 上升沿，本 FB 一次只取队列里的一个 incoming。推荐把 Accept 出来的句柄塞进数组 `aClients : ARRAY[1..MAX] OF T_HSOCKET`，每个槽位维护独立状态机；每个客户端都需要自己的一对 `FB_SocketReceive` / `FB_SocketSend` 实例（不能共享，因为 Send/Receive 内部各自维护 ADS 异步状态）。这种"listener + 一组 client slot"的结构是 PDF §5.1.20.2 `FB_ServerClientConnection` 封装的内部模型。

**典型陷阱**：把 `bExecute` 接电平 `TRUE` 持续不会持续 polling，只首次上升沿生效一次；要周期接受必须周期生成上升沿（TON 自反馈 + 边沿检测最常用）。`bAccepted = FALSE` 时不要读 `hSocket`，因为该字段未被 FB 写入新值，会拿到旧句柄或全 0 结构，后续 Send/Receive 走幽灵句柄报 `NOTFOUND`。一个 listener 同时接多个客户端却只共用一对 Send/Receive 实例，会导致两客户端流量交叉错乱，必须为每个 client slot 单独实例化收发对。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | listener 句柄无效或已关 |
| `0x00008005` | `TCPADSERROR_NOTLISTENING` | listener 内部错误 |
| `0x80072747` | `WSAENETDOWN` | 网络层挂 |
| ADS 6 / 7 / 1861 | — | 同常规 socket FB |

## 5. 使用注意 / 常见坑

- **`bAccepted` 必须先查再用 `hSocket`**：只有 `bAccepted=TRUE` 那一个 PLC 周期内 `hSocket` 才是新句柄。
- **句柄列表的维护**：建立数组 + 状态机（slot 空/已 accept/通信中/待关闭），accept 成功就找空 slot 填入；客户端断开时把 slot 标空并 `FB_SocketClose`。
- **backlog 满**：OS listen backlog 默认通常 SOMAXCONN = 128。如果 Accept polling 间隔太长，第 129 个客户端会被 OS 直接拒绝。
- **PLC 周期太长**：1 秒以上的 PLC 周期不适合做高频 Accept——HMI 连接可接受，但工业相机这类频繁短连不要这样配。
- **同一 incoming 不能被 Accept 两次**：成功 Accept 后 listener 队列就移除该项；想"复用"必须先 Close 这个客户端句柄并等其重新连。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketAccept.xml`](../examples/P_Demo_FB_SocketAccept.xml)

```iecst
// 场景：把 incoming 连接放入一个简单的客户端槽位数组里。
PROGRAM P_Demo_FB_SocketAccept
VAR
    fbAcceptIncoming : FB_SocketAccept;
    hPlcListener     : T_HSOCKET;            // 由 FB_SocketListen 提供
    bPollAccept      : BOOL;                 // 每周期上升沿
    bAcceptBusy      : BOOL;
    bClientAccepted  : BOOL;
    bAcceptError     : BOOL;
    nAcceptErrId     : UDINT;
    hRemoteClient    : T_HSOCKET;
END_VAR

fbAcceptIncoming(
    sSrvNetId := '',
    hListener := hPlcListener,
    bExecute  := bPollAccept,
    tTimeout  := T#5S,
    bAccepted => bClientAccepted,
    bBusy     => bAcceptBusy,
    bError    => bAcceptError,
    nErrId    => nAcceptErrId,
    hSocket   => hRemoteClient
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 当 TCP 服务器接 HMI / SCADA / 工业相机 / PC 上位机。每接一个新连接就为它分配一对 Send/Receive 实例。
- **价值**：把 OS 级 `accept()` 封装成 ADS 异步状态机，PLC 不阻塞、polling 模型清晰。
- **替代方案对比**：
  - `FB_ServerClientConnection`（PDF §5.1.20.2）：自动管理 listener + accept + close 三件事，业务侧只设 `bEnable`。简单场景推荐 helper
  - 用本 FB：需要细粒度控制（如自定义并发上限、按 IP 黑名单拒绝），但要自己维护句柄数组

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84147595.html
- **相关**：`FB_SocketListen`（必须配对）、`FB_SocketClose`、`FB_SocketSend` / `FB_SocketReceive`、`FB_ServerClientConnection`
