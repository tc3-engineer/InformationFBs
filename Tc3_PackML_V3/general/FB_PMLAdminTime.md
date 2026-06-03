# FB_PMLAdminTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `General` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PMLAdminTime.TcPOU`](../examples/P_Demo_FB_PMLAdminTime.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminTime` 是 **PackML Admin-PackTag 时间统计 FB**。周期调用本 FB，它自动填充 PackML 标准定义的所有时间相关字段：

- `PlcDateTime`（当前时间，供 `FB_PMLAdminAlarm` 等方法做时间戳）
- `ModeTimeCurrent`（当前 UnitMode 的累计时间）
- `StateTimeCurrent`（当前 State 的累计时间）
- `CumulativeTimes[].AccTimeSinceReset`（累计运行时间，自上次复位）
- `CumulativeTimes[].ModeStateTimes[].Mode`（各 UnitMode 编号记录）
- `CumulativeTimes[].ModeStateTimes[].State[]`（各 UnitMode 下各 State 的累计停留时间矩阵）

**V3 与 V2 的关键差异**：
- **FB 命名**：V2 叫 `PML_AdminTime`，V3 改名 `FB_PMLAdminTime`。
- **复位机制**：V2 用 `bReset : BOOL` VAR_INPUT；V3 改为 **`M_ResetCumulativeTime(CumulativeTimesIdx)` 方法**——可以指定要复位的 CumulativeTimes 数组下标，更精细。
- **选项类型名**：V2 是 `ST_AdminTimeOptions`；V3 是 `ST_PMLAdminTimeOptions`（统一加 PML 前缀）。⚠️ **PDF §4.2.2 的 VAR_INPUT 代码块印刷错误**——内部把类型写成 `ST_AdminTimeOptions`（V2 命名）但数据类型表里写的 `ST_PMLAdminTimeOptions`（V3 命名）。以数据类型表 + §5.1.1 的实际声明（`ST_PMLAdminTimeOptions`）为准。

这些数据是 OEE（设备综合效率）计算的原始素材。本 FB 必须配合 PackTags 的 Status-PackTag（`stStatus.UnitModeCurrent` / `stStatus.StateCurrent`）使用——必须先把当前模式/状态写入 stStatus，本 FB 才能正确累计时间。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stOptions        : ST_AdminTimeOptions;
END_VAR
```

> ⚠️ **PDF 印刷错误**：VAR_INPUT 代码块内写 `ST_AdminTimeOptions`，但同节"Name Type Description"表里写 `ST_PMLAdminTimeOptions`，且 §5.1.1 的 TYPE 定义是 `ST_PMLAdminTimeOptions`——实际类型为 `ST_PMLAdminTimeOptions`，PLC 中应这样声明。

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stOptions` | `ST_AdminTimeOptions` | - | FB 的附加选项（实际类型 `ST_PMLAdminTimeOptions`）：是否用外部时间替代系统时间、外部时间值 |

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
| `stAdmin` | `ST_PMLa` | PackML 管理 PackTag。FB 写入 `PlcDateTime` / `ModeTimeCurrent` / `StateTimeCurrent` / `CumulativeTimes` 等字段 |
| `stStatus` | `ST_PMLs` | PackML 状态 PackTag。FB 读取 `UnitModeCurrent` / `StateCurrent` 判断当前在哪个模式/状态以累计对应时间 |

### 方法

| 方法 | 含义 | 返回 |
|---|---|---|
| `M_ResetCumulativeTime` | 复位指定下标的 `Admin.CumulativeTimes[]` 累计时间项 | `BOOL` |

#### `M_ResetCumulativeTime` 方法接口（PDF 内联在 §4.2.2）

```iecst
METHOD M_ResetCumulativeTime : BOOL
VAR_INPUT
  CumulativeTimesIdx : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CumulativeTimesIdx` | `UDINT` | 要复位的 `Admin.CumulativeTimes[]` 数组下标（合法范围 0..`cMaxAdminCumulativeTimes-1`，默认 cMaxAdminCumulativeTimes=1 即只下标 0）|

调用示例：`fbAdminTime.M_ResetCumulativeTime(CumulativeTimesIdx := 1);`

**方法行为**：复位 `Admin.CumulativeTimes[CumulativeTimesIdx]` 全字段——`AccTimeSinceReset := 0` + `ModeStateTimes[*].Mode := 0` + `ModeStateTimes[*].State[*] := 0`。返回 TRUE 表示复位成功。

**V3 vs V2 复位机制**：V2 用 `bReset : BOOL` 顶层输入做全局复位；V3 改为方法且带下标参数——可以独立复位多个 CumulativeTimes 槽位（一个机器同时跑"班次/日/月"多个累计周期时各自复位）。这是 V2→V3 升级最大的 API 破坏性改动之一。

## 3. 行为说明

`FB_PMLAdminTime` 是 PackML 时间统计的"心跳" FB——**必须周期调用**（每个 PLC 扫描周期），否则所有时间字段不会更新、依赖 `PlcDateTime` 的其他方法（如 `FB_PMLAdminAlarm` 的所有 Set/Ack）也会拿不到新鲜时间戳。

**核心逻辑**：

1. 读取系统时间（默认 Windows 系统时间）写入 `stAdmin.PlcDateTime`（`ST_PMLDateAndTime` 结构体：Year/Month/Day/Hour/Minute/Second/mSec）。若 `stOptions.UseExternalTime = TRUE`，则用 `stOptions.ExternalPackMLTime` 替代——常用于 EtherCAT 主站同步时间或外部 RTC 校准场景。
2. 累计 `ModeTimeCurrent` / `StateTimeCurrent`：相对当前 Mode/State 的本次连续停留时长（切换 Mode/State 时归零重计）。
3. 累计 `CumulativeTimes[].AccTimeSinceReset`：自上次 `M_ResetCumulativeTime` 起累加 dt。
4. 按 `stStatus.UnitModeCurrent + stStatus.StateCurrent` 二维索引累计 `CumulativeTimes[].ModeStateTimes[mode].State[state]`。
5. 调用 `M_ResetCumulativeTime(CumulativeTimesIdx := i)` 复位 `CumulativeTimes[i]` 的所有计时器到零。

**V3 比 V2 的差异**：V2 整个 FB 共用一个 `bReset : BOOL` 输入——按下复位所有累计时间；V3 改成方法且带索引参数——可以独立复位多个 CumulativeTimes 槽位（一个机器有多套 OEE 周期统计时用得到）。

**前置条件（PDF 强调）**：必须先正确写入 `stStatus.UnitModeCurrent` 与 `stStatus.StateCurrent`，本 FB 才能正确分配时间到对应 mode/state 桶。如果未写、二者全为 0，时间会全部累计到索引 0 的桶里。

**典型用法**：在 PLC 主任务里实例化 `fbAdminTime : FB_PMLAdminTime;`，每周期调用一次 `fbAdminTime(stAdmin := PackTags.Admin, stStatus := PackTags.Status, stOptions := stOpts);`。HMI 上"复位时间"按钮上升沿调 `fbAdminTime.M_ResetCumulativeTime(CumulativeTimesIdx := 1);`；OEE 数据通过 OPC UA 拉 `PackTags.Admin.CumulativeTimes[*].ModeStateTimes[*].State[*]`。

**典型陷阱**：
- 漏调本 FB → 所有时间字段不更新、`FB_PMLAdminAlarm` 时间戳是 0。
- 漏写 `stStatus.UnitModeCurrent / StateCurrent` → 时间全累计到 0 索引。
- `stOptions.UseExternalTime` 配错（外部时间没初始化）→ 时间戳读到垃圾值。

## 4. 错误码 / 返回值

本 FB 没有 VAR_OUTPUT，也没有声明返回值——输出通过 stAdmin / stStatus 的 VAR_IN_OUT 写回。FB 不直接报错。`M_ResetCumulativeTime` 方法返回 BOOL，详见其文档。

## 5. 使用注意 / 常见坑

- **必须每周期调用**——少调一次时间累计不准，少调多次 alarm 时间戳全停留。
- 必须配合 PackTags Status 写好当前 mode/state，本 FB 才能正确分桶累计时间。
- **V3 复位通过方法不是输入**——从 V2 升级时把 `fbAdminTime.bReset := bResetTimes` 改成上升沿调 `fbAdminTime.M_ResetCumulativeTime(CumulativeTimesIdx := i)`；这是 V2→V3 升级最大的 API 破坏性改动之一。
- ⚠️ **PDF VAR_INPUT 类型名印刷不一致**——代码块写 `ST_AdminTimeOptions`，表格写 `ST_PMLAdminTimeOptions`，§5.1.1 实际定义是 `ST_PMLAdminTimeOptions`。以实际定义为准。
- `UseExternalTime` 主要用于 EtherCAT 分布式时钟（DC）同步、多 PLC 时间一致性场景；单机用默认 Windows 时间即可。
- `ExternalPackMLTime` 必须按 `ST_PMLDateAndTime` 格式。可用本库的 `DCTIME64_TO_PMLTime` / `DT_TO_PMLTime` / `TIMESTRUCT_TO_PMLTime` 等转换函数从其他时间类型生成。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PMLAdminTime.TcPOU`](../examples/P_Demo_FB_PMLAdminTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台一周 7×24 运行的灌装线，要计算 OEE。本 FB 周期调用，自动累计"Production 模式下 Execute 态停留时间 / Held 态停留时间 / Stopped 态停留时间 / Aborted 态停留时间"等矩阵。MES 通过 OPC UA 拉取 `PackTags.Admin.CumulativeTimes[0].ModeStateTimes[1].State[6]`（Production + Execute）作为 OEE 的"Run Time"，拉取 `ModeStateTimes[1].State[2]`（Production + Stopped）作为"Down Time"，自动算出可用率（Availability）。
- **价值**：OEE 计算的"时间分配数据"由本 FB 标准化提供，应用层不必自己写"状态变化时间戳+停留时长累计"——这套逻辑细节多、易出 bug。同时 PackTags 的标签命名标准化让跨厂家 MES 可以直接对接。V3 用方法做复位比 V2 的 bReset 单字段更灵活。
- **替代方案对比**：自己写"读当前 state + 计算 dt + 数组累加"——代码量大、不同设备不一致、不符合 PackTags 标准。本 FB 是 OMAC 推荐路径。`ST_PMLAdminTimeOptions.UseExternalTime` 还提供了 EtherCAT DC 同步选项，多机时间一致性自动解决。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html
- **相关**：`M_ResetCumulativeTime`（本 FB 唯一方法）、`FB_PMLAdminAlarm`（消费 PlcDateTime 写报警时间戳）、`FB_PMLStateMachine`（提供当前状态用于时间分桶）、`ST_PMLAdminTimeOptions`、`ST_PMLa` / `ST_PMLs`、`ST_PMLCumulativeTimes` / `ST_PMLModeStateTimes`、`DCTIME64_TO_PMLTime` / `DT_TO_PMLTime` / `TIMESTRUCT_TO_PMLTime`（生成 ExternalPackMLTime）

## 9. 待确认项 (⚠️)

- PDF §4.2.2 VAR_INPUT 代码块的类型名 `ST_AdminTimeOptions` 与同节描述表的 `ST_PMLAdminTimeOptions` 以及 §5.1.1 实际定义不一致——属 PDF 印刷错误，以 `ST_PMLAdminTimeOptions` 为准。
