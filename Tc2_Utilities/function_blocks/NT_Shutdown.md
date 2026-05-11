# NT_Shutdown
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_NT_Shutdown.xml`](../examples/P_Demo_NT_Shutdown.xml) |

---
## 1. 功能简述

This functionality is not available under Windows CE! The Windows NT operating system can be shut down with the aid of the function block NT_Shutdown. The function largely corresponds to the Shut Down command on the Windows taskbar. A delay before execution of the Shut Down command can be defined via the DELAY parameter. Notes: Newer operating systems ( e.g. Windows 2000 ) perform with the aid of the "NT_Shutdown" function block the "Shutdown with Power OFF" ( the computer switches its power OFF). This function can only be used on systems which are ACPI conform (Advanced Configuration and Power Interface). The ACPI functions should be activated in BIOS before the installation of the operating system. The ACPI-functions have to be supported by the motherboard and the power supply of the PC. A change afterwards is not recognized by the operating system. If there is an ACPI-supporting PC, you can check e. g. at Windows 2000 in the following way: 1. In the "System Manager" open the folder "system". 2. on the tab "Hardware" choose the "Device Manager". In the navigation tree with the devices now you can read at "Computer": "Advanced Configuration and Power Interface (ACPI) PC". The defa

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DELAY : DWORD;
    START : BOOL;
    TMOUT : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `NETID` | `T_AmsNetId` | （详见 PDF） |
| `DELAY` | `DWORD` | （详见 PDF） |
| `START` | `BOOL` | （详见 PDF） |
| `TMOUT` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | （详见 PDF） |
| `ERR` | `BOOL` | （详见 PDF） |
| `ERRID` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.70 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.70 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_NT_Shutdown.xml`](../examples/P_Demo_NT_Shutdown.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_NT_Shutdown
VAR
    fbNT_Shutdown : NT_Shutdown;
    arg_NETID : T_AmsNetId;
    arg_DELAY : DWORD;
    arg_START : BOOL;
    arg_TMOUT : TIME;
    out_BUSY : BOOL;
    out_ERR : BOOL;
    out_ERRID : UDINT;
END_VAR

fbNT_Shutdown(
    NETID := arg_NETID,
    DELAY := arg_DELAY,
    START := arg_START,
    TMOUT := arg_TMOUT,
    BUSY => out_BUSY,
    ERR => out_ERR,
    ERRID => out_ERRID
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
