# FB_EcMasterFrameStatisticClearFrames

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57056907.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcMasterFrameStatisticClearFrames.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatisticClearFrames.TcPOU) |

---

## 1. 功能简述

清除主站中的"丢失帧"计数（`nLostFrames` 与 `nLostQueuedFrames`）。是配合 `FB_EcMasterFrameStatistic` 做"压力测试 / 故障处理后建立新基线"的工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId; 
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `bExecute` | `BOOL` | — | 上升沿触发一次清零 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

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
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后执行完毕。本 FB 与 `FB_EcMasterFrameStatisticClearCRC` 类似，但清零目标是"丢失帧计数"，不是"从站 CRC 计数"。

**与 ClearCRC 的区别**：
- `FB_EcMasterFrameStatisticClearCRC` 清的是各从站 ESC 内 CRC 寄存器
- 本 FB 清的是主站维护的丢失帧累计（即 `FB_EcMasterFrameStatistic.nLostFrames` 与 `nLostQueuedFrames`）

二者属性不同 —— 一个是从站层、一个是主站层；可分别清，也可一起清。日常做完整 baseline 重置应一起调用，避免一边清一边漏的情况。

**典型用法**：
- 压力测试前清 → 跑 → 读，得"该测试期纯净丢包数"
- 现场处理完 EMI 干扰源后清，验证后续是否还有丢失

**典型陷阱**：
- 与 ClearCRC 混淆：清 CRC 计数 ≠ 清 LostFrames
- 频繁清零让 KPI 不可比

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 已清零 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **清主站统计 vs 清从站 CRC**：明确不同；做完整 baseline 时通常两者都要清
- **不可回退**
- **工程态用**（工程经验补充）：日常运行避免

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcMasterFrameStatisticClearFrames.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatisticClearFrames.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：实验室验收测试，先用本 FB 清掉之前调试期间累积的 lost 计数，然后跑 1 小时压力测试，结束后读 `FB_EcMasterFrameStatistic.nLostFrames` 得"实际测试期丢包数"
- **价值**：让 KPI 数字可信，避免混入调试期噪声
- **替代方案对比**：重启主站 → 影响其他业务；本 FB → 仅清统计

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57056907.html
- **相关 FB / FC**：`FB_EcMasterFrameStatistic`（读统计）、`FB_EcMasterFrameStatisticClearCRC`、`FB_EcMasterFrameStatisticClearTxRxErr`
