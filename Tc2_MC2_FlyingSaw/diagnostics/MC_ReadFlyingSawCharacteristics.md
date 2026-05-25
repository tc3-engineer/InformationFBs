# MC_ReadFlyingSawCharacteristics

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_FlyingSaw` |
| Library Version | `1.6.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Flying saw` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/1004094731.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadFlyingSawCharacteristics.xml`](../examples/P_Demo_MC_ReadFlyingSawCharacteristics.xml) |

---

## 1. 功能简述

读取通用飞锯（Universal Flying Saw）**同步阶段特征值**的功能块（Function Block, FB）。`Execute` 上升沿触发后，从 TwinCAT NC 读取本次飞锯同步生成的轮廓特征数据，结果写入 `CamTableCharac`（类型 `MC_FlyingSawCharacValues`）结构，包含同步起止点的主/从位置、速度、加速度、Jerk，以及同步过程中从轴位置/速度/加速度的最大最小极值等。

这些特征值用于**校核同步轮廓是否在机械允许范围内**：例如检查从轴在同步段是否超过了允许的最大速度/加速度，或位置是否越过软限位。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次从 TwinCAT NC 读取特征值 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Slave          : AXIS_REF;
    CamTableCharac : MC_FlyingSawCharacValues;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Slave` | `AXIS_REF` | 从轴数据结构（特征值是针对该从轴的同步轮廓计算的） |
| `CamTableCharac` | `MC_FlyingSawCharacValues` | 输出特征值的结构体；读取成功后由本 FB 填充（结构字段含义见 `MC_FlyingSawCharacValues` 文档） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done    : BOOL;
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 数据集成功读取后置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 触发后置 `TRUE`，命令处理期间保持；变 `FALSE` 即可接新命令，同时 `Done` 或 `Error` 被置位 |
| `Error` | `BOOL` | 发生错误时置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号 |

## 3. 行为说明

**触发与时序**：`Execute` 上升沿启动读取，`Busy` 立即置 `TRUE`，FB 向 TwinCAT NC 请求当前从轴飞锯同步的特征值。读取成功后 `Busy` 落下、`Done` 置 `TRUE`，`CamTableCharac` 被填入计算结果；若出错则 `Error` 置 `TRUE` 并由 `ErrorID` 给出错误号。标准用法是触发后在 `NOT Busy` 时把 `Execute` 写回 `FALSE` 复位边沿。

**数据可用时机（关键）**：特征值是 NC 在飞锯**启动后**才计算出来的——PDF 明确"在通用飞锯启动之前，计算出的数据不可用"。因此本 FB 必须在已经建立飞锯耦合（`MC_GearInVelo` / `MC_GearInPos` 同步开始）之后再调用读取，否则读不到有效数据。

**典型用途**：调试阶段读出 `CamTableCharac.fSlaveVeloMax` / `fSlaveAccMax` 等极值，确认同步轮廓没有超过从轴机械极限；或读出同步起止位置用于诊断/记录。结构字段的逐项含义见 `MC_FlyingSawCharacValues` 文档。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC / 飞锯错误号。

| 输出 | 类型 | 含义 |
|---|---|---|
| `Error` | `BOOL` | 发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | 错误号；飞锯尚未启动（特征值未计算）、从轴状态不满足等会反映在此 |

⚠️ PDF 在本 FB 章节未逐条列出 `ErrorID` 数值含义。完整错误码见 TF5055 飞锯手册的 Error Codes 主题。

## 5. 使用注意 / 常见坑

- **飞锯没启动就读会读不到**：特征值在飞锯同步启动后才由 NC 计算出来，过早调用拿不到有效数据。先建立 `MC_GearInVelo`/`MC_GearInPos` 同步再读。
- **`CamTableCharac` 是 VAR_IN_OUT 必须传引用**：要传入一个 `MC_FlyingSawCharacValues` 实例供 FB 填写，不能只声明不传。
- **`Slave` 也是 VAR_IN_OUT 必须传引用**：特征值是针对该从轴的同步轮廓算的。
- **边沿触发**：每次想刷新特征值都要新的 `Execute` 上升沿。
- **极值字段读出后自行比对机械限值**：本 FB 只给数据，不替你判断是否超限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadFlyingSawCharacteristics.xml`](../examples/P_Demo_MC_ReadFlyingSawCharacteristics.xml)

```iecst
// 场景：飞锯调试，建立同步后读出本次同步轮廓的从轴速度/加速度极值，确认没超机械极限
PROGRAM P_Demo_MC_ReadFlyingSawCharacteristics
VAR
    fbReadCharac    : MC_ReadFlyingSawCharacteristics;
    axisCrossSaw    : AXIS_REF;                  // 从轴（已建立飞锯同步）
    charValues      : MC_FlyingSawCharacValues;  // 输出特征值结构
    bReadReq        : BOOL;
    rtRead          : R_TRIG;
    bDone           : BOOL;
    bBusy           : BOOL;
    bErr            : BOOL;
    nErrID          : UDINT;
    fSlaveVeloMax   : LREAL;                      // 监视：同步段从轴最大速度
END_VAR

rtRead(CLK := bReadReq);
fbReadCharac(
    Execute        := rtRead.Q,
    Slave          := axisCrossSaw,
    CamTableCharac := charValues,
    Done           => bDone,
    Busy           => bBusy,
    Error          => bErr,
    ErrorID        => nErrID
);
IF bDone THEN
    fSlaveVeloMax := charValues.fSlaveVeloMax;   // 读出极值供后续比对
END_IF;
IF NOT bBusy THEN
    bReadReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：飞锯/横切的投产前校核、在线诊断同步轮廓、记录每次同步的起止点与极值用于追溯、自适应调参（根据极值反向调整速比或同步窗口）。
- **价值**：不用本 FB 时无法从 PLC 侧拿到 NC 计算的同步轮廓内部特征，只能盲调；本 FB 把整套特征值（30+ 字段）一次性读出，让 PLC 能定量判断同步是否健康、是否逼近机械极限。
- **替代方案对比**：
  - 自己用 ADS 读 NC cam-table 内部数据：底层、易错、需知 NC 内部参数地址
  - **本 FB**：飞锯特征值读取的官方封装，配合 `MC_FlyingSawCharacValues` 结构使用

## 8. 参考资料

- **PDF**：[TF5055_TC3_NC_Flying_Saw_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf) §5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/1004094731.html
- **相关 FB / DUT**：`MC_FlyingSawCharacValues`（特征值结构定义）、`MC_GearInVelo` / `MC_GearInPos`（建立飞锯同步）
