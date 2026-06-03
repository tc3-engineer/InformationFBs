# FB_EcGetAllMasters

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/18716287371.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllMasters.TcPOU`](../examples/P_Demo_FB_EcGetAllMasters.TcPOU) |

---

## 1. 功能简述

读取 TwinCAT 控制器上所有 EtherCAT 主站的清单。一次成功调用后，`pAddrBuf` 指向的数组会被填入若干 `ST_EcDeviceInfo` 结构，每个结构包含一台主站的 Device ID、AMS NetID 与名称；输出 `nMasters` 给出实际主站总数。当传入缓冲区太小时，主站信息仅填到容量上限，但 `nMasters` 仍返回真实总数 —— 调用方可据此重新分配缓冲再调一次。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId;
    bExecute : BOOL; 
    pAddrBuf : POINTER TO ARRAY[0..EC_MAX_DEVICES] OF ST_EcDeviceInfo;
    cbBufLen : UDINT; 
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | 要读取主站清单的 TwinCAT IPC 的 AMS NetID。本机用空串 `''` |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `pAddrBuf` | `POINTER TO ARRAY[0..EC_MAX_DEVICES] OF ST_EcDeviceInfo` | — | 接收数组首地址；每元素含主站 Device ID / AMS NetID / 名称 |
| `cbBufLen` | `UDINT` | — | `pAddrBuf` 数组的字节容量，必须用 `SIZEOF(...)` 实际填 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用允许的最长时间 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrId   : UDINT;
    nMasters : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | `bBusy` 落沿后若出错则置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码；典型 `1798 (0x706)` = `pAddrBuf` 为空指针 |
| `nMasters` | `UINT` | 该 IPC 上 EtherCAT 主站总数（即使缓冲区放不下，本字段返回真实值） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次 ADS 读。`bBusy = TRUE` 期间必须每周期继续调用本实例让状态机推进。`bBusy` 落沿后再读 `nMasters` / 数组内容才有效。

**缓冲区不足的处理**：若实际主站数 > `cbBufLen / SIZEOF(ST_EcDeviceInfo)`，数组只填到上限，但 `nMasters` 仍返回真实总数。调用方应对比 `nMasters` 与数组容量，必要时重新分配再读。

**典型用法**：多 EtherCAT 卡的 IPC（例如某些 CX 控制器装了两块 EL/EK 主站卡，或 EAP master 与 EtherCAT master 共存）首先用本 FB 拿到 AMS NetID 列表，再用 NetID 调用其他 FB（`FB_EcGetMasterState` 等）按主站逐个诊断。

**典型陷阱**：
- 数组维度写成 `EC_MAX_DEVICES` 但 `cbBufLen` 填了较小值 → 不报错，只填到 cbBufLen 上限
- 单主站设备调用本 FB 是合法的（`nMasters = 1`），但通常更直接地用 `FB_EcGetMasterState`

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nMasters` 与数组 |
| `1798` (`0x706`) | `pAddrBuf` 为空指针 | 检查 `ADR(arr)` |
| `1797` (`0x705`) | 缓冲区太小 | 增大数组维度 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **TwinCAT 版本要求**：本 FB 需 TwinCAT ≥ v3.1.4024.62 + Tc2_EtherCAT ≥ v3.6.1.0（PDF 明确列出）
- **`sNetId` 空串**：枚举本机 IPC 上的主站。若要枚举远端 IPC，必须先建好 ADS 路由
- **`EC_MAX_DEVICES`**：库定义的最大主站数常量，用它做数组维度最稳妥
- **缓冲区生命周期**（工程经验补充）：数组必须是全局或 FB 成员，不可栈变量

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllMasters.TcPOU`](../examples/P_Demo_FB_EcGetAllMasters.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX2030 控制器带两块以太网卡，分别配置为 EtherCAT 主站 A 和 EtherCAT 主站 B；HMI 需要"主站清单"下拉，让操作员选要诊断哪台
- **价值**：把"几台主站、各自 NetID 是什么"这个清单查询封装成单次 ADS 调用，不需要写硬编码常量
- **替代方案对比**：硬编码 NetID 表 → 多机型工程无法通用；本 FB 给出运行时实际清单

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/18716287371.html
- **相关 FB / FC**：`FB_EcGetMasterState`、`FB_EcGetMasterDevState`（拿到 NetID 后逐主站读状态）
