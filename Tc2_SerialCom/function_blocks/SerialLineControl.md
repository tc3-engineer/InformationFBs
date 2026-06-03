# SerialLineControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85905675.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SerialLineControl.TcPOU`](../examples/P_Demo_SerialLineControl.TcPOU) |

---

## 1. 功能简述

负责串口硬件（KL60xx、EL60xx 或 PC COM 口）与 PLC 之间的底层收发，即"后台通信"。它必须每个 PLC 周期调用一次：把硬件收到的字节放进 `RxBuffer`，同时把 `TxBuffer` 里待发的字节发往硬件。由于它独立于应用逻辑运行，可以（尤其对串口总线端子）放在一个更快的任务里执行。它是 `SendByte` / `ReceiveByte` 等收发功能块与硬件之间的桥梁。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Mode             : ComSerialLineMode_t;
  pComIn           : POINTER TO BYTE;
  pComOut          : POINTER TO BYTE;
  SizeComIn        : INT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Mode` | `ComSerialLineMode_t` | — | 明确指定所用串口硬件类型 |
| `pComIn` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输入变量的通用指针（`PcComInData` / `EL6inData22b` / `KL6inData` / `KL6inData5b` / `KL6inData22b`），用 `ADR()` 赋值 |
| `pComOut` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输出变量的通用指针（`PcComOutData` / `EL6outData22b` / `KL6outData` / `KL6outData5b` / `KL6outData22b`），用 `ADR()` 赋值 |
| `SizeComIn` | `INT` | — | 所用串口硬件输入过程映像的大小，用 `SIZEOF()` 赋值 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  TxBuffer         : ComBuffer;
  RxBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TxBuffer` | `ComBuffer` | 与所用串口对应的发送缓冲区，由 `SendByte` / `SendData` / `SendString` 等填充 |
| `RxBuffer` | `ComBuffer` | 与所用串口对应的接收缓冲区，由 `ReceiveByte` / `ReceiveData` / `ReceiveString` 等读取 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  Error      : BOOL;
  ErrorID    : ComError_t;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Error` | `BOOL` | 一旦发生错误变 `TRUE` |
| `ErrorID` | `ComError_t` | 出错时给出错误码 |

## 3. 行为说明

电平驱动、每周期调用一次的后台通信功能块，没有 Execute / Done 状态：只要在循环执行的任务里被调用，它就持续在硬件过程映像与 `ComBuffer` 之间搬运字节。一个周期内它把硬件接收到的所有字节搬进 `RxBuffer`，把 `TxBuffer` 里待发的字节交给硬件发送缓冲。它本身只管"搬运"，成帧 / 解析交给上层的 `Receive*` / `Send*` 功能块。`SizeComIn` 这里是 `INT` 类型（注意与 `KL6Configuration` / `ComReset` 等用 `UINT` 的功能块不同）。典型架构是：把本功能块放在一个比较快的 PLC 任务（如串口总线端子用 1ms 任务）里每周期调用，应用层的收发功能块放标准任务；这样硬件层通信和业务逻辑解耦，互不拖慢。`TxBuffer` / `RxBuffer` 必须与对应的 `Send*` / `Receive*` 功能块共用同一实例，否则数据搬不通。`Error = TRUE` 时通过 `ErrorID`（`ComError_t`）查具体原因。对虚拟串口（USB 转串口）应改用 `SerialLineControlADS`。

## 4. 错误码 / 返回值

错误标志为 `Error`（`BOOL`），错误码在 `ErrorID`（`ComError_t`）。常见取值：

| `ErrorID` | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常运行 |
| `COMERROR_MODENOTSUPPORTED` (16#0101) | 模式不支持（如 3 字节端子接在总线控制器后） | 确认 `Mode` 与实际硬件、过程映像类型匹配 |
| `COMERROR_INVALIDPROCESSDATASIZE` (24) | 过程数据大小无效 | 检查 `SizeComIn` 是否用 `SIZEOF()` 取正确映像大小 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **必须每周期调用**：漏调会导致字节积压 / 丢失。建议放在循环执行的任务里。
- **`TxBuffer` / `RxBuffer` 共用实例**：收发功能块用的缓冲必须正是这里传入的两个实例。
- **`SizeComIn` 是 `INT`**：与 `KL6Configuration`、`ComReset` 等用 `UINT` 不同，赋值时类型注意。
- **快任务部署**：串口总线端子（KL6 / EL6）建议把本功能块放进 1ms 等快任务，避免标准任务周期慢导致硬件缓冲溢出（工程经验补充）。
- **虚拟串口用 ADS 版**：USB 转串口等虚拟 COM 口用 `SerialLineControlADS`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SerialLineControl.TcPOU`](../examples/P_Demo_SerialLineControl.TcPOU)

```iecst
// 场景：PC COM 口后台通信，每周期调用搬运字节。
PROGRAM P_Demo_SerialLineControl
VAR
    fbSerialLine : SerialLineControl;
    bufTx        : ComBuffer;
    bufRx        : ComBuffer;
    arrComIn     : PcComInData;
    arrComOut    : PcComOutData;
    bError       : BOOL;
END_VAR

fbSerialLine(
    Mode      := ComSerialLineMode_t.SERIALLINEMODE_PC_COM_PORT,
    pComIn    := ADR(arrComIn),
    pComOut   := ADR(arrComOut),
    SizeComIn := SIZEOF(arrComIn),
    TxBuffer  := bufTx,
    RxBuffer  := bufRx,
    Error     => bError
);
```

## 7. 业务场景与实际价值

- **场景**：任何使用 KL60xx / EL60xx 串口端子或 PC COM 口的串口通信工程，都需要本功能块作为硬件层的后台收发引擎。
- **价值**：把硬件过程映像与应用层缓冲解耦——业务代码只跟 `ComBuffer` 打交道，硬件细节（端子模式、过程映像格式）由本功能块统一处理，且可放快任务保证实时性。
- **替代方案对比**：虚拟串口（USB-COM）用 `SerialLineControlADS`（走 ADS 串口服务器）；物理串口 / 总线端子用本功能块直接走过程映像，效率更高。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85905675.html
- **相关**：`SerialLineControlADS`（虚拟串口版）、`SendByte` / `ReceiveByte` 等（消费 / 填充缓冲）、`ComReset`（复位硬件）、`ComSerialLineMode_t`、`ComError_t`
