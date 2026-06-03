# Tc3_PackML_V2

> Beckhoff TwinCAT 3 PackML V2 — OMAC PackML V3 包装机械标准状态机库。提供 PackML
> 标准的 19 状态机回调接口、中央自动状态机、UnitMode 配置/管理 FB、Admin PackTag
> 报警/告警/停机原因方法集，以及多种时间格式 → PackML 7 元素 DINT 数组的转换函数。

- **Library Version**: `1.2.4`
- **Source PDF**: <https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf>
- **InfoSys 库根**: <https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/>
- **总条目**: 25（3 INTERFACE + 13 FUNCTION_BLOCK + METHOD + 9 FC = 全部 25 POU）
- **状态**: ✅ done (25/25 verified · 25/25 lint)

## 子目录索引

| 子目录 | 条目数 | 说明 |
|---|---|---|
| [`packaging_machine_state/`](packaging_machine_state/) | 6 | PackML 状态机核心：3 接口 + PML_StateMachine + PML_UnitModeConfig + PML_UnitModeManager |
| [`general/`](general/) | 11 | Admin PackTag 操作：PML_AdminAlarm (parent) + 9 个方法 + PML_AdminTime |
| [`conversion/`](conversion/) | 8 | 时间/枚举转换函数：3 时长转换 + 3 时刻转换 + 2 字符串转换 |
| [`examples/`](examples/) | 25 | 全部条目配套 `P_Demo_*.TcPOU`（TwinCAT 3 原生例程，可直接拖入 XAE）|

## 条目清单

### `packaging_machine_state/`（PackML 状态机核心，PDF §2）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`I_UnitState.md`](packaging_machine_state/I_UnitState.md) | INTERFACE | `6298407051.html` — 全集 19 方法接口（PDF §2.1.1）|
| [`I_UnitStateWaiting.md`](packaging_machine_state/I_UnitStateWaiting.md) | INTERFACE | `6298422923.html` — 7 个 Waiting 稳态方法子接口（PDF §2.1.2）|
| [`I_UnitStateActing.md`](packaging_machine_state/I_UnitStateActing.md) | INTERFACE | `6298430859.html` — 12 个 Acting 过渡方法子接口（PDF §2.1.3）|
| [`PML_StateMachine.md`](packaging_machine_state/PML_StateMachine.md) | FUNCTION_BLOCK | `1335962123.html` — 中央自动状态机（PDF §2.3.1.1）|
| [`PML_UnitModeConfig.md`](packaging_machine_state/PML_UnitModeConfig.md) | FUNCTION_BLOCK | `1336141323.html` — 自定义 UnitMode 注册器（PDF §2.3.1.2）|
| [`PML_UnitModeManager.md`](packaging_machine_state/PML_UnitModeManager.md) | FUNCTION_BLOCK | `1336429067.html` — UnitMode 切换管理器（PDF §2.3.1.3）|

### `general/`（Admin PackTag 报警/时间，PDF §2.3.2）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`PML_AdminAlarm.md`](general/PML_AdminAlarm.md) | FUNCTION_BLOCK | `6298477963.html` — 报警/告警/停机原因 9 方法封装（parent）|
| [`M_SetAlarm.md`](general/M_SetAlarm.md) | METHOD | `6298536971.html` — 写入 alarm |
| [`M_AcknowledgeAlarm.md`](general/M_AcknowledgeAlarm.md) | METHOD | `6298615435.html` — 确认 alarm |
| [`M_ClearAlarm.md`](general/M_ClearAlarm.md) | METHOD | `6298997387.html` — 删除 alarm 到 AlarmHistory |
| [`M_SetWarning.md`](general/M_SetWarning.md) | METHOD | `6299606539.html` — 写入 warning |
| [`M_AcknowledgeWarning.md`](general/M_AcknowledgeWarning.md) | METHOD | `6300081163.html` — 确认 warning |
| [`M_ClearWarning.md`](general/M_ClearWarning.md) | METHOD | `6300095371.html` — 删除 warning |
| [`M_SetStopReason.md`](general/M_SetStopReason.md) | METHOD | `6300112267.html` — 写入停机原因 |
| [`M_AcknowledgeStopReason.md`](general/M_AcknowledgeStopReason.md) | METHOD | `6300126091.html` — 确认停机原因 |
| [`M_ClearStopReason.md`](general/M_ClearStopReason.md) | METHOD | `6300140299.html` — 删除停机原因 |
| [`PML_AdminTime.md`](general/PML_AdminTime.md) | FUNCTION_BLOCK | `6301131915.html` — 时间统计 FB（PDF §2.3.2.2）|

### `conversion/`（时间与枚举转换，PDF §2.3.3）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`LTIME_TO_PackMLTime.md`](conversion/LTIME_TO_PackMLTime.md) | FUNCTION | `6301243147.html` — 64 位时长 → PackML 数组 |
| [`TIME_TO_PackMLTime.md`](conversion/TIME_TO_PackMLTime.md) | FUNCTION | `6301648907.html` — 32 位时长 → PackML 数组 |
| [`ULINT_TO_PackMLTime.md`](conversion/ULINT_TO_PackMLTime.md) | FUNCTION | `6301953547.html` — 裸 ULINT → PackML 数组 |
| [`DCTIME64_TO_PackMLTime.md`](conversion/DCTIME64_TO_PackMLTime.md) | FUNCTION | `6301977739.html` — EtherCAT DC 时刻 → PackML 数组 |
| [`DT_TO_PackMLTime.md`](conversion/DT_TO_PackMLTime.md) | FUNCTION | `6302001931.html` — IEC DT → PackML 数组 |
| [`TIMESTRUCT_TO_PackMLTime.md`](conversion/TIMESTRUCT_TO_PackMLTime.md) | FUNCTION | `6302026123.html` — Beckhoff TIMESTRUCT → PackML 数组 |
| [`F_StateCommandToString.md`](conversion/F_StateCommandToString.md) | FUNCTION | `6302052235.html` — `E_PMLCommand` → STRING |
| [`F_UnitModeToString.md`](conversion/F_UnitModeToString.md) | FUNCTION | `6302851083.html` — UnitMode 编号 → STRING |

## 例程导入说明

每个条目都有配套的 `examples/P_Demo_<Name>.TcPOU`，是 TwinCAT 3 原生 `.TcPOU` 格式，可直接导入 XAE：

1. 在 PLC 项目的 **POUs** 文件夹右键 → **Add** → **Existing Item...**
2. 选择 `examples/P_Demo_<Name>.TcPOU`
3. 在 **References** → **Add library** 引用 `Tc3_PackML_V2`
4. 编译 → 登录 → 运行
5. 按例程头部"验证步骤"指引在线写值观察输出

例程头部用中文注释三件套说明：**场景 / 价值 / 验证步骤**。所有 FB 实例化都采用单次完整调用形式（`fbX(IN := ..., OUT => ...);`），所有 VAR_INPUT 显式赋值便于阅读。

变量命名贴近工业语义（如 `bMotorStartReq` / `stHighTempAlarm` / `bShiftEnd`），避免占位符（如 `bSig1`）。

注释行数 ≥ 代码行数 1/3，注释解释 WHY 不复述 WHAT。

## 设计判定与本库特色

### PackML V3 状态机模式

- **`I_UnitState` / `I_UnitStateActing` / `I_UnitStateWaiting`** 三个接口对应 OMAC PackML V3 的"状态钩子"模型。应用层把每个状态的工艺代码（启动序列、生产主循环、急停安全输出等）写入对应方法，由 `PML_StateMachine` 中央状态机多态分派。这使得状态决策（状态机标准化）与机器执行代码（工艺特定）完全解耦。
- 全集接口 `I_UnitState` 19 方法骨架；如果只关心稳态（保温/待命）用 `I_UnitStateWaiting`（7 方法）；只关心动作（启动/急停）用 `I_UnitStateActing`（12 方法）。可以一个 Acting FB + 一个 Waiting FB 配合 = 完整覆盖。

### Admin PackTag 三类事件

- **Alarm** 三阶段：Set → Acknowledge → Clear（移入 `AlarmHistory[]`）。符合 ISA-18.2 报警管理标准。
- **Warning** 两阶段：Set → Acknowledge（无 history、被新 warning 顶替）。用于不停机的提醒。
- **StopReason** 两阶段：Set → Acknowledge（无 history、被新 StopReason 顶替）。用于 OEE 停机分类标签。

### 时间转换体系

PackML PackTag 的时间字段统一用 `ARRAY [0..6] OF DINT`（年/月/日/时/分/秒/毫秒）。各种时间源（IEC TIME/LTIME/DT、Beckhoff TIMESTRUCT、EtherCAT DCTIME64）都有对应转换函数。

**关键语义**：
- LTIME/TIME/ULINT → 时长（duration），输出数组的"年"是流逝多少年
- DT/DCTIME64/TIMESTRUCT → 时刻（timestamp），输出数组的"年"是日历年份

## 验证基线（截至 2026-06-03）

- **verify_doc PASS**：25 / 25（含 VAR 一致性、占位短语扫描、InfoSys topic URL 检查、行为说明长度阈值）
- **lint_tcpou PASS**：25 / 25（XML 结构、CDATA 包裹、POU/VAR 头部、GUID 格式）
- **全仓 GUID 唯一性 (`--check-unique`)**：PASS（25 个 GUID 在 `tc3-libraries-kb/Tc3_PackML_V2/P_Demo_<Name>` 命名空间下生成，与其他库无冲突）

## 待人工确认项汇总（⚠️）

各篇文档 §9 列出的可疑/待确认项主要集中在以下几类，所有项均在 PDF + InfoSys 双源均未列出，需要联系 Beckhoff 或 PLC 实测确认：

1. `nErrorId / bErrorID` 数值映射：`PML_StateMachine` / `PML_UnitModeConfig` / `PML_UnitModeManager` 各有错误号但 PDF + InfoSys 都没列具体码值。
2. 数组满覆盖策略：`Alarm[] / Warning[] / StopReason[]` 满时的覆盖规则（是否真的"顶老"、还是"拒绝写入返回 FALSE"）PDF 文本简略。
3. PDF 已知印刷错误：`M_AcknowledgeStopReason` 与 `M_ClearStopReason` 的 Syntax 段方法头被错印为 `M_AcknowledgeAlarm` / `M_ClearAlarm`（VAR_IN_OUT/VAR_INPUT 内容正确，方法名以章节标题为准）。在对应文档 §2 与 §9 已点名。
4. PDF 命名小瑕疵：`PML_UnitModeConfig` 与 `PML_UnitModeManager` 的输出表把 `nErrorId/bErrorID` 与 VAR_OUTPUT 声明大小写不一致；以 VAR_OUTPUT 为准。

## 与其他 PackML 库的关系

- **Tc3_PackML（V1）**：上一代 PackML 库，已被本 V2 替代。
- **Tc3_PackML_V3**：更新版 PackML 库（V3 状态机标准的官方升级），与本库 API 不完全兼容。
