# DT_TO_SYSTEMTIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35082251.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DT_TO_SYSTEMTIME.TcPOU`](../examples/P_Demo_DT_TO_SYSTEMTIME.TcPOU) |

---

## 1. 功能简述

把 PLC 的 `DT`（DATE_AND_TIME，秒精度）转换为 Windows `TIMESTRUCT`（系统时间结构，毫秒精度）。`TIMESTRUCT` 的字段是 wYear/wMonth/wDay/wDayOfWeek/wHour/wMinute/wSecond/wMilliseconds，便于 HMI 显示或写日志。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION DT_TO_SYSTEMTIME : TIMESTRUCT
VAR_INPUT
    DTIN : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DTIN` | `DT` | 待转换的日期时间（DATE_AND_TIME 格式） |

### 返回值

`TIMESTRUCT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

`DT` 是自 1970-01-01 起的秒计数；`TIMESTRUCT` 是按「年-月-日-时-分-秒-毫秒」分量展开的结构体。本函数拆分 `DT` 整数后按公历规则填进 `TIMESTRUCT` 的字段，并自动计算 `wDayOfWeek`（0=Sunday … 6=Saturday，Windows 约定）。

因为 `DT` 精度只到 1 秒，**结果 `TIMESTRUCT.wMilliseconds` 永远为 0**（这是 PDF 明确说明的实现细节，不要在结果毫秒位上找有效信息）。

函数纯计算、无副作用、可在任意任务上下文调用。

## 4. 错误码 / 返回值

返回类型 `TIMESTRUCT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **毫秒永远 0**：要保留毫秒精度必须改用 `FILETIME64_TO_SYSTEMTIME`（先把毫秒源转 `T_FILETIME64` 再转 `TIMESTRUCT`）。
- **`wDayOfWeek` 用 Windows 约定（0=Sunday）**：与 IEC `F_GetDayOfWeek` 的 DIN 1355 / ISO 8601 约定（1=Monday）不同，混用要小心。
- **1970 年下界**：`DT` 不能表达 1970 年前；输入虽然形式上接受任意 `DT`，但小于 1970 的时间在 PLC 上无法构造。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DT_TO_SYSTEMTIME.TcPOU`](../examples/P_Demo_DT_TO_SYSTEMTIME.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
SystemTimeStruct := DT_TO_SYSTEMTIME(DT#2026-05-11-12:34:56);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：HMI 上显示当前 PLC 系统时间，需要按 年-月-日-时-分-秒 拆开字段单独显示；或把时间结构写入 OPC UA 节点的 `DateTime` 字段。
- **价值**：1 行调用拿到 7 个时间字段，比手写整除取余 + 闰年 / 月长度判断省 50 行代码且不会出错。
- **替代方案对比**：手写 `(dt MOD 86400) / 3600` 等分量提取（极易出错）/ 用 `SYSTEMTIME_TO_STRING(DT_TO_SYSTEMTIME(...))` 组合走字符串（更慢）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35082251.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
