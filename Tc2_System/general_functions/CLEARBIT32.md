# CLEARBIT32

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31016971.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_CLEARBIT32.TcPOU`](../examples/P_Demo_CLEARBIT32.TcPOU) |

---

## 1. 功能简述

CLEARBIT32 把 32 位值 `inVal32` 中指定位号 `bitNo` 清零，返回新值；原值不变。与 `SETBIT32` 完全对称（一个置 1、一个置 0），共同构成位操作工具集。

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
| `bitNo` | `SINT` | 位号 0-31。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法**：返回值 = `inVal32 AND NOT (1 SHL (bitNo MOD 32))`。

**`bitNo` modulo 32**：同 SETBIT32。

**纯函数**：要更新原变量需 `myVar := CLEARBIT32(myVar, 5)`。

**示例**：`CLEARBIT32(16#C0000000, 31) = 16#40000000`（PDF 原文）。

**典型用法**：复位错误标志、清理状态字的某些位、在状态机切换分支前清掉前一个分支留下的位标志。

**与 `SETBIT32` 对称**：两个函数共同构成位操作工具集；`CSETBIT32` 是『二合一』变体。三者搭配可以替代所有 `OR` / `AND NOT` 位运算的常见场景，让代码可读性大幅提升。

**性能**：底层是单条 CPU 位指令，几乎无开销，可以放心在 PLC 主循环里高频调用。

## 4. 错误码 / 返回值

本函数返回 `DWORD`：把 `bitNo` 位清零后的新值。

## 5. 使用注意 / 常见坑

- **`bitNo` modulo 32**：同 SETBIT32。
- **返回值不写回原变量**：与 SETBIT32 同坑。
- **`bitNo` 是 `SINT`**：负数未定义。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CLEARBIT32.TcPOU`](../examples/P_Demo_CLEARBIT32.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：错误恢复时清掉状态字中所有错误位，保留运行状态位；用 CLEARBIT32 比 NOT + AND 直观。
- **价值**：可读性比 AND + NOT 强。
- **替代方案对比**：
  - `dwVal AND NOT SHL(1, bitNo)`：等价但难读。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31016971.html
- **相关 FB / FC**：`SETBIT32`, `CSETBIT32`, `GETBIT32`
