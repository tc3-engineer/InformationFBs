# FB_CoERead_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2217655179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoERead_ByDriveRef.TcPOU`](../examples/P_Demo_FB_CoERead_ByDriveRef.TcPOU) |

---

## 1. 功能简述

通过 CoE 协议读取驱动（EtherCAT Drive）参数。不像 `FB_EcCoeSdoRead` 接 `sNetId + nSlaveAddr`，本 FB 用 `stDriveRef`（驱动引用结构）作为唯一输入定位驱动。驱动引用可由 System Manager 直接链接到 NC 配置，运行时取得，工程内更紧凑。同时支持 `bCompleteAccess`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef       :  ST_DriveRef;
    nIndex           :  WORD;
    nSubIndex        :  BYTE; 
    pDstBuf          :  PVOID;
    cbBufLen         :  UDINT;
    bExecute         :  BOOL;
    tTimeout         :  TIME;
    bCompleteAccess  :  BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动引用：含主站 NetID + 从站地址 + DriveNo；可由 NC 配置链接，免手工填 |
| `nIndex` | `WORD` | — | CoE 对象 index |
| `nSubIndex` | `BYTE` | — | CoE 对象 sub-index |
| `pDstBuf` | `PVOID` | — | 接收缓冲首地址 |
| `cbBufLen` | `UDINT` | — | 缓冲容量 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | — | 超时（无默认） |
| `bCompleteAccess` | `BOOL` | — | TRUE = 读整对象 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy         : BOOL;
    bError        : BOOL;
    iAdsErrId     : UINT;
    iCANopenErrId : UINT;
    cbRead        : UDINT;    
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `iAdsErrId` | `UINT` | ADS 错误码 |
| `iCANopenErrId` | `UINT` | CANopen 错误码（CoE Abort） |
| `cbRead` | `UDINT` | 实际读取字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 `FB_EcCoeSdoReadEx` 区别**：本 FB 用 `stDriveRef` 一次封装"找哪个驱动"，与 NC 配置中的 Drive Reference 直接挂钩；不需要 PLC 端硬编码 `sNetId` 和 `nSlaveAddr`，工程编译期就把驱动绑定关系建立。`FB_EcCoeSdoReadEx` 是按 NetID + 地址访问任意从站，本 FB 是按已绑定的驱动引用访问。两者底层走的都是 CoE 邮箱，但访问语义不同，建议运动场景统一用本 FB。

**`stDriveRef` 来源**：
- 在 XAE System Manager 中右键 PLC 程序的 `ST_PlcDriveRef` 实例 → Change Link → 链接到 NC 配置的某个轴；NetID 与从站地址会自动填入
- 也可手工填值：将 byte 数组 NetID 转字符串赋给 `stDriveRef.sNetId`、`nSlaveAddr` 设为驱动从站地址

**典型用法**：
- NC 轴诊断：读 0x6041（CIA402 Statusword）查驱动状态
- 读 0x1018:1 验证 vendor

**典型陷阱**：
- 错误码分两路返回（`iAdsErrId` 和 `iCANopenErrId`），需都检查
- 没正确链接 NC 配置时 `stDriveRef` 内容无效

## 4. 错误码 / 返回值

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `iAdsErrId = 0` AND `iCANopenErrId = 0` | 成功 | 读 `pDstBuf` |
| `iAdsErrId = 1861` | ADS 超时 | 增大 `tTimeout` |
| `iCANopenErrId` 非 0 | CoE Abort | 对照 CoE Abort 表 |

## 5. 使用注意 / 常见坑

- **驱动专用**：本 FB 名字含 Drive，意在驱动场景；非驱动从站也可用，但工程上不推荐
- **`tTimeout` 必填**：无默认值
- **NC 链接关系**（工程经验补充）：System Manager 中 `ST_PlcDriveRef` 与 NC 配置链接是关键

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoERead_ByDriveRef.TcPOU`](../examples/P_Demo_FB_CoERead_ByDriveRef.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：6 轴运动机器，每轴在 NC 中独立配置；PLC 端读 CIA402 Statusword 做轴状态监视。每轴一个 `ST_DriveRef` 全局变量，PLC 启动时 NC 自动填入；本 FB 直接读，业务侧无需关心从站地址
- **价值**：把"PLC 引用驱动"做成结构体引用，工程更模块化
- **替代方案对比**：`FB_EcCoeSdoRead` + 硬编码地址 → 维护差；本 FB → 与 NC 绑定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2217655179.html
- **相关 FB / FC**：`FB_CoEWrite_ByDriveRef`、`FB_EcCoeSdoReadEx`、`FB_SoERead_ByDriveRef`（SoE 版本）
