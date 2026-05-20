# HEXASCNIBBLE_TO_BYTE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934086795.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml) |

---

## 1. 功能简述

把 hex 字符的 ASCII 码（如 0x41 即字符 `'A'`）转为 0-15 的十进制 nibble 值；非法字符返回 255 表错误。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    asc : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `asc` | `BYTE` | — | hex 字符的 ASCII 码：`'0'..'9'`（0x30~0x39）、`'a'..'f'`（0x61~0x66）、`'A'..'F'`（0x41~0x46）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BYTE` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BYTE` | 0..15 为成功值；`255` 为错误码（输入超出 hex 字符范围）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：`'0'..'9'` (0x30..0x39) → 0..9；`'A'..'F'` (0x41..0x46) → 10..15；`'a'..'f'` (0x61..0x66) → 10..15；其他任何字节 → 255 表错。**返回值 0..15 是合法 nibble；255 是错误码**（255 不能误判为合法 nibble 因为合法范围 0-15）。本函数适合**输入是 ASCII 码字节**的场景，例如从串口收到的 hex 字符流的逐字节解码。对应字符版（`STRING(1)` 输入）的姐妹函数是 `HEXCHRNIBBLE_TO_BYTE`。

## 4. 错误码 / 返回值

返回 `BYTE`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **返回 255 表错**——0..15 合法、其它都是错。`IF F_NbReturned <= 15 THEN ... ELSE error END_IF;`
- **大小写都接受**（`'a'` 和 `'A'` 都给 10）。
- **输入是 ASCII 码（BYTE）**——传字符变量本身需 `BYTE(sChar[0])` 转换。
- **`HEXCHRNIBBLE_TO_BYTE` 接受 `STRING(1)`**——直接传字符常量 `'A'` 更方便。
- **Nibble = 半字节**（4 位）；2 个 nibble 组成 1 字节。
- **典型组合**：高 nibble + 低 nibble → 一个完整 BYTE：`b := SHL(F_NbReturned1, 4) OR F_NbReturned2;`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXASCNIBBLE_TO_BYTE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：串口收 hex 字符流：每个字节是一个 hex 字符的 ASCII 码；逐字节调用本函数得到 nibble，每两个拼成 1 BYTE。
- **价值**：替代手写 ASCII → nibble 映射（条件分支或查找表）；本函数 1 调用。
- **替代方案对比**：`HEXCHRNIBBLE_TO_BYTE`：STRING(1) 输入版本；`HEXSTR_TO_DATA`：整串版本（推荐用于大数据）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.47 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934086795.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
