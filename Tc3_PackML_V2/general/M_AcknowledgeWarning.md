# M_AcknowledgeWarning

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300081163.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_AcknowledgeWarning.TcPOU`](../examples/P_Demo_M_AcknowledgeWarning.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_AcknowledgeWarning()` 确认一条 warning：`Warning[].Trigger := FALSE`、`Warning[].AckDateTime := Admin.PlcDateTime`。返回 TRUE 表示成功找到并确认。

与 Alarm 不同的是：warning 被确认后**仍留在 `Warning[]` 数组**直到被下一条新 warning 顶掉——没有 Clear 后的 History 归档机制。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeWarning : BOOL
VAR_INPUT
  stWarning        : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stWarning` | `ST_Alarm` | 用于匹配要确认的 warning 项（按 Id）|

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

`M_AcknowledgeWarning` 实现与 `M_AcknowledgeAlarm` 一致的确认逻辑，但作用于 `Warning[]` 数组：

1. 按 `stWarning.Id` 在 `stAdmin.Warning[]` 找匹配项；
2. 找到后：`Warning[i].Trigger := FALSE`、`Warning[i].AckDateTime := stAdmin.PlcDateTime`；
3. 返回 TRUE；未找到返回 FALSE。

**与 Alarm 的关键区别**：
- Alarm 三阶段：Set → Ack → Clear（移入 History）
- Warning 两阶段：Set → Ack（仅置标志和时间戳，仍留 Warning[]）

PDF 直译："The warning remains in the Warning array until it is pushed out of the array by the next warning." —— 确认后 warning 留在数组里，直到下一条新 warning 把它顶掉。

**调用语义**：调用即执行——用 HMI 按钮上升沿触发一次。

**时间戳依赖**：保证 `PML_AdminTime` 周期调用。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并确认成功 | 通知 HMI 刷新确认状态 |
| `FALSE` | 未找到 | 检查 `stWarning.Id` |

## 5. 使用注意 / 常见坑

- Warning 没有 Clear→History 流程；确认后 warning 仍占用槽位直到被顶替。（工程经验补充）
- 如果操作员从未确认过的 warning 被顶掉，AckDateTime 永远为 0——可作为 HMI 区分"曾被看到"和"被悄悄顶替"的依据。（工程经验补充）
- 用 HMI 按钮上升沿触发避免重复。
- 配合 `PML_AdminTime` 周期调用确保 AckDateTime 有效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeWarning.TcPOU`](../examples/P_Demo_M_AcknowledgeWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：操作员看到 "Material level approaching minimum" 黄色提示后点"了解"按钮——本方法被调用，HMI 把警示改为半透明显示但不消失，提醒操作员补料还在 todo 列表里。
- **价值**：让 warning 也有 acknowledge 时间戳，便于审计"操作员什么时候开始知道这条提示"。区分"全新出现"和"已确认未消失"两种状态符合操作员心智模型。
- **替代方案对比**：不实现 warning ack——HMI 没法清掉黄色提示让人焦虑；直接把 warning 删了——失去"操作员已了解"信息。本方法是 PackML 推荐路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300081163.html
- **相关**：`PML_AdminAlarm.M_SetWarning`、`PML_AdminAlarm.M_ClearWarning`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- 匹配规则细节（仅 Id 还是 Id+其他字段）PDF + InfoSys 均未明确。
