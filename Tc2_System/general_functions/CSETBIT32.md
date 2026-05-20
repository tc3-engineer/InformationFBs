# CSETBIT32

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31013899.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_CSETBIT32.xml`](../examples/P_Demo_CSETBIT32.xml) |

---

## 1. 功能简述

CSETBIT32 是 `SETBIT32` 的『C 风格』变体：根据 `bitVal` 决定把 `bitNo` 位**设为 1 还是 0**，省去自己判断走 SETBIT32 还是 CLEARBIT32 的分支。返回修改后的 32 位值。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    inVal32 : DWORD;
    bitNo : SINT;
    bitVal : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `inVal32` | `DWORD` | 要操作的 32 位值。 |
| `bitNo` | `SINT` | 位号 0-31。 |
| `bitVal` | `BOOL` | TRUE 置 1；FALSE 清 0。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法**：`bitVal = TRUE` → 同 `SETBIT32`；`bitVal = FALSE` → 同 `CLEARBIT32`。

**`bitNo` modulo 32**：与 `SETBIT32` 一致。

**纯函数**：要更新原变量需 `myVar := CSETBIT32(myVar, 5, bFlag)`。

**示例**：`CSETBIT32(16#80000000, 15, TRUE) = 16#80008000`（PDF 原文）。

**典型用法**：根据 BOOL 旗标动态置位 / 清位，例如『读到 DI 高电平 → 把状态字 bit5 置 1，低电平 → 清 0』。把 32 个 BOOL 通道打包到 DWORD 状态字时尤其方便，可以省掉 IF / ELSE 分支。

**与 `SETBIT32` / `CLEARBIT32` 关系**：本函数 = 两者的合成；旗标 TRUE 走 SETBIT32 路径，FALSE 走 CLEARBIT32 路径。可读性更高的同时函数调用开销也相同。

## 4. 错误码 / 返回值

本函数返回 `DWORD`：根据 `bitVal` 把 `bitNo` 位设为 1 或 0 后的新值。

## 5. 使用注意 / 常见坑

- **`bitVal` 必须明确**：传 BOOL 表达式时确保结果非 NULL / 未初始化。（工程经验补充）
- **`bitNo` 同 SETBIT32 的 modulo 32**：负数 / 越界要小心。
- **返回值不写回原变量**：与 SETBIT32 同坑。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CSETBIT32.xml`](../examples/P_Demo_CSETBIT32.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把 32 个 DI 通道的实时状态打包到一个 DWORD 状态字（每位对应一通道），HMI 一次读取就拿到全部 32 通道状态。
- **价值**：替代 SETBIT32 / CLEARBIT32 二选一的 IF 分支。
- **替代方案对比**：
  - IF + SETBIT32 / CLEARBIT32：2 倍代码量。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31013899.html
- **相关 FB / FC**：`SETBIT32`, `CLEARBIT32`, `GETBIT32`
