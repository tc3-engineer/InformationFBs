# EIB_TIME_REC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187751179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_TIME_REC.TcPOU`](../examples/P_Demo_EIB_TIME_REC.TcPOU) |

---

## 1. 功能简述

接收 EIB 网络上指定组地址的 **3 字节时间 telegram**（DPT 10.001），解码到三个 IEC `WORD` 变量（时 0..23、分 0..59、秒 0..59）。

**PDF 拼写错**：PDF 把小时输出引脚命名为 `wHoure`（多个 e）——典型 PDF/原始库的拼写错。本文档保留 PDF 原写法以便代码逐字对照。IEC 实际访问就是 `fb.wHoure`。

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
    wHoure       : WORD;
    wMinute      : WORD;
    wSecond      : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDataReceive` | `BOOL` | **单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期 |
| `wHoure` | `WORD` | 小时，0..23。**PDF 引脚名拼写错为 `wHoure`**（应是 wHour），与 IEC 实际声明一致，逐字保留 |
| `wMinute` | `WORD` | 分钟，0..59 |
| `wSecond` | `WORD` | 秒，0..59 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：调用即检查，每个 PLC 周期被调用时本 FB 检查 `strData_Rec` 内是否有与 `Group_Address` 匹配的**新到达 telegram**。

**`bDataReceive` 的脉冲语义**：当本 FB 在某 PLC 周期检测到新 telegram 时，`bDataReceive := TRUE` **仅 1 个 PLC 周期**，下个周期自动回 FALSE。这是 EIB 库收发 FB 的**统一约定**——必须用边沿触发或单周期采样，不能写 `IF bDataReceive THEN ... END_IF` 当电平用，否则只有一帧的事件会被多次处理。

**数据有效期**：`wHoure/wMinute/wSecond` 在收到第一帧之前是 `0`（IEC 默认值）；首次收到 telegram 后保持上一次的值直到下一次更新——也就是**电平保持**。这一点与 `bDataReceive` 的脉冲语义不同。

**与 KL6301 的依赖**：必须先有 `KL6301` 实例配置完成（`bReady = TRUE`）；KL6301 的 `EIB_GROUP_FILTER` 必须包含本 FB 的 `Group_Address`，否则 KL6301 根本不会把该 telegram 收进过程数据，本 FB 永远看不到事件。

**调用次数**：每个 `Group_Address` 每个 PLC 任务**建议只挂一个接收实例**。多个实例监听同一地址会同时触发各自的 `bDataReceive`，不会互相干扰但占内存。

**数据宽度匹配**：发送端 telegram 的负载长度必须与本 FB 类型对应（3 byte time telegram）。类型不匹配的 telegram 会被 KL6301 丢弃（`WRONG_EIB_DATA_LEN`），本 FB 永远收不到。

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
- **PDF 拼写 `wHoure` 不是 `wHour`**：库实际命名就是这样，代码必须按 PDF 写，否则编译报错。
- **KNX DPT 10 不带日期**：日期用 `EIB_DATE_REC`（DPT 11）。
- **DPT 10 还有可选的星期字段**：本 FB 不输出星期；如需要用 `EIB_ALL_DATA_TYPES_REC` 接收 raw 字节自己解析（PDF §4.3.2 没列星期格式）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_TIME_REC.TcPOU`](../examples/P_Demo_EIB_TIME_REC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_TIME_REC
VAR
    fb       : EIB_TIME_REC;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);
    wH,wM,wS : WORD;
    bNew     : BOOL;
END_VAR
fb(Group_Address := stGroup, strData_Rec := stEibRec,
   bDataReceive => bNew, wHoure => wH, wMinute => wM, wSecond => wS);
```

## 7. 业务场景与实际价值

- **场景**：BMS 主时钟同步、运维日志时间戳标定
- **价值**：DPT 10 标准接收；3-byte 自动拆分
- **替代方案对比**：
  - NTP / Tc2_TcpIp：精度高但需 IP 协议
  - 本地 RTC：偏移大
  - 本 FB：KNX BMS 标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.4.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187751179.html
- **相关**：`EIB_TIME_SEND` / `_EX`（同库 §4.2.5.28/29）、`EIB_DATE_REC`
