# FB_NT_QuickShutdown

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NT_QuickShutdown.xml`](../examples/P_Demo_FB_NT_QuickShutdown.xml) |

---

## 1. 功能简述

**触发立即重启**控制器，不停止 TwinCAT/Windows。⚠️ **不要单独使用**——本 FB 由 `FB_S_UPS_*` 内部调用，独立使用可能造成数据丢失。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID           : T_AmsNetId;
    START           : BOOL;
    TMOUT           : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `NETID` | `T_AmsNetId` | 控制器 AmsNetId |
| `START` | `BOOL` | 上升沿触发立即重启 |
| `TMOUT` | `TIME` | ADS 超时（默认 DEFAULT_ADS_TIMEOUT） |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY               : BOOL;
    ERR                : BOOL;
    ERRID              : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 正在执行 quick shutdown |
| `ERR` | `BOOL` | 出错时为 TRUE |
| `ERRID` | `UDINT` | ERR 为 TRUE 时返回错误号 |


### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方'功能简述'。
- 调用细节随平台/参数而异，请逐项核对 PDF 原文。

## 4. 错误码 / 返回值


PDF 列出了 ERR/bError 与 ERRID/nErrId 输出但未列具体错误码表（⚠️ 待人工补充错误码表，可参考 InfoSys 在线版）。

## 5. 使用注意 / 常见坑


- **不要单独调用**——会绕过持久化，导致数据丢失。生产代码应通过 `FB_S_UPS_*` 间接使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NT_QuickShutdown.xml`](../examples/P_Demo_FB_NT_QuickShutdown.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_NT_QuickShutdown
VAR
    fbFB_NT_QuickShutdown : FB_NT_QuickShutdown;
    arg_NETID         : T_AmsNetId;
    arg_START         : BOOL;
    arg_TMOUT         : TIME;
    out_BUSY          : BOOL;
    out_ERR           : BOOL;
    out_ERRID         : UDINT;
END_VAR

fbFB_NT_QuickShutdown(
    NETID := arg_NETID,
    START := arg_START,
    TMOUT := arg_TMOUT,
    BUSY => out_BUSY,
    ERR => out_ERR,
    ERRID => out_ERRID
);
```

## 7. 相关

- 见 [`Tc2_SUPS README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
