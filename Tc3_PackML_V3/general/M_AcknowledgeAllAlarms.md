# M_AcknowledgeAllAlarms

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
| Example | [`examples/P_Demo_M_AcknowledgeAllAlarms.TcPOU`](../examples/P_Demo_M_AcknowledgeAllAlarms.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_AcknowledgeAllAlarms()` 一次性确认 PackML Admin-Tag 中**所有**未确认的 alarm。遍历 `Admin.Alarm[]` 数组，对每条 `Trigger=TRUE` 的项把 `Trigger` 置 FALSE、把 `Admin.PlcDateTime` 写入 `AckDateTime`。返回 TRUE 表示全部确认成功。

**V3 新增方法**：V2 版本（`PML_AdminAlarm`）没有此批量方法，只能逐条调 `M_AcknowledgeAlarm`。V3 把"全部确认"做成单方法，HMI 上"全部确认"按钮一行调用即可，省去应用层 for 循环。

为了让 `AckDateTime` 时间戳有效，主程序必须周期调用 `FB_PMLAdminTime`。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeAllAlarms : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Alarm[]`，对所有 Trigger=TRUE 的项 Ack 处理 |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_AcknowledgeAllAlarms` 是 `M_AcknowledgeAlarm` 的批量版本：

1. 遍历 `stAdmin.Alarm[0..cMaxAlarms-1]` 数组；
2. 对每条 `Trigger=TRUE` 的项：把 `Trigger` 置 `FALSE`、`AckDateTime := stAdmin.PlcDateTime`；
3. 全部处理完返回 `TRUE`。

**重要：确认不删除**——和单条 Ack 一样，alarm 仍占用 `Alarm[]` 槽位，直到调用 `M_ClearAllAlarms` 才被批量移入 `AlarmHistory[]`。

**调用语义**：调用即执行——HMI"全部确认"按钮按下时调一次。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。

**返回值含义**：PDF 描述 "If all alarms have been acknowledged, the method returns TRUE."（如全部 alarm 已确认完成则返回 TRUE）。

**典型用法**：HMI 上"全部确认"按钮的事件处理上升沿调一次 `fbAdminAlarm.M_AcknowledgeAllAlarms(stAdmin := PackTags.Admin);`。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 全部 alarm 已确认 | 继续业务 |
| `FALSE` | 部分或全部未确认成功 | 检查 stAdmin 初始化、PlcDateTime 是否更新；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **必须配合 `FB_PMLAdminTime` 周期调用**——否则 AckDateTime 全是初值。
- **确认不删除**——后续要把 alarm 移入 history 必须用 `M_ClearAllAlarms` 或逐条 `M_ClearAlarm`。
- HMI 上"全部确认"按钮强烈建议**上升沿一次性触发**——避免按住按钮每周期重复刷 AckDateTime。
- 同时按"全部确认"+"全部清除"两按钮顺序敏感：先 Ack 后 Clear → alarm 全部移入 AlarmHistory；顺序反过来 PDF 未明示。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeAllAlarms.TcPOU`](../examples/P_Demo_M_AcknowledgeAllAlarms.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：操作员看到 HMI 上挂着 5 条未确认的 alarm，按"全部确认"按钮一次性确认所有项。本方法被调用：所有 alarm 的 Trigger 全部置 FALSE、AckDateTime 全填，但 alarm 行仍留在 HMI（提醒未清除）。
- **价值**：V3 新增的批量方法让 HMI 一键操作免去 for 循环。HMI 程序员不需要遍历 `Alarm[0..9]`，调用单方法即可。
- **替代方案对比**：手写 `FOR i := 0 TO cMaxAlarms-1 DO fbAdminAlarm.M_AcknowledgeAlarm(stAdmin := PackTags.Admin, stAlarm := PackTags.Admin.Alarm[i]); END_FOR` ——代码冗长、循环逻辑可能出错；V3 一行搞定。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.2
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeAlarm`（单条版本）、`M_ClearAllAlarms`（清除批量）、`FB_PMLAdminTime`、`ST_PMLa`

## 9. 待确认项 (⚠️)

- FALSE 返回的细分原因 PDF 未列。
- 数组中部分 alarm 已 Acked 部分未 Acked 时的行为细节 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
