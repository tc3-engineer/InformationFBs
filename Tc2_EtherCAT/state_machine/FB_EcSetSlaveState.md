# FB_EcSetSlaveState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57034251.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcSetSlaveState.TcPOU`](../examples/P_Demo_FB_EcSetSlaveState.TcPOU) |

---

## 1. 功能简述

请求并等待指定从站到达目标状态。同步等待版（对 `FB_EcReqSlaveState` 的异步版）。`bBusy` 保持 TRUE 直到从站达成目标或 `tTimeout` 超时。`currState` 输出的是 `ST_EcSlaveState` 结构（比 SetMasterState 输出的 WORD 更详细）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId;
    nSlaveAddr : UINT;     
    bExecute   : BOOL; 
    tTimeout   : TIME := T#10s; 
    reqState   : WORD; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次切换 |
| `tTimeout` | `TIME` | `T#10s` | 等待状态达成最长时间 |
| `reqState` | `WORD` | — | 目标状态：0x01=INIT, 0x02=PREOP, 0x03=BOOTSTRAP, 0x04=SAFEOP, 0x08=OP, 0x10=ERROR (清错误位) |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    currState : ST_EcSlaveState;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错或超时置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `currState` | `ST_EcSlaveState` | 从站当前状态（含 deviceState 与 linkState） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿。`bBusy` 保持 TRUE 直到目标达成或超时。

**与 `FB_EcReqSlaveState` 区别**：
- 本 FB：同步等待，业务流程必须等
- ReqSlaveState：异步发送，不等结果

**`currState` 字段**：是 `ST_EcSlaveState` 不是单个 WORD，含 `deviceState`（状态机）与 `linkState`（链路）两个 WORD，比 SetMasterState 的 `WORD currState` 信息更丰富。这让业务在切换过程中可同时看到"状态机进展"与"物理链路是否在线"，对诊断"从站没切过去到底是状态机卡了还是链路断了"非常有用。

**典型用法**：
- 固件升级前把目标从站切到 BOOTSTRAP（用 reqState = 0x03），同步等切完才开 FoE
- 错误恢复完整流程：clear ERROR → wait → set OP，最后一步用本 FB 同步等

**典型陷阱**：
- 单从站可能因总线问题切不到目标，超时报错
- 切到 BOOTSTRAP 后必须 FoE 完成再切回 INIT 再 OP，否则该从站不工作
- `bBusy` 期间阻塞，与 SetMasterState 一样

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 切换完成 |
| `1861` (`0x745`) | 切换超时 | 增大 `tTimeout` 或检查从站健康 |

## 5. 使用注意 / 常见坑

- **`currState` 是结构体**：用 `currState.deviceState` 取状态值
- **BOOTSTRAP 用法**：仅 FoE 固件升级；升级完务必恢复到 OP
- **配合 ReqSlaveState 选择**（工程经验补充）：必须确认切完用本 FB；不等用 Req

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcSetSlaveState.TcPOU`](../examples/P_Demo_FB_EcSetSlaveState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：FoE 固件升级流程：第一步本 FB 切目标从站到 BOOTSTRAP；第二步 `FB_EcFoeLoad` 写新固件；第三步本 FB 切回 INIT 然后 OP。每步同步等
- **价值**：状态切换 + 等待结果 一行搞定，固件升级流程清晰
- **替代方案对比**：ReqSlaveState + 轮询 GetSlaveState → 状态机复杂；本 FB → 同步

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57034251.html
- **相关 FB / FC**：`FB_EcReqSlaveState`（异步版）、`FB_EcGetSlaveState`、`FB_EcFoeLoad`
