# GUID_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35275147.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_GUID_TO_STRING.xml`](../examples/P_Demo_GUID_TO_STRING.xml) |

---

## 1. 功能简述

把 GUID 结构转为**无**大括号的字符串 `'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'`（36 字符）。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stIn : GUID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `stIn` | `GUID` | — | 源 GUID 结构。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法与 `GUID_TO_REGSTRING` 相同——把 16 字节 GUID 按 `8-4-4-4-12` 段式 hex 格式化——但**不加大括号**；输出 36 字符。第一段按 little-endian、后续段按 big-endian 字节序（Microsoft GUID 历史规范）。OPC UA Application URI、数据库主键、文件名等场景多用无大括号格式；Windows 注册表 / COM API 用带大括号的 `GUID_TO_REGSTRING`。**本函数无错误返回**——任意输入都格式化合法；全零 GUID 输出 `'00000000-0000-0000-0000-000000000000'`。

## 4. 错误码 / 返回值

返回 `STRING`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **与 `GUID_TO_REGSTRING` 区别**：本函数**不**含大括号。
- **返回类型 `STRING`**（实际 36 字节内容 + null）；不是 `STRING(36)`——但实际占用相当。
- **反向函数 `STRING_TO_GUID`**：把 36 字符串解析回 GUID。
- **全零 GUID** 输出合法 36 字符串——业务侧不能仅用 `LEN > 0` 判有效。
- 字符大写。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GUID_TO_STRING.xml`](../examples/P_Demo_GUID_TO_STRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OPC UA Application URI 写入数据库——数据库习惯无大括号 UUID；本函数直接输出可入库格式。
- **价值**：替代手写 16 字节 → hex + 连字符拼接。
- **替代方案对比**：`GUID_TO_REGSTRING`：带大括号版本；`STRING_TO_GUID`：反向。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.45 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35275147.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
