# FindAndSplitChar

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/8245507851.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndSplitChar.TcPOU`](../examples/P_Demo_FindAndSplitChar.TcPOU) |

---

## 1. 功能简述

`FindAndSplit` 的单字符版本——分隔符直接传字符常量。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSeparatorChar : STRING(1);
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
| `sSeparatorChar` | `STRING(1)` | — | 分隔字符（单字符）。 |
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pLeftString` | `POINTER TO STRING` | — | 左侧结果 STRING 地址。 |
| `nLeftSize` | `UDINT` | — | 左侧缓冲字节数。 |
| `pRightString` | `POINTER TO STRING` | — | 右侧结果 STRING 地址。 |
| `nRightSize` | `UDINT` | — | 右侧缓冲字节数。 |
| `bSearchFromRight` | `BOOL` | — | `TRUE` = 从右向左搜索。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 找到分隔字符并成功输出左右两段；`FALSE` = 未找到。 |

## 3. 行为说明

逻辑同 `FindAndSplit`——按分隔符把源串切成左右两段（仅切一次）；但 `sSeparatorChar` 是直接 `STRING(1)` 字符常量（`'/'`、`':'` 等），不需要 `ADR`。`bSearchFromRight = FALSE` 从左扫第一个分隔字符位置；`= TRUE` 从右扫最后一个。分隔字符本身不出现在任何输出段。**多段切分推荐写法是循环**：每次切完把右段当作下一轮的源，直到 `FALSE` 表示切完——PDF 4.2.12 给了完整循环模板。缓冲不够时仍可能返回 `TRUE`（结果被截断），调用方需检查 `LEN(left/right) < nLeftSize/nRightSize - 1` 才算未截断。最多扫描 `Parameterlist.cMaxCharacters` 防 null 缺失死循环。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 找到分隔字符并成功输出左右两段；`FALSE` = 未找到。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- 同 `FindAndSplit` 的注意点，但分隔符限单字符。
- **循环切分典型模板**：用 `WHILE bFound DO ... bFound := FindAndSplitChar(...); END_WHILE`——每次把右段当下一轮的源继续切，直到返回 `FALSE` 表示分隔符不再出现。
- in-place 行为 ⚠️ 未明确——稳妥起见独立缓冲。
- 缓冲不够也可能返回 `TRUE`（截断），需检查 `LEN < nSize - 1`。
- 区分大小写。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndSplitChar.TcPOU`](../examples/P_Demo_FindAndSplitChar.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：切分文件路径：`'/srv/data/log/2026-05.log'` 按 `/` 切——典型循环切到所有段。
- **价值**：比 `FindAndSplit` 更简洁——单字符场景无需先 `STRING(1)` 声明。
- **替代方案对比**：`FindAndSplit`：多字符分隔符；C 风格 `STRTOK` 不存在于 TwinCAT 标准库。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.12 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/8245507851.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
