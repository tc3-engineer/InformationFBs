# F_TRIG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Trigger` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74410731.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_TRIG.xml`](../examples/P_Demo_F_TRIG.xml) |

---

## 1. 功能简述

F_TRIG 是**下降沿检测器**。`CLK = TRUE` 时 `Q = FALSE`；`CLK` 从 TRUE 变 FALSE 后，`Q` 置 TRUE 一个扫描周期。即每次 `CLK` 经历完整的（上升->下降）循环时输出一次单脉冲。

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
| `Q` | `BOOL` | `CLK` 下降沿时 TRUE 一个周期 |

### VAR_IN_OUT

无。

## 3. 行为说明

- `CLK = TRUE`：`Q = FALSE`
- `CLK` 由 TRUE → FALSE：`Q := TRUE` 仅在该周期
- 之后 `CLK` 保持 FALSE 期间：`Q = FALSE`

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- **首次扫描**：若 `CLK` 上电时已为 FALSE，不会触发 `Q`（FB 内部记录了 prev-CLK 状态）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_TRIG.xml`](../examples/P_Demo_F_TRIG.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_TRIG
VAR
    fbF_TRIG   : F_TRIG;
    bButton     : BOOL;   // 按钮输入（按下时 TRUE）
    bRelease    : BOOL;   // 按钮释放沿（单周期脉冲）
END_VAR

fbF_TRIG(
    CLK := bButton,
    Q   => bRelease
);

// 1. bButton := TRUE 保持任意时长 → bRelease 始终 FALSE
// 2. bButton := FALSE → bRelease 在该周期变 TRUE，下一周期回 FALSE
```

## 7. 相关

- R_TRIG（上升沿）

## 8. 待确认项

无。
