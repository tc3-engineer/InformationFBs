# SYSTEMTIME_TO_DT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35152907.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_DT.xml`](../examples/P_Demo_SYSTEMTIME_TO_DT.xml) |

---

## 1. 功能简述

把 Windows `TIMESTRUCT`（毫秒精度）转换为 PLC 的 `DT`（秒精度）。**毫秒部分按四舍五入到秒**——若需禁用四舍五入，调用前先把 `wMilliseconds` 置 0。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION SYSTEMTIME_TO_DT : DT
VAR_INPUT
    TIMESTR : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TIMESTR` | `TIMESTRUCT` | 待转换的 Windows 系统时间结构体 |

### 返回值

`DT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按 `TIMESTRUCT` 的字段（wYear / wMonth / wDay / wHour / wMinute / wSecond / wMilliseconds）组合为自 1970-01-01 起的秒数赋给 `DT`。

**关键行为**（PDF 强调）：因为 `DT` 精度只到秒，`wMilliseconds ≥ 500` 时秒会进位 1 秒（向上舍入）；`wMilliseconds < 500` 时直接截断。要禁用此行为请调用前 `TIMESTR.wMilliseconds := 0`。

`DT` 范围有限（1970 ~ 2106），`TIMESTRUCT` 可表达 1601 ~ 9999 年的更宽范围；超出 `DT` 范围的输入会得到截断 / 溢出的结果，无错误码。

## 4. 错误码 / 返回值

返回类型 `DT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **毫秒四舍五入到秒**：500ms 进位，与 `DT_TO_SYSTEMTIME`（永远把毫秒置 0）的语义不对称——两者不严格互逆。
- **1970 下界 / 2106 上界**：`TIMESTRUCT` 的合法范围（1601 ~ 9999）远比 `DT` 大，超出 `DT` 范围结果不可预测。
- **无错误码**：传 `TIMESTRUCT.wMonth = 13` 这种非法字段，结果未定义；先自己校验合法性再调用。
- **`wDayOfWeek` 字段被忽略**：本 FC 不读取也不校验 `wDayOfWeek`，可以传 0；同理 `SYSTEMTIME_TO_FILETIME64` 也说明会忽略 wDayOfWeek。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_DT.xml`](../examples/P_Demo_SYSTEMTIME_TO_DT.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
DTFromSystemTime := SYSTEMTIME_TO_DT(SystemTimeStruct);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：Windows API / OPC UA / HMI 送回 `TIMESTRUCT`，但 PLC 内部业务比较时间差用 `DT` 更方便（直接 `>` `<` `-` 算秒数）。
- **价值**：1 行调用完成结构体到秒计数的折算，含毫秒舍入策略；手写要写日历计算 + 闰年判定 + 毫秒舍入决策。
- **替代方案对比**：用 `SYSTEMTIME_TO_FILETIME64` + `FILETIME64_TO_DT`（多 1 步，但行为更可控——毫秒截断而非舍入）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35152907.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
