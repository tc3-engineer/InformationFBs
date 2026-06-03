# EIB_2OCTET_UNSIGN_REC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187732747.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_2OCTET_UNSIGN_REC.TcPOU`](../examples/P_Demo_EIB_2OCTET_UNSIGN_REC.TcPOU) |

---

## 1. 功能简述

接收 EIB 网络上指定组地址的 **2 字节无符号整数 telegram**，对应 KNX DPT 7.xxx 数据类型。解码结果直接放入 IEC `UINT`（0..65535）。

典型用于亮度（DPT 7.013，lux 单位）、时间间隔（毫秒/秒、DPT 7.003..7.005）、设备运行时长计数器等无负值的 16 位场景。

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
    uiData       : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDataReceive` | `BOOL` | **单周期脉冲信号**：收到 telegram 当 PLC 周期为 TRUE，之后立即回 FALSE。检测时用电平判断会漏掉，必须每周期采样或转上升沿 |
| `uiData` | `UINT` | 收到的负载解码为 IEC `UINT`（0..65535） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：调用即检查，每个 PLC 周期被调用时本 FB 检查 `strData_Rec` 内是否有与 `Group_Address` 匹配的**新到达 telegram**。

**`bDataReceive` 的脉冲语义**：当本 FB 在某 PLC 周期检测到新 telegram 时，`bDataReceive := TRUE` **仅 1 个 PLC 周期**，下个周期自动回 FALSE。这是 EIB 库收发 FB 的**统一约定**——必须用边沿触发或单周期采样，不能写 `IF bDataReceive THEN ... END_IF` 当电平用，否则只有一帧的事件会被多次处理。

**数据有效期**：`uiData` 在收到第一帧之前是 `0`（IEC 默认值）；首次收到 telegram 后保持上一次的值直到下一次更新——也就是**电平保持**。这一点与 `bDataReceive` 的脉冲语义不同。

**与 KL6301 的依赖**：必须先有 `KL6301` 实例配置完成（`bReady = TRUE`）；KL6301 的 `EIB_GROUP_FILTER` 必须包含本 FB 的 `Group_Address`，否则 KL6301 根本不会把该 telegram 收进过程数据，本 FB 永远看不到事件。

**调用次数**：每个 `Group_Address` 每个 PLC 任务**建议只挂一个接收实例**。多个实例监听同一地址会同时触发各自的 `bDataReceive`，不会互相干扰但占内存。

**数据宽度匹配**：发送端 telegram 的负载长度必须与本 FB 类型对应（本 FB 需要 2-byte unsigned int telegram）。类型不匹配的 telegram 会被 KL6301 丢弃（`WRONG_EIB_DATA_LEN`），本 FB 永远收不到。

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
- **16 位无符号 0..65535**：业务量纲超出会回绕（wrap-around）。
- **别用来接收 DPT 8.xxx**（signed），会把 -1 解读成 65535。用对应 `EIB_2OCTET_SIGN_REC`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_2OCTET_UNSIGN_REC.TcPOU`](../examples/P_Demo_EIB_2OCTET_UNSIGN_REC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_2OCTET_UNSIGN_REC
VAR
    fbEIB_2OCTET_UNSIGN_REC        : EIB_2OCTET_UNSIGN_REC;
    stEibRec        : EIB_REC;            // 由 KL6301 提供
    stGroupSensor   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 1);
    uiData          : UINT;
    bGotNewData     : BOOL;
END_VAR

fbEIB_2OCTET_UNSIGN_REC(
    Group_Address := stGroupSensor,
    strData_Rec   := stEibRec,
    bDataReceive  => bGotNewData,
    uiData        => uiData
);
```

## 7. 业务场景与实际价值

- **场景**：亮度传感器、时间间隔、运行时长等 16 位无负值场景
- **价值**：EIB DPT 7.xxx 的标准接收方式；替代手写字节解码
- **替代方案对比**：
  - `EIB_2OCTET_SIGN_REC`：仅 DPT 8 用
  - `EIB_4OCTET_UNSIGN_REC`：32 位无符号场景（DPT 12）
  - 本 FB：DPT 7.xxx 标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187732747.html
- **相关**：`EIB_2OCTET_SIGN_REC`（同库 §4.2.4.2）、`EIB_4OCTET_UNSIGN_REC`（同库 §4.2.4.7，32 位无符号）、`KL6301`
