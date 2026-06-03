# FB_EcMasterObjectID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/20212712843.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcMasterObjectID.TcPOU`](../examples/P_Demo_FB_EcMasterObjectID.TcPOU) |

---

## 1. 功能简述

读取 EtherCAT 主站设备的 Object ID。Object ID 是 TwinCAT 系统内主站的唯一引用，许多 FC 用它作为输入（如 `F_EcGetMailboxGatewayAddr`）。本 FB 是把"AMS NetID"映射到"Object ID"的桥梁。

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
    bBusy       : BOOL; 
    bError      : BOOL;
    nErrId      : UDINT;
    oidEcMaster : OTCID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `oidEcMaster` | `OTCID` | 该 EtherCAT 主站的 Object ID |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `oidEcMaster`。

**OTCID 概念**：TwinCAT 3 系统内为每个对象（主站、Sync Unit、Task 等）分配一个 32-bit Object ID。许多 PLC 库的 FC 接受 OTCID 作为入参；本 FB 就是把"我用 NetID 知道的主站"翻译成"我用 OTCID 引用的主站"。OTCID 在系统启动后保持稳定，工程师通常把它取一次放进 GVL 供整套诊断代码复用，无需周期重读。

**典型用法**：
- 在调用 `F_EcGetMailboxGatewayAddr` / `FB_EcMasterFrameStatisticClearTxRxErr` 等需要 OTCID 的 FC 前，先调本 FB
- 工程师从 NetID 开始排查时常作为"翻译跳板"

**典型陷阱**：
- TwinCAT 版本要求：v3.1.4024.56 + Tc2_EtherCAT ≥ 3.7.1.0
- `oidEcMaster = 0` 表示未找到对应主站；检查 `sNetId` 与路由

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `oidEcMaster` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| `7` | ADS target not found | `sNetId` / 路由问题 |

## 5. 使用注意 / 常见坑

- **版本要求严格**：低于 3.7.1.0 调本 FB 会失败
- **作为查询前置**：很多需 OTCID 的 FC 都依赖本 FB；写"诊断脚本"时先存 `oidEcMaster` 到 GVL
- **`FB_EcGetAllMasters` vs 本 FB**（工程经验补充）：前者列全部主站；本 FB 转某一台 NetID → OTCID

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcMasterObjectID.TcPOU`](../examples/P_Demo_FB_EcMasterObjectID.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 需要显示主站对应物理网卡的 IP / MAC（mailbox gateway 用），先调本 FB 拿 OTCID，再调 `F_EcGetMailboxGatewayAddr`
- **价值**：把 NetID（AMS 路由层）与 OTCID（TwinCAT 对象层）打通
- **替代方案对比**：人工查 XAE → 慢；本 FB → 一次 ADS 调用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.21
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/20212712843.html
- **相关 FB / FC**：`F_EcGetMailboxGatewayAddr`、`FB_EcGetAllMasters`、`FB_EcMasterFrameStatisticClearTxRxErr`
