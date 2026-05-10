# FB_ReadCouplerDiag

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
| Example | [`examples/P_Demo_FB_ReadCouplerDiag.xml`](../examples/P_Demo_FB_ReadCouplerDiag.xml) |

---

## 1. 功能简述

K-bus 或耦合器错误发生时，读取耦合器错误 LED 的**第一/第二闪烁序列**。数据通过 2-byte PLC interface 传到 PLC——**前提是现场总线通信仍正常**。常用法：周期性查询耦合器状态字节，发现错误时启用本 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stState         : PLCINTFSTRUCT;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stState` | `PLCINTFSTRUCT` | 2-byte PLC interface 状态字 |
| `bExecute` | `BOOL` | 上升沿触发 |
| `tTimeout` | `TIME` | 执行超时 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stCtrl             : PLCINTFSTRUCT;
    bBusy              : BOOL;
    bError             : BOOL;
    nErrId             : UDINT;
    stDiag             : ST_CouplerDiag;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCtrl` | `PLCINTFSTRUCT` | 2-byte PLC interface 控制字 |
| `bBusy` | `BOOL` | 执行中 |
| `bError` | `BOOL` | 执行出错 |
| `nErrId` | `UDINT` | 错误号 |
| `stDiag` | `ST_CouplerDiag` | 诊断结果（含两序列闪烁码） |


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

> 配套可导入文件：[`examples/P_Demo_FB_ReadCouplerDiag.xml`](../examples/P_Demo_FB_ReadCouplerDiag.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_ReadCouplerDiag
VAR
    fbFB_ReadCouplerDiag : FB_ReadCouplerDiag;
    arg_stState       : PLCINTFSTRUCT;
    arg_bExecute      : BOOL;
    arg_tTimeout      : TIME;
    out_stCtrl        : PLCINTFSTRUCT;
    out_bBusy         : BOOL;
    out_bError        : BOOL;
    out_nErrId        : UDINT;
    out_stDiag        : ST_CouplerDiag;
END_VAR

fbFB_ReadCouplerDiag(
    stState := arg_stState,
    bExecute := arg_bExecute,
    tTimeout := arg_tTimeout,
    stCtrl => out_stCtrl,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    stDiag => out_stDiag
);
```

## 7. 相关

- 见 [`Tc2_Coupler README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
