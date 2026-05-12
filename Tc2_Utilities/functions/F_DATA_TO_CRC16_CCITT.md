# F_DATA_TO_CRC16_CCITT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35114507.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml) |

---

## 1. 功能简述

对一段任意长度的数据 buffer（`pData` + `cbData`）一次性计算 CRC-16/CCITT 校验值。内部循环调用 `F_BYTE_TO_CRC16_CCITT`，对每个字节按多项式 `0x1021` 累积。

适用于"整帧到达"后整体校验的场景；如果数据是流式（边收边算）则用 `F_BYTE_TO_CRC16_CCITT` 逐字节累积更合适。`crc` 初值由协议规范决定，X.25/HDLC 用 `16#FFFF`，XMODEM 用 `16#0000`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pData  : POINTER TO BYTE;(* Pointer to first data byte *)
    cbData : UDINT;(* Length of data *)
    crc    : WORD;(* Initial value (16#FFFF or 16#0000) or previous CRC-16 result *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pData` | `POINTER TO BYTE` | — | 数据 buffer 起始地址（`ADR()`）。 |
| `cbData` | `UDINT` | — | 数据长度（字节，`SIZEOF()`）。 |
| `crc` | `WORD` | — | 初值（按协议：`16#FFFF` 或 `16#0000`）或上一段的 CRC 结果（支持分段累积）。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 16 位 CRC 累积值。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数遍历 `pData` 起的 `cbData` 个字节，对每个字节按多项式 `0x1021` 做一轮 CRC-16/CCITT 累积，等价于内部循环调用 `F_BYTE_TO_CRC16_CCITT`：先把当前 `crc` 与新字节做异或，再连续 8 次右移并按多项式异或，最终更新累积值；遍历完后返回最后一次累积结果。

```iecst
FOR i := 0 TO cbData - 1 DO
    crc := F_BYTE_TO_CRC16_CCITT(pData^[i], crc);
END_FOR;
RETURN crc;
```

关键算法属性：
- **多项式**：`0x1021`（CRC-16-CCITT 国际标准）
- **不做终值反转 / 求反**：与 `F_BYTE_TO_CRC16_CCITT` 一致；协议需求由调用方在帧尾处理
- **支持分段累积**：传上次返回值作 `crc` 入参可接着算
- **`cbData = 0`**：直接返回入参 `crc`（一字节都没算）
- **`pData = 0` 与 `cbData > 0`**：访问空指针，PLC 异常；调用前必须保证 `pData <> 0`

典型用法：
```iecst
wFrameCrc := F_DATA_TO_CRC16_CCITT(ADR(arFrame), SIZEOF(arFrame), 16#FFFF);
IF wFrameCrc = wExpectedCrc THEN
    // 帧完整，处理 payload
ELSE
    // 校验失败，丢弃
END_IF
```

与对端的 CRC 字段比对前注意：对端可能要求按特定字节序（大端 / 小端）写帧尾两字节，PLC 端要按协议规范 `SWAP` 后再比对或装帧。

## 4. 错误码 / 返回值

返回 `WORD`，无错误码。`cbData = 0` 时返回入参 `crc`；`pData = 0` 而 `cbData > 0` 触发空指针访问，由调用方保证。

## 5. 使用注意 / 常见坑

- **初值按协议**：X.25/HDLC 用 `16#FFFF`，XMODEM 用 `16#0000`；选错与对端永远对不上。
- **空指针不做检查**：本函数内部循环假设 `pData` 有效；调用前自查（工程经验补充）。
- **跨段累积要传上次结果**：分多段计算时如忘传 → 每段从初值重算 → 最终是最后一段的 CRC。
- **CRC 字段大小端**：本函数返回 `WORD` 是 PLC 原生字节序（小端）；协议如规定帧尾 CRC 大端要 `SWAP`。
- **不要用 `F_CheckSum16` 当 CRC**：checksum 强度低，能对得上字节但不能对得上"相同字节不同顺序"——CRC 才能检出顺序错。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_DATA_TO_CRC16_CCITT
VAR
    arFrame : ARRAY[0..3] OF BYTE := [16#01, 16#02, 16#03, 16#04];
    wCrc    : WORD;
END_VAR

wCrc := F_DATA_TO_CRC16_CCITT(pData := ADR(arFrame), cbData := SIZEOF(arFrame), crc := 16#FFFF);
// 等价于循环调 F_BYTE_TO_CRC16_CCITT，但一行搞定
```

## 7. 业务场景与实际价值

- **场景**：通过 EL6022 / Modbus RTU 接收完整帧后整体校验；帧尾 2 字节是 CRC-16/CCITT。
- **价值**：单调用 = 一个循环 + 多项式 + 位移；性能稳定，避免手写易错。
- **替代方案对比**：
  - 手写循环 + `F_BYTE_TO_CRC16_CCITT`：可，但每次都要写一遍
  - 自己实现 0x1021 算法：30+ 行代码，易在位序写错
  - 本函数：一行；流式需求时用 `F_BYTE_TO_CRC16_CCITT`

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.34 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35114507.html
- **相关函数**：`F_BYTE_TO_CRC16_CCITT`（单字节迭代版）、`F_CheckSum16`（弱校验，更快但不抗顺序错）
