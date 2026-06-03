# FB_EcMasterFrameStatisticClearCRC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57055371.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcMasterFrameStatisticClearCRC.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatisticClearCRC.TcPOU) |

---

## 1. 功能简述

清除主站连接的所有 EtherCAT 从站的 CRC 错误计数。是"压力测试前后做对比"和"现场处理完物理故障后重置 KPI"的关键工具。

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

**触发**：`bExecute` 上升沿启动一次清零；`bBusy` 落沿后执行完毕。本 FB 没有"读取" —— 清零是单向操作。

**清零范围**：主站连接的所有从站 ESC 内 CRC 计数寄存器（不仅是某一个端口）。等同对每个从站发送一次 FPWR 清零命令。

**典型用法**：
- 物理层故障处理完（换网线、重做端接）后清零，建立新基线
- 压力测试：清零 → 跑测试 → 再读 `FB_EcGetAllSlaveCrcErrors`，得出"测试期间纯净计数"

**典型陷阱**：
- 清零是即时的，没有"软清零选项"
- 频繁清零会让历史 KPI 不可比；只在工程态调

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 已清零 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **不可回退**：清零后无法恢复原计数；操作前如需历史值，先调 `FB_EcGetAllSlaveCrcErrors` 备份
- **运行态慎用**：会让在线 KPI 看板出现"突降"
- **配合 `FB_EcGetAllSlaveCrcErrors`**：清零前后读做"该测试期间真实计数"（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcMasterFrameStatisticClearCRC.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatisticClearCRC.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维修员现场换完一根可疑网线后，HMI 按"重置 CRC 计数"按钮调本 FB；后续 1 小时若计数仍涨说明换错线了
- **价值**：把"网线问题处理后验证"做成自动化流程
- **替代方案对比**：重启主站 → 影响生产；本 FB → 在线清零

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57055371.html
- **相关 FB / FC**：`FB_EcGetAllSlaveCrcErrors`（读 CRC）、`FB_EcMasterFrameStatisticClearFrames`、`FB_EcMasterFrameStatisticClearTxRxErr`
