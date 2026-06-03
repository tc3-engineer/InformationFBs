# M_AcknowledgeStopReason

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300126091.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_AcknowledgeStopReason.TcPOU`](../examples/P_Demo_M_AcknowledgeStopReason.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_AcknowledgeStopReason()` 确认一条 StopReason：`StopReason[].Trigger := FALSE`、`StopReason[].AckDateTime := Admin.PlcDateTime`。返回 TRUE 表示成功找到并确认。

与 Warning 类似，StopReason 被确认后**仍留在 `StopReason[]` 数组**直到被下一条新 StopReason 顶掉。

## 2. 接口定义

> **PDF 印刷瑕疵说明**：PDF §2.3.2.1.8 的 `Syntax` 段把方法头错印成 `METHOD M_AcknowledgeAlarm : BOOL`，但章节标题、Sample call、InfoSys 都明确是 `M_AcknowledgeStopReason`。VAR_IN_OUT/VAR_INPUT 体正确无误。

### VAR_INPUT

```iecst
METHOD M_AcknowledgeStopReason : BOOL
VAR_INPUT
  stStopReason     : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stStopReason` | `ST_Alarm` | 用于匹配要确认的 StopReason 项（按 Id）|

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAdmin` | `ST_PMLa` | PackML 管理 PackTag 结构 |

## 3. 行为说明

`M_AcknowledgeStopReason` 与 `M_AcknowledgeAlarm / M_AcknowledgeWarning` 实现一致的确认逻辑，作用于 `StopReason[]` 数组：

1. 按 `stStopReason.Id` 在 `stAdmin.StopReason[]` 找匹配项；
2. 找到后：`StopReason[i].Trigger := FALSE`、`StopReason[i].AckDateTime := stAdmin.PlcDateTime`；
3. 返回 TRUE；未找到返回 FALSE。

**语义说明**：StopReason 是"停机原因标签"。Acknowledge 在这里通常表示"操作员/MES 已确认这条停机原因已被记录"。PDF 直译："The StopReason remains in the StopReason array until it is pushed out of the array by the next StopReason." —— 确认后 StopReason 留在数组里，直到新 StopReason 物理顶替它。

**调用语义**：调用即执行——用 HMI 或 MES 通知的上升沿触发一次。

**典型用例**：MES 把 StopReason 数据采走后，通过 ADS 发指令让 PLC 把对应 StopReason 标为已确认（避免下次重复采集）；或者操作员复班时一次性确认上班的所有停机原因。

**时间戳依赖**：保证 `PML_AdminTime` 周期调用。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并确认成功 | 通知 HMI/MES 刷新状态 |
| `FALSE` | 未找到 | 检查 `stStopReason.Id` |

## 5. 使用注意 / 常见坑

- PDF 文档头 `Syntax` 段印为 `METHOD M_AcknowledgeAlarm`（PDF 印刷错误）；实际方法名 `M_AcknowledgeStopReason`，以 InfoSys + Sample call 为准。
- StopReason 没有 Clear→History 流程，AckDateTime 是仅有的"已确认"标记。
- 用上升沿触发避免重复确认。
- 配合 `PML_AdminTime` 周期调用确保 AckDateTime 有效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeStopReason.TcPOU`](../examples/P_Demo_M_AcknowledgeStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：MES 在每班次结束后通过 ADS 调用本方法把所有 StopReason 标为已确认，下班次的 OEE 统计从干净的状态开始。或者操作员复班时一次性确认上班的所有停机记录。
- **价值**：标准化"停机原因已被消费"的标记，避免 MES 重复采集；配合 AckDateTime 可以反向查询"哪条停机原因 MES 多久才处理"，作为信息系统响应性指标。
- **替代方案对比**：MES 自己记"上次采到哪条"——状态分散容易丢；用全局变量标记 —— 不符合 PackML 标准、跨系统不互通。本方法是 OMAC 推荐路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300126091.html
- **相关**：`PML_AdminAlarm.M_SetStopReason`、`PML_AdminAlarm.M_ClearStopReason`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- PDF §2.3.2.1.8 Syntax 段把方法名误印为 `M_AcknowledgeAlarm`；以章节标题与 Sample call 为准。
