# LTRUNC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68446347.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LTRUNC.TcPOU`](../examples/P_Demo_LTRUNC.TcPOU) |

---

## 1. 功能简述

朝零截断的整数部分函数。给一个 `LREAL` 浮点数 `lr_in`，丢掉它的小数部分，返回**整数部分**（数值上朝 `0` 方向取整），结果仍是 `LREAL`，不受 `INT` / `DINT` 数值范围限制。

数学定义：`LTRUNC(x) = SIGN(x) * ⌊|x|⌋`。正数侧 `LTRUNC(2.8) = 2`，负数侧 `LTRUNC(-2.8) = -2`（绝对值变小）——与 IEC 标准 `TRUNC` 的取整方向一致，差异**只在返回类型**：`TRUNC` 返 `DINT`、`LTRUNC` 返 `LREAL`。

这正是它存在的理由：当输入是远超 `±2³¹` 的大浮点数时，`TRUNC` 会因 `DINT` 范围溢出给错误结果，`LTRUNC` 能正确返回浮点表示的整数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LTRUNC : LREAL
VAR_INPUT
    lr_in : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_in` | `LREAL` | 待截断的 64 位双精度浮点输入值 |

### 返回值

| 类型 | 说明 |
|---|---|
| `LREAL` | `lr_in` 的整数部分（朝零方向），以 `LREAL` 表示。例：`LTRUNC(2.8) = 2.0`，`LTRUNC(-2.8) = -2.0`，`LTRUNC(0.0) = 0.0` |

### VAR_OUTPUT

无（本符号是 `FUNCTION`）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：本函数朝 `0` 方向取整，即"丢掉小数部分"。PDF §3.5 原表（搬运）：

| `x` | `0` | `0.4` | `0.5` | `0.6` | `1.4` | `1.5` | `1.6` | `-0.4` | `-0.5` | `-1.4` | `-1.5` | `-1.78` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `LTRUNC(x)` | `0` | `0` | `0` | `0` | `1` | `1` | `1` | `0` | `0` | `-1` | `-1` | `-1` |

**与三个兄弟函数的关系**：

- **正数侧**：`LTRUNC(x) = FLOOR(x)`（都朝 `-∞ = 0` 方向）
- **负数侧**：`LTRUNC(x) = CEIL(x)`（都朝 `+∞ = 0` 方向）
- **与 `TO_LINT`**：`TO_LINT` 是四舍五入（`0.5` 进位），`LTRUNC` 是直接丢小数

数学上 `LTRUNC(x) = SIGN(x) * FLOOR(ABS(x))`。

**与 IEC `TRUNC` 的关键区别**：

| 输入 | `TRUNC(x)`（IEC 标准） | `LTRUNC(x)` |
|---|---|---|
| `2.8` | `2`（`DINT`） | `2.0`（`LREAL`） |
| `1.0e10` | **溢出** → `DINT` 截断错误 | `1.0e10`（正确） |
| `-1.0e10` | **溢出** | `-1.0e10`（正确） |
| `2^53 = 9.0e15` | 溢出 | `9.0e15` |
| `1.0e18`（超 `LREAL` 精度间距） | 溢出 | 与原值相同（已无小数信息） |

**小数位截取技巧**（PDF §3.5 提供）：保留 `k` 位小数朝零截断写 `LTRUNC(x * POWER(10, k)) / POWER(10, k)`。同样存在浮点表示误差。

**典型工程应用**：把 `LREAL` 累计计件数转 MES 整数主键；把伺服位置（`LREAL` 毫米）转整毫米（朝零截，避免负数侧"多 1 毫米"误差）；构造 BCD 编码（截分位）。

## 4. 错误码 / 返回值

本函数返回类型为 `LREAL`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

PDF / InfoSys 均未规定 `NaN` / `±Inf` 的行为，需调用方保证输入合法。

## 5. 使用注意 / 常见坑

- **与 IEC `TRUNC` 行为相同但返回类型不同**：从 TwinCAT 2 / 旧代码迁移时若变量声明用了 `: DINT` 接 `TRUNC`，迁移到 `LTRUNC` 后要把目标变量改 `LREAL` 或再调 `LREAL_TO_DINT`。
- **不要当 `FLOOR` 用**：负数侧 `LTRUNC(-2.8) = -2`，但 `FLOOR(-2.8) = -3`。把 `LTRUNC` 用在 `FLOOR` 该用的"整数倍量化"场景上会少量化一格。
- **负数侧不会变更负**：与 `FLOOR` 不同，`LTRUNC` 在负数侧朝零靠近，对"绝对值上对齐到整数"业务（如累计磨损量按整毫米四舍）更合适。
- **大数失精**：`|lr_in| > 2^53 ≈ 9.0e15` 时浮点间距 ≥ 1，`LTRUNC(x) = x`。这是正常的，不是 bug。
- **小数位截取的浮点误差**：`LTRUNC(0.3 * 10) / 10` 不保证精确等于 `0.3`，可能 `0.29999...`。货币 / 显示场景需用 `LREAL_TO_FMTSTR` 控制小数位。（工程经验补充）
- **四舍五入不要用 `LTRUNC(x + 0.5 * SIGN(x))`**：在 `0.5` 边界由于浮点二进制表示问题可能误差一格。正确的四舍五入用 `LREAL_TO_LINT` 或 IEC `TO_LINT`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTRUNC.TcPOU`](../examples/P_Demo_LTRUNC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：伺服轴位置（LREAL 毫米，含小数）需要转给 PROFINET 总线上一个老 PLC，
//       对端只接受 LREAL 但要求"对齐到整毫米"（不能要分米/微米的零头）。
//       由于位置可能为负（撤回到原点以外），需要使用"朝零截断"语义——
//       避免 FLOOR 在负数侧把 -1.3 截成 -2 让对端误以为"撤回更深"。
//
// 价值：LTRUNC 一行做朝零截断；返回 LREAL 直接对接总线，无需中间 DINT 转换。
//       与 IEC TRUNC 相比能处理位置量极大或量极小的边角情况而不溢出。
//
// 验证：在线写 lrServoPositionMm = 12.7 → lrPositionTruncMm = 12.0；
//       写 -12.7 → -12.0（验证朝零截，不像 FLOOR 给 -13）；
//       写 12.0 → 12.0（整数值不变）；
//       写 1.0e10 → 1.0e10（大数 LREAL 仍保留，IEC TRUNC 会溢出）。
PROGRAM P_Demo_LTRUNC
VAR
    lrServoPositionMm    : LREAL := 12.7;   // 在线写值模拟伺服位置
    lrPositionTruncMm    : LREAL;            // LTRUNC 输出：朝零截断的整毫米
    lrSubMillimeterPart  : LREAL;            // FRAC 输出：丢掉的零头（保留诊断）
END_VAR

// 单行调用：LTRUNC 朝零截断；返回 LREAL 直接送总线
lrPositionTruncMm := LTRUNC(lrServoPositionMm);

// 互补的小数零头（业务用不到也可不算；放这里演示两者互补关系）
// FRAC(x) + LTRUNC(x) ≡ x （在 LREAL 精度内）
lrSubMillimeterPart := FRAC(lrServoPositionMm);
```

## 7. 业务场景与实际价值

- **场景**：位置 / 量值的朝零截断（与 `FLOOR` 在负数侧行为不同的场合）、`LREAL` → `LINT` 大数量级转换前的整数化、`LREAL_TO_DINT` 防止溢出的"先截断再转"前置处理。
- **价值**：替代 IEC `TRUNC` 在大数场景下的溢出风险；与 `FRAC` 配合一行拆分整数 / 小数部分；负数侧"朝零"语义在某些业务（金额抵扣、撤回量）下比 `FLOOR` 更直观。
- **替代方案对比**：
  - IEC `TRUNC`：返回 `DINT`，超过 `±2.1e9` 溢出
  - `FLOOR`：负数侧朝 `-∞`，业务语义不同
  - `LREAL_TO_LINT`：四舍五入而不是截断
  - 自己写 `IF x >= 0 THEN FLOOR(x) ELSE CEIL(x) END_IF`：能等价但 3 行替代 1 行
  - **本函数**：单调用、`LREAL` 入 `LREAL` 出、`TRUNC` 大数升级版

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68446347.html
- **相关函数**：`FLOOR`（向下取整）、`CEIL`（向上取整）、`FRAC`（取小数部分，与本函数互补）、IEC `TRUNC` / `TO_LINT`
