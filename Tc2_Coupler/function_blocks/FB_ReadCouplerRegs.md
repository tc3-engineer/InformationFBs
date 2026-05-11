# FB_ReadCouplerRegs

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42595851.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ReadCouplerRegs.xml`](../examples/P_Demo_FB_ReadCouplerRegs.xml) |

---

## 1. 功能简述

通过 **2-byte PLC interface**，**批量读取**耦合器自身的表寄存器（table register）和挂在它后面的智能 KL/KS 端子寄存器。寻址规则：**耦合器自己是 terminal 0**；其后所有非无源端子（即不计 KL9xxx 电源 / 馈电这类无源端子）从 **1 开始递增**编号——这与硬件端子排上"看见多少个端子就数到几"不同，需要小心数。每个智能端子最多有 64 个寄存器，组织成"表"（table），4 通道端子有 table 0..3，每通道独立。

可以读取整张表（reg 0..255）或仅一个子区间（`nStartReg`..`nEndReg`）。读整张表通常需要**数秒钟**（PDF 原话 "several seconds"），所以工程上建议只读自己关心的子区间。读到的字节按 high/low 顺序填到 `stCouplerTable`，数组下标对应寄存器号（`stCouplerTable[5]` 对应 reg 5）。

与 `ReadWriteTerminalReg` 的关键区别：本 FB 走 **2-byte PLC interface**（用现场总线层的 PLC interface 控制握手），适合一次批量读多个寄存器、跨多个端子；`ReadWriteTerminalReg` 走 **端子通道的 control/status 字节**（用每个端子自己的过程数据字握手），一次只能读一个寄存器、且只能访问当前通道。批量读耦合器配置 / 厂家数据用本 FB，单次改某个端子参数用 `ReadWriteTerminalReg`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stState       : PLCINTFSTRUCT;
    nTerminal     : BYTE:= TERM_COUPLER;
    nTable        : BYTE;
    nStartReg     : BYTE;
    nEndReg       : BYTE;
    bExecute      : BOOL;
    tTimeout      : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stState` | `PLCINTFSTRUCT` | — | 2-byte PLC interface 状态字（耦合器 → PLC）；System Manager 链接到耦合器 PLC interface 的 status word |
| `nTerminal` | `BYTE` | `TERM_COUPLER` | 目标端子号。`TERM_COUPLER`（= 0）指耦合器自身；其后非无源端子从 1 开始计数（无源 KL9xxx 馈电端子**不计入编号**） |
| `nTable` | `BYTE` | — | 表号。智能端子每个通道有 1 张表；4 通道端子表号 0..3；每张表最多 64 个寄存器 |
| `nStartReg` | `BYTE` | — | 起始寄存器号（包含），通常 0 |
| `nEndReg` | `BYTE` | — | 结束寄存器号（包含）。`nStartReg = 0, nEndReg = 255` 读整张表；范围越窄越快 |
| `bExecute` | `BOOL` | — | 上升沿触发一次批量读 |
| `tTimeout` | `TIME` | — | 整次读取的最大允许时长。读 N 个寄存器约 100ms × N，整表 256 个建议 ≥ T#30S |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stCtrl          : PLCINTFSTRUCT;
    bBusy           : BOOL;
    bError          : BOOL;
    nErrId          : UDINT;
    stCouplerTable  : ST_CouplerTable;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCtrl` | `PLCINTFSTRUCT` | 2-byte PLC interface 控制字（PLC → 耦合器）；链接到耦合器 PLC interface control word |
| `bBusy` | `BOOL` | FB 激活后置 TRUE，全部寄存器读完或超时回 FALSE |
| `bError` | `BOOL` | 错误发生时在 `bBusy` 下降之后置 TRUE |
| `nErrId` | `UDINT` | 错误号，见下方表 |
| `stCouplerTable` | `ST_CouplerTable` | 读取结果（详见 §5.5）。结构内部是 high/low 字节数组，下标对应寄存器号；`stCouplerTable[k]` = reg k 的当前值 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次批量读。`bBusy := TRUE` 直到 `nStartReg`..`nEndReg` 全部读完，或 `tTimeout` 到时强制结束。

**内部时序**：
1. `bExecute` 上升沿 → `bBusy := TRUE`，FB 把 (nTerminal, nTable, nStartReg, nEndReg) 经 2-byte PLC interface 编码进 control word 发给耦合器。
2. 耦合器收到批量读请求后，对指定端子（或自己）按寄存器号顺序逐个读出寄存器值，每个寄存器一次握手。
3. FB 把读回的高 / 低字节按下标填入 `stCouplerTable`。
4. 读完最后一个寄存器 → `bBusy := FALSE`，`bError := FALSE`，`nErrId := 0`。读到一半遇错或超时 → `bError := TRUE`，`nErrId` 标错误类型；`stCouplerTable` 中**已读到的部分有效**，未读到的位置保留旧值（不会清零）。

**寻址规则细节**：
- `nTerminal = 0`（`TERM_COUPLER`）：读耦合器自己的表寄存器。耦合器表里通常存型号、版本、Profibus 地址、波特率、节点配置等。
- `nTerminal = 1..N`：读非无源端子。"非无源"意思是 KL9100 / KL9180 这类纯馈电、电源端子**跳过不计数**——例如端子排排序 [KL1408, KL9100, KL3464, KL4022]，那 KL1408 是 1、KL3464 是 2（跳过 KL9100）、KL4022 是 3。**这是 K-bus 编号最容易出错的地方**。
- `nTable`：对耦合器（terminal 0）通常只用 0；对智能端子每通道 1 张表，4 通道端子用 0..3。

**性能**：每个寄存器读访问约 50-100ms（含 K-bus 握手）。`0..255` 整表 ≈ 12-25 秒，所以 `tTimeout` 必须给足，工程上推荐：读子区间 N 个寄存器时 `tTimeout = N * 100ms + 1s` 余量。

**用法**：① 上电时一次性读耦合器表（reg 0..31）记录硬件配置存档；② 启动时读某个 KL3xxx 的 user scaling 寄存器（reg 32..47）校验生产参数；③ 偶尔做一次"硬件巡检"，对比读到的端子型号与工程预期。

**与 `ReadWriteTerminalReg` 的选择**：
- 要读多个寄存器 / 跨多个端子 → 本 FB（一次 batch）
- 要读单个寄存器、配置过 control/status 字节 mapping → `ReadWriteTerminalReg`（更轻、不占 2-byte PLC interface）

## 4. 错误码 / 返回值

本 FB 无 HRESULT 返回；通过 `bError` / `nErrId` 表达错误（PDF §3.4 错误号表）：

| `nErrId` | 含义 | 常见原因 |
|---|---|---|
| `0` | 无错 | — |
| `16#100` | 2-byte PLC interface 通信初始化失败 | `stState` / `stCtrl` 没链接；耦合器未启用 2-byte interface |
| `16#200` | 通信过程中错误 | K-bus 期间总线故障 / 端子掉电 |
| `16#300` | 超时 | `tTimeout` 太短；K-bus 端子多 / 故障端子卡住 |
| `16#400` | 寄存器号参数错 | `nStartReg > nEndReg`；目标端子不支持该寄存器号；该表的寄存器范围比请求小 |
| `16#500` | 表号参数错 | `nTable` 对该端子无效（例如 4 通道端子传了 `nTable = 5`） |

## 5. 使用注意 / 常见坑

- **端子编号易错**：无源 KL9xxx（电源馈电）**不算在内**。排序 [KL1408, KL9100, KL3464] 时 `nTerminal = 2` 对应的是 KL3464 而不是 KL9100。常见 bug 是把无源端子也数进去，读到一堆无意义的零值或 `nErrId = 16#400`。可先读耦合器（terminal 0）的 reg 8 series 看端子表确认编号。
- **不要循环周期读**。PDF 的 NOTICE 警告：库内部对端子做的是寄存器访问，**寄存器位于 EEPROM**，循环写会烧死 EEPROM（典型 10 万次寿命）；读对 EEPROM 无害但批量读会占满 2-byte PLC interface，影响其它通讯。本 FB 定位是"配置 / 诊断时调用"，不是循环数据通道。
- **`tTimeout` 必须够大**。读整表 256 个寄存器约 12-25 秒，`tTimeout = T#5S` 会误超时。建议公式：`tTimeout = (nEndReg - nStartReg + 1) * T#100MS + T#2S`。
- **读到的 `stCouplerTable` 下标是绝对寄存器号**：即使你只读 reg 32..47，结果也填在 `stCouplerTable[32]..stCouplerTable[47]`，下标 0..31 不会被覆盖（保留旧值或全零）。不要写成 `stCouplerTable[0]` 取你刚读的第一个寄存器。
- **某些只读寄存器读出来不一定是当前值**：例如端子序列号、固件版本等是 EEPROM 出厂值，但少量寄存器是镜像 RAM 状态、跟硬件实时改变。具体语义查端子手册的 "Object description" 章。
- **不能与 `CouplerReset` 同时跑**。两者都占用 2-byte PLC interface，并发会让握手错乱。状态机里串行化：复位完成 → 等 1 秒 → 再做寄存器读。（工程经验补充）
- **端子越多速度越慢**。挂 30 个端子时读一个寄存器都要 100-200ms（K-bus 整圈刷新更慢）。诊断脚本建议只读关键寄存器，不要 dump 整表。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ReadCouplerRegs.xml`](../examples/P_Demo_FB_ReadCouplerRegs.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：BK3120 + 端子排 [KL1408, KL9100, KL3464, KL4022]。需要在上电做一次
//       "硬件巡检"：① 读耦合器自身的 reg 0..15（型号 / 固件 / 配置）；
//       ② 读 KL3464（端子号 2，因为 KL9100 是无源端子不计）的 reg 8（端子
//       型号，应得 16#0D80 = 3456 = KL3464）。结果存档供运维比对工程图纸。
//
// 价值：把"2-byte PLC interface 协议 + 批量寄存器握手 + 高低字节填表 + 超时
//       管理"封装为一次调用。业务代码只要给端子号 / 表号 / 寄存器范围。
//
// 验证：登录后置 bScanCouplerReg := TRUE 触发一次读 → 几秒后 bScanBusy
//       回 FALSE，bScanError = FALSE，stReadResult 中 [0..15] 有耦合器表
//       数据；再置 bScanKL3464Id := TRUE → stReadResult.aRegister[8] 应
//       等于 16#0D80 表明端子号正确。若 nLastErrId = 16#400 说明端子编号
//       数错了（很可能没排除无源端子）。
PROGRAM P_Demo_FB_ReadCouplerRegs
VAR
    fbReadRegs                  : FB_ReadCouplerRegs;
    rTrigScan                   : R_TRIG;

    // —— 链到耦合器 2-byte PLC interface ——
    stCouplerStatus     AT %I*  : PLCINTFSTRUCT;
    stCouplerControl    AT %Q*  : PLCINTFSTRUCT;

    // —— 业务输入：选目标 ——
    bScanCouplerReg             : BOOL;          // 单脉冲：读耦合器 reg 0..15
    bScanKL3464Id               : BOOL;          // 单脉冲：读 KL3464 reg 8
    nActiveTerminalSlot         : BYTE := TERM_COUPLER;
    nActiveTableNo              : BYTE := 0;
    nActiveStartReg             : BYTE := 0;
    nActiveEndReg               : BYTE := 15;
    tScanTimeout                : TIME := T#10S; // 给足时间

    // —— 输出 ——
    bScanBusy                   : BOOL;
    bScanError                  : BOOL;
    nLastErrId                  : UDINT;
    stReadResult                : ST_CouplerTable;

    // 翻译值
    wKL3464IdReadback           : WORD;          // 应为 16#0D80
END_VAR

// 触发选择：哪一类扫描请求拉高，就把对应的端子 / 范围装到 fbReadRegs 入口
IF bScanCouplerReg THEN
    nActiveTerminalSlot := TERM_COUPLER;
    nActiveTableNo      := 0;
    nActiveStartReg     := 0;
    nActiveEndReg       := 15;
ELSIF bScanKL3464Id THEN
    nActiveTerminalSlot := 2;                    // KL3464（KL9100 无源不计）
    nActiveTableNo      := 0;
    nActiveStartReg     := 8;
    nActiveEndReg       := 8;
END_IF

// 单次调用形式：所有 VAR_INPUT 显式赋值
fbReadRegs(
    stState        := stCouplerStatus,
    nTerminal      := nActiveTerminalSlot,
    nTable         := nActiveTableNo,
    nStartReg      := nActiveStartReg,
    nEndReg        := nActiveEndReg,
    bExecute       := bScanCouplerReg OR bScanKL3464Id,
    tTimeout       := tScanTimeout,
    stCtrl         => stCouplerControl,
    bBusy          => bScanBusy,
    bError         => bScanError,
    nErrId         => nLastErrId,
    stCouplerTable => stReadResult
);

// 完成后从 stReadResult 中按下标取出关键寄存器值，bScanX 标志由 HMI 复位
IF bScanKL3464Id AND NOT bScanBusy AND NOT bScanError THEN
    // ST_CouplerTable 内部含 reg-byte 数组；具体字段名以库定义为准
    wKL3464IdReadback := SHL(WORD#(stReadResult.aRegister[8].nHi), 8)
                       + WORD#(stReadResult.aRegister[8].nLo);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：BC / BK + KLxxx 在役系统的"硬件巡检 / 配置存档 / 启动期参数校验"。上电后程序读耦合器表寄存器记录站点的硬件配置（型号、固件版本、Profibus 地址），并对每个智能端子读其端子型号寄存器与工程图纸对比，发现接错就拒绝启动。典型行业：印刷、灌装、卷烟机老线运维。
- **价值**：把"批量寄存器访问 + 2-byte PLC interface 协议 + 高低字节解码 + 超时管理"封装为一次调用，业务代码只关心端子号 / 寄存器范围。手写实现至少 100 行状态机，本 FB 一行调用搞定。
- **替代方案对比**：
  - `ReadWriteTerminalReg` 逐个寄存器读：能做，但每个寄存器一次单独调用，序列化复杂；并且要求端子用 complex mapping 暴露 control/status 字节
  - KS2000 配置软件读：可视化但只能离线，无法在 PLC 程序中根据工艺动态触发
  - 改用 EtherCAT + EL 端子 + CoE Read：现代方案，所有参数走 SDO，可靠性更好；但要换硬件，老线改造代价高
  - **本 FB**：在不换硬件前提下让 PLC 程序能批量读耦合器 + 智能端子的内部寄存器，是 K-bus 时代的批量诊断标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42595851.html
- **相关**：`PLCINTFSTRUCT`（§5.1）、`ST_CouplerTable`（§5.5，高/低字节数组）、`ST_CouplerReg`（§5.4，单个寄存器结构）、`FB_WriteCouplerRegs`（写、配套使用）、`ReadWriteTerminalReg`（单寄存器轻量级访问）、`CouplerReset`（修改寄存器后通常需复位让改动生效）；全局常量 `TERM_COUPLER` = 0
