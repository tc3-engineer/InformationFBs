# LEN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/len.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LEN.xml`](../examples/P_Demo_LEN.xml) |

---

## 1. 功能简述

**取字符串长度**。返回 `STR` 的字符数（不含末尾 NUL）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LEN: INT
VAR_INPUT
    STR    : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 目标字符串 |

### 返回值

`INT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `LEN('SUSI')` → `4`
- IL 形式：
```iecst
LD 'SUSI'
LEN
ST Var1 (* Result is 4 *)
```
- ST 形式：
```iecst
Var1 := LEN('SUSI');
```

## 4. 错误码 / 返回值

返回值：`INT`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- PDF 中 VAR_INPUT 末尾误写为 `END_VA`（缺 R），文档逐字保留为 `END_VAR`。
- 返回 INT 而非 UDINT——上限 32767。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LEN.xml`](../examples/P_Demo_LEN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LEN
VAR
    sResult : INT;   // LEN 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := LEN('SUSI');
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 4
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- FIND

## 8. 待确认项

无。
