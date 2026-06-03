# FB_PMLUnitModeManager

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Packaging Machine State` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003759883.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PMLUnitModeManager.TcPOU`](../examples/P_Demo_FB_PMLUnitModeManager.TcPOU) |

---

## 1. 功能简述

`FB_PMLUnitModeManager` 是 PackML V3 标准的 **UnitMode 切换管理器**，负责把"操作员请求切换模式"的命令转化为符合 PackML 状态机规则的实际切换动作。"Mode Manager" 决定机器在什么状态下可以切换 UnitMode（内置规则禁止机器在不合适的状态切换）。Production / Maintenance / Manual 三个基础模式的切换规则已预定义，其他自定义模式（4-31）的切换规则由配套的 `FB_PMLUnitModeConfig` 给出。

**V3 与 V2 的关键差异**：
- **FB 命名**：V2 叫 `PML_UnitModeManager`，V3 改名 `FB_PMLUnitModeManager`。
- **输出大改**：V2 只有 `bDone / bError / nErrorId`；V3 新增 `eModeStatus : DINT`（当前 UnitMode 编号）、`sModeStatus : STRING(80)`（当前 UnitMode 名称）——HMI 顶端"当前模式"标签直接绑这两个输出。
- **状态判定**：V3 加 `eState : E_PMLState` 作输入，让 Manager 实时知道状态机当前态，从而判断当前态是否允许切模式。

WARNING 注意（PDF 原文）：模式切换的具体逻辑取决于应用，特别是 Manual ↔ Production 之间的切换。可能需要硬件安全设备（如安全光幕、急停联锁）支持。模式切换的合规性责任在实施方。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute        : BOOL;
    eModeCommand    : DINT;
    eState          : E_PMLState;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次模式切换请求 |
| `eModeCommand` | `DINT` | - | 请求的目标 UnitMode 编号（1=Production / 2=Maintenance / 3=Manual / 4..31=自定义模式）|
| `eState` | `E_PMLState` | - | 当前 PML 状态机的状态（由 `FB_PMLStateMachine.eState` 给出），Manager 据此判断在当前态是否允许切模式 |

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

> ⚠️ **PDF 命名小瑕疵**：VAR_OUTPUT 段把变量声明为 `bErrorID : UDINT`，但描述段又叫做 `nErrorID`——PDF 内部命名不一致。以 `bErrorID`（VAR_OUTPUT 声明）为编程时实际名称（但语义其实是错误编号，名字以 b 开头有点误导，可能是 PDF 笔误）。⚠️ 实测以 PLC 编辑器为准。

| 名称 | 类型 | 说明 |
|---|---|---|
| `eModeStatus` | `DINT` | 当前 UnitMode 编号（V3 新增；HMI 顶端"当前模式"标签直接绑）|
| `sModeStatus` | `STRING` | 当前 UnitMode 名称（V3 新增；HMI 文本显示直接绑，省去 `F_PMLUnitModeToString` 反查）|
| `bDone` | `BOOL` | 模式切换成功完成时置 TRUE |
| `bError` | `BOOL` | 模式切换失败时置 TRUE |
| `bErrorID` | `UDINT` | `bError = TRUE` 时给出错误号（⚠️ PDF 命名 `bErrorID` 但描述写 `nErrorID`，实测为准）|

### VAR_IN_OUT

无。

## 3. 行为说明

`FB_PMLUnitModeManager` 在 `bExecute` 上升沿处理模式切换请求：

1. 检查请求的 `eModeCommand` 是否合法（基础模式 1-3，或已通过 `FB_PMLUnitModeConfig` 注册的自定义模式 4-31）；
2. 检查当前 `eState` 是否处于该模式允许切换的稳态（基础模式按 PackML 标准预定义；自定义模式按 `bEnableUnitModeChangeXxx` 配置）；
3. 满足条件 → 把当前 UnitMode 切到 `eModeCommand`、`bDone := TRUE`、`eModeStatus / sModeStatus` 反映新模式；
4. 不满足条件 → `bError := TRUE` + `bErrorID` 给出原因码；
5. 后续 `FB_PMLStateMachine` 通过 `eMode` 输入接收新模式（应用层把 `eModeStatus` 写到状态机 `eMode`）。

**PackML 标准切换规则**（基础模式）：
- Production ↔ Maintenance：通常在 Stopped 稳态切换；
- Production ↔ Manual：必须在 Stopped 切换，且可能需要硬件安全联锁；
- Maintenance ↔ Manual：同上。

具体规则由 PackML PDF §4.3.3 的"基础模式 + 切换图"定义；自定义模式由 `FB_PMLUnitModeConfig` 输入决定。

**典型用法**：HMI 模式下拉框选择某个模式（如 'Maintenance'），按"切换"按钮 → 应用层把按钮事件接 `bExecute`（用 R_TRIG 转脉冲）、把下拉框值接 `eModeCommand`、把 `FB_PMLStateMachine.eState` 接 `eState`；输出 `bDone` 接成功提示，`eModeStatus / sModeStatus` 接 HMI 顶端标签实时显示当前模式。

## 4. 错误码 / 返回值

PDF 标注 `bErrorID`（或描述里写的 `nErrorID`） 在 `bError = TRUE` 时给出错误号。PDF 未列具体码值。

常见出错场景：

| 出错场景 | 含义 | 处理建议 |
|---|---|---|
| `eModeCommand` 未注册 | 4-31 范围但没用过 `FB_PMLUnitModeConfig` 注册 | HMI 提示"未知模式"；先注册再切 |
| 当前 `eState` 不允许切模式 | 例如在 Execute 态切到 Maintenance（基础模式只允许 Stopped 切） | HMI 提示"请先停机再切模式" |
| 跨模式安全联锁未就位 | 如 Production → Manual 但安全光幕未触发 | HMI 提示"安全条件未满足"|

⚠️ 待人工确认：具体 `bErrorID` 数值映射 PDF 未列。

## 5. 使用注意 / 常见坑

- **`bExecute` 用上升沿触发**——电平触发会每周期重新请求切换。用 R_TRIG 把 HMI 按钮转成上升沿脉冲。（工程经验补充）
- 必须传当前 `eState`——本 FB 不自己读状态机，应用层须把 `FB_PMLStateMachine.eState` 接到本 FB 的 `eState` 输入。
- 模式切换可能涉及硬件安全（如急停联锁解除）——本 FB 只检查软件层规则，实际机械动作的安全责任在实施方。
- ⚠️ PDF 输出命名 `bErrorID` 与描述 `nErrorID` 不一致——以 PLC 编辑器实际声明为准。
- V3 新增 `eModeStatus / sModeStatus` 输出让 HMI 集成简洁——从 V2 升级时直接利用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PMLUnitModeManager.TcPOU`](../examples/P_Demo_FB_PMLUnitModeManager.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 上有"模式"下拉框 + "切换"按钮。操作员选择 'Maintenance' 后按按钮——本 FB 检查机器当前状态是否处于允许切换的稳态（如 Stopped），是则切到 Maintenance 模式让维护人员操作。如果机器在生产中（Execute 状态）按下，本 FB 拒绝切换并报错"请先停机"。
- **价值**：把"模式切换合法性检查"集中化——HMI 不需要自己写状态检查；切换规则由 `FB_PMLUnitModeConfig` 配置驱动；与 `FB_PMLStateMachine` 完美配合。V3 新增的 `eModeStatus / sModeStatus` 让 HMI 显示当前模式名一行代码搞定。
- **替代方案对比**：自己写状态检查 + 模式切换逻辑——容易遗漏分支（PackML V3 有 18 状态 × 31 模式 = 558 个条件）；本 FB 把规则封装好，HMI 只需"点下拉框 + 按按钮"。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003759883.html
- **相关**：`FB_PMLStateMachine`（提供 eState 输入；接 eModeStatus 输出作 eMode）、`FB_PMLUnitModeConfig`（注册自定义模式的切换规则）、`E_PMLState`、`E_PMLProtectedUnitMode`、`F_PMLUnitModeToString`（如不用 sModeStatus 可用本函数手工查名）

## 9. 待确认项 (⚠️)

- `bErrorID` 输出变量名与 PDF 描述的 `nErrorID` 命名不一致——以 PLC 编辑器实际声明为准。
- 具体 `bErrorID` 数值映射 PDF 未列，需要实测确认。
