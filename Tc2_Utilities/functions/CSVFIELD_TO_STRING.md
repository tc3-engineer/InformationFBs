# CSVFIELD_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35078155.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_CSVFIELD_TO_STRING.xml`](../examples/P_Demo_CSVFIELD_TO_STRING.xml) |

---

## 1. 功能简述

`CSVFIELD_TO_ARG` 的 STRING-only 版本——把 CSV 字段（STRING 输入）解析为目标 STRING（去引号、解转义）。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : T_MaxString;
    bQM : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_MaxString` | — | 源 CSV 字段（STRING 形式）。 |
| `bQM` | `BOOL` | — | `TRUE` = 剥除外围双引号；`FALSE` = 源无引号。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态。算法：把源 STRING 中的双引号 `""`（CSV 转义）替换为单 `"`；`bQM = TRUE` 时再剥除最外围一对引号。失败返回空串——但当源本身就是空串时也返回空串，二者无法区分。**源不能含二进制 0x00**（STRING null 终结会截断）；二进制 CSV 字段必须用 `CSVFIELD_TO_ARG`。通常配套 `FB_CSVMemBufferReader` 使用。

## 4. 错误码 / 返回值

返回 `T_MaxString`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **返回空串可能是成功（源为空）也可能是失败**——调用方须先判源长。
- 源不能含 0x00 二进制——会被 null 截断；二进制场景用 `CSVFIELD_TO_ARG`。
- `bQM` 与生产端一致。
- **反向函数 `STRING_TO_CSVFIELD`**：STRING → CSV 字段。
- **双引号转义规则**：CSV 中 `"a""b"` 解析得 `a"b`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CSVFIELD_TO_STRING.xml`](../examples/P_Demo_CSVFIELD_TO_STRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：读 CSV 文本配置：纯字符串字段（设备名、操作员名）的逐字段提取。
- **价值**：替代手写 `STRTOK` + 引号处理；本函数 1 行带 CSV 规范遵守。
- **替代方案对比**：`CSVFIELD_TO_ARG`：二进制版本；`STRING_TO_CSVFIELD`：反向。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.21 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35078155.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
