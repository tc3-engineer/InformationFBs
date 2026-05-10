# FIND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/find.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FIND.xml`](../examples/P_Demo_FIND.xml) |

---

## 1. 功能简述

**查找子串位置**。返回 `STR2` 在 `STR1` 中第一次出现的起始位置（1 起）；未找到返回 0。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIND: INT
VAR_INPUT
    STR1   : STRING(255);
    STR2   : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 在其中搜索的字符串 |
| `STR2` | `STRING(255)` | 要搜索的子串 |

### 返回值

`INT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `FIND('SUXYSI','XY')` → `3`
- IL 形式：
```iecst
LD 'SUXYSI'
FIND 'XY'
ST Var1 (* Result is 3 *)
```
- ST 形式：
```iecst
Var1 := FIND('SUXYSI','XY');
```

## 4. 错误码 / 返回值

返回值：`INT`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- 返回 0 表示**未找到**——这是 IEC 约定，不是 -1。
- **位置从 1 开始**计数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIND.xml`](../examples/P_Demo_FIND.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FIND
VAR
    sResult : INT;   // FIND 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := FIND('SUXYSI','XY');
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 3
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- MID（按位置取子串）
- LEFT
- RIGHT

## 8. 待确认项

无。
