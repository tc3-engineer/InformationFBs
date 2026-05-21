# Tc2_MC2_Camming — NC 凸轮表运行时编辑库

> Beckhoff TwinCAT 3 NC Camming（TF5050）库，提供**在 PLC 运行时读写凸轮表（cam plate / motion function）**的功能块。
> 与 TwinCAT XAE 内的离线 cam designer 工具互补：cam designer 在工程编辑期设计 cam 形状，本库在 PLC 运行时动态读出、回写、修改、可视化 cam 形状。
>
> - **Library Version**：1.9.1
> - **Source PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/

## 关键概念

- **凸轮表（cam plate / motion function）**：定义一根从轴位置如何随主轴位置变化的曲线。由若干 `MC_MotionFunctionPoint` 插值节点 + 节点间过渡函数（polynomial / sine / linear）组成
- **`MC_CAM_ID`**：NC 内核分配给已加载凸轮表的唯一 ID（`UDINT` 别名）。本库所有读写 FB 都靠它定位目标表；ID 通常由同 PDF 的 `MC_CamTableSelect`（本库未直接列入，但工程上是入口）取得
- **`MC_CAM_REF`**：PLC 端凸轮表数据的引用结构。携带数据数组指针 `pArray`、容量 `nArraySize`、有效点数 `MFsize`、列数等元信息；本库读写 FB 通过它在 PLC 与 NC 之间传递点数据
- **写入与生效分离**：`MC_WriteMotionFunction` / `MC_WriteMotionFunctionPoint` 只是"把数据写进 NC"；何时让从轴真正按新形状跟随，由 `MC_SetCamOnlineChangeMode` 配置（立即 / 主轴到达指定位置 / ...）
- **挂起写入状态**：写入后未生效的数据通过 `Axis.Status.CamDataQueued`（`AXIS_REF` 字段）检查
- **错误码 `ErrorID`**：TwinCAT NC 错误号（不是 HRESULT）；具体码表见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys `E_AxisErrorCodes`

## 分类索引

### Motion functions（凸轮表运行时编辑，6 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_ReadMotionFunction` | 批量读取凸轮表原始节点数据（整表或一段） | [motion_functions/MC_ReadMotionFunction.md](motion_functions/MC_ReadMotionFunction.md) |
| `MC_ReadMotionFunctionPoint` | 读取单个插值节点的定义 | [motion_functions/MC_ReadMotionFunctionPoint.md](motion_functions/MC_ReadMotionFunctionPoint.md) |
| `MC_WriteMotionFunction` | 批量写入凸轮表节点（整表换型 / 配方切换） | [motion_functions/MC_WriteMotionFunction.md](motion_functions/MC_WriteMotionFunction.md) |
| `MC_WriteMotionFunctionPoint` | 改写单个插值节点（HMI 逐点编辑、相位补偿） | [motion_functions/MC_WriteMotionFunctionPoint.md](motion_functions/MC_WriteMotionFunctionPoint.md) |
| `MC_SetCamOnlineChangeMode` | 配置后续 cam 写入的生效时机与缩放策略（不实际写数据） | [motion_functions/MC_SetCamOnlineChangeMode.md](motion_functions/MC_SetCamOnlineChangeMode.md) |
| `MC_ReadMotionFunctionValues` | 把 cam 曲线按主轴位置等距采样返回（HMI 画曲线、CSV 导出） | [motion_functions/MC_ReadMotionFunctionValues.md](motion_functions/MC_ReadMotionFunctionValues.md) |

## 典型工程使用流程

1. **加载凸轮表**：使用 `Tc2_MC2` 的 `MC_CamTableSelect` 把工程内已设计的 cam 加载到 NC，取得 `MC_CAM_ID`（本库不直接提供加载 FB，但读写都需要这个 ID）
2. **配置激活策略**：调用 `MC_SetCamOnlineChangeMode` 设定后续写入的生效时机（推荐"到达主轴指定位置才切换"避免机械冲击）
3. **建立耦合**：使用 `Tc2_MC2` 的 `MC_CamIn` 把从轴绑定到主轴，按 `CamTableID` 指定的形状跟随
4. **运行时编辑（按需）**：
   - 配方切换 → `MC_WriteMotionFunction` 整表覆盖
   - 局部微调 → `MC_WriteMotionFunctionPoint` 单点写
   - 备份当前形状 → `MC_ReadMotionFunction` 整表读
   - HMI 可视化 → `MC_ReadMotionFunctionValues` 等距采样
5. **解耦**：`MC_CamOut` 解除主从绑定

## 例程

每个 FB 都配套一份可导入 TwinCAT XAE 的 PLCopenXML 例程：见 [examples/](examples/) 目录。

例程涵盖的典型工业场景：
- 包装机料厚 / 瓶宽自适应（运行时 cam 整表换型）
- 印刷机色版套印相位补偿（运行时单点微调）
- HMI 凸轮可视化（等距采样画曲线图）
- 配方切换激活策略配置
- 工艺审计 cam 形状备份

## 与相关库的关系

- **`Tc2_MC2`**：提供 `MC_CamTableSelect`（加载）、`MC_CamIn`（耦合）、`MC_CamOut`（解耦）等"使用 cam"的 FB；本库提供"修改 cam"的 FB
- **TwinCAT XAE cam designer**：工程设计期的 cam 编辑器；本库是它的运行时对偶
