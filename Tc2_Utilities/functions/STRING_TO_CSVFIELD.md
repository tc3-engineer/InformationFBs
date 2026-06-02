# STRING_TO_CSVFIELD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35151371.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_CSVFIELD.TcPOU`](../examples/P_Demo_STRING_TO_CSVFIELD.TcPOU) |

---

## 1. 功能简述

把 STRING 转为 CSV 字段格式——单引号 `'` 转为双引号 `""`（CSV 转义），可选加最外围引号。

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
| `in` | `T_MaxString` | — | 源 STRING。 |
| `bQM` | `BOOL` | — | `TRUE` = 给输出加最外围双引号；`FALSE` = 不加。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：从左到右扫描 `in`，把每个单引号 `'` 替换为 CSV 标准转义形式双引号 `""`（连续两个双引号代表内容中含一个双引号）；遇到其他字符直接复制。`bQM = TRUE` 时在结果最外层添加一对包裹双引号（`"..."`），让结果可作为 CSV 单字段直接拼入逗号分隔的行；`bQM = FALSE` 时不加外围引号——适用于源数据已知不含逗号 / 分号 / 引号 / 换行的简单标签场景。**源不能含 0x00 二进制**——STRING null 终结会让函数在 0x00 处停止扫描，导致后续内容丢失；二进制场景必须用 `ARG_TO_CSVFIELD`。结果为空表示转换失败——但当源串本就是空时也返回空，**两者无法区分**，业务侧应先判 `LEN(in) > 0`。

## 4. 错误码 / 返回值

返回 `T_MaxString`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **源不含 0x00 二进制**——二进制走 `ARG_TO_CSVFIELD`。
- **返回空可能是成功（源空）也可能是失败**——业务侧先判源。
- **`bQM` 与消费端一致**——避免引号嵌套出错。
- **反向函数 `CSVFIELD_TO_STRING`**。
- **典型用法**配合 `FB_CSVMemBufferWriter`：组装 CSV 行写入内存缓冲，再写文件。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_CSVFIELD.TcPOU`](../examples/P_Demo_STRING_TO_CSVFIELD.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把 PLC 设备名 / 操作员名等 STRING 字段写入 CSV 报表文件。
- **价值**：替代手写引号转义代码——CSV 规范严格，自写易出 bug。
- **替代方案对比**：`ARG_TO_CSVFIELD`：二进制版本；`CSVFIELD_TO_STRING`：反向。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.66 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35151371.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
