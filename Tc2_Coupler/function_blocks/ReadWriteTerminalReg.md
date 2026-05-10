# ReadWriteTerminalReg

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
| Example | [`examples/P_Demo_ReadWriteTerminalReg.xml`](../examples/P_Demo_ReadWriteTerminalReg.xml) |

---

## 1. 功能简述

通过端子通道的 control/status 字节进行**寄存器通信**，访问智能端子（如模拟输出端子）的寄存器。`READ`/`WRITE` 上升沿触发对寄存器 `REGNO` 的读/写。写入时 FB 自动解除写保护、写后再读回。`STATE`/`DATAIN`/`CTRL`/`DATAOUT` 必须在 System Manager 里链接到对应端子通道的 IO 变量。寄存器修改要持久必须切电源重启。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    STATE           : BYTE;
    DATAIN          : WORD;
    REGNO           : BYTE;
    READ            : BOOL;
    WRITE           : BOOL;
    TMOUT           : TIME;
    NEWREGVALUE     : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STATE` | `BYTE` | 端子通道状态字节 |
| `DATAIN` | `WORD` | 端子通道数据输入字 |
| `REGNO` | `BYTE` | 要读/写的寄存器号 |
| `READ` | `BOOL` | 上升沿触发读 |
| `WRITE` | `BOOL` | 上升沿触发写 |
| `TMOUT` | `TIME` | 执行超时 |
| `NEWREGVALUE` | `WORD` | WRITE 时要写入的值 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    CTRL               : BYTE;
    DATAOUT            : WORD;
    BUSY               : BOOL;
    ERR                : BOOL;
    ERRID              : UDINT;
    CURREGVALUE        : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CTRL` | `BYTE` | 端子通道控制字节 |
| `DATAOUT` | `WORD` | 端子通道数据输出字 |
| `BUSY` | `BOOL` | FB 执行中 |
| `ERR` | `BOOL` | 执行出错 |
| `ERRID` | `UDINT` | 错误号（ERR=TRUE 时有效） |
| `CURREGVALUE` | `WORD` | 成功读到的寄存器值 |


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

> 配套可导入文件：[`examples/P_Demo_ReadWriteTerminalReg.xml`](../examples/P_Demo_ReadWriteTerminalReg.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ReadWriteTerminalReg
VAR
    fbReadWriteTerminalReg : ReadWriteTerminalReg;
    arg_STATE         : BYTE;
    arg_DATAIN        : WORD;
    arg_REGNO         : BYTE;
    arg_READ          : BOOL;
    arg_WRITE         : BOOL;
    arg_TMOUT         : TIME;
    arg_NEWREGVALUE   : WORD;
    out_CTRL          : BYTE;
    out_DATAOUT       : WORD;
    out_BUSY          : BOOL;
    out_ERR           : BOOL;
    out_ERRID         : UDINT;
    out_CURREGVALUE   : WORD;
END_VAR

fbReadWriteTerminalReg(
    STATE := arg_STATE,
    DATAIN := arg_DATAIN,
    REGNO := arg_REGNO,
    READ := arg_READ,
    WRITE := arg_WRITE,
    TMOUT := arg_TMOUT,
    NEWREGVALUE := arg_NEWREGVALUE,
    CTRL => out_CTRL,
    DATAOUT => out_DATAOUT,
    BUSY => out_BUSY,
    ERR => out_ERR,
    ERRID => out_ERRID,
    CURREGVALUE => out_CURREGVALUE
);
```

## 7. 相关

- 见 [`Tc2_Coupler README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
