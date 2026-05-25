# FB_ParkAxis

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General Beckhoff` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/16678039819.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ParkAxis.xml`](../examples/P_Demo_FB_ParkAxis.xml) |

---

## 1. 功能简述

启用/解除 Beckhoff 驱动器**驻留（park）**功能的功能块（Function Block, FB）。驻留的本质是把驱动器的某个通道**临时禁用**——被驻留的通道不再参与运行，也不会因为"该通道没接电机/没反馈"而报错。

典型应用是**模块化机器**：某些工位可选配电机，未装电机的通道若不处理就会报反馈错误（feedback error）。把这些空通道用本 FB 驻留掉，机器即可在缺电机的情况下正常启动而不报错；后续装上电机再解除驻留。

通过 `Mode` 选择驻留还是解除：`eParkMode_Park`（驻留通道）/ `eParkMode_Release`（释放通道）。本 FB 是硬件无关入口，AX5000 专用版本为 `FB_SoEAX5000ParkAxis`、AX8000 专用版本为 `FB_CoEAX8000ParkAxis`。

⚠️ **重要提示（来自 PDF NOTICE）**：对多通道设备，在驻留某通道前必须先关闭该设备**所有通道**的控制器使能（controller enable）；激活通道时同理。否则其它通道的轴可能被意外失能。

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
| `Mode` | `E_ParkMode` | — | 选择 FB 驻留还是释放轴：`eParkMode_Park`（通道被驻留）/ `eParkMode_Release`（通道被释放） |

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
| `Error` | `BOOL` | `Busy` 复位后若传输命令时发生错误则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码（见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次驻留/释放：FB 通过 ADS/SoE/CoE 把驻留命令写到驱动器，`Busy := TRUE`，异步等待确认，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**`Mode` 语义**：
- `eParkMode_Park`：把该通道驻留——通道临时禁用，不再因缺电机/缺反馈而报错。
- `eParkMode_Release`：把该通道释放——通道恢复正常参与运行。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**；出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**多通道安全前提（PDF NOTICE，必须遵守）**：对多通道驱动器，驻留/激活某通道前要先**关闭该设备所有通道的控制器使能**，否则其它通道的轴会被意外停掉。正确顺序：先对该设备所有轴 `MC_Power(Enable := FALSE)` → 再 `FB_ParkAxis` 驻留/释放 → 完成后按需重新使能未驻留通道。

**典型用法**：开机阶段对未装电机的可选工位通道执行 `eParkMode_Park`，使机器在缺配置下正常启动；后续工位安装电机后执行 `eParkMode_Release`。`Execute` 是边沿触发，切换需新的上升沿。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与驱动器的 ADS 传输失败 | 检查 EtherCAT 总线 OP、轴 Link、`Axis` 引用有效性 |
| 驱动器不支持 / 状态不允许 | 固件版本不满足、或通道当前使能未关闭无法驻留 | 核对固件（AX5xxx ≥ FW v2.12 b0001；AX8xxx/MD8xxx ≥ v1.06 b0003）、TwinCAT ≥ 4024.60 / ≥ 4026.8、`Tc2_MC2_Drive ≥ V3.3.41.0`；确认按 NOTICE 先关使能 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **驻留/激活多通道设备前必须先关该设备所有通道使能**：PDF NOTICE 硬要求，否则其它通道的轴被意外停掉——这是本 FB 最危险的坑。
- **没有 `Done` 输出**：判完成靠 `Busy` 落回 `FALSE` 且 `Error = FALSE`。
- **`Execute` 是边沿触发 + `Busy` 期间持续循环调用**：异步跨周期。
- **版本门槛较高**：需要较新的 TwinCAT（≥ 4024.60 / ≥ 4026.8）和库（≥ V3.3.41.0），旧环境用不了，应先用 `F_GetVersionTcMc2Drive` 校验。
- **AX5000/AX8000 有专用版本**：`FB_SoEAX5000ParkAxis` / `FB_CoEAX8000ParkAxis`，行为等价，但本 FB 硬件无关更通用。
- **驻留是临时禁用不是永久配置**：重新上电后是否保持视配置而定，模块化机器逻辑应每次启动按需重新驻留（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ParkAxis.xml`](../examples/P_Demo_FB_ParkAxis.xml)

```iecst
// 场景：模块化机器某可选工位未装电机，开机驻留该通道避免反馈报错
rtParkTrig(CLK := bParkReq);
fbParkAxis(
    Execute := rtParkTrig.Q,
    Mode    := eRequestedParkMode,
    Axis    := axisOptionStation,
    Busy    => bParkBusy,
    Error   => bParkError,
    ErrorID => nParkErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：模块化机器缺配置工位、维修期临时屏蔽某通道、多轴设备分阶段调试时屏蔽尚未接线的轴。
- **价值**：缺电机的通道驻留后不报反馈错误，机器能在不完整配置下正常启动，省去为每种配置组合维护单独工程的成本。
- **替代方案对比**：
  - 为每种工位配置做一套独立 NC 配置：组合爆炸，维护成本高
  - 直接忽略反馈错误：危险，掩盖真实故障
  - `FB_SoEAX5000ParkAxis` / `FB_CoEAX8000ParkAxis`：型号专用，行为等价
  - **本 FB**：硬件无关，运行期动态驻留/释放，最灵活

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.1.6，枚举 §5.7 `E_ParkMode`
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/16678039819.html
- **相关 FB**：`FB_SoEAX5000ParkAxis` / `FB_CoEAX8000ParkAxis`（型号专用驻留）、`MC_Power`（驻留前关使能用）
