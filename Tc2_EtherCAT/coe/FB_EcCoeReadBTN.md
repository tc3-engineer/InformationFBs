# FB_EcCoeReadBTN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531166731.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoeReadBTN.TcPOU`](../examples/P_Demo_FB_EcCoeReadBTN.TcPOU) |

---

## 1. 功能简述

通过 CoE 协议从从站对象目录 0xF083 读取 BTN（Beckhoff Traceability Number）。与 `FB_EcReadBTN` 走 ADS 直读 EEPROM 不同，本 FB 走 CoE 邮箱。8 字符 BTN 返回到 `STRING(9)`。

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
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    sBTN   : STRING(9)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS / CoE 错误码 |
| `sBTN` | `STRING(9)` | BTN 字符串（8 字符 + 终止符） |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 `FB_EcReadBTN` 区别**：CoE 路径 vs ADS 路径。本 FB 走 0xF083 CoE 对象，要求从站 PREOP+ 且对象字典含 0xF083。ADS 版 `FB_EcReadBTN` 直读 EEPROM，不需要 CoE 协议，但占用不同的 ADS 通道。日常运行态从站都在 OP，业务流量本来就走 CoE 邮箱，本 FB 与之共用路径无需额外开销。

**典型用法**：MES 中只采集 BTN 的简短版；与 `FB_EcCoeReadBIC` 选择 —— 仅 BTN 用本 FB（9 字节内存），要 BIC 完整字段用 ReadBIC 版（1023 字节）。

**典型陷阱**：
- 0xF083 不是所有从站都有
- 从站必须 PREOP+

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `sBTN` |
| CoE Abort `0x06020000` | 对象 0xF083 不存在 | 从站不支持 BTN |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **与 ADS 版选择**（工程经验补充）：运行态首选 CoE 版
- **STRING(9) 容量**：含终止符；8 字节恰好填满
- **作为售后追溯关键**：BTN 全球唯一，Beckhoff 售后系统直接按此查批次

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoeReadBTN.TcPOU`](../examples/P_Demo_FB_EcCoeReadBTN.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：从站故障返厂流程：HMI 显示该从站 BTN，维修员对照返厂申请 —— 本 FB 实时取，免拆机
- **价值**：内存友好的 BTN 单字段读取，CoE 路径
- **替代方案对比**：`FB_EcReadBTN` ADS 版 → 仅 INIT 时用；本 FB → 运行态首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11531166731.html
- **相关 FB / FC**：`FB_EcReadBTN`（ADS 版）、`FB_EcCoeReadBIC`
