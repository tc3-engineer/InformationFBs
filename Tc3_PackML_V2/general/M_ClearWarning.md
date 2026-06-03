# M_ClearWarning

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300095371.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_ClearWarning.TcPOU`](../examples/P_Demo_M_ClearWarning.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_ClearWarning()` 删除一条 warning：把 `Warning[].Trigger` 置 FALSE。返回 TRUE 表示成功删除。

与 Alarm 不同：Warning 没有 History 数组，"清除"在语义上等于把 Trigger 置 FALSE 释放槽位——PDF 直译："The warning remains in the Warning array until it is pushed out of the array by the next warning." —— 即清除后仍占用数组槽位直到被下一条新 warning 物理顶掉。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearWarning : BOOL
VAR_INPUT
  stWarning          : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stWarning` | `ST_Alarm` | 用于匹配要清除的 warning 项（按 Id）|

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

`M_ClearWarning` 的实现逻辑：

1. 按 `stWarning.Id` 在 `stAdmin.Warning[]` 找匹配项；
2. `Warning[i].Trigger := FALSE`；
3. 返回 TRUE；未找到返回 FALSE。

**与 ClearAlarm 的关键区别**：
- `M_ClearAlarm` 把 alarm 移入 `AlarmHistory[]` 归档。
- `M_ClearWarning` 没有 history 归档——仅置 Trigger=FALSE，warning 仍占槽位（被新 warning 顶替时才物理消失）。

PDF 文本明确："The warning remains in the Warning array until it is pushed out of the array by the next warning."

**调用语义**：调用即执行——用 HMI 按钮上升沿触发一次。

**典型用例**：原料桶补到 60%（解除低液位提示）触发本方法；或操作员主动"清掉"已了解的 warning 列表。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并置 Trigger=FALSE 成功 | 通知 HMI 移出活动列表 |
| `FALSE` | 未找到 | 检查 `stWarning.Id` |

## 5. 使用注意 / 常见坑

- Clear 不删除 warning 物理项——只置 Trigger=FALSE。HMI 显示"活动 warning"必须凭 Trigger=TRUE 过滤。（工程经验补充）
- 想要严格"删除"必须等被新 warning 顶替——长期没新 warning 时旧的会一直占槽位。
- 用 HMI 按钮上升沿触发避免重复。
- 配合 `PML_AdminTime` 周期调用（虽然 Clear 不写时间戳）保持一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearWarning.TcPOU`](../examples/P_Demo_M_ClearWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：低液位 warning 在补料后由检测代码自动调用本方法清除；操作员的 HMI 黄色提示自动消失。同样的逻辑用于温度回到正常区间后清除"高温警示"等。
- **价值**：自动化的 warning 清除让 HMI 始终反映"当前真正需要操作员注意的事项"，不会被陈旧提示淹没。
- **替代方案对比**：手动让操作员清除每条 warning——HMI 信息过载、漏清问题；不清除直接覆盖 Trigger——绕过本方法的标准化接口、跨厂家 MES 不识别。本方法是 PackML 推荐路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300095371.html
- **相关**：`PML_AdminAlarm.M_SetWarning`、`PML_AdminAlarm.M_AcknowledgeWarning`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- 是否同时清空 AckDateTime/DateTime 字段 PDF 未明确，⚠️ 建议测试。
