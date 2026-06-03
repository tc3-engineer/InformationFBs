# ModbusRtuSlave_PcCOM

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186537739.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ModbusRtuSlave_PcCOM.TcPOU`](../examples/P_Demo_ModbusRtuSlave_PcCOM.TcPOU) |

---

## 1. 功能简述

通过 PC 串口（COM 口）通讯的 Modbus RTU 从站功能块（Modbus slave）。它让 TwinCAT 控制器作为从站，被动应答挂在 RS232/RS485 总线上的 Modbus 主站（上位 PLC、SCADA、网关等）发来的读写请求。

本功能块在收到主站报文前一直**被动等待**，不主动发起任何通讯。它每个 PLC 周期调用一次即可，无需 `Execute` 触发。工程只需把三块 Modbus 数据区（输入区 / 输出区 / 存储区）声明成 PLC 数组并把它们的地址和大小传给本 FB，主站就能按 Modbus 标准地址映射读写这些数组。与串口的链接所需数据结构内置在 FB 中，PLC 程序集成后会在 TwinCAT System Manager 里显示，分配方式与 TF6340 TwinCAT 3 Serial Communication 文档「Serial PC Interface」章节一致（经串行总线端子通讯请用 `ModbusRtuSlave_KL6x5B` / `ModbusRtuSlave_KL6x22B`）。

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
| `AdrInputs` | `POINTER TO BYTE` | — | Modbus 输入区起始地址，用 `ADR(输入变量)` 取。输入区通常声明为 PLC 数组 |
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

**调用方式**：直接 `fbSlave(...)` 调用，每个 PLC 周期调一次。从站没有 `Execute`、没有 `BUSY`——它是纯被动的，只在收到主站报文时处理并应答。

**三块数据区与 Modbus 地址映射**（PDF §4.2「Modbus address arrays」，是用好从站的关键）：

| 数据区 | 引脚 | Modbus 地址偏移 | 最大尺寸 | 主站可用的功能码 |
|---|---|---|---|---|
| Inputs（输入区） | `AdrInputs` / `SizeInputBytes` | `16#0`（地址 0 = 第一个元素） | 2048 words（`ARRAY[0..2047] OF WORD`） | 2（读输入状态）、4（读输入寄存器）——只读 |
| Outputs（输出区） | `AdrOutputs` / `SizeOutputBytes` | `16#800`（地址 16#800 = 第一个元素） | 14336 words（`ARRAY[0..14335] OF WORD`） | 1（读线圈状态）、3（读保持寄存器）、5（写单线圈）、6（写单寄存器）、15（写多线圈）、16（写多寄存器） |
| Memory（存储区） | `AdrMemory` / `SizeMemoryBytes` | `16#4000`（地址 16#4000 = 第一个字） | 16384 words（`ARRAY[0..16383] OF WORD`） | 3（读保持寄存器）、6（写单寄存器）、16（写多寄存器） |

举例（输入区）：PLC 变量 `Inputs[0]` 对应 Modbus 报文地址 `16#0`、设备地址 30001；`Inputs[1]` 对应 `16#1`、30002；按位访问 `Inputs[0].0` 对应 `16#0`、10001。输出区 `Outputs[0]` 对应报文地址 `16#800`、设备地址 40801。存储区 `Memory[0]` 对应报文地址 `16#4000`、设备地址 44001。**主站发来的 `MBAddr` 必须带上这些偏移**，否则会落到错误的数据区或报地址非法。

**数据区可绑定物理 I/O**：输入/输出区既可声明成普通变量（与物理 I/O 无关的纯 Modbus 数据），也可用 `AT %I*` / `AT %Q*` 直接映射到控制器的物理输入/输出过程映像，让主站直接读写物理点。例如 `Inputs AT %I* : ARRAY[0..255] OF WORD;`。

**时序语义**：从站收到合法报文后在 Modbus 帧间隔内处理并应答；处理是在本 FB 被调用的 PLC 周期里推进的，所以调用周期不能太慢（否则应答延迟可能超出主站 `Timeout`）。通讯正常时 `ErrorId = MODBUSERROR_NO_ERROR`；收到非法功能码/越界地址时按 Modbus 规范回异常应答并在 `ErrorId` 反映。

**典型陷阱**：忘记每周期调用本 FB → 从站不应答，主站报 `NO_RESPONSE`；数组开太大超出区上限（如输入区 > 2048 words）→ 越界；主站没加地址偏移（直接用 0 访问输出区而非 `16#800`）→ 读到输入区或报地址非法；`SizeXxxBytes` 用错变量算 `SIZEOF` → 主站访问到的范围与实际数组不符。

## 4. 错误码 / 返回值

错误经 `ErrorId : MODBUS_ERRORS` 输出。从站场景下常见的是地址/功能码相关异常和线路错误。`MODBUS_ERRORS` 枚举（PDF §5.2.2）：

| 枚举 | 值 | 含义（从站语境） |
|---|---|---|
| `MODBUSERROR_NO_ERROR` | 0 | 无错误，正常应答 |
| `MODBUSERROR_ILLEGAL_FUNCTION` | 1 | 主站发来本从站不支持的功能码 |
| `MODBUSERROR_ILLEGAL_DATA_ADDRESS` | 2 | 主站访问的地址超出对应数据区范围 |
| `MODBUSERROR_ILLEGAL_DATA_VALUE` | 3 | 数据值非法 |
| `MODBUSERROR_SLAVE_DEVICE_FAILURE` | 4 | 从站设备故障 |
| `MODBUSERROR_ACKNOWLEDGE` | 5 | 已受理 |
| `MODBUSERROR_SLAVE_DEVICE_BUSY` | 6 | 从站忙 |
| `MODBUSERROR_NEGATIVE_ACKNOWLEDGE` | 7 | 否定应答 |
| `MODBUSERROR_MEMORY_PARITY` | 8 | 存储器奇偶校验错 |
| `MODBUSERROR_GATEWAY_PATH_UNAVAILABLE` | 16#A | 网关路径不可用 |
| `MODBUSERROR_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND` | 16#B | 网关目标无应答 |
| `MODBUSERROR_CHARREC_TIMEOUT` | 16#20 | 字符接收超时（帧未收全） |
| `MODBUSERROR_ILLEGAL_DATA_SIZE` | 16#21 | 数据大小非法 |
| `MODBUSERROR_ILLEGAL_DEVICE_ADDRESS` | 16#22 | 设备地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_ADDRESS` | 16#23 | 目标地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_SIZE` | 16#24 | 目标大小非法 |
| `MODBUSERROR_NO_RESPONSE` | 16#25 | 无应答 |
| `MODBUSERROR_TXBUFFOVERRUN` | 102 | 发送缓冲区溢出 |
| `MODBUSERROR_SENDTIMEOUT` | 103 | 发送超时 |
| `MODBUSERROR_DATASIZEOVERRUN` | 107 | 数据大小溢出 |
| `MODBUSERROR_STRINGOVERRUN` | 110 | 字符串溢出 |
| `MODBUSERROR_INVALIDPOINTER` | 120 | 指针无效（某个 `AdrXxx` 为 0/未初始化） |
| `MODBUSERROR_CRC` | 150 | CRC 校验错（线路干扰、波特率不匹配） |
| `MODBUSERROR_INVALIDMEMORYADDRESS` | 232 | 内存地址无效 |
| `MODBUSERROR_TRANSMITBUFFERTOOSMALL` | 233 | 发送缓冲区过小 |

## 5. 使用注意 / 常见坑

- **每周期调用**：从站必须每个 PLC 周期调用一次，否则收到的报文得不到处理、主站超时。
- **地址偏移别忘**：输入区偏移 `16#0`、输出区 `16#800`、存储区 `16#4000`。主站组态时 `MBAddr` 必须带偏移。这是接 Beckhoff Modbus 从站最常见的「读不到/读错区」根因。
- **数据区上限**：输入区 ≤ 2048 words、输出区 ≤ 14336 words、存储区 ≤ 16384 words。
- **`SIZEOF` 配对**：`SizeInputBytes` 必须用 `SIZEOF(对应输入数组)`，三块区各自配对，别张冠李戴。
- **物理 I/O 映射**：用 `AT %I*` / `AT %Q*` 可让主站直读写物理点；不加则是与物理 I/O 解耦的纯数据区。安全敏感的物理输出建议用独立数据区 + PLC 逻辑过滤，而非让主站直接写物理 `%Q`。（工程经验补充）
- **波特率/校验位/停止位**：在 COM 口配置里设，与主站一致；不一致表现为 `MODBUSERROR_CRC` 或收不到报文。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ModbusRtuSlave_PcCOM.TcPOU`](../examples/P_Demo_ModbusRtuSlave_PcCOM.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：TwinCAT 作为 Modbus RTU 从站，把 3 块数据区暴露给上位主站读写。
PROGRAM P_Demo_ModbusRtuSlave_PcCOM
VAR
    fbModbusSlave : ModbusRtuSlave_PcCOM;
    aInputs       : ARRAY[0..15] OF WORD;            // 输入区（主站只读），偏移 16#0
    aOutputs      : ARRAY[0..15] OF WORD;            // 输出区（主站可读写），偏移 16#800
    aMemory       : ARRAY[0..15] OF WORD;            // 存储区（主站读写），偏移 16#4000
    eErrId        : MODBUS_ERRORS;
END_VAR

// 每周期调用一次；从站被动应答主站请求
fbModbusSlave(
    UnitID          := 1,                            // 本从站站地址
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

- **场景**：TwinCAT 控制器要把自己的数据（产量、状态、报警字、可被远程改写的设定值）通过 RS485 串口暴露给上位 Modbus RTU 主站——上位 PLC、触摸屏 HMI、SCADA、协议网关。让本机变成现场总线上的一个标准 Modbus 从站。
- **价值**：把 Modbus RTU 从站的报文解析、地址映射、应答组帧、异常处理全封装。工程只需声明三块数组并一行调用，主站即可标准读写，省去手写协议栈。
- **替代方案对比**：
  - 自己用 `Tc2_SerialCom` 收裸字节再手写从站协议栈：工作量极大、要处理帧间隔/CRC/广播。
  - 用 Modbus **TCP** 从站（TF6250）：走以太网，需主站支持 Modbus TCP。
  - **本 FB**：串口 Modbus RTU 从站标准答案；硬件依赖 PC COM 口。用 KL6x 端子改 `ModbusRtuSlave_KL6x22B` / `ModbusRtuSlave_KL6x5B`，要虚拟 COM 口用 `ModbusRtuSlave_Generic`。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.1.6（接口）、§4.2（Modbus 地址映射）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186537739.html
- **相关 FB / 枚举**：`ModbusRtuSlave_KL6x22B` / `ModbusRtuSlave_KL6x5B` / `ModbusRtuSlave_Generic`（其他硬件接口的同类从站）、`ModbusRtuMasterV2_PcCOM`（主站对端）、`MODBUS_ERRORS`、`MODBUS_UNITID`
