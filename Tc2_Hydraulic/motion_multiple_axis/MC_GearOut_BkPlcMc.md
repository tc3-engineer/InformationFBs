# MC_GearOut_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Multiple axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599697675.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearOut_BkPlcMc.TcPOU`](../examples/P_Demo_MC_GearOut_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**齿轮解耦**功能块。`Execute` 上升沿释放由 `MC_GearIn_BkPlcMc` / `MC_GearInPos_BkPlcMc` 建立的齿轮耦合。**关键行为**：解耦后从轴**保持当前速度做 ContinuousMotion**——不会自动停。要让从轴停车必须接 `MC_Halt_BkPlcMc` / `MC_Stop_BkPlcMc`。若从轴当前速度极小（< `fCreepSpeed`），则直接进入 StandStill 状态。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动解耦 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Slave:          AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Slave` | `AXIS_REF_BkPlcMc` | 从轴接口结构（解耦只需从轴；主轴不变） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:           BOOL;
    Done:           BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中 |
| `Done` | `BOOL` | 解耦成功 |
| `Error` | `BOOL` | 解耦失败 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发。

**启动检查**：
1. **轴未在耦合**：直接 `Done := TRUE`，不出错（幂等）
2. **从轴速度 < `fCreepSpeed`**：直接进入 `McState_Standstill`，残余速度被吸收，`Done := TRUE`
3. 其它情况：把耦合状态转换为 ContinuousMotion（速度方向不变）；成功 → `Done`，失败 → `Error` + 算法错码

**解耦后从轴状态**：保持当前速度独立运动（`McState_ContinousMotion`），与主轴无关。要停轴需接 Halt/Stop。

**典型用法**：
- 包装机周期末解耦推送轴：解耦后立刻发 MC_Halt 把从轴停在末位
- 飞剪剪完后立即解耦，让刀架自由减速回起点
- 急停场景：先 GearOut 后再 EmergencyStop（先解耦避免影响主轴）

**典型陷阱**：
- 期望解耦自动停从轴：错；必须接 Halt/Stop
- 用 `MC_Stop` 代替 GearOut：被耦合的轴 Stop 会报 NotReady（耦合状态下 Stop 拒绝）

## 4. 错误码 / 返回值

PDF 未明列本 FB 错误码；常见情况为"未耦合 → Done 幂等"或"算法转换失败 → 算法错码"。

## 5. 使用注意 / 常见坑

- **解耦不停轴**：最大坑，多数人首次使用都中招。务必紧跟 Halt/Stop。
- **未耦合调用幂等**：直接 Done，可放心反复调用。
- **从轴 `fCreepSpeed` 屏障**：当前速度极小直接停，没问题。
- **只需从轴**：本 FB 没有 Master 字段（与 GearIn 不同）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearOut_BkPlcMc.TcPOU`](../examples/P_Demo_MC_GearOut_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：包装机周期末解耦从轴推臂。每周期主滚筒走一圈，推臂耦合推一袋；周期末必须解耦并把推臂送回起点等下一周期。本 FB 解耦 + MC_Halt 平滑减速 + MC_MoveAbsolute 回起点。
- **价值**：解耦操作的标准接口；与 GearIn / GearInPos 配套形成完整耦合 / 解耦循环。
- **替代方案对比**：
  - 直接清耦合 bit：危险，可能瞬间速度突变
  - `MC_Stop_BkPlcMc`：耦合状态下被拒绝（NotReady）
  - **本 FB**：唯一安全的解耦方式

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599697675.html
- **相关 FB**：`MC_GearIn_BkPlcMc`（线性耦合）、`MC_GearInPos_BkPlcMc`（飞行耦合）、`MC_CamOut_BkPlcMc`（凸轮解耦）、`MC_Halt_BkPlcMc`（解耦后停轴）
