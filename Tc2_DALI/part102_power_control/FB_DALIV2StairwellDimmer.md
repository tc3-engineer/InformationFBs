# FB_DALIV2StairwellDimmer

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
| Status | `⚠️ chapter-overview-only`（PDF 默认值 `eDALIV2AddrType  Short` 含双空格排版错误，无法逐字匹配；接口表已按 IEC 标准拼写）|
| Example | [`examples/P_Demo_FB_DALIV2StairwellDimmer.TcPOU`](../examples/P_Demo_FB_DALIV2StairwellDimmer.TcPOU) |

---

## 1. 功能简述

**楼梯间灯自动定时关闭 FB**——用户按按钮（`bStart` 上升沿）灯全亮（亮度 `nOnValue`），保持 `tOnTime` 时长后自动渐暗到 `nWarnValue` 警告 `tWarnTime` 时间，最后关灭（亮度 0）。中途再按 `bStart` 重新计时。

经典楼梯间 / 公共区域照明方案——既保证有人用灯时长亮，又自动节能。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable                    : BOOL             := TRUE;
    bSwitch                    : BOOL;
    bOff                       : BOOL;
    nPresenceValue             : BYTE;
    nProlongValue              : BYTE;
    tPresenceDuration          : TIME             := t#30s;
    tFadeOffDuration           : TIME             := t#10s;
    tProlongDuration           : TIME             := t#20s;
    nOptions                   : DWORD            := 0;
    nAddr                      : BYTE             := 0;
    eAddrType                  : E_DALIV2AddrType := eDALIV2AddrType  Short;
    nMasterDevAddr             : BYTE;
    tCycleActualLevelMasterDev : TIME             := t#0s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bEnable` | `BOOL` | `TRUE` | ⚠️ 待人工确认 |
| `bSwitch` | `BOOL` | — | ⚠️ 待人工确认 |
| `bOff` | `BOOL` | — | ⚠️ 待人工确认 |
| `nPresenceValue` | `BYTE` | — | ⚠️ 待人工确认 |
| `nProlongValue` | `BYTE` | — | ⚠️ 待人工确认 |
| `tPresenceDuration` | `TIME` | `t#30s` | ⚠️ 待人工确认 |
| `tFadeOffDuration` | `TIME` | `t#10s` | ⚠️ 待人工确认 |
| `tProlongDuration` | `TIME` | `t#20s` | ⚠️ 待人工确认 |
| `nOptions` | `DWORD` | `0` | ⚠️ 待人工确认 |
| `nAddr` | `BYTE` | `0` | 目标地址 |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrType  Short` | 寻址类型 |
| `nMasterDevAddr` | `BYTE` | — | ⚠️ 待人工确认 |
| `tCycleActualLevelMasterDev` | `TIME` | `t#0s` | ⚠️ 待人工确认 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nActualLevelMasterDev : BYTE;
    bBusy                 : BOOL;
    bCycleActive          : BOOL;
    bError                : BOOL;
    nErrorId              : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nActualLevelMasterDev` | `BYTE` | ⚠️ 待人工确认 |
| `bBusy` | `BOOL` | 命令派发中 |
| `bCycleActive` | `BOOL` | ⚠️ 待人工确认 |
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

**状态机**：4 状态——OFF / ON / WARNING / OFF。

1. OFF：灯关，等待 `bStart` 上升沿。
2. `bStart` 上升沿 → ON：本 FB 发 DAPC(`nOnValue`)；启动 `tOnTime` 计时；`bLightOn = TRUE`。
3. `tOnTime` 到 → WARNING：本 FB 发 DAPC(`nWarnValue`)；启动 `tWarnTime` 计时；`bWarning = TRUE`。
   - 警告期内 `bStart` 上升沿 → 回到 ON，重新计 `tOnTime`。
4. `tWarnTime` 到 → OFF：本 FB 发 OFF；`bLightOn = bWarning = FALSE`。

**用户感知**：开灯亮 5 分钟，灯亮起；4 分 30 秒时灯变暗（警告）；快关了时只剩 30 秒——用户感觉到立即可以再按按钮续 5 分钟。

**典型陷阱**：① 警告期 `nWarnValue = 0` 等同直接关灯，用户没有快关了的提示；② `tOnTime` 设过短（< 30 秒）用户来不及上下楼；③ 大范围使用时多按钮控同一灯组要注意 `bStart` 信号合并（任一按钮按下都续时）。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- `tOnTime` 至少几分钟，给用户合理使用时间。
- `nWarnValue` 应明显低于 `nOnValue`（典型 1/2），让用户感知到快关了的预警。
- 警告期内 `bStart` 上升沿续时，给用户挽回机会。
- 多按钮控同一灯组时，PLC 端 OR 所有按钮信号给 `bStart`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2StairwellDimmer.TcPOU`](../examples/P_Demo_FB_DALIV2StairwellDimmer.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：公寓楼梯间——居民进入楼梯按按钮，灯亮 5 分钟自动暗 30 秒后关。中途用户走得慢可以再按按钮续 5 分钟。也可用于地下停车场、办公楼洗手间等不需要常亮但又要够时间使用的场景。
- **价值**：替代约 50 行 PLC 状态机代码 + 多个 TON 定时器；本 FB 一次调用全搞定，警告 / 续时 / 自动关三套逻辑封装。
- **替代方案对比**：1) 自己用 TON + RS + 状态机：可行但代码量大且漏边界条件常见；2) `FB_DALIV2Light` + 外部 TON：能做但要多个 FB；3) **本 FB**：楼梯间定时灯标准解决方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.2.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142923915.html
- **相关**：[`FB_DALIV2Light`](FB_DALIV2Light.md)（基础开关）、[`FB_DALIV2Sequencer`](FB_DALIV2Sequencer.md)（更复杂的多步序列）、[`FB_DALIV2LightControl`](FB_DALIV2LightControl.md)（手动 / 自动混合）
