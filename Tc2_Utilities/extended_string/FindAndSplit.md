# FindAndSplit

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/8235976331.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndSplit.xml`](../examples/P_Demo_FindAndSplit.xml) |

---

## 1. 功能简述

按分隔符把字符串切成左右两段（仅切一次）；支持从左或从右搜索，便于解析路径、URL、键值对。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSeparator : POINTER TO STRING;
    pSrcString : POINTER TO STRING;
    pLeftString : POINTER TO STRING;
    nLeftSize : UDINT;
    pRightString : POINTER TO STRING;
    nRightSize : UDINT;
    bSearchFromRight : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSeparator` | `POINTER TO STRING` | — | 分隔符 STRING 地址（如 `ADR('/')`、`ADR('==>')`）。 |
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pLeftString` | `POINTER TO STRING` | — | 左侧结果 STRING 地址。 |
| `nLeftSize` | `UDINT` | — | 左侧缓冲字节数（`SIZEOF`）。 |
| `pRightString` | `POINTER TO STRING` | — | 右侧结果 STRING 地址。 |
| `nRightSize` | `UDINT` | — | 右侧缓冲字节数（`SIZEOF`）。 |
| `bSearchFromRight` | `BOOL` | — | `TRUE` = 从右向左找第一个分隔符；`FALSE` = 从左向右找。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 找到分隔符并成功输出左右两段；`FALSE` = 未找到分隔符（或目标缓冲不够）。 |

## 3. 行为说明

函数无状态。`bSearchFromRight = FALSE` 时从左扫描找到第一个 `pSeparator` 匹配位置；`= TRUE` 时从右扫描找到最后一个匹配位置。左段 = 分隔符之前的子串；右段 = 分隔符之后的子串；分隔符**本身不出现**在任何一段。未找到分隔符返回 `FALSE`，两个目标串置空。多次切分（如 `'a/b/c/d'` 切成 4 段）需要在循环中重复调用：每次把 `pSrcString` 设为上轮的 `pRightString`，循环直到本函数返回 `FALSE` 表示分隔符不再出现。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 找到分隔符并成功输出左右两段；`FALSE` = 未找到分隔符（或目标缓冲不够）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **只切一次**！多段切分需要循环（典型 PDF 示例代码）。
- **找不到分隔符返 `FALSE`**——左右两段被清空，调用方须判返回值再用。
- `bSearchFromRight` 区别：路径 `'a/b/c'` 从左切左段 `'a'` 右段 `'b/c'`；从右切左段 `'a/b'` 右段 `'c'`。
- `pLeftString = pSrcString` 或 `pRightString = pSrcString` （in-place）行为 ⚠️ PDF/InfoSys 未明确——稳妥起见用独立缓冲。
- 缓冲不够会截断，**仍可能返回 `TRUE`**——业务侧应检查 `LEN(left) < nLeftSize - 1` 才算未截断。
- **多字符分隔符**（如 `'==>'`）支持；不要把它和 `FindAndSplitChar`（限单字符）混淆。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndSplit.xml`](../examples/P_Demo_FindAndSplit.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：解析 OPC UA NodeId 字符串 `'ns=2;s=Pump.State'`：用 `';'` 切左右段，再分别解析 `'ns=2'` 和 `'s=...'`。
- **价值**：替代 `FIND2` + `LEFT` + `MID` 三调用链；返回 `BOOL` 直观判断成功。
- **替代方案对比**：`FindAndSplitChar`：单字符分隔符更省事；多段循环：参考 PDF 4.2.11 示例。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.11 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/8235976331.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
