# CouplerReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_CouplerReset.xml`](../examples/P_Demo_CouplerReset.xml) |

---

## 1. 功能简述

通过 **2-byte PLC interface** 触发耦合器复位。复位会让耦合器经 K-bus 重读端子配置、重初始化通信、清除现有 K-bus 错误。`STATE`/`CONTROL` 必须在 System Manager 链接到 2-byte PLC interface 的 Control/Status 变量。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    STATE           : PLCINTFSTRUCT;
    START           : BOOL;
    TMOUT           : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STATE` | `PLCINTFSTRUCT` | 2-byte PLC interface 状态字（链接到 IO） |
| `START` | `BOOL` | 上升沿触发复位 |
| `TMOUT` | `TIME` | 执行超时 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    CONTROL            : PLCINTFSTRUCT;
    BUSY               : BOOL;
    ERR                : BOOL;
    ERRID              : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CONTROL` | `PLCINTFSTRUCT` | 2-byte PLC interface 控制字（链接到 IO） |
| `BUSY` | `BOOL` | 执行中 |
| `ERR` | `BOOL` | 执行出错 |
| `ERRID` | `UDINT` | 错误号 |


### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方'功能简述'。
- 调用细节随平台/参数而异，请逐项核对 PDF 原文。

## 4. 错误码 / 返回值


PDF 列出了 ERR/bError 与 ERRID/nErrId 输出但未列具体错误码表（⚠️ 待人工补充错误码表，可参考 InfoSys 在线版）。

## 5. 使用注意 / 常见坑


- `STATE`/`CTRL`/`DATAOUT`/`DATAIN` 必须在 System Manager 链接到 2-byte PLC interface 的 IO 变量，否则 FB 永远 BUSY。
- 寄存器修改后**必须断电重启耦合器**才会持久化。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CouplerReset.xml`](../examples/P_Demo_CouplerReset.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CouplerReset
VAR
    fbCouplerReset : CouplerReset;
    arg_STATE         : PLCINTFSTRUCT;
    arg_START         : BOOL;
    arg_TMOUT         : TIME;
    out_CONTROL       : PLCINTFSTRUCT;
    out_BUSY          : BOOL;
    out_ERR           : BOOL;
    out_ERRID         : UDINT;
END_VAR

fbCouplerReset(
    STATE := arg_STATE,
    START := arg_START,
    TMOUT := arg_TMOUT,
    CONTROL => out_CONTROL,
    BUSY => out_BUSY,
    ERR => out_ERR,
    ERRID => out_ERRID
);
```

## 7. 相关

- 见 [`Tc2_Coupler README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
