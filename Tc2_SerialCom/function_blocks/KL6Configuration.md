# KL6Configuration

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85899659.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_KL6Configuration.TcPOU`](../examples/P_Demo_KL6Configuration.TcPOU) |

---

## 1. 功能简述

初始化并配置 KL6xxx 串口总线端子：设置波特率、数据位、校验、停止位、握手方式等串口参数。它使用 KL 端子的标准寄存器通信来完成配置。注意 EtherCAT 端子（EL）不支持这种寄存器通信，配置 EL 端子要用 EtherCAT 库的 `FB_EcCoeSdoWrite`。`Execute` 上升沿触发一次配置。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Execute         : BOOL;
  Mode            : ComSerialLineMode_t;
  Baudrate        : UDINT;
  NoDatabits      : BYTE;
  Parity          : ComParity_t;
  Stopbits        : BYTE;
  Handshake       : ComHandshake_t;
  ContinousMode   : BOOL;
  pComIn          : POINTER TO BYTE;
  pComOut         : POINTER TO BYTE;
  SizeComIn       : UINT
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次配置 |
| `Mode` | `ComSerialLineMode_t` | — | 明确指定所用串口硬件类型 |
| `Baudrate` | `UDINT` | — | 波特率（须硬件支持）：115200、57600、38400、19200、9600、4800、2400、1200 |
| `NoDatabits` | `BYTE` | — | 一个数据字节里的用户数据位数：7 或 8 |
| `Parity` | `ComParity_t` | — | 校验位类型：`PARITY_NONE`=0、`PARITY_EVEN`=1、`PARITY_ODD`=2 |
| `Stopbits` | `BYTE` | — | 每数据字节的停止位数：1 或 2 |
| `Handshake` | `ComHandshake_t` | — | 握手方式（须硬件支持）：`HANDSHAKE_NONE`=0、`HANDSHAKE_RTSCTS`=1、`HANDSHAKE_XONXOFF`=2 |
| `ContinousMode` | `BOOL` | — | 开启连续发送（须硬件支持）。为 `TRUE` 时数据要等硬件发送缓冲满才发出，从而避免传输中出现时间间隙；仅在对端对时间间隙敏感（会超时）的特殊场合需要 |
| `pComIn` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输入变量的通用指针（`KL6inData` / `KL6inData5b` / `KL6inData22b` / `PcComInData`），用 `ADR()` 赋值 |
| `pComOut` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输出变量的通用指针（`KL6outData` / `KL6outData5b` / `KL6outData22b` / `PcComOutData`），用 `ADR()` 赋值 |
| `SizeComIn` | `UINT` | — | 所用串口硬件输入过程映像的大小，用 `SIZEOF()` 赋值 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  Done       : BOOL;
  Busy       : BOOL;
  Error      : BOOL;
  ErrorID    : ComError_t;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 配置无错误完成时变 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后变 `TRUE`，配置进行期间保持 `TRUE` |
| `Error` | `BOOL` | 一旦发生错误变 `TRUE` |
| `ErrorID` | `ComError_t` | 出错时给出错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

标准 Execute / Busy / Done / Error 边沿触发状态机：`Execute` 上升沿启动一次配置，`Busy` 立刻变 `TRUE` 并在通过寄存器通信写入 KL6xxx 端子参数期间保持；配置无错完成后 `Done = TRUE`、`Busy = FALSE`；出错则 `Error = TRUE`、`ErrorID` 给出 `ComError_t` 错误码。配置过程是把波特率、数据位、校验、停止位、握手等参数通过 KL 端子标准寄存器通信写进端子。`Execute` 是边沿触发，重新配置前须先复位 `Execute`。典型用法是在 PLC 初始化阶段触发一次：配置完成（`Done = TRUE`）后，再由 `SerialLineControl` 接管周期性的后台收发。注意 `Baudrate`、`Stopbits` 等参数必须是硬件实际支持的值，否则返回对应的 `COMERROR_INVALID*` 错误码（如波特率非法报 `COMERROR_INVALIDBAUDRATE`）。本功能块仅适用于 KL6xxx 端子——EL6xxx EtherCAT 端子没有寄存器通信，须改用 EtherCAT 库的 `FB_EcCoeSdoWrite` 配置。

## 4. 错误码 / 返回值

错误标志为 `Error`（`BOOL`），错误码在 `ErrorID`（`ComError_t`）。常见取值：

| `ErrorID` | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | `Done` 同时为 `TRUE` |
| `COMERROR_INVALIDBAUDRATE` (16#1001) | 波特率非法 | 用硬件支持的标准波特率 |
| `COMERROR_INVALIDNUMDATABITS` (16#1002) | 数据位数非法 | `NoDatabits` 取 7 或 8 |
| `COMERROR_INVALIDNUMSTOPBITS` (16#1003) | 停止位数非法 | `Stopbits` 取 1 或 2 |
| `COMERROR_INVALIDPARITY` (16#1004) | 校验类型非法 | 用 `ComParity_t` 合法值 |
| `COMERROR_INVALIDHANDSHAKE` (16#1005) | 握手类型非法 | 用 `ComHandshake_t` 合法值 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **只用于 KL6xxx**：EL6xxx EtherCAT 端子不支持寄存器通信，配置要用 `FB_EcCoeSdoWrite`。
- **参数须硬件支持**：波特率 / 数据位 / 停止位 / 握手都必须是该端子支持的值，否则报 `COMERROR_INVALID*`。
- **`Execute` 边沿触发**：配置一次后须先复位 `Execute` 才能再触发。
- **配置先于通信**：通常初始化时配置一次（等 `Done`），再由 `SerialLineControl` 周期性收发。
- **`ContinousMode` 仅特殊场合用**：只有当对端用时间间隙判超时时才需要它，普通通信保持 `FALSE`（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_KL6Configuration.TcPOU`](../examples/P_Demo_KL6Configuration.TcPOU)

```iecst
// 场景：初始化 KL6031 端子为 9600-8-N-1、无握手。
PROGRAM P_Demo_KL6Configuration
VAR
    fbKL6Config : KL6Configuration;
    arrComIn    : KL6inData5B;
    arrComOut   : KL6outData5B;
    bConfigNow  : BOOL;
    bDone       : BOOL;
END_VAR

fbKL6Config(
    Execute       := bConfigNow,
    Mode          := ComSerialLineMode_t.SERIALLINEMODE_KL6_5B_STANDARD,
    Baudrate      := 9600,
    NoDatabits    := 8,
    Parity        := ComParity_t.PARITY_NONE,
    Stopbits      := 1,
    Handshake     := ComHandshake_t.HANDSHAKE_NONE,
    ContinousMode := FALSE,
    pComIn        := ADR(arrComIn),
    pComOut       := ADR(arrComOut),
    SizeComIn     := SIZEOF(arrComIn),
    Done          => bDone
);
```

## 7. 业务场景与实际价值

- **场景**：使用 KL6001 / KL6011 / KL6031 等串口总线端子的设备，PLC 上电时需把端子配置成与对端一致的串口参数（波特率、数据位、校验等）。
- **价值**：用一次调用把 KL6xxx 的全部串口参数通过寄存器通信写好，免去手工拼寄存器读写命令。
- **替代方案对比**：EL6xxx EtherCAT 端子用 `FB_EcCoeSdoWrite`（CoE 对象字典）；KL6xxx 用本功能块最直接。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85899659.html
- **相关**：`ComReset`（复位硬件）、`KL6ReadRegisters` / `KL6WriteRegisters`（读写寄存器）、`SerialLineControl`（后台通信）、`ComSerialLineMode_t` / `ComParity_t` / `ComHandshake_t`（参数枚举）、`ComError_t`
