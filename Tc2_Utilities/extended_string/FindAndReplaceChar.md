# FindAndReplaceChar

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200643851.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndReplaceChar.TcPOU`](../examples/P_Demo_FindAndReplaceChar.TcPOU) |

---

## 1. 功能简述

把源串中所有 `sDeleteChar` 字符替换为 `sInsertChar` 字符；单字符版的 `FindAndReplace`。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    sDeleteChar : STRING(1);
    sInsertChar : STRING(1);
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `sDeleteChar` | `STRING(1)` | — | 要替换掉的旧字符。 |
| `sInsertChar` | `STRING(1)` | — | 替换为的新字符。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功替换的字符次数。 |

## 3. 行为说明

按字符 1:1 替换——逐字节扫描源串，每遇到一个匹配 `sDeleteChar` 的字节就写入 `sInsertChar` 的字节到目标，否则原样写入；最后写 null 终结符。**结果长度恒等于源长度**（单字符 1:1，不增不减）。`sDeleteChar` = 旧字符（单字符 STRING(1)）；`sInsertChar` = 新字符（单字符 STRING(1)）。区分大小写：把 `'a'` 换成 `'A'` 不会顺带替换 `'A'` 自己。函数 in-place（pSrcString = pDstString）安全。最多扫描 `Parameterlist.cMaxCharacters` 字符防 null 缺失死循环。返回值是替换次数，便于业务统计或日志诊断。

## 4. 错误码 / 返回值

返回 `UDINT`：成功替换的字符次数。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- 结果长度 == 源长度（单字符替换不改变长度）；`nDstSize >= LEN(src) + 1` 即可。
- **只换 1 字符**。要把 `' '` 和 `'	'` 都换成 `'_'` 需调用两次。
- `sInsertChar = ''`（空串）的行为 ⚠️ PDF/InfoSys 未明确——想删字符请用 `FindAndDeleteChar`。
- 区分大小写。
- in-place 安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndReplaceChar.TcPOU`](../examples/P_Demo_FindAndReplaceChar.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：文件名规范化：把空格 `' '` 替换为下划线 `'_'`；CSV 字段清洗：把字段内的逗号 `,` 替换为分号 `;`。
- **价值**：比 `FOR` + 字节比较 + 写入的手动循环更直观；O(N) 时间。
- **替代方案对比**：`FindAndReplace`：子串版本；`FOR` 循环：手写 + null 终止判断易错。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.10 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200643851.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
