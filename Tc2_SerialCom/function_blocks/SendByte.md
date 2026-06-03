# SendByte

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85890571.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendByte.TcPOU`](../examples/P_Demo_SendByte.TcPOU) |

---

## 1. 功能简述

向与发送缓冲区 `TxBuffer`（类型 `ComBuffer`）对应的串口发送单个字符。只要发送缓冲区还能容纳数据，一个 PLC 周期里可以连续发多个字符（每周期多次调用）——但仅当有一个更快的通信任务把缓冲字符搬给硬件时才有意义。真正的发送由后台功能块 `SerialLineControl` / `SerialLineControlADS` 完成，本功能块只往 `TxBuffer` 里塞字节。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  SendByte           : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `SendByte` | `BYTE` | — | 要发送的字符 / 字节 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  TxBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TxBuffer` | `ComBuffer` | 与所用串口对应的发送数据缓冲区 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  Busy            : BOOL;
  Error           : ComError_t;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 为 `TRUE` 时发送未完成；`Busy = FALSE` 且 `Error = 0` 表示发送成功。若首次调用即发出，`Busy` 不会变 `TRUE` |
| `Error` | `ComError_t` | 发生故障时返回错误码 |

## 3. 行为说明

调用即把 `SendByte` 这个字节写入 `TxBuffer`，由后台通信功能块异步发往硬件。发送状态通过 `Busy` 反映：缓冲区放得下时字节立刻入队，`Busy` 保持 `FALSE`；缓冲区满需要等待时 `Busy` 变 `TRUE`，待后台把字节搬给硬件腾出空间后回到 `FALSE`。`Busy = FALSE` 且 `Error = 0` 即代表该字节已成功交付发送缓冲。注意"成功入缓冲"不等于"已从硬件发出"，真正出线由后台功能块按硬件节奏完成。由于一个周期内只要缓冲区有空就能反复入队，发多字节时可在循环里连续调用，但这只有在另有更快的通信任务时才会真正提升吞吐。本功能块没有 Execute 上升沿语义：每次调用就尝试发一个字节，调用方自己控制何时调、调几次。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_TXBUFFOVERRUN` (2) | 发送缓冲区溢出 | 降低发送速率，或确保后台通信任务足够快 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **`Busy` 可能始终为 `FALSE`**：缓冲区够用时字节一次就入队，`Busy` 不会变高，不要把"没看到 Busy=TRUE"误判为没发出。
- **`TxBuffer` 要与后台功能块同实例**：本功能块写入的缓冲必须正是 `SerialLineControl` / `SerialLineControlADS` 的 `TxBuffer`。
- **逐字节发送效率低**：发完整报文用 `SendData`，发字符串用 `SendString` 更省调用（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendByte.TcPOU`](../examples/P_Demo_SendByte.TcPOU)

```iecst
// 场景：向设备发一个触发字节（如 ENQ = 16#05）。
PROGRAM P_Demo_SendByte
VAR
    fbSendByte : SendByte;
    bufTx      : ComBuffer;
    bSendNow   : BOOL;
    bBusy      : BOOL;
END_VAR

IF bSendNow THEN
    fbSendByte(
        SendByte := 16#05,                      // ENQ
        TxBuffer := bufTx,
        Busy     => bBusy
    );
END_IF
```

## 7. 业务场景与实际价值

- **场景**：向设备发送单字节控制码，如 ENQ/ACK/NAK 握手字符、触发扫码的单字节命令、简单协议的心跳字节。
- **价值**：把"向发送缓冲入队一个字节"封装为一次调用，免去自行操作 `ComBuffer` 环形缓冲结构。
- **替代方案对比**：连续多字节报文用 `SendData`（一次给地址+长度）；字符串用 `SendString`；仅在确实只需发单字节、或要按字节级精细控制时间时才用本功能块。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85890571.html
- **相关**：`ReceiveByte`（收单字节）、`SendData` / `SendString`（成块/字符串发送）、`SerialLineControl`（消费 `TxBuffer`）、`ComBuffer`、`ComError_t`
