# FB_SocketUdpDropMulticastAddress

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84158347.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketUdpDropMulticastAddress.TcPOU`](../examples/P_Demo_FB_SocketUdpDropMulticastAddress.TcPOU) |

---

## 1. 功能简述

把已加入多播组的 UDP socket 退出该组的功能块——之前由 `FB_SocketUdpAddMulticastAddress` 注册的成员关系被撤销。底层等价于 OS 的 `setsockopt(IPPROTO_IP, IP_DROP_MEMBERSHIP, ...)`。退出后 socket 仍然存在，可以继续收发单播 UDP；只是不再接收该多播组的包。**Add / Drop 必须配对**：每个 Add 都应有一个对应 Drop（关 socket 时 OS 会自动清理，但显式 Drop 更规范，也便于动态订阅切换）。

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
| `hSocket` | `T_HSOCKET` | — | UDP socket 句柄 |
| `sMulticastAddr` | `STRING(15)` | — | 要退出的多播 IPv4 地址。必须是之前 Add 过的同一地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次退出 |
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
| `bBusy` | `BOOL` | 正在退出 |
| `bError` | `BOOL` | 退出失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次退出。

**单次退出状态机**：上升沿 → `bBusy := TRUE`；Server 调 `setsockopt + IP_DROP_MEMBERSHIP`；OS 向上游路由器发 IGMP Leave 报文；完成 → `bBusy := FALSE`、`bError := FALSE`。之后该 socket 上的 `FB_SocketUdpReceiveFrom` 不再收到该多播组的包（单播和其它仍在的组照常工作）。

**幂等行为**：对一个不曾加入的组调本 FB 会报 `WSAEADDRNOTAVAIL` (10049) 或类似错误——不要靠 Drop 来"清理任意 socket"，先确认有加入过。

**动态订阅切换**：典型用法是"先 Drop 旧组，再 Add 新组"，比如多 SCADA 通道切换。建议两步用上下文标志同步，等 Drop 的 `bBusy=FALSE` 再发 Add 触发。

**典型陷阱**：在 socket 已关闭（`FB_SocketClose` 跑过）后调本 FB——`NOTFOUND`。`sMulticastAddr` 写错（如多打了空格）——OS 找不到匹配的组成员关系，报错。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x80072731` | `WSAEADDRNOTAVAIL` (10049) | 未加入过该组或地址错 |
| `0x80072736` | `WSAEINVAL` (10022) | 地址不是合法多播 IP |

## 5. 使用注意 / 常见坑

- **必须 Add / Drop 配对**：上层维护"已加入组列表"，做到能枚举关闭。
- **Drop 后 socket 仍可用**：只是不再接收该组包；单播和其它组照常。
- **关闭 socket 等价于自动 Drop 所有组**：紧急关闭时可直接 `FB_SocketClose`，OS 会清；但生产代码仍建议显式 Drop 以表达意图。
- **跨网段多播 IGMP**：Drop 之后路由器经过一定 IGMP query 周期才会停转发到本网段，期间可能仍偶尔收到，业务侧需自己滤掉。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketUdpDropMulticastAddress.TcPOU`](../examples/P_Demo_FB_SocketUdpDropMulticastAddress.TcPOU)

```iecst
// 场景：动态切换多播订阅，先退出 239.1.1.100，再加入 239.1.1.200。
PROGRAM P_Demo_FB_SocketUdpDropMulticastAddress
VAR
    fbDropGroup    : FB_SocketUdpDropMulticastAddress;
    hUdpSocket     : T_HSOCKET;
    bRequestDrop   : BOOL;
    bDropBusy      : BOOL;
    bDropError     : BOOL;
    nDropErrId     : UDINT;
END_VAR

fbDropGroup(
    sSrvNetId      := '',
    hSocket        := hUdpSocket,
    sMulticastAddr := '239.1.1.100',
    bExecute       := bRequestDrop,
    tTimeout       := T#5S,
    bBusy          => bDropBusy,
    bError         => bDropError,
    nErrId         => nDropErrId
);
```

## 7. 业务场景与实际价值

- **场景**：多播订阅切换（如换班时把 SCADA 监听源从车间组改成总装组）、节省网络带宽（不再需要的组主动退出）、PLC 下线前优雅释放组成员关系。
- **价值**：把 OS `IP_DROP_MEMBERSHIP` 异步封装；和 Add 形成对称 API，业务代码读起来对称易懂。
- **替代方案对比**：
  - 直接 `FB_SocketClose`：粗暴但有效；适合"完全退出多播"场景
  - 本 FB：仅解除一组成员关系，保留 socket 做单播或其它组——更精细

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84158347.html
- **相关**：`FB_SocketUdpAddMulticastAddress`（必须配对）、`FB_SocketUdpCreate`、`FB_SocketUdpReceiveFrom`、`FB_SocketClose`
