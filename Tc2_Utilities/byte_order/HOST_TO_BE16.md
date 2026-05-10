# HOST_TO_BE16
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
| Example | [`examples/P_Demo_HOST_TO_BE16.xml`](../examples/P_Demo_HOST_TO_BE16.xml) |

---
## 1. 功能简述

16-bit 数从主机字节序转大端（network byte order）。Beckhoff 控制器是小端，所以这个等价于交换两个字节。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION HOST_TO_BE16 : WORD
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

- 调用 `HOST_TO_BE16(16#1234)`，返回 `WORD` 类型结果。
- 期望：`16#3412`

## 4. 错误码 / 返回值

返回 `WORD`。无错误码。

## 5. 使用注意 / 常见坑

- **实质**：在小端控制器上等价于 `SWAP`。
- 用 `BE16_TO_HOST` 反向。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HOST_TO_BE16.xml`](../examples/P_Demo_HOST_TO_BE16.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HOST_TO_BE16
VAR
    bResult : WORD;
    bRun    : BOOL;
END_VAR


IF bRun THEN
    bResult := HOST_TO_BE16(16#1234);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
