# FindAndDelete

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200570507.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndDelete.xml`](../examples/P_Demo_FindAndDelete.xml) |

---

## 1. 功能简述

在源串中查找子串的**所有出现位置**并删除，把剩余拼起来写到目标；返回值是删除次数。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pDeleteString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pDeleteString` | `POINTER TO STRING` | — | 要删除的子串地址。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址（结果写入）。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功删除的子串次数；0 = 未找到该子串。 |

## 3. 行为说明

函数无状态。从左到右扫描 `pSrcString`，找到 `pDeleteString` 匹配就跳过该段不写入 `pDstString`，否则写入；继续扫描直到源串 null。结果末尾写 null 终结符。返回值是匹配次数。`pDstString` 缓冲不够时截断（结果不完整、但返回值仍是已删除的子串数）。最多扫描 `Parameterlist.cMaxCharacters` 字符。

## 4. 错误码 / 返回值

返回 `UDINT`：成功删除的子串次数；0 = 未找到该子串。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- 删除是**不重叠**的：删除完一段后从该段之后继续扫，不会回到前面。例如 `'aaaa'` 删除 `'aa'` 得 `''`（2 次），不是 `'a'`。
- `pDeleteString` 为空时行为 ⚠️ PDF/InfoSys 未明确——稳妥起见调用前判 `LEN(del) > 0`。
- 目标缓冲足够大时不会丢数据（在最坏情况 = 源串原长）；建议 `nDstSize >= SIZEOF(src)`。
- 区分大小写。要大小写不敏感请先把两边都 `F_ToUCase` 再调用。
- 返回值是**子串数**，不是字节数。需要算字节差请用 `LEN(src) - LEN(dst)`。
- in-place（src=dst）安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndDelete.xml`](../examples/P_Demo_FindAndDelete.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HTML 转纯文本：用 `FindAndDelete` 把 `'<br>'`、`'</p>'` 等固定标签整批删掉。
- **价值**：不用本函数则需 `FIND2` + `DELETE2` 循环，至少 8 行；本函数 1 行解决，并返回总删除次数用于报表。
- **替代方案对比**：`FindAndReplace` 把目标改成空串：等价但语义不直观；正则替换：TwinCAT 标准库无原生 regex。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.7 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200570507.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
