# F_SplitPathName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31007755.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SplitPathName.xml`](../examples/P_Demo_F_SplitPathName.xml) |

---

## 1. 功能简述

F_SplitPathName 把一个完整路径字符串（如 `'C:\BC\INCLUDE\file.txt'`）拆成 4 个分量：盘符 / 目录 / 文件名 / 扩展名，输出到 4 个 `VAR_IN_OUT` 字符串。返回 `BOOL`：`TRUE` 成功，`FALSE` 失败（路径格式不合法）。适用于配方 / 日志路径预处理：根据扩展名分发、根据目录归类。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sPathName : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sPathName` | `T_MaxString` | 完整路径字符串，格式 `'X:\DIR\SUBDIR\FILENAME.EXT'`。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sDrive : STRING(3);
    sDir : T_MaxString;
    sFileName : T_MaxString;
    sExt : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sDrive` | `STRING(3)` | **输出**：盘符（如 `'C:'`），3 字符。 |
| `sDir` | `T_MaxString` | **输出**：目录路径（如 `'\BC\INCLUDE\'`），含前后反斜杠。 |
| `sFileName` | `T_MaxString` | **输出**：文件名主体（不含扩展名）。 |
| `sExt` | `T_MaxString` | **输出**：扩展名（如 `'.txt'`），含点号。 |

## 3. 行为说明

**输出 4 个分量**：

- `sDrive`：盘符 + 冒号（如 `'C:'`），3 字符 STRING；
- `sDir`：目录路径，**含**前导和尾随反斜杠（如 `'\BC\INCLUDE\'`），`T_MaxString`；
- `sFileName`：文件名主体（不含扩展名），`T_MaxString`；
- `sExt`：扩展名**含**点号（如 `'.txt'`），`T_MaxString`。

**返回值**：`TRUE` = 拆分成功；`FALSE` = 路径格式错（缺少盘符或非法字符）。

**调用方负责分配输出字符串**：4 个 `VAR_IN_OUT` 都由调用方提供本地变量，FB 把结果写进去。`sDrive` 必须分配 `STRING(3)` 容量，其他 3 个 `T_MaxString`（约 255 字节）。

**调用例子**：完整路径 `'C:\\BC\\INCLUDE\\file.txt'` 拆分后 `sDrive = 'C:'`、`sDir = '\\BC\\INCLUDE\\'`、`sFileName = 'file'`、`sExt = '.txt'`。

**纯字符串处理**：本函数同步函数，立即返回；不做文件系统访问，路径不存在或无效路径不报错，只检查格式。

## 4. 错误码 / 返回值

本函数返回 `BOOL`：

| 返回值 | 含义 |
|---|---|
| `TRUE` | 调用成功 |
| `FALSE` | 调用失败（参数错误或硬件故障） |

## 5. 使用注意 / 常见坑

- **`sDir` 含尾随 `\`**：拼新路径时不要重复加 `\`，否则得到 `'C:\dir\\file.txt'` 双斜杠。
- **`sExt` 含点号**：业务比较扩展名要用 `'.csv'` 而不是 `'csv'`。
- **Linux 风格 `/` 路径**：PDF 没明确，实测 Windows 上 `/` 也能被识别为分隔符，但建议统一用 `\`。（工程经验补充）
- **`VAR_IN_OUT` 必须先分配本地变量**：不能传匿名表达式。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitPathName.xml`](../examples/P_Demo_F_SplitPathName.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：读到一份新的工艺文件路径 `'D:\Recipes\Apr\BatchA.csv'`，根据 `sExt = '.csv'` 走 CSV 解析分支，根据 `sDir` 把文件名记录到对应月份归档表。
- **价值**：替代手写 `RIGHT` / `FIND` / `MID` 4 段：一行得到 4 分量。
- **替代方案对比**：
  - 手写字符串扫描：约 15-20 行。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31007755.html
- **相关 FB / FC**：`FB_FileOpen`
