# CONCAT2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483024651.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_CONCAT2.TcPOU`](../examples/P_Demo_CONCAT2.TcPOU) |

---

## 1. 功能简述

把两个 **任意长度** `STRING` 拼接，比 `Tc2_Standard.CONCAT` 突破了 255 字符限制；返回 `BOOL` 标记是否完整拼接（未截断）。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcString1 : POINTER TO STRING;
    pSrcString2 : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcString1` | `POINTER TO STRING` | — | 前段 `STRING` 变量地址（`ADR(sA)`）。 |
| `pSrcString2` | `POINTER TO STRING` | — | 后段 `STRING` 变量地址（`ADR(sB)`）。 |
| `pDstString` | `POINTER TO STRING` | — | 目标 `STRING` 变量地址（`ADR(sOut)`）。可与某个源同址（in-place 自拼接）。 |
| `nDstSize` | `UDINT` | — | 目标缓冲区字节数。用 `SIZEOF(sOut)`；含 null 终结符位置。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 拼接全部成功；`FALSE` = 结果超出 `nDstSize` 被截断、内存溢出风险，调用方应丢弃结果。 |

## 3. 行为说明

函数无状态、立即返回。内部按字节扫描 `pSrcString1` 到 `nul`、追加 `pSrcString2` 到 `nul`、写入 `pDstString` 并以 `nul` 收尾。如果累计长度（不含 null 终结符）超过 `nDstSize - 1`，则按 `nDstSize - 1` 截断，写 null 终结符，返回 `FALSE`。为防止 `pSrcStringN` 未正确以 null 结尾导致的无限循环，函数最多扫描 `Tc2_Utilities.Parameterlist.cMaxCharacters` 个字符（默认 1024×1024 = 约 1M）后强制停止。`pDstString` 与某个源同址时，函数内部会先拼到临时缓冲再 memcpy，所以 in-place 自拼接是安全的。返回值 `FALSE` 时 `*pDstString` 中是被截断的结果，**不可作为完整字符串使用**——业务侧应丢弃或转为错误处理。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 拼接全部成功；`FALSE` = 结果超出 `nDstSize` 被截断、内存溢出风险，调用方应丢弃结果。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nDstSize` 用 `SIZEOF` 不要用 `LEN`**：`SIZEOF(sA)` 是声明字节数（包含 null 位）；`LEN(sA)` 是当前实际字符数。错传会导致缓冲溢出。
- **返回 `FALSE` 必须当错误处理**。截断后 `pDstString` 内容已损坏（典型场景：日志拼装时把 alarm code 拼到 message 后却截断，下游解析失败）。
- **只接受 `STRING`，不接受 `WSTRING`**。WSTRING 拼接请用 `WCONCAT2`。
- **`Tc2_Standard.CONCAT` 限制 255 字符**——长字符串场景必须用 `CONCAT2`；混用 `CONCAT` + 长 STRING 会得到错误结果（CONCAT 看到的 NUL 已经超过 255 字符指针）。
- **指针参数必须用 `ADR`**，不能直接传 STRING 变量。`CONCAT2(sA, sB, ...)` 会编译失败（类型不匹配）。
- 源串和目标串可重叠（in-place 安全），但建议拆开声明以提高可读性。
- 扫描上限 `Parameterlist.cMaxCharacters` 是全局参数，需要更长串拼接时（罕见）需要修改全局参数表，不是本函数的入参。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CONCAT2.TcPOU`](../examples/P_Demo_CONCAT2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：日志聚合：把模块名 ("PumpCtrl") + ': ' + 详细错误描述 + ' @ ' + 时间戳拼成完整日志行。完整日志 > 255 字符时 `Tc2_Standard.CONCAT` 直接溢出，必须用 `CONCAT2`。
- **价值**：替代 `Tc2_Standard.CONCAT` + 长度检查 + 多次声明 `STRING(80)`/`STRING(255)`/`STRING(1024)` 的混乱体系，统一用 `STRING` + `CONCAT2` 即可。返回值 `BOOL` 提供超长检测，比裸 `CONCAT` 更安全。
- **替代方案对比**：`Tc2_Standard.CONCAT`：限 255 字符；`WCONCAT2`：Unicode 版本；`MEMCPY`：手动版本但容易写错 null 终结符。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.2 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483024651.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
