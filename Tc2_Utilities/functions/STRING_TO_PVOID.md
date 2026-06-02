# STRING_TO_PVOID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35105291.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_PVOID.TcPOU`](../examples/P_Demo_STRING_TO_PVOID.TcPOU) |

---

## 1. 功能简述

`PVOID_TO_STRING` 的反向——把 IEC 61131-3 风格的数字字符串（hex / oct / bin / dec）解析为指针值；非法字符返 0。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `STRING` | — | 要解析的字符串——支持 `'16#XXXX'`（hex）、`'8#XXX'`（八进制）、`'2#XXXX'`（二进制）、`'XXX'`（十进制）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `PVOID` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：检测字符串前缀决定进制——`'16#'` 前缀表示 hex、`'8#'` 表示八进制、`'2#'` 表示二进制、无前缀则默认 dec；按相应进制把后续数字字符解析为整数，再转为 PVOID 类型返回。例如 `STRING_TO_PVOID('16#80001000')` 与 `STRING_TO_PVOID('8#20000010000')` 与 `STRING_TO_PVOID('2147487744')` 三种写法得到同一指针值（10 进制 = 2147487744 = 0x80001000）。**非法字符（含 hex 串里出现非 0-9A-F、八进制串里出现 8/9、空串、未知前缀等）返回 0**——业务侧用 `pResult <> 0` 判合法，但 0 也可能是合法的空指针，**需结合调用场景判断**。

## 4. 错误码 / 返回值

返回 `PVOID`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **非法字符返 0**——与合法的 NULL 指针不可区分。
- **前缀决定进制**——`'16#FF'` = 255、`'8#377'` = 255、`'2#11111111'` = 255、`'255'` = 255；混用进制要小心。
- **位宽随平台**——32 位平台最大可表示 `2^32 - 1`；超大数字在 32 位平台会被截断。
- **主要用于反序列化诊断输出**——业务逻辑不要把指针存为字符串再回灌（地址不稳定）。
- **`STRING(255)`** 上限——非常长的二进制字符串可能超长。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_PVOID.TcPOU`](../examples/P_Demo_STRING_TO_PVOID.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从配置文件读出 `'16#80000000'` 格式的内存基址字符串 → 转 PVOID 作为某硬件寄存器映射地址。
- **价值**：替代手写多进制解析；本函数自动按前缀适应。
- **替代方案对比**：`PVOID_TO_STRING`：反向；`STRING_TO_DWORD`：仅十进制。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.68 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35105291.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
