# FB_EcGetAllSlaveStates

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57029643.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllSlaveStates.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveStates.TcPOU) |

---

## 1. 功能简述

一次性读取主站连接的所有从站的 EtherCAT 状态机状态和链路状态。每个从站对应一条 `ST_EcSlaveState` 记录（含 `deviceState` 字段：INIT/PREOP/SAFEOP/OP 之一；以及 link 状态字段）。是"全网状态全景图"的核心工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId    : T_AmsNetId;
    pStateBuf : POINTER TO ARRAY[0..EC_MAX_SLAVES] OF ST_EcSlaveState;
    cbBufLen  : UDINT;    
    bExecute  : BOOL; 
    tTimeout  : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `pStateBuf` | `POINTER TO ARRAY[0..EC_MAX_SLAVES] OF ST_EcSlaveState` | — | 接收每从站状态的数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy   : BOOL;
    bError  : BOOL;
    nErrId  : UDINT;
    nSlaves : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码；`1798` 空指针、`1797` 缓冲过小 |
| `nSlaves` | `UINT` | 主站连接的从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `nSlaves` 与数组。

**状态语义**：每条 `ST_EcSlaveState` 含两个关键字段：
- `deviceState`（WORD）：EtherCAT 状态机当前状态，取 EC_DEVICE_STATE_INIT (0x01) / PREOP (0x02) / SAFEOP (0x04) / OP (0x08)，加上错误位（如 0x14 = SAFEOP_ERR）
- `linkState`（WORD）：物理链路状态

**期望状态**：正常运行时全部 = OP (0x08)。任何从站非 OP 都应触发报警检查。

**典型用法**：HMI 主页面的"全网状态总览"绑本 FB 1 s 周期；任何从站非 OP 即弹出报警。配合 `F_ConvSlaveStateToString` 把 0x08 翻译成 "OP" 字符串显示更友好。

**典型陷阱**：
- `deviceState` 状态可能含错误标志位（如 OP + Error）；判 OP 时用 `state.deviceState = 16#08`，不要用 `>= 16#08`
- 主站启动期会经过 INIT → PREOP → SAFEOP → OP；上电后立即读可能拿到中间态
- 调用频率不宜过高，1 s 周期足够；100 ms 周期会显著加 ADS 负载

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nSlaves` 与数组 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **状态判读**：用 `F_ConvSlaveStateToString`、`F_ConvSlaveStateToBits` 等转换 FC 把 WORD 解码为可读
- **EC_DEVICE_STATE_xxx 常量**：库内有全局常量，避免硬编码 0x01/0x02/...
- **缓冲生命周期**（工程经验补充）：用全局或 FB 成员变量

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllSlaveStates.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveStates.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：12 从站机型，HMI 主页要显示 12 个圆点 OP / 非 OP 颜色标识。每秒调本 FB 一次，更新颜色
- **价值**：把"全网状态总览"做成 1 行调用 + 一个循环遍历，免去为每个从站单独调 `FB_EcGetSlaveState`
- **替代方案对比**：逐个调 `FB_EcGetSlaveState` × 12 → ADS 调用 12 次成本高；本 FB → 单次

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57029643.html
- **相关 FB / FC**：`FB_EcGetSlaveState`（单从站）、`FB_EcGetMasterState`（主站）、`F_ConvSlaveStateToString`、`ST_EcSlaveState`
