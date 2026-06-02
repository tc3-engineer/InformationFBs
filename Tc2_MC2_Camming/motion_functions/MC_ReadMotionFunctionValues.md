# MC_ReadMotionFunctionValues

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Camming` |
| Library Version | `1.9.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460426507.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadMotionFunctionValues.TcPOU`](../examples/P_Demo_MC_ReadMotionFunctionValues.TcPOU) |

---

## 1. 功能简述

**把凸轮表（motion function）按主轴位置等距采样，返回离散化后的曲线数据表**的功能块。与 `MC_ReadMotionFunction`（读原始节点定义）不同：本 FB 读出来的是按 `Increment` 步长对整段曲线**做插值采样**的结果——主轴从 `StartPosMaster` 走到 `EndPosMaster`，每隔 `Increment` 取一组数据。

可同时取多种导数：`ValueSelectMask` 是位掩码，选位置 / 速度 / 加速度 / jerk 等中的哪些（基于 `MC_ValueSelectType` 枚举累加）。结果通过 VAR_IN_OUT 的 `CamTable : MC_CAM_REF` 返回——`CamTable.pArray` 指向 PLC 端用于接收结果的二维数据数组。

**核心用途**：HMI / SCADA 上画凸轮曲线、把 cam 形状导出成 CSV、做轨迹规划分析。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    CamTableID      : MC_CAM_ID;
    ValueSelectMask : UINT; (* MC_ValueSelectType; position, velocity, acceleration, jerk… *)
    StartPosMaster  : LREAL; (* master position of first point *)
    EndPosMaster    : LREAL; (* master position of last point *)
    Increment       : LREAL; (* increment of master position *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次采样读取 |
| `CamTableID` | `MC_CAM_ID` | — | 已加载凸轮表的 ID（`UDINT` 别名）；由 `MC_CamTableSelect` 在加载时分配。该表必须是 motion function 类型 |
| `ValueSelectMask` | `UINT` | — | 选择采样数据类型的位掩码。基于 `MC_ValueSelectType` 枚举累加：选位置一列、速度一列、加速度一列、jerk 一列等。`CamTable` 列数必须与本掩码列数一致：仅位置 → 2 列（主+从位置）；每加一种导数列数 +1 |
| `StartPosMaster` | `LREAL` | — | 主轴起始位置（采样区间下限） |
| `EndPosMaster` | `LREAL` | — | 主轴结束位置（采样区间上限） |
| `Increment` | `LREAL` | — | 主轴位置采样步长。决定输出点密度：步长越小点越多、曲线越平滑、CamTable 数组要求越大 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    CamTable : MC_CAM_REF;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `CamTable` | `MC_CAM_REF` | 接收采样数据的引用结构。`pArray` 指向 PLC 端的数组，FB 把每个主轴位置 + 对应从轴位置（及可选的速度/加速度/jerk）按行写入；行数等于 `(EndPosMaster - StartPosMaster) / Increment + 1`，列数由 `ValueSelectMask` 决定 |

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
| `Done` | `BOOL` | 采样数据成功写入 `CamTable.pArray` 置 `TRUE`；与 `Error` 互斥 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，结束后变 `FALSE`；`Busy = FALSE` 才能接受新命令 |
| `Error` | `BOOL` | 采样过程出错置 `TRUE`，与 `Done` 互斥 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次采样请求——FB 让 NC 用 cam 表内的过渡函数（polynomial / sine 等）在 `[StartPosMaster, EndPosMaster]` 区间按 `Increment` 步长逐点计算从轴位置（以及可选的速度 / 加速度 / jerk），把结果整体写到 `CamTable.pArray` 指向的数组。

**与 `MC_ReadMotionFunction` 的本质区别**：
- `MC_ReadMotionFunction` 读的是 cam 表的**原始节点定义**——主轴位置 X 和从轴位置 Y 是 cam designer 设计时挑的关键点，相邻节点之间靠过渡函数连接
- 本 FB 读的是**插值后的离散化曲线**——按 PLC 给的等距步长把整段曲线"密采样"，每个采样点都是真实运动时从轴会到达的位置

所以本 FB 的输出**直接可用于画曲线图**（HMI 折线图），而 `MC_ReadMotionFunction` 的输出还要在 PLC 内自己做插值才能画出连续曲线。

**`ValueSelectMask` 与列数关系**：基于 `MC_ValueSelectType` 枚举累加，常见组合：
- 仅 Position：列数 = 2（主轴位置 + 从轴位置）
- Position + Velocity：列数 = 3
- Position + Velocity + Acceleration：列数 = 4
- Position + Velocity + Acceleration + Jerk：列数 = 5

**`CamTable` 数据布局**：每行是一个采样点；列含义按 `ValueSelectMask` 顺序排列；PLC 端数组必须声明为相应的二维结构或自定义 row 结构，并且行数 ≥ `(EndPosMaster - StartPosMaster) / Increment + 1`。

**典型用法**：
1. 算出需要的行数和列数，在 PLC 声明对应数组
2. 把 `CamTable.pArray := ADR(arr)`、`nArraySize := SIZEOF(arr)` 填好
3. 上升沿 `Execute`，传起止主轴位置和步长
4. 等 `Done`，从数组取数据画图 / 导出

**典型陷阱**：
- `CamTable` 列数与 `ValueSelectMask` 不匹配 → FB 报错
- 数组容量不够 → 行数算错了导致缓冲溢出风险
- `Increment` 太小 → 数组超大占内存、NC 计算时间长
- `Increment` 太大 → 曲线粗糙，HMI 上看起来折线
- 起止位置不在 cam 表定义范围内 → NC 报参数越界

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出，`ErrorID` 是 TwinCAT NC 错误号（不是 HRESULT）。常见错误类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4Bxx` 段（NC cam 表错） | `CamTableID` 不是 motion function 类型 / `StartPosMaster`/`EndPosMaster` 超出 cam 定义域 / `ValueSelectMask` 与 `CamTable` 列数不匹配 | 确认 cam 表为 motion function；范围在表的主轴起止之间；列数匹配 |
| `16#4260`、`16#4261` 等 | NC 通道命令错（参数检查失败、通道未 ready） | 检查 `Increment > 0`、`StartPosMaster < EndPosMaster`、`pArray` 非空 |

> ⚠️ 待人工确认：PDF 第 7.6 节未列出本 FB 专属的具体错误码值。完整 NC 错误号请参见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys 主题 `E_AxisErrorCodes`。

**清错**：本 FB 自身无 reset 入口；`Error / ErrorID` 在下一次 `Execute` 上升沿自动清零。NC 通道级错误需 `MC_Reset` 清除。

## 5. 使用注意 / 常见坑

- **本 FB 只用于 motion function 类型的 cam 表**：传统点表（pointer table）类型的 cam 不能用；PDF 明确"motion function type"。
- **列数一致是硬约束**：`ValueSelectMask` 选了几个指标，PLC 端数组就要恰好是几列；多 / 少都会报错。
- **`Increment` 选取要权衡**：太小 → 内存爆 / 处理慢；太大 → HMI 看起来粗糙。工程经验：HMI 显示一般 100–500 个采样点足够，按 cam 主轴范围反算 `Increment`。
- **`pArray` 必须是 PLC 内有效内存**：FB 不分配；调用方负责声明并取地址。
- **不能边读边写**：与同表的 `MC_WriteMotionFunction*` 冲突会读到中间状态。
- **`Done` 仅维持到 `Execute` 下降沿**：要把数据用上得在 `Done = TRUE` 的周期内拷走或立即处理。
- **本 FB 不取代 `MC_ReadMotionFunction`**：要拿原始节点定义（做修改后写回）必须用 `MC_ReadMotionFunction` / `MC_ReadMotionFunctionPoint`；本 FB 只给可视化用的离散化数据（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadMotionFunctionValues.TcPOU`](../examples/P_Demo_MC_ReadMotionFunctionValues.TcPOU)

例程演示"HMI 凸轮可视化：把当前生效的 cam 曲线按主轴 0 → 360 度每 1 度采样一次，输出到 PLC 数组供 HMI 画曲线图"。

## 7. 业务场景与实际价值

- **场景**：
  - HMI / SCADA 上画凸轮曲线给操作员看
  - 把当前 cam 形状导出成 CSV / JSON 用于工艺审计
  - 凸轮设计完成后做"轨迹分析"——把速度 / 加速度 / jerk 一起读出来检查是否超机械极限
  - 算法层面要做曲线对比（对比两张 cam 的形状差异）
- **价值**：相比 `MC_ReadMotionFunction` 拿到原始节点再 PLC 内做插值（要自己写过渡函数计算），本 FB 让 NC 内核帮做插值，速度更快、与运行时实际跟随的曲线完全一致。HMI 可视化的唯一干净方案。
- **替代方案对比**：
  - **`MC_ReadMotionFunction` + 自己插值**：要自己实现 polynomial / sine 过渡函数计算，复杂且容易与 NC 实际跟随有微差；本 FB 直接拿权威结果。
  - **离线 cam designer 导出图**：只能看设计时形状，看不到运行时被 `MC_WriteMotionFunction` 改过的实际形状。
  - **本 FB**：运行时可视化和分析的唯一选择。

## 8. 参考资料

- **PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf) §7.6（第 44 页）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460426507.html
- **相关 FB**：`MC_ReadMotionFunction`（读原始节点）、`MC_CamTableSelect`（取 ID）、`MC_CamIn`（激活耦合）
- **相关 DUT**：`MC_CAM_ID`、`MC_CAM_REF`、`MC_ValueSelectType`（位掩码枚举，PDF §8.x）
