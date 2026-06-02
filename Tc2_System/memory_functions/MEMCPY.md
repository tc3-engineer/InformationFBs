# MEMCPY

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Memory functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31041163.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_MEMCPY.TcPOU`](../examples/P_Demo_MEMCPY.TcPOU) |

---

## 1. 功能简述

MEMCPY 把源内存地址 `srcAddr` 开始的 `n` 个字节复制到目的地址 `destAddr`。**直接操作物理内存**：参数错误（地址非法、越界、源 / 目标重叠）可能导致系统崩溃或破坏其他变量，PDF NOTICE 段明确警告。返回值是实际复制的字节数（成功 = `n`，参数非法 = 0）。

**重叠未定义**：源和目的重叠时行为未定义；要安全复制重叠区域必须用 `MEMMOVE`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    destAddr : PVOID;
    srcAddr : PVOID;
    n : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `destAddr` | `PVOID` | 目标内存区域起始地址（`PVOID`）。用 `ADR(dstVar)`；不可为 0。 |
| `srcAddr` | `PVOID` | 源内存区域起始地址（`PVOID`）。用 `ADR(srcVar)`；不可为 0。 |
| `n` | `UDINT` | 要复制的字节数。常用 `SIZEOF(dstVar)`，并确保源至少有这么多字节。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，返回时复制已完成。无任何状态机或异步等待。

**参数语义**：`destAddr` / `srcAddr` 通常用 `ADR(myVar)` 取得；`n` 通常用 `SIZEOF(myVar)` 取得。如果两者类型不一致（如 `ADR(stA)` 与 `SIZEOF(stB)`），编译器无法检测错误，会导致越界。

**返回值**：返回实际复制字节数；若 `destAddr == 0` 或 `srcAddr == 0` 或 `n == 0`，返回 0 表示未做任何操作。

**性能**：底层是 C `memcpy`，速度接近内存带宽峰值；远快于自己写 `FOR i := 0 TO n-1 DO dst[i] := src[i]; END_FOR;` 循环（后者每字节有边界检查）。

**重叠时**：源和目的内存区域重叠时行为未定义（PDF 明确）；典型例子是数组元素整体前移 / 后移，必须改用 `MEMMOVE`。

## 4. 错误码 / 返回值

本函数返回 `UDINT`：

| 返回值 | 含义 |
|---|---|
| `0` | 参数非法（`destAddr == 0` 或 `srcAddr == 0` 或 `n == 0`），未复制任何字节 |
| `> 0` | 实际复制的字节数（成功时 = `n`） |

## 5. 使用注意 / 常见坑

- **重叠区域未定义**：要前 / 后移数组元素必须用 `MEMMOVE`，不能用 MEMCPY。
- **不查边界**：参数错可能写坏邻近变量或崩 PLC。永远 `destAddr := ADR(dst); n := SIZEOF(dst)` 并确保 `SIZEOF(src) >= n`。
- **`destAddr == 0`**：地址为 0 返回 0；不要把未初始化的指针传入，建议先 `IF p <> 0 THEN MEMCPY(...); END_IF;`。
- **绕过类型安全**：MEMCPY 抹平所有类型信息，写错结构布局不会被编译器发现。建议优先 `:=` 赋值（同类型）或用 `__VARIANT` 接口。（工程经验补充）
- **对齐**：在 Arm 平台上对非对齐地址的 MEMCPY 可能比 x86 慢；对齐对齐到 4 / 8 字节边界。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MEMCPY.TcPOU`](../examples/P_Demo_MEMCPY.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把刚 `FB_FileRead` 读到的 256 字节缓冲区一次性拷贝到工艺参数结构体里，避免逐字段赋值的繁琐。
- **价值**：一行代码替代手写 256 次 BYTE 赋值循环；速度快、代码短。
- **替代方案对比**：
  - 手写 FOR 循环：可读但慢 5–10 倍且容易写错下标。
  - `MEMMOVE`：支持重叠区域，慢约 10%。
  - `:=` 整体赋值（同类型）：编译器自动展开，更类型安全，但跨类型不行。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31041163.html
- **相关 FB / FC**：`MEMMOVE`, `MEMSET`, `MEMCMP`
