# FB_ReadCouplerRegs

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
| Example | [`examples/P_Demo_FB_ReadCouplerRegs.xml`](../examples/P_Demo_FB_ReadCouplerRegs.xml) |

---

## 1. 功能简述

**读**耦合器表寄存器与智能端子寄存器。耦合器自身是 terminal 0；其他端子（不含无源/电源端子）从 1 起递增编号。可读全部或子区间（`nStartReg` 到 `nEndReg`）。读完整表（0..255）需若干秒。结果按高/低字节存入 `stCouplerTable`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stState       : PLCINTFSTRUCT;
    nTerminal     : BYTE:= TERM_COUPLER;
    nTable        : BYTE;
    nStartReg     : BYTE;
    nEndReg       : BYTE;
    bExecute      : BOOL;
    tTimeout      : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stState` | `PLCINTFSTRUCT` | 2-byte PLC interface 状态字 |
| `nTerminal` | `BYTE` | 目标端子号（0=耦合器；不计无源端子） |
| `nTable` | `BYTE` | 表号（智能端子每通道 1 表） |
| `nStartReg` | `BYTE` | 起始寄存器号 |
| `nEndReg` | `BYTE` | 结束寄存器号 |
| `bExecute` | `BOOL` | 上升沿触发 |
| `tTimeout` | `TIME` | 执行超时 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stCtrl             : PLCINTFSTRUCT;
    bBusy              : BOOL;
    bError             : BOOL;
    nErrId             : UDINT;
    stCouplerTable     : ST_CouplerTable;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCtrl` | `PLCINTFSTRUCT` | 2-byte PLC interface 控制字 |
| `bBusy` | `BOOL` | 执行中 |
| `bError` | `BOOL` | 执行出错 |
| `nErrId` | `UDINT` | 错误号 |
| `stCouplerTable` | `ST_CouplerTable` | 读取的寄存器值数组 |


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

> 配套可导入文件：[`examples/P_Demo_FB_ReadCouplerRegs.xml`](../examples/P_Demo_FB_ReadCouplerRegs.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_ReadCouplerRegs
VAR
    fbFB_ReadCouplerRegs : FB_ReadCouplerRegs;
    arg_stState       : PLCINTFSTRUCT;
    arg_nTerminal     : BYTE;
    arg_nTable        : BYTE;
    arg_nStartReg     : BYTE;
    arg_nEndReg       : BYTE;
    arg_bExecute      : BOOL;
    arg_tTimeout      : TIME;
    out_stCtrl        : PLCINTFSTRUCT;
    out_bBusy         : BOOL;
    out_bError        : BOOL;
    out_nErrId        : UDINT;
    out_stCouplerTable : ST_CouplerTable;
END_VAR

fbFB_ReadCouplerRegs(
    stState := arg_stState,
    nTerminal := arg_nTerminal,
    nTable := arg_nTable,
    nStartReg := arg_nStartReg,
    nEndReg := arg_nEndReg,
    bExecute := arg_bExecute,
    tTimeout := arg_tTimeout,
    stCtrl => out_stCtrl,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    stCouplerTable => out_stCouplerTable
);
```

## 7. 相关

- 见 [`Tc2_Coupler README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
