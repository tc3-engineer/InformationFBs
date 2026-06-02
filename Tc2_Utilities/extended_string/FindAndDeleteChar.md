# FindAndDeleteChar

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200594955.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndDeleteChar.TcPOU`](../examples/P_Demo_FindAndDeleteChar.TcPOU) |

---

## 1. 功能简述

`FindAndDelete` 的**单字符版本**——删除所有指定字符。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    sDeleteChar : STRING(1);
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `sDeleteChar` | `STRING(1)` | — | 要删除的单字符。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功删除的字符次数；0 = 未找到该字符。 |

## 3. 行为说明

逻辑与 `FindAndDelete` 相同——从左到右扫描源串，遇到匹配字符就跳过不写入目标，否则原样写入；最后写 null 终结符。区别在于匹配单字符比较快：每个源字节只与 `sDeleteChar` 的首字节直接比较，不需要进入子串匹配状态机。`sDeleteChar` 是 `STRING(1)`：传 `'X'` 删大写 X，传 `' '` 删空格，传 `'	'` 删 Tab（编辑器渲染对应字符）。返回值是删除次数，便于业务统计被清理掉的字符数。最多扫描 `Parameterlist.cMaxCharacters` 字符以防 null 缺失死循环。in-place（pSrcString = pDstString）安全。

## 4. 错误码 / 返回值

返回 `UDINT`：成功删除的字符次数；0 = 未找到该字符。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **只删 1 字符**。要删多个字符（如同时删 `' '` 和 `'	'`）需多次调用。
- 区分大小写。
- `sDeleteChar` 必须长度恰为 1。传 `'XY'` 行为 ⚠️ PDF/InfoSys 未明确。
- 比 `FindAndDelete(..., ADR('X'), ...)` 写法更简洁——单字符场景首选 `FindAndDeleteChar`。
- in-place 安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndDeleteChar.TcPOU`](../examples/P_Demo_FindAndDeleteChar.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：清理 CSV 字段：删除所有 `	` Tab 字符；或者把电话号码中的 `-` 和 ` ` 都删掉只保留数字。
- **价值**：比 `FindAndDelete` 调用更省事——单字符常量直接写入参数，不用预先声明 STRING 变量取地址。
- **替代方案对比**：`FindAndDelete`：子串版本，更通用；`FindAndReplaceChar(..., '')`：替换为空（不太直观）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.8 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200594955.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
