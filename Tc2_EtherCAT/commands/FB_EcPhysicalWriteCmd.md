# FB_EcPhysicalWriteCmd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Commands` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57005323.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcPhysicalWriteCmd.TcPOU`](../examples/P_Demo_FB_EcPhysicalWriteCmd.TcPOU) |

---

## 1. 功能简述

EtherCAT 物理写命令功能块。PLC 通过本功能块向某一个或全部 EtherCAT 从站发送底层写命令（FPWR / APWR / BWR），直接写入从站控制器（ESC）的寄存器或 DPRAM 内存。`bExecute` 上升沿触发一次写命令，`wkc` 反馈成功处理该命令的从站数量。寻址方式由 `eType` 决定，分别对应固定地址、自动增量、广播三种 EtherCAT 命令。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId; 
    adp      : UINT;
    ado      : UINT;
    len      : UDINT;
    eType    : E_EcAdressingType := eAdressingType_Fixed;
    pSrcBuf  : PVOID;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站设备的 AMS NetID 字符串。本机主站用空串 `''` |
| `adp` | `UINT` | — | 要寻址的从站地址。含义随 `eType` 变化（详见下表 adp value） |
| `ado` | `UINT` | — | 要写入的物理内存（DPRAM）或寄存器地址 |
| `len` | `UDINT` | — | 要写入的字节数 |
| `eType` | `E_EcAdressingType` | `eAdressingType_Fixed` | 选择寻址模式 / 命令类型；不同枚举值对应不同的 EtherCAT 命令（详见下表 eType） |
| `pSrcBuf` | `PVOID` | — | 待写出数据缓冲区首地址（指针）；至少 `len` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次写命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 单次命令允许的最长执行时间 |

**adp 取值含义**：

| `eType` | `adp` 含义 |
|---|---|
| `eAdressingType_Fixed` | 已配置 EtherCAT 从站地址；可通过 `FB_EcGetAllSlaveAddr` 读取 |
| `eAdressingType_AutoInc` | 基于从站在环中的位置寻址；第 1 个 `adp = 0`，第 2 个 `adp = 16#FFFF`，第 3 个 `adp = 16#FFFE` |
| `eAdressingType_Broadcast` | 一次寻址所有从站；`adp` 应置为 0 |

**eType 对应的 EtherCAT 命令**：

| `eType` | 实际 EtherCAT 命令 |
|---|---|
| `eAdressingType_Fixed` | Configured Address Physical Write (`FPWR`) |
| `eAdressingType_AutoInc` | Auto Increment Physical Write (`APWR`) |
| `eAdressingType_Broadcast` | Broadcast Write (`BWR`) |

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
| `bBusy` | `BOOL` | 命令进行中；启动后置 `TRUE`，收到反馈前保持 |
| `bError` | `BOOL` | `bBusy` 落沿后若传输出错则置 `TRUE` |
| `nErrId` | `UDINT` | `bError = TRUE` 时返回 ADS 错误码 |
| `wkc` | `UINT` | 工作计数器；每个成功处理该命令的从站递增 1 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：仅 `bExecute` 上升沿触发一次写命令。电平 `TRUE` 期间不会反复写；要再写一次必须先把 `bExecute` 拉回 `FALSE`。

**异步执行**：触发后立即置 `bBusy := TRUE`，通过 ADS 把对应 FPWR / APWR / BWR 帧交给 EtherCAT 主站发送。期间必须保持每周期调用同一实例以推进内部 ADS 状态机。`bBusy` 由 `TRUE → FALSE` 后再读 `bError` / `wkc` 才有意义。

**写入语义**：FPWR / APWR / BWR 是无确认的 EtherCAT 命令（slave 处理后只更新 wkc，没有应用层级别的 ACK）。这意味着写"成功"只表明从站 ESC 接受了帧，并不代表 ESC 内部硬件已把变化反映到外设；对于多数寄存器写入是即时的，但写 AL Control（请求状态转换）等寄存器后还需读 AL Status 确认转换完成。

**典型用法**：
- 写 ESC 寄存器 `0x0120`（AL Control）让从站切换状态（INIT → PREOP → SAFEOP → OP），但通常应用层用 `FB_EcSetSlaveState` 已封装好
- 写从站厂商专有控制位（diagnostic enable、test pattern 等）
- 广播写复位某些公共寄存器（极少用，需谨慎）

**典型陷阱**：
- 写 ESC 关键寄存器（DC 时钟、SyncManager 配置）可能导致从站脱离主站状态机，进入 INIT；调试期常见
- `eType = Broadcast` + 写关键寄存器：可能瞬间让所有从站离线
- 与主站同时操作同一寄存器：例如主站正在自己写 SyncManager 配置时 PLC 也写，结果未定义

## 4. 错误码 / 返回值

`nErrId` 是 ADS 错误码。常见取值：

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | ADS 调用成功 | 读 `wkc` 判定是否真有从站应答 |
| `6` | ADS port not found | 主站未启动 |
| `7` | ADS target not found | `sNetId` / 路由问题 |
| `1861` (`0x745`) | 命令超时 | 增大 `tTimeout` |
| `0x70C` / `0x70D` | EtherCAT 命令传输错误 | 链路 CRC 错误，查 `FB_EcGetSlaveCrcError` |

完整 ADS 错误码表请对照 Beckhoff『ADS Return Codes』。

## 5. 使用注意 / 常见坑

- **`wkc` 必查**：`bError = FALSE` 仅说明 ADS 调用回执 OK；要确认从站确实接受了写命令，必须 `wkc ≥ 1`（单点）或预期数（广播）。
- **写寄存器有风险**：ESC 寄存器图涉及 SyncManager / FMMU / DC 等关键功能，错写可能令该从站直接脱机。务必参考 ETG.1000.4（EtherCAT Specification）核对 `ado`。
- **不要替代 CoE**：应用层对象（0x6000、0x7000、0x8000 …）必须用 CoE（`FB_EcCoeSdoWrite`），不能用 FPWR；FPWR 只看到 ESC 寄存器，看不到 CoE 对象字典。
- **指针生命周期**（工程经验补充）：`pSrcBuf` 指向的数据必须在 `bBusy = TRUE` 期间保持不变；建议用全局或 FB 成员变量。
- **`Broadcast` 写谨慎**：BWR 会同时写所有从站，多数情况下不是你想要的。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcPhysicalWriteCmd.TcPOU`](../examples/P_Demo_FB_EcPhysicalWriteCmd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：某 EL6021 串口模块出厂时 ESC 寄存器某厂商位未清，导致初始化偶发失败；维修工程用本 FB 写 ESC `0x0140` 区某一位完成"软复位"，绕过整机重启。
- **价值**：旁路主站状态机直接写 ESC，可在线下发厂商专有调试命令或低级初始化，避免重新 boot 整机的工时。
- **替代方案对比**：
  - `FB_EcCoeSdoWrite`：仅能写应用层对象字典，写不到 ESC 寄存器
  - `FB_EcSetSlaveState`：仅能控制状态机迁移，写不到任意寄存器
  - **本 FB**：能写任何 ESC 寄存器，但需要懂 ESC 寄存器图与从站手册，错写后果严重

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57005323.html
- **相关 FB / FC**：`FB_EcPhysicalReadCmd`（读）、`FB_EcLogicalWriteCmd`（按 logical address 写）、`FB_EcGetAllSlaveAddr`（取 Fixed 寻址用的 adp 值）、`E_EcAdressingType`（eType 枚举）
