# ASC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85910155.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ASC.TcPOU`](../examples/P_Demo_ASC.TcPOU) |

---

## 1. 功能简述

返回输入字符串首字符的 ASCII 码（一个字节）。串口发送的数据常以字符串形式准备，而逐字节发送（如 `SendByte`）需要把字符转成字节，`ASC` 就用于取出字符串第一个字符对应的字节值。

## 2. 接口定义

### Syntax

```iecst
FUNCTION ASC : BYTE
VAR_INPUT
   str : STRING;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `str` | `STRING` | — | 输入字符串，函数取其首字符的 ASCII 码 |

### 返回值

| 类型 | 说明 |
|---|---|
| `BYTE` | 输入字符串首字符的 ASCII 码 |

## 3. 行为说明

纯函数，调用即返回，无副作用、无异步状态：传入一个字符串，返回它第一个字符对应的 ASCII 字节值。例如 `ASC('A')` 返回 16#41（65）。同一输入重复调用返回相同结果。它只看首字符——传入多字符串（如 `'ABC'`）只取 `'A'` 的码。常见用法是把要发送的字符逐个转成字节后用 `SendByte` 发出，或在解析协议时把字符串里的字符与期望的 ASCII 码比较。它是 `CHR` 的逆操作（`CHR` 把字节转回单字符字符串）。

## 4. 错误码 / 返回值

无错误码——纯函数，恒返回一个 `BYTE`。传入空串时返回值取决于字符串首字节（空串首字节为 `$00`，即返回 0）。

## 5. 使用注意 / 常见坑

- **只取首字符**：多字符串只返回第一个字符的码，需要逐字符处理时配合 `MID` / `DELETE` 等逐个取。
- **空串返回 0**：空字符串首字节是 `$00`，返回 0；调用前确认串非空（工程经验补充）。
- **逆操作是 `CHR`**：字节转字符用 `CHR`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ASC.TcPOU`](../examples/P_Demo_ASC.TcPOU)

```iecst
// 场景：把字符 'A' 转成 ASCII 码 65（16#41），准备用 SendByte 发出。
PROGRAM P_Demo_ASC
VAR
    sChar   : STRING := 'A';
    byCode  : BYTE;
END_VAR

byCode := ASC(sChar);                            // 结果 16#41
```

## 7. 业务场景与实际价值

- **场景**：把字符串里的字符转成字节用于逐字节发送（`SendByte`）、或在解析接收数据时把收到的字符与期望 ASCII 码做比较。
- **价值**：一行调用取字符的 ASCII 码，免去手工查码表或位运算。
- **替代方案对比**：IEC 标准库也有字符串 / 字符转换，但 `ASC` 与本库的串口收发流程配套，语义直观。逆向（字节转字符）用 `CHR`。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.2.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85910155.html
- **相关**：`CHR`（字节转字符，逆操作）、`SendByte`（发字节）、`ReceiveByte`（收字节）
