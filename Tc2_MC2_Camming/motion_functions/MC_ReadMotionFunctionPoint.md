# MC_ReadMotionFunctionPoint

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Camming` |
| Library Version | `1.9.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460420363.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadMotionFunctionPoint.xml`](../examples/P_Demo_MC_ReadMotionFunctionPoint.xml) |

---

## 1. 功能简述

运行时**读取凸轮表（cam plate / motion function）中单个插值点（interpolation point）**的功能块。给定 `CamTableID` 和 `PointID`，把对应那一个 motion function point 的完整数据（主轴位置、从轴位置、过渡函数类型、边界条件等）读到 VAR_IN_OUT 的 `Point : MC_MotionFunctionPoint` 结构里。

与同库的 `MC_ReadMotionFunction`（批量读多个点）相比，本 FB 一次只读一个点；适合"只需要确认 / 修改某一点参数"的场景，避免为单点动作分配整张表的数组缓冲。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute    : BOOL;
    CamTableID : MC_CAM_ID;
    PointID    : MC_MotionFunctionPoint_ID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次读取 |
| `CamTableID` | `MC_CAM_ID` | — | 已加载凸轮表的 ID（`UDINT` 别名）；由 `MC_CamTableSelect` 在加载凸轮表时分配 |
| `PointID` | `MC_MotionFunctionPoint_ID` | — | 要读取的那个插值点 ID（点在表内的唯一编号） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Point : MC_MotionFunctionPoint;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `Point` | `MC_MotionFunctionPoint` | 单个 motion function point 的数据结构。本 FB `Done = TRUE` 后该结构被填充为目标点的内容（主轴位置 X、从轴位置 Y、过渡类型 etc.） |

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
| `Done` | `BOOL` | 单点数据成功读出置 `TRUE`；与 `Error` 互斥 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，结束后变 `FALSE`；`Busy = FALSE` 才能接受新命令 |
| `Error` | `BOOL` | 读取过程出错置 `TRUE`，与 `Done` 互斥 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号；具体编码参见 §4 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次单点读请求——FB 向 NC 发起异步请求，按 `CamTableID` 定位表、按 `PointID` 定位点，把该点的全部字段拷贝到 PLC 侧的 `Point` 结构。请求接受后 `Busy := TRUE`，完成置 `Done := TRUE`、`Busy := FALSE`，整个过程不阻塞 PLC 周期，但要等若干周期才能完成（典型 1–N 个）。

**异步特性**：与 `MC_ReadMotionFunction` 一样经 NC ADS 通道，PLC 必须**周期性调用本 FB 实例**直至 `Done` 为止。`Execute := TRUE` 一次后立刻 `Execute := FALSE` 不影响请求继续处理，但**必须保留 FB 实例的周期调用**才能拿到 `Done` 信号。

**`Point` 字段含义**：`MC_MotionFunctionPoint` 结构（PDF §8.x 定义）含主轴位置、从轴位置、速度/加速度/jerk 边界条件、点之间的过渡函数类型（直线 / 多项式 / 正弦等）。读出后 PLC 可基于这些字段判断"这点在曲线哪段"、做 HMI 显示、或叠加修改后用 `MC_WriteMotionFunctionPoint` 写回。

**典型用法**：
1. 用 `MC_CamTableSelect` 加载凸轮表，获得 `CamTableID`
2. 上升沿 `Execute`，传 `CamTableID` + 目标 `PointID`
3. 等 `Done := TRUE`，从 `Point` 结构取数据；若 `Error := TRUE` 处理 `ErrorID`
4. 同一 FB 实例可下次再触发，但需先等 `Busy := FALSE`

**典型陷阱**：传一个表里不存在的 `PointID` → `Error`；并发用同一 FB 实例同时读两个点（必须串行）；`Done` 在 `Execute` 下降沿后会清零，应在 `Done = TRUE` 周期内立刻把 `Point` 数据拷走再降沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出，`ErrorID` 是 TwinCAT NC 错误号（不是 HRESULT）。常见错误类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4Bxx` 段（NC cam 表错） | `CamTableID` 无效 / 表未加载 / `PointID` 在表内不存在 | 确认 `MC_CamTableSelect` 已 `Done`、`PointID` 在 `[0, MFsize-1]` 范围 |
| `16#4260`、`16#4261` 等 | NC 通道命令错（参数检查失败、通道未 ready） | 检查 NC 通道、cam 表加载状态 |

> ⚠️ 待人工确认：PDF 第 7.2 节未列出本 FB 专属的具体错误码值。完整 NC 错误号请参见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys 主题 `E_AxisErrorCodes`。

**清错**：本 FB 自身无 reset 入口；`Error / ErrorID` 在下一次 `Execute` 上升沿自动清零。NC 通道级错误需 `MC_Reset` 清除。

## 5. 使用注意 / 常见坑

- **`Point` 是 VAR_IN_OUT，必须传一个真实的 PLC 变量**：不能传字面常量；调用前不必预填字段，FB 会写入。
- **`PointID` 不是数组下标**：是 NC 内部分配给每个 motion function point 的唯一 ID；不能假设它从 0 连续递增。要枚举所有点请用 `MC_ReadMotionFunction` 一次性批读。
- **不要在读取期间用 `MC_WriteMotionFunctionPoint` 改同一点**：竞态会读到中间状态。
- **`Done` 是脉冲式信号**：`Execute = TRUE` 期间维持，`Execute := FALSE` 后下个周期 `Done := FALSE`；用 `Done` 上升沿做"读完成"动作。
- **FB 实例不可重入**：单实例同一时刻只跑一次读，多个 `CamTableID` 不能并发用一个 FB 实例（工程经验补充）。
- **典型场景需配合 `MC_CamTableSelect`**：单纯一个 `MC_CAM_ID` 数字（不经过 select）不能直接当 `CamTableID` 用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadMotionFunctionPoint.xml`](../examples/P_Demo_MC_ReadMotionFunctionPoint.xml)

例程演示"工艺工程师做料厚自适应：先用 `MC_ReadMotionFunctionPoint` 读出指定 `PointID` 处的当前主从轴位置，与 HMI 上设定值对比，再决定要不要写回"。

## 7. 业务场景与实际价值

- **场景**：包装机 / 印刷机做"局部凸轮微调"——只想知道第 K 个节点的当前主轴位置和从轴位置，不想读整张表（整张表可能几百点，回读慢）。或在调试期间确认上一次写入是否真的落到了那一点。
- **价值**：相比 `MC_ReadMotionFunction` 批读再筛选某点，本 FB 一次只读一个点，PLC 缓冲区开销最小、NC 处理时间最短，适合 HMI"逐点编辑"界面。
- **替代方案对比**：
  - **`MC_ReadMotionFunction`**：批读多点，适合整表备份/可视化；单点查询用它有点重。
  - **`MC_ReadMotionFunctionValues`**：返回插值后的等间距采样曲线，**不是原始节点**；不能用来获取某个具体 PointID 的真实定义。
  - **本 FB**：单节点定义查询的最直接方式。

## 8. 参考资料

- **PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf) §7.2（第 37 页）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460420363.html
- **相关 FB**：`MC_ReadMotionFunction`（批读）、`MC_WriteMotionFunctionPoint`（单点写）、`MC_CamTableSelect`（取 ID）
- **相关 DUT**：`MC_CAM_ID`、`MC_MotionFunctionPoint_ID`、`MC_MotionFunctionPoint`（PDF §8.x）
