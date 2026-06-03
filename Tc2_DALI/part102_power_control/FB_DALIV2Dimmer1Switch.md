# FB_DALIV2Dimmer1Switch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Power Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2Dimmer1Switch.TcPOU`](../examples/P_Demo_FB_DALIV2Dimmer1Switch.TcPOU) |

---

## 1. 功能简述

**单按钮调光开关 FB（high-level）**——一个机械按钮接到 PLC 的 BOOL 输入，本 FB 把它解读为"短按 = 开 / 关 切换 / 长按 = 调光"两种语义：短按（持续时间 < `tSwitchOverTime`）每按一次在 ON / OFF 之间翻转；长按（≥ `tSwitchOverTime`）进入调光模式，输出电平在 `nMinLevelMasterDev` ～ `nMaxLevelMasterDev` 之间往返、到达边界时停 `tCycleDelay` 时间以方便锁定最大 / 最小，松开按钮停在当前亮度；同一次长按再次短按可反向调光。同时另外提供 `bOn` / `bOff` 直接开关、`bSetDimmValue` + `nDimmValue` 数值直驱两条次要控制路径。

可控制单灯（`eAddrType = eDALIV2AddrTypeShort` + `nAddr`）、组（`eDALIV2AddrTypeGroup` + 组号）、广播全线（`eDALIV2AddrTypeBroadcast`）。**这是楼宇 / 工业照明里最常用的"按钮 + 调光"标准模块**，等价于自己写 100 行以上的"按钮去抖 + 短按长按识别 + 调光状态机 + 边界 dwell + 内存记忆"。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bSwitchDimm                : BOOL;
    bOn                        : BOOL;
    bOff                       : BOOL;
    bSetDimmValue              : BOOL;
    nDimmValue                 : BYTE;
    tSwitchOverTime            : TIME := t#400ms;
    tCycleDelay                : TIME := t#500ms;
    bMemoryModeOn              : BOOL := FALSE;
    nOnValueWithoutMemoryMode  : BYTE := 254;
    nAddr                      : BYTE := 0;
    eAddrType                  : E_DALIV2AddrType := eDALIV2AddrTypeShort;
    nMasterDevAddr             : BYTE := 0;
    nMinLevelMasterDev         : BYTE := 126;
    nMaxLevelMasterDev         : BYTE := 254;
    tCycleActualLevelMasterDev : TIME := t#0s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bSwitchDimm` | `BOOL` | — | 主控制端：连物理按钮的电平信号。短按 ON/OFF 翻转，长按 ≥ `tSwitchOverTime` 进入调光 |
| `bOn` | `BOOL` | — | 上升沿强制开灯。开灯亮度取决于 `bMemoryModeOn`（TRUE 取上次值 / FALSE 取 `nOnValueWithoutMemoryMode`）|
| `bOff` | `BOOL` | — | 上升沿强制关灯（亮度归 0）|
| `bSetDimmValue` | `BOOL` | — | 与 `nDimmValue` 配合：上升沿瞬时把 `nDimmValue` 写到输出。**静态 TRUE 时锁定**——`nDimmValue` 变化不再透传到输出，需要再次上升沿才生效（适合 HMI 数值微调场景）|
| `nDimmValue` | `BYTE` | — | 期望亮度 0..254；`bSetDimmValue = FALSE` 时变化即透传，TRUE 时被锁定 |
| `tSwitchOverTime` | `TIME` | `t#400ms` | 短按 / 长按判定阈值（典型 200 ms）。**设为 0 → `bSwitchDimm` 仅做调光、不能开关**，必须用 `bOn` / `bOff` 开关 |
| `tCycleDelay` | `TIME` | `t#500ms` | 调光到达 `nMinLevelMasterDev` 或 `nMaxLevelMasterDev` 时停顿时间，方便用户在边界松开按钮锁定全亮 / 全暗 |
| `bMemoryModeOn` | `BOOL` | `FALSE` | 记忆模式：TRUE 时下次开灯回到关灯前的亮度；FALSE 时下次开灯统一到 `nOnValueWithoutMemoryMode` |
| `nOnValueWithoutMemoryMode` | `BYTE` | `254` | 非记忆模式下的固定开灯亮度（必须落在 `nMinLevelMasterDev`..`nMaxLevelMasterDev` 范围内）|
| `nAddr` | `BYTE` | `0` | 目标地址：单灯 short address 0..63、组号 0..15、或 `eAddrType=Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort` 单灯 / `eDALIV2AddrTypeGroup` 组 / `eDALIV2AddrTypeBroadcast` 全线广播 |
| `nMasterDevAddr` | `BYTE` | `0` | "主设备"短地址 0..63——组 / 广播控制时本 FB 跟踪该单灯的实际亮度作"参考值"（避免组内多灯亮度不同时无法判断"现在算开还是关"）。`eAddrTypeShort` 时本字段不参与 |
| `nMinLevelMasterDev` | `BYTE` | `126` | 调光下限（DALI 标准下限是 1，但 `126` 对应中等亮度 ~10%，避免用户调到全黑）|
| `nMaxLevelMasterDev` | `BYTE` | `254` | 调光上限（最大 254 即 100% 满载）|
| `tCycleActualLevelMasterDev` | `TIME` | `t#0s` | 后台读 `nMasterDevAddr` 实际亮度的周期。`0` 禁用（默认）；非 0 时本 FB 周期性下发 low-priority "QUERY ACTUAL LEVEL" 命令，结果填入 `nActualLevelMasterDev`。读操作走 low priority 不影响调光下发 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nActualLevelMasterDev : BYTE;
    bBusy                 : BOOL;
    bError                : BOOL;
    nErrorId              : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nActualLevelMasterDev` | `BYTE` | "主设备"当前亮度（0..254）。`eAddrTypeShort` 时即被控单灯的实际亮度。HMI 显示用 |
| `bBusy` | `BOOL` | 任一命令在派发到 `FB_KL68x1Communication` 缓冲区或等待 DALI 响应时为 TRUE |
| `bError` | `BOOL` | 命令执行错（`nAddr` 越界 / 设备无响应等）|
| `nErrorId` | `UDINT` | 错误号；全库共表 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区；连到对应 KL6821/6811 通信 FB 的同名变量 |

## 3. 行为说明

**`bSwitchDimm` 状态机**：上升沿启动计时，三类终态——
1. **短按**：信号在 `tSwitchOverTime` 内消失（默认 < 400 ms）→ 翻转开关。如果当前是 OFF（亮度 0），则按 `bMemoryModeOn` 选取"上次值"或 `nOnValueWithoutMemoryMode` 开灯；如果当前是 ON（亮度 > 0），则关灯（亮度 → 0）。
2. **长按**：信号持续 > `tSwitchOverTime` → 进入调光模式。当前如果是 OFF 则先开灯到 `nOnValueWithoutMemoryMode`（或上次值），然后亮度按 DALI Fade 速率连续变化在 `nMinLevelMasterDev` 与 `nMaxLevelMasterDev` 之间；触到上 / 下限时停 `tCycleDelay` 方便锁定，然后回弹反向继续。
3. **长按中途短暂松开后再按**：本 FB 识别为"反向"——本来在亮度上升的话变成下降，反之亦然。这是楼宇照明面板的标准 UX："长按一直加亮，加过头了短按一下立即变变暗"。

**`bOn` / `bOff`** 是强制开关，**上升沿触发**，与 `bSwitchDimm` 状态机并行：例如可以接一个独立的"开"按钮和"关"按钮，与摸索式调光按钮并存。

**`bSetDimmValue` + `nDimmValue` 双重语义**：（1）`bSetDimmValue = FALSE` 时 `nDimmValue` 的变化即透传——HMI 调亮度滑块边滑动边看灯实时反应；（2）`bSetDimmValue = TRUE` 静态高电平时 `nDimmValue` 不透传——HMI 可以把目标值填好但等用户按"确认"按钮（即给 `bSetDimmValue` 一次上升沿）才下发。`nDimmValue` 必须在 `nMinLevelMasterDev`..`nMaxLevelMasterDev` 范围内，越界自动钳位；**`nDimmValue = 0` 是特例，代表关灯**。

**记忆模式（`bMemoryModeOn`）**：影响"从 OFF 切到 ON"时的目标亮度——TRUE 时本 FB 在内部记住关灯前的最后亮度，下次开灯先调到该值；FALSE 时无论上次什么亮度都统一开到 `nOnValueWithoutMemoryMode`。后者更适合需要固定起点的工艺场景（如医院 / 实验室照明）；前者更适合家用 / 办公（用户体验是"灯还是上次那么亮"）。

**`nMasterDevAddr` 的设计意图**：DALI 组 / 广播控制时，组内多灯当前亮度可能不同（有些可能被单独调过）。组命令下发后没法知道"现在算 ON 还是 OFF"——本 FB 选一个组员作"主设备"，跟踪其单灯亮度作判断依据：主设备亮度 > 0 即认为本组 ON，主设备 = 0 即 OFF。`tCycleActualLevelMasterDev` 控制后台查询主设备亮度的周期；设为 0 则禁用查询，主设备亮度仅靠本 FB 内部跟踪（不会自动校正用户用其它工具直接改了主设备亮度的情况）。**`eAddrTypeShort` 单灯模式下 `nMasterDevAddr` 无效**——直接以 `nAddr` 单灯亮度为参考。

**`tSwitchOverTime = 0` 的特殊行为**：本 FB 把 `bSwitchDimm` 仅当调光按钮使用——长按调光、短按无效。开关必须用 `bOn` / `bOff` 配套独立按钮。

**`nMinLevelMasterDev = 126`** 是物理意义为"DALI 中等亮度（约 10% 物理亮度）"。DALI 亮度是对数曲线，0 = 关 / 1 = ~0.1% / 254 = 100%。把下限设到 126 而不是 1 避免用户调到"几乎全黑只剩一点"的不实用状态，对楼宇照明友好；专业舞台 / 摄影场景可降到 1。

**典型陷阱**：① 把 `bSwitchDimm` 接物理按钮时忘了去抖（DALI 命令会被多次触发，调光状态机错乱）—— 实际工程在 IL/ST 加一段 R_TRIG 去抖；② `nOnValueWithoutMemoryMode` 不在 `nMinLevel..nMaxLevel` 范围内 → 本 FB 自动钳位到边界但用户可能困惑；③ `bMemoryModeOn` 在线切换 → 切换瞬间不影响当前亮度，下次开关时才生效；④ 组控制下没设 `nMasterDevAddr` 默认 0，如果短地址 0 灯并不存在 → 主设备查询会持续报错；⑤ 组员有的被设了独立 short address 用其它 FB 控过，导致本 FB 看到的"组亮度"与实际不符。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。本 FB 主要错误来自下发的"setDimmValue / Off / RecallMaxLevel" 等基础命令：

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#1xxx` | 设备无响应（`nAddr` 错或灯不在线）| 用 `FB_DALIV2QueryActualLevel` 单独验证目标灯能否查询到 |
| `16#2xxx` | 命令缓冲区溢出 | 调短 `FB_KL68x1Communication` 任务节拍 |
| `16#3xxx` | 主设备查询错（`nMasterDevAddr` 灯不存在）| 确认 master 设备真实存在；或把 `tCycleActualLevelMasterDev` 设为 0 关闭查询 |

## 5. 使用注意 / 常见坑

- **物理按钮去抖**：`bSwitchDimm` 接机械按钮必须 PLC 端先 R_TRIG/F_TRIG 去抖，否则一次按下可能被解释为多次短按。
- **`nMinLevelMasterDev` < `nMaxLevelMasterDev`**：反了的话本 FB 行为未定义；通常 PLC 编译期就该校验。
- **`tCycleDelay` 不宜过短**：太短（< 200 ms）用户来不及在边界松开锁定全亮 / 全暗；太长（> 1 s）显得反应迟钝。500 ms 是文档推荐值。
- **记忆模式与多套调光面板共享一灯**：如果同一盏灯被多个本 FB 实例控制（楼梯间不同楼层都能调），各实例记忆值独立——下次开灯按"哪个实例最后操作"决定亮度可能不一致。一般做法是把多个实例共享同一外部 retain 变量存"上次亮度"。
- **组 / 广播模式下 `nMasterDevAddr` 必须存在**：master 不存在 → 后台查询持续报 `bError`，干扰 HMI 错误指示。
- **`tCycleActualLevelMasterDev` 与命令吞吐**：非 0 时本 FB 周期性下发 low-priority 查询命令；设过短（< 200 ms）会让 low buffer 频繁排队，与其它 low-priority FB 抢资源。500..1000 ms 是均衡值。
- **`bOn` / `bOff` 同时上升沿不可预测**：编程时确保两个不会同时上升（用同一个按钮一对、或 IF-ELSIF 互斥）。
- **本 FB 一定基于已配置好的 KL68x1 通信链**：先确认 `FB_KL68x1Communication.bLineIsInitialized = TRUE` 再让本 FB 工作，否则前几次命令进缓冲区但发不出去（HMI 看到 `bBusy` 一直 TRUE）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Dimmer1Switch.TcPOU`](../examples/P_Demo_FB_DALIV2Dimmer1Switch.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_DALIV2Dimmer1Switch
VAR
    fbDimmer1Switch : FB_DALIV2Dimmer1Switch;
    stCommandBuffer : ST_DALIV2CommandBuffer;

    bRoomButton     : BOOL;     // 房间面板按钮（短按开关 / 长按调光）
    nActualLevel    : BYTE;
END_VAR

fbDimmer1Switch(
    bSwitchDimm     := bRoomButton,
    bMemoryModeOn   := TRUE,    // 下次开灯回上次亮度
    nOnValueWithoutMemoryMode := 200,
    nAddr           := 5,       // 房间灯组 #5
    eAddrType       := eDALIV2AddrTypeGroup,
    nMasterDevAddr  := 12,      // 组内 short addr 12 灯作 master
    nMinLevelMasterDev  := 100,
    nMaxLevelMasterDev  := 254,
    tSwitchOverTime := T#400MS,
    tCycleDelay     := T#500MS,
    tCycleActualLevelMasterDev := T#1S,
    stCommandBuffer := stCommandBuffer
);

nActualLevel := fbDimmer1Switch.nActualLevelMasterDev;
```

完整工程版本（含通信 FB / 按钮去抖 / HMI 反馈）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：办公室 / 会议室 / 房间照明面板——墙上一个机械按钮（或 24 VDC PLC GPIO 接入），用户短按开 / 关、长按渐进调光。一个面板控制一组灯（5..20 个 DALI 镇流器）。也用于走廊 / 公共区灯具广播控制（一个按钮控制整条 DALI 线）。
- **价值**：替代约 100 行手写的"按钮去抖 + 短按 / 长按识别 + 调光状态机 + 边界 dwell + 记忆模式"代码；让 PLC 工程师只关心"哪盏灯（地址）+ 亮度上下限"。本 FB 内部已经处理了 DALI 帧排队、DALI Fade 速率、组成员状态跟踪等细节。
- **替代方案对比**：
  - 自写状态机：可控但 100 行起步、不同工程难复用、漏边界情况频繁
  - 用 `FB_DALIV2Light` 单纯开关：太基础，不带调光功能
  - 用 `FB_DALIV2Dimmer2Switch`：双按钮版本——上 / 下两个按钮分别调光（专业舞台 / 影院偏好），按钮接线多一根
  - 用 `FB_DALIV2Dimmer1SwitchEco`：节能版本，支持自动关灯延时；本 FB 不带定时关灯
  - 直接发 DALI 命令（`FB_DALIV2DirectArcPowerControl` 等）：能做但要自己写所有 UX
  - **本 FB**：单按钮调光场景标准选择，覆盖 80% 的楼宇 / 办公照明面板需求

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142909067.html
- **相关**：[`FB_DALIV2Dimmer1SwitchEco`](FB_DALIV2Dimmer1SwitchEco.md)（节能版本带定时关灯）、[`FB_DALIV2Dimmer2Switch`](FB_DALIV2Dimmer2Switch.md)（双按钮调光）、[`FB_DALIV2Light`](FB_DALIV2Light.md)（纯开关）、[`FB_DALIV2DirectArcPowerControl`](../part102_low_power/FB_DALIV2DirectArcPowerControl.md)（直接亮度命令）、`E_DALIV2AddrType`（PDF §4.2.1.1）、`ST_DALIV2CommandBuffer`
