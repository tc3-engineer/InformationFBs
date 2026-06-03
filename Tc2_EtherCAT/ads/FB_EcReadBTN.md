# FB_EcReadBTN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS Interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531169803.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcReadBTN.TcPOU`](../examples/P_Demo_FB_EcReadBTN.TcPOU) |

---

## 1. 功能简述

通过 ADS 从 EtherCAT 从站 EEPROM 中读取 BTN（Beckhoff Traceability Number）单独字段。BTN 是 Beckhoff 工厂烧入的 8 字符可追溯标识。本 FB 只取 BTN（`STRING(9)`，含终止符共 9 字节）；要看完整 BIC 用 `FB_EcReadBIC`。

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
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    sBTN   : STRING(9);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `sBTN` | `STRING(9)` | BTN 字符串（8 字符 + 终止符），例 `"0002agdw"` |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `sBTN`。

**BTN 与 BIC 关系**：BTN 是 BIC 的一个子字段；本 FB 直接给 8 字节 BTN，省去解析 BIC 字符串的步骤。若只关心 BTN（追溯用），本 FB 比 `FB_EcReadBIC` 更省内存（9 字节 vs 1023 字节），对 PLC 内存敏感的小工程更合适。BTN 是 Beckhoff 全球唯一的追溯码，售后系统按 BTN 反查物料批次与产线日期最直接。

**典型用法**：
- 单点追溯：某从站坏了取下来时记录其 BTN 走售后流程
- MES 简短记录：只要 BTN 不要完整 BIC 时

**典型陷阱**：
- 老型号无 BTN 时返回空串
- 字符串 `STRING(9)` 容量含终止符；BTN 长度典型 8 字节恰好填满

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `sBTN` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| 其他 | EEPROM 读取失败 | 检查从站是否在线、是否有 BTN |

## 5. 使用注意 / 常见坑

- **与 `FB_EcReadBIC` 选择**：只要 BTN 用本 FB，要完整 BIC 用 BIC 版
- **与 `FB_EcCoeReadBTN` 区别**：本 FB 走 ADS 直读 EEPROM；CoE 版走 0xF083 对象字典
- **空串处理**（工程经验补充）：若 sBTN 长度为 0，说明该从站不支持 BTN

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcReadBTN.TcPOU`](../examples/P_Demo_FB_EcReadBTN.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：售后流程，客户某 EL 模块返厂，PLC 端先调本 FB 拿 BTN 自动填入返厂申请表，免去拆下来才能看背面贴的标签
- **价值**：内存友好（9 字节）的 BTN 单字段读取
- **替代方案对比**：拆机看标签 → 麻烦；`FB_EcReadBIC` → 拿全部但内存大

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531169803.html
- **相关 FB / FC**：`FB_EcReadBIC`（完整 BIC）、`FB_EcCoeReadBTN`（CoE 路径）
