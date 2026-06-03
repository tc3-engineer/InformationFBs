# FB_EcGetAllSlavePresentStateChanges

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239481867.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllSlavePresentStateChanges.TcPOU`](../examples/P_Demo_FB_EcGetAllSlavePresentStateChanges.TcPOU) |

---

## 1. 功能简述

读取所有从站从 "slave is present" 状态切换到 "INIT_NO_COMM" 的累计计数。该切换发生时意味着与从站的通讯被中断（典型场景：拔掉 EtherCAT 网线）。`pAddrBuf` 数组按从站顺序填入每个从站的断线计数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId    :  T_AmsNetId;
    pAddrBuf  :  POINTER TO ARRAY [0..EC_MAX_SLAVES] OF UDINT;
    cbBufLen  :  UDINT;
    bExecute  :  BOOL;
    tTimeout  :  TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `pAddrBuf` | `POINTER TO ARRAY [0..EC_MAX_SLAVES] OF UDINT` | — | 接收每从站断线计数的数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量；至少 `nSlaves * 4` |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | — | ADS 调用超时 |

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
| `nErrId` | `UDINT` | ADS 错误码；`1798` 空指针、`1797` 缓冲过小 |
| `nSlaves` | `UINT` | 从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读数组。

**断线检测语义**：每个从站对应 UDINT 在主站启动后从 0 开始单调递增；每次该从站发生一次"present → INIT_NO_COMM"切换就 +1。典型触发原因：
- EtherCAT 网线被拔
- 链路上某中间从站掉电
- 从站本身硬件复位

**与 abnormal state changes 的区别**：
- `FB_EcGetAllSlaveAbnormalStateChanges`：状态降级（OP → SAFEOP_ERR 等），从站还在通讯
- 本 FB：通讯本身中断（从站不在了），更严重

**典型用法**：周期 1 Hz 调用，差值法监测"过去 1 秒有几个从站丢失通讯"；多用于现场可靠性 KPI 与 SCADA 报警。

**典型陷阱**：
- `tTimeout` 没有默认值，必须显式传 `DEFAULT_ADS_TIMEOUT`
- 主站重启计数清零；做 baseline 时记录起始值
- 短瞬时断线（几 ms）也计数，可能比你直觉预期更多

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 数组可读 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`tTimeout` 必须显式传入**：PDF 原型未带 `:= DEFAULT_ADS_TIMEOUT`，漏填会即时超时
- **差值算法**：日常做 Δ 累加；主站重启后 baseline 需重新建立
- **缓冲生命周期**（工程经验补充）：用全局或 FB 成员，不可栈变量

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllSlavePresentStateChanges.TcPOU`](../examples/P_Demo_FB_EcGetAllSlavePresentStateChanges.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：客户现场 EL3204 模块温度采集偶发"无数据"，怀疑网线接触不良；用本 FB 每秒读累计，做 1 分钟 Δ 报警阈值
- **价值**：把"哪台从站断线了几次"指标化，把"偶发故障"变成可观测可统计的数据
- **替代方案对比**：日志监听报警 → 漏 ms 级瞬时；本 FB 累计计数不丢

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239481867.html
- **相关 FB / FC**：`FB_EcGetAllSlaveAbnormalStateChanges`、`FB_EcGetAllSlaveStates`
