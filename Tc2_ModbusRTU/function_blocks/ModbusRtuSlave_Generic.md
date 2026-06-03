# ModbusRtuSlave_Generic

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/14013409931.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ModbusRtuSlave_Generic.TcPOU`](../examples/P_Demo_ModbusRtuSlave_Generic.TcPOU) |

---

## 1. 功能简述

硬件无关的 Modbus RTU 从站功能块（Modbus slave），可经各种串行接口通讯（COM 口、虚拟 COM 口、EtherCAT 端子等）。由于与硬件解耦，用法比硬件相关的 `ModbusRtuSlave_PcCOM` / `ModbusRtuSlave_KL6x22B` / `ModbusRtuSlave_KL6x5B` 稍复杂；所有这些 FB 提供完全相同的 Modbus RTU 功能，但**只有 `ModbusRtuSlave_Generic` 支持虚拟 COM 口**。

本功能块在收到主站报文前一直**被动等待**。与硬件的连接需经 TF6340 TwinCAT 3 Serial Communication（需 license）：链接通讯口所需的数据结构必须单独实例化。本 FB 上的 `ComBuffer` 型数据结构是用于解耦后台硬件通讯的缓冲；后台通讯须用 `Tc2_SerialCom` 库的相应功能块（`SerialLineControl`、`SerialLineControlADS`）实现，因此工程里必须先引入 `Tc2_SerialCom` 库，并具备 TF6340 license。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    UnitID          : UINT;
    AdrInputs       : POINTER TO BYTE; (* Pointer to the Modbus input area *)
    SizeInputBytes  : UINT;
    AdrOutputs      : POINTER TO BYTE; (* Pointer to the Modbus output area *)
    SizeOutputBytes : UINT;
    AdrMemory       : POINTER TO BYTE; (* Pointer to the Modbus memory area *)
    SizeMemoryBytes : UINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `UnitID` | `UINT` | — | 本从站的 Modbus 站地址（1..247）。从站只应答含自身站地址的报文；可选用集合地址应答任意请求；地址 0 保留给广播，不是有效站地址。集合地址取值见枚举 `MODBUS_UNITID`（256/257/258） |
| `AdrInputs` | `POINTER TO BYTE` | — | Modbus 输入区起始地址，用 `ADR(输入变量)` 取 |
| `SizeInputBytes` | `UINT` | — | Modbus 输入数组的字节大小，用 `SIZEOF(输入变量)` 计算 |
| `AdrOutputs` | `POINTER TO BYTE` | — | Modbus 输出区起始地址，用 `ADR(输出变量)` 取 |
| `SizeOutputBytes` | `UINT` | — | Modbus 输出数组的字节大小，用 `SIZEOF(输出变量)` 计算 |
| `AdrMemory` | `POINTER TO BYTE` | — | Modbus 存储区起始地址，用 `ADR(存储变量)` 取 |
| `SizeMemoryBytes` | `UINT` | — | Modbus 存储数组的字节大小，用 `SIZEOF(存储变量)` 计算 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    ErrorId : MODBUS_ERRORS;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ErrorId` | `MODBUS_ERRORS` | 通讯受扰或出错时给出错误号（枚举 `MODBUS_ERRORS`，见 §4） |

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

**调用方式**：直接 `fbSlave(...)` 调用，每个 PLC 周期调一次，并把 `RxBuffer` / `TxBuffer` 作为 in-out 传入。从站没有 `Execute`、没有 `BUSY`，纯被动。

**与硬件相关从站的关键区别**：本 FB 自己不碰硬件，它只从 `RxBuffer` 取主站报文、把应答帧塞进 `TxBuffer`。真正把字节在物理线路与缓冲之间搬运，是由 `Tc2_SerialCom` 的 `SerialLineControl` / `SerialLineControlADS` 在后台周期执行的。因此工程结构是：每周期调一次串口通讯块（搬运 `RxBuffer`/`TxBuffer` 与物理口之间的字节）+ 每周期调一次本从站 FB（解析报文/组应答）。这套解耦使它能挂在任何 `Tc2_SerialCom` 支持的接口上，包括虚拟 COM 口。

**三块数据区与 Modbus 地址映射**（PDF §4.2，与其他从站一致）：

| 数据区 | 引脚 | Modbus 地址偏移 | 最大尺寸 | 主站可用的功能码 |
|---|---|---|---|---|
| Inputs（输入区） | `AdrInputs` / `SizeInputBytes` | `16#0` | 2048 words | 2、4（只读） |
| Outputs（输出区） | `AdrOutputs` / `SizeOutputBytes` | `16#800` | 14336 words | 1、3、5、6、15、16 |
| Memory（存储区） | `AdrMemory` / `SizeMemoryBytes` | `16#4000` | 16384 words | 3、6、16 |

举例：输入区 `Inputs[0]` 对应 Modbus 报文地址 `16#0`；输出区 `Outputs[0]` 对应 `16#800`；存储区 `Memory[0]` 对应 `16#4000`。主站发来的地址必须带这些偏移。输入/输出区可用 `AT %I*` / `AT %Q*` 映射物理 I/O。

**典型陷阱**：忘记每周期调用 `Tc2_SerialCom` 串口块 → 收不到主站报文、应答发不出；`RxBuffer`/`TxBuffer` 必须是跨周期稳定的同一份实例；未装 TF6340 license → 后台通讯块无法运行；地址偏移别忘；数组别超区上限。

## 4. 错误码 / 返回值

错误经 `ErrorId : MODBUS_ERRORS` 输出。`MODBUS_ERRORS` 枚举（PDF §5.2.2）：

| 枚举 | 值 | 含义（从站语境） |
|---|---|---|
| `MODBUSERROR_NO_ERROR` | 0 | 无错误，正常应答 |
| `MODBUSERROR_ILLEGAL_FUNCTION` | 1 | 主站发来不支持的功能码 |
| `MODBUSERROR_ILLEGAL_DATA_ADDRESS` | 2 | 访问地址超出数据区范围 |
| `MODBUSERROR_ILLEGAL_DATA_VALUE` | 3 | 数据值非法 |
| `MODBUSERROR_SLAVE_DEVICE_FAILURE` | 4 | 从站设备故障 |
| `MODBUSERROR_ACKNOWLEDGE` | 5 | 已受理 |
| `MODBUSERROR_SLAVE_DEVICE_BUSY` | 6 | 从站忙 |
| `MODBUSERROR_NEGATIVE_ACKNOWLEDGE` | 7 | 否定应答 |
| `MODBUSERROR_MEMORY_PARITY` | 8 | 存储器奇偶校验错 |
| `MODBUSERROR_GATEWAY_PATH_UNAVAILABLE` | 16#A | 网关路径不可用 |
| `MODBUSERROR_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND` | 16#B | 网关目标无应答 |
| `MODBUSERROR_CHARREC_TIMEOUT` | 16#20 | 字符接收超时 |
| `MODBUSERROR_ILLEGAL_DATA_SIZE` | 16#21 | 数据大小非法 |
| `MODBUSERROR_ILLEGAL_DEVICE_ADDRESS` | 16#22 | 设备地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_ADDRESS` | 16#23 | 目标地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_SIZE` | 16#24 | 目标大小非法 |
| `MODBUSERROR_NO_RESPONSE` | 16#25 | 无应答 |
| `MODBUSERROR_TXBUFFOVERRUN` | 102 | 发送缓冲区溢出 |
| `MODBUSERROR_SENDTIMEOUT` | 103 | 发送超时 |
| `MODBUSERROR_DATASIZEOVERRUN` | 107 | 数据大小溢出 |
| `MODBUSERROR_STRINGOVERRUN` | 110 | 字符串溢出 |
| `MODBUSERROR_INVALIDPOINTER` | 120 | 指针无效（某 `AdrXxx` 为 0） |
| `MODBUSERROR_CRC` | 150 | CRC 校验错 |
| `MODBUSERROR_INVALIDMEMORYADDRESS` | 232 | 内存地址无效 |
| `MODBUSERROR_TRANSMITBUFFERTOOSMALL` | 233 | 发送缓冲区过小 |

## 5. 使用注意 / 常见坑

- **必须配 `Tc2_SerialCom` + TF6340**：本 FB 只解析/组帧，物理收发靠 `Tc2_SerialCom` 的 `SerialLineControl(ADS)` 后台块，且需 TF6340 license。这是它与三款硬件相关从站 FB 最大的不同。
- **每周期都要调串口块 + 本从站块**：通讯块负责把 `RxBuffer`/`TxBuffer` 与物理口之间搬字节；漏调会导致从站收不到/答不出。
- **`RxBuffer`/`TxBuffer` 实例稳定**：作为 `VAR_IN_OUT` 传入，须是跨周期保持的同一份实例。
- **唯一支持虚拟 COM 口**：要走虚拟串口只能用本 FB。
- **地址映射同其他从站**：输入区 `16#0`、输出区 `16#800`、存储区 `16#4000`；数组别超区上限。
- **数据区上限**：输入 ≤ 2048 words、输出 ≤ 14336 words、存储 ≤ 16384 words。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ModbusRtuSlave_Generic.TcPOU`](../examples/P_Demo_ModbusRtuSlave_Generic.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：TwinCAT 经虚拟 COM 口作 Modbus RTU 从站，暴露 3 块数据区给上位主站。
PROGRAM P_Demo_ModbusRtuSlave_Generic
VAR
    fbModbusSlave : ModbusRtuSlave_Generic;
    stRxBuffer    : ComBuffer;                       // Tc2_SerialCom 收发缓冲（跨周期稳定）
    stTxBuffer    : ComBuffer;
    aInputs       : ARRAY[0..15] OF WORD;            // 输入区，偏移 16#0
    aOutputs      : ARRAY[0..15] OF WORD;            // 输出区，偏移 16#800
    aMemory       : ARRAY[0..15] OF WORD;            // 存储区，偏移 16#4000
    eErrId        : MODBUS_ERRORS;
END_VAR

// 注意：实际工程还须每周期调 Tc2_SerialCom 的 SerialLineControl(ADS) 块，
//       让它在 stRxBuffer/stTxBuffer 与物理（虚拟）串口之间搬字节。
fbModbusSlave(
    UnitID          := 1,
    AdrInputs       := ADR(aInputs),
    SizeInputBytes  := SIZEOF(aInputs),
    AdrOutputs      := ADR(aOutputs),
    SizeOutputBytes := SIZEOF(aOutputs),
    AdrMemory       := ADR(aMemory),
    SizeMemoryBytes := SIZEOF(aMemory),
    RxBuffer        := stRxBuffer,
    TxBuffer        := stTxBuffer,
    ErrorId         => eErrId
);
```

## 7. 业务场景与实际价值

- **场景**：需要走**虚拟 COM 口**或非标准串行接口把 TwinCAT 做成 Modbus RTU 从站——例如经 USB 转串口、软件虚拟串口对，或不在 KL6x/PC COM 标准型号里的串行硬件。
- **价值**：把硬件后端从 FB 里彻底解耦，给最大灵活性；只要 `Tc2_SerialCom` 能驱动的串口，本 FB 都能挂上去做 Modbus RTU 从站。
- **替代方案对比**：
  - `ModbusRtuSlave_PcCOM` / `_KL6x22B` / `_KL6x5B`：硬件相关、用法更简单（串口数据结构内置），但只支持各自固定硬件，且不支持虚拟 COM 口。
  - **本 FB**：硬件无关、支持虚拟 COM 口，代价是必须额外引入 `Tc2_SerialCom`、加 TF6340 license、每周期跑后台串口块。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.1.9（接口）、§4.2（Modbus 地址映射）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/14013409931.html
- **相关 FB / 枚举**：`ModbusRtuSlave_PcCOM` / `ModbusRtuSlave_KL6x22B` / `ModbusRtuSlave_KL6x5B`（硬件相关同类）、`ModbusRtuMasterV2_Generic`（主站对端）、`ComBuffer`（`Tc2_SerialCom`）、`MODBUS_ERRORS`、`MODBUS_UNITID`

## 9. 待确认项 (⚠️)

- InfoSys 的结构化解析把 `RxBuffer`/`TxBuffer` 归到了 inputs 区，而 PDF 明确它们位于 `VAR_IN_OUT`；本文档以 PDF 的 `VAR_IN_OUT` 划分为准（两源在变量名/类型 `ComBuffer` 上一致）。
