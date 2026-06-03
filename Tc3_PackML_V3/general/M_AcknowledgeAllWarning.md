# M_AcknowledgeAllWarning

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
| Example | [`examples/P_Demo_M_AcknowledgeAllWarning.TcPOU`](../examples/P_Demo_M_AcknowledgeAllWarning.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_AcknowledgeAllWarning()` 一次性确认 PackML Admin-Tag 中**所有**未确认的 warning。遍历 `Admin.Warning[]`，对每条 `Trigger=TRUE` 的项把 `Trigger` 置 FALSE、把 `Admin.PlcDateTime` 写入 `AckDateTime`。返回 TRUE 表示全部确认成功。

**V3 新增方法**（与 `M_AcknowledgeAllAlarms` 对称）。HMI"全部确认 warning"按钮一行调用即可。

注意：方法名末尾是 `Warning`（不是 `Warnings`），与 `M_AcknowledgeAllAlarms`（带 s）命名不严格对称——以 PDF 头部 `METHOD M_AcknowledgeAllWarning : BOOL` 为准。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_AcknowledgeAllWarning : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Warning[]` 全部 Ack |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_AcknowledgeAllWarning` 是 `M_AcknowledgeWarning` 的批量版本。它内部遍历整个 warning 数组，对每条仍处于活跃状态的项一次性完成确认动作；调用方不需要再写 for 循环。这是 V3 比 V2 用户体验上的一个显著改进。

具体步骤：

1. 遍历 `stAdmin.Warning[0..cMaxWarnings-1]`（cMaxWarnings 默认 10）；
2. 对每条 `Trigger=TRUE` 的项：把 `Trigger` 置 `FALSE`、`AckDateTime := stAdmin.PlcDateTime`；
3. 全部处理完返回 `TRUE`。

**PDF §4.2.1.3.1 描述**："If all warnings are acknowledged, the method returns TRUE."（中文译：如果所有 warning 都已确认，方法返回 TRUE）。

**与 alarm 批量确认的关键差异**：Warning 没有 history 转移逻辑——即使后续调 `M_ClearAllWarning` 也只是把 Trigger 置 FALSE，不会移入任何历史容器。这反映了"警告轻于报警"的 PackML 语义设计哲学。

**调用语义**：调用即执行——HMI"全部确认 warning"按钮按下时调一次。**强烈建议上升沿一次性触发**，避免按住按钮每周期重复刷 AckDateTime 时间戳。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充，主程序必须周期调用 AdminTime。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 全部 warning 已确认 | 继续业务 |
| `FALSE` | 部分或全部未确认成功 | 检查 stAdmin 初始化、PlcDateTime；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **必须配合 `FB_PMLAdminTime` 周期调用**——否则 AckDateTime 全是初值。
- HMI"全部确认"按钮强烈建议上升沿一次性触发。
- 数组里没有 Trigger=TRUE 时调用本方法的行为 PDF 未列（⚠️ 可能直接返回 TRUE）。
- 方法名末尾是 `Warning` 单数（不是 `Warnings`）——容易拼错。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_AcknowledgeAllWarning.TcPOU`](../examples/P_Demo_M_AcknowledgeAllWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：维护人员看到 HMI 上多个 warning（滤芯/油位/温度接近阈值等），按"全部确认"按钮一次确认全部。本方法被调用：所有 Trigger 置 FALSE、AckDateTime 填好。
- **价值**：V3 新增的批量方法让 HMI 一键操作免去 for 循环。
- **替代方案对比**：自己写 for 循环——代码冗长；本方法一行搞定。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.3.1
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeWarning`（单条版本）、`M_ClearAllWarning`、`M_AcknowledgeAllAlarms`（对应 Alarm 批量）

## 9. 待确认项 (⚠️)

- 数组里无 Trigger=TRUE 时的返回行为 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
