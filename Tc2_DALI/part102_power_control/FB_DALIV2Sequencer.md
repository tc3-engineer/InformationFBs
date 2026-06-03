# FB_DALIV2Sequencer

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
| Example | [`examples/P_Demo_FB_DALIV2Sequencer.TcPOU`](../examples/P_Demo_FB_DALIV2Sequencer.TcPOU) |

---

## 1. 功能简述

**DALI 序列化亮度场景执行 FB（high-level）**——按 `ST_DALIV2SequenceTable` 表里定义的多步亮度 + 时长，自动按顺序播放：第一步亮度 → 等 T1 → 第二步 → 等 T2... 直到最后一步。支持 `bToggle` 在开 / 关之间切换、`bRestart` 重新开始当前序列。

适合复杂的多步定时灯效场景：舞台灯光秀、店铺橱窗循环展示、博物馆展品光照编程等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable                    : BOOL                                                    := TRUE;
    bOn                        : BOOL;
    bOff                       : BOOL;
    bToggle                    : BOOL;
    bStart                     : BOOL;
    nStartIndex                : USINT                                                   := 0;
    arrSequenceTable           : ARRAY [1..nMaxSequenceValues] OF ST_DALIV2SequenceTable;
    nOptions                   : DWORD                                                   := 0;
    nAddr                      : BYTE                                                    := 0;
    eAddrType                  : E_DALIV2AddrType                                        := eDALIV2AddrTypeShort;
    nMasterDevAddr             : BYTE                                                    := 0;
    tCycleActualLevelMasterDev : TIME                                                    := t#0s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bEnable` | `BOOL` | `TRUE` | ⚠️ 待人工确认 |
| `bOn` | `BOOL` | — | ⚠️ 待人工确认 |
| `bOff` | `BOOL` | — | ⚠️ 待人工确认 |
| `bToggle` | `BOOL` | — | 上升沿在 ON（启动序列） / OFF（停止）之间切换 |
| `bStart` | `BOOL` | — | 上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿 |
| `nStartIndex` | `USINT` | `0` | ⚠️ 待人工确认 |
| `arrSequenceTable` | `ARRAY [1..nMaxSequenceValues] OF ST_DALIV2SequenceTable` | — | ⚠️ 待人工确认 |
| `nOptions` | `DWORD` | `0` | 序列选项（保留 + 循环模式等） |
| `nAddr` | `BYTE` | `0` | 目标地址 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型 |
| `nMasterDevAddr` | `BYTE` | `0` | master 设备短地址 |
| `tCycleActualLevelMasterDev` | `TIME` | `t#0s` | 后台读 master 亮度周期 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nActualLevelMasterDev : BYTE;
    nActualIndex          : USINT;
    bLight                : BOOL;
    bSequenceActive       : BOOL;
    bBusy                 : BOOL;
    bError                : BOOL;
    nErrorId              : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nActualLevelMasterDev` | `BYTE` | master 当前亮度 |
| `nActualIndex` | `USINT` | ⚠️ 待人工确认 |
| `bLight` | `BOOL` | ⚠️ 待人工确认 |
| `bSequenceActive` | `BOOL` | 序列正在播放 |
| `bBusy` | `BOOL` | 命令派发中 |
| `bError` | `BOOL` | 出错 |
| `nErrorId` | `UDINT` | 错误号 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量 |


## 3. 行为说明

**序列定义**：通过 `stSequenceTable` VAR_IN_OUT 提供——结构包含步数 `nSteps`、每步亮度数组 `arrLevel[0..49]`、每步停留时间数组 `arrTime[0..49]`。最多 50 步。

**播放控制**：`bToggle = TRUE 上升沿` 启动序列从第 0 步开始；`bToggle = FALSE` 时序列停止（灯保持当前亮度，下次 toggle 重新开始）。`bRestart` 上升沿不影响 toggle 状态、重置回第 0 步。

**循环模式**：`nOptions` 的 bit0 决定到最后一步后是否循环——0 = 一次性、播完停在最后一步；1..31 = 保留位。

**典型应用**：店铺橱窗 24 小时光照编程（早晨渐亮、白天柔和、傍晚暖色、夜间动态）；舞台灯光秀（按音乐节拍预编好的灯效）；博物馆展品照明（白天展示 vs 夜间维护）。

**典型陷阱**：① 序列时长之和超过你打算的总时间——序列结束后停在最后一步可能不是你想要的；② `bToggle = FALSE` 中断后没有暂停的概念，下次启动从头开始；③ 序列表用 retain 变量保持工程参数，避免每次开机重写。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 最多 50 步。
- `bToggle = FALSE` 是停止不是暂停。
- 序列结束行为按 `nOptions` 决定。
- `stSequenceTable` 建议用 retain 变量。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Sequencer.TcPOU`](../examples/P_Demo_FB_DALIV2Sequencer.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：店铺橱窗 24 小时光照编程：早 6 点渐亮、9-21 点零售模式、22 点降亮、24 点关。
- **价值**：替代 PLC 自己写 50 个 TON + 状态机；序列表数据驱动，运维只改表不改代码。
- **替代方案对比**：1) 自己写 TON + 状态机：代码长且漏边界；2) `FB_DALIV2Dimmer1Switch` 等：单事件触发型，不适合序列；3) **本 FB**：多步定时灯效标准方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.2.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142922379.html
- **相关**：[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)、`ST_DALIV2SequenceTable`（DUT 结构）、[`FB_DALIV2Ramp`](FB_DALIV2Ramp.md)（单步线性渐变）
