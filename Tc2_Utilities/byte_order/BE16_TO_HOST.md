# BE16_TO_HOST
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
| Example | [`examples/P_Demo_BE16_TO_HOST.xml`](../examples/P_Demo_BE16_TO_HOST.xml) |

---
## 1. 功能简述

16-bit 数从大端转主机字节序。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION BE16_TO_HOST : WORD
VAR_INPUT
    in : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `WORD` | 要转换的数 |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `BE16_TO_HOST(16#3412)`，返回 `WORD` 类型结果。
- 期望：`16#1234`

## 4. 错误码 / 返回值

返回 `WORD`。无错误码。

## 5. 使用注意 / 常见坑

- 和 `HOST_TO_BE16` 互为反操作；在小端主机上两者实质相同（都是字节交换）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BE16_TO_HOST.xml`](../examples/P_Demo_BE16_TO_HOST.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BE16_TO_HOST
VAR
    bResult : WORD;
    bRun    : BOOL;
END_VAR


IF bRun THEN
    bResult := BE16_TO_HOST(16#3412);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
