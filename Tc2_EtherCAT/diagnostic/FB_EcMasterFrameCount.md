# FB_EcMasterFrameCount

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2895330059.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcMasterFrameCount.TcPOU`](../examples/P_Demo_FB_EcMasterFrameCount.TcPOU) |

---

## 1. 功能简述

读取主站配置中的 EtherCAT 帧总数。返回的 `nFrames` 是主站为完成一个循环所需要发送的帧数；该值取决于配置的从站数、PDO 大小、是否分包等。常用于评估主站任务负载或调整 sync 周期。

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
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy   : BOOL; 
    bError  : BOOL;
    nErrId  : UDINT;
    nFrames : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `nFrames` | `UDINT` | 主站配置的 EtherCAT 帧数（每循环发送数） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `nFrames`。

**`nFrames` 语义**：典型小型工程 = 1 或 2（一个 LRD + 一个 LWR）；从站多、PDO 大、跨 Sync Unit 时会分多个 EtherCAT 帧才能装下。`nFrames` 直接决定每循环以太网占用率：1 ms 周期下 nFrames=1 占大约 1 % 带宽，nFrames=10 占大约 10 %。当 nFrames 比预期增大时通常意味着工程添加了从站或 PDO 数据扩大，需要重新评估循环周期。

**典型用法**：
- 工程评估：调本 FB 把 `nFrames` 与机型期望对比，配置改大了立即知道
- 网络负载估算：`nFrames * frame_size * 1000 / cycleTime_us` ≈ 占用带宽
- 调优依据：`nFrames` 过大说明 PDO 太多，可能需要拆分 Sync Unit

**典型陷阱**：
- 本 FB 给出的是"配置"帧数，不是"实际发送"帧数
- 主站重启后立即调用：值可能还没初始化，建议主站 IO 启动后再调

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nFrames` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **静态查询**：`nFrames` 在主站启动后基本不变；周期高频读无意义
- **配合 `FB_EcMasterFrameStatistic`**：本 FB 给"应发数"，那个 FB 给"实发数 + 丢失数"，两者结合做"丢包率"
- **作为容量指标**（工程经验补充）：日常做 `nFrames < 5` 即正常的快速判定

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcMasterFrameCount.TcPOU`](../examples/P_Demo_FB_EcMasterFrameCount.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工程师怀疑某机型 EtherCAT 任务超时是因为 PDO 配置过大；调本 FB 拿 `nFrames`，预算每循环占用带宽确定是否网络层瓶颈
- **价值**：把"网络是否拥堵"问题转化为可观测的数字
- **替代方案对比**：人工估算 → 易错；本 FB → 自动

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.16
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2895330059.html
- **相关 FB / FC**：`FB_EcMasterFrameStatistic`（实发统计）、`FB_EcMasterFrameStatisticClearCRC`
