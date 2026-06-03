# M_ClearAllAlarms

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
| Example | [`examples/P_Demo_M_ClearAllAlarms.TcPOU`](../examples/P_Demo_M_ClearAllAlarms.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_ClearAllAlarms()` 一次性删除 PackML Admin-Tag 中**所有** alarm。遍历 `Alarm[]`，把所有项的 `Trigger` 置 FALSE；已 Ack 过的 alarm 被移入 `AlarmHistory[]`。返回 TRUE 表示全部清除成功。

**V3 新增方法**：V2 没有此批量方法，HMI"全部清除"按钮必须自己遍历。V3 一行调用搞定。

如果 `AlarmHistory[]` 已满，最老一批 history 项被覆盖。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_ClearAllAlarms : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法遍历 `Alarm[]` 全部清除 |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_ClearAllAlarms` 是 `M_ClearAlarm` 的批量版本：

1. 遍历 `stAdmin.Alarm[0..cMaxAlarms-1]`；
2. 每条 alarm 的 `Trigger` 置 `FALSE`；
3. 已 Ack 的项被移入 `AlarmHistory[]`；未 Ack 直接清除（PDF 未明示是否进 history，⚠️）；
4. 若 `AlarmHistory[]` 满，最老一批被覆盖。

**PDF §4.2.1.1.4 描述**："The alarms remain in the alarm array until an M_AcknowledgeAlarm or M_AcknowledgeAllAlarms call has also been made, at which point the alarms in question are moved to the AlarmHistory array."（同时调过 Ack 的 alarm 在调本方法时才被移入 history）。

**调用语义**：调用即执行——HMI"全部清除"按钮按下时调一次。

**典型用法序列**：
1. 调 `M_AcknowledgeAllAlarms` 一键确认全部；
2. 操作员处理完成；
3. 调 `M_ClearAllAlarms` 一键清除全部并搬入 history。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 全部 alarm 清除成功 | 继续业务 |
| `FALSE` | 部分或全部清除失败 | PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **建议先 AckAll 后 ClearAll**——保证所有 alarm 都进 AlarmHistory，故障审计链完整。
- HMI"全部清除"按钮强烈建议上升沿一次性触发，避免按住按钮重复刷历史。
- AlarmHistory 一次性涌入大量项目可能瞬间填满——重要 history 应同步导出到外部存储。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_ClearAllAlarms.TcPOU`](../examples/P_Demo_M_ClearAllAlarms.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：操作员处理完多条故障后按 HMI"全部清除"按钮，把所有已 Ack 的 alarm 一次搬入 AlarmHistory，主显示区清空。
- **价值**：V3 新增的批量方法让 HMI 一键操作免去 for 循环。一行调用比 V2 写循环更简洁。
- **替代方案对比**：手写 for 循环遍历 + 调单条 ClearAlarm——代码冗长、循环逻辑可能出错；V3 一行搞定。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.4
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeAllAlarms`（先 Ack 再 Clear）、`M_ClearAlarm`（单条版本）

## 9. 待确认项 (⚠️)

- 未 Ack 直接 ClearAll 的 alarm 是否进 AlarmHistory PDF 未明示。
- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
