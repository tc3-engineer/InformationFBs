# M_SetWarning

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
| Example | [`examples/P_Demo_M_SetWarning.TcPOU`](../examples/P_Demo_M_SetWarning.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_SetWarning()` 把一条 warning 写入 PackML Admin-Tag 的 `Warning[]` 数组：把空位的 `Trigger` 置 TRUE、从 `Admin.PlcDateTime` 读取并写入 `Warning[].DateTime`，其余字段（`Id` / `Value` / `Message` / `Category`）从入参 `stWarning` 拷贝。返回 TRUE 表示写入成功。

**与 Alarm 的语义差异**：Warning 表示"提醒类事件"——不停机、可以继续生产，但应记录（如"滤芯接近寿命"、"温度接近报警阈值但未到"）。数组满时（默认 cMaxWarnings=10）按 PackML 标准顶出最老一条（PDF §4.2.1.3.1 描述："The warnings remain in the Warning array until they are pushed out of the array by the next warnings"）。

**Warning 没有 history 数组**——清除即丢失，与 Alarm 有 AlarmHistory 不同。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_SetWarning : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
VAR_INPUT
  stWarning        : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法读取 PlcDateTime + 写入 Warning[] |
| `stWarning` | `ST_PMLEvent` | `VAR_INPUT` | 输入 warning 结构（与 alarm 同型）。调用方填好 Id/Value/Message/Category |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_SetWarning` 实现 warning 上报流程：

1. 在 `stAdmin.Warning[]` 数组中找第一个 `Trigger=FALSE` 的空槽位；
2. 拷贝 `stWarning.Id / Value / Message / Category`；
3. 该槽位 `Trigger := TRUE`、`DateTime := stAdmin.PlcDateTime`；
4. 如果数组满则**顶出最老一条**（PackML §4.2.1.3.1 明确：被新 warning 推出数组）；
5. 返回 `TRUE` 表示写入成功。

**与 Alarm 关键差异**：Warning 没有 AlarmHistory 这种 history 数组——清除或顶出后就丢失。需要长期记录的事件用 Alarm 而非 Warning。

**调用语义**：调用即执行。**只在故障检测的上升沿调一次**——每周期调会瞬间填满数组并不停顶替。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 写入成功 | 继续业务 |
| `FALSE` | 写入失败 | 检查 stAdmin 初始化、PlcDateTime；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **Warning 没有 history**——需要长期保留的事件用 Alarm；Warning 用于"提醒但不需要长期保留"。
- **上升沿一次调用**——避免每周期调用刷数组。
- Warning Category 同样按 ISA-18.2 惯例使用——通常 Warning 用 2 或更高（Critical=1 留给 Alarm）。（工程经验补充）
- 数组满时按 PDF 明确"顶出最老"——重要 warning 想保留就转 alarm。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_SetWarning.TcPOU`](../examples/P_Demo_M_SetWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：滤芯使用了 80% 寿命——还能继续生产但应提醒维护人员准备更换。本方法写入 warning（Id=2001, Message='Filter at 80% life'），HMI 显示提醒；MES 用作维护计划输入。
- **价值**：标准化的 warning 上报接口——HMI/MES 端按 PackML 标准消费。提醒类事件不污染 alarm history，保持 alarm 数据"严肃"。
- **替代方案对比**：自己写 warning 数组管理——容易和 alarm 混淆；本方法清晰分类。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.3.6
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeWarning`、`M_ClearWarning`、`M_HasWarning`、`M_SetAlarm`（Alarm 类似但有 history）、`ST_PMLa.Warning`

## 9. 待确认项 (⚠️)

- FALSE 返回的细分原因 PDF 未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
