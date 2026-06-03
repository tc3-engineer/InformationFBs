# EIB_BIT_CONTROL_REC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187746571.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_BIT_CONTROL_REC.TcPOU`](../examples/P_Demo_EIB_BIT_CONTROL_REC.TcPOU) |

---

## 1. 功能简述

接收 EIB **2-bit Controlled telegram**（DPT 2.xxx：带优先级控制的 1-bit 数据）：1 位控制 + 1 位数据。对应 KNX「安全 / 应急覆盖」语义——比如普通开关 + 应急按钮共用一个组地址，应急按钮的命令 `bControl = TRUE` 强制覆盖普通命令。

**DPT 2.001 示例**：普通开关发 `bControl = FALSE, bValue = TRUE`（请求开灯）；应急按钮发 `bControl = TRUE, bValue = FALSE`（强制关灯，不可被覆盖）。设备解释 `bControl` 决定是否优先。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    strData_Rec   : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | EIB 组地址（发起方的源地址；**必须出现在 KL6301 过滤器内**），3 级形式 MAIN/SUB_MAIN/NUMBER |
| `strData_Rec` | `EIB_REC` | — | 收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bDataReceive : BOOL;
    bControl     : BOOL;
    bValue       : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDataReceive` | `BOOL` | **单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期 |
| `bControl` | `BOOL` | 控制位（TRUE/FALSE）。在 DPT 2.001 (Switch_Control) 中 = 强制优先级位（TRUE = 强制生效） |
| `bValue` | `BOOL` | 数据位（TRUE/FALSE）。在 DPT 2.001 中 = 实际开关值（TRUE = ON、FALSE = OFF） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：调用即检查，每个 PLC 周期被调用时本 FB 检查 `strData_Rec` 内是否有与 `Group_Address` 匹配的**新到达 telegram**。

**`bDataReceive` 的脉冲语义**：当本 FB 在某 PLC 周期检测到新 telegram 时，`bDataReceive := TRUE` **仅 1 个 PLC 周期**，下个周期自动回 FALSE。这是 EIB 库收发 FB 的**统一约定**——必须用边沿触发或单周期采样，不能写 `IF bDataReceive THEN ... END_IF` 当电平用，否则只有一帧的事件会被多次处理。

**数据有效期**：`bControl + bValue` 在收到第一帧之前是 `0`（IEC 默认值）；首次收到 telegram 后保持上一次的值直到下一次更新——也就是**电平保持**。这一点与 `bDataReceive` 的脉冲语义不同。

**与 KL6301 的依赖**：必须先有 `KL6301` 实例配置完成（`bReady = TRUE`）；KL6301 的 `EIB_GROUP_FILTER` 必须包含本 FB 的 `Group_Address`，否则 KL6301 根本不会把该 telegram 收进过程数据，本 FB 永远看不到事件。

**调用次数**：每个 `Group_Address` 每个 PLC 任务**建议只挂一个接收实例**。多个实例监听同一地址会同时触发各自的 `bDataReceive`，不会互相干扰但占内存。

**数据宽度匹配**：发送端 telegram 的负载长度必须与本 FB 类型对应（2 bit telegram）。类型不匹配的 telegram 会被 KL6301 丢弃（`WRONG_EIB_DATA_LEN`），本 FB 永远收不到。

**位分配**（PDF §4.2.4.12 末段）：2 个 bit 按高到低 = [`bControl`, `bValue`]。

## 4. 错误码 / 返回值

本 FB 自身**没有 `bError` / `iErrorID` 输出**——错误统一由 `KL6301` FB 通过 `str_Data_Rec` 内部的 `Rec_iErrorID` 字段透传：若收到了不符长度的 telegram（例：用 `EIB_2OCTET_*` 接收 1-byte telegram）→ `KL6301.iErrorId := WRONG_EIB_DATA_LEN (20)`，本 FB 不会上送数据。

完整错误码见 `KL6301` 文档 §4 或 `EIB_ERROR_CODE` 枚举（同库 §4.3.1.1）。

## 5. 使用注意 / 常见坑

- **`bDataReceive` 是脉冲信号，1 个 PLC 周期就回 FALSE**：检测必须用上升沿或单周期采样，写 `IF bDataReceive THEN x := y; END_IF` 会因为脉冲太短在高周期任务里偶尔丢事件。建议跟 `R_TRIG` 配合使用。
- **`Group_Address` 不在 KL6301 过滤器内 → 永远收不到**：检查 `KL6301.EIB_GROUP_FILTER[]` 是否覆盖。监控模式 iMode=100 例外。
- **`strData_Rec` 必须传 KL6301 的 `str_Data_Rec` 同一个实例**：传错 / 没传 / 传到其它 KL6301 实例的 EIB_REC 都会「不工作但不报错」。
- **必须与 KL6301 在同一 PLC 任务**：跨任务时 EIB_REC 状态不一致，收不到。
- **首次收 telegram 前数据值是 0**：业务逻辑别在启动就直接读，先等 `bDataReceive` 至少跳过一次。（工程经验补充）
- **EIB 长帧理论 EOT 时间 ≤ 100 ms**：如果两个发起方在 100 ms 内同时往同一组地址发，KL6301 只会收到先到的；另一帧若被丢，目标方 `bDataReceive` 不会出来。这是 EIB TP1 总线物理特性，不是本 FB 问题。（工程经验补充）
- **`bControl` = 优先级 / 强制位**：DPT 2.xxx 的语义是「控制位为 TRUE 表示这条命令必须执行不可被普通指令覆盖」。
- **与 1-bit `EIB_BIT_REC` 区别**：1 bit 是单纯开关，没有优先级概念；本 FB 多 1 位优先级。混用会出现意外的覆盖关系。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_BIT_CONTROL_REC.TcPOU`](../examples/P_Demo_EIB_BIT_CONTROL_REC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_BIT_CONTROL_REC
VAR
    fb       : EIB_BIT_CONTROL_REC;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 30);
    bCtl     : BOOL;
    bVal     : BOOL;
    bNew     : BOOL;
END_VAR
fb(Group_Address := stGroup, strData_Rec := stEibRec,
   bDataReceive => bNew, bControl => bCtl, bValue => bVal);
```

## 7. 业务场景与实际价值

- **场景**：带优先级的 KNX 1-bit 控制：应急关闭、安全联锁覆盖普通操作
- **价值**：替代手写 2-bit 解码 + 优先级状态机；DPT 2.xxx 语义直接对应
- **替代方案对比**：
  - `EIB_BIT_REC` 简单 1 bit：失去优先级语义
  - `EIB_3BIT_CONTROL_REC`：调光 / 步进，不是开关
  - 本 FB：DPT 2.xxx 标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.4.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187746571.html
- **相关**：`EIB_BIT_REC`（同库 §4.2.4.13，简单 1 bit）、`EIB_BIT_CONTROL_SEND`（同库 §4.2.5.20，对应发送端）、`EIB_3BIT_CONTROL_REC`（同库 §4.2.4.4，4-bit 调光控制）
