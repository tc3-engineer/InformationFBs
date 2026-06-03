# PML_AdminTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `General` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301131915.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_PML_AdminTime.TcPOU`](../examples/P_Demo_PML_AdminTime.TcPOU) |

---

## 1. 功能简述

`PML_AdminTime` 是 **PackML Admin-PackTag 时间统计 FB**。周期调用本 FB，它自动填充 PackML 标准定义的所有时间相关字段：

- `PlcDateTime`（当前时间，供 `PML_AdminAlarm` 等方法做时间戳）
- `AccTimeSinceReset`（累计运行时间，自上次 bReset 起）
- `ModeCurrentTime[]` / `ModeCumulativeTime[]`（每个 UnitMode 的当前/累计停留时间）
- `StateCurrentTime[][]` / `StateCumulativeTime[][]`（每个 UnitMode 下每个 State 的当前/累计停留时间）

这些数据是 OEE（设备综合效率）计算的原始素材。本 FB 必须配合 PackTags 的 Status-PackTag（`stStatus.UnitModeCurrent` / `stStatus.StateCurrent`）使用——必须先把当前模式/状态写入 stStatus，本 FB 才能正确累计时间。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bReset           : BOOL;
    stOptions        : ST_AdminTimeOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bReset` | `BOOL` | - | 上升沿/电平触发：复位所记录的累计时间（AccTimeSinceReset / ModeCumulativeTime / StateCumulativeTime 归零）|
| `stOptions` | `ST_AdminTimeOptions` | - | FB 的附加选项：是否用外部时间替代系统时间、外部时间值 |

### VAR_OUTPUT

无（数据通过 `stAdmin / stStatus` 的 VAR_IN_OUT 写回）。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stAdmin          : ST_PMLa;
    stStatus         : ST_PMLs;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAdmin` | `ST_PMLa` | PackML 管理 PackTag。FB 写入 `PlcDateTime` / `AccTimeSinceReset` / `ModeCurrentTime` / `ModeCumulativeTime` / `StateCurrentTime` / `StateCumulativeTime` 等字段 |
| `stStatus` | `ST_PMLs` | PackML 状态 PackTag。FB 读取 `UnitModeCurrent` / `StateCurrent` 判断当前在哪个模式/状态以累计对应时间 |

## 3. 行为说明

`PML_AdminTime` 是 PackML 时间统计的"心跳" FB——**必须周期调用**（每个 PLC 扫描周期），否则所有时间字段不会更新、依赖 `PlcDateTime` 的其他方法（如 `PML_AdminAlarm` 的所有 Set/Ack）也会拿不到新鲜时间戳。

**核心逻辑**：

1. 读取系统时间（默认 Windows 系统时间）写入 `stAdmin.PlcDateTime`（7 元素 DINT：年/月/日/时/分/秒/毫秒）。若 `stOptions.UseExternalTime = TRUE`，则用 `stOptions.ExternalPackMLTime` 替代——常用于 EtherCAT 主站同步时间或外部 RTC 校准场景。
2. 累计运行时间 `AccTimeSinceReset += dt`，`dt` 是上次调用到本次的时间差。
3. 读取 `stStatus.UnitModeCurrent`，对该模式索引的 `ModeCurrentTime[mode]` 累加 dt；首次进入该模式时把上一个模式的 `ModeCurrentTime` 复位为 0、把上一个模式的 `ModeCumulativeTime` 加上停留时长（前提是模式已切换）。`ModeCumulativeTime[mode]` 始终累计。
4. 类似地按 `stStatus.UnitModeCurrent` + `stStatus.StateCurrent` 二维索引累计 `StateCurrentTime[mode][state]` 与 `StateCumulativeTime[mode][state]`。
5. 若 `bReset` 上升沿：所有累计时间归零（CurrentTime/CumulativeTime/AccTimeSinceReset）。

**前置条件（PDF 强调）**：必须先正确写入 `stStatus.UnitModeCurrent` 与 `stStatus.StateCurrent`，本 FB 才能正确分配时间到对应 mode/state 桶。如果未写、二者全为 0，时间会全部累计到索引 0 的桶里。

**典型用法**：在 PLC 主任务里实例化 `fbAdminTime : PML_AdminTime;`，每周期调用一次 `fbAdminTime(stAdmin := PackTags.Admin, stStatus := PackTags.Status, bReset := bResetTimes, stOptions := stOptions);`。HMI 上"复位时间"按钮接 `bResetTimes`；OEE 数据通过 OPC UA 拉 `PackTags.Admin.StateCumulativeTime[][]`。

**典型陷阱**：
- 漏调本 FB → 所有时间字段不更新、PML_AdminAlarm 时间戳是 0。
- 漏写 `stStatus.UnitModeCurrent / StateCurrent` → 时间全累计到 0 索引。
- `stOptions.UseExternalTime` 配错（外部时间没初始化）→ 时间戳读到垃圾值。

## 4. 错误码 / 返回值

本 FB 没有 VAR_OUTPUT，也没有声明返回值——输出通过 stAdmin / stStatus 的 VAR_IN_OUT 写回。FB 不直接报错。

## 5. 使用注意 / 常见坑

- **必须每周期调用**——少调一次时间累计不准，少调多次 alarm 时间戳全停留。
- 必须配合 PackTags Status 写好当前 mode/state，本 FB 才能正确分桶累计时间。
- `bReset` 是电平/上升沿都可——PDF 没明说边沿，但典型 HMI 按钮做成上升沿一次性复位，避免按住按钮不放导致累计始终为 0。（工程经验补充）
- `UseExternalTime` 主要用于 EtherCAT 分布式时钟（DC）同步、多 PLC 时间一致性场景；单机用默认 Windows 时间即可。
- `ExternalPackMLTime` 必须按 7 元素 DINT 格式（年/月/日/时/分/秒/毫秒）。可用本库的 `DCTIME64_TO_PackMLTime` / `DT_TO_PackMLTime` / `TIMESTRUCT_TO_PackMLTime` 等转换函数从其他时间类型生成。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PML_AdminTime.TcPOU`](../examples/P_Demo_PML_AdminTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台一周 7×24 运行的灌装线，要计算 OEE。本 FB 周期调用，自动累计"Production 模式下 Execute 态停留时间 / Held 态停留时间 / Stopped 态停留时间 / Aborted 态停留时间"等矩阵。MES 通过 OPC UA 拉取 `PackTags.Admin.StateCumulativeTime[1][6]`（Production+Execute）作为 OEE 的"Run Time"，拉取 `StateCumulativeTime[1][2]`（Production+Stopped）作为"Down Time"，自动算出可用率（Availability）。
- **价值**：OEE 计算的"时间分配数据"由本 FB 标准化提供，应用层不必自己写"状态变化时间戳+停留时长累计"——这套逻辑细节多、易出 bug。同时 PackTags 的标签命名标准化让跨厂家 MES 可以直接对接。
- **替代方案对比**：自己写"读当前 state + 计算 dt + 数组累加"——代码量大、不同设备不一致、不符合 PackTags 标准。本 FB 是 OMAC 推荐路径。`ST_AdminTimeOptions.UseExternalTime` 还提供了 EtherCAT DC 同步选项，多机时间一致性自动解决。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301131915.html
- **相关**：`PML_AdminAlarm`（消费 PlcDateTime 写报警时间戳）、`PML_StateMachine`（提供当前状态用于时间分桶）、`ST_AdminTimeOptions`、`ST_PMLa` / `ST_PMLs`、`DCTIME64_TO_PackMLTime` / `DT_TO_PackMLTime` / `TIMESTRUCT_TO_PackMLTime`（生成 ExternalPackMLTime）
