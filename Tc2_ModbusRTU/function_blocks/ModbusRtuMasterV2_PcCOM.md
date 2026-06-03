# ModbusRtuMasterV2_PcCOM

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/13966844555.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ModbusRtuMasterV2_PcCOM.TcPOU`](../examples/P_Demo_ModbusRtuMasterV2_PcCOM.TcPOU) |

---

## 1. 功能简述

通过 PC 串口（COM 口）通讯的 Modbus RTU 主站功能块（Modbus master）。它让 TwinCAT 控制器作为主站，主动向挂在 RS232/RS485 总线上的 Modbus 从站（变频器、电表、温控器、第三方 PLC 等）发起读写请求。

本功能块**不以基本形式直接调用**，而是把每一个 Modbus 功能码实现成一个**动作（Action）**，工程里按需调用对应动作。例如 `ModbusMaster.ReadRegs` 对应 Modbus 功能码 3（读保持寄存器）、`ModbusMaster.WriteRegs` 对应功能码 16（写多个寄存器）。与串口的链接所需的数据结构已内置在 FB 中，PLC 程序集成后会在 TwinCAT System Manager 里显示出来，可与一个 COM 口连接（连接方式与 TF6340 TwinCAT 3 Serial Communication 文档中「Serial PC Interface」章节一致）。

带 `V2` 后缀的版本在旧版基础上额外提供功能码 23（`ReadWriteRegs`，读写组合）和用户自定义报文（`UserReadWrite`），并引入了 `Aux*` 一组辅助参数。

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
| `UnitID` | `BYTE` | — | Modbus 从站站地址（1..247）。从站只应答含自身站地址的报文。可选用集合地址应答任意请求；地址 0 保留给广播报文，不是有效站地址（取值集合见枚举 `MODBUS_UNITID`）。⚠️ 见 §9：声明类型为 `BYTE`，但 InfoSys/PDF 的参数表把类型列写成 `UINT` |
| `Quantity` | `WORD` | — | 字操作功能码要读/写的数据字数；位操作功能码（线圈/输入位）时表示位的数量 |
| `MBAddr` | `WORD` | — | Modbus 数据地址，从站据此定位被读写的数据区；该地址原样发给从站并在从站侧被解释为数据地址。诊断功能码 8（`Diagnostics`）时这里传的是功能码（子功能码） |
| `cbLength` | `UINT` | — | 发送/读取所用数据变量的字节大小。`cbLength` 必须 ≥ 由 `Quantity` 决定的实际数据量，字访问时例如 `cbLength >= Quantity * 2`。可用 `SIZEOF(Modbus 数据)` 计算 |
| `pMemoryAddr` | `POINTER TO BYTE` | — | PLC 内数据缓冲区起始地址，用 `ADR(Modbus 数据)` 取。读动作把读回的数据写入该变量；写动作把该变量内容发往从站 |
| `AuxQuantity` | `WORD` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 这类读写组合功能码使用的辅助参数 |
| `AuxMBAddr` | `WORD` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助参数 |
| `AuxcbLength` | `UINT` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助参数 |
| `pAuxMemoryAddr` | `POINTER TO BYTE` | — | 仅 `ReadWriteRegs` / `UserReadWrite` 使用的辅助缓冲区地址 |
| `Execute` | `BOOL` | — | 启动信号。`Execute` 上升沿触发一次动作 |
| `Timeout` | `TIME` | — | 等待被寻址从站应答的超时时间 |

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
| `BUSY` | `BOOL` | 指示功能块正在执行。`Execute` 上升沿时变 `TRUE`，所启动的动作完成后变回 `FALSE`。同一时刻只能有一个动作处于活动状态 |
| `Error` | `BOOL` | 指示动作执行期间发生了错误 |
| `ErrorId` | `MODBUS_ERRORS` | 通讯受扰或出错时给出错误号（枚举 `MODBUS_ERRORS`，见 §4） |
| `cbRead` | `UINT` | 读动作时给出已读回的数据字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：本 FB 不直接 `fb(...)` 调用，而是调用它的动作，例如 `fbMaster.ReadRegs(...)`、`fbMaster.WriteRegs(...)`。所有动作共用上面同一组输入/输出引脚，因此一个实例同一时刻只能跑一个动作（由 `BUSY` 互锁）。要并发多个请求需多个实例，但同一条物理串口上的报文最终仍是串行的——这是 RS485 半双工总线的物理约束。

**支持的功能码（动作）**：

| 动作 | 功能码 | 含义 | 数据方向 |
|---|---|---|---|
| `ModbusMaster.ReadCoils` | 1 | 读线圈（二进制输出），按压缩格式（每字节 8 位）存入 `pMemoryAddr` | 从站 → PLC |
| `ModbusMaster.ReadInputStatus` | 2 | 读二进制输入，按压缩格式存入 `pMemoryAddr` | 从站 → PLC |
| `ModbusMaster.ReadRegs` | 3 | 读保持寄存器 | 从站 → PLC |
| `ModbusMaster.ReadInputRegs` | 4 | 读输入寄存器 | 从站 → PLC |
| `ModbusMaster.WriteSingleCoil` | 5 | 写单个线圈（数据须按压缩格式备好在 `pMemoryAddr`） | PLC → 从站 |
| `ModbusMaster.WriteSingleRegister` | 6 | 写单个寄存器（一个数据字） | PLC → 从站 |
| `ModbusMaster.WriteMultipleCoils` | 15 | 写多个线圈（压缩格式） | PLC → 从站 |
| `ModbusMaster.WriteRegs` | 16 | 写多个寄存器（Preset Multiple Registers） | PLC → 从站 |
| `ModbusMaster.Diagnostics` | 8 | 诊断请求，子功能码经 `MBAddr` 传入；该功能不寻址内存，所需数据放在 `pMemoryAddr` | 双向 |
| `ModbusMaster.ReadWriteRegs` | 23 | 读写组合：用 `Aux*` 参数指定要写的数据发给从站，同时读回数据存到 `pMemoryAddr`（仅 V2） | 双向 |
| `ModbusMaster.UserReadWrite` | 用户自定义 | 通用用户报文：功能码由用户写在 `pMemoryAddr` 数据的首字节，可发任意功能码报文，应答数据存到 `pAuxMemoryAddr`（仅 V2） | 双向 |

**时序状态机**：`Execute` 由 `FALSE → TRUE` 上升沿触发一次动作 → `BUSY := TRUE` → FB 组帧并经串口发出请求 → 等待从站应答或 `Timeout` 计时到 → 收到合法应答则 `BUSY := FALSE`、`Error := FALSE`，读动作把数据落到 `pMemoryAddr` 并在 `cbRead` 给出字节数 → 从站返回异常码、CRC 错或超时则 `BUSY := FALSE`、`Error := TRUE`、`ErrorId` 给出错误号。

**触发语义**：仅上升沿触发，电平为 `TRUE` 不会反复发起；要再发一帧必须先把 `Execute` 拉回 `FALSE` 再上升一次。`BUSY = TRUE` 期间必须每个 PLC 周期继续调用该动作让内部串口收发状态机推进，且不要修改 `pMemoryAddr` 指向的缓冲区（写动作期间改缓冲会发出错乱数据；读动作完成前缓冲内容无效）。

**典型用法**：周期轮询多台从站时，做一个轮询状态机——给从站 A 发 `ReadRegs` 上升沿，等 `BUSY` 落回且 `Error = FALSE`，再切到从站 B（改 `UnitID` 后再上升 `Execute`）。轮询节奏受 `Timeout` 与从站应答速度限制。

**典型陷阱**：`cbLength` 小于 `Quantity*2` 会触发 `MODBUSERROR_ILLEGAL_DATA_SIZE`；多个动作并发抢同一实例会被 `BUSY` 互锁丢请求；`Timeout` 太短在低波特率（如 9600）下读多寄存器容易报 `MODBUSERROR_NO_RESPONSE`。

## 4. 错误码 / 返回值

错误经 `Error` + `ErrorId : MODBUS_ERRORS` 输出。`MODBUS_ERRORS` 是枚举，分三段（PDF §5.2.2 / InfoSys「Modbus RTU Error Codes」）：

**Modbus 标准异常码（从站在应答里回的）**：

| 枚举 | 值 | 含义 |
|---|---|---|
| `MODBUSERROR_NO_ERROR` | 0 | 无错误 |
| `MODBUSERROR_ILLEGAL_FUNCTION` | 1 | 从站不支持该功能码 |
| `MODBUSERROR_ILLEGAL_DATA_ADDRESS` | 2 | 数据地址非法（`MBAddr` 超出从站地址范围） |
| `MODBUSERROR_ILLEGAL_DATA_VALUE` | 3 | 数据值非法 |
| `MODBUSERROR_SLAVE_DEVICE_FAILURE` | 4 | 从站设备故障 |
| `MODBUSERROR_ACKNOWLEDGE` | 5 | 从站已受理（长操作进行中） |
| `MODBUSERROR_SLAVE_DEVICE_BUSY` | 6 | 从站忙，稍后重试 |
| `MODBUSERROR_NEGATIVE_ACKNOWLEDGE` | 7 | 否定应答 |
| `MODBUSERROR_MEMORY_PARITY` | 8 | 从站存储器奇偶校验错 |
| `MODBUSERROR_GATEWAY_PATH_UNAVAILABLE` | 16#A | 网关路径不可用 |
| `MODBUSERROR_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND` | 16#B | 网关后的目标设备无应答 |

**库追加的 Modbus 错误定义**：

| 枚举 | 值 | 含义 |
|---|---|---|
| `MODBUSERROR_CHARREC_TIMEOUT` | 16#20 | 字符接收超时 |
| `MODBUSERROR_ILLEGAL_DATA_SIZE` | 16#21 | 数据大小非法（多为 `cbLength` 不足） |
| `MODBUSERROR_ILLEGAL_DEVICE_ADDRESS` | 16#22 | 设备地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_ADDRESS` | 16#23 | 目标地址非法 |
| `MODBUSERROR_ILLEGAL_DESTINATION_SIZE` | 16#24 | 目标大小非法 |
| `MODBUSERROR_NO_RESPONSE` | 16#25 | 从站无应答（最常见的「掉线/地址错/总线断」错误） |

**底层通讯错误 + 高层 PLC 错误**：

| 枚举 | 值 | 含义 |
|---|---|---|
| `MODBUSERROR_TXBUFFOVERRUN` | 102 | 发送缓冲区溢出 |
| `MODBUSERROR_SENDTIMEOUT` | 103 | 发送超时 |
| `MODBUSERROR_DATASIZEOVERRUN` | 107 | 数据大小溢出 |
| `MODBUSERROR_STRINGOVERRUN` | 110 | 字符串溢出 |
| `MODBUSERROR_INVALIDPOINTER` | 120 | 指针无效（`pMemoryAddr` 为 0/未初始化） |
| `MODBUSERROR_CRC` | 150 | CRC 校验错（线路干扰、波特率/校验位不匹配） |
| `MODBUSERROR_INVALIDMEMORYADDRESS` | 232 | 内存地址无效 |
| `MODBUSERROR_TRANSMITBUFFERTOOSMALL` | 233 | 发送缓冲区过小 |

## 5. 使用注意 / 常见坑

- **`UnitID` 类型不一致**：VAR 声明是 `BYTE`，参数说明表写 `UINT`。`BYTE` 取值 0..255，足够覆盖 1..247 的站地址；集合地址（256..258，见 `MODBUS_UNITID`）超过 `BYTE` 范围，本 FB 的 `BYTE` 引脚无法直接送集合地址（这点与从站 FB 的 `UINT` UnitID 不同）。详见 §9。
- **`cbLength` 必须够大**：字访问 `cbLength >= Quantity*2`，否则报 `MODBUSERROR_ILLEGAL_DATA_SIZE`。用 `SIZEOF()` 算最稳。
- **缓冲区生命期**：`BUSY = TRUE` 期间不要改 `pMemoryAddr`（及 `pAuxMemoryAddr`）指向的变量；最好把它声明成稳定的全局/局部数组。
- **波特率/校验位/停止位要和从站一致**：这些在 COM 口配置里设（System Manager 或 `Tc2_SerialCom` 配置块），不在本 FB 上。不一致表现为 `MODBUSERROR_CRC` 或 `MODBUSERROR_NO_RESPONSE`。
- **RS485 半双工**：同一总线上同时只能有一个主站发问，本 FB 的 `BUSY` 互锁保证一个实例内动作串行；多实例并发到同一物理口需要工程自己排队。（工程经验补充）
- **`Diagnostics`(8) 的特殊性**：子功能码走 `MBAddr` 而不是寻址内存，别误把它当普通寄存器地址。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ModbusRtuMasterV2_PcCOM.TcPOU`](../examples/P_Demo_ModbusRtuMasterV2_PcCOM.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：主站每来一次 bReadReq 上升沿，就用功能码 3 读站地址 1 从站的 10 个保持寄存器。
PROGRAM P_Demo_ModbusRtuMasterV2_PcCOM
VAR
    fbModbusMaster : ModbusRtuMasterV2_PcCOM;
    aHoldingRegs   : ARRAY[0..9] OF WORD;          // 读回的 10 个寄存器
    bReadReq       : BOOL;                          // 在线上升沿触发一次读
    bBusy          : BOOL;
    bError         : BOOL;
    eErrId         : MODBUS_ERRORS;
    nBytesRead     : UINT;
END_VAR

// 调用 ReadRegs 动作（功能码 3），不是直接 fbModbusMaster()
fbModbusMaster.ReadRegs(
    UnitID      := 1,                               // 从站站地址
    Quantity    := 10,                              // 读 10 个字
    MBAddr      := 16#0000,                          // 从地址 0 开始
    cbLength    := SIZEOF(aHoldingRegs),             // >= Quantity*2 = 20
    pMemoryAddr := ADR(aHoldingRegs),
    Execute     := bReadReq,
    Timeout     := T#1S,
    BUSY        => bBusy,
    Error       => bError,
    ErrorId     => eErrId,
    cbRead      => nBytesRead
);
```

## 7. 业务场景与实际价值

- **场景**：TwinCAT 控制器通过板载 / 扩展 COM 口的 RS485，主动轮询现场的 Modbus RTU 设备——变频器（读转速、写频率给定）、智能电表（读电压电流电能）、温控仪、称重仪表、第三方小 PLC。这是工业现场最常见的串行总线集成场景。
- **价值**：把 Modbus RTU 的组帧（地址 + 功能码 + 数据 + CRC）、串口收发时序、应答解析、异常码翻译全部封装成「调一个动作 + 给指针 + 等 `BUSY` 落回」。业务代码不碰一个字节的协议细节。
- **替代方案对比**：
  - 自己用 `Tc2_SerialCom` 收发裸字节再手写 Modbus 组帧/CRC：工作量大、易错、CRC 调半天。
  - 用 Modbus **TCP**（Tc2_ModbusSrv / TF6250）：走以太网不走串口，需要设备支持 Modbus TCP 或加网关。
  - **本 FB**：串口 Modbus RTU 的标准答案；硬件依赖 PC COM 口。换成 KL6031/KL6041 串口端子用 `ModbusRtuMasterV2_KL6x22B`，换 KL6001/6011/6021 用 `ModbusRtuMasterV2_KL6x5B`，要用虚拟串口/EtherCAT 端子用 `ModbusRtuMasterV2_Generic`。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/13966844555.html
- **相关 FB / 枚举**：`ModbusRtuMasterV2_KL6x22B` / `ModbusRtuMasterV2_KL6x5B` / `ModbusRtuMasterV2_Generic`（其他硬件接口的同类主站）、`ModbusRtuSlave_PcCOM`（从站对端）、`MODBUS_ERRORS`（错误枚举）、`MODBUS_UNITID`（站地址枚举）、`ModbusRtuMaster_PcCOM`（已废弃的旧版）

## 9. 待确认项 (⚠️)

- `UnitID` 类型：PDF 与 InfoSys 的 **VAR_INPUT 声明块**均写 `UnitID : BYTE;`，而二者的**参数说明表「Type」列**均写 `UINT`。本文档逐字搬运声明块（`BYTE`），并在 §5 说明其对集合地址的影响。Beckhoff 文档自身的这处不一致建议以实际库声明（`BYTE`）为准。
