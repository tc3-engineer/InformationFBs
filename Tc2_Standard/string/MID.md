# MID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/mid.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_MID.xml`](../examples/P_Demo_MID.xml) |

---

## 1. 功能简述

**取中间子串**。从 `STR` 的第 `POS` 字符起取 `LEN` 个字符。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MID: STRING(255)
VAR_INPUT
    STR    : STRING(255);
    LEN    : INT;
    POS    : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 源字符串 |
| `LEN` | `INT` | 取的字符数 |
| `POS` | `INT` | 起始位置（1 起） |

### 返回值

`STRING(255)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `MID('SUSI',2,2)` → `'US'`
- IL 形式：
```iecst
LD 'SUSI'
MID 2,2
ST Var1 (* Result is 'US' *)
```
- ST 形式：
```iecst
Var1 := MID('SUSI',2,2);
```

## 4. 错误码 / 返回值

返回值：`STRING(255)`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- **位置 1 起**。
- `POS + LEN - 1` 超出原长时行为以 PDF 实现为准（⚠️ 待人工确认）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MID.xml`](../examples/P_Demo_MID.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_MID
VAR
    sResult : STRING(255);   // MID 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := MID('SUSI',2,2);
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 'US'
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- LEFT
- RIGHT
- FIND

## 8. 待确认项

- `POS + LEN - 1` 超出原长时行为以 PDF 实现为准（⚠️ 待人工确认）。
