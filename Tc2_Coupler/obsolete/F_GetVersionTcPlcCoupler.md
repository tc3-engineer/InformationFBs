# F_GetVersionTcPlcCoupler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION` |
| Category | `[obsolete functions]` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcPlcCoupler.xml`](../examples/P_Demo_F_GetVersionTcPlcCoupler.xml) |

---

## 1. 功能简述

⚠️ **已废弃**——请改用全局常量 `stLibVersion_Tc2_Coupler`。

旧 API：返回 PLC 库的某个版本元素（major/minor/revision）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetVersionTcPlcCoupler: UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 1=major、2=minor、3=revision |


### 返回值

`UINT` —— 函数计算结果。


### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方'功能简述'。

## 4. 错误码 / 返回值


返回 `UINT` 类型的版本元素值。

## 5. 使用注意 / 常见坑


- `STATE`/`CTRL`/`DATAOUT`/`DATAIN` 必须在 System Manager 链接到 2-byte PLC interface 的 IO 变量，否则 FB 永远 BUSY。
- 寄存器修改后**必须断电重启耦合器**才会持久化。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcPlcCoupler.xml`](../examples/P_Demo_F_GetVersionTcPlcCoupler.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetVersionTcPlcCoupler
VAR
    nResult : UINT;
    bRun : BOOL;
END_VAR

IF bRun THEN
    nResult := F_GetVersionTcPlcCoupler(1);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Coupler README`](../README.md) 同库其他条目

## 8. 待确认项


无。
