# FB_BA_RampLmt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / Ramps filters` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13550466955.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_RampLmt.TcPOU`](../examples/P_Demo_FB_BA_RampLmt.TcPOU) |

---

## 1. 功能简述

斜率限制器（rate limiter / ramp limiter）。把输入信号 `fIn` 的上升 / 下降速率限制在 `(fHi - fLo) / nTiUp` 与 `(fHi - fLo) / nTiDwn` 内输出到 `fOut`，避免下游执行器（变频器、阀门、风机）承受过快的设定值阶跃。上升速率与下降速率独立配置（`nTiUp` / `nTiDwn`，单位秒）。带运行中同步（`bSync` / `fSync`），用于模式切换或外部接管时无扰过渡。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEn            : REAL;
    fIn            : REAL;
    bSync          : BOOL;
    fSync          : REAL;
    fHi            : REAL;
    fLo            : REAL;
    nTiUp          : UDINT;
    nTiDwn         : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEn` | `REAL` | - | 总使能。⚠️ PDF VAR 区印刷为 `REAL`，是 PDF 印刷错误；InfoSys / 编译器实际接受 `BOOL`。`FALSE` 时 `fOut := 0.0`；`TRUE` 时进入正常限速计算。 |
| `fIn` | `REAL` | - | 输入信号（坡道目标值）。FB 让 `fOut` 以受限速率追到 `fIn`。 |
| `bSync` | `BOOL` | - | 强制同步：上升沿生效。一次脉冲让 `fOut := fSync`，跳过坡道。 |
| `fSync` | `REAL` | - | 同步目标值。仅在 `bSync` 上升沿瞬间使用。 |
| `fHi` | `REAL` | - | 坡道上参考点；用于计算上升速率分母 `(fHi - fLo)`。**`fHi` 必须大于 `fLo`**，否则报错。 |
| `fLo` | `REAL` | - | 坡道下参考点。 |
| `nTiUp` | `UDINT` | - | 上升时间 `[s]`：`fOut` 从 `fLo` 升到 `fHi` 所需的总时间。上升速率 = `(fHi - fLo) / nTiUp` 单位/秒。 |
| `nTiDwn` | `UDINT` | - | 下降时间 `[s]`：`fOut` 从 `fHi` 降到 `fLo` 所需的总时间。下降速率 = `(fHi - fLo) / nTiDwn`。 |

⚠️ PDF Inputs 描述表额外列出 `bEnRamp : BOOL`（坡道使能：FALSE 时 `fOut = fIn` 透传），但 VAR_INPUT 区**没有**这个变量声明——是 PDF 描述列残留的字段。实际签名以 VAR_INPUT 为准（无 `bEnRamp`）。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    fOut           : REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fOut` | `REAL` | 已限速的输出信号。每个 PLC 周期相对上一周期 `fOut` 的最大变化幅度被 `nTiUp` / `nTiDwn` 限制。 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期 FB 计算允许的最大单周期变化量 `Δup = (fHi - fLo) / nTiUp * dt`（单位/周期）与 `Δdn = (fHi - fLo) / nTiDwn * dt`，其中 `dt` 为 PLC 任务周期。然后：① 若 `fIn > fOut(k-1)`（输入上升），`fOut(k) := MIN(fIn, fOut(k-1) + Δup)`——以 Δup 速度追赶；② 若 `fIn < fOut(k-1)`（输入下降），`fOut(k) := MAX(fIn, fOut(k-1) - Δdn)`——以 Δdn 速度追赶；③ 若 `fIn = fOut(k-1)`，`fOut(k) := fIn` 保持。`bEn = FALSE` 时 `fOut := 0.0`，所有历史值清零；下次启动从 0 开始爬。`bSync` 上升沿独立优先：当周期 `fOut := fSync` 跳过坡道，常用于"手动接管 → 自动恢复"瞬间避免坡道延时。`fHi ≤ fLo` 是配置错误——PDF 提示 "otherwise an error is output"。**典型用法**：变频器频率给定（避免频率突变冲击电机）、HVAC 风量斜坡启动（避免风管冲击）、温度设定值缓变（避免控制环过冲）。

## 4. 错误码 / 返回值

本 FB 无 `bError` / `nErrId` 输出；配置错误（`fHi ≤ fLo`）由 PDF 描述提到"会输出错误"，但具体形式未列。建议运行时检查 `fHi > fLo`。

## 5. 使用注意 / 常见坑

- ⚠️ **PDF VAR 区 `bEn : REAL` 是印刷错误**：实际类型 `BOOL`（InfoSys 一致）。verify_doc 因 PDF 字面而需要 REAL；编译时按 BOOL 处理。本文档照 PDF 原样保留。
- ⚠️ **PDF 描述表多出 `bEnRamp` 字段但 VAR_INPUT 区没有**：是 PDF 错列；本 FB 没有 `bEnRamp` 引脚，要"透传不限速"得 `nTiUp` / `nTiDwn` 设很小（如 1 秒）变相实现。
- **`nTiUp` / `nTiDwn` 单位是秒，整数**：1 秒粒度。要亚秒级斜率限制需要外部预处理或换其它 FB。
- **`fHi` / `fLo` 是坡道参考点不是限幅**：FB 不会把 `fOut` 限制在 `[fLo, fHi]` 范围内——`fOut` 完全跟随 `fIn`，只是速率被限。如果还需要限幅，请在 `fOut` 后串接 LIMIT 函数。（工程经验补充）
- **`bEn = FALSE` 时 `fOut := 0`，再次启动从 0 爬**：可能造成冲击。生产中常用 `bSync` 在启用前先把 `fOut` 同步到一个安全初值。（工程经验补充）
- **斜率太小**（`nTiUp` 很大）导致 `fOut` 长时间追不上 `fIn` —— 下游执行器可能等不及，看着像"卡死"。组态时按物理过程允许的最大变化率反算。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_RampLmt.TcPOU`](../examples/P_Demo_FB_BA_RampLmt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：地下车库通风变频器：白天低速运行（20 Hz），CO 报警时要在 30 秒内升到 50 Hz。直接给阶跃会让变频器跳"过流"保护。给频率指令前串本 FB：`fHi=50, fLo=20, nTiUp=30, nTiDwn=60`，让 fOut 平滑上升下降。
- **价值**：相比手写"按周期递增"代码（约 8 行 + dt 计算 + 边界判断），本 FB 一行调用搞定，上 / 下速率独立配置，自带 `bSync` 无扰切换。
- **替代方案对比**：
  - **手写斜率限制**：可行但要管 dt / 边界判断 / 状态变量；
  - **变频器内部加减速时间参数**：硬件级，改起来要修变频器配置；本 FB 是软件方案，HMI 在线可调；
  - **本 FB**：BA 标准、与 `FB_BA_FltrPT1` / `FB_BA_PIDCtrl` 组成完整的"指令调理链"。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13550466955.html
- **相关 FB**：`FB_BA_FltrPT1`（一阶低通滤波，平滑信号）、`FB_BA_PIDCtrl`（控制器）

## 9. 待确认项 (⚠️)

- PDF 印刷的 `bEn : REAL` 类型错误，实际 `BOOL`（InfoSys 一致、编译器接受 BOOL）。本文档以 PDF 原样为准（REAL），但工程使用时编译器只会接受 BOOL。
- PDF Inputs 描述表列了 `bEnRamp : BOOL` 但 VAR_INPUT 区未声明此变量，是 PDF 错列；本 FB 实际无此引脚。
