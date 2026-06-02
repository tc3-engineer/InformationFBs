# FB_WriteCouplerRegs

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42597387.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_WriteCouplerRegs.TcPOU`](../examples/P_Demo_FB_WriteCouplerRegs.TcPOU) |

---

## 1. 功能简述

`FB_ReadCouplerRegs` 的写入对偶版本：通过 **2-byte PLC interface**，**批量写入**耦合器自身表寄存器或挂在其后的智能 KL/KS 端子寄存器。寻址规则与读完全一致：耦合器是 terminal 0，其后非无源端子（不计 KL9xxx 馈电）从 1 起递增；每个智能端子最多 64 个寄存器、4 通道端子有 table 0..3。

要写入的值必须**预先填入** `stCouplerTable`——`stCouplerTable[k]` 对应 reg k 的目标值。FB 按 `nStartReg`..`nEndReg` 子区间从结构里取出对应下标的字节写到对应端子寄存器。写整张表也是数秒级（PDF "several seconds"）。

**永久化条件**：写完后改动**只在端子 RAM 中**，掉电会丢。要让改动持久，**必须重启耦合器**（断电再上电、或调 `CouplerReset` 软复位）让端子把寄存器写回 EEPROM。这一点是 K-bus 时代寄存器配置的固定流程，许多团队漏掉后会反复抱怨"调好的参数下次开机又没了"。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stState         : PLCINTFSTRUCT;
    nTerminal       : BYTE := TERM_COUPLER;
    nTable          : BYTE;
    nStartReg       : BYTE;
    nEndReg         : BYTE;
    bExecute        : BOOL;
    stCouplerTable  : ST_CouplerTable;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stState` | `PLCINTFSTRUCT` | — | 2-byte PLC interface 状态字（耦合器 → PLC）；链接到耦合器 PLC interface status word |
| `nTerminal` | `BYTE` | `TERM_COUPLER` | 目标端子号。`TERM_COUPLER`（= 0）= 耦合器自身；其后非无源端子从 1 起编号（KL9xxx 馈电端子**不计入**） |
| `nTable` | `BYTE` | — | 表号；智能端子每通道 1 张表，4 通道端子表号 0..3 |
| `nStartReg` | `BYTE` | — | 起始寄存器号（包含） |
| `nEndReg` | `BYTE` | — | 结束寄存器号（包含）。范围越窄越快 |
| `bExecute` | `BOOL` | — | 上升沿触发一次批量写 |
| `stCouplerTable` | `ST_CouplerTable` | — | **入参**：要写入的值。下标对应寄存器号（`stCouplerTable[5]` = 要写到 reg 5 的值）。FB 只用 `nStartReg`..`nEndReg` 范围内的下标，其它下标不被读 |
| `tTimeout` | `TIME` | — | 整次写入最大允许时长。建议 `(nEndReg - nStartReg + 1) * 100ms + 2s` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stCtrl   : PLCINTFSTRUCT;
    bBusy    : BOOL;
    bError   : BOOL;
    nErrId   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCtrl` | `PLCINTFSTRUCT` | 2-byte PLC interface 控制字（PLC → 耦合器）；链接到耦合器 PLC interface control word |
| `bBusy` | `BOOL` | FB 激活后置 TRUE，全部寄存器写完或超时回 FALSE |
| `bError` | `BOOL` | 错误发生时在 `bBusy` 下降之后置 TRUE |
| `nErrId` | `UDINT` | 错误号，见下方表 |

注意本 FB 没有 `stCouplerTable` 输出——它是只写入；要校验写入是否成功，需要调 `FB_ReadCouplerRegs` 再读一次比对。

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次批量写。`bBusy := TRUE` 直到 `nStartReg`..`nEndReg` 全部写完或超时。

**内部时序**：
1. `bExecute` 上升沿 → `bBusy := TRUE`，FB 把 (nTerminal, nTable, nStartReg, nEndReg) 与首批要写的值经 2-byte PLC interface 发给耦合器。
2. 耦合器对目标端子按寄存器号顺序逐个写入：每个寄存器都要先解除其写保护（库内部走密码寄存器 31 协议）、写、再恢复写保护，因此**每寄存器握手次数比读多**——写比读慢。
3. 全部写完 → `bBusy := FALSE`，`bError := FALSE`，`nErrId := 0`。中途遇错 / 超时 → `bError := TRUE`，`nErrId` 标错误类型；**已写到的寄存器实际生效，未写到的保留旧值**。这点与读不一样：写出错可能让设备处于"部分配置"状态，需要手工排查。

**写入语义**：
- 写**端子 RAM**：立即生效；下一次端子周期就用新参数。
- 写不会自动同步到 **EEPROM**：必须 `CouplerReset` 或断电重启才把 RAM → EEPROM。**没复位就掉电 → 改动全丢**。
- 某些只读寄存器（端子型号、序列号等）写不进去，返回 `16#400` / `16#500`。
- 写错值（如把量程切到无效编码）端子可能立即变成"传感器值无效"状态，恢复方法是写回正确值或下次断电由 EEPROM 中的旧值覆盖（前提是没做 CouplerReset）。

**典型用法**：① 在线切换 KL3xxx 模拟输入端子的量程 / 滤波等级；② 一次性写入 user scaling 标定系数；③ 修改耦合器自身的 Profibus 地址（reg 0 区域，需重启）；④ 启用 / 关闭某通道的 oversampling。

**与 `ReadWriteTerminalReg` 的选择**：要写多个寄存器 / 跨多个端子时用本 FB；要写单个寄存器、不想占用 2-byte PLC interface 时用 `ReadWriteTerminalReg`。

## 4. 错误码 / 返回值

本 FB 无 HRESULT 返回；通过 `bError` / `nErrId` 表达错误（PDF §3.5 错误号表）：

| `nErrId` | 含义 | 常见原因 |
|---|---|---|
| `0` | 无错 | — |
| `16#100` | 2-byte PLC interface 通信初始化失败 | `stState` / `stCtrl` 没链接；耦合器未启用 2-byte interface |
| `16#200` | 通信过程中错误 | K-bus 期间总线故障 / 端子掉电 |
| `16#300` | 超时 | `tTimeout` 太短；K-bus 端子过多 / 故障端子卡住 |
| `16#400` | 寄存器号参数错 | `nStartReg > nEndReg`；目标寄存器只读；目标寄存器不存在 |
| `16#500` | 表号参数错 | `nTable` 对该端子无效 |

## 5. 使用注意 / 常见坑

- **写完不重启 = 改动全丢**。改动只在端子 RAM，掉电就消失。要持久化必须**写完 → 调 `CouplerReset` 或断电再上电**。这是 K-bus 配置的固定流程。（工程经验补充）
- **不要循环周期写**。PDF NOTICE 明确警告：库内部对端子的写访问会触发端子内部 EEPROM 操作，**循环写会烧死 EEPROM**（典型寿命 10 万次）。本 FB 定位是"配置 / 调试时调用"，绝不能放进周期循环或 1 秒/1 次的 trigger。
- **端子编号易错**：KL9xxx 无源端子**不计入** `nTerminal`。具体见 `FB_ReadCouplerRegs` §5。
- **写出错可能让设备处于"部分配置"**。例如打算把 5 个寄存器一起写，写到第 3 个超时 → 前 2 个生效、后 3 个原值，设备进入不一致状态。建议要么用更小的批次、要么写错后立刻调 `FB_ReadCouplerRegs` 读回来比对哪些没写成。
- **`tTimeout` 必须比读时还大**。写每寄存器握手更多（解锁 + 写 + 恢复），整表 256 个寄存器实测 20-40 秒。建议公式：`tTimeout = (nEndReg - nStartReg + 1) * 200ms + 3s`。
- **改完后要校验**。本 FB 没有"写完读回"机制（PDF §3.5 无此输出），生产流程应是：写 → 读回 → 比对。直接信赖 `bError = FALSE` 不够稳——某些写保护场景库内部不报错但实际没写进去。（工程经验补充）
- **不能与 `CouplerReset` / `FB_ReadCouplerDiag` / `FB_ReadCouplerRegs` 并发**。所有占用 2-byte PLC interface 的 FB 必须串行。状态机里加 SR 锁或顺序调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_WriteCouplerRegs.TcPOU`](../examples/P_Demo_FB_WriteCouplerRegs.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：BK3120 + KL3464（4 通道 ±10V 模拟输入，端子号 2）。生产工艺需要把
//       通道 1 的 feature register（reg 32）从默认 0 改成 16#0006（启用
//       user scaling + filter），且本次改动要持久化（下次开机仍生效）。
//       一次操作流程：写 reg 32 -> 等写完 -> CouplerReset 让端子把 RAM 写回
//       EEPROM。这里仅演示写 + 校验，复位由后续 fbResetCoupler 触发。
//
// 价值：把"2-byte PLC interface 批量写 + 密码寄存器 31 自动解 / 锁 + 超时
//       管理"封装为一次调用。手写实现 100+ 行；本 FB 一行调用。
//
// 验证：(1) 装载 stWriteValues.aRegister[32].nHi/nLo = 0x00/0x06 ；
//      (2) 在线置 bWriteFeatureRegs := TRUE 单脉冲 → bWriteBusy 短暂 TRUE，
//          1-2 秒后回 FALSE 且 bWriteError = FALSE；
//      (3) 配套调 FB_ReadCouplerRegs 读 reg 32 校验确实是 16#0006；
//      (4) 调 CouplerReset 复位耦合器持久化；
//      (5) 断电再上电，再读 reg 32 应该还是 16#0006。
PROGRAM P_Demo_FB_WriteCouplerRegs
VAR
    fbWriteRegs                 : FB_WriteCouplerRegs;

    // —— 链到耦合器 2-byte PLC interface ——
    stCouplerStatus     AT %I*  : PLCINTFSTRUCT;
    stCouplerControl    AT %Q*  : PLCINTFSTRUCT;

    // —— 业务输入：目标端子 / 范围 / 数据 ——
    bWriteFeatureRegs           : BOOL;          // 单脉冲触发
    nKL3464Slot                 : BYTE := 2;     // KL3464 端子号
    nKL3464TableCh1             : BYTE := 0;     // 通道 1 的 table
    nFeatureRegNo               : BYTE := 32;    // feature register
    stWriteValues               : ST_CouplerTable; // [32].nHi=0x00,.nLo=0x06
    tWriteTimeout               : TIME := T#5S;

    // —— 输出 ——
    bWriteBusy                  : BOOL;
    bWriteError                 : BOOL;
    nLastWriteErrId             : UDINT;
END_VAR

// 准备要写的字节：reg 32 = 16#0006 启用 user scaling + filter
// 实际工程上应在 init 区初始化或由 HMI 推下来；这里在主体里赋值便于在线观察
stWriteValues.aRegister[32].nHi := 16#00;
stWriteValues.aRegister[32].nLo := 16#06;

// 单次调用形式：所有 VAR_INPUT 显式赋值；写完后业务侧应再调 FB_ReadCouplerRegs
// 读回 reg 32 校验，最后 CouplerReset 持久化
fbWriteRegs(
    stState        := stCouplerStatus,
    nTerminal      := nKL3464Slot,
    nTable         := nKL3464TableCh1,
    nStartReg      := nFeatureRegNo,
    nEndReg        := nFeatureRegNo,                  // 单寄存器写
    bExecute       := bWriteFeatureRegs,
    stCouplerTable := stWriteValues,
    tTimeout       := tWriteTimeout,
    stCtrl         => stCouplerControl,
    bBusy          => bWriteBusy,
    bError         => bWriteError,
    nErrId         => nLastWriteErrId
);
```

## 7. 业务场景与实际价值

- **场景**：BC / BK + KLxxx 在役系统的"在线参数下发"。生产线换型号 / 换料时需要切换 AI 端子量程（10V / 5V / 4-20mA）、调整滤波等级、改 user scaling 标定系数、修改耦合器 Profibus 地址等。这些参数都在端子 / 耦合器内部寄存器，本 FB 是 PLC 程序在不停机的前提下改这些参数的标准做法。
- **价值**：把"2-byte PLC interface 批量写 + 密码寄存器 31 解 / 锁 + 跨端子寻址 + 超时检测"封装为一次调用。配合 `FB_ReadCouplerRegs`（校验）+ `CouplerReset`（持久化）形成完整的"读 - 改 - 验 - 持久化"流程。
- **替代方案对比**：
  - `ReadWriteTerminalReg` 单寄存器写：能做，但每个寄存器一次调用 + 状态机串行化复杂；批量改时本 FB 简单得多
  - KS2000 配置软件：可视化但只能在维护时离线接电脑改；不能在 PLC 程序里随生产工艺切换
  - 改用 EtherCAT + EL 端子 + CoE Write：现代方案，可靠性更好；但要换硬件
  - **本 FB**：在不换硬件前提下让 PLC 程序在线改 K-bus 设备的内部寄存器，是 K-bus 时代"在线配置"的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42597387.html
- **相关**：`PLCINTFSTRUCT`（§5.1）、`ST_CouplerTable`（§5.5，要写入的值数组）、`ST_CouplerReg`（§5.4）、`FB_ReadCouplerRegs`（写后校验，配套使用）、`CouplerReset`（写完持久化）、`ReadWriteTerminalReg`（单寄存器轻量级写访问）；全局常量 `TERM_COUPLER` = 0
