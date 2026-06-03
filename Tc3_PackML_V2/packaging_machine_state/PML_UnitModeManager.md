# PML_UnitModeManager

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Packaging Machine State` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/1336429067.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_PML_UnitModeManager.TcPOU`](../examples/P_Demo_PML_UnitModeManager.TcPOU) |

---

## 1. 功能简述

`PML_UnitModeManager` 是 **PackML UnitMode 切换管理器**。在 PackML 标准中机器除了"状态"还有"模式"——生产模式、维护模式、手动模式以及通过 `PML_UnitModeConfig` 注册的自定义模式。每个模式有自己的允许切换状态集（"在哪些 PML 稳态可以切模式"）。本 FB 负责响应 HMI 的模式切换请求，按规则判断是否允许、执行切换、回报新模式名称。

警告（PDF 直译）：模式之间的切换逻辑（特别是 Manual → Production）依赖于具体应用，可能需要硬件互锁或安全设备配合。模式切换的安全性由实现者负责。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute        : BOOL;
    eModeCommand    : DINT;
    ePMLState       : E_PMLState;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次模式切换尝试 |
| `eModeCommand` | `DINT` | - | 请求切换到的目标 UnitMode 编号（1=Production / 2=Maintenance / 3=Manual / 4-31=自定义）|
| `ePMLState` | `E_PMLState` | - | 当前 PackML 自动状态机的状态，本 FB 据此判断当前态是否允许切模式 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    eModeStatus     : DINT;
    sModeStatus     : STRING;
    bDone           : BOOL;
    bError          : BOOL;
    bErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eModeStatus` | `DINT` | 当前生效的 PML UnitMode 编号（切换成功后变为 `eModeCommand`，失败保持原值）|
| `sModeStatus` | `STRING` | 当前 UnitMode 名称字符串（如 'Production' / 'Maintenance' / 'Cleaning'）|
| `bDone` | `BOOL` | 切换成功完成时为 TRUE |
| `bError` | `BOOL` | 出错时置 TRUE（不允许在当前态切、目标模式未注册等）|
| `bErrorID` | `UDINT` | `bError = TRUE` 时给出错误号 |

> **PDF 文档命名小瑕疵**：PDF 输出表第 5 行写的 `nErrorID`、变量声明里写的 `bErrorID`（首字母 `b` 通常表示 BOOL，但这里类型是 UDINT，疑为 PDF 文档笔误）。VAR_OUTPUT 声明以 `bErrorID : UDINT` 为准。

### VAR_IN_OUT

无。

## 3. 行为说明

`PML_UnitModeManager` 把"模式切换"从主状态机里独立出来，让模式切换规则集中维护。

**触发语义**：`bExecute` **上升沿**触发一次切换尝试——`bExecute := TRUE` 持续期间只触发一次。这与 PackML 命令的电平触发不同，目的是防止 HMI 按钮被多次响应。

**判定逻辑**：收到上升沿后，本 FB 读取当前 `ePMLState`，查询：(a) 当前状态是否在请求模式的允许切换状态集（基础模式 Production/Maintenance/Manual 各有内建图，自定义模式由 `PML_UnitModeConfig` 配置）；(b) 目标 `eModeCommand` 是否已注册。两条都满足才切换。

**切换成功路径**：`eModeStatus := eModeCommand` → `sModeStatus` 改为对应名称（基础模式名是 'Production' / 'Maintenance' / 'Manual'，自定义模式来自 PML_UnitModeConfig.sName）→ `bDone := TRUE`（保持一个周期供 HMI latch）。`PML_StateMachine` 读到 `eMode` 变化后会按新模式的状态集运行。

**切换失败路径**：`bError := TRUE` + `bErrorID` 给出错误号；`eModeStatus / sModeStatus` 保持原值不动。常见失败：当前态不在允许列表（如 Production 模式在 Execute 态切到 Maintenance 被拒，必须先 Stop 到 Stopped）、目标模式未注册（HMI 发了未配置的 4-31 编号）。

**典型用法**：在主程序里实例化本 FB；HMI 模式选择按钮按下时设 `eModeCommand := 期望编号` 并把按钮信号送到 `bExecute`；用输出 `eModeStatus` 喂回 `PML_StateMachine.eMode`。

**典型陷阱**：忘记把 `eModeStatus` 馈给 `PML_StateMachine.eMode` 会导致状态机继续按旧模式运行；`bExecute` 用电平而非上升沿触发会重复切换；自定义模式没先调 `PML_UnitModeConfig` 注册就发 `eModeCommand` 会失败。

## 4. 错误码 / 返回值

PDF 标注 `bErrorID` 在 `bError = TRUE` 时给出错误号。PDF + InfoSys 均未列具体码值。

常见出错场景：

| 出错场景 | 含义 | 处理建议 |
|---|---|---|
| 当前 `ePMLState` 不允许切模式 | 如 Production 在 Execute 切到 Manual 通常被拒 | 先 Stop 到允许切换的稳态再切 |
| 目标 `eModeCommand` 未注册 | 自定义模式没先调 PML_UnitModeConfig | 注册后再尝试 |
| `eModeCommand` = 0 或 > 31 | 不合法编号 | 检查 HMI 映射 |

⚠️ 待人工确认：具体 `bErrorID` 数值与含义 PDF + InfoSys 均未列。

## 5. 使用注意 / 常见坑

- `bExecute` 是**上升沿**触发——`TRUE` 持续期间只触发一次，需要再次切换必须先 FALSE 再 TRUE。
- 自定义模式（4-31）必须先调 `PML_UnitModeConfig` 注册，否则本 FB 无法切到。
- 输出 `eModeStatus` 必须被馈给 `PML_StateMachine.eMode`——本 FB 自己不会去改状态机的 eMode。（工程经验补充）
- Manual → Production 的切换在 PDF 中专门警告：依赖硬件互锁/安全设备配合，HMI 切换前需检查安全门、双手按钮等。
- `sModeStatus` 字符串可直接绑定 HMI 文本框，操作员能立即看到当前模式名。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PML_UnitModeManager.TcPOU`](../examples/P_Demo_PML_UnitModeManager.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台食品包装机在生产期间需要切到 "Maintenance" 模式做日常清洁。操作员在 Production 模式 Execute 态点 "Stop" → 状态机进入 Stopped → 操作员选择 Maintenance 并按"切换模式"按钮 → `PML_UnitModeManager` 检查 Stopped 允许切换 → 切到 Maintenance；维护完成后用类似流程切回 Production。
- **价值**：模式切换规则集中维护、由 FB 强制执行，避免出现 "操作员在执行中切到 Manual 模式导致联动安全失效" 这种事故。`bError` 拒绝后 HMI 可立即提示用户"请先停机再切"。所有切换路径符合 ISA-TR88 标准。
- **替代方案对比**：自己在主 POU 里写 IF/CASE 检查切模式条件——容易遗漏组合、不同设备实现不一致、自定义模式硬编码代码量大。本 FB 配合 `PML_UnitModeConfig` 把规则配置化，硬件升级（多一个模式）只需注册不改主程序。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/1336429067.html
- **相关**：`PML_StateMachine`（消费本 FB 输出的 eMode）、`PML_UnitModeConfig`（注册自定义模式）、`E_PMLProtectedUnitMode`（基础模式枚举）、`F_UnitModeToString`（按 eMode 反查模式名）

## 9. 待确认项 (⚠️)

- `bErrorID` 数值与含义映射：PDF + InfoSys 均未列。
- PDF 输出表头第 5 行写 `nErrorID`、变量声明写 `bErrorID`（类型 UDINT）；命名不一致疑为 PDF 笔误，以 VAR_OUTPUT 为准。
