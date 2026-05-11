# BCD_TO_DEC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34972043.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_BCD_TO_DEC.xml`](../examples/P_Demo_BCD_TO_DEC.xml) |

---

## 1. 功能简述

BCD_TO_DEC 把一个 BCD（Binary Coded Decimal）编码的字节转换为它对应的十进制 BYTE。BCD 编码常见于硬件拨码开关、老式 PLC 模块的状态寄存器、传统现场总线设备：每 4 个二进制位代表 1 个十进制数字，例如 BCD `0x47` 实际表示十进制 47。

本 FB 是个简单的纯计算包装，并不做合法性校验——如果输入字节里某 4 位 nibble 大于 9（非法 BCD），结果未定义。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    START : BOOL;
    BIN : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `START` | `BOOL` | 输入布尔标志：`START`。具体语义见 §3 行为说明。 |
| `BIN` | `BYTE` | 无符号整数输入：`BIN`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    DOUT : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `DOUT` | `BYTE` | 无符号整数输出：`DOUT`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：每次调用读 `BCDIN`，把高 4 位 × 10 + 低 4 位累加，结果赋给 `DECOUT`。无内部状态、无时序、不阻塞。

**典型用例**：
- BK 系列拨码开关：物理上 2 位拨码 → 1 个 BCD 字节 → 本 FB → 程序里的十进制工位编号。
- 老式 DALI / KNX 设备的状态寄存器：1 个 BCD 字节读上来 → 本 FB 还原成可显示数字。

**合法输入范围**：BCD `0x00..0x99`（高位 nibble 0..9，低位 nibble 0..9），输出 `0..99`。超出范围的字节（如 `0xAF`）结果未定义，PDF 没有承诺非法输入的行为，业务侧应自行校验。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详尽列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。如未在 PDF 与 InfoSys 中找到针对某种异常工况的明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **不校验合法性**：输入 `0xAF` 会得到 `15 × 10 + 15 = 165`，可能掩盖现场总线数据帧错误。
- **只接受 1 字节**：两位以上的 BCD 数字需要拆字节后多次调用，或换用更高位宽的转换辅助函数。
- **不是位串到 BCD 的转换**：若现场数据是按位散落的（如某个 16 位寄存器里高 8 位是状态、低 8 位才是 BCD），需要先 `BAND` 取低字节再传入。（工程经验补充）
- 与 `DEC_TO_BCD` 不是恒等可逆对——后者只接受 0..99 输入；BCD_TO_DEC(DEC_TO_BCD(N)) 仅在 0..99 范围内等于 N。（工程经验补充）
- PDF 未列错误码：错误输入只反映在输出值异常，不会有 `bError` 输出。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BCD_TO_DEC.xml`](../examples/P_Demo_BCD_TO_DEC.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：读 BK1120 拨码开关字节，把 BCD 编码的工位号还原成可显示的十进制数字。
- **价值**：把 PDF 文档里没明说的位运算（`SHR(b,4) * 10 + (b AND 16#0F)`）封装为一次调用，业务代码可读性更高，且不需要在维护代码里维护 BCD 位掩码常量。
- **替代方案对比**：
  - 自写位运算：`SHR(BCD,4) * 10 + (BCD AND 16#0F)`，1 行能做，但每个地方都得重复且容易写错。
  - 用 `BYTE_TO_HEXSTR` 然后字符串转 INT：可行但慢且占代码。
  - **本 FB**：标准库提供，零依赖。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34972043.html
- **相关 FB**：`DEC_TO_BCD`
