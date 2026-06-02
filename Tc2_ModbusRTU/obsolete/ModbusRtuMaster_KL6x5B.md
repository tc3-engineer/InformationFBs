# ModbusRtuMaster_KL6x5B

> ⚠️ **本功能块已废弃（[obsolete]，PDF §5.1.1）**。新工程请用 `ModbusRtuMasterV2_KL6x5B`（带功能码 23 `ReadWriteRegs` 与用户自定义报文 `UserReadWrite`）。本文档用于维护存量老程序。

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186539275.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ModbusRtuMaster_KL6x5B.TcPOU`](../examples/P_Demo_ModbusRtuMaster_KL6x5B.TcPOU) |

---

## 1. 功能简述

通过串行总线端子 KL6001、KL6011 或 KL6021 通讯的 Modbus RTU 主站功能块（Modbus master）的**旧版本**。它让 TwinCAT 控制器作为主站，主动向总线上的 Modbus 从站发起读写请求。功能与新版 `ModbusRtuMasterV2_KL6x5B` 类似，但**不含**功能码 23（`ReadWriteRegs`）和用户自定义报文（`UserReadWrite`），因此没有 `Aux*` 一组辅助参数。

本功能块**不以基本形式直接调用**，而是把每个 Modbus 功能码实现成一个**动作（Action）**。与端子的链接所需数据结构内置在 FB 中，分配方式与 TF6340 TwinCAT 3 Serial Communication 文档「Serial bus terminal」章节一致（经 PC 串口通讯请用旧版 `ModbusRtuMaster_PcCOM`；22 字节过程映像端子 KL6031/6041 用旧版 `ModbusRtuMaster_KL6x22B`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    UnitID      : UINT;
    Quantity    : WORD;
    MBAddr      : WORD;
    cbLength    : UINT;
    pMemoryAddr : POINTER TO BYTE;
    Execute     : BOOL;
    Timeout     : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `UnitID` | `UINT` | — | Modbus 从站站地址（1..247）。从站只应答含自身站地址的报文；可选用集合地址（256/257/258，见 `MODBUS_UNITID`）；地址 0 保留给广播 |
| `Quantity` | `WORD` | — | 字操作功能码要读/写的数据字数；位操作功能码时表示位数 |
| `MBAddr` | `WORD` | — | Modbus 数据地址，原样发给从站。诊断功能码 8 时这里传子功能码 |
| `cbLength` | `UINT` | — | 发送/读取数据变量的字节大小，须 ≥ `Quantity*2`（字访问）。可用 `SIZEOF()` 计算 |
| `pMemoryAddr` | `POINTER TO BYTE` | — | PLC 数据缓冲区起始地址，用 `ADR()` 取。读动作落数据、写动作取数据 |
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

无。

## 3. 行为说明

**调用方式**：调用动作而非 FB 本体，例如 `fbMaster.ReadRegs(...)`。所有动作共用同一组引脚，`BUSY` 互锁保证一个实例同一时刻只跑一个动作。

**支持的功能码（动作）**（旧版只有基础 9 个，无 `ReadWriteRegs`/`UserReadWrite`）：

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

**时序状态机**：`Execute` 上升沿触发一次动作 → `BUSY := TRUE` → 经 KL6x 端子组帧发出请求 → 等应答或 `Timeout` → 成功则 `BUSY := FALSE`、`Error := FALSE`、读动作落数据并给 `cbRead`；失败则 `Error := TRUE`、`ErrorId` 给错误号。仅上升沿触发，电平 `TRUE` 不重发；`BUSY = TRUE` 期间须每周期继续调用并保持 `pMemoryAddr` 缓冲区不变。

**与新版的差异**：旧版 `UnitID` 是 `UINT`（新版 V2 的 VAR 块是 `BYTE`），可直接送集合地址；旧版缺功能码 23 和用户自定义报文，需要时必须升级到 V2。

**典型陷阱**：端子波特率/校验位与从站不符 → `MODBUSERROR_CRC`/`NO_RESPONSE`；`cbLength` 不足 → `MODBUSERROR_ILLEGAL_DATA_SIZE`；`BUSY` 期间改缓冲 → 发出错乱数据。

## 4. 错误码 / 返回值

错误经 `Error` + `ErrorId : MODBUS_ERRORS` 输出。`MODBUS_ERRORS` 枚举（PDF §5.2.2）：

| 枚举 | 值 | 含义 |
|---|---|---|
| `MODBUSERROR_NO_ERROR` | 0 | 无错误 |
| `MODBUSERROR_ILLEGAL_FUNCTION` | 1 | 从站不支持该功能码 |
| `MODBUSERROR_ILLEGAL_DATA_ADDRESS` | 2 | 数据地址非法 |
| `MODBUSERROR_ILLEGAL_DATA_VALUE` | 3 | 数据值非法 |
| `MODBUSERROR_SLAVE_DEVICE_FAILURE` | 4 | 从站设备故障 |
| `MODBUSERROR_ACKNOWLEDGE` | 5 | 从站已受理 |
| `MODBUSERROR_SLAVE_DEVICE_BUSY` | 6 | 从站忙 |
| `MODBUSERROR_NEGATIVE_ACKNOWLEDGE` | 7 | 否定应答 |
| `MODBUSERROR_MEMORY_PARITY` | 8 | 存储器奇偶校验错 |
| `MODBUSERROR_GATEWAY_PATH_UNAVAILABLE` | 16#A | 网关路径不可用 |
| `MODBUSERROR_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND` | 16#B | 网关目标设备无应答 |
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

- **已废弃，优先升级**：新工程用 `ModbusRtuMasterV2_KL6x5B`。本 FB 仅为兼容老程序保留。
- **`UnitID` 是 `UINT`**：可直接送集合地址 256/257/258。
- **端子组态**：KL6001/6011/6021 串口参数用 KS2000 或 `Tc2_SerialCom` 的 `KL6configuration` 块设，波特率/校验位与从站一致。
- **`cbLength >= Quantity*2`**：字访问不足报 `MODBUSERROR_ILLEGAL_DATA_SIZE`。
- **缓冲区生命期**：`BUSY = TRUE` 期间不要改 `pMemoryAddr` 指向的变量。
- **端子选型**：3 字节过程映像端子（KL6001/6011/6021）用本 FB；22 字节映像（KL6031/6041）用旧版 `ModbusRtuMaster_KL6x22B`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ModbusRtuMaster_KL6x5B.TcPOU`](../examples/P_Demo_ModbusRtuMaster_KL6x5B.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：维护老程序——经 KL6011 端子向站地址 3 温控器写一个设定值（功能码 6）。
PROGRAM P_Demo_ModbusRtuMaster_KL6x5B
VAR
    fbModbusMaster : ModbusRtuMaster_KL6x5B;
    nTempSetpoint  : WORD := 1850;
    bWriteReq      : BOOL;
    bBusy          : BOOL;
    bError         : BOOL;
    eErrId         : MODBUS_ERRORS;
    nBytesRead     : UINT;
END_VAR

fbModbusMaster.WriteSingleRegister(
    UnitID      := 3,
    Quantity    := 1,
    MBAddr      := 16#0800,
    cbLength    := SIZEOF(nTempSetpoint),
    pMemoryAddr := ADR(nTempSetpoint),
    Execute     := bWriteReq,
    Timeout     := T#1S,
    BUSY        => bBusy,
    Error       => bError,
    ErrorId     => eErrId,
    cbRead      => nBytesRead
);
```

## 7. 业务场景与实际价值

- **场景**：维护早期用本 FB 写成的存量工程（KL6001/6011/6021 串口端子 Modbus RTU 主站）。新建项目不应再用它。
- **价值**：保留旧接口让老程序能继续编译运行。
- **替代方案对比**：
  - **新工程**：用 `ModbusRtuMasterV2_KL6x5B`（功能更全）。
  - 其他硬件：旧版 PC 串口用 `ModbusRtuMaster_PcCOM`；旧版 22 字节端子用 `ModbusRtuMaster_KL6x22B`。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.1.1.2（[obsolete]）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186539275.html
- **相关 FB / 枚举**：`ModbusRtuMasterV2_KL6x5B`（推荐的新版替代）、`ModbusRtuMaster_PcCOM` / `ModbusRtuMaster_KL6x22B`（同为旧版）、`MODBUS_ERRORS`、`MODBUS_UNITID`
