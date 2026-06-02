# UTF8Len

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483035787.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UTF8Len.TcPOU`](../examples/P_Demo_UTF8Len.TcPOU) |

---

## 1. 功能简述

UTF-8 字符串的长度（字符数）+ 字节数 + 是否纯 ASCII；性能优化关键函数（判定后选择零拷贝路径）。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pUTF8 : PVOID;
END_VAR

VAR_OUTPUT
    bASCII : BOOL;
    nSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pUTF8` | `PVOID` | — | UTF-8 字节流地址（null 终结）。 |

### VAR_OUTPUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bASCII` | `BOOL` | `TRUE` = 全部是合法 ASCII 字符（0x00-0x7F）—— 可零拷贝当 STRING 用。 |
| `nSize` | `UDINT` | 字节数（不含 null 终结符）；多字节字符时 nSize > 字符数。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | UTF-8 字符串的字符数；非法 UTF-8 编码时返回 0。 |

## 3. 行为说明

函数无状态、立即返回。算法：逐字节解析 UTF-8 编码——连续的单字节（高位为 0、即 0x00-0x7F）算作 1 个 ASCII 字符；多字节字符按 UTF-8 前缀位识别（首字节 110xxxxx → 2 字节字符、1110xxxx → 3 字节、11110xxx → 4 字节），每个多字节序列的后续字节必须形如 10xxxxxx（continuation 字节）。函数同时维护三个计数：**字符数**（最终返回值）、**字节数**（`nSize` 输出）、**bASCII 标志**（只要遇到任意非 ASCII 字节就置 `FALSE`）。最多扫描 `Parameterlist.cMaxCharacters` 字符防 null 缺失死循环。**遇到非法 UTF-8 编码**（如孤立 continuation 字节、首字节后缺少 continuation、5 字节序列等）时立即停止并**返回 0**——业务侧用 `nChars > 0` 判 UTF-8 合法。空串（首字节即 null）返回 0 + bASCII = TRUE + nSize = 0（实测但 PDF/InfoSys 未明确 ⚠️）。`bASCII = TRUE` 的语义：所有字节均在 ASCII 范围——这意味着该 UTF-8 串与 STRING 字节级等价，可以零拷贝 MEMCPY 当 STRING 用，无需 `UTF8_TO_STRING` 转换。这是性能优化的关键判定点。

## 4. 错误码 / 返回值

返回 `UDINT`：UTF-8 字符串的字符数；非法 UTF-8 编码时返回 0。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **返回 0 = 非法 UTF-8** —— 不是空串。空串返 0 + bASCII = TRUE + nSize = 0（边界 ⚠️ 待确认）。
- **字符数 ≠ 字节数**（多字节字符）。需字节数用 `nSize`，需字符数用返回值。
- **`bASCII = TRUE` 时可零拷贝**：UTF-8 串 == STRING 串。前置 `F_StringIsASCII` + `UTF8Len` 的组合用于优化高频路径。
- `pUTF8` 必须 null 终结。
- 适合做 OPC UA / ADS Notification 收到 UTF-8 数据后的长度统计与 ASCII 旁路判断。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UTF8Len.TcPOU`](../examples/P_Demo_UTF8Len.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OPC UA 客户端收到 UTF-8 字符串：先 `UTF8Len` 算字符数 + `bASCII`；若 `bASCII = TRUE` 直接当 STRING 用；否则走 `UTF8_TO_STRING` / `UTF8_TO_WSTRING`。
- **价值**：性能优化关键——避免在高频数据上做不必要的编码转换。
- **替代方案对比**：`LEN2`：当作 STRING 长度（字节数，多字节字符不对）；`STRING_TO_UTF8` 不算长度只转换。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.23 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483035787.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
