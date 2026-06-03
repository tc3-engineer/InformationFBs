# M_ClearAlarm

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
| Example | [`examples/P_Demo_M_ClearAlarm.TcPOU`](../examples/P_Demo_M_ClearAlarm.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_ClearAlarm()` 删除 PackML Admin-Tag 中的一条 alarm：把 `Alarm[].Trigger` 置 FALSE。返回 TRUE 表示删除成功。

**与 Ack 的协作语义**（按 PDF §4.2.1.1.3 描述）：alarm 只有在被 `M_AcknowledgeAlarm` 确认过之后，本方法才会把它移入 `AlarmHistory[]`；未确认的 alarm 调本方法只是清掉 Trigger，不进 history。如果 AlarmHistory 数组已满，最老一条被覆盖。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearAlarm : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
VAR_INPUT
  stAlarm          : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法操作其 `Alarm[]` 和（条件性）`AlarmHistory[]` |
| `stAlarm` | `ST_PMLEvent` | `VAR_INPUT` | 要清除的 alarm 模板（按其 Id 等字段匹配；具体匹配键 PDF 未明示）|

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_ClearAlarm` 实现"清除单条 alarm"流程：

1. 在 `stAdmin.Alarm[]` 中找到与 `stAlarm` 匹配的项（PDF 未明示具体匹配键）；
2. 把该项的 `Trigger` 置 `FALSE`；
3. 如果该项**已被 Ack 过**（即 AckDateTime 已填），则把项从 `Alarm[]` 移入 `AlarmHistory[]`；
4. 若 `AlarmHistory[]` 已满（达到 `cMaxHistoryAlarms` 默认 10），覆盖最老一条；
5. 返回 `TRUE` 表示删除成功。

**Ack 与 Clear 协作**（PDF §4.2.1.1.3 描述）：原文说"The alarm remains in the Alarm array until an M_AcknowledgeAlarm has been called, then it is moved to the AlarmHistory array."——即只有 Ack 过的 alarm 在 Clear 时才进 history。如果先 Clear 没 Ack 的，PDF 没明确是否进 history（⚠️）。

**调用语义**：调用即执行——HMI"清除"按钮按下时调一次。

**与 `M_ClearAllAlarms` 对比**：本方法只清除匹配 stAlarm 的一项；`M_ClearAllAlarms` 一次性清除全部。

**返回值含义**：PDF 说 "The method returns TRUE if the alarm was deleted successfully."（成功删除返回 TRUE）。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 删除成功 | 继续业务 |
| `FALSE` | 未找到或删除失败 | 检查 stAlarm.Id 是否在数组中、stAdmin 是否初始化；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **建议先 Ack 后 Clear**——这样 alarm 进入 AlarmHistory 留下完整审计链；直接 Clear 没 Ack 的 alarm 不会进 history，故障可追溯性差。（工程经验补充）
- AlarmHistory 满时覆盖最老——重要历史 alarm 长期保存建议同步导出到 SQL/MES。
- 匹配键 PDF 未明示——确保每条 alarm Id 唯一，避免歧义删除。（工程经验补充）
- HMI"清除"按钮强烈建议上升沿一次性触发。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearAlarm.TcPOU`](../examples/P_Demo_M_ClearAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：操作员处理完高温故障（关掉热源、温度降回正常），按 HMI"清除"按钮把 alarm 从主显示区移除。本方法被调用：因为之前已经 Ack 过，alarm 被搬入 AlarmHistory；MES 通过 OPC UA 拉 AlarmHistory 做"过去 24 小时故障统计"。
- **价值**：标准化的 alarm 全生命周期（Trigger → Ack → Clear → AlarmHistory），符合 ISA-18.2；故障审计链完整。
- **替代方案对比**：自己写"找 Id+置 Trigger+条件移入 history"——容易遗漏 history 转移逻辑；本方法封装完整。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.3
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeAlarm`（清除前需先 Ack）、`M_ClearAllAlarms`（批量版本）、`ST_PMLa.AlarmHistory`

## 9. 待确认项 (⚠️)

- 未 Ack 直接 Clear 的 alarm 是否进 AlarmHistory PDF 未明示。
- FALSE 返回的细分原因 PDF 未列。
- 匹配键（Id？组合键？）PDF 未明示。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
