# FB_Send_4BS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Send 4BS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173283979.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Send_4BS.TcPOU`](../examples/P_Demo_FB_Send_4BS.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **4BS 电报发送 FB**——固定 `ORG = 7`（4-byte sensor 电报）的简化变体。比 `FB_Send_Generic` 少 2 个参数（不需要再填 `by_ORG` 和 `by_STATE`），用于发标准 4-byte 传感器数据格式。典型应用：用 PLC 模拟一个 4-byte 数据源（例如发送温度、设定值、状态字给 EnOcean 接收端）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart      : BOOL;
    by_Node     : BYTE;
    pt_SendData : DWORD;
    nEnOceanID  : BYTE;
    str_KL6581  : STR_KL6581;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发一次发送 |
| `by_Node` | `BYTE` | — | 经哪个 KL6583 节点发出（1..8） |
| `pt_SendData` | `DWORD` | — | 指向 4 字节发送数据的指针；用 `ADR(...)` |
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
| `iErrorID` | `E_KL6581_Err` | 错误号（同 `FB_KL6581`） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 上升沿触发一次。本 FB 内部硬编码 ORG = 7（STM_4BYTE_TELEGRAM），byState = 0；其余流程与 `FB_Send_Generic` 一致：拷贝 4 字节 → 主端子打包 → 经指定 KL6583 节点 RF 发出。

**与 FB_Send_Generic 的差异**：参数少 2 个（ORG 和 STATE 都固定）；用于"发送方就是模拟一个标准 4-byte 传感器"的场景。如果要发其它 ORG 类型（5/6/8 等）请用 Generic 版。

**典型陷阱**：
- 电平触发（同 Generic）。
- 指针未用 `ADR()` 包（同 Generic）。
- 主端子未 Ready（同 Generic）。
- 期望发 RPS 4 键开关：选错 FB，应该用 `FB_Send_RPS_Switch`。

## 4. 错误码 / 返回值

同 `FB_KL6581` 错误枚举 `E_KL6581_Err`。常见：`KL6581_not_ready (16#14)`、`KL6581_TransmissionError (16#16)`、`KL6581_Switch_to_Stopp (16#13)`。

## 5. 使用注意 / 常见坑

- **固定 ORG = 7**：不要拿来发 RPS / 1BS 电报，会被对端解码错。
- **上升沿**：典型用 `R_TRIG` 整形或在控制流里用边沿变量自动复位。
- **`pt_SendData := ADR(my4Bytes)`**：`my4Bytes` 可以是 `ARRAY[0..3] OF BYTE`、`DWORD`、`STRUCT 4-byte` 等任何 4 字节类型。
- **等 `fbKL6581.bReady = TRUE`**：上电初未 Ready 触发会报错。
- **`nEnOceanID` 偏移**：可实现"一片 KL6583 模拟 128 个虚拟 4-byte sensor"，每个虚拟 sensor 各一个 FB 实例 + 各自 `nEnOceanID`。
- **比 Generic 简洁，但失去灵活性**：只能发 ORG = 7。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Send_4BS.TcPOU`](../examples/P_Demo_FB_Send_4BS.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Send_4BS
VAR
    fbKL6581       : FB_KL6581;
    fbSend4BS      : FB_Send_4BS;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bTriggerSend   : BOOL;
    abData         : ARRAY [0..3] OF BYTE := [16#1A, 16#2B, 16#3C, 16#4D];
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbSend4BS(
    bStart      := bTriggerSend AND fbKL6581.bReady,
    by_Node     := 1,
    pt_SendData := ADR(abData),
    nEnOceanID  := 0,
    str_KL6581  := fbKL6581.str_KL6581
);
```

## 7. 业务场景与实际价值

- **场景**：用 PLC 模拟一台 EnOcean 温度传感器，把 PLC 内部计算的虚拟温度（来自 PT100 或工艺值）经 EnOcean 广播给楼宇 BMS 接收节点。BMS 那边按收 EnOcean 4-byte sensor 的逻辑处理，对方完全不知道发送方实际是 PLC。
- **价值**：单 FB + 上升沿 + `ADR()` 指针就发出去，不用碰 ORG / STATE / 帧拼装；适合"PLC ↔ EnOcean BMS"桥接场景。
- **替代方案对比**：
  - 用 `FB_Send_Generic`：多 2 个参数，灵活但啰嗦
  - 直接接 EL6233 EtherCAT 发送：要换硬件
  - **本 FB**：KL6581 体系下发 4 byte 数据的标准简化版

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173283979.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Send_Generic`（通用版）、`FB_Send_RPS_Switch`/`FB_Send_RPS_SwitchAuto`（4 键开关）、`E_ENOCEAN_ORG`
