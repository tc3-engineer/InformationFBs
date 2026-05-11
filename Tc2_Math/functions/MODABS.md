# MODABS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68447883.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_MODABS.xml`](../examples/P_Demo_MODABS.xml) |

---

## 1. 功能简述

无符号浮点模运算函数。给定被除数 `lr_val` 与模数 `lr_mod`，返回 `lr_val` 在模数范围内的**无符号**余数，结果总是落在 `[0.0, |lr_mod|)` 半开区间内。

数学定义：`MODABS(v, m) = v - FLOOR(v / m) * m`，即先朝 `-∞` 取整数商（注意是 `FLOOR` 不是 `LTRUNC`），再用 `余数 = 被除数 - 商 * 除数`。例：`MODABS(400.56, 360) = 40.56`，`MODABS(-400.56, 360) = 319.44`（**负被除数也给正余数**）。

这正是 NC 伺服轴的"模值位置"语义：物理上轴在 `[0, 360)` 范围内连续旋转，PDF 提供的标准用法 `ModuloSetPosition := MODABS(NcToPlc.fPosSoll, 360);` 把任何累计角度（包括多圈或反向）归一到一圈内的物理位置。这与 `LMOD`（保留符号）形成对照。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MODABS : LREAL
VAR_INPUT
    lr_val : LREAL;
    lr_mod : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_val` | `LREAL` | 被除数（输入值，如 NC 轴累计角度） |
| `lr_mod` | `LREAL` | 模数范围（modulo range，正数，如 `360.0`） |

### 返回值

| 类型 | 说明 |
|---|---|
| `LREAL` | 无符号余数，范围 `[0.0, |lr_mod|)`。`MODABS(400.56, 360) = 40.56`；`MODABS(-400.56, 360) = 319.44`；`MODABS(0, 360) = 0` |

### VAR_OUTPUT

无（本符号是 `FUNCTION`）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：`MODABS(v, m) = v - FLOOR(v / m) * m`。与 `LMOD` 的差别就在 `FLOOR` vs `LTRUNC`：`FLOOR` 朝 `-∞` 取，使得负被除数的余数被"翻正"。

**取值表**：

| `(v, m)` | `MODABS(v, m)` | `LMOD(v, m)` 对照 | 说明 |
|---|---|---|---|
| `(400.56, 360)` | `40.56` | `40.56` | 正被除数两者一致 |
| `(-400.56, 360)` | `319.44` | `-40.56` | **负被除数差异最大** |
| `(720.7, 360)` | `0.7` | `0.7` | 多圈正向 |
| `(-720.7, 360)` | `359.3` | `-0.7` | 多圈反向 |
| `(360, 360)` | `0` | `0` | 整模值归零 |
| `(-1.0, 360)` | `359.0` | `-1.0` | 微小负数翻正 |
| `(0, 360)` | `0` | `0` | 零保持 |

**为什么 NC 轴一定要用 `MODABS`**：伺服编码器的"绝对位置"是单方向累计的，跑了几圈后累计到 `1080°` 也好、反向跑到 `-540°` 也好，物理上轴的"现在面朝哪儿"必须是 `[0, 360)` 的某个值。如果用 `LMOD`，反向跑出的 `-90°` 不会被翻成 `270°`——HMI 显示 `-90°` 而轴上贴的角度刻度是 `0..360`，运维就会困惑。

**PDF 提供的标准用法**：

```iecst
ModuloSetPosition := MODABS(NcToPlc.fPosSoll, 360);
```

**边界**：

- `lr_mod = 0.0`：除零，PDF 未规定，⚠️ 实测结果 `NaN`
- `lr_mod < 0`：PDF 未明说，建议总是传正模数；负模数行为按 `FLOOR(v/m) * m` 推导也能得正余数，但语义上不直观
- `lr_val = NaN` / `±Inf`：⚠️ 不可依赖
- 大数失精：`|lr_val| > 2^53 ≈ 9e15` 时精度衰减

**配合 `MODTURNS`**：`MODTURNS(v, m) * m + MODABS(v, m) ≡ v`（在 LREAL 精度范围内）。`MODTURNS` 给"圈数"，`MODABS` 给"圈内位置"。

## 4. 错误码 / 返回值

本函数返回类型为 `LREAL`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

特殊输入：

- `lr_mod = 0`：除零，PDF 未明说，⚠️ 必须由调用方先保证模数非零
- `lr_val = NaN` / `±Inf`：⚠️ 不可依赖
- 大数：`|lr_val| > 2^53` 时精度衰减

## 5. 使用注意 / 常见坑

- **与 `LMOD` 在负被除数上结果不同**：`MODABS(-1, 360) = 359`，`LMOD(-1, 360) = -1`。NC 轴 / 旋转编码器场景几乎必用 `MODABS`；信号相位 / 控制理论场景一般用 `LMOD`。**选错函数导致 HMI 角度跳变** 是最常见的事故。
- **模数为 0 必须先检查**：和 `LMOD` 同样的除零问题。
- **正向 + 反向累计也是无符号**：往复运动时 `MODABS(累计位置, 360)` 永远 `[0, 360)`。判断"在 0° 附近"需 `MODABS(x, 360) < 1 OR MODABS(x, 360) > 359`（角度环绕）。
- **PDF / InfoSys 写"unsigned modulo value within the modulo range"**：注意 *unsigned* 这个词，明示了与 `LMOD` 的差异。
- **不要预先 `ABS(v)` 再 `LMOD`**：那样 `LMOD(ABS(-90), 360) = 90`，但 `MODABS(-90, 360) = 270`——结果不同，前者丢失"反向跑了多少"信息。（工程经验补充）
- **精度衰减**：长时间累计位置（如`v` 累加到 `1e10`）在浮点除法 `v / m` 时低位精度损失，最终模值会与数学预期偏几个 `ULP`。配合 `MODTURNS` 周期性把累计量"卸下来"可改善。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MODABS.xml`](../examples/P_Demo_MODABS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：转盘式装配工位（rotary indexing table），驱动用单方向累计计数的伺服轴。
//       本程序读伺服累计位置 lrAxisAbsPositionDeg（可以跑了几圈），用 MODABS
//       归一到 [0, 360) 给 HMI 显示"现在面朝哪个工位"。共 4 工位（每 90°）。
//
// 价值：MODABS 一行处理"多圈累计 + 反向 + 零点"；用 LMOD 反向时会显示负角度
//       误导操作员，是工程中典型陷阱。
//
// 验证：在线写 lrAxisAbsPositionDeg = 400.56 → lrPositionInOneTurnDeg = 40.56；
//       写 -400.56 → 319.44（验证负数翻正）；
//       写 90 → 90（第二工位）；写 -1 → 359（边界翻正）；
//       写 720 → 0（整模值归零）。
PROGRAM P_Demo_MODABS
VAR
    lrAxisAbsPositionDeg     : LREAL := 400.56;  // 在线写值模拟伺服位置
    lrTurnSizeDeg            : LREAL := 360.0;   // 一圈大小
    lrPositionInOneTurnDeg   : LREAL;            // MODABS 输出：[0, 360)
    nCurrentStationIndex     : DINT;             // 当前工位号（0..3，每 90°）
END_VAR

// 单行调用：MODABS 把累计角度归一为 [0, 360) 的物理位置
// 与 LMOD 关键区别：负被除数也给正余数
lrPositionInOneTurnDeg := MODABS(lrAxisAbsPositionDeg, lrTurnSizeDeg);

// 工位号 = FLOOR(归一角度 / 90)；4 工位每 90°
// （FLOOR 而非 LTRUNC：业务上 89.999° 算 1 号工位即可）
nCurrentStationIndex := LREAL_TO_DINT(FLOOR(lrPositionInOneTurnDeg / 90.0));
```

## 7. 业务场景与实际价值

- **场景**：NC 伺服模值位置归一化、转盘工位判定、定向天线方位角显示、罗盘 / 陀螺仪角度规整。PDF 明确点名"NC 轴模值"作为标准用例。
- **价值**：把"累计角度"翻译为"圈内物理位置"一行解决；避免负数 / 多圈两个陷阱；配合 `MODTURNS` 可同时提供"已转圈数"用于回零、累计计数等。
- **替代方案对比**：
  - 用 `LMOD` 再 `IF result < 0 THEN result += m`：能等价但 2-3 行替代 1 行，易漏
  - 自己写 `v - FLOOR(v/m) * m`：3 次浮点运算，等价但冗余
  - **本函数**：单调用、`LREAL` 入 `LREAL` 出、PDF 明确为 NC 轴推荐

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68447883.html
- **相关函数**：`LMOD`（带符号的浮点取余）、`MODTURNS`（模运算的整数商部分）、`FLOOR` / `LTRUNC`（取整辅助）
