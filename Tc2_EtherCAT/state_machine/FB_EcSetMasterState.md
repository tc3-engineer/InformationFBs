# FB_EcSetMasterState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57035787.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcSetMasterState.TcPOU`](../examples/P_Demo_FB_EcSetMasterState.TcPOU) |

---

## 1. 功能简述

请求并等待主站到达目标状态。本 FB 是"请求 + 同步等待"型 —— `bBusy` 保持 TRUE 直到状态切换完成或 `tTimeout` 超时。默认 timeout 10 s。是"必须确认切换完成"的同步场景标准 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId;
    bExecute : BOOL; 
    tTimeout : TIME := T#10s; 
    reqState : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `bExecute` | `BOOL` | — | 上升沿触发一次切换 |
| `tTimeout` | `TIME` | `T#10s` | 等待目标状态达成的最长时间 |
| `reqState` | `WORD` | — | 目标状态：0x01=INIT, 0x02=PREOP, 0x04=SAFEOP, 0x08=OP |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    currState : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中（持续到状态达成或超时） |
| `bError` | `BOOL` | 出错或超时置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `currState` | `WORD` | 当前主站状态；用于监视切换过程 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿。`bBusy` 保持 TRUE 直到：
- 主站达到 `reqState` → `bBusy = FALSE`, `bError = FALSE`, `currState = reqState`
- 超时 `tTimeout` → `bBusy = FALSE`, `bError = TRUE`, `currState = 最后已知状态`

**与 `FB_EcReqMasterState` 的关键区别**：
- 本 FB：等结果；适用于"必须确认完成"的同步流程（启动初始化、调试切换）
- ReqMasterState：发即返；适用于"不阻塞"场景

**`tTimeout` 默认 10 s 含义**：状态切换可能涉及全部从站状态同步，可能需要数秒；默认 10 s 应付绝大多数场景，复杂网络可加到 30 s。主站需要先让自己进入目标状态，再要求每个从站都进入该状态，才算切换完成 —— 任何一个从站超时都会让本 FB 超时报错。

**典型用法**：
- 上电启动序列：等主站到 OP 后才放过业务
- 维护态切换：调试时把主站切到 INIT 做配置

**典型陷阱**：
- `tTimeout` 设太短：复杂网络可能切换中超时
- 业务循环不能阻塞时不要用本 FB —— `bBusy` 期间会卡死调用方任务
- 超时不等于失败：可能主站还在切，再轮询确认

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 切换完成 |
| `1861` (`0x745`) | 切换超时 | 增大 `tTimeout` 或检查网络 |

## 5. 使用注意 / 常见坑

- **同步等待意味着阻塞**：`bBusy = TRUE` 期间调用方任务被卡；只在启动 / 维护态用
- **`currState` 可用于进度监视**：HMI 显示"正在切换：当前 PREOP，目标 OP"
- **配合 ReqMasterState 选择**（工程经验补充）：常规启动用本 FB；紧急切换用 ReqMasterState

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcSetMasterState.TcPOU`](../examples/P_Demo_FB_EcSetMasterState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上电启动序列：PLC 启动 → 调本 FB 等主站到 OP（最多 10 s）→ 完成后才放过业务程序去做后续动作。免去业务在主站半状态时跑出问题
- **价值**：把"启动 OP 确认"做成 1 行同步等待
- **替代方案对比**：用 ReqMasterState + 轮询 GetMasterState → 状态机复杂；本 FB → 一行搞定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57035787.html
- **相关 FB / FC**：`FB_EcReqMasterState`（异步版）、`FB_EcGetMasterState`、`FB_EcSetSlaveState`
