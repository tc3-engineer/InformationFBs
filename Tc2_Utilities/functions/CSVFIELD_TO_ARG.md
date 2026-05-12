# CSVFIELD_TO_ARG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35076107.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_CSVFIELD_TO_ARG.xml`](../examples/P_Demo_CSVFIELD_TO_ARG.xml) |

---

## 1. 功能简述

把 CSV 字段（字节缓冲）解析为指定 PLC 变量；返回转换字节数。支持二进制 CSV 字段（比 `CSVFIELD_TO_STRING` 更通用）。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pInput : POINTER TO BYTE;
    cbInput : UDINT;
    bQM : BOOL;
    out : T_Arg;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pInput` | `POINTER TO BYTE` | — | 源 CSV 数据字段（字节缓冲）起始地址；`ADR(buf)`。 |
| `cbInput` | `UDINT` | — | 源数据长度（字节，`SIZEOF`）。 |
| `bQM` | `BOOL` | — | `TRUE` = 源外围有双引号需剥除（CSV 严格模式）；`FALSE` = 源无引号。 |
| `out` | `T_Arg` | — | 目标 PLC 变量描述符（`T_Arg`）—— 用 `F_BYTE(b)` / `F_INT(n)` / `F_STRING(s)` 等辅助函数构造。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：扫描源 CSV 字段（可能带 `"` 引号），剥除引号后按 `out` 对应的 `T_Arg` 类型解析——例如 `out` 描述 BYTE 时解析数字串为 BYTE；描述 STRING 时直接复制并把双引号 `""` 解为单引号 `"`（CSV 转义规则）。`bQM = TRUE` 时剥除最外围引号；`= FALSE` 时假设源无引号。**成功返回**转换字节数；**失败或源长 = 0** 返回 0。**通常与 `FB_CSVMemBufferReader` 搭配**——后者把 CSV 文件按行/字段切到内存，再用本函数逐字段解析为 PLC 变量。配套例子见 PDF 4.20 / InfoSys 35076107。`out` 通过 `F_<TYPE>` 辅助函数构造 `T_Arg`，使本函数能解析任何基本类型。

## 4. 错误码 / 返回值

返回 `UDINT`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **返回 0 表示失败**——不要把 0 字节当成功；调用方判 `nLen > 0`。
- **通常与 `FB_CSVMemBufferReader` 搭配**：单独调用需要业务侧自己切字段（按 `,` / `;`）。
- `out` 是 `T_Arg`——必须先用 `F_BYTE` / `F_INT` / `F_LREAL` / `F_STRING` 等打包目标变量；不能直接传 PLC 变量本身。
- **`bQM` 必须与生产端的设置匹配**——否则解析后多/少一对引号。
- **`pInput` 字节缓冲必须有效——`cbInput` 大于实际数据时函数读越界**（PDF 未明确边界检查），建议精确传 `LEN`。
- **CSV 双引号转义**：源 `"a""b"` 解析为 STRING 时得 `'a"b'`。
- **`CSVFIELD_TO_STRING` 是仅 STRING 版本**——只解析 STRING 类型字段；本函数解析任意 `T_Arg`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CSVFIELD_TO_ARG.xml`](../examples/P_Demo_CSVFIELD_TO_ARG.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：读 CSV 配方文件：每行 `name, batch_id, recipe_id, target_temp` 四字段；用本函数把 batch_id (UDINT)、target_temp (LREAL) 等二进制字段直接解析进 PLC 变量。
- **价值**：替代手写 `STRTOK` + `STRING_TO_INT/LREAL` 链；本函数 1 行解析任意类型 + 自带 CSV 引号 / 转义处理。
- **替代方案对比**：`CSVFIELD_TO_STRING`：仅 STRING；`ARG_TO_CSVFIELD`：反向（PLC → CSV）；`STRING_TO_CSVFIELD`：STRING 反向。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.20 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35076107.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
