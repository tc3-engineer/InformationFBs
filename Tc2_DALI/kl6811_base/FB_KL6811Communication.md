# FB_KL6811Communication

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6811 Base` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL6811Communication.TcPOU`](../examples/P_Demo_FB_KL6811Communication.TcPOU) |

---

## 1. 功能简述

**KL6811 老款 DALI 端子的通信驱动 FB**——功能与 [`FB_KL6821Communication`](../kl6821_base/FB_KL6821Communication.md) 等价，把上层 `FB_DALIV2*` 命令 FB 排进 `ST_DALIV2CommandBuffer` 的三个优先级缓冲区里的命令按 high → middle → low 顺序取出，下发到 KL6811 过程映像，并把响应同步回去。KL6811 是早期产品（前一代 DALI K-Bus 端子），相对 KL6821 缺少独立 DALI 内置电源管理、数字输入硬触发等扩展功能，故输出信号也少几个（无 `bDigitalInputXActive` / `bProcessImageInactive` / `bCollisionError` / `bPowerSupplyError` / `bShortCircuit`）。新工程建议优先选 KL6821 + `FB_KL6821Communication`，本 FB 主要用于维护现存 KL6811 设备的工程。

**任务节拍**：与 KL6821 版本一样，本 FB 必须放在尽可能快的独立 PLC 任务（理想 2 ms，最大 6 ms），与上层命令 FB 所在任务（10..60 ms）分离。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bResetMaximumDemandCounter : BOOL;
    bResetOverflowCounter      : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bResetMaximumDemandCounter` | `BOOL` | — | 上升沿复位 `arrBufferMaximumDemandMeter` 三个缓冲区的历史最大占用率记录（0..100%）|
| `bResetOverflowCounter` | `BOOL` | — | 上升沿复位 `arrBufferOverflowCounter` 三个缓冲区的溢出累计计数 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT 
    bBusy                       : BOOL;
    bError                      : BOOL;
    nErrorId                    : BYTE;
    arrBufferDemandMeter        : ARRAY [0..2] OF BYTE;
    arrBufferMaximumDemandMeter : ARRAY [0..2] OF BYTE;
    arrBufferOverflowCounter    : ARRAY [0..2] OF UINT;
    bLineIsBusy                 : BOOL;
    bLineIsInitialized          : BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 命令调度核心正在处理缓冲区命令时为 TRUE |
| `bError` | `BOOL` | 出现命令执行错时置 TRUE |
| `nErrorId` | `BYTE` | 错误号（KL6811 版本是 BYTE，不像 KL6821 是 UDINT）；与全库错误码共表 |
| `arrBufferDemandMeter` | `ARRAY [0..2] OF BYTE` | 三个缓冲区（[0]high / [1]middle / [2]low）当前占用率 0..100% |
| `arrBufferMaximumDemandMeter` | `ARRAY [0..2] OF BYTE` | 三个缓冲区历史最大占用率，由 `bResetMaximumDemandCounter` 复位 |
| `arrBufferOverflowCounter` | `ARRAY [0..2] OF UINT` | 三个缓冲区累计溢出次数，由 `bResetOverflowCounter` 复位 |
| `bLineIsBusy` | `BOOL` | 本 FB 处于运行状态 |
| `bLineIsInitialized` | `BOOL` | 首次调用后初始化完成；初始化期间不能下发 DALI 命令 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stDALIInData    : ST_KL6811InData;
    stDALIOutData   : ST_KL6811OutData;
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stDALIInData` | `ST_KL6811InData` | KL6811 输入过程映像（端子 → PLC）；正常做法是 `FB_KL6811ConfigNew` 的同名输出 |
| `stDALIOutData` | `ST_KL6811OutData` | KL6811 输出过程映像（PLC → 端子）；同上 |
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；所有上层命令 FB 共享 |

## 3. 行为说明

**架构**：每周期从 `stCommandBuffer.arrBuffer[0..2]` 按 high → middle → low 顺序取出待发命令，写到 `stDALIOutData`；同时从 `stDALIInData` 读响应，分发回上层 FB 的结果区；并刷新 `arrBufferDemandMeter` / `arrBufferMaximumDemandMeter` / `arrBufferOverflowCounter` 三个统计输出。

**与 KL6821 版本的区别**：KL6811 是 DALI 1.0 时代产品，端子内部没有独立 DALI 内置电源管理（一般要外部 DALI PSU），也没有 KL6821 那种"数字输入硬触发 DALI 命令 + 锁过程映像"的扩展机制，因此本 FB 没有 `bDigitalInputXActive` / `bProcessImageInactive` / `bCollisionError` / `bPowerSupplyError` / `bShortCircuit` 几个输出。`nErrorId` 是 BYTE 类型（KL6821 是 UDINT），错误码总量较少。

**与 `FB_KL6811ConfigNew` 的协作**：与 KL6821 链同样模式——`FB_KL6811ConfigNew.stInData` / `stOutData` 输出连本 FB 的 `stDALIInData` / `stDALIOutData`；真实端子 IO 链到 `FB_KL6811ConfigNew.stInDataTerminal` / `stOutDataTerminal`。两个 FB 必须在同一 PLC 任务。

**任务分离**：与 KL6821 版本一致——本 FB 放快任务（2..6 ms），上层命令 FB 放慢任务（10..60 ms）。

**与 KL6821 不可混用**：`stCommandBuffer` 类型虽然都是 `ST_DALIV2CommandBuffer`，但内部协议字节序与命令编码细节有差异，KL6811 链上的 `FB_DALIV2*` 命令 FB 必须挂在 `FB_KL6811Communication` 上、不能挂到 KL6821 链。（工程经验补充）

**典型陷阱**：① 多实例绑同一 KL6811（必然冲突）；② 把本 FB 与上层命令 FB 放进同一慢任务（缓冲区溢出）；③ 跳过 `FB_KL6811ConfigNew` 直接接端子过程映像（操作模式 / 设备计数等参数未初始化）；④ 把 KL6811 工程的 FB 实例迁移到 KL6821 链（编译过但命令不发或时序错乱）。

## 4. 错误码 / 返回值

`nErrorId` 是 BYTE（注意与 KL6821 的 UDINT 不同）。复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）；本 FB 最常见：

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 无错 | — |
| `1..3` | 三个优先级缓冲区溢出（高 / 中 / 低）| 缩短本 FB 任务节拍 |
| `7` | 端子无响应 | 检查 IO mapping 与端子供电 |
| `8` | 端子固件版本不支持当前操作 | 升级端子固件 |

## 5. 使用注意 / 常见坑

- **新工程优先 KL6821**：KL6811 是已停产端子，新工程要求 DALI 2 / IEC 62386 兼容（应急照明 / 颜色控制 / 输入设备等）的功能时只能用 KL6821。
- **任务节拍要求与 KL6821 一致**：放快任务，目标 2 ms。
- **每台端子一个实例**：与 KL6821 同。
- **必须先用 `FB_KL6811ConfigNew`**：（旧版 `FB_KL6811Config` 已废弃，从库 v3.6.2.0 起改用 `FB_KL6811ConfigNew`）。
- **`stCommandBuffer` 在所有上层命令 FB 之间共享**：与 KL6821 同模式。
- **`bLineIsInitialized` 上电后第一拍才 TRUE**：HMI 等待这个信号 TRUE 后才能让操作员下发命令。
- **`nErrorId` 是 BYTE 而非 UDINT**：移植 KL6821 工程到 KL6811 时要注意类型截断（工程经验补充）。
- **没有过程映像锁机制**：KL6811 端子没有数字输入硬触发功能，所以也没有过程映像锁——所有 DALI 命令都由 PLC 主动发起，端子完全是被动从机。这同时意味着 KL6811 不支持"PLC 死机时端子还能由按钮直接驱动灯"的故障安全机制。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL6811Communication.TcPOU`](../examples/P_Demo_FB_KL6811Communication.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_KL6811Communication
VAR
    fbKL6811Comm   : FB_KL6811Communication;
    stCommandBuffer: ST_DALIV2CommandBuffer;
    stBridgeIn     : ST_KL6811InData;
    stBridgeOut    : ST_KL6811OutData;
    bResetMaxDemand: BOOL;
    bResetOverflow : BOOL;
    arrDemand      : ARRAY[0..2] OF BYTE;
END_VAR

fbKL6811Comm(
    bResetMaximumDemandCounter := bResetMaxDemand,
    bResetOverflowCounter      := bResetOverflow,
    stDALIInData               := stBridgeIn,
    stDALIOutData              := stBridgeOut,
    stCommandBuffer            := stCommandBuffer
);

arrDemand := fbKL6811Comm.arrBufferDemandMeter;
```

完整可运行版本（含 `FB_KL6811ConfigNew` 串接 + 真实 IO 链接）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：老工程维护——已经投入使用 KL6811 端子的 DALI 工程，需要软件升级 / 加新功能。也可用于纯 DALI 1.0 设备的小项目（仅做基础调光，不需要 IEC 62386 扩展）。
- **价值**：与 KL6821 版本一样，封装 DALI 物理层时序 + 三优先级队列 + 缓冲区统计，上层应用只关心业务命令。
- **替代方案对比**：
  - 全面换 KL6821 + `FB_KL6821Communication`：新工程优先，但旧工程换硬件成本高
  - EL6821 + 同库：EtherCAT 替换 K-Bus，性能更好但要重新规划网络拓扑
  - 自写 KL6811 字节驱动：不建议，相当于重新实现本 FB

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.2.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1031/tcplclib_tc2_dali/4439015947.html
- **相关**：[`FB_KL6821Communication`](../kl6821_base/FB_KL6821Communication.md)（KL6821 版本，新工程优先）、`FB_KL6811ConfigNew`（KL6811 端子参数化，必须先调用）、`ST_DALIV2CommandBuffer`、`ST_KL6811InData` / `ST_KL6811OutData`（PDF §4.2.2.10 / §4.2.2.11）
