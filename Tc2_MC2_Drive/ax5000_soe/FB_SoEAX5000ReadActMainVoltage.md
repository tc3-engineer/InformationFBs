# FB_SoEAX5000ReadActMainVoltage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306260363.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU`](../examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU) |

---

## 1. 功能简述

读取 **AX5000** 驱动器当前**电网电压峰值**的功能块（Function Block, FB）。它通过 SoE 读 AX5000 的参数 `P-0-0200`，把当前主电源电压（峰值）以 `LREAL` 形式输出，单位伏特（例如 `303.0` 表示 303.0 V）。

这是针对 AX5000 的专用便捷 FB——相当于 `FB_SoERead` 预设好了 `P-0-0200` 这个 IDN，调用方无需自己拼 IDN/Element，直接拿电压值。典型用于监控电网质量、检测掉电/欠压、记录上电时电压等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId   : T_AmsNetID := '';
    Execute : BOOL;
    Timeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | `''` | 含 NC 所在 PC 的 AMS NetId 字符串；空串表示本机 |
| `Execute` | `BOOL` | — | 上升沿触发一次读取 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy              : BOOL;
    Error             : BOOL;
    AdsErrId          : UINT;
    SercosErrId       : UINT;
    Attribute         : DWORD;
    ActualMainVoltage : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `SercosErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 Sercos 错误码 |
| `Attribute` | `DWORD` | 返回该 Sercos 参数（`P-0-0200`）的属性 |
| `ActualMainVoltage` | `LREAL` | 返回 AX5000 当前电网电压峰值（如 `303.0` 对应 303.0 V） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次读取：FB 向 AX5000 读 `P-0-0200`，把电压峰值写入 `ActualMainVoltage`，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此时 `ActualMainVoltage` 有效。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId`/`SercosErrId` 给错误码。

**双错误码语义**：`AdsErrId` 管 ADS 通道；`SercosErrId` 管 AX5000 内部 Sercos 服务。诊断时两者都看。

**数值含义**：`ActualMainVoltage` 是**峰值**电压，不是 RMS（有效值）；判断电网是否正常时要按峰值口径，不要直接拿三相 RMS 标称值比较。`303.0` 这种值即 303.0 V 峰值。

**周期性读取**：要持续监控电压需周期性触发（如每秒一次上升沿），单次 `Execute` 只读一次当前值。`Execute` 是边沿触发，重读需新上升沿。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `SercosErrId : UINT`（Sercos 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、设备不可达、NetId 错 | 检查 EtherCAT OP、`Axis` Link、`NetId` |
| `SercosErrId` ≠ 0 | Sercos 服务错误：`P-0-0200` 不可读、轴非 AX5000 | 确认连接的是 AX5000；非 AX5000 应用通用 `FB_SoERead` 或对应型号 FB |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / Sercos 错误码数值。见 Beckhoff ADS Return Codes 总表与 AX5000 Sercos 文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **只适用于 AX5000**：本 FB 写死读 AX5000 的 `P-0-0200`；非 AX5000 设备用 `FB_SoERead` 读对应参数。
- **`ActualMainVoltage` 是峰值不是 RMS**：判断电压正常与否按峰值口径，别拿三相标称 RMS 直接比。
- **持续监控要周期性触发**：单次 `Execute` 只读一次；要实时监控需定时给上升沿。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **两个错误码都要看**：`AdsErrId` 通信、`SercosErrId` 参数/设备。
- **掉电检测要结合采样频率**：电压跌落可能很快，读取周期太慢会错过瞬时跌落（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU`](../examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU)

```iecst
// 场景：周期性读 AX5000 电网电压峰值用于欠压监控
rtVoltTrig(CLK := bReadVoltageReq);
fbReadVoltage(
    NetId   := '',
    Execute := rtVoltTrig.Q,
    Timeout := DEFAULT_ADS_TIMEOUT,
    Axis    := axisServo,
    Busy    => bVoltBusy,
    Error   => bVoltError,
    AdsErrId    => nVoltAdsErr,
    SercosErrId => nVoltSercosErr,
    Attribute   => nVoltAttribute,
    ActualMainVoltage => lrMainVoltage
);
```

## 7. 业务场景与实际价值

- **场景**：电网质量监控、欠压/掉电预警、上电自检记录电压、能耗/电压趋势记录。
- **价值**：一个专用 FB 直接拿到 AX5000 电压峰值，无需查 `P-0-0200` IDN 也无需自己拼 SoE 读取参数。
- **替代方案对比**：
  - 用通用 `FB_SoERead` 读 `P-0-0200`：要自己查 IDN、设 Element、做单位换算，繁琐
  - 外接电压表 / 采集模块：增加硬件成本，且与驱动器内部测量不一致
  - **本 FB**：AX5000 电压读取的便捷专用入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306260363.html
- **相关 FB**：`FB_SoERead`（通用 SoE 读，可读任意 AX5000 参数）、`FB_SoEAX5000SetMotorCtrlWord`（AX5000 电机控制字）
