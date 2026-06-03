# M_AcknowledgeStopReason

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
| Example | [`examples/P_Demo_M_AcknowledgeStopReason.TcPOU`](../examples/P_Demo_M_AcknowledgeStopReason.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_AcknowledgeStopReason()` 确认 PackML Admin-Tag 中**当前**的 StopReason：把 `Admin.StopReason.Trigger` 置 FALSE、从 `Admin.PlcDateTime` 读取并写入 `Admin.StopReason.AckDateTime`，返回 TRUE 表示确认成功。

**V3 单值语义**：因为 V3 把 StopReason 改为单值（非数组），本方法不需要传 `stStopReason` 参数——直接确认当前那个。

为了让 AckDateTime 时间戳有效，主程序必须周期调用 `FB_PMLAdminTime`。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeStopReason : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法把 `StopReason.Trigger` 置 FALSE + 填 AckDateTime |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_AcknowledgeStopReason` 实现"确认当前停机原因"流程：

1. `stAdmin.StopReason.Trigger := FALSE`；
2. `stAdmin.StopReason.AckDateTime := stAdmin.PlcDateTime`；
3. 返回 `TRUE` 表示已确认。

**PDF §4.2.1.2.1 描述**："The StopReason remains in the Admin-Tags until it is replaced by a subsequent StopReason."（StopReason 留在 Admin-Tag 中直到被下一个 StopReason 覆盖）——这意味着 Ack 并不清除内容，只是标记"操作员已看到"。

**调用语义**：调用即执行——HMI"确认"按钮按下时调一次。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 已确认 | 继续业务 |
| `FALSE` | 确认失败 | 检查 stAdmin 初始化、PlcDateTime；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- 单值语义——StopReason 总是当前那个，不需要匹配 Id。
- Ack 不删除——内容仍在 `Admin.StopReason`，HMI 凭 `Trigger=FALSE && AckDateTime!=零` 判"已确认未清除"。
- 后续要清除调 `M_ClearStopReason` 或写新的 StopReason 覆盖。
- **必须配合 `FB_PMLAdminTime` 周期调用**。
- 上升沿触发避免每周期重复刷 AckDateTime。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeStopReason.TcPOU`](../examples/P_Demo_M_AcknowledgeStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：当前 StopReason 是"故障停机"，处理人员看到后按"确认"按钮告诉系统"我已经知道并在处理"。Trigger 置 FALSE 但 Id 仍是 3——HMI 仍显示"故障停机"红条，但条上多个"已确认"标记。
- **价值**：标准化的 StopReason 两阶段（Set → Ack → Clear / 被新 StopReason 覆盖）生命周期，符合 OEE 数据采集规范。
- **替代方案对比**：自己写直接置 Trigger=FALSE——容易遗漏 AckDateTime；本方法封装完整。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.2.1
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_SetStopReason`、`M_ClearStopReason`、`M_HasStopReason`、`ST_PMLa.StopReason`

## 9. 待确认项 (⚠️)

- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
