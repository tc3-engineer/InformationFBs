# CTD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Counter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74399371.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_CTD.xml`](../examples/P_Demo_CTD.xml) |

---

## 1. 功能简述

`CTD` 是 **IEC 61131-3 标准块**之一，实现**向下递减计数器**（Counter Down）。`LOAD` 上升时把起始值 `PV` 装入计数变量 `CV`；之后每次 `CD` 输入上升沿让 `CV` 减 1；`CV` 减到 0 时输出 `Q` 置 TRUE 且不再继续减。

计数值类型 `WORD`（16 位无符号），范围 0–65535。CTD 不会减到负数——到 0 后停止。

典型用途：倒计时余量（剩余产品数）、限次操作（剩余可点击次数）、库存预警（剩余库存满 0 报警）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CD   : BOOL; (* Count Down on Rising Edge *)
    LOAD : BOOL; (* Load Start Value *)
    PV   : WORD; (* Start Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CD` | `BOOL` | 计数输入。**上升沿** 时 `CV` 减 1（前提是 `CV > 0`） |
| `LOAD` | `BOOL` | 装载输入。TRUE 时 `CV := PV`，`Q := FALSE`；屏蔽 `CD` |
| `PV` | `WORD` | 起始值（装载时使用，也是计数器允许的最大初始值） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL; (* Counter reached 0 *)
    CV : WORD; (* Current Counter Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `CV = 0` 时为 TRUE，否则为 FALSE |
| `CV` | `WORD` | 当前计数值 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 被调用时按"装载优先、其次边沿、最后比较"三个阶段依次处理：先看 `LOAD` 是否有效，有效则把起始值 `PV` 强制写入 `CV` 并屏蔽本周期的计数边沿；其次比较 `CD` 当前值与上一周期保存的值，若发生 FALSE→TRUE 跃迁且 `CV > 0` 则把 `CV` 减 1；若已经是 0 则忽略此次边沿——CTD 不会减成负数也不会回卷成 65535，这是 IEC 标准明确的"防下溢"。最后用 `CV = 0` 判断决定输出 `Q`。注意 CTD 与 CTU 接口不对称：CTU 有 RESET（清零）但 CTD 没有，CTD 改用 LOAD 装入 PV 来重置状态。FB 实例的 CV 不是 retain，断电重启 `CV = 0`、`Q = TRUE`（已到底状态），必须先 LOAD 一次才能开始倒数。

**完整状态机**（每个 PLC 周期调用 FB 一次时）：

1. **`LOAD = TRUE`**：本周期 `CV := PV`，`Q := FALSE`（除非 `PV = 0`，此时立即 `Q := TRUE`）；屏蔽 `CD`
2. **`LOAD = FALSE` 且 `CD` 上升沿且 `CV > 0`**：`CV := CV - 1`
3. **`LOAD = FALSE` 且 `CD` 上升沿且 `CV = 0`**：不动作（不会减到负数）
4. **`LOAD = FALSE` 且 `CD` 无上升沿**：`CV` 不变
5. **每周期末**：`Q := (CV = 0)`

**关键语义**：

- **必须先 LOAD 才能开始数**：FB 上电后 `CV = 0`、`Q = TRUE`（已"到底"状态）；不先来一次 LOAD 上升沿把 PV 装入，`CD` 来再多上升沿也无效。
- **`CD` 必须是脉冲**：与 `CTU` 一样，电平触发只数一次。需要持续触发请用 R_TRIG 把电平转脉冲。
- **CV 到 0 后停在 0**：CTD 不会回卷为 65535，这是 IEC 标准明确的"防下溢"语义。
- **LOAD 优先于 CD**：同周期都为高时 LOAD 赢，本周期 CD 边沿丢失。

## 4. 错误码 / 返回值

`CTD` 是标准计数器，**无错误码、无 HRESULT**。`PV = 0` 装载后 `Q` 立即为 TRUE。

## 5. 使用注意 / 常见坑

- **首次必须 LOAD**：新手最常见的错是直接开始喂 CD 边沿，结果 CV 一直是 0、Q 一直是 TRUE，看似"不工作"——实际是没装载。
- **`CD` 是边沿不是电平**：与 CTU 同坑，电平触发只减一次。
- **CV 不会减到负数**：减到 0 后再来 CD 上升沿无效，业务上要"超额扣减"必须自己组合（如 CTUD 或自写 INT 累加）。
- **LOAD 一直保持 TRUE 等于禁用计数**：因为每周期都重新装 PV。要让计数器"自由运行"必须 LOAD 一拍后立即回 FALSE（典型做法是用 R_TRIG）。
- **CV 类型 WORD**：上限 65535，超过这个起始值必须自己用 UDINT 维护。
- **断电不保持**：CV 非 RETAIN，断电重启 CV=0、Q=TRUE。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CTD.xml`](../examples/P_Demo_CTD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：自动售货机一次充值 50 元，每次出货扣 5 元 = 50 / 5 = 10 次。剩余 0
//       次（CV=0）时点亮"请充值"指示灯，停止出货。
PROGRAM P_Demo_CTD
VAR
    fbCreditCounter   : CTD;
    bRechargeReq      : BOOL;             // 投币 / 充值（上升沿装载）
    bDispenseDone     : BOOL;             // 出货完成脉冲（上升沿扣 1）
    nMaxDispenses     : WORD := 10;       // 50 元 / 5 元 = 10 次
    bNeedRecharge     : BOOL;             // CV=0 时变 TRUE → 提示充值
    nDispensesLeft    : WORD;             // 剩余次数（监视用）
END_VAR

fbCreditCounter(
    CD   := bDispenseDone,
    LOAD := bRechargeReq,
    PV   := nMaxDispenses,
    Q    => bNeedRecharge,
    CV   => nDispensesLeft
);
```

## 7. 业务场景与实际价值

- **场景**：余量倒计时（产品/能源/credit）、库存预警（剩余件数到 0 报警）、限次操作（密码错误 3 次锁定）、批次倒计完成提醒。
- **价值**：1 次调用拿到"装载/减/到底停止/状态比较"完整状态机；手写约 8 行，且容易忘记防下溢导致 WORD 回卷。
- **替代方案对比**：
  - **手写 UDINT --**：写 `IF nC > 0 THEN nC := nC - 1; END_IF` 加边沿检测，约 6 行
  - **`CTUD`**：双向都能用但接口大；只倒数用 CTD 简洁
  - **本 FB**：IEC 标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74399371.html
- **相关 FB**：`CTU`（向上计数）、`CTUD`（上下双向）、`R_TRIG`
