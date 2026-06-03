# FB_Send_RPS_Switch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Send RPS switch` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173285515.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Send_RPS_Switch.TcPOU`](../examples/P_Demo_FB_Send_RPS_Switch.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **RPS 开关电报发送 FB**——固定 `ORG = 5`，按"4 键面板"协议发送。`bStart` 上升沿触发一次发送：`bData = TRUE` 发"按下"电报、`bData = FALSE` 发"释放"电报，`nRockerID` 选择 4 个按键位中的哪一个（0..3）。

**注意**：模拟"按一下"需要触发两次本 FB——先 `bData = TRUE` 发按下，再 `bData = FALSE` 发释放。如果只想触发一次，用 `FB_Send_RPS_SwitchAuto`（按下后自动延时发释放）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart     : BOOL;
    by_Node    : BYTE;
    bData      : BOOL;
    nRockerID  : INT;
    nEnOceanID : BYTE;
    str_KL6581 : STR_KL6581;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发一次发送 |
| `by_Node` | `BYTE` | — | KL6583 节点（1..8） |
| `bData` | `BOOL` | — | 要发的开关动作：TRUE = 按下，FALSE = 释放 |
| `nRockerID` | `INT` | — | 按键位（0..3，对应 4 键面板） |
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
| `bBusy` | `BOOL` | 发送进行中 |
| `bError` | `BOOL` | 发送失败 |
| `iErrorID` | `E_KL6581_Err` | 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 上升沿触发一次。FB 内部根据 `bData / nRockerID` 拼 RPS 电报，经主端子 / KL6583 发出空中。

**两次触发模拟按一下**：典型用法是先用 `bData = TRUE` 触发一次（按下），过 100-300 ms 后再用 `bData = FALSE` 触发一次（释放）；接收端把"按下 + 释放"识别为一次完整按键动作。**这两次都需要单独的 `bStart` 上升沿**。

如果嫌麻烦，用 `FB_Send_RPS_SwitchAuto`，它在按下后内部计时然后自动发释放，调用方只触发一次。

**典型陷阱**：
- 只发 `bData = TRUE` 不发释放 → 接收端可能误以为按键被"按住"不放（部分 RPS 接收逻辑会重复触发）。
- 两次触发之间间隔太短（< 50 ms）→ 接收端的 RPS 重复抑制把"释放"过滤了；建议 100-300 ms。
- `nRockerID > 3` → 数据错位。
- `by_Node = 0` 或 > 8 → 报错。

## 4. 错误码 / 返回值

同 `FB_KL6581` 错误枚举。常见 `KL6581_not_ready`、`KL6581_TransmissionError`。

## 5. 使用注意 / 常见坑

- **必须发释放才完整**：用本 FB 模拟按键时一定要"按下 + 释放"成对发送。若工程允许，直接用 `FB_Send_RPS_SwitchAuto` 省心。
- **`nRockerID` 0..3** 是按键位（一片 4 键面板 4 个位）。
- **`bData` 是动作不是状态**：TRUE = "按下"事件，FALSE = "释放"事件。每次发送都是一帧动作不是当前长期状态。
- **配合 R_TRIG 实现"PLC 按键"**：在 PLC 端把 HMI 上的按钮按下事件转成两次 `bStart` 触发即可远程模拟一次物理按键。
- **`nEnOceanID` 偏移**：让一片 KL6583 模拟多个虚拟 RPS 面板。
- **比 SwitchAuto 灵活**：手动控制按下与释放间隔，可以做"长按 / 短按 / 双击"序列。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Send_RPS_Switch.TcPOU`](../examples/P_Demo_FB_Send_RPS_Switch.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Send_RPS_Switch
VAR
    fbKL6581       : FB_KL6581;
    fbSendSwitch   : FB_Send_RPS_Switch;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bTrigger       : BOOL;
    bPress         : BOOL;
    nKey           : INT := 0;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbSendSwitch(
    bStart     := bTrigger,
    by_Node    := 1,
    bData      := bPress,
    nRockerID  := nKey,
    nEnOceanID := 0,
    str_KL6581 := fbKL6581.str_KL6581
);
```

## 7. 业务场景与实际价值

- **场景**：HMI 屏上的"虚拟开关"远程触发现场 EnOcean 灯控接收器。例如保洁人员在中控室 HMI 上点"会议室全开"，PLC 发一帧 EnOcean RPS 按键给会议室的 EnOcean 灯控器。还可用于自动化测试——PLC 自动按虚拟开关序列模拟人按面板的工厂测试。
- **价值**：精确控制按下 / 释放时间间隔，可实现长按、双击等高级语义；比 SwitchAuto 灵活但更复杂。
- **替代方案对比**：
  - `FB_Send_RPS_SwitchAuto`：一次触发自动发释放；省心但失去时序控制
  - `FB_Send_Generic`：可以发任何 ORG，但要懂 RPS 协议字节布局
  - **本 FB**：4 键开关协议 + 手动时序控制，适合按键序列模拟

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173285515.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Send_RPS_SwitchAuto`（自动释放版）、`FB_Send_Generic`（通用版）、`FB_Rec_RPS_Switch`（对应接收）
