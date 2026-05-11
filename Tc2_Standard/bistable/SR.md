# SR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bistable` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74396043.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_SR.xml`](../examples/P_Demo_SR.xml) |

---

## 1. 功能简述

SR 是双稳态（bistable）功能块，**SET 优先（dominant）**。即当 `SET1` 与 `RESET` 同时为 TRUE 时，输出 `Q1` 被置位为 TRUE。

逻辑等价：`Q1 := (NOT RESET AND Q1) OR SET1;`

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    SET1  : BOOL;
    RESET : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `SET1` | `BOOL` | 置位输入（**优先**）— 上升沿时 `Q1` 置 TRUE |
| `RESET` | `BOOL` | 复位输入 — 上升沿时 `Q1` 置 FALSE |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q1 : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q1` | `BOOL` | 输出 |

### VAR_IN_OUT

无。

## 3. 行为说明

内部实现（PDF 原文逐字搬运）：

```iecst
Q1 := (NOT RESET AND Q1) OR SET1;
```

真值表：

| `SET1` | `RESET` | `Q1`（前一周期） | `Q1`（当前） |
|---|---|---|---|
| FALSE | FALSE | FALSE | FALSE |
| FALSE | FALSE | TRUE  | TRUE（保持）|
| FALSE | TRUE  | × | FALSE |
| TRUE  | × | × | TRUE |

`×` 表示任意值。**SET 优先于 RESET**。

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。

## 5. 使用注意 / 常见坑

- **SR vs RS**：SR 适合"启动信号必须赢过持续复位"的场景，例如：报警闩锁——故障来了必须置位，即便操作员按住复位按钮。RS 反之。（工程经验补充）
- **不要用 SR 实现安全急停**。安全急停语义是"复位永远赢"，应当用 RS 或硬接线安全模块。（工程经验补充）
- **PDF 接口表称 `SET1` / `RESET` 为 "on a rising edge" 输入，但其下面给出的布尔等价方程 `Q1 := (NOT RESET AND Q1) OR SET1` 是组合逻辑式（无边沿检测）。两说法在 PDF 中并存，PDF 未指明哪种为准（⚠️ 待人工确认）。**

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SR.xml`](../examples/P_Demo_SR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SR
VAR
    fbSR     : SR;
    bAlarm   : BOOL;    // 即时报警条件（如温度超限）
    bAck     : BOOL;    // 操作员复位按钮
    bAlarmL  : BOOL;    // 闩锁后的报警位
END_VAR

fbSR(
    SET1  := bAlarm,
    RESET := bAck,
    Q1    => bAlarmL
);

// 一旦 bAlarm 出现，bAlarmL 闩锁为 TRUE，
// 即便瞬时报警条件消失也不会自行复位，必须 bAck 上升沿才能清除。
// 若 bAlarm 与 bAck 同时为 TRUE，bAlarmL 仍为 TRUE（SET 优先）。
```

## 7. 相关

- 同类：`RS`（RESET 主导双稳态）

## 8. 待确认项

- PDF 接口表与布尔方程的边沿/电平语义不一致（⚠️ 待人工确认，详见 §5）。
