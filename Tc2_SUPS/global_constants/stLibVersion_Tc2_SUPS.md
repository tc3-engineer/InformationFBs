# stLibVersion_Tc2_SUPS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_SUPS.xml`](../examples/P_Demo_stLibVersion_Tc2_SUPS.xml) |

---

## 1. 功能简述

Tc2_SUPS 库的版本号常量（类型 `ST_LibVersion`，定义在 Tc2_System）。用 `F_CmpLibVersion` 做版本比较；TwinCAT 2 风格的 `LibVersion_*.QueryLibraryVersion()` 已废弃。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_SUPS : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_SUPS` | `ST_LibVersion` | Tc2_SUPS 库版本信息 |

### VAR_OUTPUT

不适用。

### VAR_IN_OUT

不适用。

## 3. 行为说明

- 见上方'功能简述'。

## 4. 错误码 / 返回值


无（常量声明）。

## 5. 使用注意 / 常见坑


- 类型 `ST_LibVersion` 在 `Tc2_System` 中定义，使用前需引用 Tc2_System。
- 运行时检查用 `F_CmpLibVersion`（在 Tc2_System）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_SUPS.xml`](../examples/P_Demo_stLibVersion_Tc2_SUPS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_SUPS
VAR
    stMyVer : ST_LibVersion;
    bOk     : BOOL;
END_VAR

// 需引用 Tc2_System（提供 ST_LibVersion 与 F_CmpLibVersion）
stMyVer := stLibVersion_Tc2_SUPS;

bOk := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_SUPS,
    iMajor       := 1,
    iMinor       := 5,
    iBuild       := 2,
    iRevision    := 0,
    nCmpType     := E_CmpLibVersion.GreaterOrEqual
);
```

## 7. 相关

- 见 [`Tc2_SUPS README`](../README.md) 同库其他条目

## 8. 待确认项


无。
