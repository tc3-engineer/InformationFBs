# FB_Rec_RPS_Window_Handle

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Receive RPS window handle` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173279371.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Rec_RPS_Window_Handle.TcPOU`](../examples/P_Demo_FB_Rec_RPS_Window_Handle.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **EnOcean 窗把手位置接收 FB**——专用于"三态窗把手"（典型设备：Hoppe 等无线窗把手），把手有三种位置：向下（关）、水平（开）、向上（倾斜）。本 FB 把 ORG Field 5 (RPS) 电报解码成 `AR_EnOceanWindow` 结构（三位互斥布尔 `bUp / bOpen / bClose`）。

每只窗把手一个本 FB 实例，用 `dw_ID` 区分。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    str_KL6581 : STR_KL6581;
    byNode     : BYTE;
    dw_ID      : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581` |
| `byNode` | `BYTE` | — | KL6583 节点过滤；`0` 收所有 |
| `dw_ID` | `DWORD` | — | 窗把手设备的 EnOcean ID |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    ar_Data  : AR_EnOceanWindow;
    by_Node  : BYTE;
    bReceive : BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `ar_Data` | `AR_EnOceanWindow` | 三位互斥结构：`bUp`（向上 / 倾斜）、`bOpen`（水平 / 开）、`bClose`（向下 / 关） |
| `by_Node` | `BYTE` | 接收该电报的 KL6583 节点编号 |
| `bReceive` | `BOOL` | **反相脉冲**，新电报到达时 FALSE 一周期 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：每周期被调用即可。

**三态互斥**：窗把手只有三种位置，`bUp / bOpen / bClose` 同一时刻**只有一位为 TRUE**，是真正的"当前状态"（不是事件位）。本 FB 是状态保持型——窗把手不变化时不发电报，应用层拿到的位是最近一帧的状态。

**`bReceive` 反相**：同其它接收块。

**初始状态**：上电后到第一帧之前三位都 FALSE，"位置未知"。

**典型应用**：HVAC 互锁——把手向下 (关) 才允许空调运行，向上 (倾斜) 允许新风模式，水平 (开) 强制关空调；安防系统判断窗是否关到位。

**典型陷阱**：① 上电瞬间所有位 FALSE → 不要直接当"位置 = 关闭"用；要等首帧确认。② 期望窗把手周期性发心跳验证在线 → 实际不发，无法用 watchdog 判离线，需要业务上接受这一点或加冗余机制。

## 4. 错误码 / 返回值

本 FB 无显式错误输出，依赖上游 `fbKL6581.iErrorID`。

## 5. 使用注意 / 常见坑

- **三态互斥**：`bUp + bOpen + bClose` 在收到帧之后恒为 1。首帧前都是 0。
- **`bReceive` 反相**：同系列其它接收块。
- **HVAC 互锁建议**：
  - `bClose = TRUE` → 空调正常运行
  - `bOpen = TRUE` → 关空调（窗全开节能联动）
  - `bUp = TRUE` → 新风模式 / 通风
- **学习时**：用 `FB_Rec_Teach_In` 或现场按窗把手学习按键，PLC 端开 `FB_Rec_Generic` 观察 `dw_ID`。
- **多窗把手**：每只各开一个本 FB 实例，共享 `str_KL6581`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Rec_RPS_Window_Handle.TcPOU`](../examples/P_Demo_FB_Rec_RPS_Window_Handle.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Rec_RPS_Window_Handle
VAR
    fbKL6581         : FB_KL6581;
    fbHandle         : FB_Rec_RPS_Window_Handle;
    stKL6581Input    AT %I* : KL6581_Input;
    stKL6581Output   AT %Q* : KL6581_Output;
    nWindowHandleId  : DWORD := 16#0234CDEF;
    stWindowState    : AR_EnOceanWindow;
    bAirCondAllowed  : BOOL;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbHandle(
    str_KL6581 := fbKL6581.str_KL6581,
    byNode     := 0,
    dw_ID      := nWindowHandleId,
    ar_Data    => stWindowState
);
bAirCondAllowed := stWindowState.bClose;
```

## 7. 业务场景与实际价值

- **场景**：高档办公 / 住宅 / 酒店的电动窗或新风系统联动。三态窗把手能区分"全关 / 全开 / 倾开"三种语义，让 HVAC 与新风系统更精细地匹配用户意图。例如倾开时仅启动新风换气保留冷风、全开时直接关空调。
- **价值**：三态在单 FB 里解码完毕；应用层只看 `bUp/bOpen/bClose` 三位互斥布尔写联动逻辑，干净简洁。
- **替代方案对比**：
  - 用机械限位开关 + KL1xxx DI：要装两个限位开关识别三态，且要布线
  - 用 `FB_Rec_Generic` 读 1 字节自拆位：要懂 RPS nibble 编码
  - **本 FB**：KL6581 体系窗把手的标准选项

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173279371.html
- **相关**：`FB_KL6581`（上游必备）、`AR_EnOceanWindow`（输出结构 §4.2.2.2.3）、`FB_Rec_RPS_Switch`（同 ORG 5 的 4 键开关版）
