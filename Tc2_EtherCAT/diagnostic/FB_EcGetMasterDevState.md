# FB_EcGetMasterDevState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2895328139.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetMasterDevState.TcPOU`](../examples/P_Demo_FB_EcGetMasterDevState.TcPOU) |

---

## 1. 功能简述

读取 EtherCAT 主站设备的当前状态字。返回的 `nDevState` 是一个 16-bit WORD，每个 bit 含义不同（Link 状态、I/O 状态、frame 错误、超时等）；位为 0 即正常。该状态比"全部从站在 OP 没"更底层 —— 它反映主站底层硬件层（网卡、驱动）的健康度。

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
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID；本机用空串 `''` |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL; 
    bError    : BOOL;
    nErrId    : UDINT;
    nDevState : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `nDevState` | `WORD` | 主站设备状态位掩码：0 = 全部正常；非 0 = 至少有一位故障，用 `F_ConvMasterDevStateToString` 解码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `nDevState`。

**`nDevState` 与"从站 OP 状态"的区别**：
- 本 FB 看的是主站设备（网卡）级别的健康度：链路是否丢失、是否有 frame loss、驱动状态
- `FB_EcGetMasterState` 看的是 EtherCAT 状态机（INIT/PREOP/SAFEOP/OP）
- `FB_EcGetAllSlaveStates` 看的是从站状态

简单判定：`nDevState = 0` → 主站底层 OK；非 0 → 用 `F_ConvMasterDevStateToString` 把位掩码翻成可读字符串

**典型用法**：作为业务最顶层的"主站健康度" KPI；HMI 主页"网络状态"红绿灯一般绑这个字段，1 秒刷新一次足够给操作员看清趋势。

**典型陷阱**：
- `nDevState = 0` 不代表所有从站 OK；从站状态要看 `FB_EcGetAllSlaveStates`
- 主站重启瞬间 `nDevState` 可能短时非 0，建议平滑（连续 N 次非 0 才报警）
- 若 `bError = TRUE` 而非 `nDevState` 非 0，说明 ADS 调用本身失败（主站未启动等），需先排查主站任务

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nDevState` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| `6` / `7` | ADS port / target not found | 主站未启动 / 路由问题 |

## 5. 使用注意 / 常见坑

- **配合 `F_ConvMasterDevStateToString`**：直接显示位掩码无意义，必须用该转换 FC 解码为人类可读字符串
- **周期不宜过高**：1 s 已足够；高频读不会让你更早发现问题，只增 ADS 负载
- **作为最顶层指标**（工程经验补充）：HMI 主页一般绑这个 + `FB_EcGetMasterState`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetMasterDevState.TcPOU`](../examples/P_Demo_FB_EcGetMasterDevState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 主页"网络健康度"指示灯：绿 = 主站正常；黄 = 主站警告；红 = 主站异常。用本 FB 1 Hz 刷新
- **价值**：把底层网卡级状态抽象成业务可消费的红绿灯；不必让 HMI 工程师懂 EtherCAT 协议细节
- **替代方案对比**：`FB_EcGetMasterState` 看状态机；`FB_EcGetAllSlaveStates` 看从站；本 FB 看主站设备底层。三者一起做才完整

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2895328139.html
- **相关 FB / FC**：`F_ConvMasterDevStateToString`（位掩码 → 字符串）、`FB_EcGetMasterState`（状态机）
