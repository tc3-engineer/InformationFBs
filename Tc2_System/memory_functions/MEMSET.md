# MEMSET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Memory functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31042699.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_MEMSET.xml`](../examples/P_Demo_MEMSET.xml) |

---

## 1. 功能简述

MEMSET 把目的地址开始的 `n` 个字节全部填充为 `fillByte` 的值。典型用法是清零（`fillByte := 0`）一个结构体或缓冲区；速度远快于手写 FOR 循环逐字段赋零。**直接操作物理内存**，参数错误可能崩溃，PDF NOTICE 明确警告。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    destAddr : PVOID;
    fillByte : USINT;
    n : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `destAddr` | `PVOID` | 要填充的内存起始地址（`PVOID`）。用 `ADR(buf)`。 |
| `fillByte` | `USINT` | 填充字节值（`USINT` 范围 0–255）。清零用 0；全 1 用 `16#FF`。 |
| `n` | `UDINT` | 要填充的字节数。常用 `SIZEOF(buf)`。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，返回时填充完成。

**参数语义**：`destAddr` 通常 `ADR(myVar)`；`n` 通常 `SIZEOF(myVar)`。`fillByte` 是单字节值（`USINT`），每个字节都被写为该值——清零用 `0`，清成全 1 用 `16#FF`。

**返回值**：返回实际写入字节数；`destAddr == 0` 或 `n == 0` 时返回 0。

**性能**：底层是 C `memset`，速度接近内存带宽峰值；远快于手写循环。

## 4. 错误码 / 返回值

本函数返回 `UDINT`：

| 返回值 | 含义 |
|---|---|
| `0` | 参数非法（`destAddr == 0` 或 `n == 0`），未填充任何字节 |
| `> 0` | 实际填充的字节数（成功时 = `n`） |

## 5. 使用注意 / 常见坑

- **只能填充 1 字节模式**：不能直接用 MEMSET 把 `WORD` 数组填充为某个 16 位值；要填 `0xAAAA` 这种 pattern 必须循环填或自己实现。
- **不查边界**：`n > SIZEOF(buf)` 会写坏邻近变量。永远 `n := SIZEOF(buf)`。
- **清零结构体陷阱**：结构体里有 STRING / 类对象时，MEMSET 0 会破坏其内部状态（null terminator 被覆盖到中间）。结构体清零优先用 `myStruct := DEFAULT_VALUE_OF_TYPE;` 整体赋值。（工程经验补充）
- **浮点数清零是 0.0**：把 LREAL 数组用 MEMSET 0 填充结果是 +0.0（IEEE 754 全 0 字节）；要填 NaN / Inf 必须用循环或 MEMCPY 一个预制 pattern。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MEMSET.xml`](../examples/P_Demo_MEMSET.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：设备启动时把一个 1 KB 的工艺数据缓冲区一次性清零，避免冷启动残留旧数据污染逻辑。
- **价值**：一行代码替代 1024 次 BYTE 赋零循环；速度快约 5–10 倍。
- **替代方案对比**：
  - 手写 FOR 循环逐字节赋零：慢且代码冗长。
  - 结构体整体赋值 `myStruct := (default)`：编译器自动展开，更类型安全。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31042699.html
- **相关 FB / FC**：`MEMCPY`, `MEMMOVE`, `MEMCMP`
