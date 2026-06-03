# M_GetAlarmCategory

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
| Example | [`examples/P_Demo_M_GetAlarmCategory.TcPOU`](../examples/P_Demo_M_GetAlarmCategory.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_GetAlarmCategory()` 返回 PackML Admin-Tag 中**当前最高优先级**（数值最小）alarm 的 `Category` 字段。

按 PackML/ISA-18.2 惯例：Category 数值越小优先级越高（1=Critical/2=Major/3=Minor 等）。本方法遍历 `Alarm[]` 中所有 `Trigger=TRUE` 的项找出 Category 最小值返回。

**V3 新增方法**：V2 没有此查询方法，HMI 红绿灯指示必须自己遍历数组取最小。

⚠️ PDF 说本方法 "returns the highest AlarmCategory (smallest value)"——但 `METHOD M_GetAlarmCategory : BOOL` 的语法段显示返回类型是 BOOL；正文又强调返回 DINT 数值。PDF 文档此处**类型描述不一致**，以 PDF 的功能描述（DINT 数值）和示例（`AlarmCategory := fbAdminAlarm.M_GetAlarmCategory(...);` 接 DINT 变量）为准——实际返回 DINT。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_GetAlarmCategory : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

> ⚠️ PDF 头部把返回类型写成 `BOOL`，与功能描述（返回 Category 数值）矛盾；正文示例和功能描述都把返回值当 DINT 使用。**实际返回类型以 PLC 编辑器中实测为准**。

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Alarm[]` 找最高优先级 |

### VAR_OUTPUT

无（返回值通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_GetAlarmCategory` 遍历 `stAdmin.Alarm[0..cMaxAlarms-1]`，对每条 `Trigger=TRUE` 的项读 `Category`，返回这些 Category 中的最小值。

**Category 语义**（PackML/ISA-18.2 惯例）：
- 1 = Critical（最高优先级）
- 2 = Major
- 3 = Minor
- 数值越大优先级越低

**当前无 alarm 时返回值**：PDF 未明示——可能返回 0 或某个最大值。⚠️ 实测确认。建议调用前先用 `M_HasAlarm` 判断。

**调用语义**：纯查询——多次调用返回相同结果（除非 alarm 状态变化）。可每周期调用。

**典型用法**：HMI 红绿灯指示——`nCategory := fbAdminAlarm.M_GetAlarmCategory(stAdmin := PackTags.Admin); CASE nCategory OF 1: bLightRed := TRUE; 2: bLightOrange := TRUE; ... END_CASE`。

## 4. 错误码 / 返回值

返回最高优先级 alarm 的 `Category` 数值（DINT，PDF 功能描述）。

⚠️ PDF 头部声明返回 `BOOL`——与正文/示例矛盾。实际返回类型以 PLC 编辑器中实测为准。

当前无 alarm 时的返回值 PDF 未列（⚠️ 实测）。

## 5. 使用注意 / 常见坑

- ⚠️ **返回类型 PDF 写法不一致**——`METHOD M_GetAlarmCategory : BOOL` 但正文描述和示例当 DINT 用。实测以 PLC 编辑器为准。
- 当前无 alarm 时返回值 PDF 未明示——建议先调 `M_HasAlarm` 判断有无 alarm 再调本方法。
- Category 编号是应用层自己定义的——本方法只返回最小值，业务含义由应用约定（默认推荐 1=最严重、按 ISA-18.2 标准）。
- 适合每周期调用——HMI 红绿灯指示实时响应。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_GetAlarmCategory.TcPOU`](../examples/P_Demo_M_GetAlarmCategory.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 顶端的状态灯（红/橙/黄/绿）实时反映当前最严重 alarm 的等级。本方法每周期调用，根据返回 Category 决定灯色。MES 收到这个值也能做生产线优先级排序。
- **价值**：V3 新增方法把"找最高优先级 alarm 等级"封装好，HMI 不必自己遍历 Alarm[] 数组。
- **替代方案对比**：自己写 for 循环遍历 + 取 MIN(Category)——代码冗长；本方法一行搞定。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.5
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_HasAlarm`（先判有无再取 Category）、`ST_PMLEvent.Category`、`ST_PMLa.Alarm`

## 9. 待确认项 (⚠️)

- **PDF 头部 METHOD 返回类型 BOOL 与功能描述/示例返回 DINT 矛盾**——实际类型以 PLC 编辑器实测为准。
- 当前无 alarm 时的返回值 PDF 未明示。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
