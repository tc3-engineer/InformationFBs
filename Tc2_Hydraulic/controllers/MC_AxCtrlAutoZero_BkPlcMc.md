# MC_AxCtrlAutoZero_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Controllers` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599749003.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AxCtrlAutoZero_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxCtrlAutoZero_BkPlcMc.TcPOU) |

---

## 1. 功能简述

液压**零遮盖阀自动零位补偿**功能块。零遮盖阀（zero overlap valve）的阀芯零位与控制零位通常存在制造公差，导致控制器关闭时缸体漂移、或位置控制器有持续跟随误差。本 FB 通过对跟随误差和控制器响应积分得到补偿值写入 `ST_TcHydAxParam.fZeroCompensation`，让阀输出在"零命令"时实际输出一个微小补偿电压消除漂移。**仅适用于零遮盖阀**——其它类型阀（正遮盖、负遮盖）不要用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:         BOOL:=FALSE;
    EnableOnMoving: BOOL:=FALSE;
    OffsetLimit:    LREAL:=0.0;
    Tn:             LREAL:=0.0;
    Threshold:      LREAL:=0.1;
    Filter:         LREAL:=0.1;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | `FALSE` | 控制补偿功能整体激活 |
| `EnableOnMoving` | `BOOL` | `FALSE` | 控制运动期间是否也允许补偿（默认仅静止时补偿） |
| `OffsetLimit` | `LREAL` | `0.0` | `fZeroCompensation` 的绝对值上限，单位 V |
| `Tn` | `LREAL` | `0.0` | 补偿积分时间，单位 s。指"10 V 变化所需时间"。推荐 > 100 s（避免补偿过快不稳定） |
| `Threshold` | `LREAL` | `0.1` | Done 信号判据：补偿误差阈值，单位 V |
| `Filter` | `LREAL` | `0.1` | Done 信号判据：滤波时间常数，单位 s |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:           AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Error:          BOOL;
    ErrorID:        UDINT;
    Active:         BOOL;
    Limiting:       BOOL;
    Done:           BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Error` | `BOOL` | 出错指示 |
| `ErrorID` | `UDINT` | 编码错误号 |
| `Active` | `BOOL` | 当前正在调整 `fZeroCompensation` |
| `Limiting` | `BOOL` | `fZeroCompensation` 已达到 `OffsetLimit`（继续触底说明硬件偏差超出补偿能力） |
| `Done` | `BOOL` | 补偿趋于稳定（误差 < `Threshold` 且滤波时长达 `Filter`） |

## 3. 行为说明

**调用模式**：每周期调用，电平触发。

**调用顺序**：PDF 明确要求"在 `MC_AxRtFinish_BkPlcMc` 之前调用"——本 FB 必须紧靠 Finish 输出阶段。

**启用逻辑**：
1. `Enable = FALSE` 或轴控制器禁用 → 不 Active，Done 计时器复位
2. `Enable = TRUE` 但轴在运动且 `EnableOnMoving = FALSE` → 不补偿，Done 计时器复位
3. `Enable = TRUE` 且（轴静止 或 `EnableOnMoving = TRUE`）→ 执行补偿与计时

**补偿算法**：
- 从跟随误差与控制器响应导出修正值
- 根据 `Tn` 算出每周期可变化的 delta（限制变化速度避免不稳）
- 误差超过容差（用 `LagAmpDx` 内部参数判定）且方向正确时，按 delta 修正 `fZeroCompensation`
- 修正值被 `OffsetLimit` 限幅，触底时 `Limiting := TRUE`

**Done 判据**：补偿误差 < `Threshold` 持续 `Filter` 时间 → `Done := TRUE`

**典型用法**：
- 比例阀调试阶段：手动开 AutoZero 让它自动学出 `fZeroCompensation`，保存到机械参数文件
- 长期运行后的"在线零位漂移补偿"
- 维护后重新校准阀零位

**典型陷阱**：
- 错用在正遮盖阀：PDF 明确警告"may only be used for zero overlap valves"——其它阀型用了会失稳
- `Tn` 太小：补偿过快导致控制环不稳定
- 没保存到参数：调出来的 `fZeroCompensation` 只在 RAM；重启丢失。建议 Done 后调 `MC_AxParamSave_BkPlcMc`
- `OffsetLimit` 太小：好阀的偏差也补不到位
- 运行时不停开启：长期改 `fZeroCompensation` 可能引入系统漂移；通常只在调试 / 维护阶段开

## 4. 错误码 / 返回值

PDF 未在本 FB 章节列具体 `ErrorID` 数值；⚠️ 待人工补充。

## 5. 使用注意 / 常见坑

- **仅零遮盖阀**：明确硬约束。
- **`Tn` 应 > 100 s**：PDF 推荐值，确保不振荡。
- **Done 后建议保存参数**：避免重启丢失。
- **`Limiting = TRUE` 是危险信号**：说明硬件偏差超出补偿能力，可能阀有问题或机械变形。
- **`Threshold` 单位 V**：是控制电压维度，不是位置。
- **PDF 接口图首行写 `MC_AxUtiOffsetLatch_BkPlcMc`**：是 PDF 复制粘贴错误，本 FB 真实名为 `MC_AxCtrlAutoZero_BkPlcMc`（与章节标题一致）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AxCtrlAutoZero_BkPlcMc.TcPOU`](../examples/P_Demo_MC_AxCtrlAutoZero_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：比例阀控制的液压锁模轴，调试阶段发现位置控制器关闭后缸体每秒漂移 0.1 mm（阀芯零位 ≠ 控制零位 0.3 V 偏差）。开 AutoZero 让它 5 分钟内自动学出补偿值，存入轴参数文件，之后位置控制器即使关掉缸体也不漂。
- **价值**：手写需要在调试时人工示波器观察 + 试错调 `fZeroCompensation`；本 FB 自动闭环学习。
- **替代方案对比**：
  - 手动调零：耗时，且温度变化后失效
  - 在线 PID 死区补偿：复杂
  - **本 FB**：液压库专门解决方案

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599749003.html
- **相关 FB**：`MC_AxRtFinish_BkPlcMc`（必须紧靠它之前调用）、`MC_AxParamSave_BkPlcMc`（保存补偿值）、`MC_AxCtrlPressure_BkPlcMc`（压力闭环）

## 9. 待确认项 (⚠️)

- PDF 接口图首行写 `MC_AxUtiOffsetLatch_BkPlcMc` 是复制粘贴错误，章节标题 `MC_AxCtrlAutoZero_BkPlcMc` 才是正确 FB 名。
- PDF 未列具体 `ErrorID` 数值。
