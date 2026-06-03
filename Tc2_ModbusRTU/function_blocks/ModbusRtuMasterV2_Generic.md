# ModbusRtuMasterV2_Generic

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/14013447179.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ModbusRtuMasterV2_Generic.TcPOU`](../examples/P_Demo_ModbusRtuMasterV2_Generic.TcPOU) |

---

## 1. 功能简述

硬件无关的 Modbus RTU 主站功能块（Modbus master），可经各种串行接口通讯（COM 口、虚拟 COM 口、EtherCAT 端子等）。由于它与硬件解耦，用法比硬件相关的 `ModbusRtuMasterV2_PcCOM` / `ModbusRtuMasterV2_KL6x22B` / `ModbusRtuMasterV2_KL6x5B` 稍复杂；所有这些 FB 提供完全相同的 Modbus RTU 功能，但**只有 `ModbusRtuMasterV2_Generic` 支持虚拟 COM 口**。

与硬件的连接需经 TF6340 TwinCAT 3 Serial Communication（需 license）：链接通讯口所需的数据结构必须单独实例化。本 FB 上的 `ComBuffer` 型数据结构是用于解耦后台硬件通讯的数据缓冲；后台通讯须用 `Tc2_SerialCom` 库的相应功能块（`SerialLineControl`、`SerialLineControlADS`）实现，因此工程里必须先引入 `Tc2_SerialCom` 库，并具备 TF6340 license。与其他主站一样，本 FB 不以基本形式直接调用，而是调用其动作（`ReadRegs` 等），`V2` 版额外提供功能码 23（`ReadWriteRegs`）和用户自定义报文（`UserReadWrite`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    UnitID      : BYTE;
    Quantity    : WORD;
    MBAddr      : WORD;
    cbLength    : UINT;
    pMemoryAddr : POINTER TO BYTE;
    AuxQuantity    : WORD;
    AuxMBAddr      : WORD;
    AuxcbLength    : UINT;
    pAuxMemoryAddr : POINTER TO BYTE;
    Execute     : BOOL;
    Timeout     : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `UnitID` | `BYTE` | — | Modbus 从站站地址（1..247）。从站只应答含自身站地址的报文；地址 0 保留给广播。取值集合见 `MODBUS_UNITID`。⚠️ 见 §9：声明 `BYTE`，参数表写 `UINT` |
| `Quantity` | `WORD` | — | 字操作功能码要读/写的数据字数；位操作功能码时表示位数 |
| `MBAddr` | `WORD` | — | Modbus 数据地址，原样发给从站并在从站侧解释为数据地址。诊断功能码 8 时这里传子功能码 |
| `cbLength` | `UINT` | — | 发送/读取数据变量的字节大小，须 ≥ `Quantity*2`（字访问）。可用 `SIZEOF()` 计算 |
| `pMemoryAddr` | `POINTER TO BYTE` | — | PLC 数据缓冲区起始地址，用 `ADR()` 取。读动作落数据、写动作取数据 |
| `AuxQuantity` | `WORD` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助参数 |
| `AuxMBAddr` | `WORD` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助参数 |
| `AuxcbLength` | `UINT` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助参数 |
| `pAuxMemoryAddr` | `POINTER TO BYTE` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助缓冲区地址 |
| `Execute` | `BOOL` | — | 启动信号。上升沿触发一次动作 |
| `Timeout` | `TIME` | — | 等待从站应答的超时时间 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY    : BOOL;
    Error   : BOOL;
    ErrorId : MODBUS_ERRORS;
    cbRead  : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 功能块正在执行。`Execute` 上升沿置 `TRUE`，动作完成后落回 `FALSE`。同一时刻只能有一个动作活动 |
| `Error` | `BOOL` | 动作执行期间发生错误 |
| `ErrorId` | `MODBUS_ERRORS` | 通讯受扰或出错时的错误号（见 §4） |
| `cbRead` | `UINT` | 读动作已读回的数据字节数 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    RxBuffer    : ComBuffer;
    TxBuffer    : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `RxBuffer` | `ComBuffer`（`Tc2_SerialCom` 库） | 接收数据存放缓冲。用户从不直接读写它，它只作为通讯块之间的缓冲；后台通讯须用 `Tc2_SerialCom` 库的相应功能块实现 |
| `TxBuffer` | `ComBuffer`（`Tc2_SerialCom` 库） | 发往所用串行硬件的发送数据缓冲。用户从不直接读写它，仅作通讯块缓冲；后台通讯须用 `Tc2_SerialCom` 库的相应功能块实现 |

## 3. 行为说明

**调用方式**：调用动作而非 FB 本体，例如 `fbMaster.ReadRegs(...)`，并在动作调用里同时把 `RxBuffer` / `TxBuffer` 作为 in-out 传入。所有动作共用同一组引脚，`BUSY` 互锁保证一个实例同一时刻只跑一个动作。

**与硬件相关 FB 的关键区别**：本 FB 自己不碰硬件，它只把要发的 Modbus 帧塞进 `TxBuffer`、从 `RxBuffer` 取应答帧。真正把字节推到物理线路上、再把收到的字节放回缓冲，是由 `Tc2_SerialCom` 的 `SerialLineControl` / `SerialLineControlADS` 在后台周期执行的。因此工程结构是：每周期调一次串口通讯块（搬运 `RxBuffer`/`TxBuffer` 与物理口之间的字节）+ 按需调本 FB 的动作（组帧/解析）。这套解耦使得本 FB 能挂在任何 `Tc2_SerialCom` 支持的接口上，包括虚拟 COM 口。

**支持的功能码（动作）**：

| 动作 | 功能码 | 含义 |
|---|---|---|
| `ModbusMaster.ReadCoils` | 1 | 读线圈（压缩格式存入 `pMemoryAddr`） |
| `ModbusMaster.ReadInputStatus` | 2 | 读二进制输入（压缩格式） |
| `ModbusMaster.ReadRegs` | 3 | 读保持寄存器 |
| `ModbusMaster.ReadInputRegs` | 4 | 读输入寄存器 |
| `ModbusMaster.WriteSingleCoil` | 5 | 写单个线圈 |
| `ModbusMaster.WriteSingleRegister` | 6 | 写单个寄存器 |
| `ModbusMaster.WriteMultipleCoils` | 15 | 写多个线圈 |
| `ModbusMaster.WriteRegs` | 16 | 写多个寄存器 |
| `ModbusMaster.Diagnostics` | 8 | 诊断（子功能码经 `MBAddr` 传） |
| `ModbusMaster.ReadWriteRegs` | 23 | 读写组合（仅 V2，用 `Aux*` 参数） |
| `ModbusMaster.UserReadWrite` | 用户自定义 | 任意功能码报文（仅 V2） |

**时序状态机**：`Execute` 上升沿 → `BUSY := TRUE` → 把 Modbus 帧写入 `TxBuffer` → 由后台串口块发出 → 从 `RxBuffer` 取应答或 `Timeout` 计时到 → 成功则 `BUSY := FALSE`、`Error := FALSE`、读动作落数据并给 `cbRead`；失败则 `Error := TRUE`、`ErrorId` 给错误号。仅上升沿触发，`BUSY = TRUE` 期间须每周期继续调用动作并保持 `pMemoryAddr` 缓冲区不变。

**典型陷阱**：忘记每周期调用 `Tc2_SerialCom` 的串口通讯块 → 帧永远发不出去/收不回来，本 FB 一直 `BUSY` 直到 `Timeout` 报错；`RxBuffer`/`TxBuffer` 必须是稳定的实例（声明在程序里，跨周期同一份）而不能临时构造；未装 TF6340 license → 后台通讯块无法运行。

## 4. 错误码 / 返回值

错误经 `Error` + `ErrorId : MODBUS_ERRORS` 输出。`MODBUS_ERRORS` 枚举（PDF §5.2.2）分三段：

**Modbus 标准异常码**：

| 枚举 | 值 | 含义 |
|---|---|---|
| `MODBUSERROR_NO_ERROR` | 0 | 无错误 |
| `MODBUSERROR_ILLEGAL_FUNCTION` | 1 | 不支持的功能码 |
| `MODBUSERROR_ILLEGAL_DATA_ADDRESS` | 2 | 数据地址非法 |
| `MODBUSERROR_ILLEGAL_DATA_VALUE` | 3 | 数据值非法 |
| `MODBUSERROR_SLAVE_DEVICE_FAILURE` | 4 | 从站设备故障 |
| `MODBUSERROR_ACKNOWLEDGE` | 5 | 从站已受理 |
| `MODBUSERROR_SLAVE_DEVICE_BUSY` | 6 | 从站忙 |
| `MODBUSERROR_NEGATIVE_ACKNOWLEDGE` | 7 | 否定应答 |
| `MODBUSERROR_MEMORY_PARITY` | 8 | 存储器奇偶校验错 |
| `MODBUSERROR_GATEWAY_PATH_UNAVAILABLE` | 16#A | 网关路径不可用 |
| `MODBUSERROR_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND` | 16#B | 网关目标设备无应答 |

**库追加 + 底层 + 高层错误**：

| 枚举 | 值 | 含义 |
|---|---|---|
| `MODBUSERROR_CHARREC_TIMEOUT` | 16#20 | 字符接收超时 |
| `MODBUSERROR_ILLEGAL_DATA_SIZE` | 16#21 | 数据大小非法（多为 `cbLength` 不足） |
| `MODBUSERROR_ILLEGAL_DEVICE_ADDRESS` | 16#22 | 设备地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_ADDRESS` | 16#23 | 目标地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_SIZE` | 16#24 | 目标大小非法 |
| `MODBUSERROR_NO_RESPONSE` | 16#25 | 从站无应答 |
| `MODBUSERROR_TXBUFFOVERRUN` | 102 | 发送缓冲区溢出 |
| `MODBUSERROR_SENDTIMEOUT` | 103 | 发送超时 |
| `MODBUSERROR_DATASIZEOVERRUN` | 107 | 数据大小溢出 |
| `MODBUSERROR_STRINGOVERRUN` | 110 | 字符串溢出 |
| `MODBUSERROR_INVALIDPOINTER` | 120 | 指针无效 |
| `MODBUSERROR_CRC` | 150 | CRC 校验错 |
| `MODBUSERROR_INVALIDMEMORYADDRESS` | 232 | 内存地址无效 |
| `MODBUSERROR_TRANSMITBUFFERTOOSMALL` | 233 | 发送缓冲区过小 |

## 5. 使用注意 / 常见坑

- **必须配 `Tc2_SerialCom` + TF6340**：本 FB 只组帧/解析，物理收发靠 `Tc2_SerialCom` 的 `SerialLineControl(ADS)` 后台块，且需 TF6340 license。这是它与三款硬件相关主站 FB 最大的不同。
- **每周期都要调串口块**：通讯块负责把 `TxBuffer`/`RxBuffer` 与物理口之间搬字节；漏调会让本 FB 一直 `BUSY` 到超时。
- **`RxBuffer`/`TxBuffer` 实例稳定**：作为 `VAR_IN_OUT` 传入，须是跨周期保持的同一份实例。
- **唯一支持虚拟 COM 口**：要走虚拟串口（如经 USB 转串口的虚拟口、或软件虚拟串口对）只能用本 FB。
- **`UnitID` 类型不一致**：声明 `BYTE`、参数表 `UINT`。`BYTE`（0..255）够覆盖站地址 1..247，集合地址（256..258）超出范围。详见 §9。
- **要求 Tc2_ModbusRTU >= v3.5.6.0、TwinCAT v3.1.4024.0**：Generic 系列比硬件相关 FB 的版本要求更高（PDF Requirements 表）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ModbusRtuMasterV2_Generic.TcPOU`](../examples/P_Demo_ModbusRtuMasterV2_Generic.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：经虚拟 COM 口（由 Tc2_SerialCom 后台块驱动）读站地址 1 从站的 4 个寄存器。
PROGRAM P_Demo_ModbusRtuMasterV2_Generic
VAR
    fbModbusMaster : ModbusRtuMasterV2_Generic;
    stRxBuffer     : ComBuffer;                      // Tc2_SerialCom 收发缓冲
    stTxBuffer     : ComBuffer;
    aSensorRegs    : ARRAY[0..3] OF WORD;
    bReadReq       : BOOL;
    bBusy          : BOOL;
    bError         : BOOL;
    eErrId         : MODBUS_ERRORS;
    nBytesRead     : UINT;
END_VAR

// 注意：实际工程里还须每周期调用 Tc2_SerialCom 的 SerialLineControl(ADS) 块，
//       让它在 stRxBuffer/stTxBuffer 与物理串口之间搬运字节。这里只演示主站动作。
fbModbusMaster.ReadRegs(
    UnitID      := 1,
    Quantity    := 4,
    MBAddr      := 16#0000,
    cbLength    := SIZEOF(aSensorRegs),
    pMemoryAddr := ADR(aSensorRegs),
    Execute     := bReadReq,
    Timeout     := T#1S,
    RxBuffer    := stRxBuffer,
    TxBuffer    := stTxBuffer,
    BUSY        => bBusy,
    Error       => bError,
    ErrorId     => eErrId,
    cbRead      => nBytesRead
);
```

## 7. 业务场景与实际价值

- **场景**：需要走**虚拟 COM 口**或非标准串行接口做 Modbus RTU 主站——例如经 USB 转串口适配器、软件虚拟串口对、或不在 KL6x/PC COM 标准型号里的串行硬件。
- **价值**：把硬件后端从 FB 里彻底解耦，给最大灵活性；只要 `Tc2_SerialCom` 能驱动的串口，本 FB 都能挂上去做 Modbus RTU 主站。
- **替代方案对比**：
  - `ModbusRtuMasterV2_PcCOM` / `_KL6x22B` / `_KL6x5B`：硬件相关、用法更简单（串口数据结构内置），但只支持各自固定的硬件，且不支持虚拟 COM 口。
  - **本 FB**：硬件无关、支持虚拟 COM 口，代价是必须额外引入 `Tc2_SerialCom`、加 TF6340 license、每周期跑后台串口块。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/14013447179.html
- **相关 FB / 枚举**：`ModbusRtuMasterV2_PcCOM` / `ModbusRtuMasterV2_KL6x22B` / `ModbusRtuMasterV2_KL6x5B`（硬件相关同类）、`ModbusRtuSlave_Generic`（从站对端）、`ComBuffer`（`Tc2_SerialCom`）、`MODBUS_ERRORS`、`MODBUS_UNITID`

## 9. 待确认项 (⚠️)

- `UnitID` 类型：PDF 与 InfoSys 的 VAR_INPUT 声明块均写 `UnitID : BYTE;`，参数说明表「Type」列均写 `UINT`。本文档逐字搬运声明块（`BYTE`）。
- InfoSys 的结构化解析把 `RxBuffer`/`TxBuffer` 归到了 inputs 区，而 PDF 明确它们位于 `VAR_IN_OUT`；本文档以 PDF 的 `VAR_IN_OUT` 划分为准（两源在变量名/类型 `ComBuffer` 上一致）。
