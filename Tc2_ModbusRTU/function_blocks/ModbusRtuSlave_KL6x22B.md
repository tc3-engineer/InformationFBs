# ModbusRtuSlave_KL6x22B

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186543883.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ModbusRtuSlave_KL6x22B.TcPOU`](../examples/P_Demo_ModbusRtuSlave_KL6x22B.TcPOU) |

---

## 1. 功能简述

通过串行总线端子 KL6031 或 KL6041 通讯的 Modbus RTU 从站功能块（Modbus slave），也支持数据过程映像为 22 字节的串行 EtherCAT 端子。功能与 `ModbusRtuSlave_PcCOM` 完全相同，区别仅在底层硬件接口走 KL6x 总线端子而非 PC 的 COM 口（经 PC 串口通讯请用 `ModbusRtuSlave_PcCOM`）。

本功能块在收到主站报文前一直**被动等待**，不主动发起通讯，每个 PLC 周期调用一次即可，无需 `Execute`。工程把三块 Modbus 数据区（输入区 / 输出区 / 存储区）声明成 PLC 数组并把地址与大小传入，主站即可按 Modbus 标准地址映射读写。与端子的链接所需数据结构内置在 FB 中，分配方式与 TF6340 TwinCAT 3 Serial Communication 文档「Serial bus terminal」章节一致。

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

无。

## 3. 行为说明

**调用方式**：直接 `fbSlave(...)` 调用，每个 PLC 周期调一次。从站没有 `Execute`、没有 `BUSY`，纯被动，只在收到主站报文时处理并应答。

**三块数据区与 Modbus 地址映射**（PDF §4.2，用好从站的关键）：

| 数据区 | 引脚 | Modbus 地址偏移 | 最大尺寸 | 主站可用的功能码 |
|---|---|---|---|---|
| Inputs（输入区） | `AdrInputs` / `SizeInputBytes` | `16#0` | 2048 words | 2、4（只读） |
| Outputs（输出区） | `AdrOutputs` / `SizeOutputBytes` | `16#800` | 14336 words | 1、3、5、6、15、16 |
| Memory（存储区） | `AdrMemory` / `SizeMemoryBytes` | `16#4000` | 16384 words | 3、6、16 |

举例：输入区 `Inputs[0]` 对应 Modbus 报文地址 `16#0`（设备地址 30001）；输出区 `Outputs[0]` 对应报文地址 `16#800`（40801）；存储区 `Memory[0]` 对应报文地址 `16#4000`（44001）。**主站发来的地址必须带这些偏移**，否则落到错误数据区或报地址非法。输入/输出区可用 `AT %I*` / `AT %Q*` 直接映射物理 I/O，也可声明为与物理无关的纯数据区。

**时序语义**：收到合法报文后在帧间隔内处理并应答；处理在本 FB 被调用的 PLC 周期推进，调用周期不能太慢。通讯正常时 `ErrorId = MODBUSERROR_NO_ERROR`。

**典型陷阱**：忘记每周期调用 → 不应答；数组超出区上限 → 越界；主站没加地址偏移 → 读错区；`SIZEOF` 配错变量 → 范围不符。

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

- **每周期调用**：漏调则从站不应答、主站超时。
- **地址偏移别忘**：输入区 `16#0`、输出区 `16#800`、存储区 `16#4000`。主站 `MBAddr` 必须带偏移。
- **数据区上限**：输入 ≤ 2048 words、输出 ≤ 14336 words、存储 ≤ 16384 words。
- **`SIZEOF` 配对**：三块区各自用对应数组算 `SIZEOF`。
- **端子组态**：KL6031/KL6041 串口参数用 KS2000 或 `Tc2_SerialCom` 的 `KL6configuration` 块设（配置不需 license，通讯需 TF6340），波特率/校验位与主站一致。
- **端子选型**：22 字节过程映像端子（KL6031/6041）用本 FB；3 字节映像（KL6001/6011/6021）用 `ModbusRtuSlave_KL6x5B`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ModbusRtuSlave_KL6x22B.TcPOU`](../examples/P_Demo_ModbusRtuSlave_KL6x22B.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：TwinCAT 经 KL6041 端子作 Modbus RTU 从站，暴露 3 块数据区给上位主站。
PROGRAM P_Demo_ModbusRtuSlave_KL6x22B
VAR
    fbModbusSlave : ModbusRtuSlave_KL6x22B;
    aInputs       : ARRAY[0..15] OF WORD;            // 输入区（主站只读），偏移 16#0
    aOutputs      : ARRAY[0..15] OF WORD;            // 输出区（主站读写），偏移 16#800
    aMemory       : ARRAY[0..15] OF WORD;            // 存储区（主站读写），偏移 16#4000
    eErrId        : MODBUS_ERRORS;
END_VAR

fbModbusSlave(
    UnitID          := 1,
    AdrInputs       := ADR(aInputs),
    SizeInputBytes  := SIZEOF(aInputs),
    AdrOutputs      := ADR(aOutputs),
    SizeOutputBytes := SIZEOF(aOutputs),
    AdrMemory       := ADR(aMemory),
    SizeMemoryBytes := SIZEOF(aMemory),
    ErrorId         => eErrId
);
```

## 7. 业务场景与实际价值

- **场景**：用 KL6031/KL6041 串口端子（或对应串行 EtherCAT 端子）把 TwinCAT 控制器接入 RS485 现场总线作 Modbus RTU 从站，被上位 PLC/HMI/SCADA 读写。串口做成端子，省 PC 串口卡，接线规整。
- **价值**：与 `ModbusRtuSlave_PcCOM` 同样封装整套从站协议；硬件后端换成总线端子，业务代码无需改动。
- **替代方案对比**：
  - `ModbusRtuSlave_PcCOM`：走 PC COM 口。
  - `ModbusRtuSlave_KL6x5B`：用 KL6001/6011/6021（3 字节过程映像）端子。
  - `ModbusRtuSlave_Generic`：硬件无关、可走虚拟 COM 口，但需 `Tc2_SerialCom` 配合且更复杂。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.1.7（接口）、§4.2（Modbus 地址映射）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186543883.html
- **相关 FB / 枚举**：`ModbusRtuSlave_PcCOM` / `ModbusRtuSlave_KL6x5B` / `ModbusRtuSlave_Generic`、`ModbusRtuMasterV2_KL6x22B`（主站对端）、`MODBUS_ERRORS`、`MODBUS_UNITID`
