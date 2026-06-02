# MC_ReadMotionFunction

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Camming` |
| Library Version | `1.9.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460418827.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadMotionFunction.TcPOU`](../examples/P_Demo_MC_ReadMotionFunction.TcPOU) |

---

## 1. 功能简述

运行时**读取凸轮表（cam plate / motion function）数据**的功能块。读取的对象是已经加载进 NC（Motion Control 内核）的某张凸轮表，按表 ID（`MC_CAM_ID`）定位；可以一次性把整张表所有插值点（interpolation point）读回 PLC，也可以从某个 `PointID` 开始只读 `NumPoints` 个点。

读回的数据通过 VAR_IN_OUT 的 `CamTable : MC_CAM_REF` 结构传递——`MC_CAM_REF` 携带一个指向 PLC 侧数据数组的指针 `pArray` 以及数组容量、行/列数等元信息；本 FB 只往该数组写数据，**不会扩容**，调用方必须保证数组足够大。

常用于"把 NC 内已激活的凸轮形状回读到 PLC，再做可视化 / 备份 / 校验" 这类场景；与离线 cam designer（TwinCAT XAE 工具里画 cam）相比，本 FB 的优势是在 PLC 运行中能动态拿到当前生效的凸轮数据。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute    : BOOL;
    CamTableID : MC_CAM_ID;
    PointID    : MC_MotionFunctionPoint_ID;
    NumPoints  : UDINT; (* 0 = fill MFsize *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次读取；读取期间不需保持高电平 |
| `CamTableID` | `MC_CAM_ID` | — | 已加载凸轮表的 ID（`UDINT` 别名）。该 ID 由 `MC_CamTableSelect` 在加载凸轮表时分配；ID 在 NC 通道范围内唯一 |
| `PointID` | `MC_MotionFunctionPoint_ID` | — | 第一个要读取的插值点 ID；从该 ID 开始按表内顺序往后读 |
| `NumPoints` | `UDINT` | — | 要读取的点数。填 `0` 表示按 `CamTable.MFsize` 自动填满（一次性读整张表的常用写法） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    CamTable : MC_CAM_REF;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `CamTable` | `MC_CAM_REF` | 凸轮表数据的引用结构。包含数据数组指针 `pArray`、容量 `nArraySize`、当前点数 `MFsize`、列数等字段；本 FB 把读出的点写入 `pArray` 指向的内存，并把实际写入的点数返回到 `NumPointsRead` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done          : BOOL;
    Busy          : BOOL;
    Error         : BOOL;
    ErrorID       : UDINT;
    NumPointsRead : UDINT; (* return value <= NumPoints *)
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `Done` | `BOOL` | 数据成功读取完成时置 `TRUE`，与 `Error` 互斥 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，命令处理完成（无论 Done / Error）后变 `FALSE`；`Busy = FALSE` 才能接受新命令 |
| `Error` | `BOOL` | 读取过程中发生错误置 `TRUE`，与 `Done` 互斥 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号；具体编码参见 §4 |
| `NumPointsRead` | `UDINT` | 实际读出的点数，**不大于** `NumPoints`；当 `NumPoints = 0` 时返回整表实际点数 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次读取——FB 内部向 NC 发起异步请求，从指定 `CamTableID` 的表里、从 `PointID` 开始、读 `NumPoints` 个点。请求被 NC 接受后 `Busy := TRUE`，读取完成置 `Done := TRUE`、`Busy := FALSE`，并把实际读出的点数写到 `NumPointsRead`。

**异步特性**：读取经 NC ADS 通道进行，不是当前周期立刻完成的同步调用；典型耗时 1–N 个 PLC 周期（取决于点数、NC 负载）。PLC 必须**周期性调用本 FB 实例**（同一个实例、同样的输入引脚），等 `Done = TRUE` 才能拿 `CamTable.pArray` 里的数据；不能 `Execute := TRUE` 一次就 `Execute := FALSE` 后立刻读数据。

**整表读 vs 部分读**：把 `PointID` 设为表内第一个点的 ID、`NumPoints := 0` 即读整张表（按 `MFsize` 自动定长）。要读"从第 N 个点开始的 K 个点"则显式指定 `PointID` 和 `NumPoints`，常用于分批回读大表（避免一次拷贝过大数组阻塞周期）。

**`CamTable` 数组容量要求**：本 FB 只往 `CamTable.pArray` 指向的 PLC 内存写数据，**不分配也不扩容**。如果 `NumPoints` 大于 `CamTable.nArraySize`，行为未定义/会报错。调用前必须保证 PLC 侧数组足够装下要读的点数。

**典型用法**：
1. 在 PLC 中声明一块足够大的 `ARRAY[0..N-1] OF MC_MotionFunctionPoint`（或 PDF 第 8.4 节定义的相应行类型）
2. 把 `CamTable.pArray := ADR(arrPoints)`，`CamTable.nArraySize := SIZEOF(arrPoints)` 等字段填好
3. 用 `MC_CamTableSelect` 取得 `CamTableID`，把它传入本 FB
4. 上升沿 `Execute`，等 `Done`，从 `arrPoints[0 .. NumPointsRead-1]` 取数据

**典型陷阱**：忘了在调用前初始化 `CamTable.pArray` 和容量字段；用错的 `CamTableID`（比如 `MC_CamTableSelect` 还没 Done 就先用它的 `CamTableID`）；不周期调用 FB 实例导致永远拿不到 `Done`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出，`ErrorID` 是 TwinCAT NC 错误号（不是 HRESULT）。常见错误类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4Bxx` 段（NC cam 表错） | `CamTableID` 无效 / 表未加载 / `PointID` 越界 / `NumPoints` 超过表 size | 确认 `MC_CamTableSelect` 已 `Done`、`CamTableID` 与该表对应；检查 `PointID` 在 `[0, MFsize-1]` 范围内 |
| `16#4260`、`16#4261` 等 | NC 通道命令错（参数检查失败、通道未 ready） | 检查 NC 通道状态；`CamTable.nArraySize` 是否够大、`pArray` 是否非空 |

> ⚠️ 待人工确认：PDF 第 7.1 节未列出本 FB 专属的具体错误码值。完整 NC 错误号请参见 `Tc2_MC2` PDF 附录《Overview of axis error codes》或 InfoSys 主题 `E_AxisErrorCodes`。

**清错**：本 FB 自身无 reset 入口；`Error / ErrorID` 在下一次 `Execute` 上升沿自动清零。NC 通道级错误需 `MC_Reset` 清除。

## 5. 使用注意 / 常见坑

- **`CamTable.pArray` 必须先指向 PLC 内有效的数组内存**：本 FB 不分配数组。常见忘了写 `CamTable.pArray := ADR(arr)` 直接 `Execute`，结果指针为 0 → NC 报错或写坏内存。
- **`CamTable.nArraySize` 必须 ≥ 要读取的字节数**：以字节为单位，不是元素个数；用 `SIZEOF(arr)` 取。
- **不能一边读一边写同一张 cam 表**：另一实例同时跑 `MC_WriteMotionFunction` / `MC_WriteMotionFunctionPoint` 会导致回读到的是混合状态。
- **`CamTableID` 必须先由 `MC_CamTableSelect` 准备好**：直接传一个 `UDINT` 数字不行，必须是 NC 已注册的表 ID（工程经验补充）。
- **`NumPoints := 0` 用法**：是"读整张表"的官方简写；点数会自动按 `MFsize` 填好，比手动算更安全。
- **不要在多任务中复用同一 FB 实例**：cam 表 FB 实例不是可重入的，多任务并发调用会乱序触发。
- **`Done` 仅维持到 `Execute` 下降沿**：`Execute := FALSE` 后 `Done` 也会清零，要用 `Done` 数据先拷贝走再降沿。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadMotionFunction.TcPOU`](../examples/P_Demo_MC_ReadMotionFunction.TcPOU)

例程演示"包装机料厚自适应：先读出当前生效的凸轮表点列，备份到 PLC 数组以便后续 HMI 显示/重算"。

## 7. 业务场景与实际价值

- **场景**：包装机 / 印刷机 / 卷绕机里凸轮表已经在跑（通过 `MC_CamTableSelect` + `MC_CamIn` 激活），HMI 要把当前生效的凸轮曲线显示给操作员看；或在做"料厚自适应"——读出原 cam 形状作为基准，叠加偏移后再写回。
- **价值**：不用 OPC 出 NC 内部数据、也不用切回 XAE 离线工具，PLC 程序里一行调用就能把 NC 当前生效的 cam 形状全量拿回来，做可视化、备份、版本对比、参数化整形。
- **替代方案对比**：
  - **离线 cam designer 文件**：能拿到工程设计时的 cam，**拿不到运行时被 `MC_WriteMotionFunction` 改过的当前形状**；本 FB 是运行时真实状态的唯一来源。
  - **`MC_ReadMotionFunctionValues`**：返回的是"按主轴位置等距离散化"的插值结果（适合画曲线图），不是原始插值点；本 FB 拿的是 NC 内部存的**原始 motion function 点**（节点定义）。
  - **`MC_ReadMotionFunctionPoint`**：单点读，灵活但点多时多次调用低效；本 FB 一次批读更快。

## 8. 参考资料

- **PDF**：[TF5050_TC3_NC_Camming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf) §7.1（第 35 页）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclibmc2_camming/460418827.html
- **相关 FB**：`MC_CamTableSelect`（加载 cam 取得 ID）、`MC_CamIn`（激活耦合）、`MC_WriteMotionFunction`（写整段）、`MC_ReadMotionFunctionPoint`（单点读）、`MC_ReadMotionFunctionValues`（离散化读）
- **相关 DUT**：`MC_CAM_ID`、`MC_CAM_REF`、`MC_MotionFunctionPoint_ID`、`MC_MotionFunctionPoint`（PDF §8.x）
