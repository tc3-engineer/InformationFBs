# MODTURNS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68449419.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_MODTURNS.xml`](../examples/P_Demo_MODTURNS.xml) |

---

## 1. 功能简述

模运算的整数商部分函数。给定被除数 `lr_Value` 与模数 `lr_Arg`，返回 `lr_Value` 除以 `lr_Arg` 的**带符号整数商**（即"已转过多少圈 / 多少个模周期"），返回类型为 `DINT`。

数学定义：`MODTURNS(v, m) = LTRUNC(v / m)`（朝零截断的整数商）。例：`MODTURNS(800.56, 360) = 2`（800.56 度 = 2 整圈 + 80.56°），`MODTURNS(-400.56, 360) = -1`（-400.56 度 = -1 整圈 + (-40.56°)）。

PDF 的标准用法：从 NC 轴的累计绝对位置算出"已经转过几圈"，配合 `MODABS` 给出"圈内位置"，两者合起来等于原始累计值。是回零计算、累计圈数显示、长行程控制的必备工具。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MODTURNS : DINT
VAR_INPUT
    lr_Value : LREAL;
    lr_Arg : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_Value` | `LREAL` | 被除数（输入值，如 NC 轴累计角度） |
| `lr_Arg` | `LREAL` | 模数范围（modulo range，如 `360.0`） |

### 返回值

| 类型 | 说明 |
|---|---|
| `DINT` | 带符号整数商（圈数）。`MODTURNS(800.56, 360) = 2`；`MODTURNS(-400.56, 360) = -1`；`MODTURNS(0, 360) = 0`。**结果超出 `DINT` 范围 `[-2³¹, 2³¹-1]` 时返回未定义值**（PDF 明确警告） |

### VAR_OUTPUT

无（本符号是 `FUNCTION`）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：`MODTURNS(v, m) = LTRUNC(v / m)`，朝零截断的整数商（与 `LMOD` 同侧——`LMOD` 给"被截断后的余数"，`MODTURNS` 给"被截断后的商"）。

**取值表**：

| `(v, m)` | `MODTURNS(v, m)` | 说明 |
|---|---|---|
| `(800.56, 360)` | `2` | 两圈外加 80.56° |
| `(-400.56, 360)` | `-1` | 反向 1 整圈外加 -40.56° |
| `(360, 360)` | `1` | 整模值算 1 整圈 |
| `(359.99, 360)` | `0` | 不到一圈 |
| `(-1.0, 360)` | `0` | 微小负数朝零截断到 0 |
| `(0, 360)` | `0` | 零保持 |
| `(720, 360)` | `2` | 整两圈 |

**与 `LMOD` 的配合恒等式**：

```
MODTURNS(v, m) * m + LMOD(v, m) ≡ v
```

例 `v = 800.56, m = 360` → `2 * 360 + 40.56 = 800.56` ✓

例 `v = -400.56, m = 360` → `-1 * 360 + (-40.56) = -400.56` ✓

**与 `MODABS` 的配合**（注意符号不同）：`MODTURNS(v, m) * m + MODABS(v, m)` 不一定等于 `v`，仅在 `v ≥ 0` 时相等；`v < 0` 时由于 `MODTURNS` 朝零截、`MODABS` 朝 `-∞` 翻，会差一个 `m`。NC 应用中如果要"圈数 + 圈内无符号位置"严格还原，应使用 `FLOOR` 而非 `LTRUNC` 的圈数公式 `FLOOR(v/m)`——这不是 `MODTURNS` 提供的语义。

**PDF 明确警告——`DINT` 溢出**：

> Value range of DINT: If the value of the result of MODTURNS lies outside of the value range of DINT, an undefined result will be delivered.

`DINT = ±2.1e9`。若 `|v/m| > 2.1e9`（如累加位置 `1e12` 度、模 `360`），结果未定义（实测可能截断 / wrap）。这是工业累计计数器需特别留心的问题（高速旋转电机几年下来确实可能 `1e10` 圈以上）。

**PDF 提供的 NC 用法**：

```iecst
ModuloSetTurns := MODTURNS(NcToPlc.fPosSoll, 360);
```

## 4. 错误码 / 返回值

本函数返回类型为 `DINT`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

特殊情况：

- **`|v / m|` 超 `DINT` 范围**：PDF 明示返回 undefined（实测可能 wrap）。**必须由调用方保证商在 `±2.1e9` 内**
- `lr_Arg = 0`：除零，PDF 未明说，⚠️ 实测结果异常（可能为 0 或 `DINT_MAX`）
- `lr_Value = NaN` / `±Inf`：⚠️ 不可依赖
- 精度：`LREAL` 除法在 `|v| / |m| > 2^53` 时已无 ±1 圈精度

## 5. 使用注意 / 常见坑

- **`DINT` 范围限制是硬伤**：长寿命电机累计角度可能超 `±2.1e9` 度，对应 `DINT` 溢出。设计阶段就要评估累计圈数边界，必要时用 `LREAL DIV LREAL` 自己实现以 `LREAL` 接圈数。（工程经验补充）
- **朝零截断而非向下取整**：与 `LMOD` 配套。负数侧 `MODTURNS(-1, 360) = 0`（不是 `-1`）。如果想要"始终朝 `-∞` 取的圈数"（数学上更通用），应自己写 `LREAL_TO_DINT(FLOOR(v / m))`。
- **与 `MODABS` 不严格配对**：`MODTURNS * m + MODABS` 在负被除数时不等于 `v`。NC 工程把"无符号位置 + 圈数"做位置回零时要明确约定圈数定义——是 `LTRUNC(v/m)` 还是 `FLOOR(v/m)`。
- **模数为 0 必须检查**：除零导致未定义。
- **被除数 `NaN`/`Inf` 检查**：上游伺服位置读数异常时 `MODTURNS(NaN, 360)` 给的 `DINT` 值不可预测，可能引发后续逻辑错误。
- **整模值返回是商数侧的"含"**：`MODTURNS(360, 360) = 1`，不是 `0`；`MODTURNS(359.99, 360) = 0`。判断"刚好走过整圈"用 `MODTURNS` 单独看，避免 `LMOD = 0` 的边界检测因浮点误差失败。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MODTURNS.xml`](../examples/P_Demo_MODTURNS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：长行程伺服 + 转盘机构——伺服累计角度 lrAxisAbsPositionDeg 可能跑很多圈，
//       需要把它拆成"已转圈数"+"圈内位置"分别显示在 HMI：圈数给操作员看进度，
//       圈内位置驱动指示灯阵列。MODTURNS 给整数商（圈数），LMOD 给带符号余数。
//
// 价值：MODTURNS + LMOD 一次性把"累计角度"分解为可读两份；省去自己写 LTRUNC
//       与减法的三步代码。同时 PDF 明确为 NC 应用提供 ModuloSetTurns 标准用法。
//
// 验证：在线写 lrAxisAbsPositionDeg = 800.56 → nCompletedTurns = 2,
//       lrAngleInTurnDeg = 80.56 （2*360 + 80.56 = 800.56 ✓）；
//       写 -400.56 → -1, -40.56 （-1*360 + -40.56 = -400.56 ✓）；
//       写 720 → 2, 0 （整 2 圈）；写 359.99 → 0, 359.99 （差一点不到 1 圈）。
PROGRAM P_Demo_MODTURNS
VAR
    lrAxisAbsPositionDeg : LREAL := 800.56;   // 在线写值模拟伺服累计位置
    lrTurnSizeDeg        : LREAL := 360.0;
    nCompletedTurns      : DINT;              // MODTURNS 输出：朝零截断的整数圈数
    lrAngleInTurnDeg     : LREAL;             // LMOD 输出：带符号圈内位置
END_VAR

// 单行调用：MODTURNS 给整数商（圈数），返回 DINT
nCompletedTurns := MODTURNS(lrAxisAbsPositionDeg, lrTurnSizeDeg);

// 与 LMOD 配对：MODTURNS * m + LMOD = 原值（恒等式）
lrAngleInTurnDeg := LMOD(lrAxisAbsPositionDeg, lrTurnSizeDeg);
```

## 7. 业务场景与实际价值

- **场景**：长行程伺服回零计算、转盘累计圈数显示、累计长度按整圈对齐、累计计数器周期归约（"小时计 / 整天数 + 当天小时数"也可用 `MODTURNS / LMOD` 拆）。
- **价值**：与 `LMOD` 配对一次性把累计量分解为"周期数 + 周期内位置"；返回 `DINT` 可直接喂给计数器、显示器、`FOR` 循环；PDF 明确提供 NC 标准用法。
- **替代方案对比**：
  - 自己写 `LREAL_TO_DINT(LTRUNC(v / m))`：等价但 3 步；且如果忘了 `LTRUNC` 直接 `LREAL_TO_DINT` 是四舍五入，行为不同
  - 用 IEC `TRUNC(v / m)`：类型匹配但 `TRUNC` 在大数会溢出（与 `MODTURNS` 一样 `DINT` 限制但语义清晰度更差）
  - 单独算 `LMOD` 不算 `MODTURNS`：丢失圈数信息
  - **本函数**：单调用、`DINT` 输出可直接做数组下标 / 累计计数器；与 `LMOD` 形成完美的"商 + 余数"对

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68449419.html
- **相关函数**：`LMOD`（与本函数配对的带符号余数）、`MODABS`（无符号余数版本）、`LTRUNC`（本函数内部用到的取整函数）
