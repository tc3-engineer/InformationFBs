# FB_EcCoeReadBIC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531165195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoeReadBIC.TcPOU`](../examples/P_Demo_FB_EcCoeReadBIC.TcPOU) |

---

## 1. 功能简述

通过 CoE 协议从指定从站对象目录 0x10E2:01 读取 BIC（Beckhoff Identification Code）。与 `FB_EcReadBIC` 走 ADS 直读 EEPROM 不同，本 FB 走 CoE 邮箱读对象字典，需要从站在 PREOP / SAFEOP / OP 且 0x10E2 对象存在。返回结构与 `FB_EcReadBIC` 一致（含原始字符串与已拆字段）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT; 
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    sBICValue : STRING
    stMSID    : ST_SplittedBIC;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS / CoE 错误码 |
| `sBICValue` | `STRING(1023)` | 原始 BIC 字符串 |
| `stMSID` | `ST_SplittedBIC` | 拆解后子字段（同 `FB_EcReadBIC`） |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 `FB_EcReadBIC` 区别**：本 FB 走 CoE 邮箱协议读 0x10E2:01；`FB_EcReadBIC` 走 ADS 直读 EEPROM。两条路径都拿到 BIC，但要求不同：
- CoE 版（本 FB）：从站必须在 PREOP+，且对象字典含 0x10E2，邮箱可用
- ADS 版：直读 EEPROM，从站任何状态都可读（甚至 INIT）

工程上多用本 CoE 版 —— 运行时从站都在 OP，CoE 邮箱可用。两者拿到的数据内容应一致（同一物理 BIC 字符串），路径不同仅是访问方式不同。

**典型用法**：MES 集成、装配下线身份采集。流程与 `FB_EcReadBIC` 完全一样。

**典型陷阱**：
- 0x10E2 不是所有从站都有 —— 老型号、第三方多数没有
- 从站 INIT 状态时本 FB 失败（邮箱不可用）；改用 `FB_EcReadBIC`

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `sBICValue` 与 `stMSID` |
| CoE Abort `0x06020000` | 对象不存在 | 该从站不支持 BIC，改用其他识别 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **从站状态**：必须 PREOP+
- **与 ADS 版选择**（工程经验补充）：运行时用 CoE 版；维护态 INIT 时用 ADS 版
- **拆解字段直接用**：`stMSID.sBTN` 等

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoeReadBIC.TcPOU`](../examples/P_Demo_FB_EcCoeReadBIC.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MES 集成场景，运行时定期采集所有从站 BIC 写入 MES。每个从站已在 OP，CoE 邮箱可用 —— 本 FB 是首选
- **价值**：运行时 CoE 路径采集 BIC，与日常诊断流量共用邮箱协议，无需额外 EEPROM 访问
- **替代方案对比**：`FB_EcReadBIC` ADS 直读 → 占用不同的 ADS 通道；本 FB → 共用 CoE 邮箱

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531165195.html
- **相关 FB / FC**：`FB_EcReadBIC`（ADS 版）、`FB_EcCoeReadBTN`、`ST_SplittedBIC`
