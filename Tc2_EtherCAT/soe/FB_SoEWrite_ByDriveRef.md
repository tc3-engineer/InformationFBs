# FB_SoEWrite_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `SoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57050891.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEWrite_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoEWrite_ByDriveRef.TcPOU) |

---

## 1. 功能简述

通过驱动引用以 SoE 协议写入驱动参数。是 `FB_SoERead_ByDriveRef` 的写入对等版。错误码同样分 ADS 和 Sercos 两路返回。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    nIdn       : WORD;
    nElement   : BYTE;
    pSrcBuf    : PVOID;
    cbBufLen   : UDINT;
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动引用 |
| `nIdn` | `WORD` | — | 参数 IDN |
| `nElement` | `BYTE` | — | Element 位掩码 |
| `pSrcBuf` | `PVOID` | — | 数据首地址 |
| `cbBufLen` | `UDINT` | — | 数据字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy        : BOOL;
    bError       : BOOL;
    iAdsErrId    : UINT;
    iSercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `iAdsErrId` | `UINT` | ADS 错误码 |
| `iSercosErrId` | `UINT` | Sercos 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 `FB_SoERead_ByDriveRef` 完全对称**：方向相反。`pSrcBuf` 是要写的数据，其余语义一致。错误码两路分别检查（ADS 与 Sercos）。本 FB 与 `FB_EcSoeWrite` 的差异同样仅在于驱动定位方式 —— 用驱动引用替代直接的 NetID + 从站地址，让 PLC 程序与具体 EtherCAT 拓扑解耦，是 NC 集成场景的首选写入 FB。

**典型用法**：
- NC 启动期写 PID 参数（P-0-xxxx）
- 调电流环参数（S-0-0034 等）

**典型陷阱**：
- 某些 SoE 参数只在 Sercos phase 2 之前可写
- 写完通常需要让驱动 "activate" 才生效
- 写 PID 等敏感参数可能影响运动稳定性，应停轴时写

## 4. 错误码 / 返回值

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `iAdsErrId = 0` AND `iSercosErrId = 0` | 成功 | 写入完成 |
| `iAdsErrId = 1861` | ADS 超时 | 增大 `tTimeout` |
| `iSercosErrId 非 0` | Sercos 错误 | 对照 Sercos 错误码 |

## 5. 使用注意 / 常见坑

- **停轴再写**：PID 等运动相关参数建议停轴时写
- **`bSeqReadDrvAttrAndValue` 全局开关也影响写**（工程经验补充）
- **激活步骤**：部分参数写完需 reset 驱动激活

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEWrite_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoEWrite_ByDriveRef.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：换产前调整 AX5206 加减速时间常数（P-0-xxxx）。每种产品有专属参数组，PLC 切产时用本 FB 批量写
- **价值**：换产参数自动加载，免人工
- **替代方案对比**：Drive Manager 单台手动 → 慢；本 FB → PLC 批量自动

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §9.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57050891.html
- **相关 FB / FC**：`FB_SoERead_ByDriveRef`、`FB_EcSoeWrite`、`FB_CoEWrite_ByDriveRef`
