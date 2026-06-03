# M_HasAlarm

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
| Example | [`examples/P_Demo_M_HasAlarm.TcPOU`](../examples/P_Demo_M_HasAlarm.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_HasAlarm()` 检查 PackML Admin-Tag 中是否存在**活跃**的 alarm（`Trigger=TRUE`）。返回 `TRUE` 表示至少有一条未确认的 alarm 在 `Alarm[]` 中；`FALSE` 表示当前没有活跃 alarm。

**V3 新增方法**：V2 没有此查询方法，状态机判断条件必须自己遍历 `Alarm[]`。V3 一句调用搞定。

主要用于 PackML 状态机判断"现在能不能进入 Idle / Execute"等条件：有未处理 alarm 时状态机应保持在 Stopped / Aborted。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_HasAlarm : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Alarm[]` 查 Trigger=TRUE |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_HasAlarm` 遍历 `stAdmin.Alarm[0..cMaxAlarms-1]`，**只要发现任意一条 `Trigger=TRUE`**就立即返回 `TRUE`；全部为 FALSE 时返回 `FALSE`。

**PDF §4.2.1.1.6 描述**："This method checks whether an active alarm is entered in the Admin-Tags and the method returns TRUE"（检查是否有活跃 alarm，有则返回 TRUE）。

**"活跃 alarm" 定义**：`Trigger=TRUE` 的 alarm，即未被 Ack 的 alarm。Ack 后 Trigger=FALSE，本方法就不会再返回 TRUE。

**调用语义**：纯查询——多次调用返回相同结果（除非 alarm 状态变化）。可每周期调用，性能开销极小（只是遍历最多 10 个 BOOL 字段）。

**典型用法**：
- 状态机条件：`IF NOT fbAdminAlarm.M_HasAlarm(stAdmin := PackTags.Admin) THEN eCmd := E_PMLCommand.Reset; END_IF`
- HMI 静默指示：`bAnyActiveAlarm := fbAdminAlarm.M_HasAlarm(stAdmin := PackTags.Admin);`

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 至少有一条 alarm 的 Trigger=TRUE（未确认） |
| `FALSE` | 所有 alarm 都已确认或数组为空 |

无错误码——纯布尔查询。

## 5. 使用注意 / 常见坑

- "已 Ack 未 Clear" 的 alarm 本方法返回 FALSE（因为 Trigger=FALSE）——不要用本方法判断"是否还有 alarm 在 HMI 显示"。要判 HMI 还显示的 alarm 总数，自己遍历数组判 `Id != 0` 或自定义条件。（工程经验补充）
- 适合每周期调用——遍历 cMaxAlarms 默认 10 个 BOOL，开销忽略不计。
- 与 `M_GetAlarmCategory` 配合使用：先 HasAlarm 判存在性，再 GetAlarmCategory 取严重等级。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_HasAlarm.TcPOU`](../examples/P_Demo_M_HasAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：PackML 状态机收到操作员 Start 命令——但应用层需要先检查是否还有未确认 alarm。本方法一句话判完。
- **价值**：V3 新增方法把"是否有未确认 alarm"封装好，状态机条件代码简洁；HMI 指示灯逻辑直接接本方法返回值。
- **替代方案对比**：自己写 for 循环找 Trigger=TRUE——代码冗长；本方法一行解决，性能等价。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.6
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_GetAlarmCategory`（取最高优先级）、`M_AcknowledgeAllAlarms`、`FB_PMLStateMachine`（状态机消费本方法判 alarm 存在）

## 9. 待确认项 (⚠️)

- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
