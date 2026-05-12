# STRING_TO_UTF8

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483029259.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_UTF8.xml`](../examples/P_Demo_STRING_TO_UTF8.xml) |

---

## 1. 功能简述

把 `STRING`（区域码）转为 UTF-8 字节流——OPC UA、ADS Notification、文件 IO 需要 UTF-8 时调用。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDstUTF8 : PVOID;
    pSrcSTRING : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDstUTF8` | `PVOID` | — | 目标 UTF-8 缓冲地址（`ADR(buf)`）。 |
| `pSrcSTRING` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 转换成功；`FALSE` = 字符集不支持或缓冲不够。 |

## 3. 行为说明

函数无状态、立即返回。算法：按当前 Codepage（系统区域设置决定，典型 Windows-1252 / GB18030 / Latin-1）把 `pSrcSTRING` 中的每个字节解释为一个字符，再把该字符对应的 Unicode codepoint 编码为 UTF-8 字节序列写入 `pDstUTF8`。**UTF-8 每字符 1-4 字节**：ASCII (0x00-0x7F) 是 1 字节、Latin-1 高位字符（如 Ü、°）2 字节、CJK 字符 3 字节、BMP 外 4 字节。**所以目标 buffer 需要 ≥ 4× 源字符数 + 1**（最坏情况）。源含当前 Codepage 无法表示的字符（如 GB18030 区域下读到 Windows-1252 字节）时返回 `FALSE`、目标内容未定义。源超过 `Parameterlist.cMaxCharacters` 时停止扫描以防 null 缺失死循环。返回 `TRUE` 不保证缓冲足够——如果 `nDstSize` 小，函数也会截断并仍可能返回 `TRUE`（依赖于版本，⚠️ 谨慎用 `LEN < SIZEOF - 1` 自检）。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 转换成功；`FALSE` = 字符集不支持或缓冲不够。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nDstSize ≥ LEN(src) * 4 + 1`** 保险——UTF-8 一字符可达 4 字节。
- **纯 ASCII 字符串可跳过**——先用 `F_StringIsASCII` 判 `TRUE` 直接 MEMCPY，性能更好。
- 返回 `FALSE` 时目标内容**未定义**——业务侧应丢弃。
- **字符集依赖区域**：源 STRING 中 0x80~0xFF 字节的含义取决于当前 Codepage。生产环境建议先确认 Codepage 一致。
- 目标是 `PVOID` 而非 `POINTER TO STRING`——因为 UTF-8 多字节可能含 0x00 之外的特殊字节，但 STRING null 终结约定可能误读；用 PVOID 让调用方自行管理终结。
- **配套反向函数 `UTF8_TO_STRING`**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_UTF8.xml`](../examples/P_Demo_STRING_TO_UTF8.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把 PLC 报警消息（STRING 区域码）发送到云端 MQTT broker——broker 要求 UTF-8 payload。
- **价值**：替代手写 Codepage→UTF-8 编码表；统一上云接口编码。
- **替代方案对比**：`sLiteral_TO_UTF8`：仅字面量；`F_StringIsASCII` + MEMCPY：纯 ASCII 高效路径。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.18 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483029259.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
