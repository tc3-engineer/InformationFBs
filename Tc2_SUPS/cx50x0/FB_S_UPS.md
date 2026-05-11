# FB_S_UPS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `CX50x0` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/27021597794721547.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_S_UPS.xml`](../examples/P_Demo_FB_S_UPS.xml) |

---

## 1. 功能简述

`FB_S_UPS` 是面向 **CX50x0 嵌入式控制器（CX5010 / CX5020）+ 1-second UPS** 的「断电保护管家」。它每个 PLC 周期被调用一次，通过指定的 `iUPSPort`（默认 `16#4A8`，即 ADS 端口 1192）读取主板上 1-second UPS 状态；一旦检测到供电异常，按 `eUpsMode` 自动**用 `SPDM_2PASS` 把 retain 数据写入 Compact Flash** 并**调用内部 `FB_NT_QuickShutdown` 让 TwinCAT 在剩余几秒内安全断电**。

CX50x0 平台与 CB3011 最大的接口差异是多出一个 `iUPSPort` 输入：CX50x0 上 UPS 状态来自一个独立的 ADS 设备（端口 `16#4A8`），这与 CB3011 的"直接读主板 GPIO"路径不同。其它参数和行为与 CB3011 版完全对齐。

**默认输入值由 Beckhoff 针对 CX50x0 调好，不应改动**；并且若运行在 Windows Embedded Standard 7P 上，必须打开 EWF 或 FBWF 之一，并确保 `TwinCAT\Boot` 文件夹位于不被写过滤的分区里，否则 retain 会写到 RAM 覆盖层，掉电后照样丢。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId:= ''; (* '' = local netid *)
    iPLCPort        : UINT; (* PLC Runtime System for writing persistent data *)
    iUPSPort        : UINT := 16#4A8; (* Port for reading Power State of UPS, dafault 16#4A8 *)
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT; (* ADS Timeout *)
    eUpsMode        : E_S_UPS_Mode := eSUPS_WrPersistData_Shutdown; (* UPS mode (w/wo writing persistent data, w/wo shutdown) *)
    ePersistentMode : E_PersistentMode := SPDM_2PASS; (* mode for writing persistent data *)
    tRecoverTime    : TIME := T#10s; (* ON time to recover from short power failure in mode eSUPS_WrPersistData_NoShutdown/eSUPS_CheckPowerStatus *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | `''` | 控制器的 AmsNetId 字符串。空串 `''` 表示本机；跨机控制 UPS 在本平台无意义 |
| `iPLCPort` | `UINT` | — | 写 retain 时寻址的 PLC runtime 端口：第一个 runtime 是 `851`、第二个 `852` …… 填 `0` 让 FB 自动探测 |
| `iUPSPort` | `UINT` | `16#4A8` | 读取 UPS 状态使用的 ADS 端口，CX50x0 默认为 `16#4A8`（十进制 1192）。**除非 Beckhoff 平台手册明确写要换，否则不要动** |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 写 retain / 触发 quick shutdown 的 ADS 超时；保持默认即可 |
| `eUpsMode` | `E_S_UPS_Mode` | `eSUPS_WrPersistData_Shutdown` | UPS 工作模式：是否写 retain、是否关机。默认是「写 retain 后立刻关机」，即生产环境最常用 |
| `ePersistentMode` | `E_PersistentMode` | `SPDM_2PASS` | 写 retain 的模式。**必须 `SPDM_2PASS`**，其它模式来不及。可能造成短暂 real-time violation，这是设计上接受的代价 |
| `tRecoverTime` | `TIME` | `T#10s` | 「无关机」模式下电压恢复后多久才回 `eSUPS_PowerOK`。**必须大于电容最大充电时间**，否则短时连续掉电会让电容来不及回满 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bPowerFailDetect  : BOOL; (* TRUE while powerfailure is detected *)
    eState            : E_S_UPS_State := eSUPS_PowerOK; (* current ups state *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bPowerFailDetect` | `BOOL` | — | 实时电源标志：掉电中为 `TRUE`，恢复后立即 `FALSE`。瞬时位，不反映 FB 内部状态机是否还在收尾 |
| `eState` | `E_S_UPS_State` | `eSUPS_PowerOK` | FB 当前所处的状态机阶段（见 §4），业务侧观察这个即可 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约定**：必须每个 PLC 周期调用一次。FB 内部按 `iUPSPort` 周期性读 UPS 状态；漏调一次就漏掉一个采样点。

**与 CB3011 版的差异**：除了多一个 `iUPSPort` 之外，状态机和模式语义完全一致。可以把 CX50x0 看作"读 UPS 状态的方式从直接 GPIO 改成 ADS 端口 `16#4A8`"的同款 FB。

**eUpsMode 决定的四种工作流**：

1. **`eSUPS_WrPersistData_Shutdown`（默认）**：检测掉电 → `eState := eSUPS_WritePersistentData` 用 `SPDM_2PASS` 把 retain 推到 CF → 完成后 `eState := eSUPS_QuickShutdown` 触发系统重启 → `eSUPS_WaitForPowerOFF` 等电容耗尽。生产现场最常用。
2. **`eSUPS_WrPersistData_NoShutdown`**：只写 retain 不关机，写完进 `eSUPS_WaitForRecover`，`tRecoverTime` 内电压恢复则回 `eSUPS_PowerOK`，否则继续等。适合「短时晃电也要存但不允许停产」。
3. **`eSUPS_ImmediateShutdown`**：跳过 retain，直接 quick shutdown。用于"全是过程量、断电直接重启即可"。
4. **`eSUPS_CheckPowerStatus`**：纯监视，只把 `bPowerFailDetect`/`eState` 报出来，业务自己决策。`tRecoverTime` 过后才回 `eSUPS_PowerOK`。

**Windows Embedded Standard 7P 上的额外要求**（PDF 明确）：必须打开写过滤器之一：
- 用 **EWF（Enhanced Write Filter）**：`TwinCAT\Boot` 文件夹必须放在**不受 EWF 保护**的分区上（注册表里查 `HKEY_LOCAL_MACHINE\SOFTWARE\Beckhoff\TwinCAT\System\BootPrjPath`）
- 用 **FBWF（File Based Write Filter）**：必须在 Beckhoff FBWF Manager 的 Exclusion Settings 把 `TwinCAT\Boot` 排除

否则 retain 写入会被写过滤器拦在 RAM 覆盖层，重启后照样丢。

**关键时序约束**：1-second UPS 容量只够数秒；retain 必须 `SPDM_2PASS`，Router Memory 必须配足；本 FB 内部已经组合了 retain 写入 + QuickShutdown 的正确顺序，**业务不要自己再调 `FB_NT_QuickShutdown`**。

## 4. 错误码 / 返回值

本 FB 不暴露 `bError` / `nErrID` 输出。运行状态全部体现在 `eState : E_S_UPS_State` 上，PDF §5.2 列出的取值：

| 取值 | 含义 |
|---|---|
| `eSUPS_PowerOK` | 所有模式：供电正常 |
| `eSUPS_PowerFailure` | 所有模式：检测到掉电（仅一个周期，下一周期切到具体工作状态） |
| `eSUPS_WritePersistentData` | 在 `eSUPS_WrPersistData_Shutdown` 或 `eSUPS_WrPersistData_NoShutdown` 模式下：正在写 retain |
| `eSUPS_QuickShutdown` | 在 `eSUPS_WrPersistData_Shutdown` 或 `eSUPS_ImmediateShutdown` 模式下：quick shutdown 执行中 |
| `eSUPS_WaitForRecover` | 在 `eSUPS_WrPersistData_NoShutdown` 或 `eSUPS_CheckPowerStatus` 模式下：等电压恢复 |
| `eSUPS_WaitForPowerOFF` | 在 `eSUPS_WrPersistData_Shutdown` 或 `eSUPS_ImmediateShutdown` 模式下：等 UPS 电容耗尽 |

⚠️ PDF 与 InfoSys 均未列具体错误号表；retain 写入失败、ADS 读 `iUPSPort` 失败等故障**不通过本 FB 输出**，只能通过 retain 缺失、SYSLOG 或 TwinCAT Event Viewer 间接发现。

## 5. 使用注意 / 常见坑

- **写过滤器（EWF/FBWF）配置必须正确**：CX50x0 默认装 Windows Embedded Standard 7P 时通常启用了写过滤器以保护 OS 分区；如果忘记把 `TwinCAT\Boot` 排除，retain 写到 RAM 覆盖层，重启后 100% 丢失，而 FB **不会报错**。
- **`iUPSPort` 不要乱改**：CX50x0 上默认 `16#4A8`（1192）；只在 Beckhoff 平台手册或 TwinCAT 系统管理器明示更换的情况下才动。
- **Router Memory 必须预留够**：retain 总量的 1.5-2 倍。配不够 → 写一半失败 → 重启后部分变量缺失。
- **存储介质必须是 Compact Flash**：CX50x0 出厂用 CF，不要外挂硬盘期望 retain 写过去——电容支撑不到磁头到位。
- **默认参数不要改**：`ePersistentMode` 尤其不要换成 `SPDM_2PASS` 以外的；`eUpsMode` 默认值适合 95% 工厂。
- **多 runtime 时 `iPLCPort` 要显式填**（工程经验补充）：单 runtime 工程可以让 FB 自动探测；但工程上跑 2-3 个 runtime 时建议显式填 `851`/`852`/`853` 避免上电瞬间探测顺序不稳定。
- **FB 必须每周期都调用**：不要塞 IF 分支或 CASE 状态机中；漏几个周期就可能错过电压跌落瞬间。
- **不要自己调 `FB_NT_QuickShutdown`**（工程经验补充）：PDF 警告会导致数据丢失。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_S_UPS.xml`](../examples/P_Demo_FB_S_UPS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：某 CX5020 嵌入式控制器跑 PLC + HMI（CE 嵌入），断电时要保存
//       班次产量计数器 nProductCountRetain 和当前工序号 iStepNoRetain。
//       1-second UPS 给我们 ~2 秒窗口完成写盘 + 关机。
//
// 价值：CX50x0 的 UPS 状态来自 ADS 端口 16#4A8，不用本 FB 要自己写：
//       ADS 客户端 → 读端口 → 解析状态字 → SPDM_2PASS 触发 → 等回执 →
//       FB_NT_QuickShutdown → 超时保底。封装后业务只看 eUpsState 走势。
//
// 验证：登录运行 → 在线把 nProductCountRetain 加到非零 → 模拟掉电（拔 24V，
//       台架无负载下） → 观察 eUpsState 走 eSUPS_WritePersistentData →
//       eSUPS_QuickShutdown → 系统重启 → 上电后 nProductCountRetain 仍在。
PROGRAM P_Demo_FB_S_UPS
VAR
    fbSUPS                  : FB_S_UPS;
    nProductCountRetain     : UDINT;       // 工程里加 RETAIN 限定
    iStepNoRetain           : INT;
    bPowerFailNow           : BOOL;
    eUpsState               : E_S_UPS_State;
END_VAR
// 全部 PDF 默认；CX50x0 上不应改动
fbSUPS(
    sNetID           := '',
    iPLCPort         := 0,
    iUPSPort         := 16#4A8,
    tTimeout         := DEFAULT_ADS_TIMEOUT,
    eUpsMode         := eSUPS_WrPersistData_Shutdown,
    ePersistentMode  := SPDM_2PASS,
    tRecoverTime     := T#10s,
    bPowerFailDetect => bPowerFailNow,
    eState           => eUpsState
);
```

## 7. 业务场景与实际价值

- **场景**：CX5010 / CX5020 工控机在装配线、印刷设备、CNC 上位机这类场景，掉电时要保住「班次累计 / 当前工序号 / 配方参数」等 retain 量。CX50x0 多数装 Windows Embedded Standard 7P 并配了 1-second UPS 模块，是 Beckhoff 中端嵌入式控制器的主力组合。
- **价值**：用 vs 不用的差别就是「重启后状态机能从掉电前的工序号继续」vs「重启后回到上电默认 → 整批料要重做或人工对单」。技术层面省下：读 ADS UPS 端口的客户端代码、双段持久化触发、QuickShutdown 调度，约 70-90 行手写 + 边界测试。
- **替代方案对比**：
  - **不用 UPS**：掉电瞬间所有非 retain 数据丢；即使带 retain 关键字，没及时写盘也是空话
  - **手写 ADS 客户端 + 手写 QuickShutdown**：能做，但容易在「retain 还没刷完就触发关机」上踩坑，造成 CF 卡上 retain 文件损坏
  - **本 FB**：Beckhoff 官方维护，已经处理了写过滤器、连续掉电、`tRecoverTime` 超时等边界
- **与 CB3011 版的取舍**：换平台时只要改 FB 类型 + 增删 `iUPSPort` 参数，业务代码其它部分（`eUpsMode` / `tRecoverTime` 等）可保持一致。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §4.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/27021597794721547.html
- **相关枚举**：`E_S_UPS_Mode`（PDF §5.1）、`E_S_UPS_State`（PDF §5.2）
- **相关 FB**：`FB_NT_QuickShutdown`（本 FB 内部使用，不可直接调用）、其它平台变体（`FB_S_UPS_CB3011`、`FB_S_UPS_CX51x0`、`FB_S_UPS_CX9020_U900`、`FB_S_UPS_BAPI`）
