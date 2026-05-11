# FB_S_UPS_CX9020_U900

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `CX9020-U900` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/2250162827.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_S_UPS_CX9020_U900.xml`](../examples/P_Demo_FB_S_UPS_CX9020_U900.xml) |

---

## 1. 功能简述

`FB_S_UPS_CX9020_U900` 是面向 **CX9020-U900 嵌入式控制器 + 1-second UPS** 的「断电保护管家」。每个 PLC 周期被调用一次，内部读 CX9020-U900 主板上的 UPS 状态；检测到掉电后，按 `eUpsMode` 自动**用 `SPDM_2PASS` 写 retain 数据到 Compact Flash** 并**调用内部 `FB_NT_QuickShutdown` 完成系统重启**。

CX9020-U900 是 CX9020 系列里专门配 1-second UPS 子模块的硬件型号（"U900" 后缀即代表带 UPS 选件）。**与 CX50x0 / CX51x0 版的关键差别是接口里没有 `iUPSPort` 输入**——CX9020-U900 平台上 UPS 状态由 FB 内部固定路径读取，业务无需也无法指定端口。

**默认输入值由 Beckhoff 针对 CX9020-U900 调好，不应改动**。存储介质必须是 Compact Flash，电容只够数秒，retain 必须 `SPDM_2PASS`。

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
| `sNetID` | `T_AmsNetId` | `''` | 控制器 AmsNetID。空串表示本机；跨机控制 UPS 在本平台无意义 |
| `iPLCPort` | `UINT` | — | 写 retain 时寻址的 PLC runtime 端口（`851`/`852`/……）。填 `0` 让 FB 自动探测 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 写 retain / 触发 quick shutdown 的 ADS 超时 |
| `eUpsMode` | `E_S_UPS_Mode` | `eSUPS_WrPersistData_Shutdown` | UPS 工作模式：是否写 retain、是否关机。默认是「写 retain 后立刻关机」 |
| `ePersistentMode` | `E_PersistentMode` | `SPDM_2PASS` | 写 retain 的模式。**必须 `SPDM_2PASS`** |
| `tRecoverTime` | `TIME` | `T#10s` | 「无关机」模式下电压恢复后多久才回 `eSUPS_PowerOK`。**必须略大于 UPS 最大保持时间**以保证电容充满；PDF 原文「somewhat longer than the maximum holding time of the UPS」 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bPowerFailDetect  : BOOL; (* TRUE while powerfailure is detected *)
    eState            : E_S_UPS_State := eSUPS_PowerOK; (* current ups state *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bPowerFailDetect` | `BOOL` | — | 实时电源标志：掉电中 `TRUE`，恢复后立即 `FALSE`。瞬时位 |
| `eState` | `E_S_UPS_State` | `eSUPS_PowerOK` | FB 当前状态机阶段（见 §4） |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约定**：必须每个 PLC 周期调用一次。CX9020-U900 上 UPS 状态由 FB 内部读取，业务无需提供端口号。

**与 CX50x0/CX51x0 版的差异**：接口去掉了 `iUPSPort`；其它所有参数语义、状态机和模式行为完全一致。

**eUpsMode 决定的四种工作流**：

1. **`eSUPS_WrPersistData_Shutdown`（默认）**：检测掉电 → `eState := eSUPS_WritePersistentData` 用 `SPDM_2PASS` 推 retain 到 CF → `eState := eSUPS_QuickShutdown` 调用 `FB_NT_QuickShutdown` 重启 → `eSUPS_WaitForPowerOFF` 等电容耗尽硬断电。最常用。
2. **`eSUPS_WrPersistData_NoShutdown`**：只写 retain 不关机，写完进 `eSUPS_WaitForRecover`，`tRecoverTime` 内电压恢复回 `eSUPS_PowerOK`，否则继续等。
3. **`eSUPS_ImmediateShutdown`**：跳过 retain 直接 quick shutdown。用于全过程量场合。
4. **`eSUPS_CheckPowerStatus`**：纯监视，只报 `bPowerFailDetect`/`eState`，业务自己决策。

**关键时序约束**：CX9020-U900 上 1-second UPS 电容只够数秒，retain 必须 `SPDM_2PASS`（fast 2-pass，会短暂违反实时性是预期行为）；Router Memory 必须配到 retain 总量的 1.5-2 倍；本 FB 内部已经组合了 retain 写入 + QuickShutdown 的正确顺序，**业务不要自己再调 `FB_NT_QuickShutdown`**。

**`tRecoverTime` 的特殊措辞**：CX9020-U900 版 PDF 用「必须略长于 UPS 最大保持时间，以保证电容充满」（与 CB3011 / CX5x 版的「大于充电时间」表述等价但更直接），核心约束都是「下一次掉电时电容要满」。

## 4. 错误码 / 返回值

本 FB 不暴露 `bError` / `nErrID`。所有运行状态体现在 `eState : E_S_UPS_State`，PDF §5.2 列出的取值：

| 取值 | 含义 |
|---|---|
| `eSUPS_PowerOK` | 所有模式：供电正常 |
| `eSUPS_PowerFailure` | 所有模式：检测到掉电（仅一个周期） |
| `eSUPS_WritePersistentData` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_WrPersistData_NoShutdown` 模式下：正在写 retain |
| `eSUPS_QuickShutdown` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_ImmediateShutdown` 模式下：quick shutdown 执行中 |
| `eSUPS_WaitForRecover` | `eSUPS_WrPersistData_NoShutdown` / `eSUPS_CheckPowerStatus` 模式下：等电压恢复 |
| `eSUPS_WaitForPowerOFF` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_ImmediateShutdown` 模式下：等 UPS 电容耗尽 |

⚠️ PDF 与 InfoSys 均未列具体错误号表；retain 写入失败、内部 UPS 寄存器读失败等问题不通过 FB 输出报出。可借助 SYSLOG / TwinCAT Event Viewer 间接观察。

## 5. 使用注意 / 常见坑

- **CX9020-U900 才有 UPS**：CX9020 普通版（不带 -U900 后缀）没有 1-second UPS 子模块；用错型号 → FB 编译过但运行时永远读不到电源状态。
- **Router Memory 配到 retain 总量的 1.5-2 倍**：配不够 retain 写一半失败，FB 不报错。
- **存储介质必须 CF**：CX9020-U900 出厂 CF，不要外挂硬盘——电容支撑不到磁头到位。
- **默认参数不要改**：`ePersistentMode` 必须保持 `SPDM_2PASS`，`eUpsMode` 默认值在 95% 工厂适用。
- **`tRecoverTime` 必须略长于 UPS 最大保持时间**（PDF 明确）：默认 `T#10s` 对 CX9020-U900 + 标配 UPS 够用；非标配置才需要重算。
- **多 runtime 时 `iPLCPort` 显式填**（工程经验补充）：单 runtime 让 FB 自动探测；多 runtime 工程建议显式 `851`/`852`/`853` 避免上电探测顺序不稳。
- **每周期都要调**：不要塞 IF / CASE 里。漏几个周期就漏一次电压采样。
- **不要自己调 `FB_NT_QuickShutdown`**（工程经验补充）：PDF 警告会导致数据丢失。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_S_UPS_CX9020_U900.xml`](../examples/P_Demo_FB_S_UPS_CX9020_U900.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：某 CX9020-U900 控制器装在远程泵站本地控制柜，监视水位 + 控制变频泵。
//       掉电时要保留累计运行时间 tPumpRunTimeRetain 和当前模式枚举 eModeRetain，
//       重启后能从上次状态继续。1-second UPS 提供 ~2 秒写盘 + 关机窗口。
//
// 价值：CX9020-U900 上 UPS 状态由 FB 内部读取（不暴露 iUPSPort），业务侧只
//       要每周期调一次 + 看 eUpsState 即可。不用本 FB 要自己用 ADS 读 UPS
//       寄存器 + 写双段持久化 + 调 QuickShutdown，约 70-90 行手写代码。
//
// 验证：登录运行 → 在线把 tPumpRunTimeRetain 改到非零 → 模拟掉电（台架拔 24V）
//       → 观察 eUpsState 走过 eSUPS_PowerFailure → eSUPS_WritePersistentData
//       → eSUPS_QuickShutdown → 系统重启 → 上电后 tPumpRunTimeRetain 仍在。
PROGRAM P_Demo_FB_S_UPS_CX9020_U900
VAR
    fbSUPS                : FB_S_UPS_CX9020_U900;
    tPumpRunTimeRetain    : TIME;            // 工程里加 RETAIN
    eModeRetain           : INT;             // 1=Manual, 2=Auto, 3=Maintenance
    bPowerFailNow         : BOOL;
    eUpsState             : E_S_UPS_State;
END_VAR
// 全部 PDF 推荐默认；CX9020-U900 平台不应改动
fbSUPS(
    sNetID           := '',
    iPLCPort         := 0,
    tTimeout         := DEFAULT_ADS_TIMEOUT,
    eUpsMode         := eSUPS_WrPersistData_Shutdown,
    ePersistentMode  := SPDM_2PASS,
    tRecoverTime     := T#10s,
    bPowerFailDetect => bPowerFailNow,
    eState           => eUpsState
);
```

## 7. 业务场景与实际价值

- **场景**：CX9020-U900 是 Beckhoff 低端嵌入式（ARM Cortex-A8）+ 1-second UPS 的搭配，多用在远程泵站、风电场单元控制、小型水处理工艺这类工程预算紧、停机损失大的现场。掉电时要保住「累计运行时间 / 设备模式 / 工艺步骤」等 retain 量。
- **价值**：用 vs 不用的差别就是「重启后变频泵能从掉电前的累计 1234h 继续」vs「重启后变频泵累计清零，需要现场工程师拷贝运维记录回填」。技术层面省下读 UPS 寄存器代码（CX9020-U900 内部寄存器路径与其它 CX 不同）、双段持久化触发、QuickShutdown 调度共约 70-90 行。
- **替代方案对比**：
  - **不用 UPS**：掉电瞬间所有 retain 实际未写盘，重启后回到上电默认
  - **手写 ADS 读 UPS + 自调 QuickShutdown**：能做，但 CX9020-U900 上 UPS 寄存器路径与 CX50x0/CX51x0 不同，需要单独适配
  - **本 FB**：Beckhoff 维护，针对 CX9020-U900 平台已经把读 UPS 的路径写死，业务无感知
- **与其它平台版的取舍**：移植到 CX5x 系列时要把 FB 类型换为对应版本并补一个 `iUPSPort` 参数（CX50x0 用 `16#4A8`，CX51x0 用 `16#588`）；业务代码的 retain 声明 + `eUpsMode` / `tRecoverTime` 部分保持不变。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §4.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/2250162827.html
- **相关枚举**：`E_S_UPS_Mode`（PDF §5.1）、`E_S_UPS_State`（PDF §5.2）
- **相关 FB**：`FB_NT_QuickShutdown`（本 FB 内部使用）、其它平台变体（`FB_S_UPS_CB3011`、`FB_S_UPS` / CX50x0、`FB_S_UPS_CX51x0`、`FB_S_UPS_BAPI`）
