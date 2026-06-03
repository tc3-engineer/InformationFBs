# TIMESTRUCT_TO_PackMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion / Timestamp` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302026123.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_TIMESTRUCT_TO_PackMLTime.TcPOU`](../examples/P_Demo_TIMESTRUCT_TO_PackMLTime.TcPOU) |

---

## 1. 功能简述

`TIMESTRUCT_TO_PackMLTime` 把 Beckhoff 标准 `TIMESTRUCT` 结构体（含年/月/日/时/分/秒/毫秒/星期等分量）转换为 PackML 标准的 7 元素 `ARRAY [0..6] OF DINT` 时间数组。

`TIMESTRUCT` 是 Tc2_System 等系统库返回的细粒度时间结构（毫秒精度 + 星期信息）。本函数把它的核心字段映射到 PackML 标准格式写入 PackTag。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION TIMESTRUCT_TO_PackMLTime : ARRAY [0..6] OF DINT;
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `TIMESTRUCT` | 要转换的时间结构（Beckhoff 标准时间结构，毫秒精度，含星期）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`TIMESTRUCT_TO_PackMLTime` 把 Beckhoff `TIMESTRUCT` 的字段映射到 PackML 7 元素 DINT 数组。

**TIMESTRUCT 结构**（来自 `Tc2_System` 库）：
```iecst
TYPE TIMESTRUCT :
STRUCT
    wYear         : WORD;
    wMonth        : WORD;
    wDayOfWeek    : WORD;
    wDay          : WORD;
    wHour         : WORD;
    wMinute       : WORD;
    wSecond       : WORD;
    wMilliseconds : WORD;
END_STRUCT
END_TYPE
```

**映射规则**：
- `[0]` ← `wYear`（如 2026）
- `[1]` ← `wMonth`（1-12）
- `[2]` ← `wDay`（1-31）
- `[3]` ← `wHour`（0-23）
- `[4]` ← `wMinute`（0-59）
- `[5]` ← `wSecond`（0-59）
- `[6]` ← `wMilliseconds`（0-999）

`wDayOfWeek` 字段不被 PackML 数组采用——PackML 标准时间数组只有 7 元素。需要星期信息请另行从 TIMESTRUCT 取用。

**与 DT_TO_PackMLTime 区别**：
- DT 是秒精度——毫秒分量恒为 0。
- TIMESTRUCT 是毫秒精度——毫秒分量来自 wMilliseconds。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用例**：`Tc2_System.GetSystemTime()` 返回 `TIMESTRUCT`，用本函数转 PackML 数组写报警时间戳；或者把 NTP 客户端返回的 TIMESTRUCT 转 PackML 喂给 `PML_AdminTime.stOptions.ExternalPackMLTime`。

## 4. 错误码 / 返回值

返回 `ARRAY [0..6] OF DINT`：转换后的 PackML 日历时刻数组（毫秒精度）。

无错误返回——纯计算函数。

## 5. 使用注意 / 常见坑

- TIMESTRUCT 的字段都是 WORD（16 位无符号），返回数组的 DINT 容纳无压力。
- `wDayOfWeek` 不进 PackML 数组——星期信息丢失。需要星期请直接从 TIMESTRUCT 读 `wDayOfWeek`。（工程经验补充）
- 适合作为"高精度时刻 → PackML"的标准转换路径——毫秒精度满足绝大多数 PackML 应用需求。
- TIMESTRUCT 通常是本地时（取决于来源 FB 配置），需注意时区。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TIMESTRUCT_TO_PackMLTime.TcPOU`](../examples/P_Demo_TIMESTRUCT_TO_PackMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：调用 `Tc2_System.GetSystemTime` 拿到当前 TIMESTRUCT，需要把它送给 PackML PackTag 的 DateTime 字段（或 PML_AdminTime.stOptions.ExternalPackMLTime）。本函数一行转换。
- **价值**：把 Beckhoff 系统时间结构和 PackML 时间数组对接的标准转换函数——毫秒精度满足绝大多数 PackML 应用。
- **替代方案对比**：手写 8 行字段拷贝——容易漏掉某个字段或类型转换错；本函数封装好、与 PackML 标准对齐。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302026123.html
- **相关**：`DT_TO_PackMLTime`（秒精度）、`DCTIME64_TO_PackMLTime`（EtherCAT 纳秒）、`Tc2_System.GetSystemTime`（拿 TIMESTRUCT）、`PML_AdminTime`
