# FB_S_UPS_CB3011

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `CB3011` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_S_UPS_CB3011.xml`](../examples/P_Demo_FB_S_UPS_CB3011.xml) |

---

## 1. 功能简述

`FB_S_UPS_CB3011` 用于 **CB3011** 平台带 1-second UPS 设备从 PLC 控制 UPS。断电时根据 `eUpsMode` 决定保存持久化数据或/和执行 quick shutdown。**默认输入值不应改动**。

注意：1-second UPS 容量仅够数秒，仅 Compact Flash 可用作存储介质（不可用于硬盘）。持久化必须用 `SPDM_2PASS`（fast persistent mode），尽管可能造成实时性违反——确保配置足够 router 内存。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId:= ''; (* '' = local netid *)
    iPLCPort        : UINT; (* PLC Runtime System for writing persistent data *)
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT; (* ADS Timeout *)
    eUpsMode        : E_S_UPS_Mode := eSUPS_WrPersistData_Shutdown; (* UPS mode (w/ wo writing persistent data, w/wo shutdown) *)
    ePersistentMode : E_PersistentMode := SPDM_2PASS; (* mode for writing persistent data *)
    tRecoverTime    : TIME := T#10s; (* ON time to recover from short power failure in mode eSUPS_WrPersistData_NoShutdown/eSUPS_CheckPowerStatus *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetID` | `T_AmsNetId` | 控制器 AmsNetId（空字符串表本地） |
| `iPLCPort` | `UINT` | 写持久化数据的 PLC runtime 端口（851/852/...，0 = 自动） |
| `tTimeout` | `TIME` | ADS 超时（默认 DEFAULT_ADS_TIMEOUT） |
| `eUpsMode` | `E_S_UPS_Mode` | UPS 工作模式（默认 eSUPS_WrPersistData_Shutdown） |
| `ePersistentMode` | `E_PersistentMode` | 持久化数据写入模式（默认 SPDM_2PASS） |
| `tRecoverTime` | `TIME` | 短时断电恢复时间（默认 T#10s） |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bPowerFailDetect   : BOOL; (* TRUE while powerfailure is detected *)
    eState             : E_S_UPS_State := eSUPS_PowerOK; (* current ups state *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bPowerFailDetect` | `BOOL` | 断电期间为 TRUE |
| `eState` | `E_S_UPS_State` | FB 内部状态 |


### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方'功能简述'。
- 调用细节随平台/参数而异，请逐项核对 PDF 原文。

## 4. 错误码 / 返回值


PDF 列出了 ERR/bError 与 ERRID/nErrId 输出但未列具体错误码表（⚠️ 待人工补充错误码表，可参考 InfoSys 在线版）。

## 5. 使用注意 / 常见坑


- **默认输入值不要改**——Beckhoff 已为各平台调好默认。
- 1-second UPS 容量仅几秒，**只能存到 CF/CFast/MicroSD**，不能写硬盘。
- 持久化必须用 `SPDM_2PASS`（fast persistent mode），可能造成实时性违反——配足 router memory。
- **FB 必须每周期调用**才能持续监视电源状态。
- 硬件平台特异——挑错型号会编译报错或运行无效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_S_UPS_CB3011.xml`](../examples/P_Demo_FB_S_UPS_CB3011.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_S_UPS_CB3011
VAR
    fbFB_S_UPS_CB3011 : FB_S_UPS_CB3011;
    arg_sNetID        : T_AmsNetId;
    arg_iPLCPort      : UINT;
    arg_tTimeout      : TIME;
    arg_eUpsMode      : E_S_UPS_Mode;
    arg_ePersistentMode : E_PersistentMode;
    arg_tRecoverTime  : TIME;
    out_bPowerFailDetect : BOOL;
    out_eState        : E_S_UPS_State;
END_VAR

fbFB_S_UPS_CB3011(
    sNetID := arg_sNetID,
    iPLCPort := arg_iPLCPort,
    tTimeout := arg_tTimeout,
    eUpsMode := arg_eUpsMode,
    ePersistentMode := arg_ePersistentMode,
    tRecoverTime := arg_tRecoverTime,
    bPowerFailDetect => out_bPowerFailDetect,
    eState => out_eState
);
```

## 7. 相关

- 见 [`Tc2_SUPS README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
