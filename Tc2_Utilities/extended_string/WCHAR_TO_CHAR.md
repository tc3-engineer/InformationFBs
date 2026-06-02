# WCHAR_TO_CHAR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483040395.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WCHAR_TO_CHAR.TcPOU`](../examples/P_Demo_WCHAR_TO_CHAR.TcPOU) |

---

## 1. 功能简述

`CHAR_TO_WCHAR` 的反向——把 WSTRING(1) 转回 STRING(1)。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sTextIn : WSTRING(1);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sTextIn` | `WSTRING(1)` | — | 待转换的 WSTRING(1) 单字符。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(1)` | 转换得到的 STRING(1) 单字符。 |

## 3. 行为说明

函数无状态、立即返回。算法：把 `wTextIn`（WSTRING(1) = 2 字节 Unicode 字符）的低字节作为 STRING(1) 的字符返回；高字节信息被丢弃。这意味着**只对 ASCII 范围（U+0000 ~ U+007F）的 WSTRING 字符是无损转换**——这些字符的 UTF-16 编码低字节即对应 ASCII 字节、高字节恒为 0。对于 Latin-1（U+0080 ~ U+00FF）字符，结果是字节值正确但语义未定义（取决于当前 Codepage 解释）。对于 BMP 范围内更高 Unicode 字符（如中文 U+4E00+），低字节是无意义的截断、结果不可用。本函数针对**单字符**场景；整串 WSTRING → STRING 反向请用 `WSTRING_TO_STRING2`（带 Codepage 处理）或 `WSTRING_TO_UTF8`（保留 Unicode 完整性）。

## 4. 错误码 / 返回值

返回 `STRING(1)`：转换得到的 STRING(1) 单字符。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **仅适用于 ASCII 范围**。高位字符会被截断，结果不可用。
- 整串场景请用 `WSTRING_TO_STRING2`。
- 字面量直接用 STRING 字面量（`'A'`）即可，本函数适用于变量场景。
- ⚠️ Unicode → ASCII 信息丢失，调用前应确认源字符 ≤ 0x7F。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WCHAR_TO_CHAR.TcPOU`](../examples/P_Demo_WCHAR_TO_CHAR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 把 WSTRING 字符变量复制到只支持 STRING 的旧 ADS 接口。
- **价值**：单字符场景比 `WSTRING_TO_STRING2`（整串）省事。
- **替代方案对比**：`WSTRING_TO_STRING2`：整串版本。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.24 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483040395.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
