# KL6WriteRegisters

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85902731.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_KL6WriteRegisters.TcPOU`](../examples/P_Demo_KL6WriteRegisters.TcPOU) |

---

## 1. 功能简述

向 KL6xxx 串口总线端子的一个或多个寄存器写入数据。触发前须在寄存器列表（`ComRegisterData_t` 数组）里填好要写的寄存器号（`Register` 字段）和内容（`Value` 字段）。`Execute` 上升沿触发一次写入。常用于对端子做超出 `KL6Configuration` 标准参数范围的高级配置。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  Execute          : BOOL;
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
| `Execute` | `BOOL` | — | 上升沿启动写入过程。触发前寄存器列表必须已初始化：寄存器号和内容都填好 |
| `Mode` | `ComSerialLineMode_t` | — | 明确指定所用串口硬件类型 |
| `pComIn` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输入变量的通用指针（`KL6inData` / `KL6inData5b` / `KL6inData22b` / `PcComInData`），用 `ADR()` 赋值 |
| `pComOut` | `POINTER TO BYTE` | — | 指向串口硬件过程数据输出变量的通用指针（`KL6outData` / `KL6outData5b` / `KL6outData22b` / `PcComOutData`），用 `ADR()` 赋值 |
| `SizeComIn` | `UINT` | — | 所用串口硬件输入过程映像的大小，用 `SIZEOF()` 赋值 |
| `pRegisterList` | `POINTER TO ARRAY[0..63] OF ComRegisterData_t` | — | 寄存器列表起始地址，用 `ADR(寄存器列表)` 取。触发前须填好寄存器号和内容 |
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
| `Done` | `BOOL` | 写入无错误完成时变 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后变 `TRUE`，写入进行期间保持 `TRUE` |
| `Error` | `BOOL` | 一旦发生错误变 `TRUE` |
| `ErrorID` | `ComError_t` | 出错时给出错误码 |

### VAR_IN_OUT

无（寄存器列表通过 `pRegisterList` 指针传入）。

## 3. 行为说明

标准 Execute / Busy / Done / Error 边沿触发状态机：`Execute` 上升沿启动一次寄存器写入，`Busy` 立刻变 `TRUE` 并在通过串口寄存器通信写端子期间保持；写入无错完成后 `Done = TRUE`、`Busy = FALSE`；出错则 `Error = TRUE`、`ErrorID` 给出错误码。与 `KL6ReadRegisters` 不同，写入**没有**连续 / 离散两种模式——所有要写的寄存器都必须在触发前逐项填入 `ComRegisterData_t` 列表：每项的 `Register` 字段填寄存器号、`Value` 字段填要写的 `WORD` 值。`Execute` 是边沿触发，再写前须先复位 `Execute`。寄存器号有效范围 1~64，列表最多 64 项。写寄存器是配置类动作，通常初始化阶段执行一次。

## 4. 错误码 / 返回值

错误标志为 `Error`（`BOOL`），错误码在 `ErrorID`（`ComError_t`）。常见取值：

| `ErrorID` | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | `Done` 同时为 `TRUE` |
| `COMERROR_INVALIDNUMREGISTERS` (16#1006) | 寄存器数量非法 | 列表项数应在 1~64 |
| `COMERROR_INVALIDREGISTER` (16#1007) | 寄存器号非法 | 列表里 `Register` 字段应在 1~64 |
| `COMERROR_TIMEOUT` (16#1008) | 寄存器通信超时 | 检查端子链接、Mode 与硬件是否匹配 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **触发前必须先填列表**：写之前要把每个要写的寄存器号（`Register`）和内容（`Value`）填进 `ComRegisterData_t` 列表项，否则会写错或写空。
- **没有连续写模式**：不像读可以给起始号 + 数量；写必须逐项在列表里指定寄存器号。
- **`Execute` 边沿触发**：写一次后须先复位 `Execute`。
- **写寄存器有风险**：写错寄存器可能让端子进入异常配置。仅在明确知道寄存器含义时操作，标准串口参数优先用 `KL6Configuration`（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_KL6WriteRegisters.TcPOU`](../examples/P_Demo_KL6WriteRegisters.TcPOU)

```iecst
// 场景：向 KL6031 端子寄存器 34 写入一个配置值（高级配置）。
PROGRAM P_Demo_KL6WriteRegisters
VAR
    fbKL6Write  : KL6WriteRegisters;
    arrComIn    : KL6inData5B;
    arrComOut   : KL6outData5B;
    aRegList    : ARRAY[0..63] OF ComRegisterData_t;
    bWriteNow   : BOOL;
    bDone       : BOOL;
END_VAR

// 触发前填好寄存器号和值
aRegList[0].Register := 34;
aRegList[0].Value    := 16#0002;

fbKL6Write(
    Execute          := bWriteNow,
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

- **场景**：对 KL6xxx 端子做高级配置，写入超出标准串口参数的特殊寄存器（如特定数据格式、特殊功能开关），或恢复 / 调整端子出厂设置。
- **价值**：一次调用把列表里的多个寄存器值写入端子，免去手工拼寄存器写命令。
- **替代方案对比**：标准串口参数（波特率 / 校验 / 停止位）用 `KL6Configuration` 更安全；只读寄存器用 `KL6ReadRegisters`；本功能块用于需要直接写端子寄存器的高级场景。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85902731.html
- **相关**：`KL6ReadRegisters`（读寄存器）、`KL6Configuration`（标准参数配置）、`ComRegisterData_t` / `ComRegisterList_t`（寄存器列表结构）、`ComError_t`
