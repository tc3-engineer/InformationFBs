# ItpBlocksearch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Blocksearch` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3284021387.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpBlocksearch.TcPOU`](../examples/P_Demo_ItpBlocksearch.TcPOU) |

---

## 1. 功能简述

`ItpBlocksearch` 把 NCI 解释器临时停在 NC 程序指定段（按 `nBlockId` + `eBlockSearchMode` 定位），并通过 `sStartPosition` 给出该段起点坐标。操作员把物理轴搬到该坐标后，再调用 `ItpStepOnAfterBlocksearch` 让程序续接执行。常用场景是换刀 / 班次结束后续接前一程序。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute         : BOOL;
    nBlockId         : UDINT;
    eBlockSearchMode : E_ItpBlockSearchMode;
    eDryRunMode      : E_ItpDryRunMode;
    fLength          : LREAL;
    sPrgName         : STRING(255);
    nPrgLength       : UDINT;
    tTimeOut         : TIME;
    sAxesList        : ST_ItpAxes;
    sOptions         : ST_ItpBlockSearchOptions;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `nBlockId` | `UDINT` | 用作起点的 NC 程序段编号（或 EntryCounter，由 `eBlockSearchMode` 决定） |
| `eBlockSearchMode` | `E_ItpBlockSearchMode` | 块搜索定位方式：`ItpBlockSearchMode_BlockNo`=按用户写的 `N` 行号、`ItpBlockSearchMode_EntryCounter`=按内部唯一 EntryCounter、`ItpBlockSearchMode_Disable`=禁用 |
| `eDryRunMode` | `E_ItpDryRunMode` | 干跑模式：`Disable`/`SkipAll`（跳过所有，仅写 R 参数）/`SkipMotionOnly`（仅跳运动，保留延时和 M）/`SkipDwellAndMotion`（跳运动与延时，保留 R/M） |
| `fLength` | `LREAL` | 段内进入点百分比（0..100），用于在 `nBlockId` 指定段内细分起点位置 |
| `sPrgName` | `STRING(255)` | 块搜索引用的 NC 程序文件名或完整路径 |
| `nPrgLength` | `UDINT` | `sPrgName` 字符串实际长度，通常写 `LEN(sPrgName)` |
| `tTimeOut` | `TIME` | ADS 调用超时延迟（推荐 `T#1S` 起步；过短会在 `bBusy` 期间报超时错） |
| `sAxesList` | `ST_ItpAxes` | 解释器需要知道的 NCI 组内轴顺序，按 X/Y/Z/Q1.. 排列；Blocksearch 在不重建组的情况下用于运行时定位（类型 `ST_ItpAxes`） |
| `sOptions` | `ST_ItpBlockSearchOptions` | 块搜索选项结构 `ST_ItpBlockSearchOptions`：`bIsRetrace`（是否处于回退）、`bRetraceBackward`（曾反向走过）、`bScanStartPos`（开始时读当前轴位置） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy          : BOOL;
    bErr           : BOOL;
    nErrId         : UDINT;
    bDone          : BOOL;
    sStartPosition : ST_ItpBlockSearchStartPosition;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进入 ADS 后保持 TRUE，直到执行完成或超时；为 TRUE 期间输入端不再接受新命令（注意：是命令的『接受』时间被监视，不是『执行』时间） |
| `bErr` | `BOOL` | 命令执行期间发生错误时置 TRUE；命令再次触发时复位为 FALSE，具体错误号存放于 `nErrId` |
| `nErrId` | `UDINT` | 最近一次执行命令的具体错误码；命令再次触发时复位为 0；具体错误号见 ADS 错误文档或 NC 错误文档（错误码 ≥ 0x4000） |
| `bDone` | `BOOL` | 命令执行成功完成时置 TRUE |
| `sStartPosition` | `ST_ItpBlockSearchStartPosition` | 块搜索定位完成后，应当先把各物理轴搬到此处指示的坐标，然后再调用 `ItpStepOnAfterBlocksearch` 启动 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sNciToPlc : NCTOPLC_NCICHANNEL_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNciToPlc` | `NCTOPLC_NCICHANNEL_REF` | NCI → PLC 方向的循环通道接口结构（只读），类型 `NCTOPLC_NCICHANNEL_REF`，需在 System Manager Link 给输入映像 `AT %I*` |

## 3. 行为说明

`ItpBlocksearch` 走 ADS 同步调用流程：在 `bExecute` 检测到上升沿时把命令打包发给 NCI、进入 `bBusy = TRUE` 状态等回包；NC 端接受后 `bBusy = FALSE`，若执行失败则 `bErr = TRUE` 并把错误号写入 `nErrId`。注意 PDF 原文明确指出 `bBusy` 监视的是 NC 端『接受』命令的时间，不是命令真正执行完成的时间——也就是说 `bBusy = FALSE` 不等于动作做完，只是 ADS 调用收到了应答。

复位规则：再次给 `bExecute` 一次上升沿，FB 会把 `bErr` 与 `nErrId` 复位为 FALSE/0 之后再发起新命令；想观察上一次的错误现场必须在再触发前读出来。`tTimeOut` 是 ADS 调用最长等待时间——超过这个值即使 NC 没回包也会强行返回，并把 `bErr = TRUE`、`nErrId` 设为 ADS 超时错误码。

**典型调用方式**：例程见 §6；本 FB 的 VAR_IN_OUT 引脚为 `sNciToPlc : NCTOPLC_NCICHANNEL_REF`。VAR_IN_OUT 表示传引用，调用方在 PLC 端必须有一个对应类型的本地实例；对循环通道接口（`NCTOPLC_NCICHANNEL_REF` / `PLCTONC_NCICHANNEL_REF`）类型要在 System Manager 里Link 给 NCI 通道的对应接口（`AT %I*` / `AT %Q*`），不 Link 时 FB 拿到的镜像全 0。

## 4. 错误码 / 返回值

本 FB 走 ADS 调用，错误通过 `bErr = TRUE` + `nErrId : UDINT` 上报。`nErrId` 是 **TwinCAT ADS / NC 错误码**（不是 HRESULT）：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#0000_0000` | 成功 | 继续后续逻辑 |
| `16#0000_07xx` | ADS 调用层错误（超时、目标不在、不许访问等） | 检查 `tTimeOut` 是否够长、`sNetID` 路由是否通；详见 [ADS Return Codes](https://infosys.beckhoff.com/content/1033/tc3_ads_intro/374277003.html) |
| `16#0000_4xxx` | NC / NCI 通道命令错误（参数越界、组未建、轴非 Ready、Override 为 0 等） | 检查 §3 列出的调用前提；详见 [NC Error Codes](https://infosys.beckhoff.com/content/1033/tcnc/178338827.html) |

⚠️ 待人工确认：PDF 在本 FB 章节未逐条枚举具体 NC 错误码，请按上面两个文档对照实际 `nErrId` 数值定位。

## 5. 使用注意 / 常见坑

- **`bExecute` 是边沿触发不是电平触发**：一直拉高 TRUE 只第一次有效，之后改其它输入参数也不会重发。要再次触发必须先把 `bExecute` 拉回 FALSE 再 TRUE。
- **`bBusy = FALSE` ≠ 动作完成**：PDF 原文明确指出 `bBusy` 监视的是 NC 端『接受』命令的时间。对状态查询类 FB 没问题，但对真正『动起来』的命令（如 `ItpBlocksearch`），要看 `bDone` 或后续 cyclic channel interface 字段。
- **`tTimeOut` 太小会假阳性出错**：默认填 `T#1S` 起步，大文件操作（`ItpLoadProgEx` 加载大 NC 程序）需要 `T#5S` 以上。超时时 `bErr = TRUE`、`nErrId` 是 ADS 超时错误码（不是 NC 错误码）。
- **错误号要在再触发前读出来**：`bExecute` 下次上升沿会把 `bErr` / `nErrId` 复位为 FALSE/0，所以诊断逻辑必须在 `bBusy → FALSE && bErr` 一瞬间锁存错误号。
- **`sNciToPlc` 必须先 Link 给 NCI 通道**：在 System Manager 里把 PLC 端 `AT %I*` 的 `NCTOPLC_NCICHANNEL_REF` 实例 Link 给对应通道的 NCTOPLC 接口；不 Link 等于 NCI 通道镜像全 0，所有读取类 FB 拿到的都是 0。
- **Blocksearch 三步必走完**：`ItpGetBlocksearchData`（记当前位置）→ `ItpBlocksearch`（定位解释器）→ 操作员手动把物理轴搬到 `sStartPosition`（**不是 FB 自动搬，是操作员**）→ `ItpStepOnAfterBlocksearch`（续接）。跳步会让解释器位置和物理轴位置错位，恢复执行第一段就直接撞机。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ItpBlocksearch.TcPOU`](../examples/P_Demo_ItpBlocksearch.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbItpBlocksearch(
    bExecute         := rtTrig.Q,
    nBlockId         := 0,
    eBlockSearchMode := 0,
    eDryRunMode      := 0,
    fLength          := 0.0,
    sPrgName         := '',
    nPrgLength       := 0,
    tTimeOut         := T#2S,
    sAxesList        := 0,
    sOptions         := 0,
    sNciToPlc        := sNciToPlc_inst,
    bBusy            => bBusy_out,
    bErr             => bErr_out,
    nErrId           => nErrId_out,
    bDone            => bDone_out,
    sStartPosition   => sStartPosition_out
);
```

## 7. 业务场景与实际价值

- **场景**：CNC 加工到一半发现刀具磨损要换刀；或下班前『暂停在第 N 段』第二天接着干。
- **价值**：解决『程序停在哪里 → 物理轴移走 → 怎么回到那段』的难题——记录段号 + 起点坐标 → 操作员搬轴 → 续接。
- **替代方案对比**：① 重新跑整个程序 → 浪费时间、可能重复加工已完工部分；② 手动算 G-Code 跳到指定段 → 易错、漏前置 G 模态命令；③ **本 FB**：NCI 内部维护段表，定位准确，配 `Retrace` 还能沿路径回退。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.2.51.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3284021387.html
- **相关 FB / FC**：`ItpGetBlocksearchData`（记位置）、`ItpStepOnAfterBlocksearch`（续接）

