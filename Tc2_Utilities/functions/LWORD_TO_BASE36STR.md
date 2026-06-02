# LWORD_TO_BASE36STR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10943539851.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LWORD_TO_BASE36STR.TcPOU`](../examples/P_Demo_LWORD_TO_BASE36STR.TcPOU) |

---

## 1. 功能简述

把 LWORD 转为 Base36 字符串——使用 `0-9 A-Z` 共 36 个字符表示，相比 hex 更紧凑（典型 8 字节 LWORD → 13 字符 Base36）。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : LWORD;
    iPrecision : INT;
    bLoCase : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `LWORD` | — | 要转换的十进制数（无符号 64 位）。 |
| `iPrecision` | `INT` | — | 最小输出位数；不足时左填 `'0'`。 |
| `bLoCase` | `BOOL` | — | `TRUE` = 小写 `abcdef`；`FALSE` = 大写 `ABCDEFXY`。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：把 `in`（LWORD）反复对 36 取模获得各位数字，从低位到高位反向写入字符——模 0..9 用 `'0'..'9'`、模 10..35 用 `'A'..'Z'`（或 `'a'..'z'` 当 `bLoCase = TRUE`）；最后翻转字符串使高位在前。`iPrecision` 控制最小输出位数：实际位数不足时**左填 `'0'`** 直到达到 `iPrecision`；实际位数超过 `iPrecision` 时**不截断**——保留全部有效位以避免值丢失。**典型紧凑性**：64 位 LWORD 最大值 `2^64 - 1` 用 Base36 表示需 13 字符（比 hex 16 字符短 19%、比 dec 20 字符短 35%）。**边界**：`iPrecision = 0` 且 `in = 0` → 返回空串；`iPrecision > 0` 且 `in = 0` → 返回 `iPrecision` 个 `'0'`。

## 4. 错误码 / 返回值

返回 `T_MaxString`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **Base36 = 0-9 + A-Z**，比 Hex 紧凑——但可读性更差（含字母 O 与数字 0 视觉相近）。
- **`iPrecision = 0` 且 in = 0** → 空串。其他情况至少 1 字符。
- **`bLoCase`** 默认大写（`FALSE`）；小写场景类似 URL slug。
- **最大 13 字符** 表示 LWORD（2^64 < 36^13）；T_MaxString = STRING(255) 充裕。
- **反向函数 `BASE36STR_TO_LWORD` 不存在**——业务侧自写循环 × 36 + 字符查表实现。
- **与 hex 的选择**：调试用 hex（半字节对齐易读）；存储 / 传输用 Base36（更紧凑）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LWORD_TO_BASE36STR.TcPOU`](../examples/P_Demo_LWORD_TO_BASE36STR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：生产订单号编码：当前序号 `nBatchSeq : LWORD` → 5 字符 Base36 字符串作为工单 ID 打印到标签。
- **价值**：比 hex 字符串紧凑 38%；比 Base64 字符集简单（无 `+ /` 等特殊字符）。
- **替代方案对比**：`LWORD_TO_HEXSTR`：hex 版本；自写 → 大字符集（如 Base62）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.52 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10943539851.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
