# EIB_8BIT_SIGN_REC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187740427.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_8BIT_SIGN_REC.TcPOU`](../examples/P_Demo_EIB_8BIT_SIGN_REC.TcPOU) |

---

## 1. 功能简述

接收 EIB 网络上指定组地址的 **8 位 telegram** 并按 `Scaling_Mode` 自动**缩放**到 IEC `INT`。支持 KNX DPT 5.001（0..100% 百分比）、DPT 5.003（0..360° 角度）、DPT 5.005（0..255 原始字节）三种语义。

缩放在库内部完成——例如发送端发 0xFF (255)，本 FB 在 `Scaling_Mode = 0` 时输出 100；`Scaling_Mode = 1` 时输出 360；`Scaling_Mode = 2` 时输出 255。业务代码直接用 `iData` 数值即可。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    Scaling_Mode  : INT;
    strData_Rec   : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | EIB 组地址（发起方的源地址；**必须出现在 KL6301 过滤器内**），3 级形式 MAIN/SUB_MAIN/NUMBER |
| `Scaling_Mode` | `INT` | — | 缩放模式：`0` = 把 8-bit 解释为 0..100 [%]（DPT 5.001）；`1` = 解释为 0..360 [°]（DPT 5.003 角度）；`2` = 解释为 0..255 byte（DPT 5.005 原始字节）。非法值会让输出 `iData = -1` |
| `strData_Rec` | `EIB_REC` | — | 收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bDataReceive : BOOL;
    iData        : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDataReceive` | `BOOL` | **单周期脉冲信号**：收到 telegram 当 PLC 周期为 TRUE，之后立即回 FALSE。检测时用电平判断会漏掉，必须每周期采样或转上升沿 |
| `iData` | `INT` | 缩放后输出值，含义由 `Scaling_Mode` 决定（见 §3）。返回 `-1` 表示 `Scaling_Mode` 非法 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：调用即检查，每个 PLC 周期被调用时本 FB 检查 `strData_Rec` 内是否有与 `Group_Address` 匹配的**新到达 telegram**。

**`bDataReceive` 的脉冲语义**：当本 FB 在某 PLC 周期检测到新 telegram 时，`bDataReceive := TRUE` **仅 1 个 PLC 周期**，下个周期自动回 FALSE。这是 EIB 库收发 FB 的**统一约定**——必须用边沿触发或单周期采样，不能写 `IF bDataReceive THEN ... END_IF` 当电平用，否则只有一帧的事件会被多次处理。

**数据有效期**：`iData` 在收到第一帧之前是 `0`（IEC 默认值）；首次收到 telegram 后保持上一次的值直到下一次更新——也就是**电平保持**。这一点与 `bDataReceive` 的脉冲语义不同。

**与 KL6301 的依赖**：必须先有 `KL6301` 实例配置完成（`bReady = TRUE`）；KL6301 的 `EIB_GROUP_FILTER` 必须包含本 FB 的 `Group_Address`，否则 KL6301 根本不会把该 telegram 收进过程数据，本 FB 永远看不到事件。

**调用次数**：每个 `Group_Address` 每个 PLC 任务**建议只挂一个接收实例**。多个实例监听同一地址会同时触发各自的 `bDataReceive`，不会互相干扰但占内存。

**数据宽度匹配**：发送端 telegram 的负载长度必须与本 FB 类型对应（本 FB 需要 1 byte (8-bit) telegram）。类型不匹配的 telegram 会被 KL6301 丢弃（`WRONG_EIB_DATA_LEN`），本 FB 永远收不到。

**`Scaling_Mode` 处理**：库读到 8-bit 值 `raw` (0..255) 后：
- `Scaling_Mode = 0` → `iData := raw * 100 / 255`（百分比，0..100）
- `Scaling_Mode = 1` → `iData := raw * 360 / 255`（角度，0..360）
- `Scaling_Mode = 2` → `iData := raw`（原始 byte，0..255）
- 其它 `Scaling_Mode` 值 → `iData := -1` 标记错误（PDF §4.2.4.8 Outputs 注释）

## 4. 错误码 / 返回值

本 FB 自身**没有 `bError` / `iErrorID` 输出**——错误统一由 `KL6301` FB 通过 `str_Data_Rec` 内部的 `Rec_iErrorID` 字段透传：若收到了不符长度的 telegram（例：用 `EIB_2OCTET_*` 接收 1-byte telegram）→ `KL6301.iErrorId := WRONG_EIB_DATA_LEN (20)`，本 FB 不会上送数据。

完整错误码见 `KL6301` 文档 §4 或 `EIB_ERROR_CODE` 枚举（同库 §4.3.1.1）。

额外：本 FB 看到非法 `Scaling_Mode`（不是 0/1/2）时 `iData = -1`，但不会触发 KL6301 的 `bError`。调用方代码里应自查 `Scaling_Mode` 是否合法。

## 5. 使用注意 / 常见坑

- **`bDataReceive` 是脉冲信号，1 个 PLC 周期就回 FALSE**：检测必须用上升沿或单周期采样，写 `IF bDataReceive THEN x := y; END_IF` 会因为脉冲太短在高周期任务里偶尔丢事件。建议跟 `R_TRIG` 配合使用。
- **`Group_Address` 不在 KL6301 过滤器内 → 永远收不到**：检查 `KL6301.EIB_GROUP_FILTER[]` 是否覆盖。监控模式 iMode=100 例外。
- **`strData_Rec` 必须传 KL6301 的 `str_Data_Rec` 同一个实例**：传错 / 没传 / 传到其它 KL6301 实例的 EIB_REC 都会「不工作但不报错」。
- **必须与 KL6301 在同一 PLC 任务**：跨任务时 EIB_REC 状态不一致，收不到。
- **首次收 telegram 前数据值是 0**：业务逻辑别在启动就直接读，先等 `bDataReceive` 至少跳过一次。（工程经验补充）
- **EIB 长帧理论 EOT 时间 ≤ 100 ms**：如果两个发起方在 100 ms 内同时往同一组地址发，KL6301 只会收到先到的；另一帧若被丢，目标方 `bDataReceive` 不会出来。这是 EIB TP1 总线物理特性，不是本 FB 问题。（工程经验补充）
- **`Scaling_Mode` 决定输出语义**：发送端按哪种 DPT 发，接收端就必须填对应 mode。混用结果是数字仍出来但含义不对。
- **`iData = -1` 表示 mode 非法**——业务代码每次取值前可加 `IF iData &lt; 0 THEN report_error END_IF` 自检。
- **0..100% 实际有量化误差**：raw 255 = 100，raw 254 ≈ 99，**步长约 0.39% 而不是 1%**。要精确百分比的话别用 DPT 5.001，用 DPT 9.x（2-byte float）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_8BIT_SIGN_REC.TcPOU`](../examples/P_Demo_EIB_8BIT_SIGN_REC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_8BIT_SIGN_REC
VAR
    fb           : EIB_8BIT_SIGN_REC;
    stEibRec     : EIB_REC;
    stGroup      : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 4);
    iPct         : INT;
    bNew         : BOOL;
END_VAR
fb(Group_Address := stGroup, Scaling_Mode := 0,
   strData_Rec := stEibRec, bDataReceive => bNew, iData => iPct);
```

## 7. 业务场景与实际价值

- **场景**：DPT 5.001/5.003/5.005 8-bit 缩放场景：调光百分比、角度、原始字节
- **价值**：自动缩放无需手写公式；DPT 5.xxx 标准接收方式
- **替代方案对比**：
  - `EIB_8BIT_UNSIGN_REC`：纯字节（0..255），不缩放
  - `EIB_2OCTET_UNSIGN_REC`：16-bit 精度更高
  - 本 FB：DPT 5.001/003/005 的**标准**选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.4.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187740427.html
- **相关**：`EIB_8BIT_UNSIGN_REC`（同库 §4.2.4.9，原始字节）、`EIB_8BIT_SIGN_SEND`（同库 §4.2.5.15，对应发送端）
