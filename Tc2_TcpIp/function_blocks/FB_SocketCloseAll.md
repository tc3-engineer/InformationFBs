# FB_SocketCloseAll

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84144523.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SocketCloseAll.TcPOU`](../examples/P_Demo_FB_SocketCloseAll.TcPOU) |

---

## 1. 功能简述

启动期 socket 兜底清理功能块：一次性关闭某个 PLC 运行时（runtime）曾经打开过、但因 PLC Reset / Rebuild all / Download 而失去 PLC 侧引用的所有 socket 句柄（TCP + UDP）。TwinCAT 重启或停止时 Connection Server 也会重启，残留 socket 会自动消失；但 **PLC Reset/Download 这种"只 PLC 程序重来、TwinCAT 系统不动"的场景**，Server 仍持有旧 socket，PLC 程序却忘了句柄——这是 Tc2_TcpIp 唯一需要 `FB_SocketCloseAll` 的场景。Beckhoff 建议：**每个使用 socket FB 的 PLC 运行时，在 PLC 启动阶段调用一次本 FB**。

按运行时（runtime）粒度清理：在 runtime 1（端口 851 / 旧版 801）的任务里调用，就只清 runtime 1 打开过的 socket，不影响其它 runtime。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId     : T_AmsNetId := '';
    bExecute      : BOOL;
    tTimeout      : TIME := T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TwinCAT TCP/IP Connection Server 的 AMS NetID。本机默认空串 |
| `bExecute` | `BOOL` | — | 上升沿触发一次"清空本 runtime 全部 socket"操作 |
| `tTimeout` | `TIME` | `T#5s` | 单次操作超时；常规 < 1 秒，PDF 例程示范填 `T#10s` 留余量 |

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
| `bBusy` | `BOOL` | 正在执行清理 |
| `bError` | `BOOL` | 清理失败置 `TRUE` |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号（同 §4） |

### VAR_IN_OUT

无。

## 3. 行为说明

**典型时序**（PDF §5.1.3 范例）：

```iecst
IF bCloseAll THEN          (* 仅在 PLC 启动那一刻执行一次 *)
    bCloseAll := FALSE;
    fbSocketCloseAll(sSrvNetId := '', bExecute := TRUE, tTimeout := T#10s);
ELSE
    fbSocketCloseAll(bExecute := FALSE);
END_IF
```

`bCloseAll` 是一个 `BOOL := TRUE` 初值变量；冷启动时 IF 分支成真一次，自己清零自己，随后周期里都走 ELSE 分支（不触发）。

**FB 内部状态机**：

1. `bExecute` 上升沿 → `bBusy := TRUE`，FB 让 Server 遍历"由本 runtime 打开过的全部句柄"列表，逐个 `closesocket`
2. 完成 → `bBusy := FALSE`、`bError := FALSE`
3. 失败 → `bBusy := FALSE`、`bError := TRUE`、`nErrId` 含错误码

**调用要点**：

- **只能在 PLC 启动那一刻调一次**：常规运行期不要反复跑。否则其他线程刚 Connect/Listen 出来的句柄会被立刻清掉
- **每个 runtime 独立清理**：runtime 1 的清理不影响 runtime 2；多 runtime 应用各自跑一次
- **顺序**：建议把 `FB_SocketCloseAll` 放在所有 socket 业务 FB **之前** 的同一个任务里，并用 `bCloseAll` 标志保证只跑一次后续业务再开始
- **不影响 TwinCAT 重启场景**：如果是冷启 PLC（TwinCAT 系统也刚启动），Server 端本来就没残留，此时调 `FB_SocketCloseAll` 是无操作（清 0 个），无害

**典型陷阱**：

- 把它接到电平 `TRUE` 持续调——会反复清掉刚建立的连接
- 忘记在 PLC 启动调一次——`PLC Reset` 或 `Download` 后旧 socket 永久泄漏，TF6310 句柄表满后所有 Connect/Listen 都失败
- 在 runtime 851 的任务清理，期望 runtime 852 也被清——**做不到**，每个 runtime 自管自

## 4. 错误码 / 返回值

| `nErrId` (hex) | 含义 |
|---|---|
| `0` | 成功（包括清 0 个句柄的无操作情况） |
| `6` / `7` | ADS 路由错（Server 没在跑 / NetID 错） |
| `1861` | ADS timeout |

本 FB 几乎不返回 Server 内部错误（`0x00008000`–`0x000080FF`），因为没有针对具体句柄的语义校验。

## 5. 使用注意 / 常见坑

- **`bCloseAll` 标志的初值必须是 `TRUE`**：PDF 范例明确，靠这个一次性触发；写成 `FALSE` 默认值就永远不清，泄漏照旧。
- **多 runtime 工程**：每个 runtime（每个 `MAIN`）单独有一份 `fbSocketCloseAll` 实例 + `bCloseAll` 标志。
- **耗时**：清几百个 socket 通常仍在 1 秒以内；`tTimeout := T#10s` 是 PDF 推荐的安全余量。
- **不会清理你不想清的**：本 FB 不能用来"踢掉某个客户端连接"，要踢单个用 `FB_SocketClose`。它只对"本 PLC runtime 之前打开过的"句柄生效。
- **PLC 程序里没有 socket FB 实例时不需要本 FB**：Server 仅记录"打开过 socket 的 runtime"，从未开过就没有清理对象。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SocketCloseAll.TcPOU`](../examples/P_Demo_FB_SocketCloseAll.TcPOU)

```iecst
// 场景：PLC 启动时一次性清空遗留 socket，然后业务逻辑才开始跑。
PROGRAM P_Demo_FB_SocketCloseAll
VAR
    fbSocketCloseAll : FB_SocketCloseAll;
    bCloseAllOnStart : BOOL := TRUE;          // 启动标志：必须以 TRUE 为初值
    bBusyCleanup     : BOOL;
    bCleanupError    : BOOL;
    nCleanupErrId    : UDINT;
    bSocketsReady    : BOOL;                  // 清理完成后才允许业务 socket FB 上场
END_VAR

IF bCloseAllOnStart THEN
    bCloseAllOnStart := FALSE;
    fbSocketCloseAll(
        sSrvNetId := '',
        bExecute  := TRUE,
        tTimeout  := T#10S,
        bBusy     => bBusyCleanup,
        bError    => bCleanupError,
        nErrId    => nCleanupErrId
    );
ELSE
    fbSocketCloseAll(bExecute := FALSE,
                     bBusy => bBusyCleanup,
                     bError => bCleanupError,
                     nErrId => nCleanupErrId);
END_IF

IF NOT bBusyCleanup THEN
    bSocketsReady := TRUE;                    // 之后 Connect/Listen 才允许跑
END_IF
```

## 7. 业务场景与实际价值

- **场景**：所有用 Tc2_TcpIp 的工程都要在 PLC 启动跑一次本 FB。开发期反复 `Download` / `PLC Reset` 调试时尤其关键，否则越调越多句柄泄漏，最后 `FB_SocketConnect` 报 `TCPADSERROR_NOMOREENTRIES`（系统并发 socket 上限）。
- **价值**：把"PLC Reset 后 Server 仍持有旧句柄"这个 Beckhoff 系统级 quirk 用一行启动代码彻底兜底。等价于 OS 级的 `fflush + WSACleanup` 集中调用。
- **替代方案对比**：
  - 在 PLC 程序里维护一张"我开过的全部句柄"表，启动时遍历每个跑一次 `FB_SocketClose`——可以，但 PLC Reset 后这张表也清空了，所以根本做不到
  - 每次开发都重启 TwinCAT System Service——开发期低效；本 FB 让"只重启 PLC 程序"就能恢复

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84144523.html
- **相关**：`FB_SocketClose`（关闭单个）、`FB_SocketConnect` / `FB_SocketListen` / `FB_SocketUdpCreate`（打开的源头）
