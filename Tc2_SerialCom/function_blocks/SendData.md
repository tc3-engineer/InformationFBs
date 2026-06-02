# SendData

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85892107.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendData.TcPOU`](../examples/P_Demo_SendData.TcPOU) |

---

## 1. 功能简述

把任意类型变量的内容发送到与发送缓冲区 `TxBuffer`（类型 `ComBuffer`）对应的串口。通过 `pSendData` 给出发送数据的起始地址（用 `ADR()` 取）、`Length` 给出要发送的字节数。真正的发送由后台功能块 `SerialLineControl` / `SerialLineControlADS` 异步完成，本功能块负责把数据交给 `TxBuffer`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  pSendData           : POINTER TO BYTE;
  Length              : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pSendData` | `POINTER TO BYTE` | — | 发送数据的地址，用 `ADR(发送数据)` 取。在 `Busy = TRUE` 且数据尚未发完期间不得修改该数据 |
| `Length` | `UDINT` | — | 要发送的字节数，可小于等于数据结构大小；要发整个变量用 `SIZEOF(发送数据)` |

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
| `Busy` | `BOOL` | 为 `TRUE` 时发送未完成；`Busy = FALSE` 且 `Error = 0` 表示发送成功。若首次调用即发出则 `Busy` 不变 `TRUE`；数据发完 / 出错 / 超时后 `Busy` 变 `FALSE` |
| `Error` | `ComError_t` | 发生故障时返回错误码 |

## 3. 行为说明

调用即把 `pSendData` 指向的 `Length` 个字节交给 `TxBuffer`，由后台通信功能块异步发往硬件。发送进度通过 `Busy` 反映：数据一次性放得进缓冲区时 `Busy` 保持 `FALSE`；数据量大于缓冲区可用空间需要分批入队时 `Busy` 变 `TRUE`，待后台搬出腾出空间、整批数据发完后 `Busy` 回到 `FALSE`。判断"已成功交付发送"的条件是 `Busy = FALSE` 且 `Error = 0`。关键陷阱是：`Busy = TRUE` 且数据尚未发完期间，**绝不能修改 `pSendData` 指向的内存**，否则对端会收到一半旧数据一半新数据。本功能块以电平方式工作而非上升沿触发——只要调用且数据没发完就持续推进；调用方通常在数据准备好后开始调用，直到 `Busy = FALSE` 表示发完。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_INVALIDPOINTER` (20) | `pSendData` 指针无效（如为空） | 用 `ADR()` 正确赋值 |
| `COMERROR_TXBUFFOVERRUN` (2) | 数据超过发送缓冲区容量 | 减小单次 `Length`，或确保后台通信任务足够快 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **`Busy` 期间锁住发送缓冲变量**：发送未完成时修改 `pSendData` 指向的数据会导致对端收到错位数据。最简单的做法是把发送变量做成发送期间不被其他逻辑改写的局部 / 全局变量。
- **`Length` 必须正确**：用 `SIZEOF()` 取整个变量大小，或显式给出要发的字节数；写大了会发出多余字节。
- **`TxBuffer` 要与后台功能块同实例**。
- **"入缓冲成功"≠"已出线"**：`Busy = FALSE` 只表示数据已交给发送缓冲，实际出线由后台按硬件节奏完成。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendData.TcPOU`](../examples/P_Demo_SendData.TcPOU)

```iecst
// 场景：发一段固定的二进制命令帧。
PROGRAM P_Demo_SendData
VAR
    fbSendData : SendData;
    bufTx      : ComBuffer;
    abyCmd     : ARRAY[0..3] OF BYTE := [16#02, 16#41, 16#42, 16#03]; // STX A B ETX
    bSendNow   : BOOL;
    bBusy      : BOOL;
END_VAR

IF bSendNow THEN
    fbSendData(
        pSendData := ADR(abyCmd),
        Length    := SIZEOF(abyCmd),
        TxBuffer  := bufTx,
        Busy      => bBusy
    );
END_IF
```

## 7. 业务场景与实际价值

- **场景**：发送结构化二进制报文，如 STX/ETX 包裹的协议帧、定长状态包、把一个 `STRUCT` 整体发给设备。
- **价值**：一次调用给地址 + 长度即可发任意类型的数据块，免去逐字节循环和环形缓冲操作。
- **替代方案对比**：单字节用 `SendByte`；纯文本字符串用 `SendString`（直接传 `STRING`，无需指针）；二进制 / 任意结构体用 `SendData` 最合适。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85892107.html
- **相关**：`ReceiveData`（成帧接收）、`SendString`（字符串发送）、`SendByte`（单字节）、`SerialLineControl`（消费 `TxBuffer`）、`ComBuffer`、`ComError_t`
