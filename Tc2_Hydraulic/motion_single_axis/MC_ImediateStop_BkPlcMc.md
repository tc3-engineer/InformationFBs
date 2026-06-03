# MC_ImediateStop_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599700747.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ImediateStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ImediateStop_BkPlcMc.TcPOU) |

---

## 1. 功能简述

**瞬时停车**功能块——把控制值瞬间设为 0（无任何减速斜坡）。`Execute` 上升沿启动后控制阀输出立即归 0，并在 `Execute` 持续为 TRUE 期间持续抑制所有控制 / 调节电压输出。**注意 PDF 拼写 "Imediate" 缺一个 'm'（应是 Immediate）**——这是 Beckhoff 命名错误，编译时必须用 `Imediate`。⚠️ **极高冲击风险**：瞬停大惯量液压负载可能损坏机械结构和液压元件。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 电平驱动瞬停。上升沿启动；持续高维持电压抑制；下降沿撤销抑制 |

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
    Busy:           BOOL;
    Done:           BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
    Active:         BOOL;
    CommandAborted: BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中 |
| `Done` | `BOOL` | 瞬停成功（控制值已 = 0） |
| `Error` | `BOOL` | 启动检查错 |
| `ErrorID` | `UDINT` | 错误码 |
| `Active` | `BOOL` | 命令活动中 |
| `CommandAborted` | `BOOL` | 被另一 FB 打断 |

## 3. 行为说明

**调用模式**：**电平触发**，与急停同。`Execute` 持续 TRUE 期间持续抑制电压输出。

**启动检查**：
1. **轴必须有运动可停**：轴已静止 → 立即 `Done := TRUE`
2. **轴在错误/停车中**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`
3. **轴被耦合控制**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`

**停车实现**：检查通过后**立即**把轴控制值设为 0（无任何斜坡）；所有控制 / 调节电压输出在 `Execute` 持续 TRUE 期间被强制抑制为 0。

**冲击风险**：轴当前速度越高、负载惯量越大、流量切断越快 → 冲击越大。可能造成：
- 液压管路水锤压力突升损坏密封 / 接头
- 阀芯被惯性载荷撞坏
- 机械结构受力突变变形
- 油液发热（动能转化）

**适用场景**：仅在**确实需要瞬停**且**机械结构允许**时使用，例如：
- 已知动能很小（轴速度本身就低）
- 与硬件急停回路联动（硬件已切断液压源，瞬停只是 PLC 侧响应）
- 测试 / 仿真环境

**典型陷阱**：
- 普通工艺停车用本 FB：必然损坏液压元件，绝对不要这么用
- 瞬停大惯量负载：必然冲击；用 EmergencyStop + 短 RampTime 替代
- `Execute` 频繁切换：电压抑制频繁切换可能产生振铃

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotReady` | 轴在错误状态 / 已在停车 / 被耦合 | Reset 或 GearOut |

## 5. 使用注意 / 常见坑

- **PDF 拼写 `Imediate` 缺 `m`**：API 字段名 / FB 名严格是 `MC_ImediateStop_BkPlcMc`；不要"修正"为 `Immediate` 否则编译错。
- **巨大冲击风险**：除非确认机械结构能承受，否则**不要用本 FB**；用 `MC_EmergencyStop_BkPlcMc(RampTime := 0.1)` 替代。
- **电平触发**：与急停同；持续 TRUE 才维持抑制。
- **电压抑制可能导致漂动**：撤 `Execute` 瞬间所有阀控电压恢复，残余压力可能让轴突然动；建议撤 `Execute` 前先做位置归位。
- **不是硬件急停替代品**：和 EmergencyStop 同样警告——硬件回路才是终极安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ImediateStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ImediateStop_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：仿真 / 测试环境下需要 PLC 立刻让虚拟液压轴停下并保持输出为 0（验证 HMI 上的"轴停"状态显示是否正确）。无机械负载所以无冲击风险。
- **价值**：调试 / 仿真专用；在真实液压系统中**不应使用**本 FB 做常规停车。
- **替代方案对比**：
  - 真实负载下用 `MC_EmergencyStop_BkPlcMc(RampTime := 0.1)`：50-100 ms 急停，冲击在可接受范围
  - `MC_Stop_BkPlcMc(Deceleration := 大)`：可控减速
  - 硬件急停：物理切断液压源
  - **本 FB**：仅仿真 / 已知动能极小场景

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599700747.html
- **相关 FB**：`MC_EmergencyStop_BkPlcMc`（带斜坡 + 电压抑制，更安全）、`MC_Stop_BkPlcMc`（可控减速）

## 9. 待确认项 (⚠️)

- PDF FB 名拼写 `ImediateStop`（缺 `m`）；本仓库严格按 PDF 搬运，不"修正"。
