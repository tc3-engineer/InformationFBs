# WFIND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/wfind.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_WFIND.xml`](../examples/P_Demo_WFIND.xml) |

---

## 1. 功能简述

**WSTRING 版本**：在 WSTRING 中查找子串位置。 与 `FIND` 同语义，但操作 `WSTRING`（双字节字符）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WFIND: INT
VAR_INPUT
    STR1   : WSTRING(255);
    STR2   : WSTRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 目标 WSTRING |
| `STR2` | `WSTRING(255)` | 要搜索的子串 |

### 返回值

`INT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `WFIND("SUXYSI","XY")` → `3`
- IL 形式：
```iecst
LD "..."
WFIND ...
ST Var1
```
- ST 形式：
```iecst
Var1 := WFIND("SUXYSI","XY");
```

## 4. 错误码 / 返回值

返回值：`INT`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- WSTRING 字面量用双引号（`"abc"`），STRING 用单引号。
- **所有位置参数仍是 1 起**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WFIND.xml`](../examples/P_Demo_WFIND.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WFIND
VAR
    sResult : INT;   // WFIND 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := WFIND("SUXYSI","XY");
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 3
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- FIND（STRING 版）

## 8. 待确认项

无。
