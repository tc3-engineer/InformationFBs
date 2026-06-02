# KL6ReadRegisters

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85901195.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_KL6ReadRegisters.TcPOU`](../examples/P_Demo_KL6ReadRegisters.TcPOU) |

---

## 1. 功能简述

读取 KL6xxx 串口总线端子的一个或多个寄存器。可以读一段连续寄存器（从 `FirstRegister` 起读 `RegisterCount` 个），也可以读离散寄存器（`FirstRegister` 设为 `16#FFFF`，由用户在寄存器列表里预先填好要读的寄存器号）。结果存入 `pRegisterList` 指向的 `ComRegisterData_t` 数组。`Execute` 上升沿触发一次读取。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Execute          : BOOL;
  FirstRegister    : UINT;
  RegisterCount    : UINT;
  Mode             : ComSerialLineMode_t;
  pComIn           : POINTER TO BYTE;
  pComOut          : POINTER TO BYTE;
  SizeComIn        : UINT;
  pRegisterList    : POINTER TO ARRAY[0..63] OF ComRegisterData_t;
  SizeRegisterList : UINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动读取过程 |
| `FirstRegister` | `UINT` | — | 起始寄存器号（1~64），从此号起读 `RegisterCount` 个存入寄存器列表。若设为 `16#FFFF` 表示读离散寄存器，此时须预先在列表里填好寄存器号，`RegisterCount` 不再使用 |
| `RegisterCount` | `UINT` | — | 要读的寄存器数量，功能块从 `FirstRegister` 起读一段连续寄存器 |
| `Mode` | `ComSerialLineMode_t` | — | 明确指定所用串口硬件类型 |
| `pComIn` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输入变量的通用指针（`KL6inData` / `KL6inData5b` / `KL6inData22b` / `PcComInData`），用 `ADR()` 赋值 |
| `pComOut` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输出变量的通用指针（`KL6outData` / `KL6outData5b` / `KL6outData22b` / `PcComOutData`），用 `ADR()` 赋值 |
| `SizeComIn` | `UINT` | — | 所用串口硬件输入过程映像的大小，用 `SIZEOF()` 赋值 |
| `pRegisterList` | `POINTER TO ARRAY[0..63] OF ComRegisterData_t` | — | 寄存器列表起始地址，用 `ADR(寄存器列表)` 取 |
| `SizeRegisterList` | `UINT` | — | 寄存器列表字节大小，用 `SIZEOF(寄存器列表)` 取；列表 1~64 项 |

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
| `Done` | `BOOL` | 读取无错误完成时变 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后变 `TRUE`，读取进行期间保持 `TRUE` |
| `Error` | `BOOL` | 一旦发生错误变 `TRUE` |
| `ErrorID` | `ComError_t` | 出错时给出错误码 |

### VAR_IN_OUT

无（寄存器列表通过 `pRegisterList` 指针传入）。

## 3. 行为说明

标准 Execute / Busy / Done / Error 边沿触发状态机：`Execute` 上升沿启动一次寄存器读取，`Busy` 立刻变 `TRUE` 并在通过串口寄存器通信读端子期间保持；读取无错完成后 `Done = TRUE`、`Busy = FALSE`、结果已写入 `pRegisterList` 指向的数组；出错则 `Error = TRUE`、`ErrorID` 给出错误码。有两种读模式：连续读——`FirstRegister` 给起始号、`RegisterCount` 给数量，读一段连续寄存器；离散读——`FirstRegister` 设 `16#FFFF`，触发前先在 `ComRegisterData_t` 列表的各项里填好要读的寄存器号（`Register` 字段），功能块按列表逐个读，此时忽略 `RegisterCount`。读到的寄存器值写回列表项的 `Value` 字段（`WORD`）。`Execute` 是边沿触发，再读前须先复位 `Execute`。寄存器号有效范围 1~64，列表最多 64 项。

## 4. 错误码 / 返回值

错误标志为 `Error`（`BOOL`），错误码在 `ErrorID`（`ComError_t`）。常见取值：

| `ErrorID` | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | `Done` 同时为 `TRUE` |
| `COMERROR_INVALIDNUMREGISTERS` (16#1006) | 寄存器数量非法 | `RegisterCount` / 列表项数应在 1~64 |
| `COMERROR_INVALIDREGISTER` (16#1007) | 寄存器号非法 | 寄存器号应在 1~64 |
| `COMERROR_TIMEOUT` (16#1008) | 寄存器通信超时 | 检查端子链接、Mode 与硬件是否匹配 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **两种读模式别混**：连续读用 `FirstRegister` + `RegisterCount`；离散读把 `FirstRegister` 设 `16#FFFF` 并预填列表寄存器号。
- **列表大小要对**：`SizeRegisterList` 用 `SIZEOF()` 取；列表 1~64 项，超界报 `COMERROR_INVALIDNUMREGISTERS`。
- **`Execute` 边沿触发**：读一次后须先复位 `Execute`。
- **读寄存器是配置 / 诊断动作**：通常初始化或诊断时读，不在收发数据的热路径里反复调（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_KL6ReadRegisters.TcPOU`](../examples/P_Demo_KL6ReadRegisters.TcPOU)

```iecst
// 场景：读 KL6031 端子寄存器 0~7（连续读），用于诊断当前配置。
PROGRAM P_Demo_KL6ReadRegisters
VAR
    fbKL6Read   : KL6ReadRegisters;
    arrComIn    : KL6inData5B;
    arrComOut   : KL6outData5B;
    aRegList    : ARRAY[0..63] OF ComRegisterData_t;
    bReadNow    : BOOL;
    bDone       : BOOL;
END_VAR

fbKL6Read(
    Execute          := bReadNow,
    FirstRegister    := 0,
    RegisterCount    := 8,
    Mode             := ComSerialLineMode_t.SERIALLINEMODE_KL6_5B_STANDARD,
    pComIn           := ADR(arrComIn),
    pComOut          := ADR(arrComOut),
    SizeComIn        := SIZEOF(arrComIn),
    pRegisterList    := ADR(aRegList),
    SizeRegisterList := SIZEOF(aRegList),
    Done             => bDone
);
```

## 7. 业务场景与实际价值

- **场景**：读取 KL6xxx 端子的配置 / 状态寄存器，用于诊断当前波特率等参数、读取端子固件信息、排查通信故障。
- **价值**：一次调用读连续或离散寄存器并填入结构化列表，免去手工拼寄存器读命令、解析返回字节。
- **替代方案对比**：写寄存器用 `KL6WriteRegisters`；只改标准串口参数用 `KL6Configuration`（更高层）；本功能块用于需要直接访问端子寄存器的诊断 / 高级配置。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85901195.html
- **相关**：`KL6WriteRegisters`（写寄存器）、`KL6Configuration`（标准参数配置）、`ComRegisterData_t` / `ComRegisterList_t`（寄存器列表结构）、`ComError_t`
