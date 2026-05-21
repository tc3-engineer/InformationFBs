# MC_WriteMotionFunctionPoint

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Camming` |
| Library Version | `1.9.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460423435.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_WriteMotionFunctionPoint.xml`](../examples/P_Demo_MC_WriteMotionFunctionPoint.xml) |

---

## 1. 功能简述

运行时**改写凸轮表（cam plate）中单个插值点（interpolation point）**的功能块。通过 `CamTableID` 找到目标表，`PointID` 选中单个节点，再用 VAR_IN_OUT 的 `Point : MC_MotionFunctionPoint` 提供新的点数据，FB 把这一点的所有字段（主轴位置 / 从轴位置 / 过渡函数类型 / 边界条件）覆盖到 NC 内的对应位置。

新数据的生效时机与 `MC_WriteMotionFunction` 共用同一套机制——由 `MC_SetCamOnlineChangeMode` 配置：可立即生效，也可延迟到主轴到达指定位置才切换；挂起未生效的写入通过 `Axis.Status.CamDataQueued` 查询。

本 FB 是"逐节点 HMI 编辑"或"微调一两个关键点"的最直接接口；改大量点请用 `MC_WriteMotionFunction` 批写。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute    : BOOL;
    CamTableID : MC_CAM_ID;
    PointID    : MC_MotionFunctionPoint_ID;
    Options    : ST_WriteMotionFunctionOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次单点写入 |
| `CamTableID` | `MC_CAM_ID` | — | 已加载凸轮表的 ID（`UDINT` 别名）；由 `MC_CamTableSelect` 在加载时分配 |
| `PointID` | `MC_MotionFunctionPoint_ID` | — | 要写入（覆盖）的那个插值点 ID |
| `Options` | `ST_WriteMotionFunctionOptions` | — | 额外选项结构。当前已知字段：`SynchronousAccess`（`BOOL`）— `TRUE` 表示走同步访问（无时延），仅在极端时序敏感场景下用 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Point : MC_MotionFunctionPoint;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `Point` | `MC_MotionFunctionPoint` | 要写入的点数据结构。调用前由 PLC 填好主轴位置、从轴位置、过渡类型等字段；FB 拷贝到 NC 对应节点 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done    : BOOL;
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `Done` | `BOOL` | 单点数据成功写入（已交付 NC，但**不一定已激活**）置 `TRUE`；与 `Error` 互斥 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，结束后变 `FALSE`；`Busy = FALSE` 才能接受新命令 |
| `Error` | `BOOL` | 写入过程出错置 `TRUE`，与 `Done` 互斥 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号；具体编码参见 §4 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次单点写——FB 通过 ADS 把 `Point` 结构内的字段送入 NC 的指定凸轮表的指定节点。`Busy := TRUE`、写入完成后 `Done := TRUE` / `Busy := FALSE`。

**与 `MC_WriteMotionFunction` 的区别**：本 FB 只动一个点；批量改用 `MC_WriteMotionFunction`。但**生效机制一样**：`Done = TRUE` 仅代表"数据进了 NC"，是否已影响正在跟随的从轴运动取决于 `MC_SetCamOnlineChangeMode` 配置的激活模式。如果配的是"延迟到主轴到达 `ActivationPosition` 才生效"，则在主轴到达前写入会排队，通过 `Axis.Status.CamDataQueued` 判断。

**修改单点会不会影响相邻点的过渡曲线**：会。motion function 的相邻节点间是用过渡函数（polynomial / sine / linear）连起来的；改一个点意味着至少改变了它与前后两点之间的两段过渡曲线形状。所以"只想改局部一段"实际牵动相邻段。

**典型用法**：
1. 用 `MC_ReadMotionFunctionPoint` 先读出该点当前定义
2. PLC 算法基于读出值修改 `MasterPos / SlavePos` 等字段
3. 配置 `MC_SetCamOnlineChangeMode`（决定何时切到新形状）
4. 上升沿 `Execute`，传 `CamTableID` + `PointID` + 改后的 `Point`
5. 等 `Done`；若延迟激活则继续监 `CamDataQueued`

**典型陷阱**：
- 改 cam 节点时机选错，导致从轴跟随出现"突跳"——必须配合延迟激活
- `PointID` 写错改到了另一个点
- 改了一个点没注意到它会改变邻接过渡曲线，造成意外的速度/加速度峰值
- 忘记初始化 `Point` 结构里的某些字段（继承上次调用残留值）

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出，`ErrorID` 是 TwinCAT NC 错误号（不是 HRESULT）。常见错误类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4Bxx` 段（NC cam 表错） | `CamTableID` 无效 / 表未加载 / `PointID` 不存在 | 确认表已 `MC_CamTableSelect` 加载、`PointID` 在 `[0, MFsize-1]` |
| `16#4260`、`16#4261` 等 | NC 通道命令错（参数检查失败、通道未 ready） | 检查 NC 通道、cam 表加载状态 |

> ⚠️ 待人工确认：PDF 第 7.4 节未列出本 FB 专属的具体错误码值。完整 NC 错误号请参见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys 主题 `E_AxisErrorCodes`。

**清错**：本 FB 自身无 reset 入口；`Error / ErrorID` 在下一次 `Execute` 上升沿自动清零。NC 通道级错误需 `MC_Reset` 清除。

## 5. 使用注意 / 常见坑

- **改点会牵动邻接过渡曲线**：见 §3。要改"一段曲线形状"实际可能需要同时改 2–3 个相邻点；这是 cam 设计的固有性质，不是 FB bug。
- **改点必须配合 `MC_SetCamOnlineChangeMode`**：默认"立即生效"在主轴运动中会引起从轴跳变；安全做法是先配"延迟到机械上空闲位置激活"。
- **`Point` 结构必须完整填**：是 VAR_IN_OUT，本 FB 把整个结构原样写入；调用前不要留任何字段未初始化（否则会写入残留数据）。
- **不可与 `MC_ReadMotionFunctionPoint` 同时读写同一点**：竞态产生不可预知行为。
- **`Options.SynchronousAccess` 谨慎用**：占 NC 高优周期；非时序极端敏感场景不必打开（工程经验补充）。
- **`Done` 是脉冲式**：`Execute = TRUE` 期间维持，下降沿后清；用上升沿做"写完成"触发。
- **写完后建议立即读回校验**：用 `MC_ReadMotionFunctionPoint` 同 `PointID` 读回对比，确认 NC 真的收到（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_WriteMotionFunctionPoint.xml`](../examples/P_Demo_MC_WriteMotionFunctionPoint.xml)

例程演示"印刷机色版滚筒相位补偿：根据色差检测结果，把第 5 号节点的从轴位置微调 +0.2mm，配合延迟激活模式在下一个套印周期边界切换"。

## 7. 业务场景与实际价值

- **场景**：
  - 印刷机色版相位补偿（每隔几张印张测一次色差，微调 cam 局部节点）
  - 包装机封口相位调整（料长波动 → 调一两个 cam 节点）
  - HMI"逐节点编辑"凸轮编辑器（操作员在触摸屏上拖某个节点的从轴位置，下发即写入）
- **价值**：对比 `MC_WriteMotionFunction` 全量写，本 FB **数据量小**（只写一个点）、**响应快**、**不需大缓冲数组**；对 HMI 交互场景最合适。
- **替代方案对比**：
  - **`MC_WriteMotionFunction`**：批量改 N 个点，适合整张表换型；单点改用它要把所有点都传一遍，浪费。
  - **`MC_SetCamOnlineChangeMode` 单独调** 不写数据：只调激活策略不改形状；本 FB 是"形状 + 生效"的实际改写者。
  - **本 FB**：单节点微调的首选。

## 8. 参考资料

- **PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf) §7.4（第 40 页）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460423435.html
- **相关 FB**：`MC_SetCamOnlineChangeMode`（配生效时机）、`MC_WriteMotionFunction`（批写）、`MC_ReadMotionFunctionPoint`（写后回读校验）、`MC_CamTableSelect`（取 ID）
- **相关 DUT**：`MC_CAM_ID`、`MC_MotionFunctionPoint_ID`、`MC_MotionFunctionPoint`、`ST_WriteMotionFunctionOptions`（PDF §8.x）
- **状态字段**：`Axis.Status.CamDataQueued`（`AXIS_REF`）
