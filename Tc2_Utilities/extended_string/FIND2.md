# FIND2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200546059.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIND2.xml`](../examples/P_Demo_FIND2.xml) |

---

## 1. 功能简述

在长 `STRING` 中查找子串第一次出现的位置，返回起始字符序号（1 起算），未找到返 0；比 `Tc2_Standard.FIND` 突破 255 字符限制。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pFindString : POINTER TO STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 待搜索的源 STRING 地址。 |
| `pFindString` | `POINTER TO STRING` | — | 要查找的子串地址。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | **找到时**：第一次出现位置的起始字符序号（从 1 起算）。**未找到时**：返回 0。 |

## 3. 行为说明

函数无状态。从 `pSrcString[1]` 起线性扫描，逐字符比较 `pFindString` 的前 N 个字符（N = `LEN(pFindString^)`）；找到第一次完全匹配返回起始位置（1 起算）；扫到 `pSrcString` 的 null 终结符仍未匹配返 0。最多扫描 `Parameterlist.cMaxCharacters` 字符防止 null 丢失导致死循环。子串为空（`LEN(pFindString^) = 0`）时返回 1（约定：空子串总是出现在位置 1）。

## 4. 错误码 / 返回值

返回 `UDINT`：**找到时**：第一次出现位置的起始字符序号（从 1 起算）。**未找到时**：返回 0。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **返回 1 起算**（IEC 字符串习惯），不是 C 的 0 起算。后续用 `MID(s, len, pos)` 取子串可直接传 `FIND2` 的返回值。
- **未找到 = 0**，不是 `-1`（UDINT 无符号）。代码必须 `IF nPos > 0 THEN ... END_IF;` 守护。
- 只找**第一次出现**。要找全部出现请循环：第一次找到后，把搜索起点改为 `nPos + LEN(find)` 重新调用——但本函数没有偏移参数，需要手工 `MID(src, ..., nPos+LEN(find))` 取剩余子串再搜。多次替换更适合用 `FindAndReplace`。
- **`Tc2_Standard.FIND` 限 255 字符**；长串必须用 `FIND2`。
- 子串 `pFindString` 为空时返 1，**不是 0**——这与 strstr(NULL) 在 C 中的行为不同；做空判时要在调用前 `IF LEN(find) > 0 THEN ... END_IF;`。
- 区分大小写。要大小写不敏感请先 `F_ToUCase(both)` 再 `FIND2`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIND2.xml`](../examples/P_Demo_FIND2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：解析 EtherCAT 配置 XML 字符串：找到 `'<Device>'` 标签的位置，再截取标签内容。
- **价值**：比 `Tc2_Standard.FIND` + 长度判断 + MID 拆解的链条更直接；返回值 1 起算与 `MID`/`INSERT`/`DELETE` 风格一致。
- **替代方案对比**：`Tc2_Standard.FIND`：限 255 字符；`FindAndSplit`：找到后顺便切分；`FindAndReplace`：找到后顺便替换。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.6 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200546059.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
