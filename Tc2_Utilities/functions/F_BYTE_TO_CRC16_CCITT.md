# F_BYTE_TO_CRC16_CCITT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35108363.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml) |

---

## 1. 功能简述

对单个数据字节计算 CRC-16/CCITT 校验，返回新的 16 位 CRC 累积值。生成多项式 `0x1021`（即 `x^16 + x^12 + x^5 + 1`），用于 ITU X.25/T.30、ADCCP、SDLC/HDLC 等协议。

调用模式：调用方传入"上一次 CRC 累积值"或初值（`16#FFFF` / `16#0000`，看协议规范），函数返回处理完当前字节后的累积值。整个数据帧的 CRC 通过对每个字节连续调用本函数获得；如果只想算一整段数据的 CRC，可直接用 `F_DATA_TO_CRC16_CCITT`，内部就是循环调本函数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    value   : BYTE;(* Data value *)
    crc     : WORD;(* Initial value (16#FFFF or 16#0000) or previous CRC-16 result *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `value` | `BYTE` | — | 当前要纳入 CRC 计算的数据字节。 |
| `crc` | `WORD` | — | 初值（`16#FFFF` 或 `16#0000`，看协议）或上一次 `F_BYTE_TO_CRC16_CCITT` 的返回值。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 处理完当前字节后的 16 位 CRC 累积值；可作为下一次调用的 `crc` 入参，或在帧尾作为最终校验值。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数对 `value` 字节执行 CRC-16/CCITT 算法的一轮迭代：把字节移入移位寄存器，按 0x1021 多项式做 8 次异或/移位，得到新的 16 位累积值。

算法属性：
- 多项式：`0x1021`（CRC-16-CCITT 标准）
- 初值：由协议规范决定。X.25 / HDLC 用 `16#FFFF`；XMODEM、AUG-CCITT 用 `16#0000`；调用方负责传对。
- 终值反转 / 求反：本函数不做；如协议要求最终 CRC 取反或交换字节，调用方在帧尾处理。

典型用法：对 N 字节帧逐字节累积——

```iecst
wCrc := 16#FFFF;
FOR i := 0 TO N - 1 DO
    wCrc := F_BYTE_TO_CRC16_CCITT(arFrame[i], wCrc);
END_FOR;
```

得到的 `wCrc` 即帧 CRC；与对端拼到帧尾的 CRC 比对即可校验完整性。要省事直接用 `F_DATA_TO_CRC16_CCITT(ADR(arFrame), SIZEOF(arFrame), 16#FFFF)` 一次算完。

## 4. 错误码 / 返回值

返回 `WORD`，无错误码。该值要么继续作为下次 `crc` 入参，要么帧尾作为最终 CRC 与对端比对。

## 5. 使用注意 / 常见坑

- **初值选择必须按协议**：X.25/HDLC 用 `16#FFFF`，XMODEM 用 `16#0000`；用错值结果一致但与对端永远对不上。
- **字节顺序**：本函数按"先输入先处理"，帧字节顺序就是协议字节顺序；帧尾 CRC 高低字节排列由协议规范决定。
- **不能跳过任何字节**：包含帧头、长度字段、数据载荷，每一字节都要进 CRC（除非协议明示排除）。
- **逐字节调用比 `F_DATA_TO_CRC16_CCITT` 慢但更灵活**：流式协议（数据分多个周期到达）必须逐字节累积；整帧一次到位用 `F_DATA_TO_CRC16_CCITT`（工程经验补充）。
- **多项式不可改**：本函数硬编码 0x1021。需要其他 CRC-16 变体（CRC-16-IBM 0x8005、CRC-16-Modbus）须自行实现或选用其他库。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_BYTE_TO_CRC16_CCITT
VAR
    arFrame : ARRAY[0..3] OF BYTE := [16#01, 16#02, 16#03, 16#04];
    wCrc    : WORD;
    i       : INT;
END_VAR

wCrc := 16#FFFF;                                   // X.25/HDLC 初值
FOR i := 0 TO 3 DO
    wCrc := F_BYTE_TO_CRC16_CCITT(arFrame[i], wCrc);
END_FOR;
// wCrc 现在是 4 字节帧的 CRC-16/CCITT
```

## 7. 业务场景与实际价值

- **场景**：自定义串行协议（基于 EL6022 / 第三方网关）需要 CRC-16/CCITT 校验帧完整性；接收侧逐字节累积，发送侧整帧打包。
- **价值**：免去手写 CRC 表/位运算；多项式由 Beckhoff 验证、和 X.25/HDLC 兼容。
- **替代方案对比**：
  - 手写 CRC：易在多项式 / 位序上写错，调一次半天
  - 整帧调用 `F_DATA_TO_CRC16_CCITT`：流式（边收边累）不便
  - 本函数：流式累积 + 整帧调用两种场景都覆盖

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.30 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35108363.html
- **相关函数**：`F_DATA_TO_CRC16_CCITT`（整段数据一次算 CRC）、`F_CheckSum16`（更简单的 16 位累加和）
