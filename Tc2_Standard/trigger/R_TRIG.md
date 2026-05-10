# R_TRIG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Trigger` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74412139.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_R_TRIG.xml`](../examples/P_Demo_R_TRIG.xml) |

---

## 1. 功能简述

R_TRIG 是**上升沿检测器**。`CLK = FALSE` 时 `Q = FALSE`；`CLK` 从 FALSE 变 TRUE 后，`Q` 置 TRUE 一个扫描周期。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CLK    : BOOL; (* Signal to detect *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CLK` | `BOOL` | 待检测的布尔信号 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q   : BOOL; (* Edge detected *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `CLK` 上升沿时 TRUE 一个周期 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `CLK = FALSE`：`Q = FALSE`
- `CLK` 由 FALSE → TRUE：`Q := TRUE` 仅在该周期
- 之后 `CLK` 保持 TRUE 期间：`Q = FALSE`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- **首次扫描**：若 `CLK` 上电时已为 TRUE，不会立即触发 `Q`。需要先有 FALSE 周期才能再检上升沿。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_R_TRIG.xml`](../examples/P_Demo_R_TRIG.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_R_TRIG
VAR
    fbR_TRIG   : R_TRIG;
    bButton     : BOOL;   // 按钮输入
    bPress      : BOOL;   // 按钮按下沿（单周期脉冲）
END_VAR

fbR_TRIG(
    CLK := bButton,
    Q   => bPress
);

// 1. bButton := FALSE 保持 → bPress 始终 FALSE
// 2. bButton := TRUE → bPress 在该周期为 TRUE，下一周期回 FALSE
// 3. bButton 持续 TRUE → bPress 不再触发，必须先 FALSE 再 TRUE
```

## 7. 相关

- F_TRIG（下降沿）

## 8. 待确认项

无。
