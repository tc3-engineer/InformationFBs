# ItpEnableFeederBackup

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Retrace` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3286629899.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpEnableFeederBackup.TcPOU`](../examples/P_Demo_ItpEnableFeederBackup.TcPOU) |

---

## 1. 功能简述

`ItpEnableFeederBackup` 启用『路径备份』——NCI 会在执行 NC 程序时把已经走过的路径段保存下来，供 Retrace（沿原路倒车）使用。**必须在 NC 程序启动前激活**；如果 NC 程序已经在跑，本 FB 不会回追前面的段。Blocksearch 配合 Retrace 使用时，本 FB 必须在 `ItpBlocksearch` 之前调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable  : BOOL;
    bExecute : BOOL;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnable` | `BOOL` | 使能位（TRUE = 启用、FALSE = 禁用），与 `bExecute` 配合做配置开关 |
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
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

**关键时序**：必须在 NC 程序启动**之前**激活路径备份。如果 Blocksearch 也参与，必须在 `ItpBlocksearch` 之前激活；流程：`ItpEnableFeederBackup(bEnable := TRUE,...)` → `ItpLoadProgEx` → `ItpBlocksearch` → `ItpStepOnAfterBlocksearch` → 程序跑起来同时备份路径段。

**为什么不能晚激活**：NC 解释器在加载和首次执行段时把段表写入内部环形缓冲；激活晚了，前期段已经被消费掉，Retrace 沿原路退回时『退到哪一段以前没有备份』就退不动了——`ItpIsFirstSegmentReached` 会立刻为 TRUE 但实际还远没退到 NC 程序开头。

**关闭备份**：`bEnable := FALSE` + `bExecute` 上升沿 → 关闭路径备份，已备份的段被丢弃。TwinCAT 重启同样会清空备份。

**典型陷阱**：① 忘记激活就调 `RetraceMoveBackward` → 命令被静默忽略，PLC 端看不到错误但轴不动。用 `ItpIsFeederBackupEnabled` 在 `RetraceMoveBackward` 之前做检查。② 长 NC 程序备份占用内存大（每个段约几十字节）；如果只关心『最近 10 段倒退』要谨慎控制激活时机。

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
- **Retrace 链顺序硬要求**：先 `ItpEnableFeederBackup(bEnable := TRUE)` → 然后启动 NC 程序 → 运行中才能 `ItpRetraceMoveBackward` / `ItpRetraceMoveForward`。顺序错了 Retrace 命令静默失败、PLC 端看不到错误但轴不动。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ItpEnableFeederBackup.TcPOU`](../examples/P_Demo_ItpEnableFeederBackup.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbItpEnableFeederBackup(
    bEnable   := bDoIt,
    bExecute  := rtTrig.Q,
    tTimeOut  := T#2S,
    sNciToPlc := sNciToPlc_inst,
    bBusy     => bBusy_out,
    bErr      => bErr_out,
    nErrId    => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：复杂轮廓加工出错（如薄壁件让刀），操作员希望沿原路退回一段、调整后再走过。
- **价值**：开启路径备份后，NCI 记下走过的段表，Retrace FB 可让轴沿原路退回。
- **替代方案对比**：① 不备份 → Retrace 完全不工作；② 备份占内存但可控（每段几十字节）；③ **本 FB**：用前激活一次即可，无后续 PLC 介入开销。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.2.52.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3286629899.html
- **相关 FB / FC**：`ItpIsFeederBackupEnabled`（查询状态）、`ItpRetraceMoveBackward` / `ItpRetraceMoveForward`

