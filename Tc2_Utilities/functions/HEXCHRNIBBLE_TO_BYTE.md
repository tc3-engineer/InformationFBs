# HEXCHRNIBBLE_TO_BYTE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934088715.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml) |

---

## 1. 功能简述

`HEXASCNIBBLE_TO_BYTE` 的字符版本——输入 `STRING(1)` 而非 BYTE ASCII 码；返回 0..15 或 255 表错。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    chr : STRING(1);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `chr` | `STRING(1)` | — | hex 字符（`'0'..'9'` / `'a'..'f'` / `'A'..'F'`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BYTE` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法语义与 `HEXASCNIBBLE_TO_BYTE` 相同——`'0'..'9'` → 0..9、`'A'..'F'` / `'a'..'f'` → 10..15、其他 → 255 表错——区别在于输入类型 `STRING(1)`（单字符 STRING）而不是 BYTE ASCII 码。**适合直接传字符常量或单字符变量**——`HEXCHRNIBBLE_TO_BYTE('A')` 比 `HEXASCNIBBLE_TO_BYTE(16#41)` 可读得多。内部实现可能直接取 `STRING(1)` 的首字节再转 BYTE 调用 ASCII 版本，性能差异可忽略。**返回 255 是错误标识**——0..15 合法，调用方判 `result <= 15` 区分。

## 4. 错误码 / 返回值

返回 `BYTE`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **返回 255 表错**——0..15 合法。
- **大小写都接受**。
- **`HEXASCNIBBLE_TO_BYTE` 接受 BYTE**——串口收到的 ASCII 字节直接用 ASC 版本省一次转换。
- **`STRING(1)` = 1 字符 + null 终结**（2 字节）—— 多字符串只看第一个字符。
- **典型组合**：把 hex 字符串的每两个字符拼成 BYTE：`b := SHL(HEXCHRNIBBLE_TO_BYTE(s[0]), 4) OR HEXCHRNIBBLE_TO_BYTE(s[1]);`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：手工解码 hex 配置串（如 `'AB'` → 0xAB 字节）；小量数据场景，避免引入 `HEXSTR_TO_DATA` 的完整 API。
- **价值**：比 `HEXASCNIBBLE_TO_BYTE` 直观——字符常量直接传。
- **替代方案对比**：`HEXASCNIBBLE_TO_BYTE`：BYTE 输入；`HEXSTR_TO_DATA`：整串版本（推荐大数据）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.48 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934088715.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
