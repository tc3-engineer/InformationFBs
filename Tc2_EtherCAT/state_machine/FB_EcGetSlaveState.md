# FB_EcGetSlaveState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57028107.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetSlaveState.TcPOU`](../examples/P_Demo_FB_EcGetSlaveState.TcPOU) |

---

## 1. 功能简述

读取单个 EtherCAT 从站的状态机状态和链路状态。返回 `ST_EcSlaveState` 结构含 `deviceState` 和 `linkState` 两个 WORD。是单点诊断 FB；批量看用 `FB_EcGetAllSlaveStates`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT; 
    bExecute   : BOOL; 
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 要查询的从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    state  : ST_EcSlaveState;     
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `state` | `ST_EcSlaveState` | 该从站状态：`deviceState` (状态机) + `linkState` (链路) |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `state`。期间需保持每周期调用本实例让 ADS 状态机推进，否则 `bBusy` 会卡在 TRUE。

**`ST_EcSlaveState` 结构含两个 WORD**：`deviceState` 表示从站状态机当前状态，取 INIT (0x01)、PREOP (0x02)、SAFEOP (0x04)、OP (0x08)，可能带错误位 (0x10)；`linkState` 表示物理链路状态，每个 bit 对应该从站某个端口的链路连接状况。两者一起看才能区分"从站本身在 OP 但链路某端口断开"这种典型故障。

**典型用法**：关键 EL 模块的状态作为业务前置条件，调本 FB 单点读后业务才放过；HMI 详情页点某从站查看其状态时调本 FB；状态切换流程结束后确认当前状态。

**典型陷阱**：与 `FB_EcGetAllSlaveStates` 区别在于批量 vs 单点 —— 批量场景用前者更省 ADS 调用。单点高频调用是允许的，1 ms 周期也不会显著影响主站负载，与读数组不同。判 OP 必须用 `state.deviceState = 16#0008` 等值判断，不要用 `>=`，因为带错误位的 `0x14`、`0x18` 也会满足 `>=`。

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `state` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **OP 判定 = 等号**：`state.deviceState = 16#08`，不要用 `>= 16#08`（含错误位的 0x14、0x12 等同样 >= 0x08）
- **`F_ConvSlaveStateToString` 友好显示**
- **配合 `FB_EcGetSlaveCrcError`**：状态正常但 CRC 计数涨 → 物理链路质量问题

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetSlaveState.TcPOU`](../examples/P_Demo_FB_EcGetSlaveState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：某 EL3008 是温度采集关键件，业务每次取温度前先调本 FB 判其是否在 OP；非 OP 直接报警并跳过本次采集
- **价值**：把"传感器健康度"做成业务前置；避免读到陈旧 PDO 数据
- **替代方案对比**：用 `FB_EcGetAllSlaveStates` → 拿到 12 个从站但只关心 1 个；本 FB → 精确单点

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57028107.html
- **相关 FB / FC**：`FB_EcGetAllSlaveStates`（批量）、`FB_EcReqSlaveState`、`FB_EcSetSlaveState`、`F_ConvSlaveStateToString`、`ST_EcSlaveState`
