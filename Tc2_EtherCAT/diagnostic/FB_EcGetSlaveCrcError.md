# FB_EcGetSlaveCrcError

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57014411.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetSlaveCrcError.TcPOU`](../examples/P_Demo_FB_EcGetSlaveCrcError.TcPOU) |

---

## 1. 功能简述

读取指定从站三端口（A、B、C）的 CRC 错误计数细节。返回 `ST_EcCrcError` 结构含每个端口独立计数。本 FB 仅适用于 3 端口及以下从站（典型 EK1100）；4 端口从站（EK1122 等）须用 `FB_EcGetSlaveCrcErrorEx`。

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
    crcError : ST_EcCrcError; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `crcError` | `ST_EcCrcError` | 三端口 CRC 错误计数（含 A/B/C 端口各 1 个 BYTE，详见 §13.4） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `crcError`。

**与 Ex 版区别**：本 FB 仅返回 A/B/C 三端口计数；4 端口从站（EK1122 含额外的 D 端口）务必用 `FB_EcGetSlaveCrcErrorEx`，否则 D 端口故障无法被发现，是日常诊断中容易踩的坑。物理上 A 端口连接上游主站方向，B 端口连接下游级联从站方向，C 端口对应 E-Bus 出端进入背板模块。

**典型用法**：
- `FB_EcGetAllSlaveCrcErrors` 报某从站汇总值 > 0 后，针对该从站调本 FB 进一步看是 A/B/C 哪个端口有问题
- A 端口 = 上游（接来源）、B 端口 = 下游（接续端），定位是上游还是下游链路质量问题

**典型陷阱**：
- 用错版本（EK1122 调本 FB）→ D 端口故障漏检
- 计数是 BYTE，到 255 饱和；现场长期累计需要主站定期清零

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `crcError` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| 其他 | ADS / 总线错误 | 查 Beckhoff『ADS Return Codes』 |

## 5. 使用注意 / 常见坑

- **3 端口限定**：仅 EK1100 / EL 系列单链耦合器等；EK1122 等分支耦合器必须用 Ex 版
- **BYTE 饱和**：长期运行计数到 255 后停在 255，无法判增量；可结合主站 reset 重置
- **端口对应物理接口**（工程经验补充）：A 端口典型对应"上游 RJ45"，B 端口对应"下游"，C 端口对应"E-Bus 出端"。具体型号请查从站手册

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetSlaveCrcError.TcPOU`](../examples/P_Demo_FB_EcGetSlaveCrcError.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：`FB_EcGetAllSlaveCrcErrors` 报某 EK1100 汇总计数 = 5；用本 FB 查该 EK1100 分别看：A=0 / B=5 / C=0 → 下游链路问题
- **价值**：把 CRC 故障精确到端口级，缩小排查范围
- **替代方案对比**：直接 FPRD 读 ESC 0x0300 ~ 0x030F → 需要手算偏移；本 FB → 一次调用拿结构体

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57014411.html
- **相关 FB / FC**：`FB_EcGetSlaveCrcErrorEx`（4 端口）、`FB_EcGetAllSlaveCrcErrors`（全网汇总）、`ST_EcCrcError`
