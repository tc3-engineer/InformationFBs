# F_SplitBIC
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
| Example | [`examples/P_Demo_F_SplitBIC.xml`](../examples/P_Demo_F_SplitBIC.xml) |

---
## 1. 功能简述

**拆分 BIC 为结构**：把 BIC 按已知 identifier 切成子串放进 `ST_SplittedBIC` 各字段。未识别的子串放入 `sUndefined`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_SplitBIC : ST_SplittedBIC
VAR_INPUT
    sBICValue : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sBICValue` | `STRING` | Beckhoff Identification Code (BIC) |

### 返回值

`ST_SplittedBIC` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `ST_SplittedBIC`。

## 5. 使用注意 / 常见坑

- BIC 字段尾部空格自动去除；未用字段为空字符串。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitBIC.xml`](../examples/P_Demo_F_SplitBIC.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_SplitBIC
VAR
    rResult : ST_SplittedBIC;
    bRun    : BOOL;
    sBIC : STRING := '1P193995SBTN0002agdw1KEL7411 Q1 2P112104020018';
END_VAR

IF bRun THEN
    rResult := F_SplitBIC(sBIC);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
