# LTIME_TO_PMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION` |
| Category | `Conversion / Time` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_LTIME_TO_PMLTime.TcPOU`](../examples/P_Demo_LTIME_TO_PMLTime.TcPOU) |

---

## 1. 功能简述

`LTIME_TO_PMLTime` 把 IEC 64 位时长 `LTIME`（纳秒精度的时间跨度）转换为 PackML 标准的 `ST_PMLDateAndTime` 结构体（包含 `Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec` 七个 DINT 分量）。

**V3 与 V2 的关键差异**：V2 版本（`LTIME_TO_PackMLTime`）返回 `ARRAY [0..6] OF DINT` 数组——按下标访问；V3 改为返回**结构体** `ST_PMLDateAndTime`——按字段名访问，可读性更好且自动文档化字段含义。

主要用于把 EtherCAT 主站时间、`PLC_StartTimeNs` 等 LTIME 类时间量转成 PackML 标准时间结构，写入 `FB_PMLAdminTime` 的 `stOptions.ExternalPackMLTime` 输入或 PackML PackTag 时间字段。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION LTIME_TO_PMLTime : ST_PMLDateAndTime
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : LTIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `LTIME` | 要转换的时间值（IEC 64 位时长，纳秒精度）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`LTIME_TO_PMLTime` 把"时长（duration）"语义的 `LTIME` 拆分为 PackML 标准 `ST_PMLDateAndTime` 结构体的 7 个分量。`LTIME` 是 64 位有符号纳秒时间跨度，能表示约 ±292 年。函数把它按"年 / 月 / 日 / 时 / 分 / 秒 / 毫秒"分量拆解填入结构体对应字段。

**注意 LTIME 是"时长"不是"时刻"**：本函数把时长拆解成年-月-日-时-分-秒-毫秒分量。例如 `LTIME#1Y2M3D4H5M6S7MS` 概念上拆为 `Year=1, Month=2, Day=3, Hour=4, Minute=5, Second=6, mSec=7`。**不是时间点**——这与 `DT_TO_PMLTime` 或 `DCTIME64_TO_PMLTime`（处理日历时间戳）语义不同。

**返回结构体字段含义**（`ST_PMLDateAndTime`，PackML 标准）：
- `Year`（年）= DINT
- `Month`（月）= DINT
- `Day`（日）= DINT
- `Hour`（时）= DINT
- `Minute`（分）= DINT
- `Second`（秒）= DINT
- `mSec`（毫秒）= DINT

**调用语义**：纯函数——同一输入永远返回同一输出，无副作用。可在任意 PLC 上下文调用，包括方法、其他函数、PRG。

**典型用法**：`PackTags.Admin.CumulativeTimes[0].AccTimeSinceReset` 字段本质是 DINT 累计秒数，但应用层若用 LTIME 计算了"自上次复位经过时长"想转换成 PackML 时间结构显示给 MES，调本函数后取对应字段。

## 4. 错误码 / 返回值

返回 `ST_PMLDateAndTime` 结构体：转换后的 PackML 时间结构。

无错误返回——纯计算函数。LTIME 极端值（如 `LTIME#-9223372036854775808NS`）的转换结果 PDF 未明确，⚠️ 建议测试。

## 5. 使用注意 / 常见坑

- `LTIME` 是"时长"而不是"时刻"。如果想把"时间点"（如当前 wall-clock）转换，用 `DT_TO_PMLTime` 或 `TIMESTRUCT_TO_PMLTime`。（工程经验补充）
- 返回的结构体每个分量都是独立 DINT，月/日的取值范围对应"流逝的月数 / 日数"而非"日历月/日"。（工程经验补充）
- 与 V2 (`LTIME_TO_PackMLTime` 返回数组) 不兼容——从 V2 升级时需要把所有 `aOutput[3]` 风格的访问改成 `stOutput.Hour` 字段访问。（工程经验补充）
- LTIME 负值的转换行为 PDF 未列，⚠️ 建议测试或避免传负值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTIME_TO_PMLTime.TcPOU`](../examples/P_Demo_LTIME_TO_PMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：EtherCAT 主站测得本 PLC 自上电累计运行 LTIME 值（72 小时 15 分钟），想把它转成 PackML 时间结构写入某个 OEE 显示字段。调本函数一行转换。
- **价值**：LTIME 是 IEC 61131-3 标准时长类型，PackML V3 用结构体（V2 用数组）——本函数把转换标准化，应用层不必自己写"LTIME 拆解为年月日时分秒毫秒"的代码。V3 的结构体返回比 V2 的数组返回更可读，避免下标记错。
- **替代方案对比**：手写 `Input / LTIME#1S` + 取模运算——容易出错（特别是月份天数不固定）；调本函数一行完成、与 PackML 标准对齐、字段名访问更安全。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.1.1
- **InfoSys 参考 topic（返回类型）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html （ST_PMLDateAndTime 数据结构 topic；本函数返回类型即 ST_PMLDateAndTime；V3 本 FUNCTION 自身的 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`TIME_TO_PMLTime`、`ULINT_TO_PMLTime`（其他时长输入类型）、`DCTIME64_TO_PMLTime` / `DT_TO_PMLTime` / `TIMESTRUCT_TO_PMLTime`（时刻输入）、`FB_PMLAdminTime.stOptions.ExternalPackMLTime`、`ST_PMLDateAndTime`（返回结构体）

## 9. 待确认项 (⚠️)

- LTIME 负值或溢出极端值的转换行为 PDF 未列。
- V3 InfoSys topic URL：仅库根可达，具体 topic 页面未在公网检索结果中命中，已标 `⚠️ not-on-infosys`。
