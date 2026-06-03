# M_SetStopReason

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300112267.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_SetStopReason.TcPOU`](../examples/P_Demo_M_SetStopReason.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_SetStopReason()` 把一条 StopReason 写入 PackML Admin-Tag 的 `StopReason[]` 数组：`StopReason[].Trigger := TRUE` + 时间戳 + 拷贝结构字段。返回 TRUE 表示写入成功。

StopReason（停机原因）用 `ST_Alarm` 结构表示，但语义是"为本次停机贴分类标签"——如"换班停机"、"维护停机"、"故障停机"、"无料停机"。这些数据被 MES/OEE 系统用于设备综合效率（OEE）计算。StopReason **没有 History 数组**——满时顶掉最老一条。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_SetStopReason : BOOL
VAR_INPUT
  stStopReason     : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stStopReason` | `ST_Alarm` | StopReason 结构（与 Alarm 同型，Id 字段建议用项目级"停机原因枚举"）|

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAdmin` | `ST_PMLa` | PackML 管理 PackTag 结构 |

## 3. 行为说明

`M_SetStopReason` 实现与 `M_SetAlarm` / `M_SetWarning` 一致的"写入数组"逻辑，目标数组是 `stAdmin.StopReason[]`：

1. 在 `stAdmin.StopReason[]` 找第一个 `Trigger=FALSE` 的空槽位；
2. 拷贝 `stStopReason.Id / Value / Message / Category`；
3. `StopReason[i].Trigger := TRUE`；
4. `StopReason[i].DateTime := stAdmin.PlcDateTime`；
5. 返回 TRUE。

**数组满时行为**：PDF 直译 "If the StopReason array is already full of entries, the oldest entry is deleted as a result." —— 数组满时顶掉最老一条，**没有 History 归档**。

**调用时机**：每次机器从 Execute 切到 Stopped/Held/Aborted 等非生产态时调用一次，记录"为什么停"。也可以在 Idle → Starting 的 reset 流程里把旧 StopReason 清掉以便统计新一轮。

**与 PackML 状态机配合**：典型工作流是 `PML_StateMachine` 切换到 Stopped 时（在主程序里检测 eState 变化）调用本方法、把当时的停机原因（操作员选择 / 故障检测自动判定）写入 StopReason[]，MES 周期采走做 OEE 分析。

**时间戳依赖**：保证 `PML_AdminTime` 周期调用。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 写入成功 | 继续业务 |
| `FALSE` | 写入失败 | 检查 stAdmin 初始化；PDF 未列细分原因（⚠️ 待人工确认）|

## 5. 使用注意 / 常见坑

- **StopReason 无 History**——长期停机统计要应用层自存或 MES 周期采样。（工程经验补充）
- StopReason 的 Id 建议用项目级枚举（如 1=换班 / 2=维护 / 3=故障 / 4=无料）便于 OEE 分类聚合。（工程经验补充）
- 用 R_TRIG 包裹避免周期重复——典型在状态机切到 Stopped 的瞬间触发一次。
- 配合 `PML_AdminTime` 周期调用确保时间戳。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_SetStopReason.TcPOU`](../examples/P_Demo_M_SetStopReason.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：操作员按"停机"按钮 → PackML 状态机切到 Stopping/Stopped → 主程序在 eState 切换时调用本方法写 `stStopReason := {Id:1, Message:'Shift change', Category:1}`。MES 通过 OPC UA 把 `StopReason[]` 数据采走、按 Category 聚合统计"今日换班 vs 故障 vs 维护停机时间占比"。
- **价值**：本方法把"停机分类记录"标准化——OEE 计算的"计划停机"和"非计划停机"区分必需有分类标签，跨设备数据互通才有意义。
- **替代方案对比**：手写停机日志 / 全局变量记录——格式不一、跨设备没法对账；用 Alarm 代替 StopReason——语义混淆，操作员停机不是故障。本方法是 PackML/OEE 业界标准路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6300112267.html
- **相关**：`PML_AdminAlarm.M_AcknowledgeStopReason`、`PML_AdminAlarm.M_ClearStopReason`、`PML_AdminTime`、`ST_Alarm`、`PML_StateMachine`

## 9. 待确认项 (⚠️)

- 数组满时具体覆盖策略与 FALSE 返回原因 PDF + InfoSys 均未列。
