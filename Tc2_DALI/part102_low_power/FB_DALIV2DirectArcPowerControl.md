# FB_DALIV2DirectArcPowerControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Low-Level / Power Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2DirectArcPowerControl.TcPOU`](../examples/P_Demo_FB_DALIV2DirectArcPowerControl.TcPOU) |

---

## 1. 功能简述

**直接设亮度命令（Direct Arc Power Control，DAPC）**——DALI Part 102 控制设备（control gear）的核心命令，一次性把目标镇流器（单灯 / 组 / 全广播）的亮度直接设为 `nArcPowerLevel`（0..254；0 = 灯关）。若被控灯当前是关的状态，本命令会自动开灯到目标值；目标值超出灯具自身配置的 `MAX VALUE` / `MIN VALUE` 时被钳位到对应边界。亮度从当前值变化到目标值的速率由灯具寄存器 `FADE TIME` 决定（用 `FB_DALIV2SetFadeTime` 提前设置）。

这是所有上层调光 FB（`FB_DALIV2Dimmer1Switch` / `FB_DALIV2Light` / `FB_DALIV2GoToScene` 等）最终都会用到的最底层"设亮度"命令。需要完全自定义调光时序时直接用本 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    nAddr            : BYTE;
    eAddrType        : E_DALIV2AddrType := eDALIV2AddrTypeShort;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nArcPowerLevel   : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nAddr` | `BYTE` | — | 目标地址：单灯 short address 0..63、组号 0..15、或 `eAddrType = Broadcast` 时忽略 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播）|
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序 |
| `nArcPowerLevel` | `BYTE` | — | 目标亮度索引 0..254（DALI 对数曲线，0 = 关灯 / 254 = 100% 物理亮度 / 128 ≈ 10% 物理亮度）。超过灯具 `MAX VALUE` / `MIN VALUE` 寄存器配置时灯具内部钳位到边界 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrorId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE |
| `bError` | `BOOL` | 执行错时置 TRUE；下次 `bStart` 上升沿自动复位 |
| `nErrorId` | `UDINT` | 错误号（命令专用）；详见 §4 错误码表与全库错误码 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量。整条 KL68x1 链路上所有命令 FB 共享这一变量 |

## 3. 行为说明

**调用方式**：`bStart` 上升沿触发一次执行；本 FB 把"DAPC `nArcPowerLevel` 给 `nAddr` 这盏 / 组 / 全部灯"这条 8-bit DALI 命令排进 `stCommandBuffer` 的 `eCommandPriority` 队列；通信 FB 取出后下发到 DALI 物理总线（约 14 ms 帧时间）；下发完成 `bBusy` 回 FALSE。

**亮度变化时序**：本 FB 仅下发"目标亮度"命令，**真实变化速率由被控灯具自身的 `FADE TIME` 寄存器决定**（0..15 索引对应 0..90.5 秒）。例如 `FADE TIME = 4`（约 2.83 秒）时，调用 DAPC 把亮度从 0 变到 254 灯具会用 2.83 秒线性渐变（DALI 是对数曲线，看上去更平滑）。要做"瞬时跳变"需先用 `FB_DALIV2SetFadeTime` 把 `FADE TIME` 设为 0；要做"长时间渐进"需先调到大值。**Fade 期间再下一次 DAPC 立即覆盖目标，灯具会从当前中间亮度按新目标重新 Fade**。

**DAPC 序列模式**：如果在 `FB_DALIV2EnableDAPCSequence` 启用了序列模式，**连续多次 DAPC 命令必须每条间隔 ≤ 200 ms**——超时灯具自动退出序列模式回到普通响应。这是用本 FB 做连续平滑调光时（自己写 Fade 算法）必须注意的；普通单点 DAPC 不受此约束。

**关灯特例**：`nArcPowerLevel = 0` 一定是关灯，无视灯具 `MIN VALUE`（DALI 规范规定）。要"调到最低但不关灯"应使用 `MIN VALUE`（典型 `1`，即对数曲线最暗的非零档）。

**典型陷阱**：① 期望"瞬时跳变"但灯具 `FADE TIME` 是默认值（4 即 2.83 秒）→ 看上去命令"延迟生效"。先用 `FB_DALIV2SetFadeTime` 把 FADE TIME 设为 0；② 启用 DAPC 序列模式后两次调用间隔 > 200 ms → 第二条按普通命令处理而非序列内，时序可能错乱；③ `nArcPowerLevel` 直接用 1..254 范围以为是物理亮度——DALI 是对数曲线，`128` 对应物理亮度约 10%，不是 50%；④ 广播下发后立即查询亮度（`FB_DALIV2QueryActualLevel`）→ Fade 还没结束读到的是中间值。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。本 FB 主要错误：

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0001..3` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#0xxx` | DALI 总线无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#1xxx` | `nAddr` 越界 / `eAddrType` 不匹配 | 短地址 0..63 / 组号 0..15 / Broadcast 时 `nAddr` 任意 |

## 5. 使用注意 / 常见坑

- **`nArcPowerLevel = 0` 一定关灯**，与 `MIN VALUE` 寄存器无关；想"最暗不关"用 `MIN VALUE`（默认 `1`）。
- **亮度变化速率由灯具 `FADE TIME` 寄存器决定**，不是本 FB 控制——要瞬时跳变先把 `FADE TIME` 设为 `0`。
- **DAPC 是 DALI 最高频命令**，业务上批量下发时务必用 `eCommandPriorityMiddle` 或 `Low`，避免 `High` 队列被它独占而紧急关灯命令排不上去。
- **DAPC 序列模式**（`FB_DALIV2EnableDAPCSequence`）下连续命令必须 ≤ 200 ms 间隔；超时退出序列。
- **组 / 广播下发后查询亮度**时务必等 Fade 完成（典型 1..3 秒）才有意义。
- **本 FB 的 `nArcPowerLevel` 是对数曲线索引**（0..254），不是物理亮度百分比——`128` 不等于 50% 亮度。要"看上去 50%"用 DALI 自带的对数曲线对照表（`128` ≈ 物理 10%；`193` ≈ 物理 50%；`254` = 100%）。
- **灯具断电再上电后**未配置 `POWER ON LEVEL` 时初始亮度未知；建议工程上电先广播一次 DAPC 把所有灯归位到已知值。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2DirectArcPowerControl.TcPOU`](../examples/P_Demo_FB_DALIV2DirectArcPowerControl.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：所有需要"瞬时把 DALI 灯调到精确目标亮度"的场景：HMI 数值滑块调光、自定义渐变曲线编程（用 PLC 循环连续 DAPC 做特效）、舞台 / 演出灯光秒级精确控制、应急照明强制亮度切换。也是所有 high-level 调光 FB 的底层实现。
- **价值**：直接对应 IEC 62386 Part 102 的 8-bit DAPC 命令，是 DALI 协议最频繁使用的命令。本 FB 把"地址编码 + 命令字节 + 三优先级排队 + 错误处理"封装成 4 行调用。不用本 FB 要自己写 DALI 字节级 frame builder + 队列管理，工作量极大。
- **替代方案对比**：1) `FB_DALIV2Dimmer1Switch` / `Dimmer2Switch` / `Light`：高层调光 FB，封装了 UX 逻辑，普通工程优先选高层；2) `FB_DALIV2GoToScene` / `RecallMaxLevel` / `RecallMinLevel`：预设场景命令，比 DAPC 自动应用 `MAX VALUE` / `MIN VALUE` / `SCENE n VALUE`，可以省一些寄存器写；3) **本 FB**：最底层、最灵活，写自定义渐变曲线 / 复杂时序时唯一选择。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.3.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142766475.html
- **相关**：[`FB_DALIV2Dimmer1Switch`](../part102_power_control/FB_DALIV2Dimmer1Switch.md)（高层包装）、[`FB_DALIV2EnableDAPCSequence`](FB_DALIV2EnableDAPCSequence.md)（启用 DAPC 序列模式做平滑长渐变）、[`FB_DALIV2SetFadeTime`](../part102_low_config/FB_DALIV2SetFadeTime.md)（设置灯具 FADE TIME 控制 DAPC 渐变速率）、[`FB_DALIV2GoToScene`](FB_DALIV2GoToScene.md)（预设场景命令）、[`FB_DALIV2QueryActualLevel`](../part102_low_queries/FB_DALIV2QueryActualLevel.md)（查询当前实际亮度）、`E_DALIV2AddrType` / `E_DALIV2CommandPriority`（DUT 枚举）
