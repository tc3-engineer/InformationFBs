# MEMMOVE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Memory functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31044235.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_MEMMOVE.TcPOU`](../examples/P_Demo_MEMMOVE.TcPOU) |

---

## 1. 功能简述

MEMMOVE 把源内存地址开始的 `n` 个字节复制到目的地址。与 `MEMCPY` 的唯一区别是**支持源 / 目的重叠**：典型用途是把数组元素整体前移或后移。代价是内部多一层缓冲拷贝，速度比 MEMCPY 慢约 5–15%；不重叠时优先用 MEMCPY。

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
| `destAddr` | `PVOID` | 目标内存区域起始地址（`PVOID`）。允许与 `srcAddr` 重叠。 |
| `srcAddr` | `PVOID` | 源内存区域起始地址（`PVOID`）。允许与 `destAddr` 重叠。 |
| `n` | `UDINT` | 要复制的字节数。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，返回时复制完成。

**重叠区域处理**：内部检测 `srcAddr` 与 `destAddr` 的位置关系，若 `dst > src`（向右移）则**从尾向头**复制，反之**从头向尾**复制，保证不会覆盖未读的字节。

**返回值**：返回实际复制字节数；参数非法（任一地址为 0 或 `n == 0`）返回 0。

**典型用法**：数组左移一位 `MEMMOVE(ADR(arr[0]), ADR(arr[1]), (SIZEOF(arr) - SIZEOF(arr[0])));`——把 `arr[1..N]` 拷到 `arr[0..N-1]`，此时源和目的明显重叠，MEMCPY 不能用。

**性能折损**：不重叠时也能用，但每次调用都做一次方向检测，比 MEMCPY 略慢。

## 4. 错误码 / 返回值

本函数返回 `UDINT`：

| 返回值 | 含义 |
|---|---|
| `0` | 参数非法（地址为 0 或 `n == 0`），未复制任何字节 |
| `> 0` | 实际复制的字节数（成功时 = `n`） |

## 5. 使用注意 / 常见坑

- **不重叠用 MEMCPY 更快**：MEMMOVE 永远做方向检测；明确知道不重叠时用 MEMCPY 省 5–15% 时间。
- **仍不查边界**：和 MEMCPY 一样越界会写坏邻近变量，永远用 `SIZEOF` + 确认源足够大。
- **`destAddr / srcAddr == 0`**：返回 0 不复制；调用方应先做指针非空检查。
- **对齐 / Arm**：与 MEMCPY 一致，对齐到 4 / 8 字节边界可提速。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MEMMOVE.TcPOU`](../examples/P_Demo_MEMMOVE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：环形缓冲区移位：把样本数组的最新一个元素挤到末尾，前面元素整体左移一格。
- **价值**：MEMCPY 在重叠区域行为未定义；MEMMOVE 保证正确移位，替代 5–10 行手写 FOR 循环。
- **替代方案对比**：
  - 手写 FOR 循环：可读但慢且容易写错方向。
  - MEMCPY：不重叠时更快，重叠时**不能**用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31044235.html
- **相关 FB / FC**：`MEMCPY`, `MEMSET`, `MEMCMP`
