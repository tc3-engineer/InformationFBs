# FB_S_UPS_BAPI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `BAPI` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/3716524299.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_S_UPS_BAPI.xml`](../examples/P_Demo_FB_S_UPS_BAPI.xml) |

---

## 1. 功能简述

`FB_S_UPS_BAPI` 是面向 **任意支持 Beckhoff BIOS-API v1.15+ 的工控机 + 1-second UPS** 的「通用版断电保护管家」。它通过 BIOS-API（而非平台特定的 ADS 端口）读取 UPS 状态，因此**不依赖于具体的 CB/CX 型号**——CX52x0、CX9240 等新平台只要 BIOS-API ≥ 1.15 就能用同一个 FB。

工作流程：FB 首次被调用时通过 BIOS-API 探测 1-second UPS 的访问参数（耗费数个 PLC 周期），探测完成后开始循环检查电源；下一次写 retain 时把 BIOS 访问参数一起持久化保存，以后开机就不用再探测，PLC 启动后立刻能监视电源。电源检查的轮询频率是动态的：**掉电中每 50 ms 检查一次电容剩余；有电但电容 < 90% 时每 200 ms 检查一次；有电且电容 ≥ 90% 时每秒一次**——这样既保证应急响应快，又不浪费正常运行时的资源。

相比平台特定版（CB3011 / CX50x0 / CX51x0 / CX9020-U900），**BAPI 版多了 4 个输出**：`nCapacity`（电容剩余百分比）、`bBusy`（FB 处于活动期）、`bError`（错误标志）、`nErrID`（错误号）。这让业务可以监视电容老化、捕获错误，是新工程首选的版本。

**默认输入值由 Beckhoff 调好，不应改动**。

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
| `sNetID` | `T_AmsNetId` | `''` | 控制器 AmsNetID。空串表示本机；BAPI 路径仅本机有效 |
| `iPLCPort` | `UINT` | — | 写 retain 时寻址的 PLC runtime 端口（`851`/`852`/……）。填 `0` 让 FB 自动探测 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 写 retain / 触发 quick shutdown 的 ADS 超时 |
| `eUpsMode` | `E_S_UPS_Mode` | `eSUPS_WrPersistData_Shutdown` | UPS 工作模式：是否写 retain、是否关机。默认是「写 retain 后立刻关机」 |
| `ePersistentMode` | `E_PersistentMode` | `SPDM_2PASS` | 写 retain 的模式。**必须 `SPDM_2PASS`**（fast 2-pass） |
| `tRecoverTime` | `TIME` | `T#10s` | 「无关机」模式下电压恢复后多久才回 `eSUPS_PowerOK`。PDF 原文「somewhat longer than the maximum holding time of the UPS」——必须略长于 UPS 最大保持时间，确保电容充满 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bPowerFailDetect  : BOOL; (* TRUE while powerfailure is detected *)
    eState            : E_S_UPS_State; (* current ups state *)
    nCapacity         : BYTE; (* actual capacity of UPS *)
    bBusy             : BOOL; (* TRUE: function block is busy *)
    bError            : BOOL; (* FALSE: function block has error *)
    nErrID            : UDINT; (* FB error ID *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bPowerFailDetect` | `BOOL` | 实时电源标志：掉电中 `TRUE`，恢复后立即 `FALSE` |
| `eState` | `E_S_UPS_State` | FB 当前状态机阶段（见 §4），**与其它版本不同的是 BAPI 版不带默认 `eSUPS_PowerOK`**，初始为枚举第一个值；正常初始化几个周期后会变成 `eSUPS_PowerOK` |
| `nCapacity` | `BYTE` | 电容剩余电量百分比（0..100%）。用于监视 UPS 电容老化：长期运行后某时段电量始终上不到 100% 就是电容衰减信号 |
| `bBusy` | `BOOL` | FB 处于活动期（探测访问参数、写 retain、调 QuickShutdown 等）时为 `TRUE` |
| `bError` | `BOOL` | **PDF 原文「FALSE if an error has occurred」**——注意 PDF 这里描述与命名习惯相反；按 InfoSys 与实践理解，`bError = TRUE` 表示出错（PDF 表述疑似笔误，已上报待 Beckhoff 修正） |
| `nErrID` | `UDINT` | 错误号（仅当 `bError` 指示出错时有意义）。具体取值表 PDF 与 InfoSys 均未列出 ⚠️ |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约定**：每个 PLC 周期调用一次。BAPI 版的首次调用与后续调用行为不同——

**首次调用（仅启动后第一次）**：FB 通过 BIOS-API 探测 1-second UPS 的访问参数，期间 `bBusy = TRUE`，状态 `eState` 在初始几个枚举值上停留几个周期。探测完成后才进入正常监视循环。**这意味着 PLC 启动后的前几个周期 `bPowerFailDetect` 不可信**——业务侧应该等 `eState = eSUPS_PowerOK` 后再相信电源监视输出。

**首次写 retain 时**：FB 把刚才探测到的 BIOS 访问参数和 retain 一起存盘，下次开机就不再探测，启动即可立刻监视。

**动态轮询频率**（PDF 明确）：
- **掉电中**：每 50 ms 检查一次电容剩余（应急路径，必须快）
- **有电 + 电容 < 90%**：每 200 ms 检查（正在充电，关注一下）
- **有电 + 电容 ≥ 90%**：每秒一次（稳态，省资源）

**eUpsMode 决定的四种工作流**（与其它平台版完全一致）：

1. **`eSUPS_WrPersistData_Shutdown`（默认）**：掉电 → `eState := eSUPS_WritePersistentData` 用 `SPDM_2PASS` 推 retain → `eState := eSUPS_QuickShutdown` 调用 `FB_NT_QuickShutdown` → `eSUPS_WaitForPowerOFF` 等电容耗尽。
2. **`eSUPS_WrPersistData_NoShutdown`**：只写 retain 不关机，进 `eSUPS_WaitForRecover` 等电压恢复。
3. **`eSUPS_ImmediateShutdown`**：跳过 retain 直接 quick shutdown。
4. **`eSUPS_CheckPowerStatus`**：纯监视模式。

**与平台特定版的关键差异**：
- 有 `bBusy` / `bError` / `nErrID` 输出（其它版没有）→ 可以从代码里捕获 BAPI 调用失败、retain 写失败等错误
- 有 `nCapacity` → 可以做电容老化预警
- 不需要平台特定的 `iUPSPort`（CX50x0/CX51x0 才需要）
- 启动后前几个周期处于探测阶段，输出未就绪

## 4. 错误码 / 返回值

`eState : E_S_UPS_State` 取值（PDF §5.2）：

| 取值 | 含义 |
|---|---|
| `eSUPS_PowerOK` | 所有模式：供电正常 |
| `eSUPS_PowerFailure` | 所有模式：检测到掉电（仅一个周期） |
| `eSUPS_WritePersistentData` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_WrPersistData_NoShutdown` 模式下：正在写 retain |
| `eSUPS_QuickShutdown` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_ImmediateShutdown` 模式下：quick shutdown 执行中 |
| `eSUPS_WaitForRecover` | `eSUPS_WrPersistData_NoShutdown` / `eSUPS_CheckPowerStatus` 模式下：等电压恢复 |
| `eSUPS_WaitForPowerOFF` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_ImmediateShutdown` 模式下：等 UPS 电容耗尽 |

**错误输出**：`bError` 出错时为高 + `nErrID` 给出错误号。⚠️ PDF §4.5.1 与 InfoSys topic 3716524299 均未列具体 `nErrID` 取值表；常见错误推测包括 BIOS-API 不可用（platform 不支持 BAPI v1.15+）、ADS 写 retain 超时、QuickShutdown 触发失败等。业务侧应记录 `nErrID` 配合 Beckhoff 支持现场诊断。

**PDF 表述笔误提醒**：`bError` 的 PDF 描述是「FALSE if an error has occurred」（出错时为 FALSE），这与 IEC 61131 命名习惯相反；按 InfoSys 与实际固件行为，应理解为「`TRUE` 表示出错」。本字段在程序里应作 `IF bError THEN ...` 处理。

## 5. 使用注意 / 常见坑

- **`bError` 语义与 PDF 字面相反**：PDF 写「FALSE if an error has occurred」是笔误，正确语义是 `TRUE = 错误`。业务代码按 `IF bError THEN` 处理（与所有标准 Beckhoff 错误位一致）。
- **启动后前几个周期 `bPowerFailDetect` 不可信**：FB 在通过 BIOS-API 探测 UPS；业务侧要等 `eState = eSUPS_PowerOK` 或 `bBusy = FALSE` 后再判断电源。
- **平台 BIOS-API 必须 ≥ v1.15**：在 BIOS 设置或 Beckhoff 系统诊断里查；版本太低就只能用平台特定版（CB3011 / CX50x0 / CX51x0 / CX9020_U900）。
- **`nCapacity` 用来做电容老化监控**：新电容长期能稳定到 100%，老化后会停在 85-90% 之间。HMI 上加一个长期最大值 trend 能预警换板。
- **Router Memory 配到 retain 总量的 1.5-2 倍**：配不够 retain 写一半失败，FB 通过 `bError`/`nErrID` 报。
- **多 runtime 时 `iPLCPort` 显式填**（工程经验补充）：单 runtime 可让 FB 自动探测；多 runtime 工程建议显式 `851`/`852`/`853`。
- **每周期都要调**：不要塞 IF / CASE 里。漏几个周期错过电压跌落瞬间。
- **不要自己调 `FB_NT_QuickShutdown`**（工程经验补充）：PDF 警告会导致数据丢失。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_S_UPS_BAPI.xml`](../examples/P_Demo_FB_S_UPS_BAPI.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：某新型 CX52x0 控制器（BIOS-API v1.18）做 SCADA 网关，断电时要保存
//       最近一次 OPC UA 客户端配置 sLastClientConfigRetain 和已发送报文计数
//       nMsgSentRetain。BAPI 版还提供电容老化告警（nCapacity < 90 持续报）。
//
// 价值：BAPI 版不依赖具体型号 → 后续硬件升级可保持同一段代码。多了 nCapacity
//       让电容老化能在 HMI 上做趋势预警；多了 bError/nErrID 让代码可捕获故障。
//
// 验证：登录运行 → 等 eUpsState = eSUPS_PowerOK 并 bUpsBusy = FALSE（启动
//       探测完成）→ 在线把 nMsgSentRetain 改到非零 → 模拟掉电 → 观察
//       eUpsState 走 eSUPS_PowerFailure → eSUPS_WritePersistentData →
//       eSUPS_QuickShutdown → 系统重启 → 上电后 nMsgSentRetain 仍在。
//       同时观察 nCapacityPct 值范围 80-100。
PROGRAM P_Demo_FB_S_UPS_BAPI
VAR
    fbSUPS                   : FB_S_UPS_BAPI;
    sLastClientConfigRetain  : STRING(80);   // 工程里加 RETAIN
    nMsgSentRetain           : UDINT;
    bPowerFailNow            : BOOL;
    eUpsState                : E_S_UPS_State;
    nCapacityPct             : BYTE;          // 0..100
    bUpsBusy                 : BOOL;
    bUpsError                : BOOL;          // TRUE = 错误（PDF 描述笔误）
    nUpsErrID                : UDINT;
END_VAR
fbSUPS(
    sNetID           := '',
    iPLCPort         := 0,
    tTimeout         := DEFAULT_ADS_TIMEOUT,
    eUpsMode         := eSUPS_WrPersistData_Shutdown,
    ePersistentMode  := SPDM_2PASS,
    tRecoverTime     := T#10s,
    bPowerFailDetect => bPowerFailNow,
    eState           => eUpsState,
    nCapacity        => nCapacityPct,
    bBusy            => bUpsBusy,
    bError           => bUpsError,
    nErrID           => nUpsErrID
);
```

## 7. 业务场景与实际价值

- **场景**：BAPI 版是 Beckhoff 推给所有「平台无关」工程的首选版本。典型用例：① 新硬件 CX52x0/CX9240 这类未来款（其 ADS 端口可能与现有 CX 不同，但 BIOS-API 接口稳定）② 设备厂同一份 PLC 代码要部署到不同 CX 型号上 ③ 工程要求能捕获 retain 写失败 / 电容老化等故障。
- **价值**：用 vs 不用比平台版多出三个收益：
  1. **跨平台代码可移植**——不用为每个新 CX 型号换一次 FB 类型
  2. **能监控电容老化**（`nCapacity`）——以前 UPS 电容衰减只能凭经验换板，现在能 HMI 趋势报警
  3. **错误可捕获**（`bError` / `nErrID`）——以前 retain 写失败无声，现在可以触发 OPC UA / E-Mail 告警
- **替代方案对比**：
  - **用平台特定版**（CB3011 / CX50x0 / CX51x0 / CX9020_U900）：能用但代码绑定型号，新硬件来了要换 FB；少 4 个有价值的输出
  - **手写 BIOS-API 调用**：能做但 BIOS-API 文档分散在多个 Beckhoff 平台手册里，工作量大且需自己实现"探测 → 持久化访问参数 → 动态轮询频率"全套逻辑
  - **本 FB**：Beckhoff 官方维护，BIOS-API 实现细节全部封装
- **限制**：仅在 BIOS-API ≥ v1.15 的平台上可用；老 CB3011 / 早期 CX50x0 仍需用平台特定版。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §4.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/3716524299.html
- **相关枚举**：`E_S_UPS_Mode`（PDF §5.1）、`E_S_UPS_State`（PDF §5.2）
- **相关 FB**：`FB_NT_QuickShutdown`（本 FB 内部使用）、平台特定变体（`FB_S_UPS_CB3011`、`FB_S_UPS` / CX50x0、`FB_S_UPS_CX51x0`、`FB_S_UPS_CX9020_U900`）
