# WSTRNCPY

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483063563.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WSTRNCPY.xml`](../examples/P_Demo_WSTRNCPY.xml) |

---

## 1. 功能简述

`STRNCPY` 的 WSTRING 版本——安全的 WSTRING 复制。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDst : POINTER TO WSTRING;
    pSrc : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR

VAR_OUTPUT
    nSrcLen : UDINT;
    nDstLen : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDst` | `POINTER TO WSTRING` | — | 目标 WSTRING 地址。 |
| `pSrc` | `POINTER TO WSTRING` | — | 源 WSTRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### VAR_OUTPUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nSrcLen` | `UDINT` | 源 WSTRING 字符长度。 |
| `nDstLen` | `UDINT` | 目标 WSTRING 复制后字符长度。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 完整复制；`FALSE` = 截断。 |

## 3. 行为说明

函数无状态、立即返回。算法与 `STRNCPY` 完全相同——把 `pSrc` 起始的 WSTRING 内容（直到 16 位 null 或 `nDstSize / 2 - 1` 字符为止）复制到 `pDst`，**始终写入 16 位 null 终结符**保证 WSTRING 合法。同时统计 `nSrcLen`（源字符长度）和 `nDstLen`（目标字符长度，截断时小于源长）。源 ≤ 目标缓冲容量时 → 返回 `TRUE`、两 len 相等；源 > 目标 → 返回 `FALSE`、`nDstLen = nDstSize / 2 - 1`；调用方可通过 `nSrcLen - nDstLen` 量化丢失字符数。**`nDstSize` 是字节数**（WSTRING 每字符 2 字节）。in-place（pDst = pSrc）作为 self-copy 返回 `TRUE`、无副作用。最多扫描 `Parameterlist.cMaxCharacters` 字符防 null 缺失死循环。`Tc2_Standard` 中无对应的 `WSTRNCPY`——本函数填补空缺。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 完整复制；`FALSE` = 截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- `nDstSize` 是字节数（WSTRING 每字符 2 字节）。
- 保证 null 终结。
- 返 `FALSE` 必须当错误处理。
- in-place（self-copy）安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WSTRNCPY.xml`](../examples/P_Demo_WSTRNCPY.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 字符串缓冲动态复制——索引可能越界，比 `:=` 更安全。
- **价值**：`Tc2_Standard.WSTRNCPY` ⚠️ 不存在（标准库无对应）——本函数填补 WSTRING 安全复制空缺。
- **替代方案对比**：`STRNCPY`：STRING 版本；`:=` 直接复制（编译期 size 已知）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.30 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483063563.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
