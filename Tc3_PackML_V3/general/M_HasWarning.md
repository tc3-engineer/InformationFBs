# M_HasWarning

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
| Example | [`examples/P_Demo_M_HasWarning.TcPOU`](../examples/P_Demo_M_HasWarning.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_HasWarning()` 检查 PackML Admin-Tag 中是否存在**活跃**的 warning（`Trigger=TRUE`）。返回 `TRUE` 表示至少有一条未确认的 warning 在 `Warning[]`；`FALSE` 表示当前无活跃 warning。

**V3 新增方法**（与 `M_HasAlarm` 对称）。HMI 静默"提醒"指示灯一行调用即可。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_HasWarning : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Warning[]` 查 Trigger=TRUE |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_HasWarning` 遍历 `stAdmin.Warning[0..cMaxWarnings-1]` 数组，使用早退（short-circuit）策略——发现任一 `Trigger=TRUE` 立即返回 `TRUE`，不必扫完整数组；只有全部 FALSE 时才返回 `FALSE`。因为 warning 数组默认只有 10 个 BOOL 字段，即使每周期调用开销也忽略不计。

**PDF §4.2.1.3.5 描述**："This method checks whether an active warning is entered in the Admin-Tags and the method returns TRUE"（中文译：检查 Admin-Tags 中是否登记了活跃的 warning，是则返回 TRUE）。

**"活跃 warning" 定义**：`Trigger=TRUE` 的 warning，即未被 Ack 的 warning。Ack 后 Trigger=FALSE，本方法就不会再因为该项返回 TRUE。

**调用语义**：纯查询——多次调用返回相同结果（除非 warning 状态变化）。可每周期调用。

**典型用法**：
- HMI 黄色"提醒"指示灯：`bHmiWarnLight := fbAdminAlarm.M_HasWarning(stAdmin := PackTags.Admin);`
- 与 `M_HasAlarm` / `M_HasStopReason` 一起判断"机器是否所有事件都已处理完"：`bAllClear := NOT (fbAdminAlarm.M_HasAlarm(...) OR fbAdminAlarm.M_HasWarning(...) OR fbAdminAlarm.M_HasStopReason(...));`
- 状态机切到 Idle 之前的前置检查。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 至少一条 warning 的 Trigger=TRUE |
| `FALSE` | 所有 warning 已确认或数组为空 |

无错误码——纯布尔查询。

## 5. 使用注意 / 常见坑

- 已 Ack 但未 Clear 的 warning 本方法返回 FALSE（因为 Trigger=FALSE）。
- 适合每周期调用——遍历 cMaxWarnings 默认 10 个 BOOL，开销忽略。
- 与 `M_HasAlarm` 和 `M_HasStopReason` 配合一次性判机器"所有事件清空"。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_HasWarning.TcPOU`](../examples/P_Demo_M_HasWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 黄色"提醒"指示灯——有未确认 warning 时亮起。本方法每周期返回 BOOL 直接驱动指示灯。
- **价值**：V3 新增方法把"是否有未确认 warning"封装好，代码简洁。
- **替代方案对比**：自己写 for 循环——本方法一行解决，性能等价。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.3.5
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_HasAlarm`、`M_HasStopReason`、`ST_PMLa.Warning`

## 9. 待确认项 (⚠️)

- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
