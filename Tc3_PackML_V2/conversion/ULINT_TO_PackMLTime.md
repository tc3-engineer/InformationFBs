# ULINT_TO_PackMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion / Time` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301953547.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ULINT_TO_PackMLTime.TcPOU`](../examples/P_Demo_ULINT_TO_PackMLTime.TcPOU) |

---

## 1. 功能简述

`ULINT_TO_PackMLTime` 把 64 位无符号整型 `ULINT`（解读为时长，通常单位是纳秒）转换为 PackML 标准的 7 元素 `ARRAY [0..6] OF DINT` 时间数组。

输入类型 `ULINT` 是裸 64 位无符号整数，常用于来自 EtherCAT 时钟、外部接口的"时长计数值"。语义上等同于无符号版本的 `LTIME_TO_PackMLTime`。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION ULINT_TO_PackMLTime : ARRAY [0..6] OF DINT;
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `ULINT` | 要转换的时间值（64 位无符号整数，通常解读为纳秒时长）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`ULINT_TO_PackMLTime` 把 ULINT 当作"时长（duration）"按 PackML 标准 7 元素 DINT 数组拆解。

**单位假设**：PDF 没明确说"ULINT 的单位是什么"——根据 PackML 与 LTIME 的兼容性约定，应为纳秒。⚠️ 调用前需根据实际数据源确认单位（如来自 EtherCAT 时钟通常是纳秒；来自其他接口可能是毫秒）。如果单位不是纳秒、调用前需自行乘除转换。

**返回数组下标含义**（PackML 标准）：年[0] / 月[1] / 日[2] / 时[3] / 分[4] / 秒[5] / 毫秒[6]。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用例**：第三方接口或 EtherCAT 主站给出的裸 ULINT 时间计数，用本函数转 PackML 数组写入 PackTag。

## 4. 错误码 / 返回值

返回 `ARRAY [0..6] OF DINT`：转换后的 PackML 时间数组。

无错误返回——纯计算函数。

## 5. 使用注意 / 常见坑

- **单位必须确认**——PDF 没明说 ULINT 是 ns 还是 ms 还是 us，⚠️ 必须确认数据源单位再调用，单位错就转出乱码。
- 与 `LTIME_TO_PackMLTime` 区别：LTIME 是 IEC 标准时长类型有自带单位（纳秒），ULINT 是裸整数需要约定单位。
- 用于解读 ULINT 时长值；解读"时刻"（Unix epoch 时间戳等）请用 `DT_TO_PackMLTime` 或 `TIMESTRUCT_TO_PackMLTime`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULINT_TO_PackMLTime.TcPOU`](../examples/P_Demo_ULINT_TO_PackMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：EtherCAT 主站把测得的"周期时长计数值"作为 ULINT 输出给 PLC，应用层需要把它写入 PackTag 时间字段。调本函数转换。
- **价值**：处理无类型的裸时长计数值，与 LTIME 函数互补；接口适配场景必备。
- **替代方案对比**：手写时长拆解——单位约定混乱、易出错；本函数把"裸 ULINT 当时长"封装好，应用层确认单位即可调用。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301953547.html
- **相关**：`LTIME_TO_PackMLTime`（IEC 标准时长版本）、`TIME_TO_PackMLTime`（32 位时长）、`DCTIME64_TO_PackMLTime` / `DT_TO_PackMLTime` / `TIMESTRUCT_TO_PackMLTime`（时刻输入）

## 9. 待确认项 (⚠️)

- ULINT 的单位（ns vs ms vs us）PDF + InfoSys 均未明确说明，需根据数据源自行约定。
