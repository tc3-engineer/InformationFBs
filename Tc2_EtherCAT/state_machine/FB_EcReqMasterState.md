# FB_EcReqMasterState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57032715.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcReqMasterState.TcPOU`](../examples/P_Demo_FB_EcReqMasterState.TcPOU) |

---

## 1. 功能简述

向主站发起状态切换请求。本 FB 是"请求即返回"型 —— 命令发出后立即变 idle，不等待主站真正达到目标状态。要等达到目标状态需用 `FB_EcSetMasterState`。常用于"我要切换但不等结果"的快速命令场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId;
    bExecute : BOOL; 
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
    state    : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `bExecute` | `BOOL` | — | 上升沿触发一次请求 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |
| `state` | `WORD` | — | 要请求的主站状态：0x01=INIT, 0x02=PREOP, 0x04=SAFEOP, 0x08=OP |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中（短时） |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 短时为 TRUE 然后落回；不等待主站实际状态变化。

**与 `FB_EcSetMasterState` 的关键区别**：
- 本 FB（Req）：发送请求即完成；适用于"切换命令快速返回"或"主调度循环不能阻塞"
- `FB_EcSetMasterState`：发送 + 等待目标状态达成；适用于"必须确认切换完成"的同步场景

调用者必须自行设计后续状态轮询。本 FB 不会告诉你"切换成功了" —— 只告诉你"我把命令发出去了"。要确认真的切到位，业务侧必须接 `FB_EcGetMasterState` 周期轮询并判定 `state = reqState`。

**典型用法**：
- 紧急 INIT：业务异常时立即把主站切到 INIT 切断 PDO；不等切完业务先去做错误处理
- 复杂工程：上层调度循环不能阻塞，分两步：req → poll 状态

**典型陷阱**：
- `bBusy = FALSE` 不等于"切换成功"，仅代表"请求已发出"；要确认状态用 `FB_EcGetMasterState` 后续轮询
- `state = 0` 或不在 INIT/PREOP/SAFEOP/OP 中：未定义行为
- 上电后状态机不在 OP 时调用本 FB 请求 OP，可能跳过中间转换报错

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 请求已发，开始 poll 状态 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **不阻塞 ≠ 即时生效**：状态切换可能需要几百 ms，应轮询 `FB_EcGetMasterState` 确认
- **配合 SetState 模式选择**（工程经验补充）：日常用 SetState；只在不能阻塞场景用 Req
- **`EC_DEVICE_STATE_*` 常量**：用 GVL 常量避免硬编码

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcReqMasterState.TcPOU`](../examples/P_Demo_FB_EcReqMasterState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：紧急停止按钮按下，业务流程要立即把主站切到 INIT 切断所有 PDO，PLC 主循环不能等切换完成（要立刻去做其他紧急处理）。用本 FB 异步请求 INIT
- **价值**：非阻塞性命令，让上层程序不会被状态切换卡死
- **替代方案对比**：`FB_EcSetMasterState` 等待返回 → 上层阻塞；本 FB → 立即返回

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57032715.html
- **相关 FB / FC**：`FB_EcSetMasterState`（同步版）、`FB_EcGetMasterState`（读当前状态）、`FB_EcReqSlaveState`（单从站异步）
