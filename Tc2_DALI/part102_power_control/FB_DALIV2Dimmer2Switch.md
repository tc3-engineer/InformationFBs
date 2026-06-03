# FB_DALIV2Dimmer2Switch

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
| Example | [`examples/P_Demo_FB_DALIV2Dimmer2Switch.TcPOU`](../examples/P_Demo_FB_DALIV2Dimmer2Switch.TcPOU) |

---

## 1. 功能简述

**双按钮调光开关 FB（high-level）**——两个机械按钮：`bSwitchDimmUp` 长按渐亮、`bSwitchDimmDown` 长按渐暗；短按则开 / 关切换。比 `FB_DALIV2Dimmer1Switch` 多了一根按钮线，但 UX 更直观——明确的上 / 下方向。专业舞台、影院、高级会议室偏好。

可控制单灯、组或广播。共享 `nMasterDevAddr` 主设备亮度跟踪机制。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bSwitchDimmUp              : BOOL;
    bSwitchDimmDown            : BOOL;
    bOn                        : BOOL;
    bOff                       : BOOL;
    bSetDimmValue              : BOOL;
    nDimmValue                 : BYTE;
    tSwitchOverTime            : TIME             := t#400ms;
    bMemoryModeOn              : BOOL             := FALSE;
    nOnValueWithoutMemoryMode  : BYTE             := 254;
    nAddr                      : BYTE             := 0;
    eAddrType                  : E_DALIV2AddrType := eDALIV2AddrTypeShort;
    nMasterDevAddr             : BYTE             := 0;
    nMinLevelMasterDev         : BYTE             := 126;
    nMaxLevelMasterDev         : BYTE             := 254;
    tCycleActualLevelMasterDev : TIME             := t#0s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bSwitchDimmUp` | `BOOL` | — | 上方向按钮：短按开关，长按渐亮到 `nMaxLevelMasterDev` |
| `bSwitchDimmDown` | `BOOL` | — | 下方向按钮：短按开关，长按渐暗到 `nMinLevelMasterDev` |
| `bOn` | `BOOL` | — | 强制开灯（上升沿） |
| `bOff` | `BOOL` | — | 强制关灯（上升沿） |
| `bSetDimmValue` | `BOOL` | — | HMI 数值直驱（与 `nDimmValue` 配合） |
| `nDimmValue` | `BYTE` | — | 目标亮度（0..254） |
| `tSwitchOverTime` | `TIME` | `t#400ms` | 短按 / 长按阈值，典型 200..400 ms |
| `bMemoryModeOn` | `BOOL` | `FALSE` | 记忆模式（下次开灯回上次亮度） |
| `nOnValueWithoutMemoryMode` | `BYTE` | `254` | 非记忆模式开灯亮度 |
| `nAddr` | `BYTE` | `0` | 目标地址（短地址 / 组号 / 广播） |
| `eAddrType` | `E_DALIV2AddrType` | `eDALIV2AddrTypeShort` | 寻址类型 |
| `nMasterDevAddr` | `BYTE` | `0` | 主设备短地址（组 / 广播下追踪用） |
| `nMinLevelMasterDev` | `BYTE` | `126` | 调光下限 |
| `nMaxLevelMasterDev` | `BYTE` | `254` | 调光上限 |
| `tCycleActualLevelMasterDev` | `TIME` | `t#0s` | 后台读主设备亮度周期，0 禁用 |

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
| `nActualLevelMasterDev` | `BYTE` | 主设备当前亮度（HMI 显示用） |
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

**双按钮状态机**：每个按钮独立判定短按 / 长按。短按（< `tSwitchOverTime`）任一按钮翻转开关；长按 `bSwitchDimmUp` 渐亮、长按 `bSwitchDimmDown` 渐暗，触到上 / 下限停 `tCycleDelay` 后回弹反向。与 `Dimmer1Switch` 区别：方向明确不需要『反向短松』。

**`bOn` / `bOff` 强制**：上升沿强制开关，与按钮调光并行。

**HMI 数值直驱**：`bSetDimmValue = FALSE` 时 `nDimmValue` 变化即透传；TRUE 时锁定等待上升沿。

**记忆模式**：同 `Dimmer1Switch`。

**`nMasterDevAddr` 跟踪**：组 / 广播控制时跟踪一盏主设备亮度作参考。

**典型陷阱**：① 两按钮同时长按 → 行为未定义（FB 内部按谁先按下处理）；② 按钮接线时上 / 下搞反——用户体验完全反向，但 PLC 可以一键软改换 `bSwitchDimmUp` / `Down` 接线即可。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 上下按钮接反时整套 UX 反向——上线时务必测试方向。
- 两按钮同时按行为未定义，PLC 端应互斥。
- 其它行为同 `FB_DALIV2Dimmer1Switch`，包括 EEPROM 写次数 / 主设备跟踪等。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2Dimmer2Switch.TcPOU`](../examples/P_Demo_FB_DALIV2Dimmer2Switch.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：影院 / 剧院 / 舞台技术控制台——专业操作员偏好明确的方向按钮，长按上 = 渐亮、长按下 = 渐暗。短按任一按钮开关，匹配业内传统调光台 UX。
- **价值**：比 `Dimmer1Switch` UX 更直观，专业场景偏好；同样封装短按 / 长按识别、调光状态机、DALI 命令排队。
- **替代方案对比**：1) `FB_DALIV2Dimmer1Switch`：单按钮版本，普通楼宇照明首选；2) **本 FB**：专业 / 双按钮场景首选；3) `FB_DALIV2Dimmer2SwitchEco`：节能版本带定时关灯。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142913675.html
- **相关**：[`FB_DALIV2Dimmer1Switch`](FB_DALIV2Dimmer1Switch.md)、[`FB_DALIV2Light`](FB_DALIV2Light.md)、[`FB_DALIV2LightControl`](FB_DALIV2LightControl.md)
