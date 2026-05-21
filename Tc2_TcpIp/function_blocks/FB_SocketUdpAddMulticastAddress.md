# FB_SocketUdpAddMulticastAddress

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84156811.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketUdpAddMulticastAddress.xml`](../examples/P_Demo_FB_SocketUdpAddMulticastAddress.xml) |

---

## 1. 功能简述

把已创建的 UDP socket 加入到指定多播组的功能块——之后这条 socket 上的 `FB_SocketUdpReceiveFrom` 才能收到发往该多播 IP 的包。底层等价于 OS 的 `setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, ...)`。前提是已有打开的 UDP socket（来自 `FB_SocketUdpCreate`）。**只有"接收方"需要加入多播组；发送方直接往 224–239.x.x.x 发即可**。一个 socket 可以加入多个多播组（多次调用本 FB）。退出组用对应的 `FB_SocketUdpDropMulticastAddress`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId      : T_AmsNetId := '';
    hSocket        : T_HSOCKET;
    sMulticastAddr : STRING(15);
    bExecute       : BOOL;
    tTimeout       : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server 的 AMS NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | UDP socket 句柄（由 `FB_SocketUdpCreate` 提供） |
| `sMulticastAddr` | `STRING(15)` | — | 要加入的多播 IPv4 地址。**必须落在 `224.0.0.0`–`239.255.255.255`** |
| `bExecute` | `BOOL` | — | 上升沿触发一次加入 |
| `tTimeout` | `TIME` | `T#5s` | ADS 超时 |

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
| `bBusy` | `BOOL` | 正在加入 |
| `bError` | `BOOL` | 加入失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次加入。

**单次加入状态机**：上升沿 → `bBusy := TRUE`；Server 调 `setsockopt + IP_ADD_MEMBERSHIP`；OS 把本机网卡注册到 IGMP，向上游路由器报告"我加入 group X"；完成 → `bBusy := FALSE`、`bError := FALSE`。从此该 socket 上的 ReceiveFrom 能收到任何来自该 group 的包。

**典型多播流程**：

1. `FB_SocketUdpCreate(sLocalHost := '0.0.0.0', nLocalPort := <group_port>)` 创建 socket
2. `FB_SocketUdpAddMulticastAddress(hSocket := h, sMulticastAddr := '239.1.1.100')` 加入组
3. `FB_SocketUdpReceiveFrom(hSocket := h, ...)` 周期 polling 收包
4. 不再要时调 `FB_SocketUdpDropMulticastAddress`，最后 `FB_SocketClose`

**多组订阅**：同一 socket 可加入多个多播组（多次调本 FB，每次不同 `sMulticastAddr`）；ReceiveFrom 不区分来自哪个组，只能从包的目的 IP 推断（但 ReceiveFrom 输出的是 source IP 不是 dst IP——所以业务上想区分，建议每组一个 socket）。

**绑定网卡**：本 FB 在 `sLocalHost = '0.0.0.0'` 创建的 socket 上调用时，会在所有网卡上加入组（OS 默认）。要绑定具体网卡，请在 Create 时显式填该网卡 IP。

**典型陷阱**：用非多播 IP（如 192.168.1.1）调本 FB——OS 报 `WSAEINVAL`。在 socket 未创建好就调本 FB——`NOTFOUND`。退出组后忘记重新加入——不会再收到。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x80072736` | `WSAEINVAL` (10022) | `sMulticastAddr` 不在多播范围或格式错 |
| `0x8007274D` | `WSAENOPROTOOPT` (10042) | 系统不支持该 setsockopt |

## 5. 使用注意 / 常见坑

- **必须先 `FB_SocketUdpCreate`**：在 Server 端没有 socket 实体时本 FB 必失败。
- **多播 IP 范围**：`224.0.0.0/4`。注意 `224.0.0.0–224.0.0.255` 是本地链路保留（不会被路由器转发），跨网段多播请用 `239.0.0.0–239.255.255.255` 行政范围。
- **跨子网多播**：需要中间路由器支持 IGMP/PIM；纯本网段的话 IGMP 即可。
- **退出别忘 Drop**：`FB_SocketUdpDropMulticastAddress` 不调时 OS 会一直认为本机"在组里"，消耗 IGMP 资源；不过 socket 关闭时 OS 也会自动退出。
- **重复加入同一组**：通常返回错误而不是无操作；建议业务侧维护"已加入"标志。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketUdpAddMulticastAddress.xml`](../examples/P_Demo_FB_SocketUdpAddMulticastAddress.xml)

```iecst
// 场景：加入多播组 239.1.1.100，准备接收组播视频流元数据。
PROGRAM P_Demo_FB_SocketUdpAddMulticastAddress
VAR
    fbJoinGroup    : FB_SocketUdpAddMulticastAddress;
    hUdpSocket     : T_HSOCKET;          // 由 FB_SocketUdpCreate 提供
    bRequestJoin   : BOOL;
    bJoinBusy      : BOOL;
    bJoinError     : BOOL;
    nJoinErrId     : UDINT;
END_VAR

fbJoinGroup(
    sSrvNetId      := '',
    hSocket        := hUdpSocket,
    sMulticastAddr := '239.1.1.100',
    bExecute       := bRequestJoin,
    tTimeout       := T#5S,
    bBusy          => bJoinBusy,
    bError         => bJoinError,
    nErrId         => nJoinErrId
);
```

## 7. 业务场景与实际价值

- **场景**：组播视频流（监控、远程示教）、组播配方下发（一台 OEE / SCADA 同时下发到多 PLC）、组播时间同步（如 PTP 协议在某些实现里用多播）、组播报警广播。
- **价值**：把"OS setsockopt IGMP 加入"封装成 ADS 异步调用；业务侧只关心多播 IP 字串。
- **替代方案对比**：
  - 多次单播：发 100 个 PLC 就要发 100 次，带宽线性增长；多播只发一次
  - 广播：仅同 L2 段，过路由就丢
  - 多播：跨网段（需路由器 IGMP 支持），扩展性好

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84156811.html
- **相关**：`FB_SocketUdpCreate`（前置）、`FB_SocketUdpReceiveFrom`（收多播包）、`FB_SocketUdpDropMulticastAddress`（必须配对调用）
