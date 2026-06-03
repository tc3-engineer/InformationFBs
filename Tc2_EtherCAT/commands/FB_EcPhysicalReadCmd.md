# FB_EcPhysicalReadCmd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Commands` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57003787.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcPhysicalReadCmd.TcPOU`](../examples/P_Demo_FB_EcPhysicalReadCmd.TcPOU) |

---

## 1. 功能简述

EtherCAT 物理读命令功能块。通过本功能块，PLC 可向某一个或全部 EtherCAT 从站发送底层读命令（FPRD / APRD / BRD），直接读取从站控制器的寄存器或 DPRAM 内存。`bExecute` 上升沿触发一次命令，命令完成后 `wkc`（工作计数器, working counter）反馈实际响应了该命令的从站数量。寻址方式由 `eType` 决定：固定地址（Fixed）、自动增量（AutoInc）、广播（Broadcast）三种之一。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId; 
    adp      : UINT;
    ado      : UINT;
    len      : UDINT;
    eType    : E_EcAdressingType := eAdressingType_Fixed;
    pDstBuf  : PVOID;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站设备的 AMS NetID 字符串。本机主站用空串 `''` |
| `adp` | `UINT` | — | 要寻址的从站地址。含义随 `eType` 变化（详见下表 adp value） |
| `ado` | `UINT` | — | 要读取的物理内存（DPRAM）或寄存器地址 |
| `len` | `UDINT` | — | 要读取的字节数 |
| `eType` | `E_EcAdressingType` | `eAdressingType_Fixed` | 选择寻址模式 / 命令类型；不同枚举值对应不同的 EtherCAT 命令（详见下表 eType） |
| `pDstBuf` | `PVOID` | — | 接收缓冲区首地址（指针）；缓冲区必须足以容纳 `len` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 单次命令允许的最长执行时间 |

**adp 取值含义**：

| `eType` | `adp` 含义 |
|---|---|
| `eAdressingType_Fixed` | 已配置 EtherCAT 从站地址；可通过 `FB_EcGetAllSlaveAddr` 读取 |
| `eAdressingType_AutoInc` | 基于从站在环中的位置寻址；第 1 个从站 `adp = 0`，第 2 个 `adp = 16#FFFF (-1)`，第 3 个 `adp = 16#FFFE (-2)`，依此类推 |
| `eAdressingType_Broadcast` | 一次寻址所有从站；`adp` 可置为 0 |

**eType 对应的 EtherCAT 命令**：

| `eType` | 实际 EtherCAT 命令 |
|---|---|
| `eAdressingType_Fixed` | Configured Address Physical Read (`FPRD`) |
| `eAdressingType_AutoInc` | Auto Increment Physical Read (`APRD`) |
| `eAdressingType_Broadcast` | Broadcast Read (`BRD`) |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    wkc    : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中；功能块被启动后置 `TRUE`，收到反馈前保持 |
| `bError` | `BOOL` | `bBusy` 落沿后若传输出错则置 `TRUE` |
| `nErrId` | `UDINT` | `bError = TRUE` 时返回最近一次命令的 ADS 错误码 |
| `wkc` | `UINT` | 工作计数器（working counter）；每个成功处理该命令的从站递增 1。若只寻址了一个从站，正常值应为 1 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 由 `FALSE → TRUE` 的上升沿启动一次物理读命令。电平为 `TRUE` 不会重复触发；要再读一次必须先把 `bExecute` 拉回 `FALSE` 再上升。

**异步执行**：上升沿到来后立即置 `bBusy := TRUE`，功能块通过 ADS 向 EtherCAT 主站发送对应的物理命令（FPRD / APRD / BRD），主站把命令通过 EtherCAT 帧发出，到从站处理完毕回送后主站再把数据返回 PLC，此期间 PLC 任务必须在每个周期继续调用本实例，让内部 ADS 状态机推进，否则状态机会卡在 Busy。

**完成判定**：`bBusy` 由 `TRUE → FALSE` 之后才能读取 `bError` / `nErrId` / `wkc` 三者：

- `bError = FALSE` 且 `wkc = 1`（单从站寻址时）：读取成功，`pDstBuf` 指向的缓冲区已被填充
- `bError = FALSE` 但 `wkc = 0`：链路通畅但目标从站未应答（典型原因：`adp` 配错或该从站当前不在 OP 状态）
- `bError = TRUE`：ADS 通信本身失败，`nErrId` 给出错误码（最常见 `1861` = ADS 超时）

**典型用法**：读取从站 ESC（EtherCAT Slave Controller）的寄存器，例如 `ado = 16#0130`（AL Status，Application Layer 当前状态）；或读取 BK1120 总线耦合器 DPRAM 区诊断字节。日常工程通常用 §4 诊断类 FB（`FB_EcGetSlaveState` 等）即可，本 FB 适合开发底层调试工具或读取尚未在 InfoSys 文档化的厂商专有寄存器。

**典型陷阱**：
- `eType = AutoInc` 时 `adp` 是补码（slave 2 = `16#FFFF`）而不是从 0 递增；按 `0,1,2,...` 写会读到错误从站
- `len` 必须与 `pDstBuf` 指向缓冲实际大小一致；过大会导致越界覆盖
- 在 `bBusy = TRUE` 期间读取 `pDstBuf` 的内容未定义，必须等 `bBusy = FALSE`
- 寻址 BroadCAST 时 `wkc` = 网络中处于该命令可读状态的从站总数，可用于"统计有多少个从站当前在线"

## 4. 错误码 / 返回值

`nErrId` 是 ADS 错误码。常见取值：

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读取 `pDstBuf` 内容；同时检查 `wkc` 是否为 1（单从站）或预期值 |
| `6` | ADS port not found | EtherCAT 主站端口未启动，检查 TwinCAT 系统 / 主站任务是否处于 RUN |
| `7` | ADS target not found | `sNetId` 错或路由未建立 |
| `1861` (`0x745`) | ADS 调用超时 | 增大 `tTimeout`，或检查 EtherCAT 主站任务负载 |
| `0x70C` / `0x70D` | EtherCAT 命令传输错误 | 链路存在 CRC 错误或断线，对照 `FB_EcGetSlaveCrcError` 查具体端口 |

PDF + InfoSys 未列完整 ADS 错误码表，需要时对照 Beckhoff『ADS Return Codes』总表。

## 5. 使用注意 / 常见坑

- **`wkc` 是工程判定关键**：`bError = FALSE` 仅说明 ADS 调用成功（命令发出去了），不代表从站实际响应。必须配合 `wkc` 判定是否真的读到了数据。
- **本 FB 旁路了主站的从站状态机**：即使从站不在 OP，FPRD 也可能读到寄存器内容（取决于寄存器类别）；不要用本 FB 替代 `FB_EcGetSlaveState` 判定从站运行状态。
- **避免高频轮询**：物理命令直接占用主站 mailbox/cyclic 资源，1 ms 周期任务里每周期发一次会显著影响主站性能。日常诊断建议 100 ms ~ 1 s 触发一次。
- **指针生命周期**（工程经验补充）：`pDstBuf` 指向的缓冲必须在整个 `bBusy = TRUE` 期间保持有效，不能用栈上 / METHOD 局部变量。建议用 GVL 全局变量或 FB 自身的成员变量。
- **`sNetId` 用空串通常即可**：本地 PLC 与本地 EtherCAT 主站同机时空串自动路由到本机主站；远程主站需填实际 AMS NetID。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcPhysicalReadCmd.TcPOU`](../examples/P_Demo_FB_EcPhysicalReadCmd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：调试 EK1100 + EL30xx 串联拓扑时，怀疑某节点 ESC 中的 AL Status（`ado = 16#0130`）未进入 OP；现场用 `FB_EcGetSlaveState` 返回 SAFEOP 又跳到 OP 摇摆。用本 FB 在 1 s 周期下直接读 ESC 寄存器，配合 `wkc` 判定是该从站不响应还是状态字本身在变。
- **价值**：完全旁路主站状态缓存（主站每 50 ms 才轮询一次从站），可拿到 ESC 寄存器即时值；定位"主站缓存延迟 vs 真实从站状态"。
- **替代方案对比**：
  - `FB_EcGetSlaveState`：基于主站维护的状态缓存，调用快但有刷新延迟
  - `FB_EcCoeSdoRead`：走 CoE mailbox，只能读 0x6000+ 应用层对象，不能读 ESC 底层寄存器
  - **本 FB**：唯一能直接读 ESC DPRAM 全部地址的方式，但代价是占用主站资源、需要懂 ESC 寄存器图

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57003787.html
- **相关 FB / FC**：`FB_EcPhysicalWriteCmd`（写）、`FB_EcLogicalReadCmd`（按 logical address 读）、`FB_EcGetAllSlaveAddr`（取 Fixed 寻址用的 adp 值）、`E_EcAdressingType`（eType 枚举）
