# ReceiveString255

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/5291255307.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ReceiveString255.TcPOU`](../examples/P_Demo_ReceiveString255.TcPOU) |

---

## 1. 功能简述

与 `ReceiveString` 完全相同的字符串接收功能块，唯一区别是 `ReceivedString` 的长度为 255 字符（`ReceiveString` 为 80）。从 `RxBuffer` 对应的串口接收一串字符并存入 `ReceivedString`，起止通过前缀、后缀、字符间超时三种可组合的机制识别。适合一行较长（> 80 字符）的文本报文。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Prefix          : STRING;
  Suffix          : STRING;
  Timeout         : TIME;
  Reset           : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Prefix` | `STRING` | — | 收到的字符串首部必须与此前缀一致，其余字符被丢弃；空串表示从第一个收到的字符开始 |
| `Suffix` | `STRING` | — | 一直收到字符串尾部与后缀一致为止；过程中若达到接收字符串最大长度则报 `COMERROR_STRINGOVERRUN`；后缀为空串时必须改用超时判帧 |
| `Timeout` | `TIME` | — | 收到字符后间隔超过此值即结束接收，已收字符即为结果；可与后缀组合，给了后缀时可设 0 |
| `Reset` | `BOOL` | — | 置位将功能块从接收态复位到初始态；仅例外情况需要 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  ReceivedString   : STRING(255);
  RXBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ReceivedString` | `STRING(255)` | `StringReceived` 变 `TRUE` 时此处即为收到的字符串（最多 255 字符） |
| `RxBuffer` | `ComBuffer` | 与所用串口对应的接收缓冲区 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  StringReceived  : BOOL
  busy            : BOOL;
  Error           : ComError_t;
  RxTimeout       : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `StringReceived` | `BOOL` | 收齐字符串时变 `TRUE`，此时 `ReceivedString` 有效 |
| `busy` | `BOOL` | 收到第一个字符后变 `TRUE`，收齐 / 出错 / 超时后变 `FALSE` |
| `Error` | `ComError_t` | 发生故障时返回错误码 |
| `RxTimeout` | `BOOL` | 字符间隔超过最大值导致接收中止时变 `TRUE`；无后缀时是正常结束，有后缀时表示后缀未收到 |

## 3. 行为说明

行为与 `ReceiveString` 一字不差，仅 `ReceivedString` 可容纳 255 字符。调用即执行、内部带 `busy` 状态机：收到第一个字符后 `busy = TRUE`；给了 `Prefix` 时头部须匹配前缀否则丢弃前导字符；给了 `Suffix` 时收到尾部匹配后缀为止，期间若超出 255 字符报 `COMERROR_STRINGOVERRUN`；给了 `Timeout` 时按字符间隔超时断串；后缀为空串则必须靠超时识别末尾。要只接受完整无误的字符串，应在 `StringReceived = TRUE` 之外同时判 `RxTimeout = FALSE` 且 `Error = COMERROR_NOERROR`（无后缀场景下超时即正常结束）。`ReceivedString` 是 `VAR_IN_OUT`，由调用方声明 `STRING(255)` 变量传入。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_STRINGOVERRUN` (10) | 收到的字符串超出 255 字符（未匹配到后缀） | 检查后缀是否正确，或换用支持成帧的 `ReceiveData` |
| `COMERROR_ZEROCHARINVALID` (11) | 字符串中出现不允许的 0 字符 | 含 `$00` 的二进制数据请改用 `ReceiveData` |
| `COMERROR_PARAMETERCHANGED` (1) | 接收过程中输入参数被改变 | 接收期间不要改 `Prefix` / `Suffix` |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **与 `ReceiveString` 的唯一差异是长度**：接收字符串可达 255 字符；80 字符够用时用 `ReceiveString` 更省内存。
- **完整串判定**：用后缀时同时查 `RxTimeout = FALSE` 与 `Error = COMERROR_NOERROR`。
- **不能收含 0 字符的二进制**：IEC `STRING` 以 `$00` 结尾，二进制流请用 `ReceiveData`。
- **`ReceivedString` 是 IN_OUT**：调用方需声明 `STRING(255)` 变量并传入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ReceiveString255.TcPOU`](../examples/P_Demo_ReceiveString255.TcPOU)

```iecst
// 场景：收较长的 NMEA 语句（可超 80 字符），以 CR/LF 结尾。
PROGRAM P_Demo_ReceiveString255
VAR
    fbReceiveString255 : ReceiveString255;
    bufRx              : ComBuffer;
    sReceived          : STRING(255);           // IN_OUT，最长 255 字符
    bGotSentence       : BOOL;
END_VAR

fbReceiveString255(
    Prefix         := '$',                      // NMEA 语句以 '$' 开头
    Suffix         := '$R$L',                   // CR LF 结束
    Timeout        := T#500MS,
    Reset          := FALSE,
    ReceivedString := sReceived,
    RXBuffer       := bufRx,
    StringReceived => bGotSentence
);
```

## 7. 业务场景与实际价值

- **场景**：接收一行可能较长的文本报文，如 GPS 模块的完整 NMEA 语句、带多字段的命令行、SCADA 下发的长配置串。
- **价值**：在 `ReceiveString` 的便利性上把单行长度上限提到 255 字符，避免长报文触发溢出错误。
- **替代方案对比**：≤ 80 字符用 `ReceiveString`；二进制 / 含 0 字符或需要前缀字节匹配用 `ReceiveData`；逐字符处理用 `ReceiveByte`。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/5291255307.html
- **相关**：`ReceiveString`（80 字符版）、`SendString255`（发送 255 字符）、`ReceiveData`（二进制成帧）、`ComError_t`
