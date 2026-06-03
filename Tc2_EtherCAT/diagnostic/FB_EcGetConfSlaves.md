# FB_EcGetConfSlaves

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57019019.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetConfSlaves.TcPOU`](../examples/P_Demo_FB_EcGetConfSlaves.TcPOU) |

---

## 1. 功能简述

读取主站对象目录中所有"已配置"从站的详细信息清单。每个从站返回一个 `ST_EcSlaveConfigData` 结构，包含 vendor ID、product code、固定地址、名称等基本身份信息。本 FB 给出的是"工程文件中配置的从站"清单（即使该从站当前不在线），与 `FB_EcGetScannedSlaves` 给出的"实际扫描到的"是两个互补视角。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId              : T_AmsNetId; 
    pArrEcConfSlaveInfo : POINTER TO ARRAY[0..EC_MAX_SLAVES] OF ST_EcSlaveConfigData;
    cbBufLen            : UDINT; 
    bExecute            : BOOL;
    tTimeout            : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `pArrEcConfSlaveInfo` | `POINTER TO ARRAY[0..EC_MAX_SLAVES] OF ST_EcSlaveConfigData` | — | 接收数组首地址；每元素是一台配置从站的身份信息结构 |
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
| `nSlaves` | `UINT` | 已配置从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读数组。

**"已配置" vs "已扫描"**：
- 本 FB（`FB_EcGetConfSlaves`）：读 XAE 工程文件中配置的从站列表，离线即知，不依赖现场连线
- `FB_EcGetScannedSlaves`：实际向网络发 scan 命令读 EEPROM，依赖现场连线，过程慢

工程实际中常用作对比：
- 期望（配置）= 实际（扫描）→ 现场连线与工程一致
- 期望 > 实际 → 缺从站
- 期望 < 实际 → 多了从站（异常）

**典型用法**：上电首次自检，调本 FB 一次拿配置清单，再调 `FB_EcGetScannedSlaves` 拿扫描清单做 diff 报警。本 FB 不发任何 EtherCAT 命令到现场总线，仅访问主站内存里的配置表，因而无论从站是否在线、是否在 OP 状态，都能立即返回配置侧信息。

**典型陷阱**：
- 数组容量 < 实际配置数：填到上限，但 `nSlaves` 仍返回真值
- 配置改动需要 PLC 重新加载工程才更新；不是动态查询
- 排序按 XAE 工程中从站枚举顺序，与物理拓扑顺序不一定相同

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nSlaves` 与数组 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`ST_EcSlaveConfigData`**：结构定义在 §13 数据类型一节，含 `slaveAddr / vendorId / productCode / revisionNo / serialNo / name` 等字段
- **离线可调用**：与现场连线无关；适合上电启动自检
- **配合 `FB_EcGetScannedSlaves` 做 diff**：是新机型试机的标准流程

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetConfSlaves.TcPOU`](../examples/P_Demo_FB_EcGetConfSlaves.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：新设备装配线上电自检，需要确认"配置的 12 台从站 12 台都在"。先调本 FB 拿 nSlaves=12，再调 `FB_EcGetScannedSlaves` 看到 11 → 报警"缺一台"
- **价值**：把"配置 vs 实际"的对账自动化，免去现场逐台数 LED
- **替代方案对比**：人工数 LED 灯 → 容易漏；XAE 在线 scan → 需要工程师插电脑

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57019019.html
- **相关 FB / FC**：`FB_EcGetScannedSlaves`（实际扫描）、`FB_EcGetSlaveIdentity`（单从站身份）、`ST_EcSlaveConfigData`
