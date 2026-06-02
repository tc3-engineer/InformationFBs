# FB_SoEAX5000SetMotorCtrlWord

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306287115.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.xml`](../examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.xml) |

---

## 1. 功能简述

设置 **AX5000** 电机控制字（Motor Control Word，参数 `P-0-0096`）里 **ForceLock** 位（Bit 0）或 **ForceUnlock** 位的功能块（Function Block, FB），用于手动激活/释放电机抱闸。

正常情况下抱闸由驱动器使能（Enable）自动联动。本 FB 让你**绕过使能逻辑**直接控制抱闸：`ForceLock = TRUE` 时不管使能与否都抱死抱闸；`ForceUnlock = TRUE` 时不管使能与否都松开抱闸。当 `ForceLock` 与 `ForceUnlock` 同时置位时，**`ForceLock`（抱死）优先级更高**。

这是 AX5000 专用的抱闸控制 FB（操作 `P-0-0096`），与硬件无关的 `FB_BrakeControl` 行为类似但接口不同——`FB_BrakeControl` 用 `E_BrakeMode` 三态枚举，本 FB 用两个独立 Bit。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId       : T_AmsNetId := '';
    Execute     : BOOL; 
    Timeout     : TIME := DEFAULT_ADS_TIMEOUT;
    ForceLock   : BOOL;
    ForceUnlock : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetId` | `''` | 含 PC 的 AMS NetId 字符串；空串表示本机 |
| `Execute` | `BOOL` | — | 上升沿触发一次设置 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |
| `ForceLock` | `BOOL` | — | 独立于使能激活抱闸（抱死）；与 `ForceUnlock` 同时置位时本位优先 |
| `ForceUnlock` | `BOOL` | — | 独立于使能释放抱闸（松开） |

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
    Busy        : BOOL;
    Error       : BOOL;
    AdsErrId    : UINT;
    SercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `SercosErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次设置：FB 把 `ForceLock`/`ForceUnlock` 写到 AX5000 的电机控制字 `P-0-0096`，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**两个 Bit 的组合语义**：
- `ForceLock = TRUE, ForceUnlock = FALSE`：抱闸抱死（独立于使能）
- `ForceLock = FALSE, ForceUnlock = TRUE`：抱闸松开（独立于使能）
- `ForceLock = TRUE, ForceUnlock = TRUE`：两者同置时 **ForceLock（抱死）优先**
- `ForceLock = FALSE, ForceUnlock = FALSE`：两个 Force 位都清，恢复使能自动联动

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId`/`SercosErrId` 给错误码。

⚠️ **安全**：`ForceUnlock` 在垂直/重力轴上会让轴失去机械保持而下坠，操作前必须有机械支撑或风险评估（与 `FB_BrakeControl` 的 Unlock 同等风险）。手动控制用完应把两个 Force 位都清掉恢复自动联动。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `SercosErrId : UINT`（Sercos 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、设备不可达、NetId 错 | 检查 EtherCAT OP、`Axis` Link、`NetId` |
| `SercosErrId` ≠ 0 | Sercos 服务错误：`P-0-0096` 写入被拒、轴非 AX5000 | 确认连接的是 AX5000；非 AX5000 用 `FB_BrakeControl` 或对应型号 FB |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / Sercos 错误码数值。见 Beckhoff ADS Return Codes 总表与 AX5000 Sercos 文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **`ForceLock` 优先于 `ForceUnlock`**：两者同置时抱死生效，别指望同置能"互相抵消"成自动。
- **恢复自动 = 两个 Force 位都清**：`ForceLock = FALSE, ForceUnlock = FALSE` 才回到使能联动。
- **`ForceUnlock` 对垂直轴高危**：松开后失能不抱闸，重力轴下坠，操作前要机械支撑。
- **只适用于 AX5000**：本 FB 写 `P-0-0096`；非 AX5000 用 `FB_BrakeControl`。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **`ForceLock` 抱死时使能也动不了轴**：会出现"使能成功但一动报跟随误差"现象，因为抱闸还锁着（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.xml`](../examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.xml)

```iecst
// 场景：手动松开 AX5000 抱闸做机械对位（ForceUnlock），用完清两个 Force 位
rtCtrlTrig(CLK := bSetCtrlWordReq);
fbSetMotorCtrlWord(
    NetId       := '',
    Execute     := rtCtrlTrig.Q,
    Timeout     := DEFAULT_ADS_TIMEOUT,
    ForceLock   := bForceLock,
    ForceUnlock := bForceUnlock,
    Axis        := axisServo,
    Busy        => bCtrlBusy,
    Error       => bCtrlError,
    AdsErrId    => nCtrlAdsErr,
    SercosErrId => nCtrlSercosErr
);
```

## 7. 业务场景与实际价值

- **场景**：AX5000 上手动盘动电机做机械对位（ForceUnlock）、装夹工件时临时抱死防移动（ForceLock）、抱闸维护测试；用完恢复自动。
- **价值**：用两个独立 Bit 精确控制 AX5000 抱闸，绕过使能逻辑，适合需要"使能与抱闸解耦"的调试场景。
- **替代方案对比**：
  - `FB_BrakeControl`（硬件无关）：用 `E_BrakeMode` 三态，更通用；本 FB 是 AX5000 专用 Bit 级控制
  - 直接写 `P-0-0096`（通用 `FB_SoEWrite`）：要自己拼 Bit，繁琐
  - **本 FB**：AX5000 抱闸 Bit 级手动控制的便捷专用入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306287115.html
- **相关 FB**：`FB_BrakeControl`（硬件无关抱闸控制）、`FB_SoEAX5000ReadActMainVoltage`（AX5000 电压读取）
