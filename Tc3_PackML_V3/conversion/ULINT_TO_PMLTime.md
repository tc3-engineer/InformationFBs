# ULINT_TO_PMLTime

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
| Example | [`examples/P_Demo_ULINT_TO_PMLTime.TcPOU`](../examples/P_Demo_ULINT_TO_PMLTime.TcPOU) |

---

## 1. 功能简述

`ULINT_TO_PMLTime` 把裸 64 位无符号整数 `ULINT` 解读为纳秒时长，转换为 PackML 标准的 `ST_PMLDateAndTime` 结构体（`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec` 七个 DINT 分量）。

**V3 与 V2 的关键差异**：V2 版本（`ULINT_TO_PackMLTime`）返回 `ARRAY [0..6] OF DINT` 数组；V3 改为返回**结构体** `ST_PMLDateAndTime`——按字段名访问、可读性更好。

主要用于直接把第三方接口给出的 64 位纳秒时长（如某些 ADS 调用返回的 unsigned 64-bit）转成 PackML 时间结构，避免 LTIME 类型转换。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION ULINT_TO_PMLTime : ST_PMLDateAndTime
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `ULINT` | 要转换的时间值（64 位无符号整数，解读为纳秒时长）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`ULINT_TO_PMLTime` 把"纳秒时长（duration）"语义的 `ULINT` 拆分为 PackML 标准 `ST_PMLDateAndTime` 结构体的 7 个分量。与 `LTIME_TO_PMLTime` 行为相同，区别是入参类型——LTIME 是带 IEC 时长语义的类型，ULINT 是裸整数（需要调用方知道这是纳秒）。

**注意 ULINT 默认按纳秒时长解读**：64 位无符号整数 `0` ≡ 0 纳秒；`1_000_000_000` ≡ 1 秒；`60_000_000_000` ≡ 1 分钟。函数按"年/月/日/时/分/秒/毫秒"分量拆解填入结构体对应字段。

**返回结构体字段含义**：`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec`，均为 DINT。

**调用语义**：纯函数——同一输入永远返回同一输出，无副作用。

**典型用法**：第三方 PLC 或 C++ TcCOM 模块返回 64 位 unsigned 纳秒时长，PLC 端只能拿到 ULINT 而不能强制转 LTIME（IEC 类型有别），调本函数直接转换。

## 4. 错误码 / 返回值

返回 `ST_PMLDateAndTime` 结构体：转换后的 PackML 时间结构。

无错误返回——纯计算函数。ULINT 最大值约 1844 亿秒（约 584 年），转换后年字段会很大。

## 5. 使用注意 / 常见坑

- `ULINT` 是裸 64 位整数，没有时间单位语义——调用方必须确保入参确实是纳秒时长，否则结果毫无意义。
- 与 V2 (`ULINT_TO_PackMLTime` 返回数组) 不兼容——升级时改字段访问。（工程经验补充）
- ULINT 是无符号、LTIME 是有符号——本函数不接受负值；用 `LTIME_TO_PMLTime` 才能传负值（虽然 PDF 没明确负值行为）。
- 结构体的 `Year` 字段对应"流逝的年数"而非"日历年"。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULINT_TO_PMLTime.TcPOU`](../examples/P_Demo_ULINT_TO_PMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：TcCOM C++ 模块返回 64-bit unsigned 纳秒戳代表某段处理时长，PLC 接收后需要写入 PackTags.Admin 时间字段。直接转 LTIME 会有符号性问题——用本函数把 ULINT 直接转结构体。
- **价值**：避开了 ULINT↔LTIME 强转的隐患，把裸整数到 PackML 标准时间的桥接做完整。
- **替代方案对比**：`LTIME_TO_PMLTime(LTIME(Input))` 强转——可能因符号位变负值；本函数直接接受无符号语义。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.1.3
- **InfoSys 参考 topic（返回类型）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html （ST_PMLDateAndTime 数据结构 topic；V3 本 FUNCTION 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`LTIME_TO_PMLTime`（LTIME 输入，带符号语义）、`TIME_TO_PMLTime`（32 位 TIME 输入）、`FB_PMLAdminTime.stOptions.ExternalPackMLTime`、`ST_PMLDateAndTime`

## 9. 待确认项 (⚠️)

- ULINT 极端值（最大 0xFFFF_FFFF_FFFF_FFFF）的转换行为 PDF 未列。
- V3 InfoSys 本 FUNCTION 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
