# FB_WriteWatchdog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DataExchange` |
| Library Version | `1.2.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Watchdog function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/54804235.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_WriteWatchdog.xml`](../examples/P_Demo_FB_WriteWatchdog.xml) |

---

## 1. 功能简述

发送端 watchdog 心跳信号生成器。本 FB 周期性把一个内部 32 位计数器递增后用 ADS 写入到对端某个变量（按 NetID + 端口号 + 索引组/偏移 或 符号名 定位）。每写入一次成功，计数器 +1；对端跑 `FB_CheckWatchdog` 看这个计数器是否在动，即可判断本机是否还活着。

配套使用：本机用 `FB_WriteWatchdog` 发，对端用 `FB_CheckWatchdog` 收，构成最小的 PLC ↔ PLC 链路保活方案。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable          :  BOOL := FALSE;
    sNetId           :  T_AmsNetId;
    nPort            :  T_AmsPort;
    nIdxGrp          :  UDINT;
    nIdxOffs         :  UDINT;
    sVarName         :  STRING;
    tWatchdogTime    :  TIME := t#0s;
    bSendNow         :  BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEnable` | `BOOL` | `FALSE` | 使能本 FB。`FALSE` 时完全停止发送 |
| `sNetId` | `T_AmsNetId` | — | 对端的 AMS NetID（例如 `'192.168.1.100.1.1'`）。本机内部回环用空串 `''` |
| `nPort` | `T_AmsPort` | — | 对端的 AMS 端口号（典型 `851` = TwinCAT 3 运行时第一个 PLC 任务） |
| `nIdxGrp` | `UDINT` | — | 对端 ADS 索引组（指明数据区类型，如 `16#4040` = PLC 输入映像、`16#4020` = M 区） |
| `nIdxOffs` | `UDINT` | — | 对端 ADS 索引偏移（数据区内字节偏移） |
| `sVarName` | `STRING` | — | 对端符号名定位的另一种方式（如 `'GVL.nHeartbeat'`）。若提供则优先于 IdxGrp/IdxOffs；不用时填空串 |
| `tWatchdogTime` | `TIME` | `t#0s` | 发送周期。**特例**：`t#0s` 时停止发送。InfoSys 警告：**不要短于 1s**，否则 ADS 频率过高浪费带宽 |
| `bSendNow` | `BOOL` | — | 上升沿强制立即发送一次，不等当前周期到时（用于上电时立刻让对端知道本机活了） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     :  BOOL := FALSE;
    nLastCnt  :  UDINT := 0;
    bError    :  BOOL := FALSE;
    nErrorId  :  UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 当前正在执行一次 ADS 写入。`FALSE` = 空闲（要么没到周期，要么刚发完） |
| `nLastCnt` | `UDINT` | 最近一次成功发送出去的计数值。可在本地 monitor 它检查本机是否在正常发心跳 |
| `bError` | `BOOL` | 上一次 ADS 写入失败时置 `TRUE`，下一次成功时自动清零 |
| `nErrorId` | `UDINT` | ADS 错误号（参考 ADS Return Codes，如 `1861` = 目标不可达，`1808` = 符号名找不到等） |

### VAR_IN_OUT

无。

## 3. 行为说明

**两种发送模式并行**：

1. **周期发送**：`bEnable = TRUE` + `tWatchdogTime > 0s` 时，每过 `tWatchdogTime` FB 自动触发一次 ADS 写入，把内部 `nLastCnt` 递增后发往对端。
2. **手动触发**：`bSendNow` 上升沿（不论 `bEnable`、`tWatchdogTime`）立即触发一次写入。常用于上电时刻立刻通告对端。

**单次写入的内部状态机**：

1. 触发 → `bBusy := TRUE`，调用底层 ADS Write
2. ADS 返回成功 → `nLastCnt += 1`，`bBusy := FALSE`，`bError := FALSE`
3. ADS 返回失败 → `bBusy := FALSE`，`bError := TRUE`，`nErrorId := <ADS error>`；**`nLastCnt` 不递增**（这样对端能正确判断"本机没在发"）

**禁用分支**：

- `bEnable = FALSE`：停止周期发送，但保留状态（`nLastCnt` 不清零）。`bSendNow` 上升沿仍可触发单次发送
- `tWatchdogTime = t#0s`：停止周期发送（语义同 `bEnable = FALSE`，但内部计时器不重置）
- `sNetId = ''` 表示发到本机自身 AMS Router，常用于诊断/回环

`nLastCnt` 永远递增不回绕（理论上 32 位 UDINT 在 1Hz 下要 136 年才溢出）。

## 4. 错误码 / 返回值

| 输出 | 含义 |
|---|---|
| `bError = TRUE` | 上一次 ADS 写入失败 |
| `nErrorId` | ADS 错误码（典型值见下表） |

PDF / InfoSys 均未列具体错误码表，需参考 ADS Return Codes（Beckhoff InfoSys 主搜索 "ADS Return Codes"）。常见值（工程经验补充）：

- `0x06` (6) = "Target port not found" — 对端 PLC 没在跑 / nPort 错
- `0x07` (7) = "Target machine not found" — 对端 NetID 写错或离线
- `0x710` (1808) = 符号名找不到 — `sVarName` 不在对端命名空间
- `0x745` (1861) = "Target NetID not in Route table" — 没建立 AMS 路由

## 5. 使用注意 / 常见坑

- **`tWatchdogTime` 不要短于 1 秒**。1ms 周期发送会把 ADS 通道挤爆，整个 TwinCAT 系统都会卡。InfoSys 明确警告。
- **`sVarName` 与 `nIdxGrp` + `nIdxOffs` 二选一使用**。同时填两个时本 FB 优先用 `sVarName`，但容易让你以为 IdxGrp 生效，导致排查方向错。建议团队规约只用其中一种。
- **AMS 路由必须先建好**：在 TwinCAT XAE 中右键 SYSTEM → Routes 加上对端 NetID，否则 `nErrorId = 0x745`。本 FB 不负责建路由。
- **对端必须有可写的目标变量**：`sVarName` 指向只读输入映像（`%IB`）时写入会失败，必须是用户 GVL 或 M 区。
- **掉电时 `nLastCnt` 不 retain**。上电后从 0 重新开始递增。如果对端在重启间隙做了"`nLastCnt` 倒退就报警"的策略，需要双方协商初始化握手。（工程经验补充）
- **多实例不要写同一个对端地址**：两个 `FB_WriteWatchdog` 写同一个 `(NetId, IdxGrp, IdxOffs)` 会互相覆盖，对端看到的递增序列是乱的。
- **`bSendNow` 在 `bEnable=FALSE` 时仍然有效**：这个特性可用作"诊断 ping"——业务侧保持 `bEnable=FALSE` 不进入正式监视，只在按钮按下时 `bSendNow` 一脉冲触发一次写入，验证链路通不通。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_WriteWatchdog.xml`](../examples/P_Demo_FB_WriteWatchdog.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：本机是冗余主备里的 Master PLC，对端是 Slave PLC（NetID 192.168.1.20.1.1，
//       端口 851）。本机要让 Slave 知道"主机还活着"，每 2 秒往 Slave 的 GVL.nMasterHeartbeat
//       写一次递增计数。Slave 侧跑 FB_CheckWatchdog 看这个变量。
//
// 价值：不用本 FB 就得自己写：内部计数器 + 周期触发 + ADSWRITE 调用 + 错误重试。
//       本 FB 把"周期 ADS Write + 失败标记 + bSendNow 立即发"封装为 1 个调用。
//
// 验证：在线把 bEnableHeartbeat := TRUE，观察 nLastCounterSent 每 2 秒 +1，bWriting 短暂闪烁；
//       在线给 Slave PLC 断电 → 观察 bWriteError 被点亮，nLastAdsError 显示 6 或 7；
//       恢复 Slave → bWriteError 在下一周期自动清零；
//       按下 bDiagnosticPing 单脉冲 → 即使 bEnable=FALSE 也会立刻发一次（看 nLastCounterSent +1）。
PROGRAM P_Demo_FB_WriteWatchdog
VAR
    fbWriteWatchdog          : FB_WriteWatchdog;
    bEnableHeartbeat         : BOOL := FALSE;             // 在线置 TRUE 启动心跳
    sSlaveNetId              : T_AmsNetId := '192.168.1.20.1.1';
    nSlavePort               : T_AmsPort  := 851;          // TwinCAT3 PLC task1
    sSlaveSymbol             : STRING     := 'GVL.nMasterHeartbeat';
    tHeartbeatPeriod         : TIME       := T#2S;         // 不短于 1 秒
    bDiagnosticPing          : BOOL;                       // 上升沿单次诊断

    bWriting                 : BOOL;                       // 在线 monitor
    nLastCounterSent         : UDINT;                      // 应每 2 秒 +1
    bWriteError              : BOOL;
    nLastAdsError            : UDINT;
END_VAR

// 单次调用形式：所有 VAR_INPUT 显式赋值（IdxGrp / IdxOffs 不用，传 0）
fbWriteWatchdog(
    bEnable       := bEnableHeartbeat,
    sNetId        := sSlaveNetId,
    nPort         := nSlavePort,
    nIdxGrp       := 0,
    nIdxOffs      := 0,
    sVarName      := sSlaveSymbol,
    tWatchdogTime := tHeartbeatPeriod,
    bSendNow      := bDiagnosticPing,
    bBusy         => bWriting,
    nLastCnt      => nLastCounterSent,
    bError        => bWriteError,
    nErrorId      => nLastAdsError
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 主备冗余、多 PLC 协同（如总装线分段 PLC）、PLC ↔ HMI 通讯心跳。本机需要主动声明"我还活着"，让对端能识别故障切换。
- **价值**：把"周期 ADS Write + 内部计数器 + 错误诊断 + 即时触发"四件事打成一个 FB，业务代码只关心 NetID/端口/周期。配套 `FB_CheckWatchdog` 形成完整保活对。
- **替代方案对比**：
  - 自己用 `ADSWRITE` 写：要管周期触发、内部计数、ADS 状态机，约 30 行代码
  - 用 EtherCAT DC 同步：硬件级，更可靠但不能跨网段
  - 用 TF6310 TCP/UDP：协议更通用但要自己定义心跳报文格式
  - **本 FB**：纯 ADS、TwinCAT 自带、无额外协议，适合两台都是 Beckhoff TwinCAT 的场景

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf) §4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/54804235.html
- **相关**：`FB_CheckWatchdog`（接收端，配套）、`ADSWRITE`（底层 Tc2_System）、ADS Return Codes 表

## 9. 待确认项

- ⚠️ ADS 错误码表 PDF/InfoSys 均未列出，需用户参考通用 ADS Return Codes 文档自行查阅。文档已提供常见值（标"工程经验补充"）。
