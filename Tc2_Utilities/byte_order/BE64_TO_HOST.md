# BE64_TO_HOST
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Byte order converting functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_BE64_TO_HOST.xml`](../examples/P_Demo_BE64_TO_HOST.xml) |

---
## 1. 功能简述

64-bit 数从大端转主机字节序（legacy `T_ULARGE_INTEGER` 版本）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION BE64_TO_HOST : T_ULARGE_INTEGER
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_ULARGE_INTEGER` | 要转换的 64-bit 数（legacy 类型） |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `BE64_TO_HOST(x)`，返回 `T_ULARGE_INTEGER` 类型结果。
- 期望：`对应主机字节序`

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。无错误码。

## 5. 使用注意 / 常见坑

- 新代码优先用 `BE64_TO_HOSTEX`（native LWORD）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BE64_TO_HOST.xml`](../examples/P_Demo_BE64_TO_HOST.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BE64_TO_HOST
VAR
    bResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    x : T_ULARGE_INTEGER;
END_VAR

// x.lo/x.hi 自行赋值
IF bRun THEN
    bResult := BE64_TO_HOST(x);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
