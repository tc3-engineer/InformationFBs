# FB_EcGetSlaveIdentity

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57017483.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetSlaveIdentity.TcPOU`](../examples/P_Demo_FB_EcGetSlaveIdentity.TcPOU) |

---

## 1. 功能简述

读取指定从站的 CANopen 身份信息（vendor ID、product code、revision、serial number 等）。返回 `ST_EcSlaveIdentity` 结构。用于"这台从站是什么型号、什么版本、什么序列号"的运行时确认。

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
| `nSlaveAddr` | `UINT` | — | 要查询的从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrId   : UDINT;
    identity : ST_EcSlaveIdentity; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `identity` | `ST_EcSlaveIdentity` | CANopen 身份信息：`vendorId`、`productCode`、`revisionNumber`、`serialNumber`（详见 §13.9） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `identity`。

**身份信息来源**：从从站 EEPROM（SII）读取，不依赖工程配置 —— 即使工程配置与现场实物不一致，本 FB 给出现场实物的真值。是验证"装的是不是我期望那个型号"最权威的途径。

**典型用法**：
- 工程更换从站后做型号确认（防止装错型号引发 PDO 映射错配）
- 序列号采集：在 MES 系统中归档"本机用了哪台具体序列号的硬件"
- 配合 `F_CheckVendorId`（仅判断是不是 Beckhoff）做厂商白名单校验

**典型陷阱**：
- `serialNumber` 字段不是所有从站都会填（取决于厂商 EEPROM 写入）；某些第三方从站为 0
- `revisionNumber` 与 product code 配对决定 ESI 文件版本；可用于固件版本追踪
- 本 FB 不依赖工程配置，但依赖现场可达（从站离线时报 ADS 错误）

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `identity` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| 从站未响应 | 从站不在线或地址错 | 先用 `FB_EcGetAllSlaveAddr` 验证地址 |

## 5. 使用注意 / 常见坑

- **与 `FB_EcGetConfSlaves` 区别**：后者读"主站配置表"（工程视图）；本 FB 读"现场从站 EEPROM"（实物视图）。两者 diff 即"配置 vs 实物"
- **Vendor ID 速查**：Beckhoff = `16#00000002`、Siemens = `16#0000002A`、Yaskawa = `16#00000539`
- **作为身份戳**（工程经验补充）：MES 集成时把 `serialNumber` 当唯一硬件标识；缺序列号的从站需配合外部 RFID 或扫码

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetSlaveIdentity.TcPOU`](../examples/P_Demo_FB_EcGetSlaveIdentity.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：装配线下线检验：每台机 PLC 启动后调本 FB 把每台从站序列号写入 MES，建立"机器序列号 → 部件序列号"溯源表
- **价值**：自动化采集硬件身份，免去人工扫码贴标签
- **替代方案对比**：人工抄录硬件标签 → 易错且慢；XAE 在线查看 → 单台可，批量不可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57017483.html
- **相关 FB / FC**：`F_CheckVendorId`（厂商判断）、`F_ConvProductCodeToString`、`ST_EcSlaveIdentity`
