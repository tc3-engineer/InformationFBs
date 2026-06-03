# FB_EcMasterFrameStatistic

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57053835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcMasterFrameStatistic.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatistic.TcPOU) |

---

## 1. 功能简述

读取主站的 EtherCAT 帧统计：分别给出循环帧和非循环（队列）帧的丢失数与每秒帧速率。非循环帧用于初始化和参数访问；循环帧承载 PDO。丢失或无效（CRC 错、超时未回）的帧记入 lost 计数。是网络层带宽 / 丢包率的核心指标。

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
    bBusy                  : BOOL;
    bError                 : BOOL;
    nErrId                 : UDINT;
    nLostFrames            : UDINT;
    fFramesPerSecond       : LREAL;
    nLostQueuedFrames      : UDINT;
    fQueuedFramesPerSecond : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `nLostFrames` | `UDINT` | 累计丢失或无效的循环帧数 |
| `fFramesPerSecond` | `LREAL` | 当前循环帧速率（帧/秒） |
| `nLostQueuedFrames` | `UDINT` | 累计丢失或无效的非循环（队列）帧数 |
| `fQueuedFramesPerSecond` | `LREAL` | 当前队列帧速率（帧/秒） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读各计数。

**循环帧与队列帧的区分**：
- 循环帧（cyclic）是主站任务每周期下发的 PDO 数据帧，`fFramesPerSecond` 应稳定地等于 `1 / cycle_time` 的倒数。例如 1 kHz 任务期望约 1000 fps
- 队列帧（acyclic / queued）由初始化、SDO 访问、FoE 等异步操作触发，速率波动是正常的，主要看 lost 数

主站不会区分哪些帧"应到没到" —— 只看回执是否在超时窗口内返回；超时未回或 CRC 错的帧都会被记入 lost 计数。

**判定标准**：
- `nLostFrames` 持续增长 → 网络层故障（CRC 错、线缆、终端电阻等）
- `fFramesPerSecond` 显著低于 `1 / cycle_time` → 主站任务超时
- `nLostQueuedFrames` 增长 → mailbox 协议层故障（CoE / FoE 等丢失）

**典型用法**：周期 1 Hz 调用 + 计 Δ 做"网络丢包率"KPI；连接 SCADA 报表。

**典型陷阱**：
- 计数是累计值，做差才有当前丢包率
- 主站 reset 后清零；做 baseline

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读统计字段 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **diff 算法**：日常做 Δ，单次值无判定意义
- **lost 与 CRC 不一样**：`nLostFrames` 是"没回主站"；`FB_EcGetAllSlaveCrcErrors` 是"从站端口 CRC 错"；两者可能同时发生也可能只发生其一
- **配合清零** FB：`FB_EcMasterFrameStatisticClearFrames` 可清 lost 计数，做"压力测试 前后对比"

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcMasterFrameStatistic.TcPOU`](../examples/P_Demo_FB_EcMasterFrameStatistic.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：客户现场 EtherCAT 任务偶发丢周期，看不出原因；用本 FB 每秒读一次，把 `nLostFrames` 增量推 HMI；找到"每天 14:00 准时增长" → 定位是某车间大功率负载启动干扰
- **价值**：把"偶发不稳"变成可观测时序数据
- **替代方案对比**：Wireshark 抓包 → 持续抓海量数据慢；本 FB → 累计计数差值化简

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57053835.html
- **相关 FB / FC**：`FB_EcMasterFrameStatisticClearCRC`、`FB_EcMasterFrameStatisticClearFrames`、`FB_EcMasterFrameStatisticClearTxRxErr`
