# FB_EcReqSlaveState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57031179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcReqSlaveState.TcPOU`](../examples/P_Demo_FB_EcReqSlaveState.TcPOU) |

---

## 1. 功能简述

向指定从站发起状态切换请求。请求即返回（不等达成）。要等达成用 `FB_EcSetSlaveState`。除常规 INIT/PREOP/SAFEOP/OP 外还支持 BOOTSTRAP（固件升级用）和 ERROR（重置错误位）两个特殊状态。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId;
    nSlaveAddr : UINT;     
    bExecute   : BOOL; 
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
    state      : WORD; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次请求 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |
| `state` | `WORD` | — | 要请求的状态：0x01=INIT, 0x02=PREOP, 0x03=BOOTSTRAP, 0x04=SAFEOP, 0x08=OP, 0x10=ERROR (清错误位) |

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

**触发**：`bExecute` 上升沿；`bBusy` 短时为 TRUE 后落回；不等待从站实际状态变化。

**支持的 state 取值**：
- `EC_DEVICE_STATE_INIT` (0x01)：切到 INIT
- `EC_DEVICE_STATE_PREOP` (0x02)：切到 PREOP
- `EC_DEVICE_STATE_BOOTSTRAP` (0x03)：切到 BOOTSTRAP（固件升级模式）
- `EC_DEVICE_STATE_SAFEOP` (0x04)：切到 SAFEOP
- `EC_DEVICE_STATE_OP` (0x08)：切到 OP
- `EC_DEVICE_STATE_ERROR` (0x10)：清错误位（不切状态，仅复位错误标志）

**`ERROR` 状态的特殊用法**：从站发生错误（`state.deviceState & EC_DEVICE_STATE_ERROR = TRUE`）后，用 0x10 请求即可清错误位让从站恢复。这是从从站错误状态恢复的标准方式 —— 不需要把从站切回 INIT，仅清错误位即可。清完后多数情况下从站会自动回到之前的有效状态（如从 SAFEOP_ERR 自动回 SAFEOP）；如还需进一步到 OP，业务后续再单独发 OP 请求。

**典型陷阱**：
- 用本 FB 重新进 OP：先切 SAFEOP 再切 OP 较稳定；直接 INIT→OP 可能失败
- BOOTSTRAP：仅 FoE 固件升级时用，普通业务不要切
- 不等待返回，业务侧需轮询 `FB_EcGetSlaveState`

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 请求已发，poll 状态 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **错误恢复**：从站偶发掉 SAFEOP_ERR 时用 `state = 0x10` 清错误位
- **配合 SetSlaveState**（工程经验补充）：日常用 SetSlaveState 同步等结果；本 FB 用于"我不等"或固件升级流程
- **`nSlaveAddr` 必填**：用 `FB_EcGetAllSlaveAddr` 拿

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcReqSlaveState.TcPOU`](../examples/P_Demo_FB_EcReqSlaveState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：某 EL3204 偶发掉到 SAFEOP_ERR，PLC 端做自动恢复：监测 deviceState & 0x10 = TRUE → 用本 FB 发 `state = 0x10` 清错误位 → 等 200 ms → 再用 `FB_EcSetSlaveState` 切回 OP
- **价值**：从站偶发错误自动恢复无需重启工程
- **替代方案对比**：人工重启工程 → 影响生产；本 FB → 在线一键恢复

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57031179.html
- **相关 FB / FC**：`FB_EcSetSlaveState`（同步版）、`FB_EcGetSlaveState`、`FB_EcReqMasterState`
