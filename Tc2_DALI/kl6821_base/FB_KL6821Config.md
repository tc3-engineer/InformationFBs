# FB_KL6821Config

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6821 Base` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL6821Config.TcPOU`](../examples/P_Demo_FB_KL6821Config.TcPOU) |

---

## 1. 功能简述

**KL6821 端子参数化 FB**——把 KBus 看门狗触发的 DALI 命令、两个数字输入（DI1 / DI2）上升 / 下降沿映射的 DALI 命令、端子内置 DALI 电源工作模式（全开 / 仅故障时启用 / 关闭）等参数写到 KL6821 的失电保护寄存器；同时把端子真实过程映像桥接到内部 `stInData` / `stOutData`，供下游 `FB_KL6821Communication` 使用。本 FB 必须在 PLC 上电时调用一次（或通过 `bConfigurate` 上升沿手动触发再次配置）。

**配置期间不下发 DALI 命令**：本 FB 处于 `bBusy = TRUE` 时，下游通信 FB 暂停所有 DALI 命令派发，配置完成后接管端子过程映像。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bConfigurate           : BOOL := FALSE;
    eCommandKBusWatchdog   : E_DALIV2ConfigurationCommands := eDALIV2CommandDoNothing;
    eCommandDI1RisingEdge  : E_DALIV2ConfigurationCommands := eDALIV2CommandOff;
    eCommandDI1FallingEdge : E_DALIV2ConfigurationCommands := eDALIV2CommandDoNothing;
    eCommandDI2RisingEdge  : E_DALIV2ConfigurationCommands := eDALIV2CommandRecallMaxLevel;
    eCommandDI2FallingEdge : E_DALIV2ConfigurationCommands := eDALIV2CommandDoNothing;
    ePowerSupplyMode       : E_DALIV2PowerSupplyMode := eDALIV2PowerSupplyModeOn;
    nOptions               : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bConfigurate` | `BOOL` | `FALSE` | 上升沿触发端子配置；PLC 程序启动时一般直接置 TRUE 让上电就跑一次配置 |
| `eCommandKBusWatchdog` | `E_DALIV2ConfigurationCommands` | `eDALIV2CommandDoNothing` | KBus 看门狗超时（端子约 200 ms 未被 K-Bus 主访问）时端子自动下发的 DALI 命令；默认"不做事"，安全应用通常改 `eDALIV2CommandOff` 让灯灭、或 `eDALIV2CommandRecallMaxLevel` 让灯全亮（应急）|
| `eCommandDI1RisingEdge` | `E_DALIV2ConfigurationCommands` | `eDALIV2CommandOff` | 端子 DI1 上升沿触发的 DALI 命令；典型用法是接面板按钮"关灯" |
| `eCommandDI1FallingEdge` | `E_DALIV2ConfigurationCommands` | `eDALIV2CommandDoNothing` | DI1 下降沿命令 |
| `eCommandDI2RisingEdge` | `E_DALIV2ConfigurationCommands` | `eDALIV2CommandRecallMaxLevel` | DI2 上升沿命令；默认"全亮"——配合楼梯间按钮一键开灯 |
| `eCommandDI2FallingEdge` | `E_DALIV2ConfigurationCommands` | `eDALIV2CommandDoNothing` | DI2 下降沿命令 |
| `ePowerSupplyMode` | `E_DALIV2PowerSupplyMode` | `eDALIV2PowerSupplyModeOn` | KL6821 内置 DALI 电源工作模式：`On`（始终供电）/ `Off`（关闭，由外部 DALI PSU 供电）/ `Auto`（端子检测无外部 PSU 时自动开内置电源）|
| `nOptions` | `DWORD` | `0` | 保留位 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy                      : BOOL;
    bError                     : BOOL;
    nErrorId                   : UDINT;
    nTerminalDescription       : WORD;
    nFirmwareVersion           : WORD;
    sDescription               : STRING;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 配置进行中（读 / 写寄存器、读端子信息）。`bBusy = TRUE` 期间下游通信 FB 暂停 DALI 命令派发 |
| `bError` | `BOOL` | 配置错误（看 `nErrorId`），常因端子无响应或参数非法 |
| `nErrorId` | `UDINT` | 错误号；与 Tc2_DALI 全库错误码共表 |
| `nTerminalDescription` | `WORD` | 端子名称编号，正常应读出 `6821`（10 进制），对应端子寄存器 8 |
| `nFirmwareVersion` | `WORD` | 端子固件版本编号，对应端子寄存器 9（如 `2#10001000` 即 firmware "2H"）|
| `sDescription` | `STRING` | 上述两项的人类可读字符串，例如 "Terminal KL6821 / Firmware 2H" |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stInDataTerminal         : ST_KL6821InData;
    stOutDataTerminal        : ST_KL6821OutData;
    stInData                 : ST_KL6821InData;
    stOutData                : ST_KL6821OutData;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stInDataTerminal` | `ST_KL6821InData` | KL6821 真实输入过程映像；在 SysMgr 链到端子 IO 字节区 |
| `stOutDataTerminal` | `ST_KL6821OutData` | KL6821 真实输出过程映像；同上 |
| `stInData` | `ST_KL6821InData` | 内部桥结构——再传给 `FB_KL6821Communication.stInData` |
| `stOutData` | `ST_KL6821OutData` | 内部桥结构——再传给 `FB_KL6821Communication.stOutData` |

## 3. 行为说明

**配置流程**：`bConfigurate` 上升沿触发，本 FB 进入 `bBusy = TRUE`，依次（1）读端子识别寄存器（reg 8 / reg 9）填 `nTerminalDescription` / `nFirmwareVersion` / `sDescription`；（2）写 KBus 看门狗 DALI 命令到端子寄存器；（3）写 DI1 / DI2 四个边沿命令到端子寄存器；（4）写电源模式寄存器；（5）切换端子到运行模式。整套流程约 5..20 ms，完成后 `bBusy` 回 FALSE。

**与通信 FB 的协作**：标准接法是 `stInDataTerminal` / `stOutDataTerminal` 连真实 KL6821 端子 IO，`stInData` / `stOutData` 连一对**内部 VAR**（不映射任何物理 IO），同一对内部 VAR 再传给 `FB_KL6821Communication.stInData` / `stOutData`。本 FB 在配置阶段独占端子 IO，配置完后把控制权"交"给通信 FB（实现上通过两个 IN_OUT 桥）。两个 FB 必须在同一 PLC 任务调用。

**KBus 看门狗的含义**：K-Bus 总线主（CX）若约 200 ms 未刷新 KL6821 寄存器（PLC 死机、CPU 满载等），端子内部看门狗触发，端子自动按 `eCommandKBusWatchdog` 配置的命令向 DALI 总线下发——这是工业照明的"故障安全"机制：PLC 挂了灯还能按工程师选的状态运行（默认 `eDALIV2CommandDoNothing` 即保持现状；安全 / 应急场景应改 `eDALIV2CommandRecallMaxLevel` 让全亮）。

**DI1 / DI2 的硬触发机制**：KL6821 端子上的两路数字输入（24 VDC，用机械按钮或 PLC GPIO 接入）被配置成"端子自身上升 / 下降沿触发指定 DALI 命令"，**这条命令由 KL6821 端子直接下发，不经 PLC**。所以即便 PLC CPU 满载、扫描周期长到 200 ms，按下按钮也能亚秒级响应——这是楼层走廊一键开关、应急按钮一键全亮等场景的底层硬件保障。代价是 DI 触发后端子会暂时锁定过程映像（`bProcessImageInactive`），PLC 侧的命令需要等 `bResetInactiveProcessImage` 上升沿才能继续。

**`ePowerSupplyMode` 三种选择**：（1）`On` 默认，KL6821 自身提供 DALI 总线 16 V 供电——适合小 DALI 网（<32 个负载，纯 KL6821 供电够用）；（2）`Off` 关闭内置电源，由外部 DALI PSU 供电——适合大网（>32 负载）或现场已存在 DALI PSU；（3）`Auto` 端子检测外部 PSU 存在与否自动切换，最省心但偶有切换冲突报警。

**典型陷阱**：① 不调本 FB 直接用通信 FB → KBus 看门狗未配置，PLC 死机时端子保持最后状态可能造成事故；DI 边沿命令也是默认值，端子按钮按下做的不一定是你想要的事；② `bConfigurate` 反复上升沿（HMI 按错） → 配置期间所有 DALI 命令排队等待，业务停滞；③ 内部桥 `stInData` / `stOutData` 误连真实 IO → 编译过但 KL6821 配置和命令都不到端子。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 `error_handling/Error_Codes.md`）。配置阶段最常见：

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0007` | 端子无响应 | 检查 KL6821 是否在 K-Bus 链路中，IO mapping 是否完整 |
| `16#0008` | 端子固件版本不支持当前配置 | 升级 KL6821 固件，或降级 / 调整配置项 |
| `16#0009` | 参数非法（`eCommandX`）| 检查枚举值是否合法 |
| `16#000A` | 寄存器写超时 | 检查 K-Bus 状态；端子可能有故障 |

**注**：上述错误码取值是基于全库错误表的常见配置错（PDF §4.1.4）；如端子完全离线，会先以 `16#0007` 报，且 `nTerminalDescription` 始终为 0。

## 5. 使用注意 / 常见坑

- **上电必须先调本 FB**：标准模板就是 `bConfigurate := TRUE` 永远保持（程序首次扫描时上升沿触发配置；之后稳态高电平不会重复触发）。某些工程把 `bConfigurate` 默认 FALSE 是错的——端子不被配置，KBus 看门狗失效。
- **`eCommandKBusWatchdog` 必须按业务选**：安全照明 / 应急场景应选 `eDALIV2CommandRecallMaxLevel`（PLC 死机全亮）；普通照明可选 `eDALIV2CommandDoNothing`（保持现状）或 `eDALIV2CommandOff`（PLC 死机全灭）。默认值 `DoNothing` 在多数工程会过审，但要工程师明确认可。
- **DI 边沿命令是端子直接执行的硬功能**：即便 PLC 卡死也响应。如果不希望端子上 DI 触发任何 DALI 命令（例如 DI 已被复用为其它用途），把四个 `eCommandDIxX` 全设 `eDALIV2CommandDoNothing`。
- **`ePowerSupplyMode` 决定 DALI 网拓扑**：小网 `On`（内置 PSU 供电）；大网必须外置 PSU，把本字段置 `Off` 避免内置电源和外置 PSU 冲突。`Auto` 不推荐用于关键应用（切换瞬间灯具可能闪烁）。
- **同时只能有一个本 FB 实例操作同一 KL6821**：与通信 FB 同样，多实例必定冲突。
- **配置完成后 `bConfigurate` 维持 TRUE 不会反复触发**：内部是上升沿检测，稳态高电平只在第一次的上升沿生效。若需要在线重新配置（改了 DI 命令映射），需先把 `bConfigurate := FALSE`，等 `bBusy` 回 FALSE 后再置 TRUE。
- **配置时下游命令排队但不丢**：`FB_KL6821Communication` 在配置期间继续接收命令进 `stCommandBuffer`，配置完成后自动开始派发——所以上层应用不需要感知本 FB 正在配置。
- **`sDescription` 是调试金钥**：上线第一件事就看 `sDescription`——如果是空串或非 KL6821 字样，IO mapping 必有错。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL6821Config.TcPOU`](../examples/P_Demo_FB_KL6821Config.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_KL6821Config
VAR
    fbKL6821Config : FB_KL6821Config;
    stTerminalIn   AT %I* : ST_KL6821InData;
    stTerminalOut  AT %Q* : ST_KL6821OutData;
    stBridgeIn     : ST_KL6821InData;
    stBridgeOut    : ST_KL6821OutData;
    bConfigEnable  : BOOL := TRUE;
    sTerminalInfo  : STRING;
    wTermDesc      : WORD;
    wFwVersion     : WORD;
END_VAR

fbKL6821Config(
    bConfigurate           := bConfigEnable,
    eCommandKBusWatchdog   := eDALIV2CommandRecallMaxLevel,  // 应急亮灯保险
    eCommandDI1RisingEdge  := eDALIV2CommandOff,
    eCommandDI1FallingEdge := eDALIV2CommandDoNothing,
    eCommandDI2RisingEdge  := eDALIV2CommandRecallMaxLevel,
    eCommandDI2FallingEdge := eDALIV2CommandDoNothing,
    ePowerSupplyMode       := eDALIV2PowerSupplyModeOn,
    stInDataTerminal       := stTerminalIn,
    stOutDataTerminal      := stTerminalOut,
    stInData               := stBridgeIn,
    stOutData              := stBridgeOut
);

sTerminalInfo := fbKL6821Config.sDescription;
wTermDesc     := fbKL6821Config.nTerminalDescription;
wFwVersion    := fbKL6821Config.nFirmwareVersion;
```

## 7. 业务场景与实际价值

- **场景**：所有用 KL6821 接 DALI 的工程都需要本 FB——楼宇照明（办公楼 / 酒店 / 厂房）、舞台照明、应急照明（医院 / 商业综合体）、车间工位灯具集中控制。
- **价值**：把端子的 KBus 看门狗、DI 硬触发命令、内置电源模式三套配置封装成 8 个枚举入参，省去了写约 100 行 KS2000 风格的端子寄存器读 / 写代码 + 协议握手；并且**所有配置失电保护**（写在端子 EEPROM）——端子断电再上电不需要重新跑本 FB（虽然标准做法仍然每次上电跑一次以防 EEPROM 被改）。
- **替代方案对比**：
  - 用 KS2000 离线工具配置 KL6821：能做，但工程参数（看门狗动作、DI 映射）跟 PLC 项目耦合，改一次工艺要重连 KS2000 改端子，运维成本高
  - 跳过配置直接用 `FB_KL6821Communication`：编译过但端子运行行为是上一次 EEPROM 状态——不可控
  - EL6821 + 同库：API 完全兼容，只是 EtherCAT 替代 K-Bus
  - **本 FB**：KL6821 工程的标准入口，不可省略

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/4345715851.html
- **相关**：[`FB_KL6821Communication`](FB_KL6821Communication.md)（命令调度核心，必须紧随本 FB 之后调用）、[`FB_KL6811ConfigNew`](../kl6811_base/FB_KL6811ConfigNew.md)（KL6811 老款端子的对应配置 FB）、`E_DALIV2ConfigurationCommands`（PDF §4.2.1.3 - KBus / DI 命令枚举）、`E_DALIV2PowerSupplyMode`（PDF §4.2.1.10 - 电源模式枚举）、`ST_KL6821InData` / `ST_KL6821OutData`（PDF §4.2.2.8 / §4.2.2.9 - 端子过程映像）
