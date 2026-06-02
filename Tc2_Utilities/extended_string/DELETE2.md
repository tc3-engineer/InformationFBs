# DELETE2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200521611.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_DELETE2.TcPOU`](../examples/P_Demo_DELETE2.TcPOU) |

---

## 1. 功能简述

从源串中删除从 `nPos` 开始的 `nLen` 个字符，把剩余串写入目标；比 `Tc2_Standard.DELETE` 突破 255 字符限制。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
    nLen : UDINT;
    nPos : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString` | `POINTER TO STRING` | — | 源 STRING 地址。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址；可与源同址（in-place 删除）。 |
| `nDstSize` | `UDINT` | — | 目标缓冲区字节数（`SIZEOF`）。 |
| `nLen` | `UDINT` | — | 要删除的字符数。 |
| `nPos` | `UDINT` | — | 起始字符位置（1 = 第一个字符）；要删除 `[nPos, nPos+nLen-1]` 区间。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 成功删除并写入目标；`FALSE` = 目标缓冲区放不下结果，被截断。 |

## 3. 行为说明

函数无状态、立即返回。算法分三步：第一步扫描源串到 null 计算总长；第二步把 `pSrcString` 中 `[1..nPos-1]` 区段复制到 `pDstString`；第三步把 `[nPos+nLen..end]` 区段追加到 `pDstString` 并写 null 终结符。`nPos` 从 1 起算（IEC 习惯），`nPos = 1` 意味删除头部 `nLen` 字符。若 `nPos = 0` 或 `nPos > LEN(src)`，目标 = 源（无变化）；`nLen` 太大时直接到串尾停止——不会越界访问。结果总长 ≥ `nDstSize` 时按 `nDstSize - 1` 截断并返回 `FALSE`，目标缓冲虽然写满 null 但结果内容不完整应作错误处理。函数最多扫描 `Parameterlist.cMaxCharacters` 字符防止 null 缺失导致死循环。in-place 操作（src=dst）安全，因为内部先到临时缓冲再 memcpy。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 成功删除并写入目标；`FALSE` = 目标缓冲区放不下结果，被截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nPos` 从 1 起算**（不是 0）；想删头字符传 `nPos := 1`。`nPos := 0` 会被忽略。
- **返回 `FALSE` 必须当错误处理**——目标缓冲区不够，结果已损坏。
- in-place（`pSrcString = pDstString`）安全：函数内部用临时缓冲。
- 不接受 WSTRING；Unicode 版需要自行用指针运算 + `MEMCPY` 实现。
- **容易和 `FindAndDelete` 混淆**：`DELETE2` 按 **位置/长度**；`FindAndDelete` 按 **子串内容** 删除（找到匹配就删）。
- **`Tc2_Standard.DELETE` 限 255 字符**——`STRING(1024)` 必须用 `DELETE2`。
- 返回 `BOOL` 而非删除字符数；业务统计删除字符数请用 `LEN(src) - LEN(dst)`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DELETE2.TcPOU`](../examples/P_Demo_DELETE2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：数据清洗：从用户输入的 `STRING(1024)` 中去掉特定位置的固定前缀（如设备号开头的 'EL-' 前 3 字符）。
- **价值**：替代手动 `LEFT` + `RIGHT` + `CONCAT2` 的 3 调用链；本函数 1 调用即可。
- **替代方案对比**：`FindAndDelete`：按子串内容；`Tc2_Standard.DELETE`：限 255 字符；指针 + MEMCPY：手写易错。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.4 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/6200521611.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
