# CSVFIELD_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35074571.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_CSVFIELD_TO_STRING.xml`](../examples/P_Demo_CSVFIELD_TO_STRING.xml) |

---

## 1. 功能简述

把 CSV 字段（以 `T_MaxString` 形式传入的源串）反序列化为 PLC 字符串值。字段内连续两个双引号被还原为单个双引号；若 `bQM = TRUE`，则去掉源串外层包裹的双引号。

成功时返回去转义后的字符串；源串为空串时返回空串；源串非空但解析失败时也返回空串。源串不得含二进制 0 字节（`$00`），否则会被当作 C 字符串终止符提前截断——需要处理二进制字段时改用 `CSVFIELD_TO_ARG`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in  : T_MaxString;
    bQM : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_MaxString` | — | 待解析的 CSV 字段源串（`STRING(255)`）。 |
| `bQM` | `BOOL` | — | 引号模式：`TRUE` = 源串外层是双引号、需剥去；`FALSE` = 源串没有外层引号。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 去转义后的字符串。`'"A""""B"'`（`bQM=TRUE`）→ `'A""B'`；`'A""""B'`（`bQM=FALSE`）→ `'A""B'`。 |

### VAR_OUTPUT

无。

## 3. 行为说明

按 CSV 字段转义规则处理 `in` 字符串：

1. **bQM = TRUE 时剥去外层引号**：去掉首尾各一个 `"` 字节；剥完后才是真正的数据。
2. **CSV 转义还原**：字段中每两个连续 `"` 还原为一个 `"`（CSV 标准用 `""` 表示数据里的一个引号）。
3. **特殊字符保留**：`$R$N`（回车换行的 IEC 转义）等控制字符不会被解释，直接搬到结果串中。
4. **失败返回空串**：源串非空但格式有问题（外层引号不闭合等）则返回 `''`；源串本就是空串也返回 `''`，调用方无法区分二者。

PDF 列出的典型转换表（`bQM=TRUE`）：
- `'"Module_XA5"'` → `'Module_XA5'`
- `'""'` → `''`
- `'"A""""B"'` → `'A""B'`
- `'"AB$00CD"'` → `'AB'`（被 `$00` 截断！）

写文件用 `STRING_TO_CSVFIELD`，读时与之对称：写入用 `bQM=TRUE`，读取也必须 `bQM=TRUE`。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| 非空字符串 | 解析成功，已去转义 |
| 空字符串 `''` | 源串为空 / 解析失败（如外层引号不匹配） |

## 5. 使用注意 / 常见坑

- **遇 `$00` 会被截断**：源串若含二进制 0 字节，剩余字段被丢弃。处理二进制字段必须改用 `CSVFIELD_TO_ARG`。
- **空串与失败无法区分**：返回值都是 `''`；如需区分，先用 `LEN(sRaw) = 0` 判断源串是否原本就空。
- **`bQM` 必须与 writer 端一致**：错配会导致首末 1 字节被吃掉或多 1 引号残留。
- **不可换行 / 不可二进制**：CSV 字段含未转义换行 / 二进制时 PDF 标注 "No"（不符合 CSV），转换结果不可预期。
- **与 `STRING_TO_CSVFIELD` 是一对反函数**：先 `STRING_TO_CSVFIELD(s, TRUE)`，再 `CSVFIELD_TO_STRING(result, TRUE)` 应得回原串（不含 `$00` 时）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CSVFIELD_TO_STRING.xml`](../examples/P_Demo_CSVFIELD_TO_STRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CSVFIELD_TO_STRING
VAR
    sCsvField : STRING := '"ab_$04_$05_cd-""ALFA""_5"';   // 带外层引号 + CSV 转义
    sDecoded  : STRING;                                    // 去转义后的实际字符串
END_VAR

sDecoded := CSVFIELD_TO_STRING(sCsvField, TRUE);
// 结果 sDecoded = 'ab_$04_$05_cd-"ALFA"_5'
```

## 7. 业务场景与实际价值

- **场景**：读 MES 下发的 CSV 配方表中的"产品名称"列，名称里可能含双引号（如 `"60""TV"`）需要还原成 `60"TV`。
- **价值**：自动处理 CSV 转义规则（`""` → `"`），不必手写状态机扫描；与 `STRING_TO_CSVFIELD` 配对保证写入读取对称。
- **替代方案对比**：
  - 手写 `REPLACE` 链：要小心嵌套引号，易在 `""""` 这类边界出错
  - `CSVFIELD_TO_ARG` + `F_STRING`：行也可以，但 `CSVFIELD_TO_STRING` 返回类型更直观
  - 本函数：单调用、专为字符串字段优化

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.21 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35074571.html
- **相关函数 / FB**：`STRING_TO_CSVFIELD`（反向）、`CSVFIELD_TO_ARG`（支持二进制字段）、`FB_CSVMemBufferReader`
