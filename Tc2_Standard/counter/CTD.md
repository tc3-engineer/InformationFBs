# CTD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Counter` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74399371.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_CTD.xml`](../examples/P_Demo_CTD.xml) |

---

## 1. 功能简述

CTD 是**减计数器**（down counter）。`LOAD = TRUE` 时把计数变量 `CV` 初始化为上限 `PV`；`CD` 输入有从 FALSE 到 TRUE 的上升沿时，`CV` 减 1（在 `CV > 0` 时）；当 `CV = 0` 时，输出 `Q` 置 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CD     : BOOL; (* Count Down on Rising Edge *)
    LOAD   : BOOL; (* Load Start Value *)
    PV     : WORD; (* Start Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CD` | `BOOL` | 上升沿：CV 减 1 |
| `LOAD` | `BOOL` | TRUE：把 CV 设为起始值 PV |
| `PV` | `WORD` | 起始值 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (* Counter reached 0 *)
    CV  : WORD; (* Current Counter Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | CV = 0 时为 TRUE |
| `CV` | `WORD` | 当前计数值 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `LOAD = TRUE` 任一周期 → `CV := PV`
- `LOAD = FALSE` 且 `CD` 上升沿 → 若 `CV > 0` 则 `CV := CV - 1`
- `CV = 0` → `Q := TRUE`；否则 `Q := FALSE`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- `PV` 类型为 `WORD`（无符号 16 位 0..65535），不是 INT。
- 输入是**电平**触发：`CD` 必须有 FALSE→TRUE 边沿，持续 TRUE 不会重复减。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CTD.xml`](../examples/P_Demo_CTD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CTD
VAR
    fbCTD      : CTD;
    bLoad       : BOOL;   // 脉冲一次：把 CV 装入 5
    bCountDown  : BOOL;   // 每给一次上升沿 CV 减 1
    bDone       : BOOL;   // CV 减到 0 时 TRUE
    nCV         : WORD;   // 当前剩余计数（监视）
END_VAR

fbCTD(
    CD   := bCountDown,
    LOAD := bLoad,
    PV   := WORD#5,
    Q    => bDone,
    CV   => nCV
);

// 1. 强制 bLoad := TRUE 一个周期 → nCV 变成 5
// 2. 重复给 bCountDown FALSE → TRUE → FALSE 五次 → nCV 减到 0
// 3. nCV = 0 时观察 bDone 为 TRUE
```

## 7. 相关

- CTU（增计数）
- CTUD（增减一体）

## 8. 待确认项

无。
