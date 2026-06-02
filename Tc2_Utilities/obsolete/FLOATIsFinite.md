# FLOATIsFinite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `[Obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/943965835.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_FLOATIsFinite.TcPOU`](../examples/P_Demo_FLOATIsFinite.TcPOU) |

---

## 1. 功能简述

⚠️ **本函数已弃用**。PDF 与 InfoSys 都明确标注 "Obsolete function — use the `LrealIsFinite()` function instead"。**新代码不要用本函数**，请用 `LrealIsFinite`。

`FLOATIsFinite` 是 Tc2_Utilities 提供的一个 IEC 754 浮点判定函数：给定一个 `LREAL`，判断它是否是"**有限数（finite number）**"——也就是既不是无穷大（`±Inf`）也不是 NaN（Not-a-Number）。返回 `BOOL`：有限则 `TRUE`，否则 `FALSE`。

为什么被废弃：函数名 `FLOAT` 是 TwinCAT 2 时代的命名（当时 `FLOAT` 指代单精度浮点）；TwinCAT 3 时代统一用 IEC 标准类型名 `REAL` / `LREAL`。同时新函数 `LrealIsFinite` 用 `REFERENCE TO LREAL` 替代值传递，对 64 位 `LREAL` 而言**省一次拷贝**，性能更好。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FLOATIsFinite : BOOL
VAR_INPUT
    x : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `x` | `LREAL` | 待判定的 64 位浮点值。值传递（拷贝 8 字节进栈）。可以是任意 `LREAL` 字面量、变量、表达式结果 |

### 返回值

`BOOL`：
- `TRUE`：`x` 是有限数（普通数 / 0 / 次正规数）
- `FALSE`：`x` 是 `+Inf` / `-Inf` / NaN（任何 quiet NaN 或 signaling NaN）

### VAR_IN_OUT

无。

## 3. 行为说明

函数执行 IEC 754 双精度浮点的"特殊值判定"——按 IEEE 754 规范，64 位浮点的指数全为 1（`0x7FF`）时表示 Inf 或 NaN，其他情况均为有限数。函数返回 `TRUE` 当且仅当 `x` 不是 Inf 也不是 NaN。

判定的三种典型输入：
- 普通数（如 `3.14`、`-100.0`、`1.23E-10`、`0.0`、次正规数）→ `TRUE`
- `+Inf` / `-Inf`（除以 0 的结果、`LREAL#1.0E+400` 等溢出表达式）→ `FALSE`
- NaN（`0.0 / 0.0`、`SQRT(-1.0)` 等非法运算结果）→ `FALSE`

调用是纯函数式的——无副作用、无内部状态、无 ADS 通讯。单 PLC 周期内立即返回。

行为与 IEC 60559 标准的 `isfinite()` 等价，**与新函数 `LrealIsFinite` 的判定结果一一对应**——它们底层用同一 IEEE 754 位运算，差别只在接口签名（值传递 vs 引用传递）。

**典型应用场景**（值得说明的是这个函数本身的逻辑没问题，被弃只是接口风格）：在浮点计算链路中防御 NaN / Inf 污染。例如温度传感器线性化算式里的除法可能因传感器断线产生 `0/0 = NaN`，结果代入 PID 会让控制器输出彻底错乱。先 `IF FLOATIsFinite(rRaw) THEN ... END_IF` 把异常值拦在 PID 之外。

## 4. 错误码 / 返回值

返回纯 `BOOL`：

| 返回 | 含义 |
|---|---|
| `TRUE` | `x` 是有限数（普通数 / 0 / 次正规数） |
| `FALSE` | `x` 是 Inf 或 NaN |

无错误码、无异常路径。**唯一"非正常"情况**：传入未初始化的 `LREAL` 变量——读到的位模式恰好可能是有效有限数（多半为 0），也可能是 Inf / NaN（小概率），结果不可预期。务必先初始化变量。

## 5. 使用注意 / 常见坑

- **本函数已弃用**：新代码请用 `LrealIsFinite(x)`——功能等价、接口现代、性能更好（引用传递省一次 `LREAL` 拷贝）。本文档保留是为旧代码兼容性与可读性，不为推广使用。
- 不要把"`FLOATIsFinite(x) = TRUE`" 理解为"`x` 是合理的工程值"——`1.0E+300` 是有限数，但工程意义上多半是错的。本函数只判 IEEE 754 特殊值，业务合理性要业务侧另做范围检查。
- 不要在大循环里对常量调用本函数：编译器**不保证**把"`FLOATIsFinite(3.14)`"折叠成 `TRUE`，每次循环都会真的进函数。常量已知时直接写 `TRUE` 避免开销。
- 0 是有限数（返回 `TRUE`）——别把"`= 0` 是错误"和"`NaN/Inf` 是错误"混淆。
- `LREAL#0.0 / LREAL#0.0` 产生 NaN；`LREAL#1.0 / LREAL#0.0` 产生 Inf。两者本函数都返回 `FALSE`，但成因不同——调试时分别处理。
- 函数对 `signaling NaN` 与 `quiet NaN` **不区分**——两者都返回 `FALSE`。
- 移植到 TC3 现代代码时机械替换为 `LrealIsFinite`：参数名相同（`x`），返回类型相同（`BOOL`），调用语法 `LrealIsFinite(rX)`，无需改其他代码。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FLOATIsFinite.TcPOU`](../examples/P_Demo_FLOATIsFinite.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：温度变送器线性化算式里有除法 rTempC := rRawVolt / rGain；现场遇到
//       传感器掉线或 rGain 配置为 0 时会算出 NaN 或 Inf，污染 PID 输出。先
//       用 FLOATIsFinite 拦截再喂 PID，故障定位也更明确。
//
// 价值：不做有限数判定时 NaN 一旦进入 PID，比例 / 积分 / 微分都被搞坏，控
//       制器输出可能瞬间跳到饱和。一行 FLOATIsFinite 判定就把异常值拦在
//       PID 之外，进入 fail-safe 分支。
//
// 验证：登录后在线写 rTempSensorRawVolt := 2.5，rTempSensorGain := 0.0
//       → 在线观察 bSensorValueOk 应翻 FALSE（rTempSensorValueC 为 Inf）；
//       改 rTempSensorGain := 0.25 → bSensorValueOk 翻 TRUE。
// 注：新代码请改用 LrealIsFinite，本例仅为兼容旧工程演示用。
PROGRAM P_Demo_FLOATIsFinite
VAR
    rTempSensorRawVolt   : LREAL := 2.5;
    rTempSensorGain      : LREAL := 0.25;     // 在线改成 0.0 模拟掉线
    rTempSensorValueC    : LREAL;
    bSensorValueOk       : BOOL;
END_VAR

// 业务计算可能产 NaN / Inf
rTempSensorValueC := rTempSensorRawVolt / rTempSensorGain;

// 拦截异常值（已弃用函数；新代码用 LrealIsFinite）
bSensorValueOk := FLOATIsFinite(rTempSensorValueC);
// 真实工程：IF NOT bSensorValueOk THEN 进 fail-safe 分支 END_IF
```

## 7. 业务场景与实际价值

- **场景**：所有涉及"用户输入或现场传感器参数参与浮点除法 / 开方 / 对数"的算式都需要这种判定——温度线性化、流量计算、PID 反馈链路。
- **价值**：把"NaN / Inf 污染数值链路"这种隐蔽 bug 在源头拦掉，避免控制器输出突变到饱和导致硬件冲击。
- **替代方案**：**优先用 `LrealIsFinite`**（同功能、现代接口）。本函数仅在维护 TC2 时代旧工程时保留——不要在新代码里写本函数名，IDE / linter 应当对其报弃用警告。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.11.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/943965835.html
- **替代函数**：`LrealIsFinite`（Tc2_Utilities 现代接口；同功能；参数 `REFERENCE TO LREAL`）
- **相关函数**：`LrealIsNaN`（判 NaN）、`FLOATIsNaN`（同样已弃用的旧名）
