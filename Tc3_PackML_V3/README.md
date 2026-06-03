# Tc3_PackML_V3

> Beckhoff TwinCAT 3 PackML V3 — OMAC PackML V3 包装机械标准库的**升级版**（V2 是上一代）。
> 提供 PackML V3 状态机的 19 状态钩子接口、中央自动状态机、UnitMode 配置/管理 FB、
> Admin PackTag 报警/告警/停机原因方法集（V3 扩展到 17 方法），以及多种时间格式
> → `ST_PMLDateAndTime` 结构体的转换函数（V3 改用结构体，V2 用数组）。

- **Library Version**: `1.0.0`（PDF 发布日期 2025-08-25）
- **Source PDF**: <https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf>
- **InfoSys 库根**: <https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/>
- **总条目**: 32（25 FUNCTION_BLOCK + METHOD + 2 INTERFACE + 8 FUNCTION = 32 POU）
- **状态**: ✅ done (32/32 verified · 32/32 lint · GUID unique)

## 子目录索引

| 子目录 | 条目数 | 说明 |
|---|---|---|
| [`packaging_machine_state/`](packaging_machine_state/) | 3 | PackML V3 状态机核心：FB_PMLStateMachine + FB_PMLUnitModeConfig + FB_PMLUnitModeManager |
| [`interfaces/`](interfaces/) | 2 | PackML 状态钩子接口：I_PMLUnitStateActing（12 方法）+ I_PMLUnitStateWaiting（7 方法）|
| [`general/`](general/) | 19 | Admin PackTag 操作：FB_PMLAdminAlarm (parent) + 17 方法 + FB_PMLAdminTime |
| [`conversion/`](conversion/) | 8 | 时间/枚举转换函数：3 时长转换 + 3 时刻转换 + 2 字符串转换 |
| [`examples/`](examples/) | 32 | 全部条目配套 `P_Demo_*.TcPOU`（TwinCAT 3 原生例程，可直接拖入 XAE）|

## 条目清单

### `packaging_machine_state/`（PackML 状态机核心，PDF §4.3）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`FB_PMLStateMachine.md`](packaging_machine_state/FB_PMLStateMachine.md) | FUNCTION_BLOCK | `16003677835.html` — 中央自动状态机（PDF §4.3.1）|
| [`FB_PMLUnitModeConfig.md`](packaging_machine_state/FB_PMLUnitModeConfig.md) | FUNCTION_BLOCK | `16003718411.html` — 自定义 UnitMode 注册器（PDF §4.3.2）|
| [`FB_PMLUnitModeManager.md`](packaging_machine_state/FB_PMLUnitModeManager.md) | FUNCTION_BLOCK | `16003759883.html` — UnitMode 切换管理器（PDF §4.3.3）|

### `interfaces/`（PackML 状态钩子接口，PDF §8）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`I_PMLUnitStateActing.md`](interfaces/I_PMLUnitStateActing.md) | INTERFACE | ⚠️ not-on-infosys — 12 个 Acting 过渡方法子接口（PDF §8.1）|
| [`I_PMLUnitStateWaiting.md`](interfaces/I_PMLUnitStateWaiting.md) | INTERFACE | ⚠️ not-on-infosys — 7 个 Waiting 稳态方法子接口（PDF §8.2）|

### `general/`（Admin PackTag 报警/时间，PDF §4.2）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`FB_PMLAdminAlarm.md`](general/FB_PMLAdminAlarm.md) | FUNCTION_BLOCK | ⚠️ not-on-infosys — 报警/告警/停机原因 17 方法封装（parent）|
| [`M_SetAlarm.md`](general/M_SetAlarm.md) | METHOD | ⚠️ not-on-infosys — 写入 alarm |
| [`M_AcknowledgeAlarm.md`](general/M_AcknowledgeAlarm.md) | METHOD | ⚠️ not-on-infosys — 确认指定 alarm |
| [`M_AcknowledgeAllAlarms.md`](general/M_AcknowledgeAllAlarms.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：批量确认全部 alarm |
| [`M_ClearAlarm.md`](general/M_ClearAlarm.md) | METHOD | ⚠️ not-on-infosys — 删除指定 alarm（已 Ack 移入 history） |
| [`M_ClearAllAlarms.md`](general/M_ClearAllAlarms.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：批量清除全部 alarm |
| [`M_GetAlarmCategory.md`](general/M_GetAlarmCategory.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：取最高优先级 alarm 的 Category |
| [`M_HasAlarm.md`](general/M_HasAlarm.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：查询是否有未处理 alarm |
| [`M_SetStopReason.md`](general/M_SetStopReason.md) | METHOD | ⚠️ not-on-infosys — 写入停机原因（V3 单值，V2 数组）|
| [`M_AcknowledgeStopReason.md`](general/M_AcknowledgeStopReason.md) | METHOD | ⚠️ not-on-infosys — 确认停机原因 |
| [`M_ClearStopReason.md`](general/M_ClearStopReason.md) | METHOD | ⚠️ not-on-infosys — 删除停机原因 |
| [`M_HasStopReason.md`](general/M_HasStopReason.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：查询是否有未处理停机原因 |
| [`M_SetWarning.md`](general/M_SetWarning.md) | METHOD | ⚠️ not-on-infosys — 写入 warning |
| [`M_AcknowledgeWarning.md`](general/M_AcknowledgeWarning.md) | METHOD | ⚠️ not-on-infosys — 确认指定 warning |
| [`M_AcknowledgeAllWarning.md`](general/M_AcknowledgeAllWarning.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：批量确认全部 warning |
| [`M_ClearWarning.md`](general/M_ClearWarning.md) | METHOD | ⚠️ not-on-infosys — 删除指定 warning |
| [`M_ClearAllWarning.md`](general/M_ClearAllWarning.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：批量清除全部 warning |
| [`M_HasWarning.md`](general/M_HasWarning.md) | METHOD | ⚠️ not-on-infosys — **V3 新增**：查询是否有未处理 warning |
| [`FB_PMLAdminTime.md`](general/FB_PMLAdminTime.md) | FUNCTION_BLOCK | `16004004235.html` — 时间统计 FB（含内联方法 M_ResetCumulativeTime）|

### `conversion/`（时间与枚举转换，PDF §4.1）

| 文件 | 类型 | InfoSys topic |
|---|---|---|
| [`LTIME_TO_PMLTime.md`](conversion/LTIME_TO_PMLTime.md) | FUNCTION | ⚠️ not-on-infosys — 64 位时长 → ST_PMLDateAndTime |
| [`TIME_TO_PMLTime.md`](conversion/TIME_TO_PMLTime.md) | FUNCTION | ⚠️ not-on-infosys — 32 位时长 → ST_PMLDateAndTime |
| [`ULINT_TO_PMLTime.md`](conversion/ULINT_TO_PMLTime.md) | FUNCTION | ⚠️ not-on-infosys — 裸 ULINT → ST_PMLDateAndTime |
| [`DCTIME64_TO_PMLTime.md`](conversion/DCTIME64_TO_PMLTime.md) | FUNCTION | ⚠️ not-on-infosys — EtherCAT DC 时刻 → ST_PMLDateAndTime |
| [`DT_TO_PMLTime.md`](conversion/DT_TO_PMLTime.md) | FUNCTION | ⚠️ not-on-infosys — IEC DT → ST_PMLDateAndTime |
| [`TIMESTRUCT_TO_PMLTime.md`](conversion/TIMESTRUCT_TO_PMLTime.md) | FUNCTION | ⚠️ not-on-infosys — Beckhoff TIMESTRUCT → ST_PMLDateAndTime |
| [`F_PMLStateCommandToString.md`](conversion/F_PMLStateCommandToString.md) | FUNCTION | ⚠️ not-on-infosys — `E_PMLCommand` → STRING |
| [`F_PMLUnitModeToString.md`](conversion/F_PMLUnitModeToString.md) | FUNCTION | ⚠️ not-on-infosys — UnitMode 编号 → STRING |

## V3 vs V2 差异要点

> 本节集中列出从 V2 升级到 V3 时需要关注的 API 变化。详细变化见每篇文档的 §1 / §5。

### 1. 命名前缀统一加 `FB_` 和 `PML`

- **FB**：V2 `PML_AdminAlarm` → V3 `FB_PMLAdminAlarm`；V2 `PML_StateMachine` → V3 `FB_PMLStateMachine`；同样适用于 AdminTime / UnitModeConfig / UnitModeManager。
- **接口**：V2 `I_UnitState` / `I_UnitStateActing` / `I_UnitStateWaiting` → V3 仅保留 `I_PMLUnitStateActing` / `I_PMLUnitStateWaiting`（取消全集接口；想全覆盖直接 `IMPLEMENTS` 两个）。
- **函数**：V2 `LTIME_TO_PackMLTime` 等 → V3 `LTIME_TO_PMLTime`（`PackMLTime` 简化为 `PMLTime`）；V2 `F_StateCommandToString` / `F_UnitModeToString` → V3 `F_PMLStateCommandToString` / `F_PMLUnitModeToString`。

### 2. 数据类型升级

- **时间转换返回类型**：V2 返回 `ARRAY [0..6] OF DINT`；V3 返回**结构体** `ST_PMLDateAndTime`（带 Year/Month/Day/Hour/Minute/Second/mSec 7 个 DINT 字段）。从 V2 升级时全部访问从 `a[3]` 改成 `st.Hour` 字段名访问。
- **事件结构**：V2 `ST_Alarm` → V3 `ST_PMLEvent`（命名标准化）。
- **AdminTime 选项**：V2 `ST_AdminTimeOptions` → V3 `ST_PMLAdminTimeOptions`（PDF §4.2.2 VAR_INPUT 内印刷错误把 V2 名印出来——以 §5.1.1 实际定义为准）。

### 3. FB 接口扩展

- **`FB_PMLAdminAlarm` 方法数**：V2 9 个 → V3 17 个，新增 8 个："批量"系列（AckAllAlarms / ClearAllAlarms / AckAllWarning / ClearAllWarning）+ "查询"系列（HasAlarm / HasWarning / HasStopReason / GetAlarmCategory）。
- **`FB_PMLStateMachine` 输出**：V3 新增 `sState : STRING` 输出——直接给状态名字符串供 HMI 显示，不必再用 `F_PMLStateCommandToString` 反查。
- **`FB_PMLUnitModeManager` 输出**：V3 新增 `eModeStatus : DINT` 和 `sModeStatus : STRING(80)`——HMI 顶端"当前模式"标签直接绑。
- **`FB_PMLUnitModeConfig` 输入**：V3 新增 3 个 ARRAY 输入 `aStateFlashing / aStateColor / aStateTextColor`（自 V1.0.5.0 起）——把 HMI 视觉属性也封到模式配置里。

### 4. 命令/状态枚举扩展

- **`E_PMLCommand`**：V3 多 1 个 `Complete := 10`（V2 只有 0-9 共 10 个）。
- **`E_PMLState`**：V3 多 1 个 `Completed := 17`（V2 是 0-16 共 17 状态）。
- 配合上面两个新增，PackML V3 支持完整的"Producing → Completing → Completed"批结束流程。

### 5. StopReason 容器从数组改为单值

- V2 `ST_PMLa.StopReason : ARRAY OF ST_PMLEvent`（数组）；V3 `ST_PMLa.StopReason : ST_PMLEvent`（单实例）。
- 影响：V3 `M_SetStopReason` 新写入直接覆盖；`M_AcknowledgeStopReason` / `M_ClearStopReason` 不需要 stStopReason 参数（直接操作当前那个）。从 V2 升级时如果代码假设数组操作必须改。

### 6. AdminTime 复位机制改造

- V2 `PML_AdminTime` 有 `bReset : BOOL` 顶层输入——全局复位所有累计时间。
- V3 `FB_PMLAdminTime` 去掉了 `bReset`——改为 `M_ResetCumulativeTime(CumulativeTimesIdx : UDINT)` 方法，按下标精确复位。一个机器可以同时跑多个累计周期（班/日/月）独立复位。
- 升级时：把 `fbAdminTime.bReset := bResetTimes;` 替换为 `IF rtrigReset.Q THEN fbAdminTime.M_ResetCumulativeTime(CumulativeTimesIdx := 0); END_IF`。

### 7. UnitModeManager 增加 eState 输入

- V3 `FB_PMLUnitModeManager` 多了 `eState : E_PMLState` 输入——把当前状态机状态传给 Manager 让它判断是否允许切模式。V2 用户必须改：把 `FB_PMLStateMachine.eState` 接到本 FB 的 `eState`。

## 例程导入说明

每个条目都有配套的 `examples/P_Demo_<Name>.TcPOU`，是 TwinCAT 3 原生 `.TcPOU` 格式，可直接导入 XAE：

1. 在 PLC 项目的 **POUs** 文件夹右键 → **Add** → **Existing Item...**
2. 选择 `examples/P_Demo_<Name>.TcPOU`
3. 在 **References** → **Add library** 引用 `Tc3_PackML_V3`（确保库版本 1.0.0 已安装）
4. 编译 → 登录 → 运行
5. 按例程头部"验证步骤"指引在线写值观察输出

例程头部用中文注释三件套说明：**场景 / 价值 / 验证步骤**。所有 FB 实例化都采用单次完整调用形式（`fbX(IN := ..., OUT => ...);`），所有 VAR_INPUT 显式赋值便于阅读。

变量命名贴近工业语义（如 `nFilterLifePercent` / `stHighTempAlarm` / `bBtnShiftEnd`），避免占位符（如 `bSig1`）。

注释行数 ≥ 代码行数 1/3，注释解释 WHY 不复述 WHAT。

> **接口示例特别说明**：`P_Demo_I_PMLUnitStateActing.TcPOU` 和 `P_Demo_I_PMLUnitStateWaiting.TcPOU` 只展示接口调用语法，编译时可能因 `ipActor` / `ipKeeper` 未指向实例而报错——这是接口示例的正常情况。实际项目需要：(1) 创建应用 FB；(2) FB 头部 `IMPLEMENTS I_PMLUnitStateActing` 或 `I_PMLUnitStateWaiting`；(3) 实现全部方法；(4) 把 FB 实例赋给接口引用。

## 设计判定与本库特色

### PackML V3 状态机模式

- **`I_PMLUnitStateActing` / `I_PMLUnitStateWaiting`** 两个接口对应 OMAC PackML V3 的"状态钩子"模型。应用层把每个状态的工艺代码（启动序列、生产主循环、急停安全输出等）写入对应方法，由 `FB_PMLStateMachine` 中央状态机多态分派。这使得状态决策（状态机标准化）与机器执行代码（工艺特定）完全解耦。
- V3 相比 V2 取消了"全集" `I_UnitState` 接口——想覆盖全部 19 状态钩子直接 `IMPLEMENTS I_PMLUnitStateActing, I_PMLUnitStateWaiting`。

### Admin PackTag 三类事件

- **Alarm** 三阶段：Set → Acknowledge → Clear（移入 `AlarmHistory[]`）。符合 ISA-18.2 报警管理标准。
- **Warning** 两阶段：Set → Acknowledge（无 history、被新 warning 顶替）。用于不停机的提醒。
- **StopReason** **V3 单实例**：Set 直接覆盖；Ack/Clear 操作当前那个。用于 OEE 停机分类标签。

### V3 时间转换体系

PackML PackTag 的时间字段统一用 **`ST_PMLDateAndTime` 结构体**（V2 是 `ARRAY [0..6] OF DINT`）。各种时间源（IEC TIME/LTIME/DT、Beckhoff TIMESTRUCT、EtherCAT DCTIME64）都有对应转换函数。

**关键语义**：
- LTIME/TIME/ULINT → 时长（duration），输出结构体的 `Year` 是流逝多少年
- DT/DCTIME64/TIMESTRUCT → 时刻（timestamp），输出结构体的 `Year` 是日历年份

## 验证基线（截至 2026-06-03）

- **verify_doc PASS**：32 / 32（含 VAR 一致性、占位短语扫描、InfoSys topic URL 检查、行为说明长度阈值）
- **lint_tcpou PASS**：32 / 32（XML 结构、CDATA 包裹、POU/VAR 头部、GUID 格式）
- **全仓 GUID 唯一性 (`--check-unique`)**：PASS（32 个 GUID 在 `tc3-libraries-kb/Tc3_PackML_V3/P_Demo_<Name>` 命名空间下生成，与 V2 同名 FB 的 GUID 完全不冲突）

## 待人工确认项汇总（⚠️）

各篇文档 §9 列出的可疑/待确认项主要集中在以下几类，所有项均在 PDF 中未明确给出，需要联系 Beckhoff 或 PLC 实测确认：

1. **`nErrorId / bErrorID` 数值映射**：`FB_PMLStateMachine` / `FB_PMLUnitModeConfig` / `FB_PMLUnitModeManager` 各有错误号输出但 PDF 都没列具体码值。
2. **方法 FALSE 返回的细分原因**：`FB_PMLAdminAlarm` 各方法返回 BOOL，FALSE 的具体场景 PDF 未列。
3. **Alarm/Warning 数组满时具体处理**：PDF 主要描述 AlarmHistory 满时覆盖，主 Alarm/Warning 数组的满处理细节不全。
4. **PDF 印刷错误**：
   - `FB_PMLAdminTime` §4.2.2 VAR_INPUT 把类型名印成 V2 的 `ST_AdminTimeOptions`，实际是 `ST_PMLAdminTimeOptions`（§5.1.1 定义）；
   - `FB_PMLUnitModeManager` VAR_OUTPUT 声明 `bErrorID` 但描述写 `nErrorID`；
   - `M_GetAlarmCategory` Syntax 段方法头返回类型写 `BOOL` 但功能描述/示例显示返回 DINT；
   - `M_HasStopReason` Syntax 段方法头被错印为 `M_SetStopReason`。
5. **V3 INTERFACE 方法签名**：PDF §8.1 / §8.2 只给方法名列表，未给参数/返回类型——实测以 PLC 编辑器自动生成的骨架为准。
6. **V3 InfoSys 大量 topic URL 公网检索不到**：本库 32 篇中有 28 篇 `InfoSys-checked` 标为 `⚠️ not-on-infosys`，包括 FB_PMLAdminAlarm 主 FB + 全部 17 方法、8 个 conversion FC 与 2 INTERFACE。这是因为 V3 库刚发布（2025-08-25），InfoSys 站点 topic 公网索引尚未完整建立。**只有 4 篇有自身的确认 V3 topic URL**（FB_PMLStateMachine、FB_PMLUnitModeConfig、FB_PMLUnitModeManager、FB_PMLAdminTime）。其他篇章的 `Source InfoSys` 字段指向已确认存在的同章节最相关 topic（如 conversion FC 指向返回类型 `ST_PMLDateAndTime` 的 topic、FB_PMLAdminAlarm 系列指向同 §4.2 General 章节的 FB_PMLAdminTime topic）作为最接近的参考定位锚点，并明确在 §8/§9 标注该是替代而非本身；待 InfoSys V3 公网索引完整后可批量回填。

## 与其他 PackML 库的关系

- **Tc3_PackML（V1）**：第一代 PackML 库，已被 V2 / V3 替代。
- **Tc3_PackML_V2**：上一代 PackML 库；本库（V3）是 V2 的官方升级。API 不完全兼容（详见上文 V3 vs V2 差异要点）。
- **Tc3_PackML_V3**：本库（PackML V3 标准的官方实现），版本 1.0.0 发布于 2025-08-25。
