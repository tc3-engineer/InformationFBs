# PML_AdminAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `General` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298477963.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_PML_AdminAlarm.TcPOU`](../examples/P_Demo_PML_AdminAlarm.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm` 是 **PackML 管理标签（Admin-PackTags）的报警/告警/停机原因操作 FB**——把 PackML 标准定义的 `Alarm[]` / `Warning[]` / `StopReason[]` 三个数组用方法封装起来：写入、确认（acknowledge）、清除（clear）。

本 FB 自身没有 VAR_INPUT/OUTPUT；所有操作通过 9 个方法暴露：3 类事件（Alarm/Warning/StopReason）× 3 个操作（Set/Acknowledge/Clear）。每个方法接受 `stAdmin : ST_PMLa`（管理 PackTag 结构）和事件结构 `ST_Alarm` 作为输入，返回 BOOL 表示操作是否成功。

## 2. 接口定义

FB 本身没有顶层 VAR_INPUT/OUTPUT；交互全部通过 9 个方法暴露。所有方法共享同一套参数模式：

### 方法共用参数（按方法的 VAR_IN_OUT / VAR_INPUT 声明）

```iecst
(* 所有 9 个方法都遵循这套签名 *)
VAR_IN_OUT
  stAdmin          : ST_PMLa;        (* 管理 PackTag，方法读写它的 Alarm/Warning/StopReason 数组 *)
END_VAR
VAR_INPUT
  (* Alarm 类方法 *)
  stAlarm          : ST_Alarm;       (* 用于 M_SetAlarm / M_AcknowledgeAlarm / M_ClearAlarm *)
  (* Warning 类方法 *)
  stWarning        : ST_Alarm;       (* 用于 M_SetWarning / M_AcknowledgeWarning / M_ClearWarning *)
  (* StopReason 类方法 *)
  stStopReason     : ST_Alarm;       (* 用于 M_SetStopReason / M_AcknowledgeStopReason / M_ClearStopReason *)
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | VAR_IN_OUT，全部 9 个方法 | PackML 管理 PackTag 实例（通常是全局 `PackTags.Admin`），方法据此修改其 `Alarm[]` / `Warning[]` / `StopReason[]` 数组 |
| `stAlarm` | `ST_Alarm` | VAR_INPUT，3 个 Alarm 类方法 | 输入 alarm 结构：调用方填好 `Id` / `Value` / `Message` / `Category`；`Trigger` / `DateTime` / `AckDateTime` 由方法内部填 |
| `stWarning` | `ST_Alarm` | VAR_INPUT，3 个 Warning 类方法 | Warning 结构（与 Alarm 同型，语义为提醒类）|
| `stStopReason` | `ST_Alarm` | VAR_INPUT，3 个 StopReason 类方法 | 停机原因结构（与 Alarm 同型，语义为分类标签）|

### VAR_INPUT

无（顶层 FB 无 VAR_INPUT；参数见上方"方法共用参数"）。

### VAR_OUTPUT

无（顶层 FB 无 VAR_OUTPUT；各方法各自返回 BOOL）。

### VAR_IN_OUT

无（顶层 FB 无 VAR_IN_OUT；参数见上方"方法共用参数"）。

### 方法列表（9 个）

| 方法 | 操作类别 | 含义 |
|---|---|---|
| [`M_SetAlarm`](M_SetAlarm.md) | Alarm | 写入一条 alarm（`Alarm[].Trigger := TRUE` + 时间戳）|
| [`M_AcknowledgeAlarm`](M_AcknowledgeAlarm.md) | Alarm | 确认 alarm（`Trigger := FALSE` + 记 AckDateTime）|
| [`M_ClearAlarm`](M_ClearAlarm.md) | Alarm | 删除 alarm（被确认过才移入 AlarmHistory）|
| [`M_SetWarning`](M_SetWarning.md) | Warning | 写入一条 warning |
| [`M_AcknowledgeWarning`](M_AcknowledgeWarning.md) | Warning | 确认 warning |
| [`M_ClearWarning`](M_ClearWarning.md) | Warning | 删除 warning |
| [`M_SetStopReason`](M_SetStopReason.md) | StopReason | 写入一条停机原因 |
| [`M_AcknowledgeStopReason`](M_AcknowledgeStopReason.md) | StopReason | 确认停机原因 |
| [`M_ClearStopReason`](M_ClearStopReason.md) | StopReason | 删除停机原因 |

## 3. 行为说明

`PML_AdminAlarm` 把 PackML Admin-Tag 中的三个事件数组抽象成"对象 + 方法"接口，避免应用代码直接操作数组下标。

**数据流向**：方法的 `stAdmin` 参数是 PackML 管理 PackTag 实例（通常是全局 `PackTags.Admin`），方法内部按 PackML 标准修改它的 `Alarm[]` / `Warning[]` / `StopReason[]` / `AlarmHistory[]` 子数组。事件参数 `stAlarm : ST_Alarm` 由调用方填充（Id / Value / Message / Category），方法把 `Trigger` 置位 + 写入 DateTime + 复制 ST_Alarm 各字段。

**时间戳来源**：所有方法读取 `stAdmin.PlcDateTime` 作为时间戳。这意味着 `PML_AdminTime` FB 必须在主程序里周期调用以保证 `PlcDateTime` 是新鲜的，否则时间戳全是上电时刻或 0。

**数组管理策略**：
- `Alarm[]` / `Warning[]` / `StopReason[]` 按 PackML 配置的最大长度（默认 10）做环形数组——满了时插入会顶掉最老的。
- 确认（Acknowledge）不会立即从数组里删除，只是把 Trigger 置 FALSE 并记 AckDateTime；HMI 显示时凭 Trigger 判断"未确认 / 已确认未清除"。
- 清除（Clear）把项目从主数组移入 `AlarmHistory[]`（仅 Alarm 类有 History；Warning 和 StopReason 没有历史数组）。

**事件分类含义**：
- `Alarm` = 故障类，需要操作员明确处理（停机、报错）；
- `Warning` = 提醒类，不影响生产但应记录；
- `StopReason` = 停机分类标签（如"换班停机"、"维护停机"、"故障停机"），用于 OEE/效率统计。

**典型用法**：把 `PML_AdminAlarm` 实例化为全局 `fbAdminAlarm`，故障检测代码调用 `fbAdminAlarm.M_SetAlarm(stAdmin := PackTags.Admin, stAlarm := myAlarm);` 上报；HMI 上"确认"按钮调用 `M_AcknowledgeAlarm`；操作员"清除全部"按钮遍历调用 `M_ClearAlarm`。

## 4. 错误码 / 返回值

FB 自身无返回值；各方法返回 `BOOL`：
- `TRUE` = 操作成功
- `FALSE` = 操作失败（如 Alarm 数组找不到该项、AckDateTime 已存在等）

详见各方法文档。PDF + InfoSys 均未给出 FALSE 的细分原因码（⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- 必须**配合 `PML_AdminTime` 周期调用**——否则方法写入的时间戳全为初始零值。
- `stAdmin` 必须传 PackML PackTags.Admin 实例（或自定义 `ST_PMLa` 实例）；不可传未初始化的 `ST_PMLa`。
- Alarm 与 Warning 用同一个 `ST_Alarm` 结构表示，但 Warning 数组没有 History——不要假设 Warning 也能查历史。（工程经验补充）
- StopReason 用 ST_Alarm 表示但语义是分类标签，建议 Id 用枚举（如 1=换班 / 2=维护 / 3=故障）便于统计。（工程经验补充）
- `M_Set*` 在数组满时自动顶掉最老项——重要 alarm 建议先 Acknowledge+Clear 再 Set 新条目，确保不被覆盖。（工程经验补充）
- 多线程/多任务并发调用同一个 `stAdmin` 可能产生竞争——建议所有 alarm 操作集中在主任务调用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PML_AdminAlarm.TcPOU`](../examples/P_Demo_PML_AdminAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台 24/7 灌装线需要按 OMAC PackML 标准向 MES 上报所有告警、停机原因和报警历史。本 FB + PackML PackTags 结构提供标准化的事件数据布局，MES 通过 OPC UA 订阅 `PackTags.Admin.Alarm[*]` 就能拿到完整事件流（含时间戳、Id、Message、确认状态）。
- **价值**：用本 FB 不必自己设计事件队列、时间戳、确认/清除/历史的逻辑。9 个方法把所有操作覆盖完毕，HMI 与 MES 端的数据契约由 PackML 标准定义，跨厂家可互通。同时配合 `AlarmHistory` 提供完整的故障追溯链。
- **替代方案对比**：自己写 alarm/warning/history 数组+下标管理——代码量大、容易越界、与 PackML 标准命名不一致、跨厂家 MES 接入困难。本 FB 是 OMAC 推荐路径，行业惯例。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298477963.html
- **相关**：`PML_AdminTime`（提供时间戳）、`ST_PMLa`（管理 PackTag 结构）、`ST_Alarm`（事件结构）、`PML_StateMachine`（状态机配合 Alarm 触发 Abort）

## 9. 待确认项 (⚠️)

- 各方法返回 FALSE 的细分原因 PDF + InfoSys 均未列。
