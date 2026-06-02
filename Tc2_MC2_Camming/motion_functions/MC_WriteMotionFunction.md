# MC_WriteMotionFunction

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Camming` |
| Library Version | `1.9.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460421899.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_WriteMotionFunction.TcPOU`](../examples/P_Demo_MC_WriteMotionFunction.TcPOU) |

---

## 1. 功能简述

运行时**把 PLC 内的凸轮表数据写入 NC**（Motion Control 内核中已加载的 cam plate）的功能块。可以整张表覆盖，也可以从 `PointID` 起替换 `NumPoints` 个点。新数据通过 VAR_INPUT 的 `CamTable : MC_CAM_REF` 传入——`CamTable.pArray` 指向 PLC 端的点数据数组，FB 把这些点拷到 NC 凸轮表对应位置。

写入的生效时机由同库 `MC_SetCamOnlineChangeMode` 配置：可以**立即生效**、也可以**延迟到主轴下次到某个位置才切换**——后者保证机械上不会"中途跳变"。挂起未生效的写入可以通过 `Axis.Status.CamDataQueued`（`AXIS_REF` 的状态字段）查询。

本 FB 是"PLC 运行时改 cam 形状"的核心入口，典型场景：配方切换、料厚自适应、相位补偿等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute    : BOOL;
    CamTableID : MC_CAM_ID;
    PointID    : MC_MotionFunctionPoint_ID;
    NumPoints  : UDINT; 
    CamTable   : MC_CAM_REF;
    Options    : ST_WriteMotionFunctionOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次写入 |
| `CamTableID` | `MC_CAM_ID` | — | 已加载凸轮表的 ID（`UDINT` 别名）。由 `MC_CamTableSelect` 在加载时分配 |
| `PointID` | `MC_MotionFunctionPoint_ID` | — | 写入起点。表内的"第一个被覆盖点"的 ID（PDF 描述沿用 read 段，工程含义是 write 的起始锚点） |
| `NumPoints` | `UDINT` | — | 要写入的点数 |
| `CamTable` | `MC_CAM_REF` | — | 写入数据的来源结构。`CamTable.pArray` 指向第一个要写入的 motion function point；数据按表内顺序拷贝 |
| `Options` | `ST_WriteMotionFunctionOptions` | — | 额外选项结构。当前已知字段：`SynchronousAccess`（`BOOL`）— `TRUE` 表示走同步访问（无时延），仅在极端时序敏感场景下用 |

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
| `Done` | `BOOL` | 数据成功写入（已交付 NC，但**不一定已激活**——激活时机看 `MC_SetCamOnlineChangeMode` 配置）置 `TRUE`；与 `Error` 互斥 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，命令处理完（无论 Done / Error）后变 `FALSE` |
| `Error` | `BOOL` | 写入过程出错置 `TRUE`，与 `Done` 互斥 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号；具体编码参见 §4 |

### VAR_IN_OUT

无（本 FB `CamTable` 是 VAR_INPUT，参数即数据源；与 `MC_ReadMotionFunction` 不同）

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次写入——FB 通过 ADS 把 `CamTable.pArray` 指向的 `NumPoints` 个点送进 NC 内的指定凸轮表。请求接受后 `Busy := TRUE`；NC 完成接收置 `Done := TRUE`、`Busy := FALSE`。

**Done 不等于"已生效"**：`Done = TRUE` 只表示数据已写到 NC 内部，是否**立即作用到耦合中的从轴**取决于 `MC_SetCamOnlineChangeMode` 之前配置的激活模式：
- **`MC_CAMACTIVATION_NOW`** 类：写入即生效，从轴当下按新形状跟随
- **`MC_CAMACTIVATION_ATMASTERCAMPOS`** 类：先入队，等主轴到达指定 `ActivationPosition` 才切换；用 `Axis.Status.CamDataQueued` 检查是否有未生效的写入
- 其他模式见 `MC_CamActivationMode` 枚举

这种"分阶段"机制非常重要——如果"写入即生效"在主轴运动中盲目切换，从轴可能瞬间跳到不同位置造成机械冲击。

**`Options.SynchronousAccess`**：通常关（默认异步）。同步访问可减少传输时延但占据 PLC 周期内核资源，仅当 cam 数据必须严格在某一周期生效（极端时序敏感）才打开。

**`CamTable` 字段填法**：
- `pArray := ADR(arr)` — 指向 PLC 端的 `ARRAY[..] OF MC_MotionFunctionPoint`
- `nArraySize := SIZEOF(arr)` — 数组总字节数
- `MFsize` — 数组里实际有效的点数（参与的列数 / 行数）
- 其他元信息字段参见 PDF §8.4 `MC_CAM_REF` 定义

**典型用法**：
1. 把要写入的曲线点准备好放入 PLC 数组
2. 配置 `MC_SetCamOnlineChangeMode`（决定写入后何时切换）
3. 上升沿 `Execute`，传 `CamTableID` + `PointID := 起点` + `NumPoints` + `CamTable`
4. 等 `Done`，若激活模式是延迟激活则继续监 `Axis.Status.CamDataQueued`

**典型陷阱**：忘了先 `MC_SetCamOnlineChangeMode` → 用默认模式可能不是想要的；写入"立即生效"时主轴正在动 → 机械冲击；`CamTable.pArray` 没初始化为有效内存指针 → NC 读到野指针报错。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出，`ErrorID` 是 TwinCAT NC 错误号（不是 HRESULT）。常见错误类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4Bxx` 段（NC cam 表错） | `CamTableID` 无效 / 表未加载 / `PointID` 起点越界 / `NumPoints` 超过表容量 | 确认表已 `MC_CamTableSelect` 加载、`PointID + NumPoints ≤ MFsize` |
| `16#4260`、`16#4261` 等 | NC 通道命令错（参数检查失败、通道未 ready） | 检查 NC 通道、cam 表加载状态、`pArray` 非空 |

> ⚠️ 待人工确认：PDF 第 7.3 节未列出本 FB 专属的具体错误码值。完整 NC 错误号请参见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys 主题 `E_AxisErrorCodes`。

**清错**：本 FB 自身无 reset 入口；`Error / ErrorID` 在下一次 `Execute` 上升沿自动清零。NC 通道级错误需 `MC_Reset` 清除。

## 5. 使用注意 / 常见坑

- **必须先用 `MC_SetCamOnlineChangeMode` 配置激活策略**：默认策略不一定符合工艺要求。常见坑：开发期没配，结果运行时写入"立即生效"，从轴瞬间跳位。
- **激活模式延迟的话要等 `CamDataQueued = FALSE`**：`Done = TRUE` 仅代表数据已交给 NC，机械上是否已切到新形状要看 `Axis.Status.CamDataQueued`。
- **`CamTable.pArray` 必须指向 PLC 内有效数组**：与 `MC_ReadMotionFunction` 一样；写之前调用方负责把要写的点填到这块内存里。
- **`NumPoints` 必须 ≤ NC 端表能容纳的点数**：超出报错；扩容需要重新声明并加载一张更大的表。
- **不可与 `MC_ReadMotionFunction` 同时并发跑同一张表**：竞态导致读到中间数据。
- **`Options.SynchronousAccess` 谨慎使用**：开了会侵占 NC 高优任务时间，不到极端时序敏感场景不要打开（工程经验补充）。
- **`Done` 仅维持到 `Execute` 下降沿**：要用 `Done` 触发后续逻辑（比如自动激活检测），抓 `Done` 上升沿。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_WriteMotionFunction.TcPOU`](../examples/P_Demo_MC_WriteMotionFunction.TcPOU)

例程演示"包装机来料瓶宽变了——用 PLC 程序整体替换当前生效的凸轮形状，从 250mm 瓶专用 cam 切到 330mm 瓶专用 cam"。

## 7. 业务场景与实际价值

- **场景**：
  - 包装机来料规格变化 → 整体改 cam 形状切换"产品配方"
  - 卷绕机料厚自适应 → 周期性微调凸轮以补偿张力波动
  - 印刷机色差校正 → 写入相位补偿后的新凸轮
- **价值**：传统做法是给每种产品规格做一张离线 cam 文件，靠 XAE 离线下载切换——慢、需要停机；用本 FB 可以**不停机切配方**，PLC 里把新数据备好直接写入，配合延迟激活模式实现"主轴到下一个换型位置自动切换"。
- **替代方案对比**：
  - **`MC_WriteMotionFunctionPoint`**：单点写，适合微调单个节点；整表换型用本 FB 效率高得多。
  - **离线 cam designer + XAE 下载**：能改 cam 形状但需 PLC 重启或重新激活，无法在线动态切换。
  - **`MC_CamTableSelect` 切到另一张已加载的 cam**：适合"少数几种固定配方间切换"，每种配方独占一张表；本 FB 适合"配方组合无限多"或"需要算式生成"的场景。

## 8. 参考资料

- **PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf) §7.3（第 38 页）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460421899.html
- **相关 FB**：`MC_SetCamOnlineChangeMode`（配生效时机）、`MC_WriteMotionFunctionPoint`（单点写）、`MC_ReadMotionFunction`（回读校验）、`MC_CamTableSelect`（取 ID）、`MC_CamIn`（激活凸轮耦合）
- **相关 DUT**：`MC_CAM_ID`、`MC_CAM_REF`、`ST_WriteMotionFunctionOptions`（PDF §8.x）
- **状态字段**：`Axis.Status.CamDataQueued`（`AXIS_REF`）
