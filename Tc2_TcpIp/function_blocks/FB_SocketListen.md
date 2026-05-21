# FB_SocketListen

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84146059.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketListen.xml`](../examples/P_Demo_FB_SocketListen.xml) |

---

## 1. 功能简述

TCP/IP 监听 socket 创建功能块：本机作为服务器在指定 IP + 端口上监听，等待远端客户端发起连接。`bExecute` 上升沿触发一次"开监听"，成功后 `hListener` 输出 listener 句柄。listener 句柄并不直接收发数据，而是交给 `FB_SocketAccept` 用来接受连入的客户端连接；每次 Accept 出来一个 `T_HSOCKET` 即代表一条新连接。监听本身可以一直开着，关闭时调 `FB_SocketClose`。同一台机器上 listener 的端口号必须唯一。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId   : T_AmsNetId := '';
    sLocalHost  : T_IPv4Addr := '';
    nLocalPort  : UDINT;
    bExecute    : BOOL;
    tTimeout    : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TwinCAT TCP/IP Connection Server 的 AMS NetID。本机用默认空串 |
| `sLocalHost` | `T_IPv4Addr` | `''` | 本机要监听的 IPv4 字符串（例如 `'172.13.15.2'`）。**`'0.0.0.0'` 表示监听所有本地网卡**，空串也按默认网卡解析 |
| `nLocalPort` | `UDINT` | — | 本机监听端口号（例如 `200`、`9100`、`2404` 等） |
| `bExecute` | `BOOL` | — | 上升沿触发一次"开监听" |
| `tTimeout` | `TIME` | `T#5s` | 单次开监听操作允许的最长时间 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy      : BOOL;
    bError     : BOOL;
    nErrId     : UDINT;
    hListener  : T_HSOCKET;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 监听 socket 正在创建 |
| `bError` | `BOOL` | 创建失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |
| `hListener` | `T_HSOCKET` | 新创建的 listener 句柄。**仅 `bBusy=FALSE` 且 `bError=FALSE` 时有效**，传递给 `FB_SocketAccept` 用 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿创建一次 listener。listener 创建后会一直存在，直到调 `FB_SocketClose(hListener)`。

**状态机**：

1. 上升沿 → `bBusy := TRUE`，Server 执行 `bind() + listen()`
2. 成功 → `bBusy := FALSE`、`bError := FALSE`、`hListener` 输出
3. 失败 → `bBusy := FALSE`、`bError := TRUE`、`nErrId` 含错误码

**典型部署模板**：用一个 `FB_SocketListen` 创建 listener（整个生命周期只一次），用一个或多个 `FB_SocketAccept` 周期性 polling 接受 incoming 连接；每个被 Accept 出来的客户端句柄分别配一对 `FB_SocketSend` + `FB_SocketReceive`；业务结束时各自 `FB_SocketClose`，最后再关掉 listener。listener 关闭不会自动关闭已 Accept 出来的子连接句柄，必须分别 Close。

**端口冲突**：同一台机器 listener 端口必须唯一。重复在同一 IP + Port 上开 listener 会返回 `0x00008003`（`TCPADSERROR_ALREADYEXISTS`）。在不同 IP 上同端口（如 `'0.0.0.0'` 与 `'172.13.15.2'` 同时绑定 200 端口）也会冲突，因为 `'0.0.0.0'` 等于"占用所有网卡的该端口"。

**典型陷阱**：把 `bExecute` 接到电平 `TRUE` 持续不会反复开 listener——只有首次上升沿生效。若希望 listener 异常关闭后自动重开，需要外部状态机检测 `bError = TRUE` 后把 `bExecute` 复位再触发。`sLocalHost := ''` 在多网卡机器上行为依赖默认网卡，开发期建议显式填 `'0.0.0.0'`（监听全部网卡）或具体网卡 IP。Windows 上常见的 80、443、502 等端口可能被其他服务占用，`bind()` 会失败并报 `WSAEADDRINUSE`。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008001` | `TCPADSERROR_NOMOREENTRIES` | Server 已无 socket 槽位 |
| `0x00008003` | `TCPADSERROR_ALREADYEXISTS` | 同端口 listener 已存在 |
| `0x80072740` | `WSAEADDRINUSE` (10048) | 端口被 OS 上其他进程占用 |
| `0x80072741` | `WSAEADDRNOTAVAIL` (10049) | 给的 IP 在本机不存在（网卡未配置该 IP） |
| `0x80072747` | `WSAENETDOWN` (10050) | 网络层挂了 |

ADS 类 6 / 7 / 1861 同其他 socket FB。

## 5. 使用注意 / 常见坑

- **listener 关掉≠子连接关掉**：listener 关闭只停止 accept 新连接，已 accept 出来的 `T_HSOCKET` 必须各自 `FB_SocketClose`。
- **TIME_WAIT 陷阱**：listener 关闭后立刻重开同端口可能因 OS TIME_WAIT 失败（典型 60 秒）。重启服务时建议显式等待或用不同端口。（工程经验补充）
- **`hListener` 的 `localAddr` 字段会反映实际绑定的 IP + Port**——比 `sLocalHost := ''` 这种隐式情况调试有用。
- **TF6310 Connection Server 处理 incoming 连接前是不会主动通知 PLC 的**——PLC 必须靠 `FB_SocketAccept` 周期 poll；不存在"有连接进来时回调"的机制。
- **Windows / Windows CE 防火墙**：开发期常因防火墙阻挡 listener 端口看不到对端连接。请把目标端口放行。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketListen.xml`](../examples/P_Demo_FB_SocketListen.xml)

```iecst
// 场景：PLC 在 200 端口监听，等待远端 SCADA / HMI 连入。
PROGRAM P_Demo_FB_SocketListen
VAR
    fbStartListening   : FB_SocketListen;
    bRequestListen     : BOOL;
    bListenBusy        : BOOL;
    bListenError       : BOOL;
    nListenErrId       : UDINT;
    hPlcListener       : T_HSOCKET;
END_VAR

fbStartListening(
    sSrvNetId   := '',
    sLocalHost  := '0.0.0.0',
    nLocalPort  := 200,
    bExecute    := bRequestListen,
    tTimeout    := T#5S,
    bBusy       => bListenBusy,
    bError      => bListenError,
    nErrId      => nListenErrId,
    hListener   => hPlcListener
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 作为 TCP 服务器，被 SCADA / HMI / 上位机或 MES 主动连进来。典型端口 102（S7）、502（Modbus TCP）、9100（条码上送）、自定义协议端口。
- **价值**：把 `bind + listen` 封装成单一 FB，自动处理 ADS 异步状态机；业务侧只关心 IP/端口。配合 `FB_SocketAccept` 即可形成完整服务器。
- **替代方案对比**：
  - `FB_ServerClientConnection`（PDF §5.1.20.2）：进一步把 Listen + Accept + Close 三件事打包；如不需要细粒度控制建议直接用 helper
  - EtherCAT 总线：实时性强但不能跨网段
  - ADS Server：仅适用 TwinCAT ↔ TwinCAT

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84146059.html
- **相关**：`FB_SocketAccept`（必须配对使用）、`FB_SocketClose`、`FB_TlsSocketListen`（TLS 版）、`FB_ServerClientConnection`（封装 helper）
