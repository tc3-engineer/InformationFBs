# PML_StateMachine

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Packaging Machine State` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/1335962123.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_PML_StateMachine.TcPOU`](../examples/P_Demo_PML_StateMachine.TcPOU) |

---

## 1. 功能简述

`PML_StateMachine` 是 PackML V3 标准的**中央自动状态机**，负责：(1) 接收命令枚举 `E_PMLCommand`（Reset/Start/Stop/Hold/Unhold/Suspend/Unsuspend/Abort/Clear）；(2) 维护当前状态 `E_PMLState`（Stopped/Starting/Idle/Execute/…/Aborted 共 17 + 未定义态）；(3) 根据当前 `eMode`（UnitMode）调用对应的过渡/稳态钩子。

预置 3 个基础 UnitMode：`Production`（生产）、`Maintenance`（维护）、`Manual`（手动），每种模式对应一个简化的子状态集合。其他模式可由 `PML_UnitModeConfig` 自定义后注入。本 FB 是 PackML V2 库的核心，所有 PackML 应用必须实例化一个。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eMode               : DINT;  
    eCommand            : E_PMLCommand; 
    stSubUnitInfoRef    : ST_PMLSubUnitInfoRef; 
    stOptions           : ST_PMLStateMachineOptions; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eMode` | `DINT` | - | 当前 PML UnitMode（1=Production / 2=Maintenance / 3=Manual / 4..31=自定义模式编号） |
| `eCommand` | `E_PMLCommand` | - | 命令枚举：0=Undefined / 1=Reset / 2=Start / 3=Stop / 4=Hold / 5=Unhold / 6=Suspend / 7=Unsuspend / 8=Abort / 9=Clear |
| `stSubUnitInfoRef` | `ST_PMLSubUnitInfoRef` | - | 指向 `ARRAY OF ST_PMLSubUnitInfo` 的引用结构（子单元状态汇总），状态机据此判断"全部子单元到达 Idle 才能切到 Idle"等条件 |
| `stOptions` | `ST_PMLStateMachineOptions` | - | 选项结构，当前 PDF 标注 "Not used at present"（V1.2.4 保留供后续扩展，传默认零结构即可）|

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    eState     : E_PMLState; 
    bError     : BOOL; 
    nErrorId   : UDINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eState` | `E_PMLState` | 当前自动状态机的 PML 状态（Stopped/Starting/Execute/.../Aborted）|
| `bError` | `BOOL` | 出错时置 TRUE |
| `nErrorId` | `UDINT` | `bError = TRUE` 时给出错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

`PML_StateMachine` 实现 PackML V3 状态转移规则——只允许标准定义的状态切换路径，禁止跨态跳跃。

**核心循环**：每个 PLC 周期调用本 FB，传入当前 `eMode + eCommand + stSubUnitInfoRef`，FB 内部根据状态转移矩阵判断是否能从当前态切到新态：
- 若命令合法（如在 Idle 收到 Start）则启动过渡（切到 Starting → 调用 Acting 钩子）；
- 若命令非法（如在 Aborted 收到 Start，必须先 Reset/Clear）则 `bError = TRUE`、`nErrorId` 给出原因码；
- 若命令是 Abort，则无视当前态直接切到 Aborting（PackML 标准允许任意态触发急停）。

**UnitMode 切换**：本 FB 不直接处理 UnitMode 切换——切换由配套的 `PML_UnitModeManager` 在允许的状态触发。`PML_StateMachine` 只读取 `eMode` 决定当前状态集合。

**子单元状态汇总**：`stSubUnitInfoRef.pArray` 指向所有受控子单元（如多工位机的每个工位）的状态数组；状态机根据"全部子单元到达 Idle 才能进入 Idle"等组合条件判断稳态到达。

**典型用法**：在 MAIN POU 里实例化 `PML_StateMachine`，把 HMI 命令按钮映射到 `eCommand`、把 PMLc.UnitMode 映射到 `eMode`、把所有子单元数组指针通过 `ST_PMLSubUnitInfoRef` 传入；每周期把输出 `eState` 写回 PMLs.StateCurrent 供 HMI 显示。

**典型陷阱**：(1) 一上电就发 Start 命令会被拒（必须先 Reset 进入 Idle）；(2) `stSubUnitInfoRef.nNoOfSubUnits` 写大于实际数组长度会越界；(3) `stOptions` 当前未用，传未初始化结构理论上不影响，但建议显式置零。

## 4. 错误码 / 返回值

PDF 标注 `nErrorId` 在 `bError = TRUE` 时给出错误号。PDF + InfoSys 均未列具体错误码值的含义。常见出错场景：

| 出错场景 | 含义 | 处理建议 |
|---|---|---|
| 命令在当前状态非法 | 例如 Aborted 状态下收到 Start | HMI 提示"请先 Reset"；先发 Clear/Reset 进入 Idle |
| `stSubUnitInfoRef` 越界 | `nNoOfSubUnits > nArraySize / SIZEOF(ST_PMLSubUnitInfo)` | 检查初始化代码 |
| `eMode` 不在已注册范围 | 例如 100 既不是基础模式 1-3、也未通过 PML_UnitModeConfig 注册 | 先调用 PML_UnitModeConfig 注册再切模式 |

⚠️ 待人工确认：具体 `nErrorId` 数值映射 PDF + InfoSys 均未列。运行中观察实际取值或联系 Beckhoff support 确认。

## 5. 使用注意 / 常见坑

- 必须**周期调用**——本 FB 是状态机推进器，少调一次会延迟状态切换。建议放在 PLC 主任务每周期。
- `eMode` 一上电默认为 0（Invalid），需要立即写入有效模式（如 1=Production）。`PML_UnitModeManager` 可以管理这一切换。
- 收到 Abort 命令优先级最高，会从任意态切到 Aborting；恢复需要先 Clear（到 Stopped）再 Reset（到 Idle）。
- `stSubUnitInfoRef` 传空（`pArray = 0` / `nNoOfSubUnits = 0`）也合法，等于单元机器没有子单元——状态机只看自身命令。（工程经验补充）
- 多个生产线如果各自独立的 PackML 状态机，每条线实例化一个本 FB，不要全局共享。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PML_StateMachine.TcPOU`](../examples/P_Demo_PML_StateMachine.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一条饮料灌装生产线，HMI 上有 Start/Stop/Hold/Abort 5 个按钮。工艺要求严格按 ISA-TR88/PackML 状态转移：必须先 Reset 进入 Idle 才能 Start；Hold 后必须 Unhold 才能继续生产；急停后必须 Clear+Reset 才能恢复。`PML_StateMachine` 一次性把这套规则实现完毕。
- **价值**：用本 FB 不必手写状态转移矩阵（17 状态 × 9 命令 = 153 个分支判断），不必担心遗漏分支造成状态跑飞。HMI 按钮直接映射到 `eCommand`，不合法操作 FB 自动拒绝并报错。符合 OMAC 标准的状态汇报让 MES/SCADA 可直接对接。
- **替代方案对比**：自己写 case 状态机——代码量大、容易遗漏、不同设备不一致；用本 FB 一行声明 + 周期调用，整条产线状态语义统一。这是 Beckhoff 推荐的 PackML 实现路径，OEM 不需要再造轮子。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/1335962123.html
- **相关**：`PML_UnitModeConfig`（注册自定义模式）、`PML_UnitModeManager`（管理模式切换）、`E_PMLState` / `E_PMLCommand`（状态/命令枚举）、`I_UnitState` / `I_UnitStateActing` / `I_UnitStateWaiting`（单元 FB 实现的钩子接口）

## 9. 待确认项 (⚠️)

- `nErrorId` 数值与含义映射：PDF + InfoSys 均未列出具体码值，需要联系 Beckhoff 或运行测试时枚举观察实际值。
