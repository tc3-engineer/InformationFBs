# CTUD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Counter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74402187.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_CTUD.xml`](../examples/P_Demo_CTUD.xml) |

---

## 1. 功能简述

`CTUD` 是 **IEC 61131-3 标准块**之一，**上下双向计数器**——把 `CTU` 与 `CTD` 合二为一：`CU` 上升沿让 `CV` 加 1，`CD` 上升沿让 `CV` 减 1。同时提供两个独立输出 `QU`（达到上限 PV）和 `QD`（减到 0），以及两个控制输入 `RESET`（清零）和 `LOAD`（装入 PV）。

CV 类型 `WORD`，范围 0–65535。同一时刻同一边沿来 CU 和 CD 时行为依实现而定（PDF 未明确，TwinCAT 实测：净效果 0，即一个抵消一个）。

典型用途：双向闸机人数统计（进/出）、库存增减（入库+/出库-）、可逆电机定位计数（正向 CU 反向 CD）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    CU    : BOOL; (* Count Up on Rising Edge*)
    CD    : BOOL; (* Count Down on Rising Edge*)
    RESET : BOOL; (* Reset Counter to 0 *)
    LOAD  : BOOL; (* Load Start Value *)
    PV    : WORD; (* Start Value / Counter Limit *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CU` | `BOOL` | 上升沿 → `CV := CV + 1`（如果 `CV < 65535`） |
| `CD` | `BOOL` | 上升沿 → `CV := CV - 1`（如果 `CV > 0`） |
| `RESET` | `BOOL` | TRUE → `CV := 0`，屏蔽 CU/CD/LOAD（除非 LOAD 也为 TRUE，见行为说明） |
| `LOAD` | `BOOL` | TRUE → `CV := PV`，屏蔽 CU/CD |
| `PV` | `WORD` | 既是 CU 方向的"满"门限，也是 LOAD 装入的初值 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    QU : BOOL; (* Counter reached Limit *)
    QD : BOOL; (* Counter reached 0 *)
    CV : WORD; (* Current Counter Value *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `QU` | `BOOL` | `CV >= PV` 时为 TRUE（向上计数到顶） |
| `QD` | `BOOL` | `CV = 0` 时为 TRUE（向下计数到底） |
| `CV` | `WORD` | 当前计数值，0–65535 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 被调用时按"控制优先、其次边沿、最后比较"三个阶段依次处理。控制输入的优先级是 `RESET` > `LOAD` > `CU`/`CD`：RESET 有效时强制 `CV := 0` 并屏蔽所有其它输入；RESET 无效但 LOAD 有效时强制 `CV := PV` 并屏蔽 CU/CD；两者都无效才看 CU 和 CD 的边沿。CU 边沿让 CV 加 1（已达 65535 则回卷为 0，TwinCAT 实现），CD 边沿让 CV 减 1（已是 0 则忽略，CTUD 沿用 CTD 的"防下溢"，不允许减到负数）；同一周期 CU 和 CD 都上升沿时 TwinCAT 的实现是"互相抵消、CV 不动"，但 IEC 标准未明确，跨厂商移植不要依赖这一行为。最后用 `CV >= PV` 决定 QU，用 `CV = 0` 决定 QD，两者可能同时为 TRUE（仅当 `PV = 0`）。FB 实例的 CV 不是 retain，断电重启 CV=0、QU=FALSE、QD=TRUE。

**完整状态机**（每个 PLC 周期调用 FB 一次时，优先级从高到低）：

1. **`RESET = TRUE`**：本周期 `CV := 0`；屏蔽 CU/CD；如果 LOAD 也为 TRUE，IEC 标准未明确优先级，TwinCAT 实测为 **RESET 赢**（CV 还是 0）
2. **`LOAD = TRUE` 且 `RESET = FALSE`**：本周期 `CV := PV`；屏蔽 CU/CD
3. **`RESET = FALSE` 且 `LOAD = FALSE`**：根据 CU/CD 边沿调整 CV
   - 仅 CU 上升沿：`CV := CV + 1`（若 CV 已是 65535 → 实现相关，TwinCAT 回卷为 0）
   - 仅 CD 上升沿：`CV := CV - 1`（若 CV 已是 0 → 不动）
   - CU 和 CD 同时上升沿：净效果 0（抵消）
   - 都无上升沿：CV 不变
4. **每周期末**：`QU := (CV >= PV)`，`QD := (CV = 0)`

**关键语义**：

- **RESET 与 LOAD 同时为 TRUE**：PDF 标准上未定义优先级，**这是已知的"未定义行为"**——业务侧应避免同周期同时拉高。TwinCAT 当前实现 RESET 赢，但跨厂商移植不要依赖。
- **QU 和 QD 可能同时为 TRUE**：当 `PV = 0` 时 `CV >= PV` 永远成立且 `CV = 0` 也成立。
- **CU/CD 同边沿抵消**：业务上别依赖这种巧合，应保证 CU 和 CD 不会在同一 PLC 周期都上升。
- **CV 上限 WORD**：超 65535 回卷为 0；要更大上限自己用 UDINT。

## 4. 错误码 / 返回值

`CTUD` 是标准计数器，**无错误码、无 HRESULT**。

## 5. 使用注意 / 常见坑

- **RESET + LOAD 优先级未定义**：业务设计上应避免同时拉高。如果必须，建议先 RESET 一拍再 LOAD（分两个周期）。
- **CU / CD 同周期都上升 = 抵消**：双向闸机如果一进一出在同一 PLC 周期发生 → 统计漏一对。需要绝对准确时把 CU/CD 接到中断或更快速度的 R_TRIG。
- **65535 回卷**：长期累加场景必用 UDINT 自加。
- **`QU` 不会因为继续增加而清零**：达到 PV 后继续 CU 上升，CV 继续增（除非到 65535 回卷），QU 始终 TRUE。
- **首次扫描 CV = 0**：QD 一上电就是 TRUE。如果业务初始化逻辑依赖 QD=FALSE，请上电后先 LOAD 一拍。
- **断电不保持**：CV 非 RETAIN。
- **`CU` 与 `CD` 必须是脉冲**：与 CTU/CTD 同坑，电平触发只数一次。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CTUD.xml`](../examples/P_Demo_CTUD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：仓库入出库计数器。每次入库扫码（bIncomingScan 上升沿）库存+1；每次
//       出库扫码（bOutgoingScan 上升沿）库存-1；满 500 件（QU）禁止入库；
//       为 0 件（QD）禁止出库；月底盘点用 bMonthlyReset 清零、bRestoreLast
//       用 LOAD 把上月结余装回。
PROGRAM P_Demo_CTUD
VAR
    fbStockCounter        : CTUD;
    bIncomingScan         : BOOL;
    bOutgoingScan         : BOOL;
    bMonthlyReset         : BOOL;
    bRestoreLast          : BOOL;
    nWarehouseCapacity    : WORD := 500;
    bWarehouseFull        : BOOL;
    bWarehouseEmpty       : BOOL;
    nCurrentStock         : WORD;
END_VAR

fbStockCounter(
    CU    := bIncomingScan,
    CD    := bOutgoingScan,
    RESET := bMonthlyReset,
    LOAD  := bRestoreLast,
    PV    := nWarehouseCapacity,
    QU    => bWarehouseFull,
    QD    => bWarehouseEmpty,
    CV    => nCurrentStock
);
```

## 7. 业务场景与实际价值

- **场景**：闸机进出统计、仓库出入库、可逆电机正反向定位、生产线良品/不良品净计数。
- **价值**：把双向"上+下+复位+装载"一次性封装；手写需要约 15-20 行边界条件代码（防下溢、防回卷、4 路控制优先级）。
- **替代方案对比**：
  - **CTU + CTD 各一个**：能拼但 CV 同步麻烦
  - **手写 INT 累加**：可以但 4 路控制 + 边沿检测代码冗长
  - **本 FB**：IEC 标准双向计数

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74402187.html
- **相关 FB**：`CTU`、`CTD`、`R_TRIG`
