# FB_CoEWrite_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2217657099.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEWrite_ByDriveRef.TcPOU`](../examples/P_Demo_FB_CoEWrite_ByDriveRef.TcPOU) |

---

## 1. 功能简述

通过驱动引用（`ST_DriveRef`）向驱动写 CoE 参数。是 `FB_CoERead_ByDriveRef` 的写入对等版本。同样支持 `bCompleteAccess`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef       :  ST_DriveRef;
    nIndex           :  WORD;
    nSubIndex        :  BYTE;
    pSrcBuf          :  PVOID;
    cbBufLen         :  UDINT;
    bExecute         :  BOOL;
    tTimeout         :  TIME;
    bCompleteAccess  :  BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动引用 |
| `nIndex` | `WORD` | — | CoE 对象 index |
| `nSubIndex` | `BYTE` | — | sub-index |
| `pSrcBuf` | `PVOID` | — | 数据首地址 |
| `cbBufLen` | `UDINT` | — | 数据字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | — | 超时（无默认） |
| `bCompleteAccess` | `BOOL` | — | TRUE = 写整对象 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy         : BOOL;
    bError        : BOOL;
    iAdsErrId     : UINT;
    iCANopenErrId : UINT;    
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `iAdsErrId` | `UINT` | ADS 错误码 |
| `iCANopenErrId` | `UINT` | CANopen 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 `FB_CoERead_ByDriveRef` 完全对称**：仅方向相反。`pSrcBuf` 是要写出去的数据；其余字段语义相同。错误同样分两路返回，`iAdsErrId` 给底层 ADS 错误（路由不通、超时等），`iCANopenErrId` 给应用层 CoE Abort（对象不存在、只读、数据长度不匹配等），调用方需要同时检查两个字段判定真实失败原因。

**典型用法**：
- NC 启动期写 CIA402 控制参数（0x6040 Controlword、0x6060 ModeOfOperation）
- 修改驱动加减速曲线参数（0x6083、0x6084）

**典型陷阱**：
- 驱动多数运行参数要求 PREOP / SAFEOP 状态才允许写
- CIA402 Controlword 写入需配合驱动状态机：0→Switch on disabled→Ready to switch on→Switched on→Operation enabled
- 错误码两路返回（ADS + CANopen）需都检查

## 4. 错误码 / 返回值

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `iAdsErrId = 0` AND `iCANopenErrId = 0` | 成功 | 写入完成 |
| `iAdsErrId = 1861` | ADS 超时 | 增大 `tTimeout` |
| `iCANopenErrId` 非 0 | CoE Abort | 对照 CoE Abort 表 |

## 5. 使用注意 / 常见坑

- **CIA402 协议**：写驱动控制参数前必须懂 CIA402 状态机
- **驱动专用建议**（工程经验补充）：非驱动从站建议用 `FB_EcCoeSdoWrite`
- **`tTimeout` 必填**

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEWrite_ByDriveRef.TcPOU`](../examples/P_Demo_FB_CoEWrite_ByDriveRef.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：根据加工节拍动态调驱动加速度限值；用本 FB 写 0x6083（Profile Acceleration）；不停机调整运动平顺性
- **价值**：驱动参数运行时可调，无需停机重配
- **替代方案对比**：停机后用 XAE 改 → 影响节拍；本 FB → 在线即调

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2217657099.html
- **相关 FB / FC**：`FB_CoERead_ByDriveRef`、`FB_EcCoeSdoWriteEx`、`FB_SoEWrite_ByDriveRef`
