# FB_EnOceanSTM100

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6021-0023 / Read STM100 (outdated)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173265675.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOceanSTM100.TcPOU`](../examples/P_Demo_FB_EnOceanSTM100.TcPOU) |

---

## 1. 功能简述

为 KL6021-0023 体系下挂的某一个 EnOcean **STM100 房间温控面板**做"硬编码字段"友好化解析。本 FB 把 STM100 的 4 字节数据按"温度 + 设定值 + 旋钮档位 + 在场按键 + 学习按键"这种固定 mapping 直接给出可用的输出。**已废弃（PDF 标注 outdated）**——新工程应改用 `FB_EnOceanSTM100Generic` 拿原始 4 字节自己解析，避免被固定 mapping 限制。

STM100 是带温度传感器、电位器（设定值）、5 档旋钮（Auto/0/1/2/3）、在场按键、学习按键的房间面板。本 FB 把这些字段从 4 字节数据里解码后直接给：`nTemperature`（1/10 °C）、`nSetpoint`（-100..+100）、`eEnOceanRotarySwitch`（枚举档位）、`bPresentSwitch`、`bLearnSwitch`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable               : BOOL := FALSE;
    tWatchdog             : TIME;
    nTransmitterId        : UDINT;
    stEnOceanReceivedData : ST_EnOceanReceivedData;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bEnable` | `BOOL` | `FALSE` | 电平使能 |
| `tWatchdog` | `TIME` | — | watchdog 超时；STM100 周期性发送（不是按下触发），常设 `T#1h` 监视"在线状态" |
| `nTransmitterId` | `UDINT` | — | 该 STM100 房间面板的 EnOcean ID |
| `stEnOceanReceivedData` | `ST_EnOceanReceivedData` | — | 必接 `fbEnOceanReceive.stEnOceanReceivedData` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    eEnOceanRotarySwitch : E_EnOceanRotarySwitch;
    nSetpoint            : INT;
    nTemperature         : INT;
    bPresentSwitch       : BOOL;
    bLearnSwitch         : BOOL;
    bError               : BOOL := FALSE;
    nErrorId             : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `eEnOceanRotarySwitch` | `E_EnOceanRotarySwitch` | 旋钮档位枚举：`eEnOceanRotarySwitchStep0/1/2/3`（=0/1/2/3）或 `eEnOceanRotarySwitchAuto`（=4） |
| `nSetpoint` | `INT` | 设定值电位器位置，量纲 -100..+100（房间面板上下偏移设置） |
| `nTemperature` | `INT` | 测温，1/10 °C，量程 0 °C..40 °C。**watchdog 触发时本 FB 强制把 `nTemperature` 锁为 850（= 85.0 °C 类似断线值），让上层判误** |
| `bPresentSwitch` | `BOOL` | 在场按键被按下时 TRUE |
| `bLearnSwitch` | `BOOL` | 学习按键被按下时 TRUE |
| `bError` | `BOOL` | watchdog 超时 / 上游错误 |
| `nErrorId` | `UDINT` | 错误号（KL6021-0023 错误码表） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：电平触发。STM100 是周期性主动发送的温控面板（一般每数十秒一帧），不像 PTM 那种按下才发，所以推荐 `tWatchdog := T#1h` 监视"模块是否还在线 / 电池是否快没电"。

**字段映射**：本 FB 内部按 STM100 协议把 4 字节数据解码为：
- 数据字节 0 → `nTemperature`（1/10 °C，原始范围 0..255 线性映射到 0..40 °C 后乘 10）
- 数据字节 1 → `nSetpoint`（-100..+100 偏移量）
- 数据字节 2 → `eEnOceanRotarySwitch`（5 档枚举）
- 数据字节 3 / 状态位 → `bPresentSwitch`、`bLearnSwitch`

**watchdog 报错时的安全值**：与其它解析块不同，本 FB 在 watchdog 触发时**把 `nTemperature` 锁为 850（= 85.0 °C）**，这样上层"温度异常"逻辑会自然报警（85 °C 在房间场景下显然是断线值），避免控制系统按陈旧温度运行加热回路。`nSetpoint` 等其它输出仍按"FALSE/0"复位。

**与 STM100Generic 的差异**：本 FB（已废弃）做硬编码字段映射；`FB_EnOceanSTM100Generic`（推荐）只把 4 字节数据原样给出（`nDataBytes : ARRAY [0..3] OF BYTE`），应用层自己按手册解码。新工程应选 Generic 版以兼容厂商扩展字段或非标 mapping。

**典型陷阱**：① STM100 模块若是 Eltako / Thermokon 自定义协议变种，本 FB 的硬解码可能字段错位（厂商微调过 mapping），这是 Beckhoff 标本 FB 为"outdated"的核心原因；② watchdog 设 `T#0s` 会无法检测 STM100 失联，模块电池没电了 PLC 仍以最后一帧温度运行；③ `nTemperature = 850` 是断线信号不是真温度，PID 控制器需要识别该哨兵值并切到失效安全模式。

## 4. 错误码 / 返回值

`bError = TRUE` 时 `nErrorId` 同 KL6021-0023 通用错误表（§4.1.1.3）：

| `nErrorId` | 含义 |
|---|---|
| `16#0000` | 无错 |
| `16#0001` | 校验错 |
| `16#0002` | Watchdog（STM100 周期未到，模块可能离线 / 电池没电） |
| `16#0003` | KL6023 缓冲区溢出 |
| `16#0004` | 还没收到数据 |

## 5. 使用注意 / 常见坑

- **新项目用 `FB_EnOceanSTM100Generic`**：PDF 明文标本 FB outdated。当前 FB 留作老工程兼容。
- **`nTemperature = 850` 是断线哨兵**：任何上层 PID / 温度报警逻辑都要识别这个值并切到失效安全（典型做法：维持上次稳定输出、记录报警）。
- **`tWatchdog` 该设几小时**：STM100 周期发送间隔通常 100-1000 秒（取决于电池模式），`T#1h` 是安全阈值，T#15min 也可。`T#0s` 等于"放弃在线监控"。
- **`nSetpoint` 是相对偏移不是绝对设定**：-100..+100 是用户在面板上转电位器相对中间位置的偏移；真实"目标温度"= 基准温度（程序里的）+ 偏移 × 系数（典型 0.1 °C/单位）。
- **旋钮枚举对应房间模式**：Auto / 0 / 1 / 2 / 3 通常映射到 Off / 防冻 / 节能 / 舒适 / Boost。各厂商命名不同，工程里建议用 `CASE eEnOceanRotarySwitch OF ...` 显式映射不要直接拿数字算。
- **STM100 学习按键**：`bLearnSwitch = TRUE` 时可启动"模块 ID 学习"流程；在 KL6021-0023 体系下学习一般是先开 `FB_EnOceanReceive` 临时观察 `stEnOceanReceivedData.nTransmitterId`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOceanSTM100.TcPOU`](../examples/P_Demo_FB_EnOceanSTM100.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOceanSTM100
VAR
    fbEnOceanReceive : FB_EnOceanReceive;
    fbRoomPanel      : FB_EnOceanSTM100;
    stEnOceanInData  AT %I* : ST_EnOceanInData;
    stEnOceanOutData AT %Q* : ST_EnOceanOutData;
    nRoomPanelId     : UDINT := 16#000000C4;
    nRoomTempTenths  : INT;
    nRoomSetpoint    : INT;
END_VAR
fbEnOceanReceive(bEnable := TRUE, stEnOceanInData := stEnOceanInData, stEnOceanOutData := stEnOceanOutData);
fbRoomPanel(
    bEnable               := NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable,
    tWatchdog             := T#1h,
    nTransmitterId        := nRoomPanelId,
    stEnOceanReceivedData := fbEnOceanReceive.stEnOceanReceivedData,
    nTemperature          => nRoomTempTenths,
    nSetpoint             => nRoomSetpoint
);
```

## 7. 业务场景与实际价值

- **场景**：办公楼会议室、酒店客房、住宅卧室的房间温控面板。STM100 集温度 + 设定值 + 旋钮 + 在场检测于一体，挂墙无电池零布线，提供给 HVAC 系统三方面输入：当前室温、用户偏好（旋钮档位）、用户在场（present 按键），驱动 VAV / fancoil 风量与水阀。
- **价值**：把 STM100 协议解码 + 字段映射 + 温度断线哨兵 + watchdog 综合监视封装为单 FB，应用直接拿 5 个具名输出搞 HVAC 控制策略。
- **替代方案对比**：
  - 用 `FB_EnOceanSTM100Generic`：拿 4 byte 原始，自己写解码；适合厂商扩展字段
  - 用 KNX 温控面板：需要 EIB/KNX 总线
  - 自接 KL3201 温度端子 + KL2531 电位器：要走有线，房间装修要开槽
  - **本 FB（outdated）**：STM100 老项目维护时用；新项目用 Generic 版

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.1.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173265675.html
- **相关**：`FB_EnOceanReceive`（上游必备）、`FB_EnOceanSTM100Generic`（**推荐替代**）、`E_EnOceanRotarySwitch`（旋钮档位枚举）
