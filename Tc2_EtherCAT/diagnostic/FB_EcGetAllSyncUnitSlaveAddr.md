# FB_EcGetAllSyncUnitSlaveAddr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/15660862603.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllSyncUnitSlaveAddr.TcPOU`](../examples/P_Demo_FB_EcGetAllSyncUnitSlaveAddr.TcPOU) |

---

## 1. 功能简述

读取属于指定 Sync Unit 的所有从站地址。Sync Unit 是 TwinCAT 把若干 EtherCAT 从站按业务分组、单独控制循环频率与同步组的逻辑单元；本 FB 给出某一个 Sync Unit 内具体含哪些从站。`nObjectId` 指定要查询的 Sync Unit ID（在 XAE 中可查），`pAddrBuf` 接收该 Unit 内全部从站固定地址。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId    : T_AmsNetId;
    nObjectId : OTCID;
    pAddrBuf  : POINTER TO ARRAY[0..EC_MAX_SLAVES] OF UINT; 
    cbBufLen  : UDINT; 
    bExecute  : BOOL; 
    tTimeout  : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | TwinCAT IPC 的 AMS NetID；本机用空串 `''` |
| `nObjectId` | `OTCID` | — | 要查询的 Sync Unit 的 Object ID（XAE 中可查） |
| `pAddrBuf` | `POINTER TO ARRAY[0..EC_MAX_SLAVES] OF UINT` | — | 接收该 Sync Unit 所有从站固定地址的数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量 |
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
| `nErrId` | `UDINT` | ADS 错误码；`1798` 空指针、`1797` 缓冲过小 |
| `nSlaves` | `UINT` | 该 Sync Unit 内从站数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**Sync Unit 概念**：TwinCAT 3 允许把全部 EtherCAT 从站按 task 划分到不同 Sync Unit，每个 Sync Unit 单独占一个 PLC task / cycle time。例如运动控制从站绑到 1 kHz task 的 SU_Motion，过程仪表绑到 100 Hz task 的 SU_Process。

**用途**：当工程需要"按 SU 分别诊断 / 报警" 时，先用 `F_EcGetLinkedTaskOfSyncUnit` 查 task 名拿到 `nObjectId`，再用本 FB 拿到该 Unit 内全部从站清单。

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读数组。

**典型陷阱**：
- 单 Sync Unit 工程时（绝大多数小工程）调本 FB 与 `FB_EcGetAllSlaveAddr` 结果一致
- `nObjectId` 不属于任何 Sync Unit 时返回 `nSlaves = 0`，不报错

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读数组 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **TwinCAT 版本要求**：v3.2.4024.14 + Tc2_EtherCAT ≥ 3.3.17.0
- **`nObjectId` 必填**：与单纯 `FB_EcGetAllSlaveAddr` 的差别就在这；空 OTCID 会查询失败
- **典型工程少见**：大部分小工程不分 Sync Unit；本 FB 仅在多 task 高动态范围工程中用得到

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllSyncUnitSlaveAddr.TcPOU`](../examples/P_Demo_FB_EcGetAllSyncUnitSlaveAddr.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：复杂工程含两个 task（1 kHz 运动 + 100 Hz 过程）各绑一个 Sync Unit；HMI 需要在 "运动 SU" tab 下只显示运动从站状态
- **价值**：把"哪些从站属于哪个 SU"的查询自动化，免去硬编码列表
- **替代方案对比**：在 XAE 视图手抄 → 工程变更后失同步；本 FB 给出运行时实际清单

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/15660862603.html
- **相关 FB / FC**：`FB_EcGetAllSlaveAddr`（全网从站清单）、`F_EcGetLinkedTaskOfSyncUnit`、`F_EcGetSyncUnitName`
