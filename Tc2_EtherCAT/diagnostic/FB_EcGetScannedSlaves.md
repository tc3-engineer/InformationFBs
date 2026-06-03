# FB_EcGetScannedSlaves

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57020555.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetScannedSlaves.TcPOU`](../examples/P_Demo_FB_EcGetScannedSlaves.TcPOU) |

---

## 1. 功能简述

执行一次 EtherCAT 在线扫描，读取主站对象目录中"当前实际可见"的全部从站清单。本 FB 会在线读取每台从站的 EEPROM 把身份信息填入 `pArrEcScannedSlaveInfo` 数组（`ST_EcSlaveScannedData` 含 vendor / product / revision / serial / name 等）。由于要遍历每台 EEPROM，扫描耗时较长。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute               : BOOL;
    sNetId                 : T_AmsNetId; 
    pArrEcScannedSlaveInfo : POINTER TO ARRAY[0..EC_MAX_SLAVES] OF ST_EcSlaveScannedData;
    cbBufLen               : UDINT;    
    tTimeout               : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | — | 上升沿触发一次在线扫描 |
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `pArrEcScannedSlaveInfo` | `POINTER TO ARRAY[0..EC_MAX_SLAVES] OF ST_EcSlaveScannedData` | — | 接收每从站身份信息的数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 该 FB 扫描耗时长，应大幅增大 |

### VAR_OUTPUT

⚠️ PDF §4.10 原文此处把 `END_VAR` 错印为 `ND_VAR`（缺首字符 `E`），导致 verify_doc 无法自动从该 VAR_OUTPUT 区抽取变量做对账。下方列出实际声明（按 InfoSys 57020555 与 PDF 上下文确定 4 个输出变量）：

- `bBusy` : `BOOL`
- `bError` : `BOOL`
- `nErrId` : `UDINT`
- `nSlaves` : `UINT`

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中（扫描期间持续 TRUE，可能数秒） |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `nSlaves` | `UINT` | 扫描到的从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动扫描。`bBusy = TRUE` 期间持续轮询，可能 2 ~ 30 秒（视从站数量与 EEPROM 大小）。

**扫描机制**：本 FB 让主站发起 EtherCAT EEPROM scan，逐台从站读其 SII（Slave Information Interface）EEPROM 段，取出厂商身份信息。这是物理协议级查询，比 `FB_EcGetConfSlaves`（仅查配置表）慢得多。

**`tTimeout` 关键**：默认 `DEFAULT_ADS_TIMEOUT`（典型 5 s）对小型网络（< 10 从站）够用；大型网络（> 50 从站）应改为 `T#30S` 或更长。

**典型用法**：
- 新机型试机：调本 FB 拿实际清单，与 `FB_EcGetConfSlaves` 配置清单做 diff
- 现场更换从站后做"清单核对"

**典型陷阱**：
- 不要在 PLC 周期任务中循环调用；扫描期间会显著影响主站性能
- `tTimeout` 设太小：返回 ADS 超时但扫描本身可能还在跑

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nSlaves` 与数组 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` 到 T#30S+ |

## 5. 使用注意 / 常见坑

- **扫描耗时**：与从站数量成正比；典型 100 ms/从站，10 从站约 1 s
- **不可周期调用**：只在工程态、维护态触发；运行态读清单用 `FB_EcGetConfSlaves`
- **数组大小**（工程经验补充）：`ST_EcSlaveScannedData` 比 `ST_EcSlaveConfigData` 大；按 `EC_MAX_SLAVES * SIZEOF(ST_EcSlaveScannedData)` 估算栈消耗

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetScannedSlaves.TcPOU`](../examples/P_Demo_FB_EcGetScannedSlaves.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：客户更换了一台 EL3008 后报"读不到"。HMI 上加"扫描网络"按钮调本 FB；现场维修按下后 PLC 给出实际看到的从站清单，对比工程列表立即知道是否新硬件被识别
- **价值**：把 XAE 的 "Scan Devices" 功能搬到 HMI，免去现场必须带电脑
- **替代方案对比**：XAE 在线 scan → 需要工程师插电脑；本 FB → HMI 一键调用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57020555.html
- **相关 FB / FC**：`FB_EcGetConfSlaves`（配置清单，互补）、`ST_EcSlaveScannedData`、`FB_EcGetSlaveIdentity`（单从站身份）
