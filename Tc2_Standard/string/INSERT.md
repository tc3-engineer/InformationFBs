# INSERT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/insert.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_INSERT.xml`](../examples/P_Demo_INSERT.xml) |

---

## 1. 功能简述

**插入子串**。把 `STR2` 插入到 `STR1` 的第 `POS` 个字符之后。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION INSERT: STRING(255)
VAR_INPUT
    STR1   : STRING(255);
    STR2   : STRING(255);
    POS    : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 原字符串 |
| `STR2` | `STRING(255)` | 要插入的字符串 |
| `POS` | `INT` | 插入点（在第 POS 个字符之后） |

### 返回值

`STRING(255)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `INSERT('SUSI','XY',2)` → `'SUXYSI'`
- IL 形式：
```iecst
LD 'SUSI'
INSERT 'XY',2
ST Var1 (* Result is 'SUXYSI' *)
```
- ST 形式：
```iecst
Var1 := INSERT('SUSI','XY',2);
```

## 4. 错误码 / 返回值

返回值：`STRING(255)`。PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `POS = 0` 表示插到最前面；`POS = LEN(STR1)` 表示拼到末尾（等价 `CONCAT`）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_INSERT.xml`](../examples/P_Demo_INSERT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_INSERT
VAR
    sResult : STRING(255);   // INSERT 的返回值（监视）
    bRun    : BOOL;          // TRUE 触发一次调用
END_VAR

IF bRun THEN
    sResult := INSERT('SUSI','XY',2);
    bRun := FALSE;
END_IF;

// 1. 强制 bRun := TRUE 一个周期
// 2. 观察 sResult = 'SUXYSI'
// 3. bRun 自动复位到 FALSE
```

## 7. 相关

- DELETE（反向操作）
- CONCAT

## 8. 待确认项

无。
