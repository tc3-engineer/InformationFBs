# TIMESTRUCT_TO_PMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION` |
| Category | `Conversion / Timestamp` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_TIMESTRUCT_TO_PMLTime.TcPOU`](../examples/P_Demo_TIMESTRUCT_TO_PMLTime.TcPOU) |

---

## 1. 功能简述

`TIMESTRUCT_TO_PMLTime` 把 Beckhoff `TIMESTRUCT` 结构体（包含 wYear / wMonth / wDayOfWeek / wDay / wHour / wMinute / wSecond / wMilliseconds 字段，毫秒精度）转换为 PackML 标准的 `ST_PMLDateAndTime` 结构体（`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec`）。

**V3 与 V2 的关键差异**：V2 版本（`TIMESTRUCT_TO_PackMLTime`）返回 `ARRAY [0..6] OF DINT` 数组；V3 改为返回**结构体** `ST_PMLDateAndTime`——按字段名访问、可读性更好。

`TIMESTRUCT` 是 Beckhoff `Tc2_Utilities` / `Tc2_System` 提供的本地日期时间结构（带毫秒精度），常作为 `NT_GetLocalTime` / `FB_LocalSystemTime` 等 FB 的输出。本函数提供 TIMESTRUCT → PackML 标准时间结构的标准转换。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION TIMESTRUCT_TO_PMLTime : ST_PMLDateAndTime
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `TIMESTRUCT` | 要转换的时间（Beckhoff 时间结构体，毫秒精度）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`TIMESTRUCT_TO_PMLTime` 把 `TIMESTRUCT` 的 8 个字段映射到 PackML `ST_PMLDateAndTime` 的 7 个字段（`wDayOfWeek` 在 PackML 中不需要、被丢弃）。

**字段映射**：
- `TIMESTRUCT.wYear` → `ST_PMLDateAndTime.Year`
- `TIMESTRUCT.wMonth` → `ST_PMLDateAndTime.Month`
- `TIMESTRUCT.wDay` → `ST_PMLDateAndTime.Day`
- `TIMESTRUCT.wHour` → `ST_PMLDateAndTime.Hour`
- `TIMESTRUCT.wMinute` → `ST_PMLDateAndTime.Minute`
- `TIMESTRUCT.wSecond` → `ST_PMLDateAndTime.Second`
- `TIMESTRUCT.wMilliseconds` → `ST_PMLDateAndTime.mSec`
- `TIMESTRUCT.wDayOfWeek` → 丢弃（PackML 标准时间字段无星期）

**与 DT 转换对比**：TIMESTRUCT 带毫秒精度；DT 只到秒。优先用本函数获得毫秒戳。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用法**：`Tc2_Utilities.NT_GetLocalTime` 返回 TIMESTRUCT 当前本地时间，调本函数转换写入 `PackTags.Admin.PlcDateTime` 供 `FB_PMLAdminAlarm` 各方法使用。

## 4. 错误码 / 返回值

返回 `ST_PMLDateAndTime` 结构体：转换后的 PackML 日历时刻结构（带毫秒）。

无错误返回——纯计算函数。TIMESTRUCT 字段无效值（如 wMonth=0）的转换行为 PDF 未列。

## 5. 使用注意 / 常见坑

- TIMESTRUCT 是本地时间或 UTC 由调用源决定（如 `NT_GetLocalTime` 返回本地时、`NT_GetTime` 返回 UTC）——本函数不做时区转换，原样映射字段值。（工程经验补充）
- 与 V2 (`TIMESTRUCT_TO_PackMLTime` 返回数组) 不兼容——升级时改字段访问。
- `wDayOfWeek` 字段被丢弃——如果需要星期信息，调用方自行从 `Year/Month/Day` 计算。
- 毫秒精度是本函数与 `DT_TO_PMLTime` 的主要区别——需要毫秒优先用 TIMESTRUCT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TIMESTRUCT_TO_PMLTime.TcPOU`](../examples/P_Demo_TIMESTRUCT_TO_PMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：MES 要求 PackML 报警时间戳精确到毫秒。`Tc2_Utilities.NT_GetLocalTime` 周期返回 TIMESTRUCT 当前本地时间（带毫秒），调本函数转成 PackML 结构写入 `PackTags.Admin.PlcDateTime`，所有报警时间戳都带毫秒精度。
- **价值**：TIMESTRUCT 是 Beckhoff 系统库的标准时间表示；PackML 需要 ST_PMLDateAndTime。本函数把两者标准互转，应用层不必手写字段映射。
- **替代方案对比**：手写 8 行赋值——容易遗漏 wDayOfWeek 处理、容易把 wMilliseconds 漏到 0；本函数一行完成且语义准确。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.2.3
- **InfoSys 参考 topic（返回类型）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html （ST_PMLDateAndTime 数据结构 topic；V3 本 FUNCTION 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`DT_TO_PMLTime`（秒精度的 IEC 类型）、`DCTIME64_TO_PMLTime`（EtherCAT 纳秒同步）、`Tc2_Utilities.NT_GetLocalTime` / `Tc2_System.FB_LocalSystemTime`（生成 TIMESTRUCT）、`ST_PMLDateAndTime`

## 9. 待确认项 (⚠️)

- TIMESTRUCT 无效字段（如 wMonth=0）的转换行为 PDF 未列。
- V3 InfoSys 本 FUNCTION 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
