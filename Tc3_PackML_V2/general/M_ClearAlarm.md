# M_ClearAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298997387.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_ClearAlarm.TcPOU`](../examples/P_Demo_M_ClearAlarm.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_ClearAlarm()` **删除**一条 alarm：把 `Alarm[].Trigger` 置 FALSE 并把整条 alarm 从 `Alarm[]` 数组移入 `AlarmHistory[]` 归档。返回 TRUE 表示成功删除。

注意删除依赖前一步 `M_AcknowledgeAlarm` 已被调用——只有 Acknowledge 之后的 alarm 才会真正归档；否则方法只置 `Trigger := FALSE` 但 PDF 标注的"移入 AlarmHistory"行为以确认为前提。若 `AlarmHistory[]` 已满，最老一条被顶掉。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearAlarm : BOOL
VAR_INPUT
  stAlarm          : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAlarm` | `ST_Alarm` | 用于匹配要清除的 alarm 项（按 Id）|

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

`M_ClearAlarm` 完成 alarm 的"归档"阶段：

1. 按 `stAlarm.Id` 在 `stAdmin.Alarm[]` 找匹配项；
2. 若 alarm 已被 Acknowledge（即 `Trigger=FALSE` 且 `AckDateTime≠0`）：把整条 ST_Alarm 拷贝到 `stAdmin.AlarmHistory[]` 队列尾（满时顶掉最老一条）；
3. 把 `Alarm[i]` 置零（Trigger 已是 FALSE，DateTime/AckDateTime 复位为 0 释放槽位）；
4. 返回 TRUE。

**与 Acknowledge 的关系**：PackML 标准建议的工作流是 Set → Acknowledge → Clear 三步。Clear 是终态归档动作；如果跳过 Acknowledge 直接 Clear，PDF 文本写 "Trigger is set to FALSE" 但没说会进 History 数组——⚠️ 实际行为可能依赖实现，建议测试观察。

**典型时序与 `M_AcknowledgeAlarm` 的对比**：
- Acknowledge：alarm 留在 `Alarm[]`，仅置 Trigger=FALSE + 记 AckDateTime。
- Clear：alarm 移入 `AlarmHistory[]`，从 `Alarm[]` 释放槽位。

**调用语义**：调用即执行——不是上升沿触发。HMI"清除全部"按钮通常对所有 acknowledged alarms 遍历调用本方法。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并删除成功 | 通知 HMI 从活动列表移除该项 |
| `FALSE` | 未找到 | 检查 `stAlarm.Id` |

## 5. 使用注意 / 常见坑

- 标准流程是先 Acknowledge 再 Clear——跳过 Acknowledge 直接 Clear 的行为 PDF 未完整描述，⚠️ 建议测试。
- `AlarmHistory[]` 是环形数组，满时顶掉最老一条——审计要求严格的项目建议把历史导出到 MES/数据库后再让它顶替。（工程经验补充）
- 调用即执行，不带触发——HMI"清除"按钮用上升沿触发避免重复。（工程经验补充）
- 配合 `PML_AdminTime` 周期调用——虽然 Clear 不写时间戳，但保持其他方法一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearAlarm.TcPOU`](../examples/P_Demo_M_ClearAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：班次结束时操作员清理已确认的 alarm 列表，触发本方法。已确认的故障归档到 `AlarmHistory[]`，对应 `Alarm[]` 槽位释放给下班次复用。MES 通过 OPC UA 把 `AlarmHistory[]` 数据周期采走存入数据仓库。
- **价值**：标准三阶段处理（Set → Acknowledge → Clear）把"故障实时显示"与"故障历史归档"分开数组管理，活动列表保持简洁、历史保留可查。本方法自动完成"移项+顶老"，应用代码无须关心环形数组细节。
- **替代方案对比**：手写"找位置+复制到 history+清原项"代码——容易遗漏边界（如 history 满时谁顶谁）；不调用 Acknowledge 直接修改 Trigger=FALSE→不符合 ISA-18.2 标准；本方法是 OMAC 推荐路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298997387.html
- **相关**：`PML_AdminAlarm.M_SetAlarm`、`PML_AdminAlarm.M_AcknowledgeAlarm`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- 未先 Acknowledge 直接 Clear 时是否仍移入 AlarmHistory：PDF 文本 "Trigger is set to FALSE" 后未提及，⚠️ 建议测试。
