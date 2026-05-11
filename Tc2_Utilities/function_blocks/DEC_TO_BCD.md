# DEC_TO_BCD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34972811.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DEC_TO_BCD.xml`](../examples/P_Demo_DEC_TO_BCD.xml) |

---

## 1. 功能简述

DEC_TO_BCD 是 BCD_TO_DEC 的反向：把一个十进制 BYTE（0..99）编码为对应的 BCD 字节。用于把 PLC 内部的工位号、状态码写到老式 BCD 显示模块、拨码灯阵列等硬件输出端口。

本 FB 也只接受单字节输入，对 ≥ 100 的值不做范围限制——超出 99 的输入会产生不再是有效 BCD 的字节。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    START : BOOL;
    DIN : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `START` | `BOOL` | 输入布尔标志：`START`。具体语义见 §3 行为说明。 |
| `DIN` | `BYTE` | 无符号整数输入：`DIN`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    BOUT : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `BOUT` | `BYTE` | 无符号整数输出：`BOUT`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**计算公式**：`BCDOUT := SHL(DECIN / 10, 4) OR (DECIN MOD 10)`。整数除法和模运算把十进制拆为十位与个位，再拼成 BCD。

**合法输入范围**：0..99。输入 100..255 时结果仍然是个字节，但已经不是合法 BCD（高 nibble 会 ≥ A），具体值需要看公式得到的字节是否能被下游 BCD 显示模块识别。

**无副作用、无时序、不阻塞**。可在任意上下文中调用。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **不做范围校验**：输入 100 → 输出 `0x60`（看似合法 BCD 60），实际语义错乱。业务侧务必先 `LIMIT(0, val, 99)`。
- BCD 数字不能直接送到普通显示器——硬件接口要明确是 BCD 类（如 7 段译码 IC、老式 BK 拨码 IO）才用。（工程经验补充）
- 与 BCD_TO_DEC 配对时只在 0..99 范围内可逆，否则可能不等。（工程经验补充）
- PDF 未列错误码：错误只反映在输出字节异常，无 `bError`。
- 跨字节数值（≥ 100）应使用多次调用拆位发送或使用专门的多位 BCD 包，本 FB 不能处理。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DEC_TO_BCD.xml`](../examples/P_Demo_DEC_TO_BCD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把 PLC 内部计数器 0..99 编码为 BCD 字节，输出到老式 7 段译码板显示。
- **价值**：封装 `SHL(D/10,4) OR (D MOD 10)` 这段位运算，零依赖。
- **替代方案对比**：
  - 自写表达式：`SHL(D/10,4) OR (D MOD 10)`，一行能做但易写错。
  - **本 FB**：标准库提供，含义自解释。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34972811.html
- **相关 FB**：`BCD_TO_DEC`
