# F_SwapRealEx
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SwapRealEx.xml`](../examples/P_Demo_F_SwapRealEx.xml) |

---
## 1. 功能简述

**BC/BX ↔ IPC REAL 字节序转换**：BC2000/BC3100/BC9000 等总线控制器存 REAL 的 hi/lo 字与 IPC 相反。本函数就地交换。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_SwapRealEx : BOOL
```

无 VAR_INPUT。

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    fVal : REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fVal` | `REAL` | **就地交换 hi/lo 字**：BC/BX → IPC 的 REAL 字节序转换 |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。

## 5. 使用注意 / 常见坑

- **就地修改**：`fVal` 是 VAR_IN_OUT，直接改原变量。
- **仅 BC/BX 通信场景需要**——本地 PC 间通信不需要。
- 在线/Simulation 模式下编程环境已自动转换；只有 ADS 跨网络访问 BC/BX 时才用到。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SwapRealEx.xml`](../examples/P_Demo_F_SwapRealEx.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_SwapRealEx
VAR
    rResult : BOOL;
    bRun    : BOOL;
    fVal : REAL := 3.14;
END_VAR

IF bRun THEN
    rResult := F_SwapRealEx(fVal := fVal);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
