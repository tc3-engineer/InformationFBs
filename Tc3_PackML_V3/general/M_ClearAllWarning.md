# M_ClearAllWarning

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
| Example | [`examples/P_Demo_M_ClearAllWarning.TcPOU`](../examples/P_Demo_M_ClearAllWarning.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_ClearAllWarning()` 一次性删除 PackML Admin-Tag 中**所有** warning。遍历 `Warning[]`，把所有项的 `Trigger` 置 FALSE。返回 TRUE 表示全部清除成功。

**V3 新增方法**（与 `M_ClearAllAlarms` 对称）。HMI"全部清除 warning"按钮一行调用即可。

注意方法名末尾是 `Warning` 单数（不是 `Warnings`）——与 `M_ClearAllAlarms`（带 s）命名不严格对称。以 PDF 头部 `METHOD M_ClearAllWarning : BOOL` 为准。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearAllWarning : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Warning[]` 全部清除 |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_ClearAllWarning` 是 `M_ClearWarning` 的批量版本。它内部遍历整个 warning 数组一次性把全部 warning 标记为已清除（`Trigger=FALSE`），调用方不需要再写 for 循环。这是 V3 比 V2 用户体验上的改进——V2 用户必须自己写循环。

具体步骤：

1. 遍历 `stAdmin.Warning[0..cMaxWarnings-1]`（cMaxWarnings 默认 10）；
2. 每条 warning 的 `Trigger` 置 `FALSE`；
3. 返回 `TRUE` 表示全部清除完成。

**PDF §4.2.1.3.3 描述**："The warnings remain in the Warning array until they are pushed out of the array by the next warnings."（中文译：warning 留在数组里直到被下一组新 warning 顶出）——意思是 Clear 后 warning 字段（Id/Message 等）在内存里仍然占位，只是 Trigger=FALSE 让 `M_HasWarning` 返回 FALSE、HMI 不再显示。

**与 alarm 批量清除的差异**：Alarm 的批量清除会把已 Ack 的 alarm 搬入 AlarmHistory；Warning 没有 history 数组，清除即"看不见"但内存不释放。

**调用语义**：调用即执行——HMI"全部清除"按钮按下时调一次。**强烈建议上升沿一次性触发**避免重复刷数组。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 全部清除成功 | 继续业务 |
| `FALSE` | 失败 | PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- HMI"全部清除"按钮强烈建议上升沿一次性触发。
- Warning 没有 history——清除后所有 warning 字段仍在内存但 Trigger=FALSE。
- 方法名末尾是 `Warning` 单数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearAllWarning.TcPOU`](../examples/P_Demo_M_ClearAllWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：维护人员一次处理完多个 warning（滤芯/油位/温度），按 HMI"全部清除"按钮一键清空 warning 列表。
- **价值**：V3 新增的批量方法让 HMI 一键操作免去 for 循环。
- **替代方案对比**：自己写 for 循环——代码冗长；本方法一行搞定。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.3.3
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_ClearWarning`（单条版本）、`M_AcknowledgeAllWarning`、`M_ClearAllAlarms`（对应 Alarm 批量）

## 9. 待确认项 (⚠️)

- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
