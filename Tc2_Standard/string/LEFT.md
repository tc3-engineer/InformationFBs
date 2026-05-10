# LEFT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/left.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LEFT.xml`](../examples/P_Demo_LEFT.xml) |

---

## 1. 功能简述

**取左侧前 N 字符**。返回 `STR` 最左 `SIZE` 个字符。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LEFT: STRING(255)
VAR_INPUT
    STR    : STRING(255);
    SIZE   : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 源字符串 |
| `SIZE` | `INT` | 取的字符数 |

### 返回值

`STRING(255)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `LEFT('SUSI',3)` → `'SUS'`
- IL 形式：
```iecst
LD 'SUSI'
LEFT 3
ST Var1 (* Result is 'SUS' *)
```
- ST 形式：
```iecst
Var1 := LEFT('SUSI',3);
```

## 4. 错误码 / 返回值

返回值：`STRING(255)`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `SIZE` 大于实际长度时返回原字符串（⚠️ 待人工确认）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LEFT.xml`](../examples/P_Demo_LEFT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LEFT
VAR
    sResult : STRING(255);   // LEFT 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := LEFT('SUSI',3);
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 'SUS'
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- RIGHT
- MID

## 8. 待确认项

- `SIZE` 大于实际长度时返回原字符串（⚠️ 待人工确认）。
