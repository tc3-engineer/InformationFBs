# FB_S_UPS_CB3011

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `CB3011` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/2220095883.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_S_UPS_CB3011.xml`](../examples/P_Demo_FB_S_UPS_CB3011.xml) |

---

## 1. 功能简述

`FB_S_UPS_CB3011` 是面向带有 **CB3011** 主板 + 1-second UPS（1 秒级 UPS 模块）的工控机的「断电保护管家」。它每个 PLC 周期被调用一次，内部通过 ADS 读取主板上的 UPS 状态位；一旦检测到供电异常，按用户选择的 `eUpsMode` 模式自动完成两件事：**把 retain（持久化）变量按 `SPDM_2PASS` 模式写入 Compact Flash**、然后**触发 `FB_NT_QuickShutdown` 让 TwinCAT 在剩余几秒电量内安全断电**。

1-second UPS 的电容只够维持工控机几秒钟，**不足以撑过停电也不足以驱动机械硬盘**——所以存储介质只能是 Compact Flash（CB3011 平台无 CFast/SD 选项）。本 FB 替工程师把"读 UPS 寄存器 → 判断要不要保存 → 启动 retain 写入 → 等待写完 → 触发系统关机"这一整套状态机封装好，业务代码只要每周期调用 + 监视 `eState` 输出即可知道当前断电应急流程进行到哪一步。

**默认输入值由 Beckhoff 针对 CB3011 调好，不应改动**；唯一在工程中可能需要换的是 `iPLCPort`（多 runtime 系统）和 `eUpsMode`（如果业务要求"只存数据不关机"或"只关机不存"）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId:= ''; (* '' = local netid *)
    iPLCPort        : UINT; (* PLC Runtime System for writing persistent data *)
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT; (* ADS Timeout *)
    eUpsMode        : E_S_UPS_Mode := eSUPS_WrPersistData_Shutdown; (* UPS mode (w/wo writing persistent data, w/wo shutdown) *)
    ePersistentMode : E_PersistentMode := SPDM_2PASS; (* mode for writing persistent data *)
    tRecoverTime    : TIME := T#10s; (* ON time to recover from short power failure in mode eSUPS_WrPersistData_NoShutdown/eSUPS_CheckPowerStatus *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | `''` | 控制器的 AmsNetId 字符串。空串 `''` 表示本机（CB3011 自己），跨机控制 UPS 在本平台无意义 |
| `iPLCPort` | `UINT` | — | 写持久化数据时寻址的 PLC runtime 端口号：第一个 runtime 系统是 `851`、第二个是 `852` …… 留 `0` 让 FB 自己探测（PDF 与 InfoSys 一致） |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 写 retain 数据 / 触发 quick shutdown 的 ADS 超时。默认常量约 5s；保持默认即可 |
| `eUpsMode` | `E_S_UPS_Mode` | `eSUPS_WrPersistData_Shutdown` | UPS 工作模式：是否写 retain、是否关机。默认是「写 retain 后立刻关机」，即生产环境最常用 |
| `ePersistentMode` | `E_PersistentMode` | `SPDM_2PASS` | 写 retain 的模式。**只能用 `SPDM_2PASS`**（fast persistent mode），其它模式来不及。PDF 明确警告这可能造成 real-time violation，但在 1-second UPS 紧急路径上必须接受 |
| `tRecoverTime` | `TIME` | `T#10s` | 「无关机」模式下电压恢复后多久才把 `eState` 切回 `eSUPS_PowerOK`。**必须大于 UPS 最大充电时间**，否则短时连续掉电会让电容来不及回满，再次掉电时电量不够写 retain |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bPowerFailDetect   : BOOL; (* TRUE while powerfailure is detected *)
    eState             : E_S_UPS_State := eSUPS_PowerOK; (* current ups state *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bPowerFailDetect` | `BOOL` | — | 实时电源标志：检测到掉电期间为 `TRUE`，供电恢复后立即为 `FALSE`。注意它**只反映瞬时电源状态**，不反映 FB 内部状态机是否还在收尾（那个看 `eState`） |
| `eState` | `E_S_UPS_State` | `eSUPS_PowerOK` | FB 当前所处的状态机阶段（见 §4 状态值表）。业务侧观察这一个就够 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约定**：必须每个 PLC 周期调用一次。FB 内部维护状态机；漏调一次就漏掉一个电源采样点。

**eUpsMode 决定的四种工作流**（与 §4 的 `eState` 配合阅读）：

1. **`eSUPS_WrPersistData_Shutdown`（默认）**：检测到掉电 → `eState := eSUPS_WritePersistentData` 期间触发 `SPDM_2PASS` 把 retain 数据写到 Compact Flash → 写完 `eState := eSUPS_QuickShutdown` 调用内部的 `FB_NT_QuickShutdown` 让系统重启 → `eState := eSUPS_WaitForPowerOFF` 等 UPS 电容耗尽硬断电。这是生产现场最常用的模式。
2. **`eSUPS_WrPersistData_NoShutdown`**：写完 retain 后不关机，进入 `eSUPS_WaitForRecover` 等待电压回来；若 `tRecoverTime` 内电压恢复则切回 `eSUPS_PowerOK`，否则继续等。适合「短时晃电也要存一次但不允许停产」的工艺。
3. **`eSUPS_ImmediateShutdown`**：跳过写 retain，直接 quick shutdown。用于"不关心数据但要确保安全断电"的场合（例如所有数据都是过程量、断电直接重启即可）。
4. **`eSUPS_CheckPowerStatus`**：纯监视模式，FB 不动 retain 也不关机，只把 `bPowerFailDetect`/`eState` 报出来给用户代码自己决策。`tRecoverTime` 过后才回 `eSUPS_PowerOK`。

**关键时序约束**：1-second UPS 的电容只够支撑数秒，从 `bPowerFailDetect` 上升沿到主板硬断电的窗口非常窄；retain 必须用 `SPDM_2PASS`（fast 2-pass，会暂时违反实时性但能在毫秒级写完关键变量），并且**必须在 PLC 项目设置里把 Router Memory 调大**到足以容纳所有 retain。如果 router memory 不够，写到一半失败 → 下次启动数据丢失。

**不可改的默认**：PDF 明确写「The default input values of the FB_S_UPS_CB3011 should be retained」。`ePersistentMode := SPDM_2PASS` 和 `eUpsMode` 的默认值都是 Beckhoff 针对 CB3011 调好的；除非有明确工艺理由，不要改。

**与其它 FB 的关系**：本 FB 内部使用 `FB_NT_QuickShutdown` 触发系统重启，业务代码**不要**自己再去调用 `FB_NT_QuickShutdown`（PDF 警告会导致数据丢失）。

## 4. 错误码 / 返回值

本 FB 不暴露 `bError` / `nErrID` 输出（这是与 BAPI 版本的关键区别）。运行状态全部体现在 `eState : E_S_UPS_State` 上，PDF §5.2 列出的取值如下：

| 取值 | 含义 |
|---|---|
| `eSUPS_PowerOK` | 所有模式：供电正常 |
| `eSUPS_PowerFailure` | 所有模式：检测到掉电（仅一个周期，下一周期就切到具体的工作状态） |
| `eSUPS_WritePersistentData` | 在 `eSUPS_WrPersistData_Shutdown` 或 `eSUPS_WrPersistData_NoShutdown` 模式下：正在写 retain 数据 |
| `eSUPS_QuickShutdown` | 在 `eSUPS_WrPersistData_Shutdown` 或 `eSUPS_ImmediateShutdown` 模式下：quick shutdown 正在执行 |
| `eSUPS_WaitForRecover` | 在 `eSUPS_WrPersistData_NoShutdown` 或 `eSUPS_CheckPowerStatus` 模式下：等待电压恢复（最长 `tRecoverTime`） |
| `eSUPS_WaitForPowerOFF` | 在 `eSUPS_WrPersistData_Shutdown` 或 `eSUPS_ImmediateShutdown` 模式下：等待 UPS 电容耗尽 / 主板断电 |

⚠️ PDF 与 InfoSys 均未列具体 ADS 错误号表；retain 写入失败、`FB_NT_QuickShutdown` 触发失败等错误**不会通过本 FB 的输出报出来**，只能通过 retain 内容缺失、SYSLOG 或 TwinCAT Event 间接发现。这是 CB3011 版本与 BAPI 版本（后者有 `bError` / `nErrID`）的设计差异。

## 5. 使用注意 / 常见坑

- **Router Memory 一定要预留够**：retain 大小（数百 KB ~ 几 MB）+ 一些 housekeeping。在 PLC 项目右键 → Properties → PLC → Router Memory，按 retain 总量的 1.5-2 倍配。配不够 → 掉电写一半失败 → 上电缺数据，**而本 FB 不会报错**。
- **存储介质必须是 Compact Flash**：CB3011 平台不要装机械硬盘期望 retain 写过去——电容根本撑不到硬盘磁头到位。
- **默认输入值不要改**：尤其 `ePersistentMode` 不要换成 `SPDM_2PASS` 以外的（Beckhoff 标准模式 SPDM_2PASS_NORMAL / SPDM_2PASS_ZEROCHECKING 等在 1-second UPS 紧急路径上来不及）。改了就违反 PDF 明文指引。
- **FB 必须**每周期都调用**：通常在 MAIN 程序里放一个 `fbSUPS();`，**不要**塞进条件分支里。漏几个周期可能错过最关键的电压跌落瞬间。
- **`tRecoverTime` 必须大于电容充满时间**（PDF 明示）：默认 `T#10s` 对绝大多数 CB3011 + 1-second UPS 配置足够；只在工厂的 UPS 配了非标电容才需要重算。
- **`bPowerFailDetect` 是瞬时位，`eState` 是过程位**：调度 HMI 告警的时候要看 `eState` 是否进入了 `eSUPS_WritePersistentData` / `eSUPS_QuickShutdown`——这才说明应急流程真的启动了，光看 `bPowerFailDetect` 只能知道电源信号本身。
- **不要自己再调用 `FB_NT_QuickShutdown`**（工程经验补充）：PDF 明确警告「会导致数据丢失」。本 FB 已经在内部组合了 retain 写入 + QuickShutdown 的正确顺序。
- **写 retain 时短暂的 real-time violation 是正常的**（工程经验补充）：`SPDM_2PASS` 会在两个 PLC 周期里把全部 retain 推完，期间任务超时是预期行为，TwinCAT 实时性告警会出现一次——这与永久性的实时违规要区分。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_S_UPS_CB3011.xml`](../examples/P_Demo_FB_S_UPS_CB3011.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：某 CB3011 工控机做食品灌装计量，断电时必须保存"本班次累计灌装重量"
//       这个 retain 变量。1-second UPS 给我们 2-3 秒在掉电后存数据 + 关机。
//
// 价值：不用本 FB 要自己写：读 UPS 寄存器 → 解析电源位 → 启动 SPDM_2PASS →
//       等待写完 → 调 FB_NT_QuickShutdown → 监督 timeout。本 FB 把这套
//       封装好，业务侧只关心 eState 走到哪一步。
//
// 验证：登录 + 运行 → 拔掉外部 24V 电源（注意只能在硬件没接负载的台架上做） →
//       观察 bPowerFailNow 立即变 TRUE、eUpsState 依次走过
//       eSUPS_WritePersistentData → eSUPS_QuickShutdown → eSUPS_WaitForPowerOFF
//       → 设备重启 → 上电后 nBatchKgRetain 仍为掉电前的值。
PROGRAM P_Demo_FB_S_UPS_CB3011
VAR
    fbSUPS               : FB_S_UPS_CB3011;
    nBatchKgRetain       : LREAL;          // 在工程里这里会加 RETAIN 关键字
    bPowerFailNow        : BOOL;
    eUpsState            : E_S_UPS_State;
END_VAR
// 默认参数全部保留：sNetID = '' (本机), iPLCPort = 0 (自动探测),
// tTimeout = DEFAULT_ADS_TIMEOUT, eUpsMode = eSUPS_WrPersistData_Shutdown,
// ePersistentMode = SPDM_2PASS, tRecoverTime = T#10s
fbSUPS(
    sNetID          := '',
    iPLCPort        := 0,
    tTimeout        := DEFAULT_ADS_TIMEOUT,
    eUpsMode        := eSUPS_WrPersistData_Shutdown,
    ePersistentMode := SPDM_2PASS,
    tRecoverTime    := T#10s,
    bPowerFailDetect => bPowerFailNow,
    eState           => eUpsState
);
```

## 7. 业务场景与实际价值

- **场景**：带 CB3011 板 + 1-second UPS 的工控机，常见在工艺线现场柜（食品灌装、印刷设备、小型装配线）。这些场合无法上工业 UPS，但 retain 数据（班次累计、配方计数、当前工序号）一旦掉，重启后必须人工对单或者重做一整批料。1-second UPS + 本 FB 用极低成本（电容板而非铅酸电池）实现"软关机 + retain 保住"。
- **价值**：用 vs 不用的对比是「**重启后 retain 完整**」vs「**重启后 retain 一片 0**」。技术层面省下：① 自己读 ADS 4A8/588/0xX 寄存器拿电源位的代码 ② 自己写双段持久化触发器 ③ 自己写 `FB_NT_QuickShutdown` 调用 + 失败回退；估算约 60-80 行手写 + 完整的边界测试。
- **替代方案对比**：
  - **不用 UPS**：掉电瞬间 retain 不写盘，直接丢；下次开机 retain 区被 PLC 重置为类型默认值（BOOL → FALSE, INT → 0, STRING → ''）
  - **手写 ADS 读 + 手写 QuickShutdown**：能做，但容易在「retain 还没写完就调 quick shutdown」上踩坑，导致数据写一半被打断 → CF 卡上 retain 文件损坏
  - **本 FB**：Beckhoff 实现 + 验证过的正确顺序，所有边界（连续掉电 / 写一半电压恢复 / `tRecoverTime` 超时）都已处理

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/2220095883.html
- **相关枚举**：`E_S_UPS_Mode`（PDF §5.1）、`E_S_UPS_State`（PDF §5.2）
- **相关 FB**：`FB_NT_QuickShutdown`（本 FB 内部使用，不可直接调用）、其它平台的 UPS 变体（`FB_S_UPS`/CX50x0、`FB_S_UPS_CX51x0`、`FB_S_UPS_CX9020_U900`、`FB_S_UPS_BAPI`）
