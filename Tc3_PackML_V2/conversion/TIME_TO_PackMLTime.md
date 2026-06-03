# TIME_TO_PackMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion / Time` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301648907.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_TIME_TO_PackMLTime.TcPOU`](../examples/P_Demo_TIME_TO_PackMLTime.TcPOU) |

---

## 1. 功能简述

`TIME_TO_PackMLTime` 把 IEC 32 位时长 `TIME`（毫秒精度）转换为 PackML 标准的 7 元素 `ARRAY [0..6] OF DINT` 时间数组。

与 `LTIME_TO_PackMLTime` 同语义，区别只是输入类型——`TIME` 是 32 位无符号毫秒时间跨度，最大约 49 天；`LTIME` 是 64 位纳秒时间跨度，可表示 ±292 年。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION TIME_TO_PackMLTime : ARRAY [0..6] OF DINT;
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `TIME` | 要转换的时间值（IEC 32 位时长，毫秒精度）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`TIME_TO_PackMLTime` 把"时长（duration）"语义的 `TIME` 拆分为 PackML 标准 7 元素 DINT 数组（年/月/日/时/分/秒/毫秒）。

**输入类型注意**：`TIME` 是 IEC 61131-3 标准 32 位无符号毫秒时间跨度类型。最大值约 4294967295 ms ≈ 49.7 天。超出范围（49 天以上的时长）应改用 `LTIME_TO_PackMLTime`。

**返回数组下标含义**（PackML 标准）：年[0] / 月[1] / 日[2] / 时[3] / 分[4] / 秒[5] / 毫秒[6]。

**调用语义**：纯函数——同一输入永远返回同一输出，无副作用。

**典型用例**：
- 把 `T#3D5H` 这种简短的时长字面值转换成 PackML 时间数组写入计时字段；
- TwinCAT 周期任务计时（`SystemTime` 等）经常用 TIME 表示，需要写入 PackTags 时调本函数转换。

## 4. 错误码 / 返回值

返回 `ARRAY [0..6] OF DINT`：转换后的 PackML 时间数组。

无错误返回——纯计算函数。TIME 最大值 ~49 天的转换结果如何分配到 Year/Month/Day PDF + InfoSys 未明确细节，⚠️ 建议测试。

## 5. 使用注意 / 常见坑

- `TIME` 是 32 位无符号毫秒，约 49 天上限——超出请用 `LTIME_TO_PackMLTime`。（工程经验补充）
- `TIME` 是"时长"不是"时刻"——时刻类输入用 `DT_TO_PackMLTime` 或 `TIMESTRUCT_TO_PackMLTime`。
- 返回数组，赋值给 ARRAY[0..6] OF DINT 变量。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TIME_TO_PackMLTime.TcPOU`](../examples/P_Demo_TIME_TO_PackMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：测量到本次生产循环用时 `T#1H23M45S` (TIME 类型)，想把它写入 OEE 字段 `PackTags.Admin.Parameter[N].Value` 作为 PackML 标准时间数组。调本函数一行转换。
- **价值**：把 IEC 标准时长类型转换为 PackML PackTag 标准时间数组，应用层避免手写时长拆解。
- **替代方案对比**：手写 `TIME` 模除运算——`TIME` 的天数与年/月转换不规整、容易出错；本函数标准化。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301648907.html
- **相关**：`LTIME_TO_PackMLTime`（64 位时长）、`ULINT_TO_PackMLTime`（裸 ULINT 值）、`DT_TO_PackMLTime` / `TIMESTRUCT_TO_PackMLTime`（时刻类输入）

## 9. 待确认项 (⚠️)

- TIME 最大值（约 49 天）转换时 Year/Month/Day 分配的细节 PDF + InfoSys 均未明确说明。
