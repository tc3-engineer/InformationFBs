# UTF8_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483037323.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UTF8_TO_STRING.TcPOU`](../examples/P_Demo_UTF8_TO_STRING.TcPOU) |

---

## 1. 功能简述

`STRING_TO_UTF8` 的反向：把 UTF-8 字节流转回当前 Codepage 的 STRING。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDstSTRING : POINTER TO STRING;
    pSrcUTF8 : PVOID;
    nDstSize : UDINT;
END_VAR

VAR_OUTPUT
    nDstLen : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDstSTRING` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `pSrcUTF8` | `PVOID` | — | 源 UTF-8 字节流地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数。 |

### VAR_OUTPUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nDstLen` | `UDINT` | 目标 STRING 转换后字符数。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 转换成功；`FALSE` = 字符集错误（含 Codepage 外字符）。 |

## 3. 行为说明

函数无状态、立即返回。算法：从 `pSrcUTF8` 起始逐 UTF-8 字符（1-4 字节序列）读取，每读到一个完整 UTF-8 字符就解码为 Unicode codepoint，再按当前 Codepage 把 codepoint 编码为单字节字符写入 `pDstSTRING`。**源含 Codepage 无法表示的字符（如中文 UTF-8 写入西欧 Codepage 时）会被跳过**——而不是返回错误整段失败；返回 `FALSE` 通常意味目标缓冲不够或编码冲突过多。`nDstLen` 输出实际写入的字符数；调用方应比较 `nDstLen` 与预期字符数判断丢失程度。`pSrcUTF8` 必须 null 终结，否则函数会扫到 `Parameterlist.cMaxCharacters` 才停。结果 STRING 始终以 null 收尾——即使函数返回 `FALSE`。配套反向函数 `STRING_TO_UTF8`：两者构成 STRING ↔ UTF-8 完整通道；如需保留全部 Unicode 字符（不丢失），应改用 `UTF8_TO_WSTRING`。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 转换成功；`FALSE` = 字符集错误（含 Codepage 外字符）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **Codepage 外字符被跳过**而非报错——业务侧靠 `nDstLen` 判长度差。
- **`pSrcUTF8` 必须 null 终结**——否则函数会扫到 `Parameterlist.cMaxCharacters` 才停。
- 返回 `FALSE` 时目标内容**已部分写入但不完整**——根据 nDstLen 决定取舍。
- 更稳妥的 Unicode 反向是 `UTF8_TO_WSTRING`（WSTRING 能容纳所有 Unicode 字符）。
- **配套 `STRING_TO_UTF8`**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UTF8_TO_STRING.TcPOU`](../examples/P_Demo_UTF8_TO_STRING.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从云端 MQTT 收到 UTF-8 报警 → 转 STRING 写到 PLC 本地报警表（仅显示）。
- **价值**：替代手写 UTF-8 解码循环；统一与 `STRING_TO_UTF8` 的双向通道。
- **替代方案对比**：`UTF8_TO_WSTRING`：到 Unicode 字宽 WSTRING；保留 UTF-8 + `F_StringIsASCII` 旁路：节省转换开销。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.21 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483037323.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
