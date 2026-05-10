# REPLACE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/replace.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_REPLACE.xml`](../examples/P_Demo_REPLACE.xml) |

---

## 1. 功能简述

**替换子串**。从 `STR1` 第 `P` 个字符起、共 `L` 个字符替换为 `STR2`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION REPLACE: STRING(255)
VAR_INPUT
    STR1   : STRING(255);
    STR2   : STRING(255);
    L      : INT;
    P      : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 源字符串 |
| `STR2` | `STRING(255)` | 替换串 |
| `L` | `INT` | 要替换的字符数 |
| `P` | `INT` | 起始位置（1 起） |

### 返回值

`STRING(255)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `REPLACE('SUXYSI','K',2,2)` → `'SKYSI'`
- IL 形式：
```iecst
LD 'SUXYSI'
REPLACE 'K',2,2
ST Var1 (* Result is 'SKYSI' *)
```
- ST 形式：
```iecst
Var1 := REPLACE('SUXYSI','K',2,2);
```

## 4. 错误码 / 返回值

返回值：`STRING(255)`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- **形参顺序与 DELETE 反过来**：DELETE 用 `(STR, LEN, POS)`，REPLACE 用 `(STR1, STR2, L, P)`。注意 PDF 原文用 `L, P` 而不是 `LEN, POS`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_REPLACE.xml`](../examples/P_Demo_REPLACE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_REPLACE
VAR
    sResult : STRING(255);   // REPLACE 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := REPLACE('SUXYSI','K',2,2);
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 'SKYSI'
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- DELETE + INSERT 组合
- CONCAT

## 8. 待确认项

无。
