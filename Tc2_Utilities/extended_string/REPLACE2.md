# REPLACE2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200692747.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_REPLACE2.xml`](../examples/P_Demo_REPLACE2.xml) |

---

## 1. 功能简述

从源串 `nPos` 位置起替换 `nLen` 个字符为 `pInsertString`，写入目标；按位置替换（不按子串内容）。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pInsertString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
    nLen : UDINT;
    nPos : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pInsertString` | `POINTER TO STRING` | — | 替换字符串地址（用它顶替源串的某段）。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数。 |
| `nLen` | `UDINT` | — | 源串中要替换掉的字符数。 |
| `nPos` | `UDINT` | — | 替换起始位置（1 起算）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 成功替换；`FALSE` = 结果超 `nDstSize` 被截断。 |

## 3. 行为说明

函数无状态、立即返回。算法：把源串 `[1..nPos-1]` 区段复制到目标，追加 `pReplaceString` 内容，再追加源串 `[nPos+nLen..end]` 区段，最后写 null 终结符。**按位置替换不按内容**——这与 `FindAndReplace`（按子串匹配）的语义完全不同。`nLen` 比剩余字符多时按串尾停止——不会越界；`nPos = 0` 当 `nPos = 1` 处理（PDF 未明示，根据 INSERT2 类比推断 ⚠️ 建议调用前断言 `nPos > 0`）。替换字符串长度 ≠ 被替换长度时结果总长度自适应：`nDstSize` 不足返回 `FALSE` + 按 `nDstSize - 1` 截断。in-place（pSrcString = pDstString）安全：内部经临时缓冲。`Tc2_Standard.REPLACE` 限 255 字符，本函数无限制。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 成功替换；`FALSE` = 结果超 `nDstSize` 被截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **按位置替换不按内容**——和 `FindAndReplace` 不同；后者按子串匹配。
- **`nPos` 从 1 起算**；`nPos = 0` 行为 ⚠️ 待确认。
- 返回 `FALSE` 必须当错误。
- **`Tc2_Standard.REPLACE` 限 255 字符**——长串必须用 `REPLACE2`。
- 替换串可比原串长或短，结果长度自适应（受 `nDstSize` 限制）。
- in-place 安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_REPLACE2.xml`](../examples/P_Demo_REPLACE2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：时间字符串规范化：把固定位置的 `'?'` 替换为实际秒数（如 RFID 信号触发前秒数未知）。
- **价值**：替代 `LEFT` + `CONCAT2` + `MID` + `CONCAT2`；本函数 1 调用。
- **替代方案对比**：`FindAndReplace`：按内容；`Tc2_Standard.REPLACE`：限 255。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.16 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200692747.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
