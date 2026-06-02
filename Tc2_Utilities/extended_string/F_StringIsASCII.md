# F_StringIsASCII

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483026187.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_StringIsASCII.TcPOU`](../examples/P_Demo_F_StringIsASCII.TcPOU) |

---

## 1. 功能简述

检查 `STRING` 是否只包含纯 ASCII（0x00 ~ 0x7F），同时返回字符数。纯 ASCII 串可直接当 UTF-8 用而不需要 `STRING_TO_UTF8` 转换。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSTRING : POINTER TO STRING;
END_VAR

VAR_OUTPUT
    nLen : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSTRING` | `POINTER TO STRING` | — | 待检查的 STRING 变量地址。 |

### VAR_OUTPUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nLen` | `UDINT` | 字符串中 ASCII 字符的数量（不含 null 终结符）；含义同 `LEN()`，但本函数顺便扫了一次内容。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 字符串只包含 ASCII（0x00 ~ 0x7F）字符，可直接当作 UTF-8 使用；`FALSE` = 含非 ASCII 字节（高位为 1）。 |

## 3. 行为说明

函数无状态、立即返回。逐字节扫描 `pSTRING` 直到 null 或 `Parameterlist.cMaxCharacters` 上限；若任一字节高位为 1（即 ≥ 0x80），立即返回 `FALSE` 并 `nLen` 设为扫描到该处的 ASCII 计数；若全为 ASCII 字符，扫到 null 后返回 `TRUE`，`nLen` = 字符总数。该函数的意义在于：UTF-8 与 ASCII 兼容（ASCII 字符在 UTF-8 中是单字节、且高位为 0），所以**纯 ASCII 串可以零拷贝地直接送给 UTF-8 API**，省去 `STRING_TO_UTF8` 这一次扫描+复制的开销。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 字符串只包含 ASCII（0x00 ~ 0x7F）字符，可直接当作 UTF-8 使用；`FALSE` = 含非 ASCII 字节（高位为 1）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- 返回 `nLen` 等同 `LEN(s)`（前提是纯 ASCII），但**额外做了 ASCII 校验**；不需要校验只算长度请用 `LEN2`。
- Latin-1 / Windows-1252 编码的字符（0x80 ~ 0xFF）会被判为非 ASCII，但它们在某些区域设置下是合法的；**本函数从 UTF-8 兼容角度判断，不考虑区域**。
- 函数遇到 null 字节即停止——所以中间含 0x00 的二进制串会被错判（结果偏短）。仅用于文本，不要用于二进制数据。
- **用法**：常配合 `STRING_TO_UTF8` —— 先用 `F_StringIsASCII` 判 `TRUE` 跳过转换直接 memcpy；否则走完整 UTF-8 转码。性能优化点。
- 扫描上限 `cMaxCharacters` 与 CONCAT2 等共用；超长串可能在到达 null 前停止。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_StringIsASCII.TcPOU`](../examples/P_Demo_F_StringIsASCII.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OPC UA 服务器把 PLC 字符串变量发布出去，UA 协议要求 UTF-8。先 `F_StringIsASCII` 判一下：是 ASCII 直接发；不是再走 `STRING_TO_UTF8` 转换。
- **价值**：高频日志/标签场景下，跳过不必要的 STRING→UTF8 转换可显著降低 CPU 占用（典型生产环境 90% 的 PLC 字符串都是纯 ASCII）。
- **替代方案对比**：`LEN`/`LEN2`：仅长度，不做 ASCII 检查；`STRING_TO_UTF8`：完整转换（即使是 ASCII 也走流程）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.5 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483026187.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
