# ReceiveString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85889035.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ReceiveString.TcPOU`](../examples/P_Demo_ReceiveString.TcPOU) |

---

## 1. 功能简述

从与接收缓冲区 `RxBuffer` 对应的串口接收一串字符，存入 `ReceivedString`（`STRING`，标准长度 80 字符）。字符串的起止用前缀（Prefix）、后缀（Suffix）、字符间超时（Timeout）三种可组合的机制识别。需要更长的字符串时改用 `ReceiveString255`（区别仅在 `ReceivedString` 长度为 255）。

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
| `Reset` | `BOOL` | — | 置位将功能块从接收态复位到初始态；仅例外情况（期望字符串未到、功能块卡 busy）需要 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  ReceivedString   : STRING;
  RXBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ReceivedString` | `STRING` | `StringReceived` 变 `TRUE` 时此处即为收到的字符串 |
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

调用即执行、内部带 `busy` 状态机，语义与 `ReceiveData` 一致，但结果直接以 IEC `STRING` 形式给出，省去指针与字节数组。收到第一个字符后 `busy = TRUE`；给了 `Prefix` 时收到的头部必须匹配前缀，否则丢弃前面的字符；给了 `Suffix` 时一直收到尾部匹配后缀为止，期间若超出接收字符串最大长度报 `COMERROR_STRINGOVERRUN`；给了 `Timeout` 时按字符间隔超时断串。后缀为空串就必须靠超时判断结束，否则无法识别字符串末尾。要只接受完整无误的字符串，应在 `StringReceived = TRUE` 之外同时判 `RxTimeout = FALSE` 且 `Error = COMERROR_NOERROR`（无后缀场景下超时即正常结束）。注意 `ReceivedString` 是 `VAR_IN_OUT`，必须由调用方声明一个 `STRING` 变量传入，功能块写入其中。串里若可能出现 `$00`（0 字符）会和 IEC 字符串结束符冲突，此时应改用 `ReceiveData` 处理二进制。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_STRINGOVERRUN` (10) | 收到的字符串超出最大长度（未匹配到后缀） | 检查后缀是否正确，或改用 `ReceiveString255` |
| `COMERROR_ZEROCHARINVALID` (11) | 字符串中出现不允许的 0 字符 | 含 `$00` 的二进制数据请改用 `ReceiveData` |
| `COMERROR_PARAMETERCHANGED` (1) | 接收过程中输入参数被改变 | 接收期间不要改 `Prefix` / `Suffix` |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **`StringReceived` 只在收齐当周期判断**：配合后缀时务必同时查 `RxTimeout = FALSE` 与 `Error = COMERROR_NOERROR`，避免把超时截断的半串当完整串。
- **80 字符上限**：超长会报 `COMERROR_STRINGOVERRUN`；预计更长的报文用 `ReceiveString255`。
- **不能收含 0 字符的二进制**：IEC `STRING` 以 `$00` 结尾，二进制流请用 `ReceiveData`。
- **`ReceivedString` 是 IN_OUT**：调用方负责声明字符串变量并传入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ReceiveString.TcPOU`](../examples/P_Demo_ReceiveString.TcPOU)

```iecst
// 场景：收以 LF 结尾的文本命令行。
PROGRAM P_Demo_ReceiveString
VAR
    fbReceiveString : ReceiveString;
    bufRx           : ComBuffer;
    sReceived       : STRING;                   // IN_OUT，存放收到的串
    bGotLine        : BOOL;
END_VAR

fbReceiveString(
    Prefix         := '',
    Suffix         := '$L',                     // LF 作为行结束符
    Timeout        := T#500MS,
    Reset          := FALSE,
    ReceivedString := sReceived,
    RXBuffer       := bufRx,
    StringReceived => bGotLine
);
```

## 7. 业务场景与实际价值

- **场景**：和输出 ASCII 文本行的设备对接，如打印机回执、GPS NMEA 语句、命令行式仪表（每条命令以 CR/LF 结束）。
- **价值**：直接拿到 IEC `STRING`，可立即用 `FIND` / `MID` 等字符串函数解析，无需指针和字节数组转换。
- **替代方案对比**：定长或含 0 字符的二进制帧用 `ReceiveData`；更长文本用 `ReceiveString255`；逐字符流式处理用 `ReceiveByte`。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85889035.html
- **相关**：`ReceiveString255`（255 字符版）、`SendString`（发送字符串）、`ReceiveData`（二进制成帧）、`SerialLineControl`（填充 `RxBuffer`）、`ComError_t`
