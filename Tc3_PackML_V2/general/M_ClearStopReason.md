# M_ClearStopReason

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300140299.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_ClearStopReason.TcPOU`](../examples/P_Demo_M_ClearStopReason.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_ClearStopReason()` 删除一条 StopReason：把 `StopReason[].Trigger` 置 FALSE。返回 TRUE 表示成功删除。

与 Warning 类似，StopReason 没有 History 数组——清除后 StopReason 仍占用数组槽位直到被下一条新 StopReason 物理顶替。

## 2. 接口定义

> **PDF 印刷瑕疵说明**：PDF §2.3.2.1.9 的 `Syntax` 段把方法头错印成 `METHOD M_ClearAlarm : BOOL`，但章节标题、Sample call、InfoSys 都明确是 `M_ClearStopReason`。VAR_IN_OUT/VAR_INPUT 体正确无误。

### VAR_INPUT

```iecst
METHOD M_ClearStopReason : BOOL
VAR_INPUT
  stStopReason     : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stStopReason` | `ST_Alarm` | 用于匹配要清除的 StopReason 项（按 Id）|

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

`M_ClearStopReason` 的实现逻辑与 `M_ClearWarning` 一致，作用于 `StopReason[]` 数组：

1. 按 `stStopReason.Id` 在 `stAdmin.StopReason[]` 找匹配项；
2. `StopReason[i].Trigger := FALSE`；
3. 返回 TRUE；未找到返回 FALSE。

PDF 直译："The StopReason remains in the StopReason array until it is pushed out of the array by the next StopReason." —— 清除后 StopReason 仍物理留在数组里，等下一条新 StopReason 顶替时才真正消失。

**与 ClearAlarm 的关键区别**：
- `M_ClearAlarm` 把 alarm 移入 `AlarmHistory[]` 归档。
- `M_ClearStopReason` 没有 history 归档——仅置 Trigger=FALSE 释放槽位（虽然物理不消失）。

**调用语义**：调用即执行——用上升沿包裹避免重复。

**典型用例**：换班时把上班次的所有 StopReason 主动清掉、给下班次干净的统计区间；或者在 Reset 流程里清掉旧停机原因。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并置 Trigger=FALSE 成功 | 通知 HMI/MES 移出活动列表 |
| `FALSE` | 未找到 | 检查 `stStopReason.Id` |

## 5. 使用注意 / 常见坑

- PDF 文档头 `Syntax` 段印为 `METHOD M_ClearAlarm`（PDF 印刷错误）；实际方法名 `M_ClearStopReason`，以 InfoSys + Sample call 为准。
- Clear 不删除物理项——只置 Trigger=FALSE。HMI 显示"活动 StopReason"必须凭 Trigger=TRUE 过滤。
- 长期没新 StopReason 时旧的会一直占槽位（直到被顶替）。（工程经验补充）
- 用上升沿触发避免重复。
- 配合 `PML_AdminTime` 周期调用保持一致（虽然 Clear 不写时间戳）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearStopReason.TcPOU`](../examples/P_Demo_M_ClearStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：换班时班长在 HMI 点"清班"按钮，PLC 遍历 `StopReason[]` 调用本方法清掉所有上班次的停机原因，下班次以 OEE 干净统计起步。
- **价值**：让 PackML 状态数据有"清班"的标准化方式，避免新班次混入老数据造成 OEE 失真。
- **替代方案对比**：手写循环改 Trigger——绕过本方法标准接口、跨厂家 MES 不识别；不清除任凭自然顶替——可能 OEE 统计区间被旧数据污染。本方法是 PackML 推荐路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300140299.html
- **相关**：`PML_AdminAlarm.M_SetStopReason`、`PML_AdminAlarm.M_AcknowledgeStopReason`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- PDF §2.3.2.1.9 Syntax 段把方法名误印为 `M_ClearAlarm`；以章节标题与 Sample call 为准。
