# FB_BA_Swi2P

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / Hysteresis 2-Point-Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13551527307.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_Swi2P.TcPOU`](../examples/P_Demo_FB_BA_Swi2P.TcPOU) |

---

## 1. 功能简述

二点切换控制器（two-point switch）。比较输入信号 `fIn` 与"开通点 `fOn`" / "关断点 `fOff`"，按比较结果生成布尔输出 `bQ`。控制方向由 `fOn` / `fOff` 的相对位置自动判定：`fOn > fOff` ⇒ direct/synchronous（制冷模式：`fIn` 上升越 `fOn` 开通、下降越 `fOff` 关断）；`fOn < fOff` ⇒ reverse（加热模式：`fIn` 下降越 `fOn` 开通、上升越 `fOff` 关断）。带开通延时 `nDlyOn` `[s]` 与关断延时 `nDlyOff` `[s]`，防止抖动。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEn            : BOOL;
    fIn            : REAL;
    fOn            : REAL;
    fOff           : REAL;
    {attribute 'parameterUnit':= 's'}
    nDlyOn         : UDINT;
    {attribute 'parameterUnit':= 's'}
    nDlyOff        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEn` | `BOOL` | 总使能。`FALSE` 时 `bQ := FALSE`，内部延时倒计时清零。 |
| `fIn` | `REAL` | 输入值（被监视信号，如温度 / 压力）。 |
| `fOn` | `REAL` | 开通点：`fIn` 穿越此值时（按控制方向）开始 `nDlyOn` 倒计时；倒计时完成后 `bQ := TRUE`。 |
| `fOff` | `REAL` | 关断点：`fIn` 穿越此值时开始 `nDlyOff` 倒计时；倒计时完成后 `bQ := FALSE`。 |
| `nDlyOn` | `UDINT` | 开通延时 `[s]`（带 `{attribute 'parameterUnit':= 's'}` 属性）。 |
| `nDlyOff` | `UDINT` | 关断延时 `[s]`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bQ             : BOOL;
    {attribute 'parameterUnit':= 's'}
    nRemTiDlyOn    : UDINT;
    {attribute 'parameterUnit':= 's'}
    nRemTiDlyOff   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bQ` | `BOOL` | 切换输出。控制方向由 `fOn` / `fOff` 大小关系决定。 |
| `nRemTiDlyOn` | `UDINT` | 开通延时剩余时间 `[s]`，倒计时中可观察。 |
| `nRemTiDlyOff` | `UDINT` | 关断延时剩余时间 `[s]`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

控制方向自动判定：`fOn > fOff` ⇒ direct（制冷模式，dehumidify 模式）：`fIn ≥ fOn` 开始开通延时，`fIn ≤ fOff` 开始关断延时。物理含义："温度高了开冷"。`fOn < fOff` ⇒ reverse（加热模式）：`fIn ≤ fOn` 开始开通延时，`fIn ≥ fOff` 开始关断延时。物理含义："温度低了开热"。`fOn = fOff` 没有滞回（hysteresis 为 0），变成单点切换——不推荐，会震荡。延时机制：从 `fIn` 穿越阈值的瞬间开始累计延时，倒计时显示在 `nRemTiDlyOn` / `nRemTiDlyOff`。倒计时完成 `bQ` 翻转；若倒计时未完时 `fIn` 又退回原区域，倒计时清零（重新计算）。这保证短暂的传感器尖刺不会引起 `bQ` 抖动。`bEn = FALSE` 时 `bQ` 强制 FALSE，所有延时清零；下次 `bEn = TRUE` 时 `bQ` 从 FALSE 开始判定。

## 4. 错误码 / 返回值

本 FB 无错误码、无返回值。

| 现象 | 含义 | 处理建议 |
|---|---|---|
| `bQ` 一直 FALSE | `bEn = FALSE` 或 `fIn` 未到 `fOn` | 检查使能、检查阈值 |
| `bQ` 频繁切换（抖动） | `fOn = fOff`（无滞回）或延时为 0 | 加滞回 `\|fOn − fOff\| ≥ 传感器噪声峰值`；加延时 `nDlyOn / nDlyOff ≥ 5 s` |
| 控制方向反了 | `fOn` / `fOff` 大小判反 | 改回正确大小关系 |

PDF / InfoSys 未列错误码。

## 5. 使用注意 / 常见坑

- **`\|fOn − fOff\|` 是滞回宽度**：必须 ≥ 传感器噪声幅度的 2-3 倍，否则会因噪声反复切换。室温场景典型 1-2℃。（工程经验补充）
- **`fOn` / `fOff` 大小关系决定控制方向**——这是隐式约定，组态时要明确写注释。如想加热：`fOn = 18 ℃`、`fOff = 20 ℃`（fOn < fOff = 加热）；如想制冷：`fOn = 26 ℃`、`fOff = 24 ℃`（fOn > fOff = 制冷）。（工程经验补充）
- **延时单位是秒**，整数；最小 1 秒。`nDlyOn = 0` ⇒ 无延时直接切换，配合阈值滞回也能基本工作。
- **`nRemTiDlyOn` / `nRemTiDlyOff` 都是单调倒数**，等于 0 时延时完成、`bQ` 翻转。HMI 上常用作"还有 N 秒切换"显示。（工程经验补充）
- **不要在控制环里把本 FB 与 `FB_BA_PIDCtrl` 并联使用**——两个完全不同的控制类型，会互相打架。要 PID 用 PID、要 2 点用 2 点。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_Swi2P.TcPOU`](../examples/P_Demo_FB_BA_Swi2P.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：地下室除湿机：湿度高于 65% RH 开启除湿（延时 30 s 防瞬态尖刺），降到 55% RH 关闭（延时 60 s 避免短循环）。控制方向 = direct（`fOn=65 > fOff=55` 即制冷/除湿）。
- **价值**：相比手写 IF + 两个延时定时器（约 15 行），本 FB 一行调用涵盖滞回、双方向延时、剩余时间显示。
- **替代方案对比**：
  - **手写 IF + TON**：可行但代码繁琐、易写漏方向自动判定；
  - **`R_TRIG` + 设定逻辑**：只能做单点切换，无滞回；
  - **本 FB**：BA 标准、与 `FB_BA_SwiHys2P`（带滞回偏移的高级版）形成系列。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13551527307.html
- **相关 FB**：`FB_BA_SwiHys2P`（带可调滞回宽度 + 偏移的 2 点切换）、`FB_BA_PIDCtrl`（连续 PID 控制器）
