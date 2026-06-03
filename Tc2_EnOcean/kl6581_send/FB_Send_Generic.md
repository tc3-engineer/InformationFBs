# FB_Send_Generic

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Send generic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173282443.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Send_Generic.TcPOU`](../examples/P_Demo_FB_Send_Generic.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的**通用 EnOcean 电报发送 FB**。可发送任意 ORG 类型的电报（PTM / STM 1B / STM 4B / CTM / MODEM 等），数据通过 4 字节指针传入。专门化的发送 FB（`FB_Send_4BS` / `FB_Send_RPS_Switch` / `FB_Send_RPS_SwitchAuto`）是本 FB 的简化变体，本 FB 给所有非标 / 自定义类型留出灵活性。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart      : BOOL;
    by_Node     : BYTE;
    by_ORG      : E_EnOcean_Org;
    pt_SendData : DWORD;
    by_STATE    : BYTE;
    nEnOceanID  : BYTE;
    str_KL6581  : STR_KL6581;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | **上升沿触发一次发送**（电平触发会重复发，反而不利） |
| `by_Node` | `BYTE` | — | 通过哪个 KL6583 节点发出（1..8） |
| `by_ORG` | `E_EnOcean_Org` | — | 要发的 EnOcean ORG 类型（5/6/7/8/16#A/16#B） |
| `pt_SendData` | `DWORD` | — | 指向 4 字节发送数据的指针（用 `ADR(myArr)` 取地址） |
| `by_STATE` | `BYTE` | — | EnOcean STATE 字段值（可由 TCM 模块修改） |
| `nEnOceanID` | `BYTE` | — | 虚拟 EnOcean ID 偏移（0..127），将加到真实 EnOcean ID 上 |
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
| `bBusy` | `BOOL` | FB 处于发送中。`bBusy = TRUE` 期间禁止再触发新发送 |
| `bError` | `BOOL` | 发送失败 |
| `iErrorID` | `E_KL6581_Err` | 错误号（同 `FB_KL6581` 错误枚举） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 上升沿触发一次发送。`FALSE → TRUE` 沿 → FB 把 `pt_SendData` 指向的 4 字节按 `by_ORG / by_STATE / by_Node` 包装成 EnOcean 电报，经主端子 / KL6583 节点发到空中。`bBusy = TRUE` 期间忽略新的 `bStart` 沿。

**发送时序**：
1. `bStart` 上升沿 → `bBusy := TRUE`，把指针所指 4 字节复制到内部发送缓冲，更新 `str_KL6581` 中的 send 字段。
2. KL6581 主端子在下个 K-bus 周期把数据发给指定 `by_Node` 的 KL6583，KL6583 进入 RF 发射。
3. 发送完成 → `bBusy := FALSE`，等待下次 `bStart` 沿。
4. 失败（如 KL6583 不响应、`by_Node` 无效）→ `bError := TRUE`、`iErrorID := KL6581_TransmissionError (16#16)`，`bBusy := FALSE`。

**指针注意**：`pt_SendData` 是 `DWORD`（不是 PVOID），要把 4 字节变量的地址装进来。典型用法：`pt_SendData := ADR(my4ByteData)`。FB 内部把指针指向的 4 字节复制走，所以发送瞬间之后 `my4ByteData` 可以改。

**`nEnOceanID` 虚拟 ID 偏移**：EnOcean 设备本身有一个出厂硬编码的 32-bit ID，KL6583 收发器也有自己的 base ID。`nEnOceanID` 在 base ID 上加 0..127 的偏移，相当于"用一个 KL6583 模拟 128 个不同 ID 的虚拟设备"——对实现"PLC 模拟开关"很有用（一个 KL6583 节点可同时模拟 128 个 4 键面板）。

**典型陷阱**：① 用电平触发 `bStart := TRUE` → 每周期重复触发发送，会让 `bBusy` 一直 TRUE 并把 RF 信道占满。② `pt_SendData := 0` 或忘了 `ADR(...)` → 指针无效，发出去的数据是垃圾。③ `by_Node` 填 0 → 无效（发送必须指明节点 1..8）。④ 在 `fbKL6581.bReady = FALSE` 时触发发送 → 失败 `KL6581_not_ready`。

## 4. 错误码 / 返回值

`iErrorID : E_KL6581_Err` 与 `FB_KL6581` 共用错误枚举。本 FB 常见的：

| `iErrorID` | 含义 |
|---|---|
| `NO_ERROR (16#0)` | 无错 |
| `KL6581_not_ready (16#14)` | 主端子未 ready 就触发发送 |
| `KL6581_TransmissionError (16#16)` | KL6583 节点无效 / 不响应 |
| `KL6581_Switch_to_Stopp (16#13)` | 主端子停止运行 |

## 5. 使用注意 / 常见坑

- **`bStart` 严格用上升沿**：不能给电平 TRUE。
- **`pt_SendData := ADR(my4ByteData)` 必填**：典型类型 `my4ByteData : ARRAY [0..3] OF BYTE` 或 `my4ByteData : DWORD`。
- **`by_Node` 必须 1..8**：填 0 或 > 8 报错。
- **等 `fbKL6581.bReady = TRUE` 才触发**：上电初期主端子未 ready 时触发会报错。
- **`bBusy` 期间不要再触发**：上升沿被忽略不报错但发送丢失。
- **`nEnOceanID` 偏移**：要让 PLC 模拟"多个虚拟开关"时配合 0..127 偏移，每个虚拟 ID 各开一个本 FB 实例。
- **比专用 FB 复杂**：如果只是发 4-byte 数据 (ORG 7) 用 `FB_Send_4BS` 更简单；发 4 键开关用 `FB_Send_RPS_Switch`。本 FB 留给非标场景。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Send_Generic.TcPOU`](../examples/P_Demo_FB_Send_Generic.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Send_Generic
VAR
    fbKL6581       : FB_KL6581;
    fbSend         : FB_Send_Generic;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bTriggerSend   : BOOL;
    abPayload      : ARRAY [0..3] OF BYTE := [16#AA, 16#BB, 16#CC, 16#DD];
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbSend(
    bStart      := bTriggerSend,
    by_Node     := 1,
    by_ORG      := STM_4BYTE_TELEGRAM,
    pt_SendData := ADR(abPayload),
    by_STATE    := 16#0,
    nEnOceanID  := 0,
    str_KL6581  := fbKL6581.str_KL6581
);
```

## 7. 业务场景与实际价值

- **场景**：① 用 PLC 模拟一个 EnOcean 设备给现场的 EnOcean 接收器发指令（典型场景：用 PLC 代替手动按键远程触发一台 EnOcean 灯具控制器开灯）；② 透传自定义协议帧（厂家专有 ORG 9 / 10 等场景）。
- **价值**：把"发指针所指 4 字节，按 ORG 包装，经指定 KL6583 节点发出"封装为单 FB；应用层不用碰 EnOcean 协议层细节，配合 R_TRIG 即可发指令。
- **替代方案对比**：
  - 用 `FB_Send_4BS`：固定 ORG = 7，不能发其它类型
  - 用 `FB_Send_RPS_Switch`：固定 ORG = 5 + 4 键开关协议
  - **本 FB**：所有 ORG 类型都能发，配合自定义协议场景

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173282443.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Send_4BS`（ORG 7 简化版）、`FB_Send_RPS_Switch`（ORG 5 4 键开关版）、`FB_Send_RPS_SwitchAuto`（开关 + 自动释放版）、`E_ENOCEAN_ORG`（ORG 类型枚举）
