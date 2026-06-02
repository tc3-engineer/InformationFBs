# FindAndReplace

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200619403.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndReplace.TcPOU`](../examples/P_Demo_FindAndReplace.TcPOU) |

---

## 1. 功能简述

把源串中**所有出现**的 `pDeleteString` 替换为 `pInsertString`，写入目标。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pDeleteString : POINTER TO STRING;
    pInsertString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pDeleteString` | `POINTER TO STRING` | — | 要替换的旧子串地址。 |
| `pInsertString` | `POINTER TO STRING` | — | 要插入的新子串地址。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功替换的子串次数；0 = 未找到。 |

## 3. 行为说明

函数无状态。从左到右扫描，每次匹配到 `pDeleteString` 就跳过该段、写入 `pInsertString` 代替；不匹配则原样写入。结果以 null 收尾。**替换后从插入串之后继续扫描**——避免对刚插入的内容重复替换（避免无限递归）。返回匹配次数。最多扫描 `Parameterlist.cMaxCharacters` 字符。

## 4. 错误码 / 返回值

返回 `UDINT`：成功替换的子串次数；0 = 未找到。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **目标缓冲注意**：新串可能比旧串长，结果可能更长。建议 `nDstSize >= LEN(src) * (LEN(insert)/MAX(1,LEN(delete)))`。最稳妥 `STRING(1024)` 起步。
- 替换后**从插入串之后继续扫**——不会无限递归。例：`'aaa'` 把 `'a'` 换成 `'aa'` 得 `'aaaaaa'`（3 次），不是无限。
- `pDeleteString` 为空时 ⚠️ PDF/InfoSys 未明确——调用前判 `LEN(delete) > 0`。
- 区分大小写。
- **典型滥用**：把多种字符全替换成空——更适合用 `FindAndDeleteChar` 循环。
- in-place（src=dst）安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndReplace.TcPOU`](../examples/P_Demo_FindAndReplace.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把日志中的占位符 `'{ts}'`、`'{level}'`、`'{msg}'` 替换为实际值。
- **价值**：替代 `STRING_TO_UTF8` + 字节级 MEMCPY 替换的 30 行循环；本函数 1 行解决。
- **替代方案对比**：`FindAndReplaceChar`：单字符；`STRING_TO_FormatString` 类的 sprintf：更适合格式化但语义不一样。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.9 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200619403.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
