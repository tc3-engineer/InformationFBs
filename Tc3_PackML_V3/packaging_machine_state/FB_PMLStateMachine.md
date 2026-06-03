# FB_PMLStateMachine

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Packaging Machine State` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003677835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PMLStateMachine.TcPOU`](../examples/P_Demo_FB_PMLStateMachine.TcPOU) |

---

## 1. 功能简述

`FB_PMLStateMachine` 是 PackML V3 标准的**中央自动状态机**，负责：(1) 接收命令枚举 `E_PMLCommand`（Reset/Start/Stop/Hold/Unhold/Suspend/Unsuspend/Abort/Clear/Complete 共 10 个）；(2) 维护当前状态 `E_PMLState`（Undefined/Clearing/Stopped/Starting/Idle/Suspended/Execute/Stopping/Aborting/Aborted/Holding/Held/Unholding/Suspending/Unsuspending/Resetting/Completing/Completed 共 18 个状态）；(3) 根据当前 `eMode`（UnitMode）调用对应的过渡/稳态钩子。

**V3 与 V2 的关键差异**：
- **FB 命名**：V2 叫 `PML_StateMachine`，V3 改名 `FB_PMLStateMachine`。
- **输出新增 `sState`**：V3 新增 `sState : STRING(80)` 输出——给出当前状态的字符串名（如 'Execute'），HMI 直接绑定显示无需自己用 `F_PMLStateCommandToString` 反查。
- **命令枚举多 1 个**：V3 `E_PMLCommand` 多了 `Complete := 10`（V2 只有 0-9）。
- **状态枚举多 1 个**：V3 `E_PMLState` 多了 `Completed := 17`（V2 是 0-16 共 17 状态）。
- **没有 V2 的 I_UnitState 全集接口**——V3 只保留 `I_PMLUnitStateActing` / `I_PMLUnitStateWaiting` 两个细分接口；如果应用 FB 要全部 19 个方法骨架，必须同时 `IMPLEMENTS` 两个接口。

预置 3 个基础 UnitMode：`Production`（生产，eMode=1）、`Maintenance`（维护，eMode=2）、`Manual`（手动，eMode=3）；其他模式可由 `FB_PMLUnitModeConfig` 自定义后注入。本 FB 是 PackML V3 库的核心，所有 PackML 应用必须实例化一个。

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
| `eMode` | `DINT` | - | 当前 PML UnitMode（0=Invalid / 1=Production / 2=Maintenance / 3=Manual / 4..31=自定义模式编号） |
| `eCommand` | `E_PMLCommand` | - | 命令枚举：0=Undefined / 1=Reset / 2=Start / 3=Stop / 4=Hold / 5=Unhold / 6=Suspend / 7=Unsuspend / 8=Abort / 9=Clear / 10=Complete |
| `stSubUnitInfoRef` | `ST_PMLSubUnitInfoRef` | - | 指向 `ARRAY OF ST_PMLSubUnitInfo` 的引用结构（子单元状态汇总），状态机据此判断"全部子单元到达 Idle 才能切到 Idle"等条件 |
| `stOptions` | `ST_PMLStateMachineOptions` | - | 选项结构，当前 PDF 标注 "Not used at present"（V1.0.0 保留供后续扩展，传默认零结构即可）|

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    eState     : E_PMLState; 
    sState     : STRING;
    bError     : BOOL; 
    nErrorId   : UDINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eState` | `E_PMLState` | 当前自动状态机的 PML 状态枚举（Stopped/Starting/Execute/.../Completed）|
| `sState` | `STRING` | 当前 PML 状态的字符串名（V3 新增——HMI 直接绑定显示，省去 F_PMLStateCommandToString 反查）|
| `bError` | `BOOL` | 出错时置 TRUE |
| `nErrorId` | `UDINT` | `bError = TRUE` 时给出错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

`FB_PMLStateMachine` 实现 PackML V3 状态转移规则——只允许标准定义的状态切换路径，禁止跨态跳跃。

**核心循环**：每个 PLC 周期调用本 FB，传入当前 `eMode + eCommand + stSubUnitInfoRef`，FB 内部根据状态转移矩阵判断是否能从当前态切到新态：
- 若命令合法（如在 Idle 收到 Start）则启动过渡（切到 Starting → 调用 Acting 钩子）；
- 若命令非法（如在 Aborted 收到 Start，必须先 Reset/Clear）则 `bError = TRUE`、`nErrorId` 给出原因码；
- 若命令是 Abort，则无视当前态直接切到 Aborting（PackML 标准允许任意态触发急停）。

**UnitMode 切换**：本 FB 不直接处理 UnitMode 切换——切换由配套的 `FB_PMLUnitModeManager` 在允许的状态触发。`FB_PMLStateMachine` 只读取 `eMode` 决定当前状态集合。

**子单元状态汇总**：`stSubUnitInfoRef.pArray` 指向所有受控子单元（如多工位机的每个工位）的状态数组；状态机根据"全部子单元到达 Idle 才能进入 Idle"等组合条件判断稳态到达。本 FB 是一个父状态机协调多个子单元，类似多 PLC OEE 场景。

**典型用法**：在 MAIN POU 里实例化 `FB_PMLStateMachine`，把 HMI 命令按钮映射到 `eCommand`、把 PMLc.UnitMode 映射到 `eMode`、把所有子单元数组指针通过 `ST_PMLSubUnitInfoRef` 传入；每周期把输出 `eState` 写回 PMLs.StateCurrent 供 HMI 显示，`sState` 字符串直接接 HMI 文本控件。

**典型陷阱**：(1) 一上电就发 Start 命令会被拒（必须先 Reset 进入 Idle）；(2) `stSubUnitInfoRef.NoOfSubUnits` 写大于实际数组长度会越界（PDF 用 ArraySize + NoOfSubUnits 表达数组边界）；(3) `stOptions` 当前未用，传未初始化结构理论上不影响，但建议显式置零。

## 4. 错误码 / 返回值

PDF 标注 `nErrorId` 在 `bError = TRUE` 时给出错误号。PDF 未列具体错误码值的含义。常见出错场景：

| 出错场景 | 含义 | 处理建议 |
|---|---|---|
| 命令在当前状态非法 | 例如 Aborted 状态下收到 Start | HMI 提示"请先 Reset"；先发 Clear/Reset 进入 Idle |
| `stSubUnitInfoRef` 越界 | `NoOfSubUnits > ArraySize / SIZEOF(ST_PMLSubUnitInfo)` | 检查初始化代码 |
| `eMode` 不在已注册范围 | 例如 100 既不是基础模式 1-3、也未通过 FB_PMLUnitModeConfig 注册 | 先调用 FB_PMLUnitModeConfig 注册再切模式 |

⚠️ 待人工确认：具体 `nErrorId` 数值映射 PDF 未列。运行中观察实际取值或联系 Beckhoff support 确认。

## 5. 使用注意 / 常见坑

- 必须**周期调用**——本 FB 是状态机推进器，少调一次会延迟状态切换。建议放在 PLC 主任务每周期。
- `eMode` 一上电默认为 0（Invalid），需要立即写入有效模式（如 1=Production）。`FB_PMLUnitModeManager` 可以管理这一切换。
- 收到 Abort 命令优先级最高，会从任意态切到 Aborting；恢复需要先 Clear（到 Stopped）再 Reset（到 Idle）。
- V3 新增 Complete 命令（命令码 10）和 Completed 状态（状态码 17）——比 V2 多支持"Producing → Completing → Completed"的标准 PackML 收工流程。从 V2 升级时可以充分利用。
- `stSubUnitInfoRef` 传空（`pArray = 0` / `NoOfSubUnits = 0`）也合法，等于单元机器没有子单元——状态机只看自身命令。（工程经验补充）
- 多个生产线如果各自独立的 PackML 状态机，每条线实例化一个本 FB，不要全局共享。（工程经验补充）
- HMI 显示当前状态名直接绑 `sState`——比 V2 用户必须用 `F_StateCommandToString` 反查更便捷。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PMLStateMachine.TcPOU`](../examples/P_Demo_FB_PMLStateMachine.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一条饮料灌装生产线，HMI 上有 Start/Stop/Hold/Abort/Complete 5 个按钮。工艺要求严格按 ISA-TR88/PackML V3 状态转移：必须先 Reset 进入 Idle 才能 Start；Hold 后必须 Unhold 才能继续生产；急停后必须 Clear+Reset 才能恢复；批次结束后 Complete 进入 Completed 等待下一批。`FB_PMLStateMachine` 一次性把这套规则实现完毕。
- **价值**：用本 FB 不必手写状态转移矩阵（18 状态 × 11 命令 = 198 个分支判断），不必担心遗漏分支造成状态跑飞。HMI 按钮直接映射到 `eCommand`，不合法操作 FB 自动拒绝并报错。符合 OMAC PackML V3 标准的状态汇报让 MES/SCADA 可直接对接。V3 新增的 `sState` 字符串输出让 HMI 显示更简洁。
- **替代方案对比**：自己写 case 状态机——代码量大、容易遗漏、不同设备不一致；用本 FB 一行声明 + 周期调用，整条产线状态语义统一。这是 Beckhoff 推荐的 PackML 实现路径，OEM 不需要再造轮子。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003677835.html
- **相关**：`FB_PMLUnitModeConfig`（注册自定义模式）、`FB_PMLUnitModeManager`（管理模式切换）、`E_PMLState` / `E_PMLCommand`（状态/命令枚举）、`I_PMLUnitStateActing` / `I_PMLUnitStateWaiting`（单元 FB 实现的钩子接口）、`ST_PMLSubUnitInfoRef` / `ST_PMLSubUnitInfo`、`E_PMLProtectedUnitMode`（受保护的基础模式）

## 9. 待确认项 (⚠️)

- `nErrorId` 数值与含义映射：PDF 未列出具体码值，需要联系 Beckhoff 或运行测试时枚举观察实际值。
