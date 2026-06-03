# M_ClearStopReason

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
| Example | [`examples/P_Demo_M_ClearStopReason.TcPOU`](../examples/P_Demo_M_ClearStopReason.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_ClearStopReason()` 删除 PackML Admin-Tag 中当前的 StopReason：把 `Admin.StopReason.Trigger` 置 FALSE。返回 TRUE 表示删除成功。

**V3 单值语义**：因为 V3 把 StopReason 改为单值（非数组），本方法不需要传 `stStopReason` 参数——直接清除当前那个。

**PDF §4.2.1.2.2 描述**："The StopReason remains in the Admin-Tags until it is replaced by a subsequent StopReason."（StopReason 留在 Admin-Tag 直到被下一个 StopReason 覆盖）——意思是 Clear 后内容仍在 `Admin.StopReason` 字段，只是 Trigger=FALSE 表示已被清除。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearStopReason : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法把 `StopReason.Trigger` 置 FALSE |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_ClearStopReason` 实现"清除当前 StopReason"流程：

1. `stAdmin.StopReason.Trigger := FALSE`；
2. 返回 `TRUE` 表示清除成功。

**重要：内容仍在**——Id / Message / Category / DateTime 字段不变，只是 Trigger=FALSE。下一次 `M_SetStopReason` 覆盖字段；或下一次 `M_HasStopReason` 返回 FALSE。

**与 Alarm Clear 的差异**：Alarm 的 Clear 在已 Ack 情况下把 alarm 移入 AlarmHistory；StopReason 没有 history 数组——清除后内容滞留在 StopReason 字段直到被新值覆盖。

**调用语义**：调用即执行——HMI"清除"按钮按下时调一次。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 清除成功 | 继续业务 |
| `FALSE` | 清除失败 | 检查 stAdmin 是否初始化；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- StopReason 没有 history——Clear 后字段仍保留旧值，但 Trigger=FALSE，`M_HasStopReason` 返回 FALSE。
- 如果业务要"清除后字段也归零"——应用层调本方法后手动 `stPackTagAdmin.StopReason := DEFAULT;`，但这破坏了 PDF 描述的"留到被覆盖"语义。（工程经验补充）
- 与 `M_SetStopReason` 配合：新写 StopReason 自动覆盖旧值——通常不需要先 Clear 再 Set。
- 上升沿触发避免每周期重复刷 Trigger。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearStopReason.TcPOU`](../examples/P_Demo_M_ClearStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：故障停机原因已处理完毕，操作员按 HMI"清除"按钮——StopReason 标记为已清除。MES 拉 StopReason.Trigger 看到 FALSE 知道当前没有停机原因；但旧字段值仍在用于审计 OEE 历史数据。
- **价值**：标准化 OEE 停机原因生命周期；与 SetStopReason、AcknowledgeStopReason 共同形成完整状态机。
- **替代方案对比**：自己写置 Trigger=FALSE——本方法一行完成且不容易写错。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.2.2
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_SetStopReason`、`M_AcknowledgeStopReason`、`M_HasStopReason`、`ST_PMLa.StopReason`

## 9. 待确认项 (⚠️)

- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
