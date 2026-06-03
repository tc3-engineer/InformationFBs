# FB_EcGetSlaveCount

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57015947.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetSlaveCount.TcPOU`](../examples/P_Demo_FB_EcGetSlaveCount.TcPOU) |

---

## 1. 功能简述

读取主站连接的从站总数。是最轻量的 EtherCAT 诊断 FB，仅返回一个 `UINT` 计数。比 `FB_EcGetAllSlaveAddr` 等"枚举类" FB 调用更快、占资源更少；适用于"我只想知道有几台" 的快速健康检查。

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
    nSlaves : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `nSlaves` | `UINT` | 主站连接的从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `nSlaves`。

**与其他 FB 的关系**：本 FB 与 `FB_EcGetAllSlaveAddr` / `FB_EcGetConfSlaves` 都返回 `nSlaves` 字段；本 FB 是最轻量版本，不需要传缓冲区数组，纯查询数字，因而调用更便宜也更适合周期高频读。注意"连接的"含义是当前在 EtherCAT 主站缓存中存在的从站数，与 `FB_EcGetConfSlaves` 返回的"工程文件中配置数"可能不同，前者会受现场实际连通性影响。

**典型用法**：
- 周期 1 Hz 调用做"连接从站数"监测；与期望值偏差时报警"丢从站"
- 自动化测试程序的"网络初始化完成"判定：等 `nSlaves` 等于期望数才继续

**典型陷阱**：
- "连接" = 主站当前能寻址到的从站数；偶发瞬时连接 / 断开会导致计数波动
- 与 `FB_EcGetConfSlaves` 返回的"配置数"做 diff：差 ≥ 1 → 有从站离线

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nSlaves` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| `6` / `7` | ADS port / target not found | 主站未启动 / 路由问题 |

## 5. 使用注意 / 常见坑

- **最便宜的诊断**：本 FB 是单字段返回，比 `FB_EcGetAllSlaveAddr` 调用快很多；周期高频也无压力
- **与配置数对比**：单独 `nSlaves` 数值无意义，必须知道"期望多少台"才能判故障；配合 `FB_EcGetConfSlaves` 或代码里写死期望值
- **作为预热判定**（工程经验补充）：上电启动 → 循环调用直到 `nSlaves >= EXPECTED` → 启动业务

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetSlaveCount.TcPOU`](../examples/P_Demo_FB_EcGetSlaveCount.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：批量装配线 PLC 上电后启动顺序：等所有从站上线再开始业务。用本 FB 每 100 ms 读一次，等 `nSlaves = 12`（机型期望值）才把"系统就绪"位置 TRUE
- **价值**：把"系统初始化完成"判定形式化，免去 sleep 或固定延时
- **替代方案对比**：固定 sleep T#5S → 慢机型不够、快机型浪费；本 FB → 自适应

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57015947.html
- **相关 FB / FC**：`FB_EcGetAllSlaveAddr`、`FB_EcGetConfSlaves`、`FB_EcGetAllSlaveStates`
