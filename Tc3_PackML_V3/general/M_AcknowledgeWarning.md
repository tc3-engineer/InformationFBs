# M_AcknowledgeWarning

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
| Example | [`examples/P_Demo_M_AcknowledgeWarning.TcPOU`](../examples/P_Demo_M_AcknowledgeWarning.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_AcknowledgeWarning()` 确认 PackML Admin-Tag 中的一条 warning：在 `Admin.Warning[]` 中匹配传入 `stWarning` 对应的项，把 `Warning[].Trigger` 置 FALSE、从 `Admin.PlcDateTime` 读取并写入 `Warning[].AckDateTime`，返回 TRUE 表示找到并确认成功。

**与 Alarm 的语义差异**：Warning 没有"Clear → 移入 history"的逻辑——确认后 warning 仍在 `Warning[]` 数组直到被新 warning 顶出。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeWarning : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
VAR_INPUT
  stWarning        : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag |
| `stWarning` | `ST_PMLEvent` | `VAR_INPUT` | 要确认的 warning 模板（按 Id 等字段匹配，具体键 PDF 未明示）|

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_AcknowledgeWarning` 实现"操作员确认单条 warning"流程：

1. 在 `stAdmin.Warning[]` 中根据 stWarning 标识字段（最可能 Id）找到对应项；
2. 把该项的 `Trigger` 置 `FALSE`；
3. 把 `stAdmin.PlcDateTime` 拷贝到 `Warning[i].AckDateTime`；
4. 返回 `TRUE` 表示找到并已确认。

**PDF §4.2.1.3.2 描述**："The warning remains in the Warning array until it is pushed out of the array by the next warning."（warning 留在数组里直到被下一个 warning 顶出）——意思是 Ack 只标记，不删除。

**调用语义**：调用即执行——HMI"确认"按钮按下时调一次。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 找到并确认成功 | 继续业务 |
| `FALSE` | 未找到或确认失败 | 检查 stWarning.Id 是否在数组中；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- Warning 没有 history——Ack 后 warning 仍在数组，等待被新 warning 顶出或调 `M_ClearWarning` 清除。
- 匹配键 PDF 未明示——确保每条 warning Id 唯一。
- **必须配合 `FB_PMLAdminTime` 周期调用**。
- 上升沿触发避免每周期重复刷 AckDateTime。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeWarning.TcPOU`](../examples/P_Demo_M_AcknowledgeWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：维护人员看到 HMI 上"滤芯寿命 80%"提醒后按"确认"按钮告诉系统"我已收到提醒"。Trigger=FALSE 但 warning 仍在数组（HMI 仍提醒"已确认未处理"）。
- **价值**：标准化 warning 生命周期；和 alarm Ack 行为类似但 warning 没有 history 转移逻辑，反映了"警告轻于报警"的语义。
- **替代方案对比**：自己写遍历+置 Trigger=FALSE——容易遗漏 AckDateTime；本方法封装完整。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.3.2
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_SetWarning`、`M_ClearWarning`、`M_AcknowledgeAllWarning`（批量）、`M_HasWarning`

## 9. 待确认项 (⚠️)

- 匹配 stWarning 的具体键（Id？组合键？）PDF 未明示。
- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
