# ReceiveByte

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85885963.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ReceiveByte.TcPOU`](../examples/P_Demo_ReceiveByte.TcPOU) |

---

## 1. 功能简述

从与接收缓冲区 `RxBuffer`（类型 `ComBuffer`）对应的串口逐字节取出已收到的数据。每次调用最多取出一个字节：若调用后 `ByteReceived = TRUE`，则该字节在 `ReceivedByte` 中；若为 `FALSE` 则本次没有可读数据。它不直接和硬件打交道，真正的收发由后台功能块 `SerialLineControl` / `SerialLineControlADS` 负责，本功能块只从 PLC 内部的 `ComBuffer` 里取字节。

## 2. 接口定义

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  RXBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `RxBuffer` | `ComBuffer` | 与所用串口对应的接收数据缓冲区，由后台通信功能块填充 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  ByteReceived       : BOOL;
  ReceivedByte       : BYTE;
  Error              : ComError_t;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ByteReceived` | `BOOL` | 调用后为 `TRUE` 表示收到一个字节、可在 `ReceivedByte` 读取；为 `FALSE` 表示本次无数据 |
| `ReceivedByte` | `BYTE` | `ByteReceived = TRUE` 时此处为收到的数据字节 |
| `Error` | `ComError_t` | 发生故障时返回对应错误码 |

### VAR_INPUT

无。

## 3. 行为说明

调用即执行，没有 Execute 上升沿和 Busy 状态：每个 PLC 周期调用一次，功能块就尝试从 `RxBuffer` 取一个字节。当 PLC 任务周期慢于硬件的通信任务时，一个周期内缓冲区里可能积累了多个字符，因此官方要求在循环里反复读直到 `ByteReceived = FALSE`，否则数据会越积越多甚至丢失。典型写法是一个 `REPEAT … UNTIL NOT ReceiveByte.ByteReceived END_REPEAT` 循环，把缓冲区里当前可读的字节一次性全部取走再处理。循环不会变成死循环：接收缓冲区容量有限（目前约 300 字节），最多循环到缓冲区清空为止。`Error` 在正常情况下为 `COMERROR_NOERROR`（值 0），只有底层缓冲区出现异常时才置位。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，常见取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_INVALIDPOINTER` (20) | 数据指针无效（例如为空） | 检查 `RxBuffer` 是否正确声明并被后台通信功能块引用 |

完整 `ComError_t` 列表见 PDF 第 7.2 节 / InfoSys 错误码页。

## 5. 使用注意 / 常见坑

- **必须在循环里读**：单次调用只取一个字节。若 PLC 周期较慢而每周期只调一次，缓冲区会溢出、数据丢失。务必用 `REPEAT` 循环读空缓冲区。
- **`RxBuffer` 要和后台通信功能块用同一个实例**：`ReceiveByte` 读的缓冲区必须正是 `SerialLineControl` / `SerialLineControlADS` 的 `RxBuffer`，否则永远收不到数据。
- **逐字节处理开销**：适合简单字符流；定长报文用 `ReceiveData`、字符串协议用 `ReceiveString` 更省事（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ReceiveByte.TcPOU`](../examples/P_Demo_ReceiveByte.TcPOU)

```iecst
// 场景：扫码枪逐字符吐数据，PLC 周期慢于串口任务，需一次读空缓冲区。
PROGRAM P_Demo_ReceiveByte
VAR
    fbReceiveByte   : ReceiveByte;
    bufRx           : ComBuffer;            // 与 SerialLineControl 共用同一实例
    byLastReceived  : BYTE;
    nReadCount      : UDINT;
END_VAR

// 循环读空：每周期把缓冲区里当前可读字节全部取走
REPEAT
    fbReceiveByte(RXBuffer := bufRx);
    IF fbReceiveByte.ByteReceived THEN
        byLastReceived := fbReceiveByte.ReceivedByte;
        nReadCount := nReadCount + 1;
    END_IF
UNTIL NOT fbReceiveByte.ByteReceived
END_REPEAT
```

## 7. 业务场景与实际价值

- **场景**：和按字节流式输出的简单设备对接，如条码扫描器、称重仪表、老式 RS232 仪器的单字符回显。
- **价值**：把"从 PLC 接收缓冲区取一个字节"封装成一次调用，配合循环即可吞掉一周期内的全部到达字符，避免自己操作 `ComBuffer` 内部结构。
- **替代方案对比**：定长二进制报文用 `ReceiveData`（带前缀/后缀/超时判帧）；以换行或固定结束符分隔的文本用 `ReceiveString`，都比逐字节自行拼帧省代码。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85885963.html
- **相关**：`SendByte`（发单字节）、`ReceiveData` / `ReceiveString`（成帧接收）、`SerialLineControl`（填充 `RxBuffer`）、`ComBuffer`（缓冲区结构）
