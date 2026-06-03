# M_AcknowledgeAlarm

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
| Example | [`examples/P_Demo_M_AcknowledgeAlarm.TcPOU`](../examples/P_Demo_M_AcknowledgeAlarm.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_AcknowledgeAlarm()` 确认 PackML Admin-Tag 中的一条 alarm：在 `Admin.Alarm[]` 数组中匹配传入 `stAlarm` 对应的项，把 `Alarm[].Trigger` 置 FALSE、从 `Admin.PlcDateTime` 读取并写入 `Alarm[].AckDateTime`，返回 TRUE 表示找到并确认成功。

**关键语义**：**确认不等于删除**——alarm 仍保留在 `Alarm[]` 中（仅 Trigger 标记为已确认），直到 `M_ClearAlarm` 被调用才会被移入 `AlarmHistory[]`。HMI 凭 `Trigger=FALSE && AckDateTime!=零` 区分"已确认未清除"状态。

为了让 `AckDateTime` 时间戳有效，主程序必须周期调用 `FB_PMLAdminTime`。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeAlarm : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
VAR_INPUT
  stAlarm          : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法读取 `PlcDateTime` 作时间戳、把对应 alarm 的 Trigger 置 FALSE + 填 AckDateTime |
| `stAlarm` | `ST_PMLEvent` | `VAR_INPUT` | 要确认的 alarm 模板（用其 `Id` 等字段匹配 `Admin.Alarm[*]` 中的项；具体匹配规则 PDF 未明示，⚠️ 推测按 Id 匹配）|

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_AcknowledgeAlarm` 实现"操作员确认单条 alarm"的标准流程：

1. 在 `stAdmin.Alarm[]` 数组中根据 `stAlarm` 的标识字段（最可能是 `Id`，PDF 未明示具体匹配键）找到对应项；
2. 把该项的 `Trigger` 置 `FALSE`；
3. 把 `stAdmin.PlcDateTime`（7 字段 ST_PMLDateAndTime）拷贝到 `Alarm[i].AckDateTime`；
4. 返回 `TRUE` 表示找到并已确认。

**重要：确认不删除**——alarm 仍占用 `Alarm[]` 槽位，直到 `M_ClearAlarm` 被调用。这是 PackML 标准设计：HMI 上"红条变绿条"表示已确认；"绿条消失"才表示已清除（移入 history）。这套两阶段（Ack → Clear）符合 ISA-18.2 报警管理标准。

**调用语义**：调用即执行——不是上升沿触发。每次操作员按"确认"按钮调一次。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。如果 `FB_PMLAdminTime` 没在主任务里调用，`AckDateTime` 全部为 0 或上电初值。

**与 `M_AcknowledgeAllAlarms` 对比**：本方法只确认匹配 `stAlarm` 的一项；`M_AcknowledgeAllAlarms` 一次性确认所有 `Trigger=TRUE` 的 alarm（HMI"全部确认"按钮专用）。

**返回值含义**：PDF 说返回 TRUE = 找到且确认成功。FALSE 的可能原因（PDF 未列）⚠️：传入 `stAlarm.Id` 在数组里没找到、PlcDateTime 未初始化等。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并确认成功 | 继续业务 |
| `FALSE` | 未找到该 alarm 或确认失败 | 检查 stAlarm.Id 是否正确、stAdmin 是否初始化、PlcDateTime 是否在更新；PDF 未列具体原因（⚠️ 待人工确认）|

## 5. 使用注意 / 常见坑

- **必须配合 `FB_PMLAdminTime` 周期调用**——否则 AckDateTime 全是初值。
- **确认不删除**——HMI"确认"按钮只把 alarm 标记为已确认；"清除"按钮才把它移入 AlarmHistory。这是 PackML 标准设计。
- 匹配键 PDF 未明示是 Id 还是组合键（Id+Category 等）——⚠️ 实测确认。最稳妥做法是确保每条 alarm 的 Id 唯一。（工程经验补充）
- 数组里多条 Id 相同的 alarm 时本方法只会确认匹配到的第一项；想全部确认用 `M_AcknowledgeAllAlarms`。（工程经验补充）
- 与 `M_ClearAlarm` 顺序：先 Ack 再 Clear → alarm 移入 AlarmHistory；先 Clear 再 Ack → 行为 PDF 未明示（⚠️）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeAlarm.TcPOU`](../examples/P_Demo_M_AcknowledgeAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：操作员看到 HMI 上一条高温 alarm，按"确认"按钮告诉系统"我看到了，正在处理"。本方法被调用：alarm 在数组中标记为已确认，但仍占用 HMI 显示行（提醒操作员未清除），直到处理完成再按"清除"。
- **价值**：标准化的两阶段（Ack → Clear）报警生命周期管理，符合 ISA-18.2 报警标准；HMI 不需要自己写"已确认未清除"状态逻辑。
- **替代方案对比**：自己写"遍历数组找 Id+置 Trigger=FALSE"代码——容易遗漏 AckDateTime 写入、不符合 PackML 标准。本方法是 OMAC 推荐写法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.1
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic，同 §4.2 General 章节；本 METHOD 自身 InfoSys topic 页面公网未检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`（parent FB）、`M_AcknowledgeAllAlarms`（批量版本）、`M_SetAlarm`（写入）、`M_ClearAlarm`（清除）、`FB_PMLAdminTime`（提供 PlcDateTime）、`ST_PMLEvent`、`ST_PMLa`

## 9. 待确认项 (⚠️)

- 数组中匹配 stAlarm 的具体键（Id？Id+Category？）PDF 未明示。
- FALSE 返回的细分原因 PDF 未列。
- 先 Clear 再 Ack 的行为 PDF 未明示。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
