# STRING_TO_WSTRING2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483030795.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_WSTRING2.TcPOU`](../examples/P_Demo_STRING_TO_WSTRING2.TcPOU) |

---

## 1. 功能简述

把任意长度 `STRING` 转为 `WSTRING`（Unicode）；比 `Tc2_Standard.STRING_TO_WSTRING` 突破 255 字符限制。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDstWSTRING : POINTER TO WSTRING;
    pSrcSTRING : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDstWSTRING` | `POINTER TO WSTRING` | — | 目标 WSTRING 地址。 |
| `pSrcSTRING` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（注意 WSTRING 每字符 2 字节）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 完整转换；`FALSE` = 源长 > 目标缓冲，结果被截断。 |

## 3. 行为说明

函数无状态、立即返回。算法：逐字符把 `pSrcSTRING` 的字节（按当前 Codepage 解释）扩展为 WSTRING 的 16 位字符——ASCII 字符直接填入低字节、高字节置 0；高位字符按 Codepage 映射到对应 Unicode codepoint。写入 `pDstWSTRING`，最后写 16 位 null 终结符（0x0000）。**WSTRING 总字节数 = 字符数 × 2 + 2**（含 null 终结符）；目标缓冲不够时按 `nDstSize / 2 - 1` 个字符截断、写 null 终结符、返回 `FALSE`。最多扫描 `Parameterlist.cMaxCharacters` 字符以防 null 缺失死循环。源含 Codepage 外字符时行为 ⚠️ PDF/InfoSys 未明确——建议调用前用 `F_StringIsASCII` 旁路：纯 ASCII 串可直接走 `STRING_TO_WSTRING2` 而不担心 Codepage 问题。`Tc2_Standard.STRING_TO_WSTRING` 限 255 字符，本函数无限制。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 完整转换；`FALSE` = 源长 > 目标缓冲，结果被截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nDstSize` 是目标字节数**，不是字符数。目标 `WSTRING(N)` 的 SIZEOF = (N+1) × 2。
- **`Tc2_Standard.STRING_TO_WSTRING` 限 255 字符**——长串必须用 `STRING_TO_WSTRING2`。
- 源含 Codepage 外字符时行为 ⚠️ PDF/InfoSys 未明确；建议先 `F_StringIsASCII` 检查。
- 反向：`WSTRING_TO_STRING2`。
- 需要 UTF-8 而非 WSTRING 走 `STRING_TO_UTF8`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_WSTRING2.TcPOU`](../examples/P_Demo_STRING_TO_WSTRING2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 模块用 WSTRING 显示多语言字符串；从配置文件读出的 STRING 配置项需要转 WSTRING 才能显示。
- **价值**：`Tc2_Standard` 的 255 限制；本函数无限制。
- **替代方案对比**：`Tc2_Standard.STRING_TO_WSTRING`：限 255；`STRING_TO_UTF8` + `UTF8_TO_WSTRING`：UTF-8 中转。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.19 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483030795.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
