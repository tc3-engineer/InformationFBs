# M_ClearWarning

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
| Example | [`examples/P_Demo_M_ClearWarning.TcPOU`](../examples/P_Demo_M_ClearWarning.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_ClearWarning()` 删除 PackML Admin-Tag 中的一条 warning：把 `Warning[].Trigger` 置 FALSE。返回 TRUE 表示删除成功。

**与 Alarm Clear 的关键差异**：Warning 没有 history 数组——清除即丢失，不会被搬入任何历史容器。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearWarning : BOOL
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
| `stWarning` | `ST_PMLEvent` | `VAR_INPUT` | 要清除的 warning 模板（按 Id 等字段匹配）|

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_ClearWarning` 实现"清除单条 warning"流程：

1. 在 `stAdmin.Warning[]` 中找到与 stWarning 匹配的项（PDF 未明示具体匹配键）；
2. 把该项的 `Trigger` 置 `FALSE`；
3. 返回 `TRUE`。

**PDF §4.2.1.3.4 描述**："The warning remains in the Warning array until it is pushed out of the array by the next warning."（warning 留在数组里直到被下一个 warning 顶出）——意思是 Clear 后 warning 在内存里仍然占位，只是 Trigger=FALSE 不显示。

**调用语义**：调用即执行——HMI"清除"按钮按下时调一次。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 删除成功 | 继续业务 |
| `FALSE` | 未找到或删除失败 | 检查 stWarning.Id；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- Warning 没有 history——Clear 后 warning 字段仍在内存，但 Trigger=FALSE 已不显示。
- 匹配键 PDF 未明示——确保每条 warning Id 唯一。
- 上升沿触发避免每周期重复刷 Trigger。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearWarning.TcPOU`](../examples/P_Demo_M_ClearWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：维护人员换完滤芯后按"清除"按钮把对应 warning 从 HMI 移除。本方法被调用：warning 的 Trigger 置 FALSE 不再显示。
- **价值**：标准化 warning 清除接口；与 Set/Ack 配合完整生命周期。
- **替代方案对比**：自己写赋值——本方法封装好且符合 PackML 标准 API。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.3.4
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_SetWarning`、`M_AcknowledgeWarning`、`M_ClearAllWarning`（批量）

## 9. 待确认项 (⚠️)

- 匹配 stWarning 的具体键 PDF 未明示。
- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
