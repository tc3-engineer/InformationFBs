# stLibVersion_Tc2_Coupler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_Coupler.xml`](../examples/P_Demo_stLibVersion_Tc2_Coupler.xml) |

---

## 1. 功能简述

Tc2_Coupler 库版本常量。用 `F_CmpLibVersion`（在 Tc2_System）做运行时版本检查。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_Coupler : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_Coupler` | `ST_LibVersion` | Tc2_Coupler 库版本信息 |

### VAR_OUTPUT

不适用。

### VAR_IN_OUT

不适用。

## 3. 行为说明

- 见上方'功能简述'。

## 4. 错误码 / 返回值


无（常量声明）。

## 5. 使用注意 / 常见坑


- `STATE`/`CTRL`/`DATAOUT`/`DATAIN` 必须在 System Manager 链接到 2-byte PLC interface 的 IO 变量，否则 FB 永远 BUSY。
- 寄存器修改后**必须断电重启耦合器**才会持久化。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_Coupler.xml`](../examples/P_Demo_stLibVersion_Tc2_Coupler.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_Coupler
VAR
    stMyVer : ST_LibVersion;
    bOk     : BOOL;
END_VAR

// 需引用 Tc2_System（提供 ST_LibVersion 与 F_CmpLibVersion）
stMyVer := stLibVersion_Tc2_Coupler;

bOk := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_Coupler,
    iMajor       := 1,
    iMinor       := 1,
    iBuild       := 1,
    iRevision    := 0,
    nCmpType     := E_CmpLibVersion.GreaterOrEqual
);
```

## 7. 相关

- 见 [`Tc2_Coupler README`](../README.md) 同库其他条目

## 8. 待确认项


无。
