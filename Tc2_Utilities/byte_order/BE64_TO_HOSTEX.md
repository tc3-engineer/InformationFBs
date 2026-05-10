# BE64_TO_HOSTEX
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
| Example | [`examples/P_Demo_BE64_TO_HOSTEX.xml`](../examples/P_Demo_BE64_TO_HOSTEX.xml) |

---
## 1. 功能简述

64-bit 数从大端转主机字节序（**native** LWORD 版本）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION BE64_TO_HOSTEX : LWORD
VAR_INPUT
    in : LWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `LWORD` | 要转换的 64-bit 数（native LWORD） |

### 返回值

`LWORD` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `BE64_TO_HOSTEX(16#EFCDAB8967452301)`，返回 `LWORD` 类型结果。
- 期望：`16#0123456789ABCDEF`

## 4. 错误码 / 返回值

返回 `LWORD`。无错误码。

## 5. 使用注意 / 常见坑

- 新代码优先用本函数；对应 `HOST_TO_BE64EX`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BE64_TO_HOSTEX.xml`](../examples/P_Demo_BE64_TO_HOSTEX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BE64_TO_HOSTEX
VAR
    bResult : LWORD;
    bRun    : BOOL;
END_VAR


IF bRun THEN
    bResult := BE64_TO_HOSTEX(16#EFCDAB8967452301);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
