# FB_EcReadBIC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS Interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531168267.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcReadBIC.TcPOU`](../examples/P_Demo_FB_EcReadBIC.TcPOU) |

---

## 1. 功能简述

通过 ADS 从 EtherCAT 从站 EEPROM 中读取 BIC（Beckhoff Identification Code）字符串。BIC 是 Beckhoff 工厂烧入 EEPROM 的可追溯标识，含物料号、BTN（Beckhoff Traceability Number）、产品描述、数量、批号。本 FB 同时输出原始 BIC 字符串和已拆解的结构。从站 EEPROM 中必须含 BIC 才能读到（较老型号或第三方从站可能没有）。

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
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    sBICValue : STRING(1023);
    stMSID    : ST_SplittedBIC;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `sBICValue` | `STRING(1023)` | 原始 BIC 字符串，如 `"1P193995SBTN0002agdw1KEL7411   Q1  2P112104020018"` |
| `stMSID` | `ST_SplittedBIC` | 拆解后的子字段：`sItemNo`、`sBTN`、`sDescription`、`sQuantity`、`sBatchNo` |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `sBICValue` 与 `stMSID`。

**BIC 字符串格式**：Beckhoff Identification Code 是按 ETG 规范定义的可追溯标识，常见结构：
- `1P...` 物料号（item number）
- `SBTN...` Beckhoff Traceability Number（BTN）
- `1K...` 描述（product name）
- `Q1` 数量
- `2P...` 批号（batch number）

本 FB 把上述子段已拆好放在 `stMSID` 里，调用方直接用结构字段，免去自己解析字符串。`stMSID` 字段命名直接对应 ETG 子段（`sItemNo`、`sBTN`、`sDescription`、`sQuantity`、`sBatchNo`），与 BIC 字符串中的标签字符一一对照。

**典型用法**：
- MES 集成：装配下线扫描 BIC 写入 MES "本机配件溯源"表
- 工程审核：周期性确认安装的部件与采购单一致

**典型陷阱**：
- 从站 EEPROM 必须含 BIC，老型号 / 第三方从站可能为空，返回空串
- `sBICValue` 1023 字节较大，PLC 内存占用要考虑
- BIC 字符串首尾可能含空白，处理时 trim

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `sBICValue` 与 `stMSID` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| 其他 | EEPROM 读取失败 | 检查从站是否在线、是否支持 BIC |

## 5. 使用注意 / 常见坑

- **与 `FB_EcCoeReadBIC` 区别**：本 FB 走 ADS 读 EEPROM；`FB_EcCoeReadBIC` 走 CoE 邮箱读 0x10E2 对象。两者数据源不同，BIC 内容相同但访问路径不同
- **拆解后字段更易用**（工程经验补充）：直接用 `stMSID.sBTN` 即可，免去解析
- **从站必须 OP / PREOP**：INIT 状态下邮箱不可用，本 FB 读不到

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcReadBIC.TcPOU`](../examples/P_Demo_FB_EcReadBIC.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：装配下线检验，PLC 调本 FB 读所有从站 BIC，写入 MES "本机配件溯源" 表，未来若某批次出问题可按 BTN 反查具体在哪台
- **价值**：自动化采集 BIC + 已拆解结构，免去人工扫码与字符串解析
- **替代方案对比**：手工扫码 → 慢且易错；`FB_EcCoeReadBIC`走 CoE → 路径不同但内容同

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531168267.html
- **相关 FB / FC**：`FB_EcReadBTN`、`FB_EcCoeReadBIC`（CoE 路径）、`FB_EcCoeReadBTN`、`ST_SplittedBIC`
