# M_SetStopReason

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
| Example | [`examples/P_Demo_M_SetStopReason.TcPOU`](../examples/P_Demo_M_SetStopReason.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_SetStopReason()` 把一条停机原因写入 PackML Admin-Tag 的 `Admin.StopReason` 字段：把 `StopReason.Trigger` 置 TRUE、从 `Admin.PlcDateTime` 读取并写入 `StopReason.DateTime`，其余字段（`Id` / `Value` / `Message` / `Category`）从入参 `stStopReason` 拷贝。返回 TRUE 表示写入成功。

**V3 与 V2 的关键差异**：V2 的 `StopReason` 是数组 `StopReason[]`；V3 改为单实例 `StopReason : ST_PMLEvent`——同一时刻只能有一条停机原因。新调用本方法会**覆盖**旧的（包括 AckDateTime）。

⚠️ **PDF 印刷错误**：PDF §4.2.1.2.4 的 Syntax 段头部错写成 `METHOD M_SetStopReason : BOOL VAR_IN_OUT stAdmin VAR_INPUT stStopReason : ST_PMLEvent`——VAR_INPUT 内容是 stStopReason 没错，但 PDF §4.2.1.2.3 的 M_HasStopReason 的 Syntax 段错印成 `METHOD M_SetStopReason : BOOL`（章节标题是 HasStopReason 但语法段方法名写成 SetStopReason）。以章节标题/示例为准。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_SetStopReason : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
VAR_INPUT
  stStopReason     : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法把 stStopReason 写入 `Admin.StopReason`（单实例） |
| `stStopReason` | `ST_PMLEvent` | `VAR_INPUT` | 停机原因结构。调用方填好 `Id`（停机分类编号，如 1=换班/2=维护/3=故障）、`Message`、`Category` |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_SetStopReason` 把单条停机原因写入 `stAdmin.StopReason`：

1. `stAdmin.StopReason.Id / Value / Message / Category := stStopReason.Id / Value / Message / Category`；
2. `stAdmin.StopReason.Trigger := TRUE`；
3. `stAdmin.StopReason.DateTime := stAdmin.PlcDateTime`；
4. 返回 `TRUE`。

**单实例语义**：因为 V3 把 StopReason 改为单值（非数组），调用本方法会**直接覆盖**当前 StopReason，不论旧的是否已 Ack。这与 Alarm/Warning 数组语义完全不同。

**典型用法序列**（PackML OEE 数据采集）：
- 换班 → 调 `M_SetStopReason(stStopReason := stShiftEndReason)`；
- 维护 → 调 `M_SetStopReason(stStopReason := stMaintenanceReason)`；
- 故障 → 调 `M_SetStopReason(stStopReason := stFaultReason)`；
- 每次都覆盖旧的——MES 实时拿到当前停机原因。

**调用语义**：调用即执行——上升沿调用避免每周期重复刷时间戳。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 写入成功 | 继续业务 |
| `FALSE` | 写入失败 | 检查 stAdmin 初始化、PlcDateTime 是否更新；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **V3 StopReason 是单值不是数组**——新写入直接覆盖；从 V2 升级的代码如果假设数组操作要改。
- 建议 `Id` 用项目级停机分类枚举（1=换班 / 2=维护 / 3=故障 / 4=换料 / 5=待料），便于 OEE 分类统计。
- **必须配合 `FB_PMLAdminTime` 周期调用**——否则 DateTime 全是初值。
- 上升沿触发——避免每周期重复刷新 StopReason 的 DateTime。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_SetStopReason.TcPOU`](../examples/P_Demo_M_SetStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：班长操作 HMI 选择"换班停机"后按"停机"按钮——本方法被调用写入 StopReason（Id=1, Message='Shift change'）。MES 实时拿到这条 StopReason 计算 OEE 的"换班损失"。后续维护人员开始维护时再调本方法覆盖为 Id=2,Message='Maintenance'。
- **价值**：标准化 OEE 停机原因数据采集——PackML PackTags.Admin.StopReason 是行业标准字段，MES/SCADA 通用消费。本方法把"找单值+写时间戳+拷贝字段"封装。
- **替代方案对比**：自己写赋值 + 维护时间戳——容易遗漏 PlcDateTime 同步；本方法封装完整。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.2.4
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeStopReason`、`M_ClearStopReason`、`M_HasStopReason`、`ST_PMLa.StopReason`、`ST_PMLEvent`

## 9. 待确认项 (⚠️)

- PDF §4.2.1.2.3 (M_HasStopReason) 的语法段方法头被错印为 M_SetStopReason，以章节标题/示例为准。
- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
