# M_HasStopReason

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `METHOD` |
| Category | `FB_PMLAdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_M_HasStopReason.TcPOU`](../examples/P_Demo_M_HasStopReason.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_HasStopReason()` 检查 PackML Admin-Tag 中当前的 StopReason 是否处于活跃状态（`Trigger=TRUE`）。返回 `TRUE` 表示有未确认的 StopReason；`FALSE` 表示当前无停机原因或已被确认。

**V3 新增方法**：V2 没有此查询方法。

⚠️ **PDF 印刷错误**：PDF §4.2.1.2.3 Syntax 段的方法头被错印为 `METHOD M_SetStopReason : BOOL`（语法段方法名是 SetStopReason，但章节标题和功能描述是 HasStopReason）——以章节标题/示例 `HasStopReason := fbAdminAlarm.M_HasStopReason(...)` 为准。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_HasStopReason : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

> ⚠️ PDF §4.2.1.2.3 Syntax 段把方法头错印为 `METHOD M_SetStopReason : BOOL`——以章节标题 M_HasStopReason 和示例为准。

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法查 `StopReason.Trigger` |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_HasStopReason` 是一个极轻量级的查询方法——直接读取 `stAdmin.StopReason.Trigger` 字段并返回它的布尔值。因为 V3 的 StopReason 是单实例（不是数组），方法内部不需要任何遍历，性能开销几乎为零，适合每个 PLC 周期都调用一次。

返回规则：
- `stAdmin.StopReason.Trigger=TRUE` → 返回 `TRUE`（说明当前有未确认的停机原因）
- `stAdmin.StopReason.Trigger=FALSE` → 返回 `FALSE`（说明 StopReason 已被确认、清除或从未写入）

**PDF §4.2.1.2.3 描述**："This method checks whether an active StopReason is entered in the Admin-Tags and the method returns TRUE"（中文译：检查 Admin-Tags 中是否登记了活跃的 StopReason，是则返回 TRUE）。

**与 alarm/warning 的 Has 方法对比**：那两个需要遍历数组找任意 Trigger=TRUE 项；StopReason 是单值所以直接读一个字段，性能最优。

**调用语义**：纯查询——可每周期调用，无副作用。

**典型用法**：
- HMI 顶端"停机原因待处理"指示灯：`bHmiStopLight := fbAdminAlarm.M_HasStopReason(stAdmin := PackTags.Admin);`
- 状态机判断：`IF NOT fbAdminAlarm.M_HasStopReason(stAdmin := PackTags.Admin) AND NOT fbAdminAlarm.M_HasAlarm(...) THEN ePmlCmd := E_PMLCommand.Reset; END_IF`（"所有事件已处理才允许复位"）。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | StopReason.Trigger = TRUE（有未确认停机原因） |
| `FALSE` | StopReason.Trigger = FALSE（无停机原因或已确认） |

无错误码——纯布尔查询。

## 5. 使用注意 / 常见坑

- 单值语义——只查当前那个 StopReason 字段，没有数组遍历。
- 已 Ack 但未 Clear 的 StopReason 本方法返回 FALSE（因为 Trigger=FALSE）——和 alarm 行为一致。
- 适合每周期调用——读一个 BOOL 而已。
- 与 `M_HasAlarm` 和 `M_HasWarning` 配合可一次性判"机器是否所有事件都已处理完"。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_HasStopReason.TcPOU`](../examples/P_Demo_M_HasStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：状态机检查"是否所有事件已处理"准备从 Stopped 切到 Idle——必须先确认无未处理 alarm/warning/stopReason。本方法每周期返回 StopReason 状态。HMI 用同样调用驱动指示灯。
- **价值**：V3 新增方法把"是否有未确认 StopReason"封装好，调用简洁；HMI 指示灯逻辑直接绑本方法返回值。
- **替代方案对比**：自己写 `bHasStop := stPackTagAdmin.StopReason.Trigger;` 直接读字段——等价但本方法语义更清晰、跟随未来 API 演进。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.2.3
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_SetStopReason`、`M_AcknowledgeStopReason`、`M_ClearStopReason`、`M_HasAlarm`、`M_HasWarning`、`ST_PMLa.StopReason`

## 9. 待确认项 (⚠️)

- PDF §4.2.1.2.3 Syntax 段方法头被错印为 M_SetStopReason，以章节标题/示例为准。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
