# EIB_ALL_DATA_TYPES_REC_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187745035.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_ALL_DATA_TYPES_REC_EX.TcPOU`](../examples/P_Demo_EIB_ALL_DATA_TYPES_REC_EX.TcPOU) |

---

## 1. 功能简述

接收 EIB 网络上**所有**进入 `KL6301` 过滤器的 telegram，输出**源组地址 + 原始字节**。与 `EIB_ALL_DATA_TYPES_REC` 的关键区别：本 FB **不需要指定 `Group_Address`**——它「嗅探」所有进入过滤器的 telegram。

用于诊断 / 日志 / 事件归档场景：把整条 EIB 总线上的活动按时间顺序记到 PLC 程序里，每条记录带（时间 + 源组地址 + 原始字节）三元组。配合 KL6301 监控模式（iMode=100）几乎等价于楼宇行业用的 ETS Group Monitor。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    strData_Rec   : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `strData_Rec` | `EIB_REC` | — | 收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例。**本 FB 不需要 `Group_Address`**——会收到所有进入 KL6301 过滤器的 telegram |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bDataReceive     : BOOL;
    Group_Address    : EIB_GROUP_ADDR;
    EIB_Data_Receive : ARRAY [1..14] OF BYTE;
    EIB_Data_Len     : USINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDataReceive` | `BOOL` | **单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期 |
| `Group_Address` | `EIB_GROUP_ADDR` | **telegram 来源的组地址**（区别于 _REC 版本：地址是输入；这里是输出，告诉你刚收到的帧来自哪个地址） |
| `EIB_Data_Receive` | `ARRAY [1..14] OF BYTE` | 原始 EIB 负载字节 |
| `EIB_Data_Len` | `USINT` | 负载长度，编码规则同 `EIB_ALL_DATA_TYPES_REC`：< 8 bit → 1；≥ 8 bit → 字节数 + 1 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：每个 PLC 周期被调用时，本 FB 检查 `strData_Rec` 中是否有**新到达且尚未被本 FB 报告**的 telegram。有就 `bDataReceive := TRUE` 1 个 PLC 周期，并把 telegram 的源组地址、负载、长度填到输出引脚。

**与 `EIB_ALL_DATA_TYPES_REC` 的差异**：
- 不要 `Group_Address` 输入（嗅探所有过滤器内的地址）
- 多出 `Group_Address` 输出（告诉调用方刚收到的 telegram 来自哪个地址）
- 没有 `bEIB_READ` 输出（无法区分 read 请求与普通数据）

**KL6301 过滤器规则不变**：只能接收「过滤器允许进入」的 telegram。要全收必须把 KL6301 设为监控模式 iMode=100。

**与多个 _REC 实例并发**：本 FB 与 `EIB_2OCTET_FLOAT_REC` 等监听同地址的实例**可同时存在**——多个接收 FB 监听同 EIB_REC 时彼此独立，互不影响。本 FB 适合做日志，专用 FB 做业务，两者并存常见。

**调用约束**：每个 PLC 周期调用一次；与 KL6301 同任务；单个 PLC 程序里多实例无冲突。

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
- **没有 `Group_Address` 输入**：从 `EIB_ALL_DATA_TYPES_REC` 迁过来要删除这一行参数。
- **没有 `bEIB_READ`**：要识别 read 请求只能用 `EIB_ALL_DATA_TYPES_REC` 加显式地址。
- **用于做日志记录**：典型用法是把 (timestamp, Group_Address, payload) 推进环形缓冲区。结合 KL6301 监控模式做「PLC 内置 group monitor」。（工程经验补充）
- **KL6301 监控模式（iMode=100）下不发数据**：本 FB 接收没问题，但**不能反向回应**——所以做日志可以，做交互不行。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_ALL_DATA_TYPES_REC_EX.TcPOU`](../examples/P_Demo_EIB_ALL_DATA_TYPES_REC_EX.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_ALL_DATA_TYPES_REC_EX
VAR
    fb         : EIB_ALL_DATA_TYPES_REC_EX;
    stEibRec   : EIB_REC;
    stGroup    : EIB_GROUP_ADDR;
    arrPayload : ARRAY[1..14] OF BYTE;
    usLen      : USINT;
    bNew       : BOOL;
END_VAR
fb(strData_Rec := stEibRec, bDataReceive => bNew,
   Group_Address => stGroup, EIB_Data_Receive => arrPayload,
   EIB_Data_Len => usLen);
```

## 7. 业务场景与实际价值

- **场景**：EIB 总线日志 / 事件归档 / 调试期 group monitor / 不预先知道哪些地址要听
- **价值**：嗅探整条总线，不用为每个地址写一个 _REC 实例；唯一带源地址输出的接收 FB
- **替代方案对比**：
  - 为每个地址挂 `EIB_BIT_REC` / 专用 _REC：业务清晰但代码量爆炸
  - 用 `EIB_ALL_DATA_TYPES_REC` + 多实例分地址：能做，要为每地址传 Group_Address，繁琐
  - 本 _EX：日志 / 调试 / 监控类用例**首选**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.4.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187745035.html
- **相关**：`EIB_ALL_DATA_TYPES_REC`（同库 §4.2.4.10，需指定地址）、`KL6301` iMode=100 监控模式（同库 §4.2.2）、`EIB_REC`（同库 §4.3.2.5）
