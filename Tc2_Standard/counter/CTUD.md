# CTUD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Counter` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74402187.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_CTUD.xml`](../examples/P_Demo_CTUD.xml) |

---

## 1. 功能简述

CTUD 是**双向计数器**（up/down counter）。同时支持增减计数：`RESET = TRUE` 复位为 0；`LOAD = TRUE` 装入上限 `PV`；`CU` 上升沿加 1（达到上限置 `QU`）；`CD` 上升沿减 1（减到 0 置 `QD`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CU     : BOOL; (* Count Up on Rising Edge*)
    CD     : BOOL; (* Count Down on Rising Edge*)
    RESET  : BOOL; (* Reset Counter to 0 *)
    LOAD   : BOOL; (* Load Start Value *)
    PV     : WORD; (* Start Value / Counter Limit *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CU` | `BOOL` | 上升沿：CV 加 1 |
| `CD` | `BOOL` | 上升沿：CV 减 1 |
| `RESET` | `BOOL` | TRUE：CV 复位为 0 |
| `LOAD` | `BOOL` | TRUE：CV 装入起始值 PV |
| `PV` | `WORD` | 起始值 / 计数上限 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    QU  : BOOL; (* Counter reached Limit *)
    QD  : BOOL; (* Counter reached 0 *)
    CV  : WORD; (* Current Counter Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `QU` | `BOOL` | CV >= PV 时 TRUE |
| `QD` | `BOOL` | CV = 0 时 TRUE |
| `CV` | `WORD` | 当前计数值 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `RESET = TRUE` → `CV := 0`
- `LOAD = TRUE` → `CV := PV`
- 否则 `CU` 上升沿 → `CV := CV + 1`；`CD` 上升沿 → `CV := CV - 1`（且 `CV > 0`）
- `QU := (CV >= PV)`；`QD := (CV = 0)`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `RESET` 与 `LOAD` 同时为 TRUE 时的优先级 PDF 未明确（⚠️ 待人工确认）。
- `CU` 与 `CD` 同周期都上升沿时，行为以 PDF 实现为准（⚠️ 待人工确认）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CTUD.xml`](../examples/P_Demo_CTUD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CTUD
VAR
    fbCTUD     : CTUD;
    bIn         : BOOL;   // 进料：CV+1
    bOut        : BOOL;   // 出料：CV-1
    bReset      : BOOL;   // 清零
    bLoad       : BOOL;   // 装入满库 8 件
    bFull       : BOOL;   // 已满 (CV >= 8)
    bEmpty      : BOOL;   // 已空 (CV = 0)
    nCV         : WORD;   // 当前库存
END_VAR

fbCTUD(
    CU    := bIn,
    CD    := bOut,
    RESET := bReset,
    LOAD  := bLoad,
    PV    := WORD#8,
    QU    => bFull,
    QD    => bEmpty,
    CV    => nCV
);

// 1. bReset 一次 → nCV = 0、bEmpty = TRUE
// 2. bIn 上升沿 8 次 → nCV = 8、bFull = TRUE
// 3. bOut 上升沿 8 次 → nCV = 0、bEmpty = TRUE
// 4. bLoad 一次 → nCV = 8、bFull = TRUE（一键装满）
```

## 7. 相关

- CTU
- CTD

## 8. 待确认项

- `CU` 与 `CD` 同周期都上升沿时，行为以 PDF 实现为准（⚠️ 待人工确认）。
- `RESET` 与 `LOAD` 同时为 TRUE 时的优先级 PDF 未明确（⚠️ 待人工确认）。
