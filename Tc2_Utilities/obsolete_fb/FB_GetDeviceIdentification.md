# FB_GetDeviceIdentification
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete]` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `⚠️ deprecated (verified)` |
| Example | [`examples/P_Demo_FB_GetDeviceIdentification.xml`](../examples/P_Demo_FB_GetDeviceIdentification.xml) |

---
## 1. 功能简述

⚠️ **已废弃** —— 长字符串硬件型号/序列号请改用 `FB_GetDeviceIdentificationEx`。

读取目标 TwinCAT 设备的 Device ID。
## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeout : TIME; (* := DEFAULT_ADS_TIMEOUT *)
    sNetId : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发 |
| `tTimeout` | `TIME` | ADS 超时 |
| `sNetId` | `T_AmsNetId` | 目标 AmsNetId（空 = 本地） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    stDevIdent : ST_DeviceIdentification;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 执行中 |
| `bError` | `BOOL` | 出错 |
| `nErrorId` | `UDINT` | ADS 错误号 |
| `stDevIdent` | `ST_DeviceIdentification` | 设备识别信息（型号、序列号等） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

出错时 `bError = TRUE`，错误码在 `nErrorId`/`hrErrorCode`（具体码表见 InfoSys 在线文档，⚠️ 待人工补充）。

## 5. 使用注意 / 常见坑

- **已废弃**——新代码用 `FB_GetDeviceIdentificationEx`（支持更长的字段字符串）。
- `ST_DeviceIdentification` 含旧版长度受限的字段。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetDeviceIdentification.xml`](../examples/P_Demo_FB_GetDeviceIdentification.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_GetDeviceIdentification
VAR
    fbFB_GetDeviceIdentification : FB_GetDeviceIdentification;
    arg_bExecute : BOOL;
    arg_tTimeout : TIME;
    arg_sNetId : T_AmsNetId;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrorId : UDINT;
    out_stDevIdent : ST_DeviceIdentification;
END_VAR

fbFB_GetDeviceIdentification(
        bExecute := arg_bExecute,
        tTimeout := arg_tTimeout,
        sNetId := arg_sNetId,
        bBusy => out_bBusy,
        bError => out_bError,
        nErrorId => out_nErrorId,
        stDevIdent => out_stDevIdent
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 本 FB 已废弃，仅供兼容旧代码。
