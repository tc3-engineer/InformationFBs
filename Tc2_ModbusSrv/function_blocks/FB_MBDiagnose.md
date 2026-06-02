# FB_MBDiagnose

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusSrv` |
| Library Version | `1.6.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/192766219.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_MBDiagnose.TcPOU`](../examples/P_Demo_FB_MBDiagnose.TcPOU) |

---

## 1. 功能简述

Modbus 功能码 8（Diagnostics）的客户端功能块：对远端 Modbus 设备执行一系列诊断测试，用于检查主从站之间的通信系统、查询从站内部的各种错误状态。`nSubFnc` 选择子功能，`nReadData` 返回读回的诊断数据字。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sIPAddr       : STRING(15);
    nTCPPort      : UINT:= MODBUS_TCP_PORT;
    nUnitID       : BYTE:=16#FF;
    nSubFnc       : WORD;
    nWriteData    : WORD;
    bExecute      : BOOL;
    tTimeout      : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sIPAddr` | `STRING(15)` | `-` | 目标 Modbus 设备的 IP 地址字符串（如 `'192.168.1.50'`）。指向要访问的对端从站，不是本机地址 |
| `nTCPPort` | `UINT` | `MODBUS_TCP_PORT` | 目标设备的端口号。常量 `MODBUS_TCP_PORT` 即标准 Modbus TCP 端口 502 |
| `nUnitID` | `BYTE` | `16#FF` | 串行子网设备的单元标识号（Unit ID）。若经 TCP/IP 直接寻址设备，此值须为 `16#FF`；经 Modbus 网关转接串行从站时填实际从站地址 |
| `nSubFnc` | `WORD` | `-` | 要执行的诊断子功能码（sub-function），按 Modbus function 8 规范取值 |
| `nWriteData` | `WORD` | `-` | 随诊断请求写出的数据字 |
| `bExecute` | `BOOL` | `-` | 上升沿触发一次执行；FB 内部走 ADS 异步，期间保持电平不影响，完成后再次上升沿才会重发 |
| `tTimeout` | `TIME` | `-` | 本次 ADS 命令的超时时间，超过即报错。链路慢或对端响应慢时需加大 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBUSY      : BOOL;
    bError     : BOOL;
    nErrId     : UDINT;
    nReadData  : WORD;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBUSY` | `BOOL` | FB 使能后置位，直到收到反馈（成功或失败）才复位。声明名为 `bBUSY`，文档/示例中也写作 `bBusy`，指同一引脚 |
| `bError` | `BOOL` | 命令传输期间发生 ADS 错误时，在 `bBUSY` 复位的同时置 `TRUE` |
| `nErrId` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4） |
| `nReadData` | `WORD` | 返回从设备读回的诊断数据字 |

### VAR_IN_OUT

无（数据缓冲区通过 `pDestAddr` / `pSrcAddr` 指针传入，不是 VAR_IN_OUT）。

## 3. 行为说明

**触发与状态机**：`bExecute` 上升沿触发一次诊断操作。FB 通过 ADS 异步把请求转交给 TwinCAT Modbus TCP 服务组件，由它向 `sIPAddr` 指定的远端 Modbus 设备发出 TCP（端口 502，面向连接）请求。请求发出后 `bBUSY := TRUE`；收到对端响应或超时后，`bBUSY := FALSE`，并据结果置 `bError` 与 `nErrId`。`bExecute` 在 `bBUSY` 期间保持高电平不会重复触发，必须等一次执行结束、再来一个上升沿才会重发。

**角色定位**：本库的 FB_MB* 系列让 PLC 充当 Modbus **主站（master/client）**，主动去读写远端设备的诊断子功能（function 8）。它与“TwinCAT 自身作为 Modbus 从站被外部 SCADA 访问”是两回事——后者由 TF6250 服务端 + 配置器 + `mb_Input_Coils` 等 GVL 数组 + ADS 映射完成，不经过本 FB。

**典型用法**：周期任务里把 `bExecute` 接一个由业务条件产生的上升沿（如“到点采集”或“收到写指令”），其余参数（IP、地址、数量、缓冲区指针）在触发前一并赋好；用 `bBUSY` 下降沿判定本次完成，再读 `bError`/`nErrId`。

**典型陷阱**：① 把 `bExecute` 长期接 `TRUE`——只会执行一次，不会周期重发，需自行产生脉冲；② 缓冲区字节数不足（`cbLength` 给小了或缓冲区数组太短）会读写越界，务必按 §2 的公式留足；③ `bBUSY` 期间修改缓冲区或参数会让本次结果错乱；④ `tTimeout` 给太小，链路稍慢就误报超时。

## 4. 错误码 / 返回值

Modbus TCP 的错误经由 ADS 通道返回到 `nErrId`（`UDINT`）。错误码分三段：`0x0000`–`0x7800` 为 TwinCAT 系统/ADS 错误，`0x8000`–`0x80FF` 为内部 Modbus TCP 服务错误，`0x80070000`–`0x8007FFFF` 为 Win32/Winsock 错误（真值 = `nErrId - 0x80070000`）。下表列出最常见项（完整 ADS 码见 PDF §8.2，Win32 码见 §8.3）：

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 无错误 | 执行成功，读写结果有效 |
| `16#8001` (32769) | Modbus 功能未实现（function not implemented） | 对端不支持该 Modbus 功能码，换用对端支持的功能或确认设备类型 |
| `16#8002` (32770) | 地址或长度无效（invalid address or length） | 检查 `nMBAddr` / `nQuantity` 是否在对端地址空间内 |
| `16#8003` (32771) | 参数无效：寄存器数量不正确 | 核对读写数量与对端寄存器映射 |
| `16#8004` (32772) | Modbus 服务器错误（server error） | 对端从站内部错误，查从站侧诊断 |
| `16#6` (6) `ERR_TARGETPORTNOTFOUND` | 目标端口未找到——Modbus 服务组件未启动/未安装 | 确认已安装并启用 TF6250 Modbus TCP 服务 |
| `16#7` (7) `ERR_TARGETMACHINENOTFOUND` | 目标机器未找到——AMS 路由不存在 | 检查 ADS 路由与 `sNetID`（本机留空） |
| `16#745` (1861) `ADSERR_DEVICE_TIMEOUT` 区间 | ADS/设备超时 | `tTimeout` 太小或对端无响应——加大 `tTimeout`、检查对端在线与网络可达 |
| `16#70A` (1802) `ADSERR_DEVICE_NOMEMORY` | 内存不足 | 降低并发请求数 |

## 5. 使用注意 / 常见坑

- **`sIPAddr` 指向对端，不是本机**：这是最常见误解。FB_MB* 让 PLC 当 Modbus 主站去访问别的设备；要把 TwinCAT 当从站被外部读写，是另一套机制（TF6250 服务端 + 配置器 + GVL 映射数组），不经过本 FB。
- **`bExecute` 是边沿触发**：长期接 `TRUE` 只执行一次；周期采集要自己产生脉冲（如用 `bBusy` 下降沿重新拉一次）。
- **`nUnitID` 直连填 `16#FF`**：仅当经 Modbus 网关转接串行从站时才填实际从站号。
- **`tTimeout` 要给足**：默认无初值，必须显式赋值（如 `T#5S`）；链路慢或对端响应慢时加大，否则误报超时（ADS timeout）。
- **子功能码须对端支持**：`nSubFnc` 取值依从站实现而定（如 0 = Return Query Data 回显）；对端不支持会返回 Modbus 异常。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_MBDiagnose.TcPOU`](../examples/P_Demo_FB_MBDiagnose.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbDiagnose(
    sIPAddr    := sTargetIp,
    nTCPPort   := MODBUS_TCP_PORT,
    nUnitID    := 16#FF,
    nSubFnc    := 0,        // 0 = Return Query Data (回显测试)
    nWriteData := 16#A537,  // 任意测试字, 对端应原样回显
    bExecute   := bTrigger,
    tTimeout   := T#5S,
    bBUSY      => bBusy,
    bError     => bError,
    nErrId     => nErrId,
    nReadData  => nDiagReadData
);
```

## 7. 业务场景与实际价值

- **场景**：对可疑链路做联机诊断，例如用子功能 0（Return Query Data，回显测试）确认链路通畅，或读取从站的通信计数器/错误状态字排查现场故障。
- **价值**：功能码 8 是 Modbus 标准诊断入口；本 FB 把子功能号 + 写数据封装为一次调用，回读 `nReadData`，无须自拼诊断报文。
- **替代方案对比**：替代是 ping/抓包等外部手段——无法读从站内部计数器；或裸 socket 自实现。设备级诊断本 FB 直接。

## 8. 参考资料

- **PDF**：[TF6250_TC3_Modbus_TCP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf) §6.2.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/192766219.html
- **相关**：`FB_MBUdpDiagnose`（UDP 版）、`FB_MBReadRegs`（常规读）、`stLibVersion_Tc2_ModbusSrv`（库版本）
