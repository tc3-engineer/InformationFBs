# SETBIT32

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31012363.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_SETBIT32.xml`](../examples/P_Demo_SETBIT32.xml) |

---

## 1. 功能简述

SETBIT32 把 32 位输入值 `inVal32` 中指定位号 `bitNo` 设为 1，返回修改后的值；原值不被改写。`bitNo` 范围 0-31，**超出范围会内部 modulo 32**（如 `bitNo = 32` 实际作用于 bit 0）。适用于位掩码 / 状态字 / 标志组合的纯函数式拼装。

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
| `inVal32` | `DWORD` | 要操作的 32 位值。 |
| `bitNo` | `SINT` | 位号 0-31。超出自动 mod 32。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法**：返回值 = `inVal32 OR (1 SHL (bitNo MOD 32))`。

**modulo 行为**：`bitNo` 超过 31 时自动 mod 32，PDF 明确指出。但依赖此行为容易出 bug，建议调用方自己保证范围。

**纯函数**：不修改 `inVal32`；要更新原变量需 `myVar := SETBIT32(myVar, 5)`。

**与 IEC `BIT_OPERATIONS`**：本函数等价于 `inVal32 OR SHL(DWORD#1, bitNo)`，但更直观、可读性更好。

**示例**：`SETBIT32(16#00000000, 31) = 16#80000000`（PDF 原文示例）。

**典型应用场景**：组合多个 BOOL 状态到 DWORD 状态字给 HMI 一次读取、组装 EtherCAT 控制字、维护错误码位标志等。语义比直接位掩码运算清晰，新手代码可读性大幅提升。

## 4. 错误码 / 返回值

本函数返回 `DWORD`：把 `bitNo` 位置 1 后的新值（原值不变）。

## 5. 使用注意 / 常见坑

- **modulo 32 隐藏 bug**：`bitNo = 33` 实际改 bit 1，可能掩盖上层逻辑的越界错误。建议自己用 `IF bitNo &gt; 31 THEN ... ; END_IF;` 显式校验。
- **`bitNo` 是 `SINT`**：负数行为未定义（实测仍 mod 32 但要看二进制补码）。（工程经验补充）
- **返回值不写回原变量**：忘记 `:= SETBIT32(...)` 是常见错误，结果原变量没变。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SETBIT32.xml`](../examples/P_Demo_SETBIT32.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：拼装设备状态字：根据多个布尔状态依次置位组成一个 32 位状态字写到 HMI，比 `dwStatus := dwStatus OR 16#02` 这种魔法数字可读性强得多。
- **价值**：可读性比 OR + 移位强；避免魔法数字。
- **替代方案对比**：
  - `dwVal OR SHL(1, bitNo)`：等价但难读。
  - 自己写 `IF/ELSE` 分支：冗长。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31012363.html
- **相关 FB / FC**：`CSETBIT32`, `CLEARBIT32`, `GETBIT32`
