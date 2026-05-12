# WCONCAT2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483043467.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WCONCAT2.xml`](../examples/P_Demo_WCONCAT2.xml) |

---

## 1. 功能简述

`CONCAT2` 的 WSTRING 版本——拼接两个任意长度 WSTRING。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcWString1 : POINTER TO WSTRING;
    pSrcWString2 : POINTER TO WSTRING;
    pDstWString : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcWString1` | `POINTER TO WSTRING` | — | 前段 WSTRING 地址。 |
| `pSrcWString2` | `POINTER TO WSTRING` | — | 后段 WSTRING 地址。 |
| `pDstWString` | `POINTER TO WSTRING` | — | 目标 WSTRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`，WSTRING 每字符 2 字节）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 拼接成功；`FALSE` = 结果超 `nDstSize` 被截断。 |

## 3. 行为说明

函数无状态、立即返回。算法与 `CONCAT2` 完全相同——扫描 `pSrcWString1` 到 16 位 null、追加 `pSrcWString2` 到 16 位 null、写入 `pDstWString` 并以 16 位 null 收尾——区别在于操作的是 16 位字符（WSTRING / UTF-16）而不是 8 位字符（STRING）。**`nDstSize` 是字节数而非字符数**：`WSTRING(N)` 的 `SIZEOF` = (N + 1) × 2 字节。结果总字符数（含 null） × 2 > `nDstSize` 时按 `(nDstSize / 2) - 1` 个字符截断、写 null 终结符并返回 `FALSE`，调用方须丢弃结果。函数为防 16 位 null 缺失导致的死循环，最多扫描 `Parameterlist.cMaxCharacters` 字符。in-place（pSrc1/pSrc2 = pDst）安全，内部经临时缓冲再 memcpy。`Tc2_Standard.WCONCAT` 限 255 字符，本函数无限制。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 拼接成功；`FALSE` = 结果超 `nDstSize` 被截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nDstSize` 是字节数**——WSTRING(N) 的 SIZEOF = (N+1) × 2 + 2 字节。
- 返回 `FALSE` 必须当错误处理。
- in-place 安全。
- STRING 版本走 `CONCAT2`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WCONCAT2.xml`](../examples/P_Demo_WCONCAT2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 多语言消息拼装：`'Pump '` + `'Status: '` + `'Running'`（WSTRING）。
- **价值**：`Tc2_Standard.WCONCAT` 限 255 字符；本函数无限制。
- **替代方案对比**：`CONCAT2`：STRING 版本；`WSTRING_TO_UTF8` → `STRING_TO_UTF8` 中转。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.25 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483043467.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
