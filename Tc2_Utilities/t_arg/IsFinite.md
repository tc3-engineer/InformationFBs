# IsFinite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35142155.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_IsFinite.xml`](../examples/P_Demo_IsFinite.xml) |

---

## 1. 功能简述

`IsFinite` 检查一个浮点变量（被先用 `F_LREAL` / `F_REAL` 打包成 `T_Arg`）是否是**有限实数**：返回 `TRUE` 表示值落在 (−∞, +∞) 区间内；返回 `FALSE` 表示值是 `±INF` 或 `NaN`（Not a Number）。

为什么需要：浮点数学运算可能产生 `INF`（除零、溢出）或 `NaN`（0/0、INF−INF、对负数开方、非法内存覆盖后的位模式）。**`Tc2_Standard` 的浮点转换函数（`REAL_TO_DINT` 等）在收到 `INF` / `NaN` 时会触发 FPU 异常**，PC 平台（x86/x64）的 PLC 运行时会因此**停机**。`IsFinite` 在做转换之前先体检一下，落在区间外就走故障分支，避免 PLC 整机停机。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION IsFinite : BOOL
VAR_INPUT
    x : T_Arg;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `x` | `T_Arg` | — | 待检查的浮点变量描述符。调用方先用 `F_LREAL(myReal)` 或 `F_REAL(mySingle)` 打包，再把返回的 `T_Arg` 作为本函数参数 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 返回值

`BOOL` —— `TRUE` = `x` 是有限实数（−INF < x < +INF）；`FALSE` = `x` 是 `±INF` 或 `NaN`。

## 3. 行为说明

**触发**：每次调用即同步求值，无副作用，单 PLC 周期内完成。

**算法**：函数读 `x.pData^` 按 `x.cbLen`（4 字节 REAL / 8 字节 LREAL）解读，检查 IEEE-754 位模式中的 **exponent 段是否全为 1**：

```
对 LREAL (64-bit IEEE-754)：
  signBit  : 1 bit
  exponent : 11 bits
  mantissa : 52 bits
  IF exponent = 2047 (all-1) THEN
      IF mantissa = 0 THEN  /* ±INF */ RETURN FALSE
      ELSE                  /* NaN  */ RETURN FALSE
      END
  END
  RETURN TRUE

对 REAL (32-bit IEEE-754)：
  exponent 8 位全 1 ⇒ ±INF (mantissa = 0) 或 NaN (mantissa ≠ 0) ⇒ RETURN FALSE
```

**何时会出现 INF**：在运行时数学运算结果超过 LREAL/REAL 表示范围（如 `fSingle := fSingle * 2;` 持续翻倍）。

**何时会出现 NaN**：通常是**非法的位模式覆盖**——例如 `MEMSET(ADR(fSingle), 16#FF, SIZEOF(fSingle));`，或者从 wire 读到的字节按 REAL 解读但其实是其他类型的数据。

**保护用法**：在调用 `REAL_TO_DINT / LREAL_TO_INT` 之类的转换函数**之前**先 `IsFinite(F_LREAL(fX))` 校验：

```
IF IsFinite(F_LREAL(fSensorValue)) THEN
    nSensorRaw := LREAL_TO_DINT(fSensorValue);
ELSE
    /* 走故障分支：标记 sensor 失效、保持上一次值、报警 */
    bSensorFaultLatched := TRUE;
END_IF;
```

不做这个保护，一个 NaN 就能整机停机。

## 4. 错误码 / 返回值

无独立错误码。返回 `TRUE` / `FALSE`。

## 5. 使用注意 / 常见坑

- **只对 REAL / LREAL 有意义**。`x.eType` 必须是 `F_REAL` / `F_LREAL` 打包过的。如果传 `F_INT`/`F_DWORD` 的 `T_Arg`，函数对整数位模式按 IEEE-754 错误解读，结果无意义。
- **检查在转换前做**。`IF IsFinite(F_LREAL(fX)) THEN ... END_IF;` 顺序不能反——一旦先 `REAL_TO_INT(fX)` 再检查，PLC 已经在转换那一步停机了。
- **不要在 ISR / 中断里调用**。本函数内部要 deref `pData`，在不规范的内存语境下可能跨段访问。正常 PLC 任务里安全。
- **`x.pData = 0` 行为未规定**。PDF 没有说 NULL 时返回什么。**调用前先 `F_<TYPE>` 打包**保证非空。
- **不能区分 NaN 和 INF**：本函数把它们都判 FALSE。如果业务需要区分（例如 NaN 报警严重度更高），需要另读 `pData^` 的位模式手动判 mantissa。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IsFinite.xml`](../examples/P_Demo_IsFinite.xml)

```iecst
// 场景：温度传感器接入，PLC 把模拟量原始值算成 LREAL；偶发 sensor 短路或
//       wire 串扰会导致计算结果变成 INF / NaN，紧接着的 LREAL_TO_INT 会让
//       PLC 停机。在 conversion 前先 IsFinite 体检。
// 价值：替代手写 IF fX > 1E308 OR fX < -1E308 OR fX <> fX THEN（NaN 的
//       自不等于技巧），一次调用搞定 INF 和 NaN 两类异常。
// 验证：在线写 fSensorRaw := 1.0 ；bCheckSensor := TRUE；bSensorIsFinite 应为 TRUE。
//       再 MEMSET(ADR(fSensorRaw), 16#FF, SIZEOF(fSensorRaw))（用 Watch 强写位模式）；
//       下一次 bSensorIsFinite 应变 FALSE，bSensorFault 锁定。
PROGRAM P_Demo_IsFinite
VAR
    fSensorRaw         : LREAL := 25.0;     // 模拟传感器原始值
    argSensor          : T_Arg;              // 打包后的描述符
    bSensorIsFinite    : BOOL;               // IsFinite 返回
    bSensorFault       : BOOL;               // 锁存：曾经出现过非有限值
    nSensorScaledOut   : DINT;               // 转换后的工程值，安全场合才赋值
    bCheckSensor       : BOOL;
END_VAR

argSensor := F_LREAL(fSensorRaw);

IF bCheckSensor THEN
    bSensorIsFinite := IsFinite(x := argSensor);
    IF bSensorIsFinite THEN
        // 安全：现在 conversion 不会触发 FPU 异常
        nSensorScaledOut := LREAL_TO_DINT(fSensorRaw * 100.0);
    ELSE
        // 故障：跳过 conversion，保护 PLC 不停机
        bSensorFault := TRUE;
    END_IF;
    bCheckSensor := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：温度 / 压力 / 流量等模拟量在线性化后做 `LREAL_TO_DINT` 转换前的保护；浮点累加 / 除法 / 反三角函数结果前的体检；wire 协议解出浮点字段后的合法性检验。
- **价值**：一行调用就能挡住整机停机风险，比手写位模式判断 / NaN 不等于自身的小技巧更直观、跨平台一致。
- **替代方案对比**：手写 `fX <> fX`（NaN 自不等于）+ `ABS(fX) > 1E308`（粗判 INF）：能用，但容易因为编译器优化把"自不等于"消掉，且 INF 的边界数本身合法的极端值会误判。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.10.27
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35142155.html
- **相关 FC**：`F_LREAL` / `F_REAL`（打包浮点值）、`Tc2_Standard` 浮点转换函数（被保护的对象）
