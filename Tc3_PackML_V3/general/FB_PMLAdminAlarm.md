# FB_PMLAdminAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `General` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PMLAdminAlarm.TcPOU`](../examples/P_Demo_FB_PMLAdminAlarm.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm` 是 **PackML 管理标签（Admin-PackTags）的报警/告警/停机原因操作 FB**——把 PackML 标准定义的 `Admin.Alarm[]` / `Admin.Warning[]` / `Admin.StopReason` 三个事件容器用方法封装起来：写入、查询、确认（acknowledge）、清除（clear）。

**V3 与 V2 的关键差异**：
- **FB 命名**：V2 叫 `PML_AdminAlarm`，V3 改名为 `FB_PMLAdminAlarm`（统一加 `FB_` 前缀）。
- **方法数量**：V2 有 9 个方法；V3 扩展到 **17 个方法**——为每类事件增加了 "All" 批量操作和 "Has/Get" 查询方法。
- **事件结构类型**：V2 用 `ST_Alarm`；V3 改用 `ST_PMLEvent`（PackML 标准命名）。
- **StopReason 容器**：V2 的 `StopReason[]` 是数组；V3 的 `Admin.StopReason` 是单值（`ST_PMLEvent` 而非数组）——同一时刻只能有一条停机原因，新写入直接覆盖旧值。

本 FB 自身没有 VAR_INPUT/OUTPUT；所有操作通过 17 个方法暴露：3 类事件（Alarm / Warning / StopReason）× 多个操作。每个方法接受 `stAdmin : ST_PMLa`（管理 PackTag 结构）和（对 Set/Ack/Clear 类）事件结构 `ST_PMLEvent` 作为输入，返回 BOOL（部分方法返回 DINT）表示操作结果。

## 2. 接口定义

FB 本身没有顶层 VAR_INPUT/OUTPUT；交互全部通过 17 个方法暴露。所有方法共享 `stAdmin : ST_PMLa` 作为 `VAR_IN_OUT`，部分方法另带 `stAlarm` / `stWarning` / `stStopReason : ST_PMLEvent` 作为 `VAR_INPUT`。

### 方法共用参数

```iecst
(* 所有 17 个方法都共用 stAdmin 作 VAR_IN_OUT *)
VAR_IN_OUT
  stAdmin          : ST_PMLa;        (* 管理 PackTag，方法读写它的 Alarm/Warning/StopReason *)
END_VAR
VAR_INPUT
  (* Alarm 类需事件结构的方法：M_SetAlarm / M_AcknowledgeAlarm / M_ClearAlarm *)
  stAlarm          : ST_PMLEvent;
  (* Warning 类需事件结构的方法：M_SetWarning / M_AcknowledgeWarning / M_ClearWarning *)
  stWarning        : ST_PMLEvent;
  (* StopReason 类需事件结构的方法：M_SetStopReason *)
  stStopReason     : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT`，全部 17 个方法 | PackML 管理 PackTag 实例（通常是全局 `PackTags.Admin`），方法据此修改其 `Alarm[]` / `Warning[]` / `StopReason` |
| `stAlarm` | `ST_PMLEvent` | `VAR_INPUT`，3 个 Alarm 类操作方法 | 输入 alarm 结构：调用方填好 `Id` / `Value` / `Message` / `Category`；`Trigger` / `DateTime` / `AckDateTime` 由方法内部填 |
| `stWarning` | `ST_PMLEvent` | `VAR_INPUT`，3 个 Warning 类操作方法 | Warning 结构（与 Alarm 同型，语义为提醒类）|
| `stStopReason` | `ST_PMLEvent` | `VAR_INPUT`，1 个 M_SetStopReason | 停机原因结构（与 Alarm 同型，语义为分类标签）|

### VAR_INPUT

无（顶层 FB 无 VAR_INPUT；参数见上方"方法共用参数"）。

### VAR_OUTPUT

无（顶层 FB 无 VAR_OUTPUT；各方法各自返回 BOOL 或 DINT）。

### VAR_IN_OUT

无（顶层 FB 无 VAR_IN_OUT；参数见上方"方法共用参数"）。

### 方法列表（17 个）

**Alarm 类（7 个，PDF §4.2.1.1）**：

| 方法 | 含义 | 返回 |
|---|---|---|
| [`M_SetAlarm`](M_SetAlarm.md) | 写入一条 alarm | `BOOL` |
| [`M_AcknowledgeAlarm`](M_AcknowledgeAlarm.md) | 确认指定 alarm | `BOOL` |
| [`M_AcknowledgeAllAlarms`](M_AcknowledgeAllAlarms.md) | 一次确认全部 alarm | `BOOL` |
| [`M_ClearAlarm`](M_ClearAlarm.md) | 删除指定 alarm（被确认过移入 AlarmHistory）| `BOOL` |
| [`M_ClearAllAlarms`](M_ClearAllAlarms.md) | 一次清除全部 alarm | `BOOL` |
| [`M_GetAlarmCategory`](M_GetAlarmCategory.md) | 取当前最高优先级 alarm 的 Category | `DINT` |
| [`M_HasAlarm`](M_HasAlarm.md) | 查询是否存在未处理 alarm | `BOOL` |

**StopReason 类（4 个，PDF §4.2.1.2）**：

| 方法 | 含义 | 返回 |
|---|---|---|
| [`M_SetStopReason`](M_SetStopReason.md) | 写入停机原因 | `BOOL` |
| [`M_AcknowledgeStopReason`](M_AcknowledgeStopReason.md) | 确认停机原因 | `BOOL` |
| [`M_ClearStopReason`](M_ClearStopReason.md) | 删除停机原因 | `BOOL` |
| [`M_HasStopReason`](M_HasStopReason.md) | 查询是否有未处理停机原因 | `BOOL` |

**Warning 类（6 个，PDF §4.2.1.3）**：

| 方法 | 含义 | 返回 |
|---|---|---|
| [`M_SetWarning`](M_SetWarning.md) | 写入一条 warning | `BOOL` |
| [`M_AcknowledgeWarning`](M_AcknowledgeWarning.md) | 确认指定 warning | `BOOL` |
| [`M_AcknowledgeAllWarning`](M_AcknowledgeAllWarning.md) | 一次确认全部 warning | `BOOL` |
| [`M_ClearWarning`](M_ClearWarning.md) | 删除指定 warning | `BOOL` |
| [`M_ClearAllWarning`](M_ClearAllWarning.md) | 一次清除全部 warning | `BOOL` |
| [`M_HasWarning`](M_HasWarning.md) | 查询是否存在未处理 warning | `BOOL` |

## 3. 行为说明

`FB_PMLAdminAlarm` 把 PackML Admin-Tag 中的三个事件容器抽象成"对象 + 方法"接口，避免应用代码直接操作数组下标。

**数据流向**：方法的 `stAdmin` 参数是 PackML 管理 PackTag 实例（通常是全局 `PackTags.Admin`），方法内部按 PackML 标准修改它的 `Alarm[]` / `Warning[]` / `StopReason` / `AlarmHistory[]` 子结构。事件参数 `stAlarm : ST_PMLEvent` 由调用方填充（`Id` / `Value` / `Message` / `Category`），方法把 `Trigger` 置位 + 写入 `DateTime` + 复制 ST_PMLEvent 各字段。

**时间戳来源**：所有 Set/Acknowledge 方法读取 `stAdmin.PlcDateTime` 作为时间戳。这意味着 `FB_PMLAdminTime` 必须在主程序里周期调用以保证 `PlcDateTime` 是新鲜的，否则时间戳全是上电时刻或 0。

**数组管理策略**（基于 PDF 描述）：
- `Alarm[]` / `Warning[]` 按 PackML 配置的最大长度（`cMaxAlarms` / `cMaxWarnings`，默认 10）做容器。
- 确认（Acknowledge）不会立即从容器里删除，只是把 `Trigger` 置 FALSE 并记 `AckDateTime`；HMI 显示时凭 `Trigger` 判断"未确认 / 已确认未清除"。
- 清除（Clear）只对**已确认**的 Alarm 有 history 转移：把项目从 `Alarm[]` 移入 `AlarmHistory[]`（仅 Alarm 类有 History；Warning 和 StopReason 没有历史容器）。
- Warning 数组满时新写入会**顶出最老 warning**；Alarm 数组满时 PDF 仅在 AlarmHistory 描述了"溢出删最老"，主 Alarm 数组的满处理 PDF 未详细描述。
- StopReason 是单实例（`ST_PMLEvent` 而非数组）——新写入直接覆盖旧值，没有溢出概念。

**事件分类含义**：
- `Alarm` = 故障类，需要操作员明确处理（停机、报错）；
- `Warning` = 提醒类，不影响生产但应记录；
- `StopReason` = 停机分类标签（如"换班停机"、"维护停机"、"故障停机"），用于 OEE/效率统计。

**V3 新增的"All/Has/Get"系列方法**意义：
- `M_AcknowledgeAllAlarms` / `M_ClearAllAlarms` / `M_AcknowledgeAllWarning` / `M_ClearAllWarning`：HMI 上"全部确认 / 全部清除"按钮一键调用，省去应用层 for 循环遍历。
- `M_HasAlarm` / `M_HasWarning` / `M_HasStopReason`：状态机判断"现在能不能切到 Idle"等条件时一句调用，比自己遍历数组判断 `Trigger=TRUE` 简洁。
- `M_GetAlarmCategory`：HMI 红绿灯指示——根据当前最高优先级 alarm 的 Category 决定显示颜色（如 1=红/2=橙/3=黄）。

**典型用法**：把 `FB_PMLAdminAlarm` 实例化为全局 `fbAdminAlarm`，故障检测代码上升沿触发调用 `fbAdminAlarm.M_SetAlarm(stAdmin := PackTags.Admin, stAlarm := myAlarm);` 上报；HMI 上"确认全部"按钮调用 `fbAdminAlarm.M_AcknowledgeAllAlarms(stAdmin := PackTags.Admin);`；状态机条件用 `IF fbAdminAlarm.M_HasAlarm(stAdmin := PackTags.Admin) THEN ...` 判断。

## 4. 错误码 / 返回值

FB 自身无返回值；各方法返回 `BOOL`（部分如 `M_GetAlarmCategory` 返回 `DINT`）：
- `TRUE` = 操作成功
- `FALSE` = 操作失败（如指定 alarm 找不到、容器为空等）

详见各方法文档。PDF 均未给出 FALSE 的细分原因码（⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- 必须**配合 `FB_PMLAdminTime` 周期调用**——否则方法写入的 `DateTime` 全为初始零值。
- `stAdmin` 必须传 PackML `PackTags.Admin` 实例（或自定义 `ST_PMLa` 实例）；不可传未初始化的 `ST_PMLa`。
- V3 的 `StopReason` 不是数组——一次只能存一条停机原因；新 SetStopReason 直接覆盖旧的。这与 V2（StopReason 是数组）行为不同；从 V2 升级时检查相关代码。
- Alarm 与 Warning 用同一个 `ST_PMLEvent` 结构表示，但 Warning 数组没有 History——不要假设 Warning 也能查历史。（工程经验补充）
- `M_Set*` 在数组满时按 PackML 标准的环形/溢出规则处理；重要 alarm 建议先 Acknowledge+Clear 再 Set 新条目，确保不被覆盖。（工程经验补充）
- 多任务并发调用同一个 `stAdmin` 可能产生竞争——建议所有 alarm 操作集中在主任务调用。（工程经验补充）
- V3 比 V2 多 8 个方法（All/Has/Get 系列）——升级时可以利用新方法简化 HMI 按钮代码。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PMLAdminAlarm.TcPOU`](../examples/P_Demo_FB_PMLAdminAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台 24/7 灌装线需要按 OMAC PackML 标准向 MES 上报所有告警、停机原因和报警历史。本 FB + PackML PackTags 结构提供标准化的事件数据布局，MES 通过 OPC UA 订阅 `PackTags.Admin.Alarm[*]` 就能拿到完整事件流（含时间戳、Id、Message、确认状态）。V3 新增的 "All/Has/Get" 方法让 HMI 一键操作和状态机查询更简洁。
- **价值**：用本 FB 不必自己设计事件队列、时间戳、确认/清除/历史的逻辑。17 个方法把所有操作覆盖完毕，HMI 与 MES 端的数据契约由 PackML 标准定义，跨厂家可互通。同时配合 `AlarmHistory` 提供完整的故障追溯链。
- **替代方案对比**：自己写 alarm/warning/history 数组+下标管理——代码量大、容易越界、与 PackML 标准命名不一致、跨厂家 MES 接入困难。本 FB 是 OMAC 推荐路径，行业惯例。V3 比 V2 又方便：不必为常见操作（确认全部、查询有无）写 for 循环。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic，与本 FB 同属 §4.2 General 章节；V3 本 FB 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminTime`（提供时间戳）、`ST_PMLa`（管理 PackTag 结构）、`ST_PMLEvent`（事件结构）、`FB_PMLStateMachine`（状态机配合 Alarm 触发 Abort）

## 9. 待确认项 (⚠️)

- 各方法返回 FALSE 的细分原因 PDF 均未列。
- Alarm 主数组（非 AlarmHistory）满时的处理 PDF 文本未详细描述。
- V3 InfoSys 本 FB 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
