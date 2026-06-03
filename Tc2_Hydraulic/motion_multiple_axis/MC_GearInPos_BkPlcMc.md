# MC_GearInPos_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Multiple axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599696651.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearInPos_BkPlcMc.TcPOU`](../examples/P_Demo_MC_GearInPos_BkPlcMc.TcPOU) |

---

## 1. 功能简述

**飞行同步**电子齿轮耦合功能块（PLCopen GearInPos）。与 `MC_GearIn_BkPlcMc` 不同，本 FB 允许在主轴**已经运动中**触发耦合：从轴会先在 `MasterStartDistance` 距离内追上主轴速度，到达 `MasterSyncPosition` 时正好以齿比同步进入耦合。`StartSync` 表示"追赶阶段进行中"，`InSync` 表示"已完全同步"。自 V3.0.33 起加入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
     Execute:               BOOL;
     RatioNumerator:        INT;
     RatioDenominator:      INT;
     MasterSyncPosition:    LREAL;
     SlaveSyncPosition:     LREAL;
     SyncMode:              INT;
     MasterStartDistance:   LREAL;
     Acceleration:          LREAL;
     Deceleration:          LREAL;
     Jerk:                  LREAL;   //from V3.0.5
     BufferMode:            MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动飞行同步 |
| `RatioNumerator` | `INT` | — | 齿比分子 |
| `RatioDenominator` | `INT` | — | 齿比分母 |
| `MasterSyncPosition` | `LREAL` | — | 主轴上同步完成的位置，单位 mm |
| `SlaveSyncPosition` | `LREAL` | — | 从轴上同步完成的位置，单位 mm |
| `SyncMode` | `INT` | — | 当前不支持 |
| `MasterStartDistance` | `LREAL` | — | 主轴需要走过的耦合建立距离，单位 mm |
| `Acceleration` | `LREAL` | — | 同步加速度，单位 mm/s² |
| `Deceleration` | `LREAL` | — | 同步减速度，单位 mm/s² |
| `Jerk` | `LREAL` | — | jerk，单位 mm/s³（自 V3.0.5 起加入） |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
     Master:       AXIS_REF_BkPlcMc;
     Slave:        AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Master` | `AXIS_REF_BkPlcMc` | 主轴接口结构 |
| `Slave` | `AXIS_REF_BkPlcMc` | 从轴接口结构 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
     StartSync:        BOOL;
     InSync:           BOOL;
     Busy:             BOOL;
     Active:           BOOL;
     CommandAborted:   BOOL;
     Error:            BOOL;
     ErrorID:          UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `StartSync` | `BOOL` | 追赶阶段进行中（从静止到完全耦合的过渡） |
| `InSync` | `BOOL` | 首次同步成功（latched） |
| `Busy` | `BOOL` | 命令处理中 |
| `Active` | `BOOL` | 命令活动中 |
| `CommandAborted` | `BOOL` | 耦合被打断 |
| `Error` | `BOOL` | 启动检查或运行中错 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动飞行同步。

**核心机制**：从轴在主轴位置等于 `MasterSyncPosition - MasterStartDistance` 时开始加速；主轴到达 `MasterSyncPosition` 时从轴正好到达 `SlaveSyncPosition`，且从轴速度 = 主轴速度 × 齿比。耦合的"建立阶段"用 `StartSync = TRUE` 表示；正式耦合用 `InSync = TRUE` 表示。

**与 `MC_GearIn_BkPlcMc` 的核心区别**：
- GearIn：仅能在两轴静止时启动
- GearInPos：可在主轴运动中启动，从轴会在指定距离内追上同步

**典型用法**：
- 飞剪：主刀架以传送带速度移动，剪刀必须在材料经过某点时同步速度切下（必须飞行同步，不能停传送带）
- 在线包装：传送带不停，包装机以传送带速度同步贴标 / 切袋

**典型陷阱**：
- `MasterStartDistance` 太短：从轴来不及追到目标速度，`InSync` 推迟或失败
- 同步参数 `Acceleration` / `Deceleration` 太小：相同 MasterStartDistance 下从轴跟不上
- `SyncMode` 给值：当前不支持，给 0 即可

## 4. 错误码 / 返回值

PDF 未详细列本 FB 的所有 ErrorID 数值；常见与 GearIn 同：`dwTcHydErrCdIllegalGearFactor`（齿比错）、`dwTcHydErrCdNotReady`（轴有错）、算法错码。⚠️ 详细码表查 PDF §5.2。

## 5. 使用注意 / 常见坑

- **`MasterStartDistance` 计算**：从轴从静止加速到目标速度需要 `v / a` 秒，期间主轴会走 `v_master × v_slave_target / (2 × a)` 距离；`MasterStartDistance` 应略大于此。
- **`SyncMode` 当前不支持**：传 0 即可。
- **`InSync` latched**：与 GearIn 的 InGear 语义相同。
- **耦合后用 GearOut 解耦**：与 GearIn 相同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearInPos_BkPlcMc.TcPOU`](../examples/P_Demo_MC_GearInPos_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：纸张包装线"飞剪"应用。传送带不停，包装薄膜以 500 mm/s 持续移动；切刀必须在标签位置经过切刀下方时以同样速度同步切断（齿比 1:1），切完后回到起点等下一片。本 FB 触发后从轴在 200 mm 的 master 距离内追上速度，到达切点时同步切割。
- **价值**：手写飞行同步算法极其复杂（速度规划 / 位置预测 / 同步判定）；本 FB 提供 PLCopen 标准接口一行调用。
- **替代方案对比**：
  - `MC_GearIn_BkPlcMc`：仅静止启动，不适合不能停的传送带
  - 自己写飞行算法：高难度，需要硬实时
  - **本 FB**：飞行同步标准接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599696651.html
- **相关 FB**：`MC_GearIn_BkPlcMc`（静止启动版）、`MC_GearOut_BkPlcMc`（解耦）

## 9. 待确认项 (⚠️)

- PDF 在本 FB 章节未详细列具体 `ErrorID` 数值。
