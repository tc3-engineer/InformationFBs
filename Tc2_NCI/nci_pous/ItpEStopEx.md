# ItpEStopEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `NCI POUs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3284240907.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpEStopEx.TcPOU`](../examples/P_Demo_ItpEStopEx.TcPOU) |

---

## 1. 功能简述

`ItpEStopEx` 触发 NC 解释器层面的 EStop：通道立即停止解释新段，已发的段在 NC 设定值生成器里按 EStop ramp 减速到停止；与轴级 EStop 不同，这是 NC 通道级停止，可以通过 `ItpStepOnAfterEStopEx` 续接执行。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    fDec     : LREAL;
    fJerk    : LREAL;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `fDec` | `LREAL` | ⚠️ 待人工确认（PDF 与 InfoSys 均未给该字段中文释义） |
| `fJerk` | `LREAL` | ⚠️ 待人工确认（PDF 与 InfoSys 均未给该字段中文释义） |
| `tTimeOut` | `TIME` | ADS 调用超时延迟（推荐 `T#1S` 起步；过短会在 `bBusy` 期间报超时错） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bErr   : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进入 ADS 后保持 TRUE，直到执行完成或超时；为 TRUE 期间输入端不再接受新命令（注意：是命令的『接受』时间被监视，不是『执行』时间） |
| `bErr` | `BOOL` | 命令执行期间发生错误时置 TRUE；命令再次触发时复位为 FALSE，具体错误号存放于 `nErrId` |
| `nErrId` | `UDINT` | 最近一次执行命令的具体错误码；命令再次触发时复位为 0；具体错误号见 ADS 错误文档或 NC 错误文档（错误码 ≥ 0x4000） |

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

**EStop 与正常 Stop 的区别**：`ItpStartStopEx(bStop)` 终止程序并清表，再启动要重新 `LoadProg`；`ItpEStopEx` 只是『暂停』，已发段在 NC 设定值生成器里按 EStop ramp 减速停下，但通道状态保留，之后调 `ItpStepOnAfterEStopEx` 即可从断点续接执行。

**触发**：`bExecute` 上升沿 → ADS 调用 → `bBusy / bErr / nErrId` 标准状态机。成功后 `ItpIsEStopEx` 会返回 TRUE 直到 `ItpStepOnAfterEStopEx`。

**典型场景**：换刀时停下 NC 程序，工人操作完后续接；冷却液不足时暂停等待；操作员需要查看某段细节时暂停。

**典型陷阱**：① EStop 触发到轴真正停下有 ramp 时间，期间『Stop 已下但轴还在动』是预期行为。② EStop 之后再发新段或新 ADS 命令大多会被通道拒绝；唯一合法的下一步动作是 `StepOnAfterEStopEx` 或彻底 Reset。

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

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ItpEStopEx.TcPOU`](../examples/P_Demo_ItpEStopEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbItpEStopEx(
    bExecute  := rtTrig.Q,
    fDec      := 0.0,
    fJerk     := 0.0,
    tTimeOut  := T#2S,
    sNciToPlc := sNciToPlc_inst,
    bBusy     => bBusy_out,
    bErr      => bErr_out,
    nErrId    => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：CNC 加工途中冷却液不足、操作员需要查看尺寸、夹具需要重新夹紧——所有『暂停一下然后继续』的场景。
- **价值**：暂停后能续接执行（`ItpStepOnAfterEStopEx`）；区别于 `ItpStartStopEx(bStop)` 的『停了就清表，要重新加载』。
- **替代方案对比**：① `ItpStartStopEx(bStop)` 停下后必须 `ItpLoadProgEx` 重加载 → 当前段位置丢失；② **本 FB**：暂停 + 续接的设计，符合 CNC 操作员『暂停一下继续』的直觉。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3284240907.html
- **相关 FB / FC**：`ItpStepOnAfterEStopEx`（续接）、`ItpIsEStopEx`（查询状态）、`ItpResetEx2`（彻底复位）

