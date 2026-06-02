# GETBIT32

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31015435.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_GETBIT32.TcPOU`](../examples/P_Demo_GETBIT32.TcPOU) |

---

## 1. 功能简述

GETBIT32 读取 32 位值 `inVal32` 中指定位号 `bitNo` 的状态，返回 `BOOL`（`TRUE` = 1，`FALSE` = 0）。原值不变；纯读操作。用于解码状态字 / 标志组合，反向操作是 `SETBIT32` / `CLEARBIT32` / `CSETBIT32`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    inVal32 : DWORD;
    bitNo : SINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `inVal32` | `DWORD` | 要读取的 32 位值。 |
| `bitNo` | `SINT` | 位号 0-31。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法**：返回值 = `(inVal32 AND (1 SHL (bitNo MOD 32))) <> 0`。

**`bitNo` modulo 32**：超出范围自动 mod 32（PDF 明确）。

**示例**：`GETBIT32(16#04, 2) = TRUE`（PDF 原文）。

**与 IEC `BIT_OPERATIONS` 关系**：本函数等价于 `(inVal32 AND SHL(DWORD#1, bitNo)) <> 0`，但更直观。

**典型应用场景**：解码 HMI 命令字（DWORD 各位对应不同命令）、解析 EtherCAT 状态字 Statusword、提取错误码各位标志、检查打包到 DWORD 的多通道 DI 状态等。语义比直接位掩码运算清晰，避免新手把 `AND` 结果误当 BOOL。

**反向操作**：`SETBIT32` / `CLEARBIT32` / `CSETBIT32` 是配套的『写位』函数，本函数是『读位』。

## 4. 错误码 / 返回值

本函数返回 `BOOL`：TRUE = 该位为 1；FALSE = 该位为 0。

## 5. 使用注意 / 常见坑

- **`bitNo` modulo 32 隐藏 bug**：同 SETBIT32。
- **`bitNo` 是 `SINT`**：负数行为未定义。（工程经验补充）
- **返回 BOOL 而不是 INT**：直接当数字算术会编译错。要数字用 `BOOL_TO_INT(GETBIT32(...))`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETBIT32.TcPOU`](../examples/P_Demo_GETBIT32.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：解码 HMI 命令字：读到一个 DWORD 命令字后用 `GETBIT32` 提取每位含义（bit0 = 启动、bit1 = 停止、bit2 = 复位 等）。
- **价值**：替代 AND + 移位 + 非零比较；可读性强。
- **替代方案对比**：
  - `(dwVal AND SHL(1, bitNo)) <> 0`：等价但难读。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.16
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31015435.html
- **相关 FB / FC**：`SETBIT32`, `CLEARBIT32`, `CSETBIT32`
