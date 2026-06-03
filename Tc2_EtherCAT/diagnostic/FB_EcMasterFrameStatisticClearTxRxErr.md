# FB_EcMasterFrameStatisticClearTxRxErr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57058443.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcMasterFrameStatisticClearTxRxErr.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatisticClearTxRxErr.TcPOU) |

---

## 1. 功能简述

清除主站对应 EtherCAT 网卡的 miniport 驱动错误计数（Tx/Rx 错误）。是清零三件套的第三件，针对网卡驱动层（不是从站、也不是主站统计层）。须传入 `nEcMasterDevID` 指定哪台主站设备。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId         : T_AmsNetId; 
    nEcMasterDevID : INT; 
    bExecute       : BOOL; 
    tTimeout       : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | CPU (IPC) 的 AMS NetID；本机用空串 |
| `nEcMasterDevID` | `INT` | — | EtherCAT 主站 Device ID（用 `FB_EcGetAllMasters` 或 `FB_EcMasterObjectID` 取） |
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

**触发**：`bExecute` 上升沿；`bBusy` 落沿后执行完毕。

**清零目标**：本 FB 清的不是 EtherCAT 协议层错误，而是网卡 miniport 驱动层的 Tx/Rx 错误计数 —— 如硬件发送失败、接收 FCS 错等。这些计数在 Windows 网卡设备管理器中也能看到，是底层硬件健康度指标。

**与其他 Clear 区别**：
- `FB_EcMasterFrameStatisticClearCRC` → 各从站 ESC CRC
- `FB_EcMasterFrameStatisticClearFrames` → 主站 lost frame 统计
- 本 FB → 网卡 miniport Tx/Rx 错误

**典型用法**：
- 现场怀疑网卡硬件或驱动问题（持续 Tx 错），先清零再观察短时趋势
- 整机重启前留底 baseline

**典型陷阱**：
- `nEcMasterDevID` 不是 `nSlaveAddr`！是主站设备 ID，单主站机典型 = 1，多主站机用 `FB_EcGetAllMasters` 拿
- 清零后无法恢复

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 已清零 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`nEcMasterDevID` 必填**：默认 0 在某些版本会被拒绝
- **多主站机**：每个主站独立清；要清全部需逐 DevID 调一次
- **底层硬件指标**（工程经验补充）：与 EtherCAT 协议层指标互补；高质量网卡应永远 0

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcMasterFrameStatisticClearTxRxErr.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatisticClearTxRxErr.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维修员怀疑某 IPC 主站网卡老化（持续少量 Tx Err 计数）；先清零再观察 30 分钟，若仍出现说明网卡需换
- **价值**：把"网卡是否健康"做成可观测对比测试
- **替代方案对比**：重启主机查看初始计数 → 影响生产；本 FB → 在线即可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.20
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57058443.html
- **相关 FB / FC**：`FB_EcMasterFrameStatisticClearCRC`、`FB_EcMasterFrameStatisticClearFrames`、`FB_EcMasterObjectID`、`FB_EcGetAllMasters`
