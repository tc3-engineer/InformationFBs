# EIB_ALL_DATA_TYPES_REC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187743499.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_ALL_DATA_TYPES_REC.TcPOU`](../examples/P_Demo_EIB_ALL_DATA_TYPES_REC.TcPOU) |

---

## 1. 功能简述

接收 EIB 网络上指定组地址的 **任意类型** telegram，把负载以**原始字节数组**形式输出，调用方自己解码。比所有专门类型 FB 更灵活——一个组地址可能有多种 DPT 数据，或对端 DPT 不在标准列表里，本 FB 都能收。

**对比专门 FB**：`EIB_2OCTET_FLOAT_REC` 等会按特定 DPT 长度过滤——长度不符会被丢；本 FB 不过滤长度。**对比 `EIB_ALL_DATA_TYPES_REC_EX`**：本 FB 必须先指定 `Group_Address`，只接该地址；EX 版本不需要地址，接全部进入过滤器的 telegram，附带源地址输出。

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
    bDataReceive     : BOOL;
    EIB_Data_Receive : ARRAY [1..14] OF BYTE;
    EIB_Data_Len     : USINT;
    bEIB_READ        : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDataReceive` | `BOOL` | **单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期 |
| `EIB_Data_Receive` | `ARRAY [1..14] OF BYTE` | 原始 EIB 负载字节，从 `[1]` 开始填。库不解码，业务自己解释 |
| `EIB_Data_Len` | `USINT` | 负载长度。规则：负载 < 8 bit 时 `EIB_Data_Len = 1`；负载 ≥ 8 bit 时 `EIB_Data_Len = 字节数 + 1`。PDF 举例：收 1 bit 数据 → len 1；收 2 byte 数据 → len 3 |
| `bEIB_READ` | `BOOL` | 区分 telegram 类型：`TRUE` = 这是 EIB Read 命令（来自 `EIB_READ_SEND` 或其它 read_group_req）；`FALSE` = 普通数据 telegram。本字段自 V3.3.5.0 起可用（PDF §4.2.4.10） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：调用即检查，每个 PLC 周期被调用时本 FB 检查 `strData_Rec` 内是否有与 `Group_Address` 匹配的**新到达 telegram**。

**`bDataReceive` 的脉冲语义**：当本 FB 在某 PLC 周期检测到新 telegram 时，`bDataReceive := TRUE` **仅 1 个 PLC 周期**，下个周期自动回 FALSE。这是 EIB 库收发 FB 的**统一约定**——必须用边沿触发或单周期采样，不能写 `IF bDataReceive THEN ... END_IF` 当电平用，否则只有一帧的事件会被多次处理。

**数据有效期**：`EIB_Data_Receive[]` 在收到第一帧之前是 `0`（IEC 默认值）；首次收到 telegram 后保持上一次的值直到下一次更新——也就是**电平保持**。这一点与 `bDataReceive` 的脉冲语义不同。

**与 KL6301 的依赖**：必须先有 `KL6301` 实例配置完成（`bReady = TRUE`）；KL6301 的 `EIB_GROUP_FILTER` 必须包含本 FB 的 `Group_Address`，否则 KL6301 根本不会把该 telegram 收进过程数据，本 FB 永远看不到事件。

**调用次数**：每个 `Group_Address` 每个 PLC 任务**建议只挂一个接收实例**。多个实例监听同一地址会同时触发各自的 `bDataReceive`，不会互相干扰但占内存。

**数据宽度匹配**：发送端 telegram 的负载长度必须与本 FB 类型对应（任意长度，从 1 bit 到 14 byte 都行）。类型不匹配的 telegram 会被 KL6301 丢弃（`WRONG_EIB_DATA_LEN`），本 FB 永远收不到。

**`EIB_Data_Len` 编码规则**（PDF §4.2.4.10 Outputs 表）：
- 负载 < 8 bit → `EIB_Data_Len = 1`
- 负载 ≥ 8 bit → `EIB_Data_Len = 字节数 + 1`
举例：收 1 bit 数据 → `EIB_Data_Len = 1`；收 2 byte 数据 → `EIB_Data_Len = 3`。
**注意**：这与「正常字节计数 + 1」不直观，是历史协议遗留——使用时建议把它当作「已用 BYTE 数」的索引上限来记。

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
- **`EIB_Data_Len` 编码不直观**：1 bit 数据 len = 1（不是 0），2 byte 数据 len = 3（不是 2）。读 PDF §4.2.4.10 末段表确认。
- **`bEIB_READ` 区分 read 请求 vs 普通数据**：网络上有别人调 `EIB_READ_SEND` 请求本地址的数据时本 FB 会同时收到，用 `bEIB_READ = TRUE` 区分。如果业务上要「被读到时主动答」，需要看本字段。
- **用本 FB 接专门类型时损失抽象**：能用 `EIB_2OCTET_FLOAT_REC` 就别用本 FB——专门 FB 已经做了解码，业务代码更清楚。本 FB 适合**异构数据 / 非标 DPT**。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_ALL_DATA_TYPES_REC.TcPOU`](../examples/P_Demo_EIB_ALL_DATA_TYPES_REC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_ALL_DATA_TYPES_REC
VAR
    fb         : EIB_ALL_DATA_TYPES_REC;
    stEibRec   : EIB_REC;
    stGroup    : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 20);
    arrPayload : ARRAY[1..14] OF BYTE;
    usLen      : USINT;
    bIsRead    : BOOL;
    bNew       : BOOL;
END_VAR
fb(Group_Address := stGroup, strData_Rec := stEibRec,
   bDataReceive => bNew, EIB_Data_Receive => arrPayload,
   EIB_Data_Len => usLen, bEIB_READ => bIsRead);
```

## 7. 业务场景与实际价值

- **场景**：非标 DPT / 私有协议 / 变长 telegram / 需要识别 EIB read 请求
- **价值**：比专用 FB 灵活；唯一支持识别 EIB read 命令的接收 FB
- **替代方案对比**：
  - 所有专用 `EIB_*_REC` FB：能用就用，业务代码清晰
  - `EIB_ALL_DATA_TYPES_REC_EX`：不指定地址收全部
  - 本 FB：异构 DPT、识别 read 请求时必选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.4.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187743499.html
- **相关**：`EIB_ALL_DATA_TYPES_REC_EX`（同库 §4.2.4.11，不指定地址）、`EIB_ALL_DATA_TYPES_SEND`（同库 §4.2.5.19，配套发送端）、`EIB_READ_SEND`（同库 §4.2.5.27，对应的 read 命令）
