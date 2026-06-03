# TIME_TO_PMLTime

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
| Example | [`examples/P_Demo_TIME_TO_PMLTime.TcPOU`](../examples/P_Demo_TIME_TO_PMLTime.TcPOU) |

---

## 1. 功能简述

`TIME_TO_PMLTime` 把 IEC 32 位时长 `TIME`（毫秒精度的时间跨度）转换为 PackML 标准的 `ST_PMLDateAndTime` 结构体（`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec` 七个 DINT 分量）。

**V3 与 V2 的关键差异**：V2 版本（`TIME_TO_PackMLTime`）返回 `ARRAY [0..6] OF DINT` 数组；V3 改为返回**结构体** `ST_PMLDateAndTime`——按字段名访问、可读性更好。

主要用于把 TON/TOF/TP 等 IEC 定时器累计时间、ST 语言 `T#xx` 字面量等 TIME 类时间量喂给 `FB_PMLAdminTime` 的 `stOptions.ExternalPackMLTime` 输入，或写到 PackML PackTag 时间字段。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION TIME_TO_PMLTime : ST_PMLDateAndTime
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `TIME` | 要转换的时间值（IEC 32 位时长，毫秒精度，最大约 49.7 天）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`TIME_TO_PMLTime` 把"时长（duration）"语义的 `TIME` 拆分为 PackML 标准 `ST_PMLDateAndTime` 结构体的 7 个分量。`TIME` 是 32 位无符号毫秒时间跨度，最大可表示约 49 天 17 小时。函数把它按"天 / 时 / 分 / 秒 / 毫秒"分量拆解（年与月分量在 TIME 范围内一般为 0，除非超过 30 天阈值）填入结构体对应字段。

**注意 TIME 是"时长"不是"时刻"**：本函数把时长拆解成年-月-日-时-分-秒-毫秒分量。例如 `T#1H30M45S` 概念上拆为 `Hour=1, Minute=30, Second=45, mSec=0`，其余为 0。**不是日历时间点**——这与 `DT_TO_PMLTime`（处理日历时间戳）语义不同。

**返回结构体字段含义**（`ST_PMLDateAndTime`，PackML 标准）：`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec`，均为 DINT。

**调用语义**：纯函数——同一输入永远返回同一输出，无副作用。可在任意 PLC 上下文调用。

**典型用法**：取定时器累计 `TON.ET` 值（TIME 类型）想转成 PackML 时间结构显示给 HMI 或写到 OPC UA。调本函数一行完成。

## 4. 错误码 / 返回值

返回 `ST_PMLDateAndTime` 结构体：转换后的 PackML 时间结构。

无错误返回——纯计算函数。

## 5. 使用注意 / 常见坑

- `TIME` 32 位毫秒最大约 49.7 天——超出会溢出。长时长用 `LTIME_TO_PMLTime`（64 位 LTIME）或 `ULINT_TO_PMLTime`（裸 ULINT）。（工程经验补充）
- TIME 是"时长"而不是"时刻"。如果想转日历时间，用 `DT_TO_PMLTime` / `TIMESTRUCT_TO_PMLTime`。
- 与 V2 (`TIME_TO_PackMLTime` 返回数组) 不兼容——升级时把所有 `aOutput[3]` 风格改成 `stOutput.Hour` 字段访问。（工程经验补充）
- 返回结构体的 `Year`、`Month` 字段对应"流逝的年/月数"而非"日历年/月"。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TIME_TO_PMLTime.TcPOU`](../examples/P_Demo_TIME_TO_PMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：传送带运行 `T#2H15M` 后想把累计运行时长写入 PackTags.Admin 的 OEE 字段。调本函数一行转换。
- **价值**：TIME 是 IEC 61131-3 标准时长类型，PackML V3 用结构体（V2 用数组）——本函数把转换标准化、字段名访问更安全。
- **替代方案对比**：手写 `Input / T#1S` 取模——容易出错；调本函数一行完成、与 PackML 标准对齐。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.1.2
- **InfoSys 参考 topic（返回类型）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html （ST_PMLDateAndTime 数据结构 topic；V3 本 FUNCTION 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`LTIME_TO_PMLTime`（64 位 LTIME 输入）、`ULINT_TO_PMLTime`（裸 ULINT 输入）、`DT_TO_PMLTime` / `TIMESTRUCT_TO_PMLTime` / `DCTIME64_TO_PMLTime`（时刻输入）、`FB_PMLAdminTime.stOptions.ExternalPackMLTime`、`ST_PMLDateAndTime`

## 9. 待确认项 (⚠️)

- TIME 溢出（超过 49.7 天范围）的转换行为 PDF 未列。
- V3 InfoSys 本 FUNCTION 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
