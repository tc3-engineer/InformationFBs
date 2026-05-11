# RS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bistable` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74394507.html |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_RS.xml`](../examples/P_Demo_RS.xml) |

---

## 1. 功能简述

RS 是双稳态（bistable）功能块，**RESET 优先（dominant）**。即当 `SET` 与 `RESET1` 同时为 TRUE 时，输出 `Q1` 被复位为 FALSE。

逻辑等价：`Q1 := NOT RESET1 AND (Q1 OR SET);`

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    SET    : BOOL;
    RESET1 : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `SET` | `BOOL` | 置位输入 — 上升沿时 `Q1` 置 TRUE |
| `RESET1` | `BOOL` | 复位输入（**优先**）— 上升沿时 `Q1` 置 FALSE |

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
Q1 := NOT RESET1 AND (Q1 OR SET);
```

真值表：

| `RESET1` | `SET` | `Q1`（前一周期） | `Q1`（当前） |
|---|---|---|---|
| FALSE | FALSE | FALSE | FALSE |
| FALSE | FALSE | TRUE  | TRUE（保持）|
| FALSE | TRUE  | × | TRUE |
| TRUE  | × | × | FALSE |

`×` 表示任意值。**RESET 优先于 SET**。

## 4. 错误码 / 返回值

PDF 未列出错误码（无错误码）。RS 是纯组合 + 锁存逻辑。

## 5. 使用注意 / 常见坑

- **RS vs SR 选择**：需要"安全/紧急停止覆盖一切启动"语义时用 RS（RESET 主导）；需要"启动信号必须能赢过持续的复位"语义时用 SR（SET 主导）。**安全相关电路通常用 RS**。（工程经验补充）
- **PDF 接口表称 `SET` / `RESET1` 为 "on a rising edge" 输入，但其下面给出的布尔等价方程 `Q1 := NOT RESET1 AND (Q1 OR SET)` 是组合逻辑式（无边沿检测）。两说法在 PDF 中并存**，以方程为准（⚠️ 待人工确认；推荐用户在使用时按上升沿语义建模）。
- 上电时 Q1 默认为 FALSE（除非声明为 PERSISTENT/RETAIN）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RS.xml`](../examples/P_Demo_RS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_RS
VAR
    fbRS    : RS;
    bStart  : BOOL;     // 操作员启动按钮
    bEStop  : BOOL;     // 急停信号（常开，按下时为 TRUE）
    bRunOk  : BOOL;     // 运行允许位
END_VAR

fbRS(
    SET    := bStart,
    RESET1 := bEStop,
    Q1     => bRunOk
);

// bRunOk 为 TRUE → 允许运行
// 即便操作员按住 bStart，只要 bEStop = TRUE，bRunOk 必为 FALSE
```

## 7. 相关

- 同类：`SR`（SET 主导双稳态）

## 8. 待确认项

- PDF 接口表与布尔方程的边沿/电平语义不一致（⚠️ 待人工确认，详见 §5）。
