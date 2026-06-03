# FB_EcGetLastProtErrInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/8538584971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetLastProtErrInfo.TcPOU`](../examples/P_Demo_FB_EcGetLastProtErrInfo.TcPOU) |

---

## 1. 功能简述

读取某 EtherCAT 从站最近一次邮箱协议（CoE / FoE / SoE / EoE / AoE）失败的额外信息。每当该从站发送了一条邮箱命令并失败时，主站会记录最近一次错误细节（错误码、来源、辅助二进制描述等）；任何后续无错邮箱命令都会清掉这个"最近错误"。本 FB 把那份"最近错误"取出来用于诊断。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT;
    eProtocol  : E_EcMbxProtType := eEcMbxProt_FoE;
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 要查询的从站固定地址 |
| `eProtocol` | `E_EcMbxProtType` | `eEcMbxProt_FoE` | 邮箱协议类型：CoE/FoE/SoE 等 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    info   : ST_EcLastProtErrInfo; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `info` | `ST_EcLastProtErrInfo` | 含 `nErrCode`、`binDesc[]` 等字段；`binDesc` 是邮箱协议返回的扩展错误描述（CoE Abort Code、FoE Error String 等），可用 `BYTEARR_TO_MAXSTRING` 转字符串 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `info`。

**最近错误生命周期**：主站为每个从站每种协议维护一份"最近错误"。任何成功的同种协议邮箱命令都会清掉该错误（即使是一次无关的 CoE 读）。所以本 FB 必须在错误发生后立即调用，不能等业务里再调一遍 SDO 读再来查 ——已经被清了。

**典型用法**：
- `FB_EcCoeSdoRead` 报错（`bError = TRUE`），紧接着调本 FB 拿到 CoE Abort Code 的语义
- FoE 上传失败时拿厂商自定义的错误描述串

**典型陷阱**：
- 读完之后该错误依然保留（不是 read-and-clear）；下一次新错误才会覆盖
- 不同协议的"最近错误"独立维护：调本 FB 时 `eProtocol` 必须与失败时一致

## 4. 错误码 / 返回值

`info.nErrCode` 是邮箱协议错误码，含义按协议规范划分（PDF §14.3 列出了 EtherCAT mailbox protocol error codes 完整表）。`nErrId` 是 ADS 错误码：

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `info` 字段 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **立刻调用**：失败后立刻查，不要先做别的 SDO 读
- **`binDesc`**：是字节数组，转字符串用 `BYTEARR_TO_MAXSTRING(info.binDesc)`
- **不同 eProtocol 各有一份"最近错误"**：诊断 FoE 错误时必须 `eEcMbxProt_FoE`，CoE 错时 `eEcMbxProt_CoE`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetLastProtErrInfo.TcPOU`](../examples/P_Demo_FB_EcGetLastProtErrInfo.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：现场 FoE 固件升级失败，HMI 仅显示"FoE Write 失败"无法定位原因；用本 FB 取出最近一次 FoE 错误信息（如 "Disk full" / "Invalid PW"），HMI 直接显示给现场维修
- **价值**：把厂商协议级错误信息透传给上层应用，免去现场抄录 PCAP 抓包再人工解码
- **替代方案对比**：Wireshark 抓 EtherCAT 帧解析 → 慢且需要专家；本 FB 让 PLC 自动取出语义

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/8538584971.html
- **相关 FB / FC**：`ST_EcLastProtErrInfo`、`E_EcMbxProtType`、`FB_EcCoESdoAbortCode`
