# FB_Send_RPS_SwitchAuto

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Send RPS switch auto` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173287051.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Send_RPS_SwitchAuto.TcPOU`](../examples/P_Demo_FB_Send_RPS_SwitchAuto.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **RPS 开关电报"自动按下释放"发送 FB**——`FB_Send_RPS_Switch` 的便利版本。`bStart` 上升沿触发：FB 先发一帧"按下"电报（`bData` 状态），然后等 `t_SwitchDelay` 时长后**自动发一帧"释放"电报**，完成一次完整按键模拟。调用方只需触发一次。

适合"PLC 模拟单次按键"的常见场景。要更精细的时序控制（长按 / 双击 / 序列），用 `FB_Send_RPS_Switch` 手动。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart        : BOOL;
    bData         : BOOL;
    by_Node       : BYTE;
    t_SwitchDelay : TIME := T#100ms;
    nRockerID     : INT;
    nEnOceanID    : BYTE;
    str_KL6581    : STR_KL6581;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发一次"按下 + 等待 + 释放"完整动作 |
| `bData` | `BOOL` | — | 要传的开关值（接收端按 RPS 协议解码为某半键事件） |
| `by_Node` | `BYTE` | — | KL6583 节点（1..8） |
| `t_SwitchDelay` | `TIME` | `T#100ms` | "按下"与"自动释放"之间的延时（即"按键按住时长"） |
| `nRockerID` | `INT` | — | 按键位（0..3） |
| `nEnOceanID` | `BYTE` | — | 虚拟 EnOcean ID 偏移（0..127） |
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    iErrorID : E_KL6581_Err;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 完整动作进行中（包括按下 + 等待 + 释放）。`TRUE → FALSE` 表示一次完整按键发送完成 |
| `bError` | `BOOL` | 发送失败 |
| `iErrorID` | `E_KL6581_Err` | 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 上升沿触发。内部状态机：
1. `bStart` 上升沿 → `bBusy := TRUE`，发"按下"电报（`bData` 当前值）。
2. 等待 `t_SwitchDelay`（默认 100 ms）。
3. 发"释放"电报。
4. `bBusy := FALSE`，回空闲态。

**`bBusy` 完整覆盖**：从触发到自动释放发完，`bBusy` 全程 TRUE。调用方等 `bBusy` 回 FALSE 即知按键模拟完整结束。期间再触发 `bStart` 上升沿会被忽略。

**`t_SwitchDelay` 用途**：模拟"按住时长"。某些接收端对按键长度敏感（< 50 ms 视为干扰过滤，> 1 s 视为长按）；默认 100 ms 适合短按。要长按时设大（例如 T#1500ms）。

**典型陷阱**：
- `t_SwitchDelay` 设过小（< 50 ms）→ 接收端的去抖逻辑可能把"释放"过滤掉。
- 在 `bBusy = TRUE` 时再触发 → 被忽略，下个"按键"消息丢失。
- 用 `bData = TRUE`/`FALSE` 区分两个键位 → 实际是同 `nRockerID` 键的上半 / 下半语义，不是不同按键。

## 4. 错误码 / 返回值

同 `FB_KL6581` 错误枚举。`KL6581_not_ready (16#14)`、`KL6581_TransmissionError (16#16)` 常见。

## 5. 使用注意 / 常见坑

- **比 `FB_Send_RPS_Switch` 省心**：一次触发完成完整动作，HMI 集成最方便。
- **`t_SwitchDelay` 默认 100 ms** 适合大多数场景；某些 EnOcean 接收设备要求更长（≥ 250 ms）才把"释放"识别为正常按键，需要调。
- **`bBusy` 完成时刻是一次按键的结束沿**：可用于"按键序列等待完成"逻辑。
- **`nEnOceanID` 偏移配合多虚拟面板**：一片 KL6583 模拟 128 个虚拟按键面板。
- **不能做长按 vs 短按区分**：本 FB 内 t_SwitchDelay 是固定的按住时长。如果想"长按 / 短按 / 双击"用 `FB_Send_RPS_Switch` 手动控制。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Send_RPS_SwitchAuto.TcPOU`](../examples/P_Demo_FB_Send_RPS_SwitchAuto.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Send_RPS_SwitchAuto
VAR
    fbKL6581       : FB_KL6581;
    fbAuto         : FB_Send_RPS_SwitchAuto;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bHmiTrigger    : BOOL;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbAuto(
    bStart        := bHmiTrigger AND fbKL6581.bReady,
    bData         := TRUE,
    by_Node       := 1,
    t_SwitchDelay := T#200MS,
    nRockerID     := 0,
    nEnOceanID    := 0,
    str_KL6581    := fbKL6581.str_KL6581
);
```

## 7. 业务场景与实际价值

- **场景**：智能酒店"一键退房"——HMI 触发后 PLC 模拟一组虚拟开关向房间所有 EnOcean 接收器发送指令（关灯、关空调、降幕、把房间状态切到"清洁待入住"）。每个指令一行 `fbAuto(bStart := bTrigOnce, ...)`，比手动管按下 / 释放省去状态机。
- **价值**：把"按下 + 等待 + 释放"完整动作封装为单 FB；HMI 集成最简单；适合所有"PLC 单次按键模拟"场景。
- **替代方案对比**：
  - `FB_Send_RPS_Switch`：手动控制时序，灵活但啰嗦
  - `FB_Send_Generic`：通用版，要懂 RPS 协议
  - **本 FB**：单次按键模拟首选；省去状态机

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173287051.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Send_RPS_Switch`（手动版）、`FB_Send_Generic`（通用版）、`FB_Rec_RPS_Switch`（对应接收）
