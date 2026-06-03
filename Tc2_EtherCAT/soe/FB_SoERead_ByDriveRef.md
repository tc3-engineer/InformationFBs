# FB_SoERead_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `SoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57049355.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoERead_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoERead_ByDriveRef.TcPOU) |

---

## 1. 功能简述

通过驱动引用（`ST_DriveRef`）以 SoE 协议读取驱动参数。是 `FB_EcSoeRead` 用驱动引用版的对应；输出额外包含 `dwAttribute`（参数属性字）。全局变量 `bSeqReadDrvAttrAndValue` 可强制顺序访问 attribute 与 value（部分第三方设备需要）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    nIdn       : WORD;
    nElement   : BYTE;
    pDstBuf    : PVOID;
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
| `pDstBuf` | `PVOID` | — | 接收缓冲首地址 |
| `cbBufLen` | `UDINT` | — | 缓冲容量 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy        : BOOL;
    bError       : BOOL;
    iAdsErrId    : UINT;
    iSercosErrId : UINT;
    dwAttribute  : DWORD;
    cbRead       : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `iAdsErrId` | `UINT` | ADS 错误码 |
| `iSercosErrId` | `UINT` | Sercos 错误码 |
| `dwAttribute` | `DWORD` | 参数属性（数据类型、长度、scaling 等） |
| `cbRead` | `UDINT` | 成功读取字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 `FB_EcSoeRead` 区别**：用 `stDriveRef` 一次封装驱动定位；不需 `nSlaveAddr` / `nDriveNo`。同时输出多一个 `dwAttribute`，给应用层做参数自描述（如知道数据类型、scaling 因子等）。

**`bSeqReadDrvAttrAndValue` 全局开关**：AX5xxx 系列支持并发读 attribute 与 value，速度快；部分第三方设备需要顺序访问，置此全局变量为 TRUE 即可，但会慢若干个邮箱周期。

**典型用法**：
- NC 集成轴诊断：直接读 S-0-0148 (Drive Diagnostic) 取错误码
- 用 `dwAttribute` 自动识别参数数据类型，动态做单位换算

**典型陷阱**：
- 全局变量 `bSeqReadDrvAttrAndValue` 影响所有实例
- ADS / Sercos 错误码两路返回，都要检查

## 4. 错误码 / 返回值

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `iAdsErrId = 0` AND `iSercosErrId = 0` | 成功 | 读 `pDstBuf` |
| `iAdsErrId = 1861` | ADS 超时 | 增大 `tTimeout` |
| `iSercosErrId 非 0` | Sercos 错误 | 对照 Sercos 错误码 |

## 5. 使用注意 / 常见坑

- **AX5xxx 推荐**：并发模式，性能最优
- **第三方设备**（工程经验补充）：失败时试 `bSeqReadDrvAttrAndValue := TRUE`
- **`dwAttribute` 用于自描述**：解析数据格式时极有用

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoERead_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoERead_ByDriveRef.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：NC 集成的多轴诊断 —— 每轴用 `ST_DriveRef` 引用，本 FB 读 S-0-0148 错误码 + S-0-0040 当前速度，HMI 多轴看板一目了然
- **价值**：NC 与 PLC 解耦的驱动参数访问，工程可维护性强
- **替代方案对比**：`FB_EcSoeRead` + 硬编码地址 → 维护差；本 FB → NC 绑定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §9.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57049355.html
- **相关 FB / FC**：`FB_EcSoeRead`、`FB_SoEWrite_ByDriveRef`、`FB_CoERead_ByDriveRef`
