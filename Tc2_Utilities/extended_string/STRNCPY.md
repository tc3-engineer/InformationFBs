# STRNCPY

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483034251.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRNCPY.xml`](../examples/P_Demo_STRNCPY.xml) |

---

## 1. 功能简述

安全的 STRING 复制——比 `:=` 多了 size 检查与截断告警；返回 `BOOL` 表明是否完整复制，并输出源/目标实际长度便于诊断。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDst : POINTER TO STRING;
    pSrc : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR

VAR_OUTPUT
    nSrcLen : UDINT;
    nDstLen : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDst` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `pSrc` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### VAR_OUTPUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nSrcLen` | `UDINT` | 源 STRING 实际字符长度。 |
| `nDstLen` | `UDINT` | 目标 STRING 复制后字符长度（截断时 < 源长）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 完整复制；`FALSE` = 源比目标长，被截断（含 null）。 |

## 3. 行为说明

函数无状态、立即返回。算法：把 `pSrc` 起始的字节流（直到 null 或 `nDstSize - 1` 字节为止）复制到 `pDst`，然后**始终写入 null 终结符**（这与 C 的 strncpy 不同——C strncpy 不保证 null 终结）。同时统计 `nSrcLen`（源实际字符长度，扫描到源 null 处的字节数）和 `nDstLen`（目标实际字符长度，截断时 < 源长）。源 ≤ 目标缓冲时 → 返回 `TRUE`、`nSrcLen = nDstLen`；源 > 目标 → 返回 `FALSE`、`nDstLen = nDstSize - 1`、调用方可通过 `nSrcLen - nDstLen` 量化丢失的字符数。最多扫描 `Parameterlist.cMaxCharacters` 字符防 null 缺失死循环。in-place（pDst = pSrc）作为 self-copy 返回 `TRUE`、无副作用。`nDstSize = 0` 行为 ⚠️ 未明确——建议调用前断言 `nDstSize >= 1`。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 完整复制；`FALSE` = 源比目标长，被截断（含 null）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **目标缓冲不够时只复制 `nDstSize - 1` 字节**——保证 null 终结。
- **返回 `FALSE` 必须当错误处理**——结果被截断。
- `:=` STRING 复制本身在 TwinCAT 里也安全（编译期 size 已知），**本函数适合指针场景**（运行时大小未知 / 跨 buffer 复制）。
- `pDst = pSrc`（自复制）当作正常情况：返回 `TRUE`，无副作用。
- **对照 C 的 strncpy 区别**：C strncpy 不保证 null 终结；本函数**保证 null 终结**。
- `nDstSize = 0` 行为 ⚠️ 未明确——建议先判 `nDstSize >= 1`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRNCPY.xml`](../examples/P_Demo_STRNCPY.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从动态数组 `ARRAY OF STRING(N)` 中按索引复制一行到固定 buffer——索引可能越界，需要边界保护的 `STRNCPY` 比 `:=` 更安全。
- **价值**：替代 `:=` + 自写长度检查；返回值 + 长度输出便于诊断越界场景。
- **替代方案对比**：`:=` 直接复制（编译期 size 已知时即可）；`WSTRNCPY`：WSTRING 版本；`MEMCPY` + 手写 null：易错。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.20 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483034251.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
