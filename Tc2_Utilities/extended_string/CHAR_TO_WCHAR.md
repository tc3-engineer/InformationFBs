# CHAR_TO_WCHAR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3482945931.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_CHAR_TO_WCHAR.xml`](../examples/P_Demo_CHAR_TO_WCHAR.xml) |

---

## 1. 功能简述

把一个 `STRING(1)` 的单字符变量转换为 `WSTRING(1)`（带 null 终结符）。该函数处理逐字符场景：例如把上位机界面提取出来的单个 ASCII 字符送到需要 Unicode 字面量的下游 API。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sTextIn : STRING(1);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sTextIn` | `STRING(1)` | — | 待转换的 STRING(1) 变量（单个 ASCII 字符）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WSTRING(1)` | 转换得到的 WSTRING(1) 变量（含 null 终结符）。 |

## 3. 行为说明

函数无状态、立即返回。输入 `STRING(1)` 是 1 字节 ASCII；输出 `WSTRING(1)` 是 2 字节 Unicode 字符（UTF-16 编码）+ null 终结符。Beckhoff 在 STRING / WSTRING 互转时区分单字符（CHAR/WCHAR）与多字符（STRING/WSTRING）两套 API：单字符走 `CHAR_TO_WCHAR` / `WCHAR_TO_CHAR`，整串走 `STRING_TO_WSTRING2` / `WSTRING_TO_STRING2`。本函数针对前者，开销小、不分配额外缓冲。需要注意 ASCII 0x00 ~ 0x7F 范围内可直接转，超出范围（如 Latin-1 0x80~0xFF）的字符在 WSTRING 中可能与原编码不同（取决于当前 codepage）。

## 4. 错误码 / 返回值

返回 `WSTRING(1)`：转换得到的 WSTRING(1) 变量（含 null 终结符）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- 输入只能是单字符。整串转换请用 `STRING_TO_WSTRING2` 或 `STRING_TO_UTF8` + `UTF8_TO_WSTRING`。
- 非 ASCII 字符（含中文）走 STRING(1) 通常截断，结果未定义。需要 Unicode 字面量请用 WSTRING 字面量 `"中"` 而不是 `'中'`。
- 字面量赋值更直接：`wstr := "A"` 比 `wstr := CHAR_TO_WCHAR('A')` 高效。本函数适用于变量到变量的场景。
- 返回的 `WSTRING(1)` 已含 null 终结符。拼接到更长 WSTRING 时注意 null 截断行为。
- ⚠️ PDF / InfoSys 未列错误码，函数总是返回（不报错）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CHAR_TO_WCHAR.xml`](../examples/P_Demo_CHAR_TO_WCHAR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 把操作员输入的 ASCII 控制字符（如 'Y' / 'N' / 'Q'）转换为 Unicode 送到 OPC UA 或 ADS notification 接口。
- **价值**：不用本函数则需手写位扩展（高字节补 0）+ null 终结，3 行代码；本函数 1 行解决，且 Beckhoff 保证 codepage 处理一致。
- **替代方案对比**：对单字符场景：本函数；对整串场景：`STRING_TO_WSTRING2`；对 UTF-8 中转：`STRING_TO_UTF8` + `UTF8_TO_WSTRING`。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.1 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3482945931.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
