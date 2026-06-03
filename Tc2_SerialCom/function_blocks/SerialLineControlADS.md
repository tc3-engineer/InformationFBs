# SerialLineControlADS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85907211.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SerialLineControlADS.TcPOU`](../examples/P_Demo_SerialLineControlADS.TcPOU) |

---

## 1. 功能简述

负责虚拟串口（如 USB 转串口）与 PLC 之间的后台收发，通过 TwinCAT ADS 串口服务器（TcAdsSerialCommServer）访问 COM 口。它每个 PLC 周期调用一次：把收到的字节放进 `RxBuffer`，把 `TxBuffer` 里待发的字节发出。`Connect = TRUE` 时按 `SerialCfg` 参数自动打开指定 COM 口；该口随即被独占，`Connect = FALSE` 则关闭释放。与 `SerialLineControl` 不同，它一般可放在标准任务里，无需单独的快任务。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Connect    : BOOL;   (* connect to serial port [TRUE=connect, FALSE=disconnect] *)
  SerialCfg  : ComSerialConfig;
  NetId      : T_AmsNetId := '';            (* host NetId *)
  Timeout    : TIME := DEFAULT_ADS_TIMEOUT; (* Timeout for ADS calls *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Connect` | `BOOL` | — | `TRUE` 建立到串口的连接、打开端口；`FALSE` 关闭已打开的端口。⚠️ 改变此输入后最多需 6 倍 `Timeout` 时间才完全执行完，应用必须监视 `PortOpened` 等到目标状态 |
| `SerialCfg` | `ComSerialConfig` | — | 输入结构，定义用哪个 COM 口、以什么参数打开（见 §5 结构说明） |
| `NetId` | `T_AmsNetId` | `''` | 目标 TwinCAT 设备的 AMS Net ID；本机执行可不填或填空串 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 功能块执行的最大时长，默认 5 秒（建议至少 1000 ms） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  TxBuffer         : ComBuffer;
  RxBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TxBuffer` | `ComBuffer` | 待发数据缓冲区，由 `SendByte` / `SendData` / `SendString` 等填充 |
| `RxBuffer` | `ComBuffer` | 接收数据缓冲区，由 `ReceiveByte` / `ReceiveData` / `ReceiveString` 等读取 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  PortOpened : BOOL;   (* Indicates if selected serial port is opened *)
  Error      : BOOL;   (* 'TRUE' if an error occurred *)
  ErrorID    : UDINT;  (* Displays the error code; 0 = no error *)
  Busy       : BOOL;   (* 'TRUE' if internal ADS communication is busy *)
  TxBufCount : UDINT;  (* number of bytes in internal Tx buffer *)
  RxBufCount : UDINT;  (* number of bytes in internal Rx buffer *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `PortOpened` | `BOOL` | 指示所选串口是否已打开并链接 |
| `Error` | `BOOL` | 一旦发生错误变 `TRUE` |
| `ErrorID` | `UDINT` | 错误码，0 表示无错误（取值范围见 §4） |
| `Busy` | `BOOL` | 内部 ADS 通信进行中为 `TRUE` |
| `TxBufCount` | `UDINT` | 内部发送缓冲区中的字节数 |
| `RxBufCount` | `UDINT` | 内部接收缓冲区中的字节数 |

## 3. 行为说明

电平驱动、每周期调用的后台通信功能块，通过 ADS 与 TcAdsSerialCommServer 交互来打开 / 读 / 写 / 关闭 COM 口。`Connect = TRUE` 时按 `SerialCfg` 自动打开端口，端口随即被本应用独占（其他程序无法访问）；`Connect = FALSE` 时关闭端口、释放给其他程序。若在循环调用中改变了 `SerialCfg` 的参数（如换 COM 口号或波特率），旧端口会自动关闭、按新参数重开，无需先手动置 `Connect = FALSE`。关键时序陷阱：改变 `Connect` 后动作不是立即完成——最多要 6 倍 `Timeout` 的时间，因此应用必须监视 `PortOpened` 输出、等它达到期望状态再继续，不能假设改完立刻生效。`PortOpened = TRUE` 表示端口已打开可收发。`Busy` 表示内部 ADS 通信正忙。`TxBufCount` / `RxBufCount` 反映服务器内部缓冲的字节数——稳定通信时 `RxBufCount` 通常不超过 1000，持续上升说明 PLC 侧读取太慢、接收数据在积压。注意本功能块的 `ErrorID` 是 `UDINT`（不是 `ComError_t`），错误码按 ADS / 服务器 / Win32 / Linux 几段范围划分（见 §4）。

## 4. 错误码 / 返回值

`Error`（`BOOL`）置位时，`ErrorID`（`UDINT`）给出错误码。按偏移 + 范围分段（PDF 第 7.3 节）：

| 偏移 + 范围（hex） | 来源 | 含义 |
|---|---|---|
| `0x00000000`–`0x00007800` | TwinCAT 系统错误（含 ADS 错误码） | 例 `0x06` 找不到目标端口（ADS 服务器未启动）；ADS 返回码列于 PDF 第 7.6 节 |
| `0x00009000`–`0x000091FF` | TcAdsSerialCommServer 错误 | 服务器内部错误，常见值见下表 |
| `0x3D090000`–`0x3D09FFFF` | Win32 系统错误 | 真值 = `ErrorID − 0x3D090000`，Win32 错误码列于 PDF 第 7.7 节 |
| `0x7A120000`–`0x7A12FFFF` | FreeBSD® / Linux® 系统错误 | TwinCAT/BSD 与 RT Linux 平台 |

TcAdsSerialCommServer 常见错误（节选）：

| `ErrorID` (hex) | 符号 | 含义 / 处理 |
|---|---|---|
| `0x00009001` | `COMERRORADS_INVALID_COMPORT` | COM 口号无效（有效 1~255）；检查 `SerialCfg.ComPort` |
| `0x00009021` | `COMERRORADS_INVALID_BAUDRATE` | 波特率不支持 |
| `0x00009032` | `COMERRORADS_RD_BUFFER_OVERRUN` | 接收缓冲溢出、数据丢失；PLC 必须及时读取，监视 `RxBufCount` 不应持续 > 1000 |
| `0x00009033` | `COMERRORADS_PORT_CONNECTED` | COM 口已打开；功能块会自动关闭重开，后续 `PortOpened = TRUE` 即成功 |
| `0x00009037` | `COMERRORADS_RD_FAILURE` | 读错误（如 USB 设备被拔出）；拔 USB 前应先把 `Connect` 置 FALSE |
| `0x3D090002` | `ERROR_FILE_NOT_FOUND` | 找不到指定 COM 口；检查 `ComPort` 与参数 |
| `0x3D090005` | `ERROR_ACCESS_DENIED` | 端口已被其他程序占用；先释放该端口 |

完整列表见 PDF 第 7.3 节及 `ComSerialConfig` 的 `TraceLevel` 调试说明。

## 5. 使用注意 / 常见坑

- **改 `Connect` 不会立刻生效**：最多需 6 倍 `Timeout`。必须等 `PortOpened` 变到期望状态，不能假设改完即生效。
- **端口独占**：`Connect = TRUE` 后该 COM 口被独占；`Access denied`（`0x3D090005`）说明被别的程序占用。
- **监视 `RxBufCount`**：持续上升说明 PLC 读取太慢，会触发 `RD_BUFFER_OVERRUN`（`0x00009032`）丢数据。
- **拔 USB 前先断开**：USB 转串口设备拔出前先把 `Connect` 置 FALSE，否则报 `RD_FAILURE`（`0x00009037`）。
- **依赖 ADS 服务器**：需要目标系统装有 TwinCAT（含 ADS 串口服务器）；找不到端口报 ADS 错误 `0x06`。
- **`SerialCfg` 结构**：`ComPort`（1~255 或 ttyU* / ttyUSB* 设备名）、`Baudrate`（默认 9600）、`Parity`、`DataBits`（4~8，默认 8）、`StopBits`、`DTR` / `RTS` 握手控制、`CTS` / `DSR` 流控、`TraceLevel`（调试级别 0~5）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SerialLineControlADS.TcPOU`](../examples/P_Demo_SerialLineControlADS.TcPOU)

```iecst
// 场景：打开本机 COM3（USB 转串口）做后台通信。
PROGRAM P_Demo_SerialLineControlADS
VAR
    fbSerialLineADS : SerialLineControlADS;
    bufTx           : ComBuffer;
    bufRx           : ComBuffer;
    stCfg           : ComSerialConfig := (ComPort := 3, Baudrate := 9600);
    bConnect        : BOOL;
    bPortOpened     : BOOL;
END_VAR

fbSerialLineADS(
    Connect    := bConnect,
    SerialCfg  := stCfg,
    NetId      := '',
    Timeout    := DEFAULT_ADS_TIMEOUT,
    TxBuffer   := bufTx,
    RxBuffer   := bufRx,
    PortOpened => bPortOpened
);
```

## 7. 业务场景与实际价值

- **场景**：与通过 USB 转串口、虚拟 COM 口接入的设备通信（如 USB-RS232 适配器、USB 仪表、micro:bit 等）。这类端口不在 EtherCAT / KL 总线上，无法用 `SerialLineControl`。
- **价值**：把"通过 ADS 串口服务器打开 / 收发 / 关闭虚拟 COM 口"封装为一个每周期调用的功能块，且能放标准任务、运行时换口换参数自动重连。
- **替代方案对比**：物理串口 / 总线端子（KL6 / EL6）用 `SerialLineControl` 直接走过程映像，更高效、实时性更好；虚拟串口只能用本功能块（走 ADS 服务器）。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.3.2、§7.3（错误码）、§5.3.1.3（`ComSerialConfig`）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85907211.html
- **相关**：`SerialLineControl`（物理串口版）、`SerialLineControlADSErr_TO_TcEventEntry`（错误码转事件）、`SendByte` / `ReceiveByte` 等、`ComSerialConfig`（配置结构）、`T_AmsNetId`
