# M_AcknowledgeAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298615435.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_AcknowledgeAlarm.TcPOU`](../examples/P_Demo_M_AcknowledgeAlarm.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_AcknowledgeAlarm()` **确认**一条已触发的 alarm：把 `Alarm[].Trigger` 置 FALSE、从 `Admin.PlcDateTime` 读取并写入 `Alarm[].AckDateTime`。返回 TRUE 表示成功找到并确认了对应 alarm。

确认 alarm **不会删除它**——alarm 仍留在 `Alarm[]` 数组里直到调用 `M_ClearAlarm` 才移入 `AlarmHistory[]`（移入时若 History 数组已满会顶掉最老一条）。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeAlarm : BOOL
VAR_INPUT
  stAlarm          : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAlarm` | `ST_Alarm` | 用于匹配要确认的 alarm 项（通常用 `Id` 字段定位）|

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

`M_AcknowledgeAlarm` 实现 alarm 确认（acknowledge）的标准流程：

1. 在 `stAdmin.Alarm[]` 数组里按 `stAlarm.Id` 找匹配项；
2. 找到后：`Alarm[i].Trigger := FALSE`、`Alarm[i].AckDateTime := stAdmin.PlcDateTime`；
3. 返回 TRUE；未找到则返回 FALSE。

**与 ClearAlarm 的区别**：Acknowledge 只是"操作员承认看到了"，alarm 仍占用 `Alarm[]` 槽位；Clear 才把 alarm 移到 `AlarmHistory[]`。这种两阶段处理符合 ISA-18.2 报警管理标准。

**典型时序**：
- 时刻 T0：故障检测代码调用 `M_SetAlarm` → `Alarm[i] = {Trigger:TRUE, DateTime:T0, AckDateTime:0}`
- 时刻 T1：操作员在 HMI 点"确认"按钮 → 调用 `M_AcknowledgeAlarm` → `Alarm[i] = {Trigger:FALSE, DateTime:T0, AckDateTime:T1}`
- 时刻 T2：操作员点"清除"按钮 → 调用 `M_ClearAlarm` → alarm 移入 `AlarmHistory[]`

**时间戳依赖**：与 `M_SetAlarm` 同理，必须保证 `PML_AdminTime` 周期调用以让 `PlcDateTime` 新鲜。

**调用语义**：调用即执行——不是上升沿触发。建议用 HMI 按钮的上升沿触发一次性调用。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并确认成功 | 通知 HMI 刷新确认状态 |
| `FALSE` | 未找到匹配项 | 检查 `stAlarm.Id` 是否对应活动 alarm（可能已被 Clear 或不存在）|

## 5. 使用注意 / 常见坑

- 用 `stAlarm.Id` 作为匹配 key——必须与 `M_SetAlarm` 时的 Id 一致才能确认。（工程经验补充）
- Acknowledge **不删除** alarm，只置 Trigger=FALSE。HMI 在 alarm 列表上画"已确认未清除"状态需要凭 `Trigger=FALSE` + `AckDateTime≠0` 组合判断。（工程经验补充）
- 多次 Acknowledge 同一 alarm 会刷新 `AckDateTime`，建议用 HMI 按钮上升沿触发一次。（工程经验补充）
- 配合 `PML_AdminTime` 周期调用确保时间戳有效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeAlarm.TcPOU`](../examples/P_Demo_M_AcknowledgeAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：包装机产生 "纸张卡住" alarm，操作员处理完故障后在 HMI 点"确认"按钮，触发本方法。alarm 仍留在列表里（带"已确认"标记），等班次结束统一清除归档。
- **价值**：标准两阶段处理（acknowledge + clear）符合 ISA-18.2 报警管理标准，便于审计——可以查询"故障被操作员看到的时间"和"故障被清理归档的时间"。本方法把"找位置+置标志+写时间戳"自动化，应用代码只需调一次。
- **替代方案对比**：HMI 直接把 `Trigger := FALSE` 改了——没有 AckDateTime 时间戳、不符合标准、审计困难。本方法是 OMAC PackML 推荐路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298615435.html
- **相关**：`PML_AdminAlarm.M_SetAlarm`、`PML_AdminAlarm.M_ClearAlarm`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- 匹配 alarm 的具体规则（仅 Id 还是 Id+Value+其他）PDF + InfoSys 均未明确，⚠️ 建议测试观察。
