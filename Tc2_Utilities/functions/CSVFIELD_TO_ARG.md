# CSVFIELD_TO_ARG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/18014398544558091.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_CSVFIELD_TO_ARG.xml`](../examples/P_Demo_CSVFIELD_TO_ARG.xml) |

---

## 1. 功能简述

把字节缓冲中的一个 CSV 字段（pInput 指向、长度 cbInput）反序列化成 PLC 变量（通过 `T_Arg` 描述目标变量的地址、类型、长度）。CSV 转义规则：字段内的连续两个双引号被还原为一个单独的双引号；若 `bQM = TRUE`，则去掉字段最外层包裹的双引号后再写入目标。

成功返回写入目标变量的字节数；输入为空、出错或不可识别时返回 0。与 `CSVFIELD_TO_STRING` 的本质区别在于：本函数允许 CSV 字段含二进制数据（如 `INT` / `REAL`），目标类型由 `T_Arg` 显式声明；而 `CSVFIELD_TO_STRING` 只能把字段当字符串处理，遇到内嵌 `00` 字节会被截断。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pInput   : POINTER TO BYTE;
    cbInput  : UDINT;
    bQM      : BOOL;
    out      : T_Arg;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pInput` | `POINTER TO BYTE` | — | 待转换 CSV 字段所在字节缓冲的起始地址，常用 `ADR()` 取得。 |
| `cbInput` | `UDINT` | — | 待转换字段长度（字节），常用 `SIZEOF()` 取得。 |
| `bQM` | `BOOL` | — | 引号模式（QM = quotation marks）：`TRUE` = 字段外层包裹双引号、需剥去；`FALSE` = 字段没有外层引号。 |
| `out` | `T_Arg` | — | 目标 PLC 变量的描述结构（`T_Arg`，含变量地址 + 类型 + 容量）。应用必须保证容量足够装下解析结果。 |

### VAR_IN_OUT

无（`out` 是 `VAR_INPUT` 的 `T_Arg`，但其 `.pData` 指向用户变量，函数通过该指针写回结果）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功写入目标变量的字节数；输入空、解析失败、目标容量不足返回 0。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数按 CSV 规范扫描 [pInput, pInput+cbInput) 字节区间：

1. **去外层引号（bQM）**：若 `bQM = TRUE`，跳过首尾各一个 `"` 字节；剩余内容是真实数据。
2. **CSV 转义还原**：把字段中连续两个 `"` 替换为单个 `"`，恢复用户原意。
3. **写入目标**：按 `out.eType`（`T_Arg` 内的类型 enum）把字段解析为对应类型并写到 `out.pData`。若是字符串类型，新字符串受 `out.nLen`（容量）限制；若是数值，按字面 `STRING_TO_xxx` 规则转换。
4. **返回值**：写入字节数，便于上层游标推进。

应用模式：通常和 `FB_CSVMemBufferReader` 配合，先把 CSV 文件读到内存 buffer，再逐字段调用 `CSVFIELD_TO_ARG`，把字段写入结构体不同字段。要构造 `T_Arg` 描述子，用 `F_BYTE` / `F_WORD` / `F_DWORD` / `F_INT` / `F_REAL` / `F_STRING` 等辅助函数（同库提供）。

陷阱：`bQM = TRUE` 但字段实际没有引号时会把首尾两个字节当成引号丢掉，导致结果错乱——`bQM` 必须严格匹配上游写文件时的转义策略。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `> 0` | 写入目标变量的字节数（成功） |
| `0` | 输入长度为 0 / 目标容量不足 / 类型不匹配 / 字段解析失败 |

## 5. 使用注意 / 常见坑

- **目标容量必须够**：`T_Arg.nLen` 小于待写入字段长度时返回 0；不要预设"应该够"。
- **`bQM` 与 writer 端要对齐**：写文件时是 `STRING_TO_CSVFIELD(s, TRUE)`，读时也要 `bQM = TRUE`；二者错配会导致首尾 1 字节被吃掉或多 1 个引号残留。
- **可处理二进制字段**：这是相对 `CSVFIELD_TO_STRING` 的关键差别——字段里允许出现 `16#00`，因为按 `cbInput` 计长，不是 C 字符串。
- **`T_Arg` 必须用 `F_xxx` 辅助函数构造**：直接手动填 `T_Arg` 字段容易类型 enum 写错；用 `F_INT(myVar)` 等更安全（工程经验补充）。
- **配合 `FB_CSVMemBufferReader`**：单字段读取后游标推进、再读下一字段，本函数返回值是推进步长。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CSVFIELD_TO_ARG.xml`](../examples/P_Demo_CSVFIELD_TO_ARG.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CSVFIELD_TO_ARG
VAR
    sCsvField    : STRING := '"42"';     // 模拟从 CSV 内存 buffer 里截出的一段
    nParsedValue : INT;                   // 解析目标变量
    nBytesWritten: UDINT;
END_VAR

// 字段是 "42"（带外层引号），所以 bQM = TRUE 剥去引号后按 INT 解析
nBytesWritten := CSVFIELD_TO_ARG(
    pInput  := ADR(sCsvField),
    cbInput := LEN(sCsvField),
    bQM     := TRUE,
    out     := F_INT(nParsedValue));
```

## 7. 业务场景与实际价值

- **场景**：MES 把生产参数写成 CSV 下发到 PLC，PLC 端读取并把每个字段写入对应结构体成员（温度、压力、扭矩等数值字段；产品 ID 等字符串字段；二进制时间戳字段）。
- **价值**：单一函数同时支持文本字段和二进制字段，统一处理 CSV 转义；不必手写 split + 类型转换两步流水。
- **替代方案对比**：
  - `CSVFIELD_TO_STRING` + 手写 `STRING_TO_INT`：要分支类型，遇到二进制字段（含 `00`）会截断
  - 自己写 split：要处理双引号转义、嵌套字符串，复杂且易错
  - 本函数：一次调用完成 split + 转义 + 类型转换三件事

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.20 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/18014398544558091.html
- **相关函数 / FB**：`ARG_TO_CSVFIELD`（反向，将变量序列化为 CSV 字段）、`CSVFIELD_TO_STRING`（纯文本字段读取）、`FB_CSVMemBufferReader`（CSV 内存缓冲读取器）、`T_Arg`（变量描述结构体）、`F_INT` / `F_REAL` / `F_STRING` 等 `T_Arg` 构造辅助函数
