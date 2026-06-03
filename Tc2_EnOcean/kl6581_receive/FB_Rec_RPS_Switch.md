# FB_Rec_RPS_Switch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Receive RPS switch` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173277835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Rec_RPS_Switch.TcPOU`](../examples/P_Demo_FB_Rec_RPS_Switch.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **RPS（Repeated Switch Telegram）按键接收 FB**——专门接收 EnOcean ORG Field 5 的"开关"电报（典型设备：4 键无线开关 / 摇杆面板）。本 FB 把电报解码成 `STR_EnOceanSwitch` 结构（8 个布尔：4 键的 ON / OFF 各 1 位）。

`STR_EnOceanSwitch` 结构字段：`bT1_ON/bT1_OFF/bT2_ON/bT2_OFF/bT3_ON/bT3_OFF/bT4_ON/bT4_OFF`，对应 4 个按键的"按下 ON 沿"与"按下 OFF 沿"。RPS 协议把按键事件分 ON / OFF 两种，可用于 dim up / dim down 或场景 A / 场景 B 互补语义。

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
| `dw_ID` | `DWORD` | — | RPS 开关设备的 EnOcean ID |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    str_EnOceanSwitch : STR_EnOceanSwitch;
    by_Node           : BYTE;
    bReceive          : BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `str_EnOceanSwitch` | `STR_EnOceanSwitch` | 4 键 × 2 状态：`bT1_ON/bT1_OFF/bT2_ON/bT2_OFF/bT3_ON/bT3_OFF/bT4_ON/bT4_OFF` |
| `by_Node` | `BYTE` | 接收该电报的 KL6583 节点编号 |
| `bReceive` | `BOOL` | **反相脉冲**，新电报到达时 FALSE 一周期 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：每周期被调用即可，无显式 enable。

**RPS 协议解码**：EnOcean RPS（ORG 5）电报里每个按键事件区分 ON / OFF——例如按"键 1 上半部分"发"bT1_ON"，按"键 1 下半部分"发"bT1_OFF"。`STR_EnOceanSwitch` 把这 8 个事件位直接展开。每个事件位在收到对应电报的当周期 TRUE，**之后保持 FALSE**——这与 PTM200 的"按住保持"语义**不同**，更像"按下沿"。

**事件 vs 状态**：本 FB 输出是事件位（按下时一帧 TRUE，松开和持续按住都不再触发），如果想要"按住电平"，需要另一帧 RPS"释放"电报（厂家不一定发），或者用 `FB_Send_RPS_SwitchAuto` 的对侧逻辑。多数 EnOcean 4 键面板（Eltako FT55、PEHA Easyclick）只发按下不发释放，只用 `bTn_ON / bTn_OFF` 区分上下半键。

**`bReceive` 反相脉冲**：与同系列其它接收块一致，新电报到达时 FALSE 一周期。

**典型陷阱**：① 把 `bT1_ON` 当成"键 1 被按下"——其实是"键 1 的上半按下事件"（同时还有 `bT1_OFF` 表示下半按下）。② 期待"按住 LED 持续亮"——本 FB 是事件触发不是电平，应用要自己做 RS 锁存。

## 4. 错误码 / 返回值

本 FB 无显式错误输出，依赖上游 `fbKL6581.iErrorID`。

## 5. 使用注意 / 常见坑

- **`bTn_ON / bTn_OFF` 是"键 n 的上半 / 下半事件"，不是开关状态**。Eltako FT55 风格面板里：
  - `bT1_ON` = 键 1 上半（典型场景：场景 A）
  - `bT1_OFF` = 键 1 下半（场景 B / 关 / 调暗）
- **要"按住电平"用自锁**：典型代码 `IF str_EnOceanSwitch.bT1_ON THEN bLightOn := TRUE; END_IF; IF str_EnOceanSwitch.bT1_OFF THEN bLightOn := FALSE; END_IF;`
- **`bReceive` 反相**：取沿用 `NOT bReceive`。
- **多面板共用**：每面板各开本 FB 实例，`dw_ID` 不同。
- **EnOcean 学习**：用 `FB_Rec_Teach_In` 或 `FB_EnOcean_Search` 抓 ID。
- **与 PTM200 (KL6021-0023) 的语义不同**：PTM200 给"4 键当前按下状态"（电平式 4 位数组），本 FB 给"上 / 下半事件 8 位"。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Rec_RPS_Switch.TcPOU`](../examples/P_Demo_FB_Rec_RPS_Switch.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Rec_RPS_Switch
VAR
    fbKL6581       : FB_KL6581;
    fbWallSwitch   : FB_Rec_RPS_Switch;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    nSwitchId      : DWORD := 16#01AABBCC;
    stSwitchData   : STR_EnOceanSwitch;
    bLight1On      : BOOL;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbWallSwitch(
    str_KL6581         := fbKL6581.str_KL6581,
    byNode             := 0,
    dw_ID              := nSwitchId,
    str_EnOceanSwitch  => stSwitchData
);
IF stSwitchData.bT1_ON THEN bLight1On := TRUE; END_IF;
IF stSwitchData.bT1_OFF THEN bLight1On := FALSE; END_IF;
```

## 7. 业务场景与实际价值

- **场景**：办公室 / 走廊 / 会议室壁挂 4 键场景面板。每键上 / 下半各一种动作，4 键共 8 种功能（"全开 / 全关 / 工作灯 / 调暗 / 投影模式 / 阅读 / 会议 / 影音"等）。EnOcean Eltako 等供应商有大量库存的现成 RPS 面板。
- **价值**：把 RPS 协议 8 位事件解码 + 与 KL6583 节点过滤 + 共享主端子状态一次接入；应用层直接用 `bTn_ON / bTn_OFF` 写场景脚本。
- **替代方案对比**：
  - 用 `FB_Rec_Generic` + 自己拆 1 字节：要懂 RPS 协议 nibble 编码，多写 20 行
  - 用 `FB_EnOceanPTM200`（KL6021-0023）：硬件不同，且只给 4 位状态不给 8 位事件
  - **本 FB**：KL6581 + 4 键场景面板的标准选项

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173277835.html
- **相关**：`FB_KL6581`（上游必备）、`STR_EnOceanSwitch`（输出结构 §4.2.2.2.4）、`FB_Rec_RPS_Window_Handle`（同 ORG 5 的窗把手版）、`FB_Send_RPS_Switch`/`FB_Send_RPS_SwitchAuto`（对侧发送）、`FB_EnOceanPTM200`（KL6021-0023 体系等价 FB）
