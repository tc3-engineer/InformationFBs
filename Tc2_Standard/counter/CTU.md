# CTU

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Counter` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74400779.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_CTU.xml`](../examples/P_Demo_CTU.xml) |

---

## 1. 功能简述

CTU 是**增计数器**（up counter）。`RESET = TRUE` 时 `CV` 复位为 0；`CU` 输入上升沿时 `CV` 加 1；当 `CV` 达到上限 `PV` 时，输出 `Q` 置 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CU     : BOOL; (* Count Up on Rising Edge*)
    RESET  : BOOL; (* Reset Counter to 0 *)
    PV     : WORD; (* Counter Limit *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CU` | `BOOL` | 上升沿：CV 加 1 |
| `RESET` | `BOOL` | TRUE：CV 复位为 0 |
| `PV` | `WORD` | 计数上限 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (* Counter reached Limit *)
    CV  : WORD; (* Current Counter Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | CV >= PV 时为 TRUE |
| `CV` | `WORD` | 当前计数值 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `RESET = TRUE` → `CV := 0`
- `RESET = FALSE` 且 `CU` 上升沿 → `CV := CV + 1`
- `CV >= PV` → `Q := TRUE`；否则 `Q := FALSE`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `PV` 类型为 `WORD`（0..65535）。
- 到 PV 后 `Q` 置 TRUE；`CV >= PV` 时的进一步行为 PDF 未描述（⚠️ 待人工确认）。
- 上升沿触发：持续 TRUE 不会重复加。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CTU.xml`](../examples/P_Demo_CTU.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CTU
VAR
    fbCTU      : CTU;
    bReset      : BOOL;   // 复位计数到 0
    bCountUp    : BOOL;   // 每个产品到位给一次上升沿
    bFull       : BOOL;   // 达到 10 件时 TRUE
    nCV         : WORD;   // 已累计件数（监视）
END_VAR

fbCTU(
    CU    := bCountUp,
    RESET := bReset,
    PV    := WORD#10,
    Q     => bFull,
    CV    => nCV
);

// 1. 强制 bReset := TRUE 一个周期 → nCV 归 0、bFull = FALSE
// 2. 重复给 bCountUp 上升沿 10 次 → nCV 增到 10、bFull = TRUE
// 3. CV >= PV 后的进一步行为 PDF 未描述（⚠️ 待人工确认）
```

## 7. 相关

- CTD（减计数）
- CTUD（增减一体）

## 8. 待确认项

无。
