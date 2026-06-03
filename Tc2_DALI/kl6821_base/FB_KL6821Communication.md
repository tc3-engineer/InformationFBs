# FB_KL6821Communication

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
| Example | [`examples/P_Demo_FB_KL6821Communication.TcPOU`](../examples/P_Demo_FB_KL6821Communication.TcPOU) |

---

## 1. 功能简述

**KL6821 DALI 端子的通信驱动 FB**——所有上层 DALI 命令功能块（`FB_DALIV2*` 高层 / 低层、`FB_DSI*` 等）都不直接访问 KL6821 过程映像，而是把命令排进 `ST_DALIV2CommandBuffer` 的三个优先级缓冲区（high / middle / low）。本 FB 每个 PLC 周期从三个缓冲区里按优先级顺序取出命令，写到 KL6821 的输出过程映像，并把读到的响应同步回去，是整个 DALI 链路 PLC 侧的"调度核心"。

**每台 KL6821 必须对应且仅对应一个 FB_KL6821Communication 实例 + 一个 ST_DALIV2CommandBuffer 变量**。本 FB 应该放在尽可能**快的独立 PLC 任务**（理想 2 ms，最大 6 ms），与上层命令 FB 所在任务（10..60 ms）分离，以保证 DALI 物理层吞吐。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bResetMaximumDemandCounter   : BOOL;
    bResetOverflowCounter        : BOOL;
    bResetInactiveProcessImage   : BOOL;
    nOptions                     : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bResetMaximumDemandCounter` | `BOOL` | — | 上升沿复位 `arrBufferMaximumDemandMeter` 三个缓冲区的最大占用率（0..100%）记录 |
| `bResetOverflowCounter` | `BOOL` | — | 上升沿复位 `arrBufferOverflowCounter` 三个缓冲区的溢出计数器 |
| `bResetInactiveProcessImage` | `BOOL` | — | 上升沿解除 KL6821 过程映像的锁定：当端子两个数字输入之一被触动时端子会自动锁过程映像（不允许下发 DALI 命令）；本输入用来手动清除这种锁定，使 `bProcessImageInactive` / `bDigitalInput1Active` / `bDigitalInput2Active` 都回到 FALSE |
| `nOptions` | `DWORD` | `0` | 保留位，留作未来扩展 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy                        : BOOL;
    bError                       : BOOL;
    nErrorId                     : UDINT;
    arrBufferDemandMeter         : ARRAY [0..2] OF BYTE;
    arrBufferMaximumDemandMeter  : ARRAY [0..2] OF BYTE;
    arrBufferOverflowCounter     : ARRAY [0..2] OF UINT;
    bLineIsBusy                  : BOOL;
    bLineIsInitialized           : BOOL;
    bDigitalInput1Active         : BOOL;
    bDigitalInput2Active         : BOOL;
    bProcessImageInactive        : BOOL;
    bCollisionError              : BOOL;
    bPowerSupplyError            : BOOL;
    bShortCircuit                : BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 本 FB 正在处理缓冲区中的命令时为 TRUE；缓冲区清空后回 FALSE |
| `bError` | `BOOL` | 任何一类错（缓冲区溢出 / 总线冲突 / 电源故障 / 短路 / DALI 命令执行错）出现时置 TRUE，由本 FB 自动按命令重新加载复位 |
| `nErrorId` | `UDINT` | 错误号；见 §4 错误码表与 `Tc2_DALI` 全库错误码（PDF §4.1.4） |
| `arrBufferDemandMeter` | `ARRAY [0..2] OF BYTE` | 三个缓冲区（[0] = high / [1] = middle / [2] = low）当前占用率，0..100% |
| `arrBufferMaximumDemandMeter` | `ARRAY [0..2] OF BYTE` | 三个缓冲区历史最大占用率（HMI 长期观察用），由 `bResetMaximumDemandCounter` 复位 |
| `arrBufferOverflowCounter` | `ARRAY [0..2] OF UINT` | 三个缓冲区累计溢出次数，由 `bResetOverflowCounter` 复位 |
| `bLineIsBusy` | `BOOL` | 本 FB 处于运行（已被调用）状态时为 TRUE |
| `bLineIsInitialized` | `BOOL` | 首次调用后内部初始化完成时置 TRUE；初始化期间不能下发 DALI 命令 |
| `bDigitalInput1Active` | `BOOL` | KL6821 端子上 DI1 被触动；同时 `bProcessImageInactive` 置 TRUE 锁住过程映像 |
| `bDigitalInput2Active` | `BOOL` | KL6821 端子上 DI2 被触动；同时 `bProcessImageInactive` 置 TRUE |
| `bProcessImageInactive` | `BOOL` | 过程映像被锁（任一 DI 触动后）；用 `bResetInactiveProcessImage` 上升沿手动解锁 |
| `bCollisionError` | `BOOL` | DALI 总线上检测到帧冲突（多个主机同时发送，或外部干扰） |
| `bPowerSupplyError` | `BOOL` | KL6821 内部 DALI 电源故障（电压超出 9.5..22.5 V 规格） |
| `bShortCircuit` | `BOOL` | DALI 双线接口短路（最常见是布线时火零误接） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stInData                     : ST_KL6821InData;
    stOutData                    : ST_KL6821OutData;
    stCommandBuffer              : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stInData` | `ST_KL6821InData` | KL6821 的**内部输入结构**——配合 `FB_KL6821Config` 使用时，这里连的是 `FB_KL6821Config` 的同名输出（不直接接端子过程映像）。配置 FB 把端子的真实过程映像桥接进来 |
| `stOutData` | `ST_KL6821OutData` | KL6821 的**内部输出结构**——同上，连到 `FB_KL6821Config` 的同名输出 |
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构。**所有上层命令 FB（`FB_DALIV2*` 等）的 `stCommandBuffer` 入口都必须连到这同一个变量**——上层 FB 把命令排进去、本 FB 取出来发 |

## 3. 行为说明

**架构**：每个 PLC 周期本 FB 都做四件事：（1）从 `stCommandBuffer` 三个优先级队列中按 high → middle → low 顺序取出待发命令；（2）按 DALI 时序写入 `stOutData`；（3）从 `stInData` 读回总线响应，分发回上层命令 FB 的结果区；（4）刷新统计输出（`arrBufferDemandMeter` 等）。

**与配置 FB 的串接关系**：`FB_KL6821Config` 是端子参数化 FB（KBus watchdog、数字输入边沿映射的 DALI 命令、电源模式等），它必须**与 FB_KL6821Communication 在同一 PLC 任务**调用，且 `FB_KL6821Config` 的 `stInData` / `stOutData` 输出连到本 FB 的同名输入。配置阶段（`FB_KL6821Config.bBusy = TRUE`）本 FB 不下发 DALI 命令；配置完成后本 FB 接管端子过程映像。

**任务分离要求**：上层 DALI 命令 FB（例如 `FB_DALIV2AddToGroup`、`FB_DALIV2DirectArcPowerControl`）的执行节拍通常在 10..60 ms，因为单条 DALI 16-bit 电报本身就需要约 14 ms 才能完成空中传输；但本 FB 是低延迟桥接层，需要在每个 KL6821 IO 刷新窗口内即时响应，建议放进 2 ms（理想）/ 6 ms（上限）任务。把上层命令 FB 与本 FB 放进**同一慢任务**就会出现 `arrBufferOverflowCounter` 持续增长。

**三个优先级缓冲区**：上层每个命令 FB 都有 `eCommandPriority`（`eDALIV2CommandPriorityHigh` / `Middle` / `Low`），命令按该优先级落进 `stCommandBuffer.arrBuffer[0..2]`。本 FB 严格按 high → middle → low 顺序取——所以紧急关灯之类的命令应该用 high，巡检查询用 low。各队列容量约 40 条，超出则丢最新条目并把对应 `arrBufferOverflowCounter` 加 1。

**过程映像锁定行为**：KL6821 的 DI1 / DI2 数字输入在 `FB_KL6821Config` 里被配置成"上升沿/下降沿触发的 DALI 命令"（例如 DI2 上升沿触发 `eDALIV2CommandRecallMaxLevel` 一键开灯）；当 DI 触发后，KL6821 自身会按预编程命令发 DALI 电报、同时锁住 PLC 侧过程映像（避免上层 PLC 命令与"硬触发命令"撞车），表现为 `bProcessImageInactive = TRUE` + `bDigitalInputNActive = TRUE`。上层应用看到该锁定后通常等几百毫秒让端子完成、然后给 `bResetInactiveProcessImage` 一次上升沿手动解锁。这套机制是"楼层走廊一键开灯"场景的底层支撑：即便 PLC 卡死，端子上的物理按钮也能直接驱动灯。

**典型陷阱**：① 把本 FB 与上层命令 FB 放进同一慢任务 → 缓冲区频繁溢出（先看 `arrBufferOverflowCounter`，再缩短本 FB 任务节拍）；② 多实例同时绑同一 KL6821 → DALI 时序冲突，端子直接报 `bCollisionError`；③ 忘了在 SysMgr 把 `FB_KL6821Config` 的过程映像入口链到真实端子 IO → `bShortCircuit` / `bPowerSupplyError` 全 FALSE 但所有命令都不到现场（端子根本没收到字节）；④ 在 IF 分支里调用本 FB 而不是每周期无条件调用 → 命令积压、上层 FB 长时间 `bBusy = TRUE`。

## 4. 错误码 / 返回值

本 FB 的 `nErrorId` 复用 `Tc2_DALI` 全库错误码（PDF §4.1.4，对应 `Tc2_DALI/error_handling/Error_Codes.md`）。最常见取值：

| `nErrorId` | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `16#0000` | 无错 | 正常运行 | — |
| `16#0001` | Buffer overflow (high) | high 缓冲区溢出 | 缩短本 FB 任务周期 / 调低上层命令并发 |
| `16#0002` | Buffer overflow (middle) | middle 缓冲区溢出 | 同上 |
| `16#0003` | Buffer overflow (low) | low 缓冲区溢出 | 同上 |
| `16#0004` | Collision error | DALI 总线帧冲突 | 检查是否多 master；干扰源排查 |
| `16#0005` | Power supply error | KL6821 内部 DALI 电源异常 | 检查端子供电；端子可能损坏 |
| `16#0006` | Short circuit | DALI 双线短路 | 检查布线 |
| `16#0xxx` | DALI 命令执行错 | 由上层命令 FB 转译为具体语义（如 `nAddr` 越界、设备无响应） | 详见对应命令 FB 文档 |

**注**：当多个错误同时存在时，`nErrorId` 报最早发生的；专属位标志（`bCollisionError` / `bPowerSupplyError` / `bShortCircuit`）会同时为 TRUE，便于 HMI 同时显示。

## 5. 使用注意 / 常见坑

- **任务节拍**：本 FB 必须在尽可能快的独立任务，目标 2 ms、最大不超过 6 ms。上层命令 FB 放在 10..60 ms 任务。把两者放同一任务 → `arrBufferOverflowCounter` 会持续增长，DALI 链路有效吞吐降到 50% 以下。
- **每台端子一个实例**：同一 KL6821 端子上挂两个 FB_KL6821Communication 实例必定冲突——端子过程映像被双写，输出 `bCollisionError` 持续置位。
- **必须先用 `FB_KL6821Config`**：直接拿本 FB 接端子过程映像虽然能编译，但端子的 KBus watchdog / DI 边沿命令 / 电源模式都没初始化，DI 触发不响应 + 看门狗误触发；标准用法是 `FB_KL6821Config` 在 `FB_KL6821Communication` 之前调用。
- **`stCommandBuffer` 在所有上层命令 FB 之间共享**：一个 KL6821 上挂的几十上百个 `FB_DALIV2*` 命令 FB，每个的 `stCommandBuffer` 入口都连到这同一个变量。变量类型 `ST_DALIV2CommandBuffer` 内部是 3 × 40 条命令的循环队列。
- **DI 锁定要主动解除**：DI1 / DI2 触发后过程映像被锁住，下一次 PLC 侧命令前必须给 `bResetInactiveProcessImage` 一次上升沿，否则该 KL6821 上后续 PLC 命令都不发出去（等手动按钮释放也行，但 PLC 不主动重置就一直锁着）。
- **缓冲区溢出可观察**：上线后定期看 `arrBufferDemandMeter[0..2]` 与 `arrBufferOverflowCounter[0..2]`。前者若长期 > 70% 说明命令密度太大要调度优化；后者若非 0 说明已经在丢命令了。
- **`bLineIsInitialized` 是上线第一个看的信号**：上电后本 FB 调用 1..2 个周期内 `bLineIsInitialized` 才会从 FALSE 变 TRUE；HMI 必须等这个信号 TRUE 后才能让操作员下发 DALI 命令。
- **同 KL6811 不兼容**：本 FB 专用 KL6821（带 DALI 2 IEC62386 全面支持 + DI / 电源模式扩展）。老 KL6811 端子用对应的 `FB_KL6811Communication`，命令缓冲区也是 `ST_DALIV2CommandBuffer` 但内部协议字节序不同（工程经验补充）。
- **使用 EL6821 EtherCAT 替代**：新工程可考虑 EL6821（EtherCAT 版本）+ 对应库；但本仓库主要面向 K-Bus KL6821（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL6821Communication.TcPOU`](../examples/P_Demo_FB_KL6821Communication.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_KL6821Communication
VAR
    fbKL6821Config        : FB_KL6821Config;
    fbKL6821Communication : FB_KL6821Communication;
    stCommandBuffer       : ST_DALIV2CommandBuffer;

    // 端子真实过程映像（在 SysMgr 链到 KL6821 IO）
    stTerminalIn          AT %I* : ST_KL6821InData;
    stTerminalOut         AT %Q* : ST_KL6821OutData;

    // 配置 FB 与通信 FB 之间的内部桥
    stBridgeIn            : ST_KL6821InData;
    stBridgeOut           : ST_KL6821OutData;

    bStartConfig          : BOOL := TRUE;
    bResetMaxDemand       : BOOL;
    bResetOverflow        : BOOL;
    bResetImageLock       : BOOL;

    // 监控
    arrBufDemand          : ARRAY[0..2] OF BYTE;
    arrBufMaxDemand       : ARRAY[0..2] OF BYTE;
    arrBufOverflow        : ARRAY[0..2] OF UINT;
END_VAR

fbKL6821Config(
    bConfigurate          := bStartConfig,
    stInDataTerminal      := stTerminalIn,
    stOutDataTerminal     := stTerminalOut,
    stInData              := stBridgeIn,
    stOutData             := stBridgeOut
);

fbKL6821Communication(
    bResetMaximumDemandCounter := bResetMaxDemand,
    bResetOverflowCounter      := bResetOverflow,
    bResetInactiveProcessImage := bResetImageLock,
    stInData                   := stBridgeIn,
    stOutData                  := stBridgeOut,
    stCommandBuffer            := stCommandBuffer,
    arrBufferDemandMeter        => arrBufDemand,
    arrBufferMaximumDemandMeter => arrBufMaxDemand,
    arrBufferOverflowCounter    => arrBufOverflow
);
```

## 7. 业务场景与实际价值

- **场景**：楼宇 / 工业照明：CX 工控机 + KL6821 端子接 DALI 总线，控制几十到上百个 DALI 镇流器（控制驱动器、LED 驱动、传感器、紧急照明等）。本 FB 是整个 DALI 子系统在 PLC 侧的"调度核心"——所有上层 `FB_DALIV2*` 命令都通过它发出去。
- **价值**：把 DALI 物理层时序（每帧 14 ms 时间窗、bit-banging 字节序、ACK 等待）、三优先级队列、缓冲区溢出统计、端子层错误（短路 / 电源故障）全部封装。上层应用只关心"我要把这个 channel 调到 50% 亮度"，本 FB 负责实际下发。不用就需要自己写 ~500 行 KL6821 字节级驱动 + DALI 时序状态机。
- **替代方案对比**：
  - 自己写 KL6821 字节级 DALI 主机：理论可行但要实现 IEC 62386 各 part 的命令编码 + 16/24-bit 电报区分 + DALI 时序，几个月工作量
  - EL6821 EtherCAT 版本 + 同一套 Tc2_DALI 库：API 完全兼容，只换硬件；新工程优先 EL6821
  - 用 KNX/EIB 经 KL6301 替代 DALI：协议不同，不能直接替换；DALI 走光环境总线优势在镇流器层而不是开关层
  - **本 FB**：在 KL6821 硬件存在前提下是唯一标准入口，没有真正替代

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/4345713931.html
- **相关**：[`FB_KL6821Config`](FB_KL6821Config.md)（端子参数化，必须先调用）、[`FB_KL6811Communication`](../kl6811_base/FB_KL6811Communication.md)（老款 KL6811 端子的对应版本）、`ST_DALIV2CommandBuffer`（PDF §4.2.2 - 命令缓冲区结构，所有上层命令 FB 共享）、`ST_KL6821InData` / `ST_KL6821OutData`（PDF §4.2.2.8 / §4.2.2.9 - KL6821 过程映像结构）、`E_DALIV2CommandPriority`（PDF §4.2.1.2 - 命令优先级枚举）
