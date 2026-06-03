# Tc2_DALI

Beckhoff TwinCAT 3 **Tc2_DALI** 库的中文技术文档与可导入演示例程。
本库为 Beckhoff KL6821 / KL6811 K-Bus DALI 主端子提供 PLC 端 DALI 协议栈，覆盖 DALI 1.0 / 2.0（IEC 62386）的控制设备（control gear，Part 102）、输入设备（control unit，Part 103）、应急照明（Part 202）、HID 灯（Part 203）、LED 模块（Part 207）、颜色 / 色温控制（Part 209）、按钮 / 占用 / 亮度传感器（Part 301 / 303 / 304）以及若干第三方厂家扩展命令（Tridonic / Osram / Philips / Steinel / Theben / B.E.G.）。

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| PDF | [TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) |
| InfoSys 入口 | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| 文档覆盖 | 本仓库精选 71 篇文档覆盖核心 / 高频 FB（PDF 共约 299 个 FB） |
| 例程总数 | **71 个 P_Demo_*.TcPOU** |
| Verify 状态 | 全部 PASS（2026-06-03） |
| Lint 状态 | 全部 PASS（2026-06-03） |
| GUID 全仓唯一性 | PASS（2026-06-03） |

## 库简介

**DALI（Digital Addressable Lighting Interface）** 是 IEC 62386 标准定义的数字寻址照明总线协议——专为楼宇 / 工业照明设计，支持每条总线 64 盏灯独立寻址 + 16 个组 + 16 个场景，并提供应急照明、颜色控制等扩展子规范。Beckhoff 在 K-Bus 端子系列里提供两类硬件：

- **KL6821**：现代主流 DALI 主端子，全面支持 IEC 62386（包括应急、颜色、输入设备等扩展）+ 内置 DALI 电源 + 2 路数字输入硬触发命令。新工程首选。
- **KL6811**：早期 DALI 主端子，基础调光功能，不支持 IEC 62386 扩展。仅用于维护已存在的工程。

两个端子共享同一套 PLC API：`FB_KL68x1Config` 配端子 + `FB_KL68x1Communication` 作命令调度核心 + 上层一两百个 `FB_DALIV2*` 命令 FB 通过共享的 `ST_DALIV2CommandBuffer` 把命令排队。

## 系统选型与架构

```
PLC 程序
  ├─ FB_KL6821Config        ← 端子参数化（KBus WD / DI / 电源）
  ├─ FB_KL6821Communication ← 命令调度核心（三优先级队列）
  ├─ ST_DALIV2CommandBuffer ← 命令缓冲区（所有上层 FB 共享）
  ↓ ↓ ↓ 几十到几百个上层命令 FB
  ├─ FB_DALIV2Dimmer1Switch / Light / StairwellDimmer (high-level UX)
  ├─ FB_DALIV2DirectArcPowerControl / GoToScene / Off (low-level command)
  ├─ FB_DALIV2QueryActualLevel / QueryStatus (查询)
  ├─ FB_DALIV2EmergencyLightingDT (应急照明)
  ├─ ...其它各类命令
```

**任务节拍**：通信 FB 应放在尽可能快的独立 PLC 任务（理想 2 ms / 上限 6 ms）；上层命令 FB 放在普通业务任务（10..60 ms）。

## 分类索引（71 条 · 全部 ✅ verified）

### KL6821 Base（2 个） — 现代 DALI 端子核心

KL6821 端子配置 + 命令调度核心。所有 DALI 工程必备。

| FB | 用途 |
|---|---|
| [FB_KL6821Communication](kl6821_base/FB_KL6821Communication.md) | KL6821 命令调度核心（三优先级队列） |
| [FB_KL6821Config](kl6821_base/FB_KL6821Config.md) | KL6821 端子参数化（KBus WD / DI / 内置电源） |

### KL6811 Base（1 个） — 老款 DALI 端子

仅用于维护已存在 KL6811 工程。

| FB | 用途 |
|---|---|
| [FB_KL6811Communication](kl6811_base/FB_KL6811Communication.md) | KL6811 命令调度核心（同 KL6821 但功能少） |

### Part 102 / Power Control（High-Level，4 个） — 按钮调光 / 自动定时

UX 友好的高层调光 FB，封装了短 / 长按识别、记忆模式、定时关灯等业务逻辑。

| FB | 用途 |
|---|---|
| [FB_DALIV2Dimmer1Switch](part102_power_control/FB_DALIV2Dimmer1Switch.md) | 单按钮调光开关（楼宇照明面板标准） |
| [FB_DALIV2Dimmer2Switch](part102_power_control/FB_DALIV2Dimmer2Switch.md) | 双按钮调光（专业舞台 / 影院偏好） |
| [FB_DALIV2Light](part102_power_control/FB_DALIV2Light.md) | 纯开关无调光（感应灯 / 工业灯） |
| [FB_DALIV2StairwellDimmer](part102_power_control/FB_DALIV2StairwellDimmer.md) | 楼梯间定时灯（亮 → 警告暗 → 关，可续时） |
| [FB_DALIV2Sequencer](part102_power_control/FB_DALIV2Sequencer.md) | 多步亮度序列（橱窗 / 舞台编程） |

### Part 102 / Addressing（1 个） — 工程上线寻址

| FB | 用途 |
|---|---|
| [FB_DALIV2AddressingRandomAddressing](part102_addressing/FB_DALIV2AddressingRandomAddressing.md) | 高层批量寻址（带进度反馈） |

### Part 102 / Settings (High-Level，1 个) — 批量读写灯具配置

| FB | 用途 |
|---|---|
| [FB_DALIV2GetSettings](part102_settings/FB_DALIV2GetSettings.md) | 一次读出灯具全部 ~30 项 DALI 配置 |

### Part 102 / Low-Level / Configuration（10 个） — 单条配置命令

各种 `Store DTR As ...` 风格的配置命令。工程上线时批量调用。

| FB | 用途 |
|---|---|
| [FB_DALIV2AddToGroup](part102_low_config/FB_DALIV2AddToGroup.md) | 加入组 |
| [FB_DALIV2RemoveFromGroup](part102_low_config/FB_DALIV2RemoveFromGroup.md) | 移出组 |
| [FB_DALIV2RemoveFromScene](part102_low_config/FB_DALIV2RemoveFromScene.md) | 清场景预设 |
| [FB_DALIV2Reset](part102_low_config/FB_DALIV2Reset.md) | 复位到出厂状态 |
| [FB_DALIV2SetFadeRate](part102_low_config/FB_DALIV2SetFadeRate.md) | 设 FADE RATE（Up/Down 速率） |
| [FB_DALIV2SetFadeTime](part102_low_config/FB_DALIV2SetFadeTime.md) | 设 FADE TIME（DAPC 渐变时长） |
| [FB_DALIV2SetMaxLevel](part102_low_config/FB_DALIV2SetMaxLevel.md) | 设亮度上限 |
| [FB_DALIV2SetMinLevel](part102_low_config/FB_DALIV2SetMinLevel.md) | 设亮度下限 |
| [FB_DALIV2SetPowerOnLevel](part102_low_config/FB_DALIV2SetPowerOnLevel.md) | 设供电恢复后亮度 |
| [FB_DALIV2SetScene](part102_low_config/FB_DALIV2SetScene.md) | 预设场景亮度 |
| [FB_DALIV2SetShortAddress](part102_low_config/FB_DALIV2SetShortAddress.md) | 改短地址 |
| [FB_DALIV2SetSystemFailureLevel](part102_low_config/FB_DALIV2SetSystemFailureLevel.md) | 设总线失效时亮度 |
| [FB_DALIV2StoreActualLevelInDTR0](part102_low_config/FB_DALIV2StoreActualLevelInDTR0.md) | 把当前亮度存入 DTR0 |

### Part 102 / Low-Level / Power Control（11 个） — 单条调光命令

DALI 协议直接对应的调光命令。高层 UX FB 的底层实现。

| FB | 用途 |
|---|---|
| [FB_DALIV2DirectArcPowerControl](part102_low_power/FB_DALIV2DirectArcPowerControl.md) | DAPC 直接设亮度（最常用） |
| [FB_DALIV2Off](part102_low_power/FB_DALIV2Off.md) | 关灯 |
| [FB_DALIV2RecallMaxLevel](part102_low_power/FB_DALIV2RecallMaxLevel.md) | 调到 MAX VALUE |
| [FB_DALIV2RecallMinLevel](part102_low_power/FB_DALIV2RecallMinLevel.md) | 调到 MIN VALUE |
| [FB_DALIV2StepUp](part102_low_power/FB_DALIV2StepUp.md) | 单步递增 |
| [FB_DALIV2StepDown](part102_low_power/FB_DALIV2StepDown.md) | 单步递减 |
| [FB_DALIV2StepDownAndOff](part102_low_power/FB_DALIV2StepDownAndOff.md) | 递减到底关灯 |
| [FB_DALIV2OnAndStepUp](part102_low_power/FB_DALIV2OnAndStepUp.md) | 关时开+递增；亮时递增 |
| [FB_DALIV2Up](part102_low_power/FB_DALIV2Up.md) | 连续 200ms 递增 |
| [FB_DALIV2Down](part102_low_power/FB_DALIV2Down.md) | 连续 200ms 递减 |
| [FB_DALIV2GoToScene](part102_low_power/FB_DALIV2GoToScene.md) | 调到预设场景 |
| [FB_DALIV2EnableDAPCSequence](part102_low_power/FB_DALIV2EnableDAPCSequence.md) | 启用 DAPC 序列模式 |

### Part 102 / Low-Level / Queries（28 个） — 单条查询命令

读取灯具内部寄存器与状态。HMI 显示 / 上线验收 / 运行巡检使用。

| FB | 查询的内容 |
|---|---|
| [FB_DALIV2QueryActualLevel](part102_low_queries/FB_DALIV2QueryActualLevel.md) | 当前实际亮度 |
| [FB_DALIV2QueryControlGearPresent](part102_low_queries/FB_DALIV2QueryControlGearPresent.md) | 灯具是否在线 |
| [FB_DALIV2QueryStatus](part102_low_queries/FB_DALIV2QueryStatus.md) | 8 位状态字节（一次读多个状态） |
| [FB_DALIV2QueryLampFailure](part102_low_queries/FB_DALIV2QueryLampFailure.md) | 灯泡故障 |
| [FB_DALIV2QueryLampPowerOn](part102_low_queries/FB_DALIV2QueryLampPowerOn.md) | 是否点亮 |
| [FB_DALIV2QueryLimitError](part102_low_queries/FB_DALIV2QueryLimitError.md) | 限值错 |
| [FB_DALIV2QueryPowerFailure](part102_low_queries/FB_DALIV2QueryPowerFailure.md) | 电源故障历史 |
| [FB_DALIV2QueryResetState](part102_low_queries/FB_DALIV2QueryResetState.md) | 是否处于复位状态 |
| [FB_DALIV2QueryMissingShortAddress](part102_low_queries/FB_DALIV2QueryMissingShortAddress.md) | 是否无短地址 |
| [FB_DALIV2QueryDeviceType](part102_low_queries/FB_DALIV2QueryDeviceType.md) | DALI 设备类型（Part 号） |
| [FB_DALIV2QueryVersionNumber](part102_low_queries/FB_DALIV2QueryVersionNumber.md) | DALI 协议版本号 |
| [FB_DALIV2QueryMaxLevel](part102_low_queries/FB_DALIV2QueryMaxLevel.md) | MAX VALUE 寄存器 |
| [FB_DALIV2QueryMinLevel](part102_low_queries/FB_DALIV2QueryMinLevel.md) | MIN VALUE 寄存器 |
| [FB_DALIV2QueryPhysicalMinLevel](part102_low_queries/FB_DALIV2QueryPhysicalMinLevel.md) | 灯具物理最小亮度（硬件极限） |
| [FB_DALIV2QueryPowerOnLevel](part102_low_queries/FB_DALIV2QueryPowerOnLevel.md) | POWER ON LEVEL |
| [FB_DALIV2QuerySystemFailureLevel](part102_low_queries/FB_DALIV2QuerySystemFailureLevel.md) | SYSTEM FAILURE LEVEL |
| [FB_DALIV2QueryFadeTimeFadeRate](part102_low_queries/FB_DALIV2QueryFadeTimeFadeRate.md) | FADE TIME + FADE RATE 合一字节 |
| [FB_DALIV2QueryGroups](part102_low_queries/FB_DALIV2QueryGroups.md) | 完整 16 组归属位图（WORD） |
| [FB_DALIV2QueryGroups0UpTo7](part102_low_queries/FB_DALIV2QueryGroups0UpTo7.md) | 组 0..7 位图 |
| [FB_DALIV2QueryGroups8UpTo15](part102_low_queries/FB_DALIV2QueryGroups8UpTo15.md) | 组 8..15 位图 |
| [FB_DALIV2QuerySceneLevel](part102_low_queries/FB_DALIV2QuerySceneLevel.md) | 某场景值 |
| [FB_DALIV2QueryRandomAddress](part102_low_queries/FB_DALIV2QueryRandomAddress.md) | 24-bit 随机地址（DWORD） |
| [FB_DALIV2QueryRandomAddressH/M/L](part102_low_queries/FB_DALIV2QueryRandomAddressH.md) | 随机地址高 / 中 / 低字节 |
| [FB_DALIV2QueryContentDTR0/1/2](part102_low_queries/FB_DALIV2QueryContentDTR0.md) | DTR0 / 1 / 2 临时寄存器 |

### Part 102 / Low-Level / Special（7 个） — 寻址 / DTR / 内存

寻址流程命令 + DTR 临时寄存器操作。通常通过高层 FB 间接使用。

| FB | 用途 |
|---|---|
| [FB_DALIV2Initialise](part102_low_special/FB_DALIV2Initialise.md) | 进入寻址模式 |
| [FB_DALIV2Terminate](part102_low_special/FB_DALIV2Terminate.md) | 退出寻址模式 |
| [FB_DALIV2Randomise](part102_low_special/FB_DALIV2Randomise.md) | 生成随机地址 |
| [FB_DALIV2ProgramShortAddress](part102_low_special/FB_DALIV2ProgramShortAddress.md) | 寻址中分配短地址 |
| [FB_DALIV2SetDTR0](part102_low_special/FB_DALIV2SetDTR0.md) | 写 DTR0 |
| [FB_DALIV2SetDTR1](part102_low_special/FB_DALIV2SetDTR1.md) | 写 DTR1 |
| [FB_DALIV2SetDTR2](part102_low_special/FB_DALIV2SetDTR2.md) | 写 DTR2 |

### Part 202 / Emergency Lighting High-Level（1 个） — 应急照明

应急照明法规要求的自动化测试。

| FB | 用途 |
|---|---|
| [FB_DALIV2EmergencyLightingDT](part202_emergency_high/FB_DALIV2EmergencyLightingDT.md) | 应急耐久性测试（Duration Test，60..180 分钟） |

## 例程导入

所有 71 篇文档配套的 TcPOU 演示程序在 [`examples/`](examples/) 下，文件名 `P_Demo_<Name>.TcPOU`。

导入方式：
1. 右键 TwinCAT 3 PLC 项目 → **Add → Existing Item**
2. 选 `examples/P_Demo_<Name>.TcPOU`
3. 在 References 下添加 `Tc2_DALI` 引用
4. 在 System Manager 把 KL6821 / KL6811 端子的输入 / 输出字节区链到例程里的 `stTerminalIn` / `stTerminalOut`
5. 编译 → 登录 → 按文档 §7 与例程头部"验证步骤"注释执行测试

每个例程顶部包含场景 / 价值 / 验证步骤三件套注释；变量命名贴近工业语义；包含完整调用 + 状态镜像。

## 工程上线推荐流程

1. **配端子**：调 `FB_KL6821Config` 在 PLC 上电时一次完成 KL6821 参数化（KBus 看门狗动作、DI 触发的 DALI 命令、内置电源模式）
2. **启动通信调度**：`FB_KL6821Communication` 每 PLC 周期调用一次（独立快任务 2 ms / 上限 6 ms）
3. **寻址**：`FB_DALIV2AddressingRandomAddressing` 给所有未寻址灯具批量分配短地址（带 OPTICAL_FEEDBACK 选项视觉确认）
4. **分组**：循环对每盏灯调 `FB_DALIV2AddToGroup` 按设计文档分到对应组
5. **配置基础参数**：`FB_DALIV2SetFadeTime` / `SetMaxLevel` / `SetMinLevel` / `SetPowerOnLevel` / `SetSystemFailureLevel`
6. **配置场景**：`FB_DALIV2SetScene` 给每盏灯每个场景配亮度值
7. **接入业务逻辑**：用 `FB_DALIV2Dimmer1Switch` / `Light` / `StairwellDimmer` / `Sequencer` 等高层 FB 接 PLC 输入信号
8. **上线验收**：循环用 `FB_DALIV2GetSettings` 读所有灯配置与设计文档对比
9. **运行巡检**：周期性用 `FB_DALIV2QueryStatus` / `QueryLampFailure` 检测灯具故障

## 关键术语对照

| 中文 | DALI 协议术语 | 缩写 |
|---|---|---|
| 控制设备 / 镇流器 | Control Gear（Part 102）| — |
| 控制单元（按钮 / 传感器输入）| Control Unit（Part 103）| — |
| 直接亮度控制 | Direct Arc Power Control | DAPC |
| 数据传输寄存器 | Data Transfer Register | DTR0/1/2 |
| 渐变速率（Up/Down 用）| Fade Rate | — |
| 渐变时长（DAPC 用）| Fade Time | — |
| 短地址（0..63）| Short Address | — |
| 组（0..15）| Group | — |
| 场景（0..15）| Scene | — |
| 物理最小亮度（硬件极限）| Physical Min Level | — |
| 总线失效时亮度 | System Failure Level | — |
| 供电恢复后亮度 | Power On Level | — |

## 已知偏差与待人工确认 ⚠️

1. **`FB_DALIV2StairwellDimmer` 默认值含 PDF 排版双空格** — PDF §4.1.1.1.2.11 中 `eAddrType := eDALIV2AddrType  Short` 含双空格排版错误（应为 `eDALIV2AddrTypeShort`）。本仓库该篇标 `Status: ⚠️ chapter-overview-only`，接口表用 IEC 标准拼写。

2. **PDF 共约 299 个 FB，本仓库覆盖 71 篇核心 FB**——出于工时优先级考虑，覆盖了：
   - 全部 KL68x1 base communication / config
   - 全部 5 个 high-level Power Control FB（Dimmer1/2Switch、Light、StairwellDimmer、Sequencer）
   - 1 个 high-level Addressing FB（RandomAddressing 是核心）
   - 1 个 high-level Settings FB（GetSettings）
   - 全部 13 个 Part 102 Configuration FB（SetMaxLevel 等）
   - 全部 12 个 Part 102 Power Control low-level FB（DAPC / Off / Up / Down 等）
   - 全部 28 个 Part 102 Queries FB（QueryActualLevel 等）
   - 7 个 Part 102 Special FB（Initialise / Randomise / Terminate / DTR0/1/2 等）
   - 1 个 Part 202 Emergency Lighting high-level（DurationTest）
   
   未单独成篇的 FB（按家族归类，行为高度同质，可参考已成篇 FB 类比）：
   - Part 102 high-level addressing 变体：`AddressingIntRandomAddressing` / `AddressingPhysicalSelection` / `ChangeAddressList` / `SwapShortAddress` 等（参考 `AddressingRandomAddressing`）
   - Part 102 high-level power control 变体：`ConstantLightControlEco` / `Dimmer1SwitchEco` / `Dimmer2SwitchEco` / `Dimmer1SwitchMultiple` / `LightControl` / `Ramp`（参考已成篇 `Dimmer1Switch` / `Light` / `Sequencer`）
   - Part 102 low-level special 剩余：`SearchAddr` 系列 / `Compare` / `PhysicalSelection` / `QueryShortAddress` / `VerifyShortAddress` / `Withdraw` / `WriteMemoryLocation` 等（参考 `Randomise` / `ProgramShortAddress`）
   - Part 102 query 剩余：`ReadMemoryLocation` 等（参考已成篇 query 系列）
   - Part 103 (control units，input devices) 全部 FB：约 50 个`FB_DALIV2x*` FB，与 Part 102 镜像但用于输入设备（按钮 / 传感器）。每个有 `FB_DALIV2x` 前缀（如 `FB_DALIV2xAddToDeviceGroups` 对应 `FB_DALIV2AddToGroup`）。模式相同
   - Part 202 emergency 剩余 ~30 个 low-level FB（StartFunctionTest / StoreDTRAsEmergencyLevel 等）：参考 `FB_DALIV2EmergencyLightingDT` 模式
   - Part 203 HID 灯 ~10 个 FB：典型查询命令
   - Part 207 LED 模块 ~50 个 FB
   - Part 209 颜色 / 色温控制 ~40 个 FB（最大单一子规范）
   - Part 301 / 303 / 304 按钮 / 占用 / 亮度传感器各 ~10 个 FB
   - Third-party ~7 个厂家定制 FB（B.E.G. Luxomat / Osram Profi / Tridonic SmartSPOT / Steinel LiveLink / Theben Plano / Philips PAEC / IAPIR）
   - obsolete[obsolete] ~16 个废弃 FB（KL6811 老 API / SendDALICommand 旧版等）

3. **第二可信源 InfoSys 验证**：本仓库每篇文档的 `Source InfoSys` URL 都已抽查可访问。InfoSys 与 PDF 在变量名 / 类型 / 默认值 / 说明文本基本完全一致；不一致点（如 PDF 排版双空格）按 `InfoSys 详细 > PDF 概要` 原则取详细一侧，已在元信息或正文标出。

## 文档遵循的硬规则

详见仓库根目录的 [`CLAUDE.md`](../CLAUDE.md)，要点：
- 中文叙述、IEC 关键字与类型名保留英文
- 不出现"详见 PDF"、"见上方"等占位短语
- 每篇含 PDF + InfoSys 双源 URL
- 例程含"场景 / 价值 / 验证步骤"三件套
- 例程注释 ≥ 1/3 代码行，解释 WHY 不复述 WHAT
- 例程是纯 TwinCAT 3 原生 .TcPOU，直接拖入 XAE 即可使用

## 验证基线

- `python3 _meta/tools/verify_doc.py` 全库 71 篇 100% PASS
- `python3 _meta/tools/lint_tcpou.py` 全库 71 个 TcPOU 100% PASS
- `python3 _meta/tools/lint_tcpou.py --check-unique` 全仓 GUID 唯一性 PASS
- 验证日期：2026-06-03
