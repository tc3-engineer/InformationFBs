# DT_TO_FILETIME64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10500987275.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DT_TO_FILETIME64.xml`](../examples/P_Demo_DT_TO_FILETIME64.xml) |

---

## 1. 功能简述

把 PLC 的 `DT`（DATE_AND_TIME，秒精度）转换为 64 位 `T_FILETIME64`（Windows 文件时间，100 纳秒精度）。两种格式互转用于跨 Windows API、时间戳序列化、报表归档。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION DT_TO_FILETIME64 : T_FILETIME64
VAR_INPUT
    DTIN : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DTIN` | `DT` | 待转换的日期时间（DATE_AND_TIME 格式） |

### 返回值

`T_FILETIME64` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

`DT` 在 PLC 里表示自 1970-01-01 00:00:00 UTC 起的秒数（32 位无符号）；`T_FILETIME64` 表示自 1601-01-01 00:00:00 UTC 起的 100 纳秒数（64 位无符号）。两者基准时间相差 369 年，单位相差 10000000 倍。

本函数按这两条规则做加法 + 单位换算；结果的低 7 位（100ns 单位的小数部分）始终为 0，因为 `DT` 只能表达整秒。无中间结构体、无副作用、无错误码。

典型搭配：用 `F_GetActualDateTime`（在 Tc2_System）拿到 `DT`，转 `T_FILETIME64` 后可调用 `F_TranslateFileTime64Bias` 做时区偏移，再 `FILETIME64_TO_ISO8601` 输出 ISO 8601 字符串写入日志。

## 4. 错误码 / 返回值

返回类型 `T_FILETIME64`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **`DT` 的有效范围**：自 1970-01-01 起约 136 年（到 2106-02-06 06:28:15）。本函数不主动校验范围，超界输入会得到无意义的 `T_FILETIME64` 数值。
- **`T_FILETIME64` 是结构体不是数值**：在 PDF 里实际上是 `STRUCT` 包含 `dwLowDateTime` / `dwHighDateTime` 两个 `DWORD`；直接打印需先用 `FILETIME64_TO_ISO8601` 等函数。
- **版本要求 Tc2_Utilities ≥ 3.3.44.0 + TwinCAT v3.1.4024**：旧版没有 `_64` 后缀的对应类型，要么升库要么用 legacy `DT_TO_FILETIME`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DT_TO_FILETIME64.xml`](../examples/P_Demo_DT_TO_FILETIME64.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
fileTime := DT_TO_FILETIME64(DT#2026-05-11-12:00:00);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：需要把 PLC 内部记录的时间戳（`DT`）写入 Windows 日志、数据库（FILETIME 列）或与外部 Windows 程序通过 ADS 交换时间数据。
- **价值**：1 行调用避免手写「秒 → 100ns + 基准偏移 116444736000000000」的常量魔法；调换基准从 1970 到 1601 是个非常容易写错的转换，本 FC 由 Beckhoff 实现保证正确。
- **替代方案对比**：手写常量计算（容易写错）/ 用 `DT_TO_FILETIME` 旧函数（legacy 类型，新代码不推荐）/ 调用本函数（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10500987275.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
