# ComReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85898123.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ComReset.TcPOU`](../examples/P_Demo_ComReset.TcPOU) |

---

## 1. 功能简述

复位所连的串口硬件，清空硬件内部的发送和接收缓冲。支持多种串口硬件：PC 串口和 KL6xxx 串口端子。它通过 `pComIn` / `pComOut` 指向的过程映像与硬件交互，`Execute` 上升沿触发一次复位。注意它**不**清空 PLC 内部 `ComBuffer` 类型的软件缓冲——那要用 `ClearComBuffer`，初始化时通常两者都调。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Execute         : BOOL
  pComIn          : POINTER TO BYTE;
  pComOut         : POINTER TO BYTE;
  SizeComIn       : UINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次复位所连的串口硬件 |
| `pComIn` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输入变量的通用指针（类型 `KL6inData` / `KL6inData5b` / `PcComInData`），用 `ADR()` 赋值 |
| `pComOut` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输出变量的通用指针（类型 `KL6outData` / `KL6outData5b` / `PcComOutData`），用 `ADR()` 赋值 |
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
| `Done` | `BOOL` | 功能无错误执行完成时变 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后变 `TRUE`，功能块执行期间保持 `TRUE` |
| `Error` | `BOOL` | 一旦发生错误变 `TRUE` |
| `ErrorID` | `ComError_t` | 出错时给出错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

标准的 Execute / Busy / Done / Error 边沿触发状态机：`Execute` 上升沿启动一次复位，`Busy` 立刻变 `TRUE` 并在复位进行期间保持；复位无错完成后 `Done = TRUE`、`Busy = FALSE`；过程中出错则 `Error = TRUE`、`ErrorID` 给出 `ComError_t` 错误码、`Busy = FALSE`。`Execute` 是边沿触发——再次复位前必须先让 `Execute = FALSE` 再给上升沿。复位动作清的是**硬件**收发缓冲（如 KL6xxx 端子或 PC COM 口内部的缓存），把硬件恢复到干净状态；它不动 PLC 软件层的 `ComBuffer`。`pComIn` / `pComOut` 必须指向正确链接到该硬件的过程映像变量，且 `SizeComIn` 与所用硬件的输入映像大小一致，否则无法正确与硬件交互。注意本功能块的 `Error` 是 `BOOL`（是否出错的标志），具体错误码在 `ErrorID`（`ComError_t`）里——这与 SendByte/ReceiveByte 等把 `Error` 直接定义为 `ComError_t` 的功能块不同。

## 4. 错误码 / 返回值

错误标志为 `Error`（`BOOL`），错误码在 `ErrorID`（`ComError_t`）。常见取值：

| `ErrorID` | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | `Done` 会同时为 `TRUE` |
| `COMERROR_MODENOTSUPPORTED` (16#0101) | 模式不支持（如 3 字节端子接在总线控制器后） | 确认硬件类型与所用过程映像类型匹配 |
| `COMERROR_INVALIDPROCESSDATASIZE` (24) | 过程数据大小无效 | 检查 `SizeComIn` 是否用 `SIZEOF()` 取正确映像大小 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **不清 PLC 软件缓冲**：本功能块只复位硬件收发缓冲。要清 PLC 侧 `ComBuffer` 用 `ClearComBuffer`，初始化时两者都调。
- **`Execute` 边沿触发**：复位完一次后须先复位 `Execute` 才能再触发。
- **过程映像指针与大小要对**：`pComIn` / `pComOut` 指向真正链接到硬件的映像变量，`SizeComIn` 用 `SIZEOF()` 取，类型不匹配会报 `COMERROR_MODENOTSUPPORTED` 或大小错误。
- **复位会丢硬件缓冲里的在途数据**：通信中途复位会丢弃硬件缓存中尚未交付的字节，仅在初始化或错误恢复时用（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ComReset.TcPOU`](../examples/P_Demo_ComReset.TcPOU)

```iecst
// 场景：上电初始化时复位 PC 串口硬件，清干净硬件收发缓冲。
PROGRAM P_Demo_ComReset
VAR
    fbComReset : ComReset;
    arrComIn   : PcComInData;
    arrComOut  : PcComOutData;
    bDoReset   : BOOL;
    bDone      : BOOL;
    bBusy      : BOOL;
    bError     : BOOL;
END_VAR

fbComReset(
    Execute   := bDoReset,
    pComIn    := ADR(arrComIn),
    pComOut   := ADR(arrComOut),
    SizeComIn := SIZEOF(arrComIn),
    Done      => bDone,
    Busy      => bBusy,
    Error     => bError
);
```

## 7. 业务场景与实际价值

- **场景**：PLC 上电初始化串口、通信异常后恢复、切换通信参数前，需要把串口硬件缓冲清干净，避免硬件缓存里的旧字节干扰新通信。
- **价值**：一个 Execute 边沿即可复位多种串口硬件（PC COM / KL6xxx），统一了硬件复位接口。
- **替代方案对比**：只清 PLC 软件缓冲用 `ClearComBuffer`（更轻量、不动硬件）；本功能块用于真正需要复位硬件的场合，两者配合用于完整初始化。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85898123.html
- **相关**：`ClearComBuffer`（清 PLC 软件缓冲）、`KL6Configuration`（配置 KL6xxx 参数）、`SerialLineControl`（后台通信）、`ComError_t`
