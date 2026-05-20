# MEMCMP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Memory functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31039627.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_MEMCMP.xml`](../examples/P_Demo_MEMCMP.xml) |

---

## 1. 功能简述

MEMCMP 比较两个内存区域的前 `n` 字节，返回 `-1` / `0` / `1` 三态表示大小关系。比较方式与 C `memcmp` 一致：逐字节无符号比较，遇到第一个不同字节即返回结果。适用于结构体批量相等性检查、二进制数据 diff 等场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pBuf1 : PVOID;
    pBuf2 : PVOID;
    n : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pBuf1` | `PVOID` | 第一块内存起始地址。 |
| `pBuf2` | `PVOID` | 第二块内存起始地址。 |
| `n` | `UDINT` | 要比较的字节数。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，返回三态值。

**返回值语义**：

- `-1`：在第一个不同字节处，`pBuf1` 的值**小于** `pBuf2`；
- ` 0`：前 `n` 字节完全相同；
- ` 1`：在第一个不同字节处，`pBuf1` 的值**大于** `pBuf2`。

**逐字节无符号比较**：把字节当作 `USINT` (0–255) 比较；不区分有符号 / 浮点；要比较 LREAL 等浮点用专门的浮点比较（考虑 NaN）。

**直接操作物理内存**：参数非法（地址 0、n 越界）可能崩溃，PDF NOTICE 警告。

**典型应用场景**：判等比手写循环灵活，可比较任意类型 / 结构体 / 数组的内存映像；返回三态语义还适用于排序键比较场景。

## 4. 错误码 / 返回值

本函数返回 `DINT`：

| 返回值 | 含义 |
|---|---|
| `-1` | `pBuf1` 在第一个不同字节处小于 `pBuf2` |
| `0`  | 前 `n` 字节完全相同 |
| `1`  | `pBuf1` 在第一个不同字节处大于 `pBuf2` |

## 5. 使用注意 / 常见坑

- **不可用于浮点比较**：`+0.0` 和 `-0.0` 字节不同但数值相等；NaN 与自身字节相同但 `NaN != NaN`。
- **不可用于含 padding 的结构体**：编译器对齐 padding 字节内容未初始化，比较结果不稳定。要比较结构体先 MEMSET 0 再赋值。
- **`pBuf1 / pBuf2 == 0`**：PDF 未明确，实测通常返回 0（视为相等）；调用方应自检指针非空。（工程经验补充）
- **返回类型 `DINT`**：不要把返回值当 BOOL 直接用 `IF MEMCMP(...) THEN`——0 = 相等才是 FALSE，反直觉。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MEMCMP.xml`](../examples/P_Demo_MEMCMP.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：检查 200 字节的工艺参数结构体是否与上次保存的一致——一致则跳过持久化，避免无变化时的频繁写盘。
- **价值**：一行函数比手写循环 + 早返判等省约 8 行；速度快约 5–10 倍。
- **替代方案对比**：
  - 手写 FOR 循环逐字节比：慢且冗长。
  - 结构体 `=` 运算符（IEC 不支持）：要 Beckhoff 拓展支持。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31039627.html
- **相关 FB / FC**：`MEMCPY`, `MEMMOVE`, `MEMSET`
