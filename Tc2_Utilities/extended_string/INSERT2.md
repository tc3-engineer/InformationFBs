# INSERT2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200668299.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_INSERT2.TcPOU`](../examples/P_Demo_INSERT2.TcPOU) |

---

## 1. 功能简述

在源串的第 `nPos` 个字符之后插入子串，写入目标；比 `Tc2_Standard.INSERT` 突破 255 字符限制。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pInsertString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
    nPos : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pInsertString` | `POINTER TO STRING` | — | 要插入的子串地址。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |
| `nPos` | `UDINT` | — | 插入位置；`nPos = 0` 表示插到最前面，`nPos = N` 表示插到第 N 个字符之后。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 成功插入；`FALSE` = 结果超 `nDstSize` 被截断。 |

## 3. 行为说明

函数无状态、立即返回。算法：把 `pSrcString[1..nPos]` + `pInsertString` + `pSrcString[nPos+1..end]` 顺序拼接写入 `pDstString`，写 null 终结符。`nPos = 0` 时等价于在头部插入；`nPos = LEN(src)` 时等价于在尾部插入（与 `CONCAT2` 等效）；`nPos > LEN(src)` 时不报错，按 `nPos = LEN(src)` 处理（追加到尾）。如果 `LEN(pSrcString) + LEN(pInsertString) >= nDstSize`，结果被按 `nDstSize - 1` 截断、写 null 终结符并返回 `FALSE`。in-place（pSrcString = pDstString 或 pInsertString = pDstString）安全：内部经临时缓冲再 memcpy。最多扫描 `Parameterlist.cMaxCharacters` 字符以防 null 缺失。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 成功插入；`FALSE` = 结果超 `nDstSize` 被截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nPos` 是字符位置（1 起算）**，`nPos = 0` = 头部，`nPos = LEN` = 尾部（等价 `CONCAT2`）。
- 返回 `FALSE` 必须当错误处理——结果已截断。
- in-place（src=dst）安全。
- `Tc2_Standard.INSERT` 限 255 字符，长串必须用 `INSERT2`。
- 插入空串（`LEN(insert) = 0`）= 复制源到目标——不报错但无副作用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_INSERT2.TcPOU`](../examples/P_Demo_INSERT2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：日志行加时间戳前缀：`INSERT2(src=msg, insert=ts+' ', pos=0)` 写到完整日志缓冲。
- **价值**：替代 `LEFT` + `CONCAT2` + `MID` + `CONCAT2` 的 4 步链；本函数 1 行调用。
- **替代方案对比**：`Tc2_Standard.INSERT`：限 255；CONCAT2 + 拆开拼接：更繁琐。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.14 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200668299.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
