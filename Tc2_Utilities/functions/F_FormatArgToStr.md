# F_FormatArgToStr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35116043.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_FormatArgToStr.xml`](../examples/P_Demo_F_FormatArgToStr.xml) |

---

## 1. 功能简述

**格式化辅助函数**——`FB_FormatString` 内部使用。把 `T_Arg`（含值 + 类型）按 printf 风格格式说明转换为字符串；返回写入字节数。**通常不直接调用**；用 `FB_FormatString` / `FB_FormatString2`。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bSign : BOOL;
    bBlank : BOOL;
    bNull : BOOL;
    bHash : BOOL;
    bLAlign : BOOL;
    bWidth : BOOL;
    iWidth : INT;
    iPrecision : INT;
    eFmtType : E_TypeFieldParam;
    arg : T_Arg;
END_VAR
VAR_IN_OUT
    sOut : T_MaxString;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bSign` | `BOOL` | — | 符号前缀标志（`%+d` 风格）。 |
| `bBlank` | `BOOL` | — | 空格前缀标志（`% d` 风格）。 |
| `bNull` | `BOOL` | — | 零填充前缀标志（`%0d` 风格）。 |
| `bHash` | `BOOL` | — | `#` 前缀标志（如 `%#x` 在 hex 前加 `0x`）。 |
| `bLAlign` | `BOOL` | — | 对齐：`FALSE` = 右对齐（默认）、`TRUE` = 左对齐。 |
| `bWidth` | `BOOL` | — | `TRUE` 时 `iWidth` 生效（启用宽度填充）；`FALSE` 不填充。 |
| `iWidth` | `INT` | — | 宽度字符数。 |
| `iPrecision` | `INT` | — | 精度（浮点小数位数 / 字符串截断长度等）。 |
| `eFmtType` | `E_TypeFieldParam` | — | 格式类型（`d` / `x` / `f` / `s` 等的枚举形式）。 |
| `arg` | `T_Arg` | — | 要格式化的 PLC 变量（通过 `F_INT` / `F_LREAL` / `F_STRING` 等辅助函数打包）。 |

### VAR_IN_OUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `sOut` | `T_MaxString` | 格式化结果输出 STRING（VAR_IN_OUT，函数写入并返回字节数）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出，部分参数同时被 VAR_IN_OUT 修改）。

## 3. 行为说明

函数无状态、立即返回。算法：根据 `eFmtType`（格式类型 `d`/`u`/`x`/`X`/`o`/`b`/`f`/`e`/`s` 等）和各个标志位（`bSign`/`bBlank`/`bNull`/`bHash`/`bLAlign`），把 `arg` 中的值格式化为字符串：整数 → 十/十六/八/二进制串；浮点 → 定点 / 科学；字符串 → 截断 / 填充。`iWidth` 控制总宽度（左/右对齐 + 填充字符）；`iPrecision` 控制精度（浮点小数位、字符串最大字节）。**返回写入字节数**（不含 null 终结符）。这是底层格式化引擎；业务侧用 `FB_FormatString` 包装的 `%d` / `%s` / `%f` 等 printf 风格调用更方便。

## 4. 错误码 / 返回值

返回 `UDINT`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **通常不直接调用**——用 `FB_FormatString` / `FB_FormatString2`，后者解析 printf-style 格式串后自动调用本函数。
- 11 个参数全要传——零繁琐；本函数适合写**自定义格式化 FB**（如本地化数字显示）。
- **`arg : T_Arg` 必须通过 `F_<TYPE>` 辅助函数构造**——直接传 PLC 变量编译失败。
- `E_TypeFieldParam` 枚举值见 PDF；与 printf 的 `d/u/x/o/f/e/s` 对应。
- `bWidth = FALSE` 时 `iWidth` 被忽略——确保两者一致。
- **输出 STRING 缓冲**：函数内部用全局 buffer，需调用方立即拷贝（PDF 未明示线程安全，⚠️ 建议在同一周期内取走结果）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_FormatArgToStr.xml`](../examples/P_Demo_F_FormatArgToStr.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：自定义可本地化数字显示 FB：根据语言环境调整小数点 / 千分位字符，调用底层 `F_FormatArgToStr` 而不是裸字符串拼接。
- **价值**：**只在自定义格式化器内部用**——`FB_FormatString` 已经包装好 printf-style，业务侧 99% 场景不用裸调本函数。
- **替代方案对比**：`FB_FormatString` / `FB_FormatString2`：printf 风格包装器（首选）；手写整数 → 字符串：`INT_TO_STRING` 等基本函数。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.35 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35116043.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
