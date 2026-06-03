# LTIME_TO_PackMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion / Time` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301243147.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_LTIME_TO_PackMLTime.TcPOU`](../examples/P_Demo_LTIME_TO_PackMLTime.TcPOU) |

---

## 1. 功能简述

`LTIME_TO_PackMLTime` 把 IEC 64 位时长 `LTIME`（纳秒精度的时间跨度）转换为 PackML 标准的 7 元素 `ARRAY [0..6] OF DINT` 时间数组（年/月/日/时/分/秒/毫秒）。返回转换后的 PackML 时间数组。

主要用于把 EtherCAT 主站时间、`PLC_StartTimeNs` 等 LTIME 类时间量喂给 `PML_AdminTime` 的 `ExternalPackMLTime` 输入，或写到 PackML PackTag 的时间字段。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION LTIME_TO_PackMLTime : ARRAY [0..6] OF DINT;
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

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`LTIME_TO_PackMLTime` 把"时长（duration）"语义的 LTIME 拆分为 PackML 标准 7 元素 DINT 数组。LTIME 是 64 位有符号纳秒时间跨度，能表示约 ±292 年。函数把它按"年/月/日/时/分/秒/毫秒"分量拆解。

**注意 LTIME 是"时长"不是"时刻"**：本函数把时长拆解成年-月-日-时-分-秒-毫秒分量。例如 `LTIME#1Y2M3D4H5M6S7MS` → `[1,2,3,4,5,6,7]`。**不是时间点**——这与 `DT_TO_PackMLTime` 或 `DCTIME64_TO_PackMLTime`（处理日历时间戳）语义不同。

**返回数组下标含义**（PackML 标准）：
- `[0]` = 年（Year）
- `[1]` = 月（Month）
- `[2]` = 日（Day）
- `[3]` = 时（Hour）
- `[4]` = 分（Minute）
- `[5]` = 秒（Second）
- `[6]` = 毫秒（mSec）

**调用语义**：纯函数——同一输入永远返回同一输出，无副作用。可在任意 PLC 上下文调用。

**典型用法**：`PackTags.Admin.AccTimeSinceReset` 字段本质是 DINT 累计秒数，但应用层若用 LTIME 计算了"自上次复位经过时长"想转换成 PackML 时间数组显示，调本函数。

## 4. 错误码 / 返回值

返回 `ARRAY [0..6] OF DINT`：转换后的 PackML 时间数组。

无错误返回——纯计算函数。LTIME 极端值（如 `LTIME#-9223372036854775808NS`）的转换结果 PDF + InfoSys 未明确，⚠️ 建议测试。

## 5. 使用注意 / 常见坑

- `LTIME` 是"时长"而不是"时刻"。如果想把"时间点"（如当前 wall-clock）转换，用 `DT_TO_PackMLTime` 或 `TIMESTRUCT_TO_PackMLTime`。（工程经验补充）
- 转换后的 7 元素数组每个分量都是独立 DINT，月/日的取值范围对应"流逝的月数 / 日数"而非"日历月/日"。（工程经验补充）
- LTIME 负值的转换行为 PDF + InfoSys 未列，⚠️ 建议测试或避免传负值。
- 函数返回数组（不是单值），需要赋值给 ARRAY[0..6] OF DINT 变量再使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTIME_TO_PackMLTime.TcPOU`](../examples/P_Demo_LTIME_TO_PackMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：EtherCAT 主站测得本 PLC 自上电累计运行 LTIME 值（72 小时 15 分钟），想把它转换成 PackML 时间数组写入某个 OEE 显示字段。调本函数一行转换。
- **价值**：LTIME 是 IEC 61131-3 标准时长类型，PackML 需要 7 元素 DINT 数组——本函数把转换标准化，应用层不必自己写"LTIME 拆解为年月日时分秒毫秒"的代码。
- **替代方案对比**：手写 `Input / LTIME#1S` + 取模运算——容易出错（特别是月份天数不固定）；调本函数一行完成、与 PackML 标准对齐。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301243147.html
- **相关**：`TIME_TO_PackMLTime`、`ULINT_TO_PackMLTime`（其他时长输入类型）、`DCTIME64_TO_PackMLTime` / `DT_TO_PackMLTime` / `TIMESTRUCT_TO_PackMLTime`（时刻输入）、`PML_AdminTime.stOptions.ExternalPackMLTime`

## 9. 待确认项 (⚠️)

- LTIME 负值或溢出极端值的转换行为 PDF + InfoSys 均未列。
