# FB_BA_FltrPT1

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / Ramps filters` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13550416779.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_FltrPT1.TcPOU`](../examples/P_Demo_FB_BA_FltrPT1.TcPOU) |

---

## 1. 功能简述

一阶低通滤波器（PT1，first-order lag filter）。把噪声较多的输入信号 `fIn` 经过时间常数 `nDampConst` `[s]` 平滑后输出到 `fOut`。首次调用时（系统上电）自动把 `fOut` 设为 `fIn` 当前值——避免开机零值冲击；`bSetActl` 上升沿可在线把 `fOut` 强制同步回 `fIn` 当前值（用于工艺切换时的无扰过渡）。常用于温度 / 压力传感器去噪、控制环 PV 平滑、避免 D 部分对噪声过度敏感。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    fIn            : REAL;
    nDampConst     : UDINT;
    bSetActl       : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fIn` | `REAL` | 输入信号（含噪声）。 |
| `nDampConst` | `UDINT` | 滤波时间常数 `[s]`。内部限制 `0..86400`（即 0 秒到 24 小时）。`0` 表示不滤波（`fOut := fIn` 透传）；常用值：温度 5-30 s；压力 1-10 s。物理意义：`fIn` 阶跃变化后，约 `nDampConst` 秒内 `fOut` 达到 63% 阶跃幅度（PT1 的时间常数定义）。 |
| `bSetActl` | `BOOL` | 上升沿强制：把当前 `fOut` 直接设为 `fIn`（无扰同步）。用于工艺模式切换或测量值校准后无冲击恢复。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    fOut           : REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fOut` | `REAL` | 滤波后的输出信号。响应 `fIn` 阶跃时按 PT1 时间常数缓慢趋近。 |

### VAR_IN_OUT

无。

## 3. 行为说明

PT1 滤波器的传递函数 `G(s) = 1 / (1 + τs)`，其中 `τ = nDampConst` `[s]`。在 PLC 离散实现下：每周期按下式更新 `fOut(k) := fOut(k-1) + (fIn - fOut(k-1)) * dt / (τ + dt)`，其中 `dt` 是任务周期。这意味着：① 输入阶跃变化后，`fOut` 第一秒（一个时间常数内）变化 63.2%，三秒（3τ）后变化 95%，五秒（5τ）后近似稳态；② 高频噪声被有效抑制——截止频率 `fc = 1/(2π·τ)` Hz；③ `nDampConst = 0` 时退化为透传。首次调用：FB 自动把 `fOut := fIn`，避免上电时 `fOut` 从 0 缓慢爬升到真值的"假冷启动"。`bSetActl` 上升沿强制同步：场景是工艺模式切换（如手动 → 自动），切换瞬间 PV 不应该被滤波器拖慢——用 `bSetActl` 一次脉冲让 `fOut` 立刻等于 `fIn` 当前值，避免下游控制器响应一次"假阶跃"。**`nDampConst` 选择**：太小不去噪；太大响应迟钝、相位滞后明显。经验：被控物理过程时间常数的 1/10 到 1/5。

## 4. 错误码 / 返回值

本 FB 无错误码、无返回值。

## 5. 使用注意 / 常见坑

- **`nDampConst` 单位是秒，整数**：`nDampConst = 1` 表示 1 秒时间常数，不是 1 ms。需要亚秒级滤波时考虑用其它带浮点时间常数的滤波 FB（或预处理）。
- **`nDampConst > 86400`** 会被内部裁剪到 86400（24 小时）。极端慢滤波场景实际上没意义。
- **首周期 `fOut := fIn`** 避免冷启动假阶跃，但 PLC 重启后第一个 `fIn` 值如果本身异常（如传感器还没就绪），`fOut` 会跟着异常。等传感器就绪后再用 `bSetActl` 重新同步一下更安全。（工程经验补充）
- **不能在控制环里给 D 部分加 PT1 滤波然后还给 D 用太大时间常数**——会引入相位滞后让控制环不稳定。`fNeutralZone` + PID 的 `tDampingTime` 通常是更好的去噪手段。（工程经验补充）
- **多通道滤波**：每路 PV 一个 `FB_BA_FltrPT1` 实例，不要共用——FB 内部 `fOut(k-1)` 状态会乱掉。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_FltrPT1.TcPOU`](../examples/P_Demo_FB_BA_FltrPT1.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：风管温度测量噪声大（Pt100 + 长线缆 + 风扰）：原始信号每秒抖动 ±0.5℃，但控制环只需要 ±0.1℃ 精度。给原始信号加 `nDampConst = 10 s` PT1 滤波，输出 `fOut` 平滑稳定，控制器再用 `fOut` 作为 PV。
- **价值**：① 一行 FB 调用替代手写离散低通滤波代码（约 5 行 + 历史值缓存）；② 自动处理首周期初值，无冷启动假阶跃；③ 在线 `bSetActl` 可平滑切换工艺模式。
- **替代方案对比**：
  - **手写离散低通**：`fOut := fOut + (fIn - fOut) * dt / (T + dt)` —— 可行但要自己维护状态变量和首周期处理；
  - **直接平均滑动窗**：响应慢、内存大，不如 PT1；
  - **本 FB**：BA 标准化，与其它 BA2 库 FB 接口一致。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13550416779.html
- **相关 FB**：`FB_BA_RampLmt`（斜率限制，输出限速）、`Tc2_Filter.FB_FTR_PT1`（Tc2 版 PT1，参数表达不同）
