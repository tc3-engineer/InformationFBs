# Tc2_MC2_FlyingSaw — 飞锯 / 横切耦合库（TF5055）

> Beckhoff TwinCAT 3 函数产品 **TF5055 NC Flying Saw** 的 PLC 库。提供在主轴运动中接入的主从同步功能块（FB），用于飞锯 / 飞剪 / 横切 / 横封等"从轴跟随主轴线速度或在指定位置精确对齐"的场景。
> 这些 FB 是对 Tc2_MC2 标准齿轮耦合（`MC_GearIn`）的扩展：标准 `MC_GearIn` 只能在从轴静止时耦合，本库的 `MC_GearInVelo` / `MC_GearInPos` 可在主轴运动中接入并完成同步。
>
> - **Library Version**：1.6.1（TF5055，PDF 头部 Version）
> - **Source PDF**：[TF5055_TC3_NC_Flying_Saw_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/

## 关键概念

- 耦合 FB 的轴接口为 `Master : AXIS_REF` 与 `Slave : AXIS_REF`（都是 **VAR_IN_OUT**，必须传引用）
- **速度同步（`MC_GearInVelo`）**：只保证从轴速度 = 主轴速度 × 齿比，不约束位置
- **位置同步（`MC_GearInPos`）**：在指定主/从同步点上**位置与速度同时精确对齐**（套准横切的关键）
- 输出遵循 PLCopen 风格：`StartSync` / `InSync` / `Busy` / `Active` / `CommandAborted` / `Error` + `ErrorID`
- 齿比用 `RatioNumerator` / `RatioDenominator` 表示，分子可为负（反向跟随）
- `SyncMode`（`ST_SyncMode`）是逐位掩码，开启后才校验对应的速度/加速度/位置限值
- **解耦不停从轴**：运动中 `MC_GearOut` 后从轴保持速度继续走，必须用 `MC_Stop` / `MC_Halt` 主动停从轴——飞锯最典型事故
- 主轴必须已在运动才能完成同步（`MC_GearInPos` 明确要求，`MC_GearInVelo` 支持运动中接入）
- 时间基同步模式 `GEARINSYNCMODE_TIMEBASED` 当前仅 `MC_GearInVelo` 支持

## 分类索引

### 飞锯耦合（Axis coupling）

| FB | 说明 | 文档 |
|---|---|---|
| `MC_GearInVelo` | 速度同步：从轴同步到主轴速度（按齿比），支持运动中接入 | [axis_coupling/MC_GearInVelo.md](axis_coupling/MC_GearInVelo.md) |
| `MC_GearInPos` | 位置同步：在指定主/从同步点上位置+速度精确对齐 | [axis_coupling/MC_GearInPos.md](axis_coupling/MC_GearInPos.md) |

### 诊断（Diagnostics）

| FB | 说明 | 文档 |
|---|---|---|
| `MC_ReadFlyingSawCharacteristics` | 读取本次飞锯同步轮廓的特征值（飞锯启动后才可用） | [diagnostics/MC_ReadFlyingSawCharacteristics.md](diagnostics/MC_ReadFlyingSawCharacteristics.md) |

### 数据类型（Data types）

| DUT | 说明 | 文档 |
|---|---|---|
| `MC_FlyingSawCharacValues` | 飞锯同步特征值结构体（由上面读特征值 FB 填充） | [data_types/MC_FlyingSawCharacValues.md](data_types/MC_FlyingSawCharacValues.md) |

## 例程

所有 `P_Demo_*.TcPOU` 例程在 [`examples/`](examples/) 目录，TwinCAT 3 原生 .TcPOU 格式，可直接右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入 TwinCAT 3 XAE。注意飞锯例程需要工程中已配置 NC 主/从轴并将相应 `AXIS_REF` 与之关联。

## 备注

本库其余数据类型（`ST_SyncMode`、`E_GearInSyncMode`、`ST_GearInPosOptions`、`ST_GearInVeloOptions`）在飞锯 FB 文档的接口表与行为说明中已引用解释，本批次未单独成文。
