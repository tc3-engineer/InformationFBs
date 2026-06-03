# MC_CamOut_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Multiple axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599691531.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_CamOut_BkPlcMc.TcPOU`](../examples/P_Demo_MC_CamOut_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**凸轮表解耦**功能块。`Execute` 上升沿释放由 `MC_CamIn_BkPlcMc` 建立的凸轮表耦合。**关键行为与 `MC_GearOut_BkPlcMc` 一致**：解耦后从轴保持当前速度做 ContinuousMotion，不自动停。本 FB 不需要时间（`Busy` 永远 FALSE）。

## 2. 接口定义

### VAR_INPUT

⚠️ PDF 在本 FB 章节 VAR_INPUT 代码块有印刷错误（`END_VAR` 被截断为 `ND_VAR`），但 PDF 接口图、PDF 描述表与 InfoSys 都确认 `Execute : BOOL` 字段存在。按 PDF 描述表搬运字段定义如下（实际代码必须用 `END_VAR`）：

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
| `Slave` | `AXIS_REF_BkPlcMc` | 从轴接口结构 |

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
| `Busy` | `BOOL` | 命令处理中。本 FB 不需任何时间，`Busy` 永远为 `FALSE`，仅为 PLCopen 兼容性保留 |
| `Done` | `BOOL` | 解耦成功 |
| `Error` | `BOOL` | 解耦失败 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发。

**启动检查**：
1. `pStAxParams` 指针未初始化 → `Error`、`ErrorID := dwTcHydErrCdPtrPlcMc` 或 `dwTcHydErrCdPtrMcPlc`
2. **轴未在耦合**：直接 `Done := TRUE`（幂等）
3. **从轴速度 < `fCreepSpeed`**：直接进入 `McState_Standstill`，残余速度被吸收，`Done := TRUE`
4. 其它：把凸轮耦合转换为 ContinuousMotion（保持速度方向）；成功 → `Done`，失败 → `Error`

**解耦后从轴**：保持当前速度独立运动，与主轴脱钩。需要主动 Halt/Stop 才停。

**典型用法**：
- 凸轮动作完成后释放从轴
- 急停场景：先 CamOut 后再处理

**典型陷阱**：与 `MC_GearOut_BkPlcMc` 完全一致——解耦不停轴。

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdPtrPlcMc` / `dwTcHydErrCdPtrMcPlc` | `pStAxParams` 指针未初始化 | 检查轴初始化 |
| (其它) | 算法转换失败 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **解耦不停轴**：与 GearOut 同。
- **`Busy` 永远 FALSE**：判完成看 `Done`。
- **未耦合调用幂等**：直接 Done。
- **只需从轴**：与 GearOut 同没有 Master 字段。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_CamOut_BkPlcMc.TcPOU`](../examples/P_Demo_MC_CamOut_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑凸轮耦合周期末，主锁模轴到末位停下，要解耦注射头并把它送回起点等下一周期。
- **价值**：标准凸轮解耦接口；与 CamIn 配套形成完整循环。
- **替代方案对比**：
  - 直接清算法耦合 bit：危险
  - `MC_GearOut_BkPlcMc`：解齿轮耦合不解凸轮
  - **本 FB**：凸轮解耦唯一安全方式

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599691531.html
- **相关 FB**：`MC_CamIn_BkPlcMc`（凸轮耦合）、`MC_GearOut_BkPlcMc`（齿轮解耦）、`MC_Halt_BkPlcMc`（解耦后停轴）
