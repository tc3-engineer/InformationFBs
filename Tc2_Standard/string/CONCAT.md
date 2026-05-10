# CONCAT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/concat.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_CONCAT.xml`](../examples/P_Demo_CONCAT.xml) |

---

## 1. 功能简述

**拼接两个字符串**。返回 `STR1` 后跟 `STR2` 的合并结果。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION CONCAT: STRING(255)
VAR_INPUT
    STR1   : STRING(255);
    STR2   : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 前段字符串 |
| `STR2` | `STRING(255)` | 后段字符串 |

### 返回值

`STRING(255)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `CONCAT('Mr.','Smith')` → `'Mr.Smith'`
- IL 形式：
```iecst
LD 'SUSI'
CONCAT 'WILLI'
ST Var1 (* Result is 'SUSIWILLI' *)
```
- ST 形式：
```iecst
Var1 := CONCAT('SUSI','WILLI');
```

## 4. 错误码 / 返回值

返回值：`STRING(255)`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- 返回值为 `STRING(255)`——超出 255 字符部分被截断。
- 用 `+` 操作符与 `CONCAT` 等价（IEC 扩展），但显式调用更可读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CONCAT.xml`](../examples/P_Demo_CONCAT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CONCAT
VAR
    sResult : STRING(255);   // CONCAT 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := CONCAT('Mr.','Smith');
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 'Mr.Smith'
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- WCONCAT（WSTRING 版）
- INSERT
- REPLACE

## 8. 待确认项

无。
