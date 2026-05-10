# WREPLACE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/wreplace.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_WREPLACE.xml`](../examples/P_Demo_WREPLACE.xml) |

---

## 1. 功能简述

**WSTRING 版本**：替换 WSTRING 中的子串。 与 `REPLACE` 同语义，但操作 `WSTRING`（双字节字符）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WREPLACE: WSTRING(255)
VAR_INPUT
    STR1   : WSTRING(255);
    STR2   : WSTRING(255);
    L      : INT;
    P      : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 源 WSTRING |
| `STR2` | `WSTRING(255)` | 替换串 |
| `L` | `INT` | 要替换的字符数 |
| `P` | `INT` | 起始位置 |

### 返回值

`WSTRING(255)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `WREPLACE("SUXYSI","K",2,2)` → `"SKYSI"`
- IL 形式：
```iecst
LD "..."
WREPLACE ...
ST Var1
```
- ST 形式：
```iecst
Var1 := WREPLACE("SUXYSI","K",2,2);
```

## 4. 错误码 / 返回值

返回值：`WSTRING(255)`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- WSTRING 字面量用双引号（`"abc"`），STRING 用单引号。
- **所有位置参数仍是 1 起**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WREPLACE.xml`](../examples/P_Demo_WREPLACE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WREPLACE
VAR
    sResult : WSTRING(255);   // WREPLACE 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := WREPLACE("SUXYSI","K",2,2);
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = "SKYSI"
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- REPLACE（STRING 版）

## 8. 待确认项

无。
