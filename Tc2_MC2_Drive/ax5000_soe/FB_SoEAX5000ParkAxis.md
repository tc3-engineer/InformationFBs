# FB_SoEAX5000ParkAxis

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/11307039499.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000ParkAxis.xml`](../examples/P_Demo_FB_SoEAX5000ParkAxis.xml) |

---

## 1. 功能简述

启用/解除 **AX5000** 驻留（park）功能的功能块（Function Block, FB）。被驻留的 AX5000 通道临时禁用——不参与运行，也不会因缺电机/缺反馈而报错。功能与硬件无关的 `FB_ParkAxis` 等价，但本 FB 是 AX5000 专用版本。

典型应用是模块化机器：未装电机的可选通道用本 FB 驻留掉，机器即可在缺配置下正常启动；装上电机再解除。通过 `Mode` 选驻留还是释放（`eParkMode_Park` / `eParkMode_Release`）。也可改用通用的 `FB_ParkAxis`，行为等价。

⚠️ **多通道安全前提**：对多通道 AX5000，驻留/激活某通道前必须先关闭该设备所有通道的控制器使能，否则其它通道的轴会被意外失能（同 `FB_ParkAxis`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
    Mode    : E_ParkMode;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次驻留/释放命令；不需保持高电平 |
| `Mode` | `E_ParkMode` | — | 选择驻留还是释放：`eParkMode_Park`（通道被驻留）/ `eParkMode_Release`（通道被释放） |

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
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次驻留/释放：FB 向 AX5000 发驻留命令，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**`Mode` 语义**：
- `eParkMode_Park`：把该通道驻留——临时禁用，不再因缺电机/缺反馈报错
- `eParkMode_Release`：把该通道释放——恢复正常参与运行

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**。出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**多通道安全前提（必须遵守）**：对多通道 AX5000，驻留/激活某通道前要先关闭该设备**所有通道**的控制器使能，否则其它通道的轴被意外停掉。正确顺序：先对该设备所有轴 `MC_Power(Enable := FALSE)` → 再 `FB_SoEAX5000ParkAxis` 驻留/释放 → 完成后按需重新使能未驻留通道。

**典型用法**：开机阶段对未装电机的可选通道执行 `eParkMode_Park`；后续工位安装电机后执行 `eParkMode_Release`。`Execute` 是边沿触发，切换需新上升沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与 AX5000 的 ADS 传输失败 | 检查 EtherCAT OP、`Axis` Link |
| 不支持 / 状态不允许 | 固件不满足，或通道使能未关闭无法驻留 | 核对 AX5000 固件 ≥ v2.12 b0001、TwinCAT ≥ 4022.32/4024.6、库 ≥ V3.3.21.0；确认先关使能 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **驻留/激活多通道设备前必须先关该设备所有通道使能**：否则其它通道的轴被意外停掉——最危险的坑。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **`Execute` 是边沿触发**：切换需新上升沿。
- **只适用于 AX5000**：本 FB 走 AX5000 SoE 通道；其它型号用 `FB_ParkAxis` 或 AX8000 专用版本。
- **接口仅 Execute/Mode**：无 `NetId`/`Timeout`，简洁，写代码注意 pin 名。
- **驻留是临时禁用**：模块化机器逻辑应每次启动按需重新驻留（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000ParkAxis.xml`](../examples/P_Demo_FB_SoEAX5000ParkAxis.xml)

```iecst
// 场景：模块化机器某 AX5000 可选通道未装电机，开机驻留避免反馈报错
rtParkTrig(CLK := bParkReq);
fbAX5000ParkAxis(
    Execute := rtParkTrig.Q,
    Mode    := eRequestedParkMode,
    Axis    := axisOptionStation,
    Busy    => bParkBusy,
    Error   => bParkError,
    ErrorID => nParkErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：AX5000 驱动的模块化机器缺配置工位、维修期临时屏蔽某通道、分阶段调试屏蔽未接线轴。
- **价值**：缺电机的 AX5000 通道驻留后不报反馈错误，机器能在不完整配置下启动；AX5000 专用接口直达。
- **替代方案对比**：
  - `FB_ParkAxis`（硬件无关）：更通用；本 FB 是 AX5000 专用等价版本
  - 为每种配置做独立 NC 配置：组合爆炸
  - **本 FB**：AX5000 驻留/释放的专用入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.4.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/11307039499.html
- **相关 FB**：`FB_ParkAxis`（硬件无关）、`FB_CoEAX8000ParkAxis`（AX8000 专用）、`MC_Power`（驻留前关使能）
