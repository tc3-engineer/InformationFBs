# FLOATIsNaN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `[Obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/943967755.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_FLOATIsNaN.xml`](../examples/P_Demo_FLOATIsNaN.xml) |

---

## 1. 功能简述

⚠️ **本函数已弃用**。PDF 与 InfoSys 都明确标注 "Obsolete function — use the `LrealIsNaN()` function instead"。**新代码请用 `LrealIsNaN`**。

`FLOATIsNaN` 判断一个 `LREAL` 是否为 NaN（Not-a-Number）——IEEE 754 浮点的特殊值，用来表示"非法运算结果"（如 `0/0`、`SQRT(-1.0)`、`LOG(-1.0)`）。返回 `BOOL`：是 NaN 则 `TRUE`，否则 `FALSE`。

被弃用的原因与 `FLOATIsFinite` 一致：`FLOAT` 命名属 TC2 时代旧风格；新函数 `LrealIsNaN` 用 `REFERENCE TO LREAL` 替代值传递，对 64 位浮点能省一次拷贝。

注意 `FLOATIsNaN` 与 `FLOATIsFinite` 的判定范围**不互补**：`+Inf` / `-Inf` 不是 NaN 但也不是有限数。所以"是否能信任这个数"的完整判定应当是 `FLOATIsFinite(x)`，而不是 `NOT FLOATIsNaN(x)`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FLOATIsNaN : BOOL
VAR_INPUT
    x : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `x` | `LREAL` | 待判定的 64 位浮点值。值传递（拷贝 8 字节进栈） |

### 返回值

`BOOL`：
- `TRUE`：`x` 是 NaN（quiet NaN 或 signaling NaN，本函数不区分）
- `FALSE`：`x` 是普通数 / 0 / 次正规数 / `+Inf` / `-Inf`

### VAR_IN_OUT

无。

## 3. 行为说明

函数执行 IEC 754 双精度浮点的"是不是 NaN"位运算判定——按 IEEE 754 规范，64 位浮点的指数全为 1（`0x7FF`）且尾数非全 0 时表示 NaN（尾数全 0 则表示 Inf）。函数返回 `TRUE` 当且仅当 `x` 命中 NaN 模式。

判定示例：
- 普通数（如 `3.14`、`0.0`、次正规数）→ `FALSE`
- `+Inf` / `-Inf`（除以 0 的溢出结果）→ `FALSE`（**Inf 不是 NaN**！）
- `0.0 / 0.0` / `LOG(-1.0)` / `SQRT(-1.0)` 等非法运算 → `TRUE`
- 任何运算中只要有一个操作数是 NaN，结果也是 NaN（NaN "传染"）

调用是纯函数式的——无副作用、无内部状态、无 ADS 通讯。单 PLC 周期内立即返回。

**与 `FLOATIsFinite` 配合用**：
- `FLOATIsFinite(x) = TRUE` 等价于 "`x` 既不是 NaN 也不是 Inf"——这是"值可信"的标准判定
- `FLOATIsNaN(x) = TRUE` 只覆盖 NaN，不覆盖 Inf
- 仅要拦 NaN 不在乎 Inf 时用本函数；要把 NaN 和 Inf 都拦掉用 `FLOATIsFinite`

## 4. 错误码 / 返回值

返回纯 `BOOL`：

| 返回 | 含义 |
|---|---|
| `TRUE` | `x` 是 NaN |
| `FALSE` | `x` 不是 NaN（普通数 / 0 / 次正规数 / `±Inf`） |

无错误码、无异常路径。

## 5. 使用注意 / 常见坑

- **本函数已弃用**：新代码请用 `LrealIsNaN(x)`——功能等价、引用传递省一次拷贝。本文档保留为旧代码兼容。
- **NaN ≠ Inf**：本函数对 `+Inf` / `-Inf` 都返回 `FALSE`。要把两者都拦掉用 `FLOATIsFinite`（或新名 `LrealIsFinite`）。
- **NaN 与任何值的比较都是 `FALSE`**——`x = NaN`、`x < NaN`、`x > NaN` 全都是 `FALSE`，**包括 `NaN = NaN`**！所以**不能**用 `x = x` 来判 NaN？严格说 `x <> x` 在 IEEE 754 等价于 `IsNaN(x)`，但 IEC 编译器对 `LREAL` 等式比较的优化策略不固定，**保守做法**：用本函数判定，不要靠等式技巧。
- 不要把 `NaN` 当"无效"标志位用——业务侧应用专门的 `BOOL bValid` 标志，浮点变量不要做双用途。
- 浮点 `0.0 / 0.0` 在 TwinCAT 上产生 NaN；整数 `0 / 0` 会引发运行时异常（不是 NaN）——两者机制不同。
- 移植到 TC3 现代代码时机械替换为 `LrealIsNaN`：参数名 / 返回类型相同，无需改其他代码。
- 检测到 NaN 后业务侧通常进入 fail-safe 分支并报警——不要悄悄把 NaN 替换为 0 继续算，会掩盖故障。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FLOATIsNaN.xml`](../examples/P_Demo_FLOATIsNaN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：流量计算公式 rFlow := SQRT(rDeltaP / rRho)，若现场压力差信号在低
//       温下偶尔为负（传感器零漂）会让 SQRT 输出 NaN，污染下游累积流量。
//       专门检测 NaN 比一并拦 Inf 更精细——本工程允许 Inf（极端工况确实
//       可能高压差）但不允许 NaN（数学非法）。
//
// 价值：用 FLOATIsNaN 而不是 FLOATIsFinite 让"Inf 表示极端高流量"这种业务
//       语义保留下来，只把真正非法的 NaN 拦掉。
//
// 验证：登录后改 rDifferentialPressure := -1.0 → bFlowIsNaN 应翻 TRUE
//       （SQRT(-1) = NaN）；改回 4.0 → bFlowIsNaN 翻 FALSE，rFlowValue 为 2.0。
// 注：新代码请改用 LrealIsNaN；本例仅为旧工程兼容演示。
PROGRAM P_Demo_FLOATIsNaN
VAR
    rDifferentialPressure : LREAL := 4.0;          // 在线改 -1.0 模拟传感器零漂
    rFlowValue            : LREAL;
    bFlowIsNaN            : BOOL;
END_VAR

// SQRT 接到负数会产 NaN（IEEE 754 标准）
rFlowValue := SQRT(rDifferentialPressure);

// 检测 NaN（已弃用，新代码用 LrealIsNaN）
bFlowIsNaN := FLOATIsNaN(rFlowValue);
// 真实工程：IF bFlowIsNaN THEN 报警 + fail-safe END_IF
```

## 7. 业务场景与实际价值

- **场景**：浮点运算链路中只对 NaN 敏感、对 Inf 允许通过的场合——例如流量 / 速度 / 压力计算中"极端高值"是有意义的诊断信号，不应被 fail-safe 误拦。
- **价值**：精确拦掉非法的 NaN，保留 `Inf` 的诊断价值（不一刀切）。这是与 `FLOATIsFinite` 的关键差别。
- **替代方案**：优先用 `LrealIsNaN`（同功能、现代接口）。本函数仅为旧工程兼容。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.11.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/943967755.html
- **替代函数**：`LrealIsNaN`（Tc2_Utilities 现代接口；同功能；参数 `REFERENCE TO LREAL`）
- **相关函数**：`LrealIsFinite`（判 NaN + Inf）、`FLOATIsFinite`（同样已弃用的旧名）
