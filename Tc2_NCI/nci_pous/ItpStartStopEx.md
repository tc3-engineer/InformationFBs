# ItpStartStopEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `NCI POUs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3286293515.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpStartStopEx.TcPOU`](../examples/P_Demo_ItpStartStopEx.TcPOU) |

---

## 1. 功能简述

`ItpStartStopEx` 启停 NCI 通道：`bStart` 上升沿启动、`bStop` 上升沿停止（同时来沿时停止优先）。停止时 NC 端会把所有已发段表项清空、把轴受控停下，等价于一次软 EStop。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart   : BOOL;
    bStop    : BOOL;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bStart` | `BOOL` | 上升沿启动通道执行 |
| `bStop` | `BOOL` | 上升沿停止通道并删除 NC 中所有待执行表项；`bStop` 优先级高于 `bStart`，两者同时来沿时执行停止 |
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

**触发**：`bStart` 上升沿启动通道（解释器开始按已加载的 NC 程序逐段发设定值），`bStop` 上升沿停止通道——停止时 NC 端会把所有已生成段表项清空、把轴受控减速到停止。

**优先级**：同一周期 `bStart` 与 `bStop` 都收到上升沿时，**停止优先**（PDF 原文明确指出）。实际工程里不会刻意同时触发，但比如 HMI 上『Start』按钮按下时 SafetyController 同时拍急停，会出现两沿同周期到达——优先级机制保证此时通道停止。

**调用前提**：先 `ItpLoadProgEx` 加载完 `.nc` 程序，再 `ItpStartStopEx(bStart := TRUE,...)`。没加载就启动 → `bErr = TRUE`，`nErrId` 含『no program loaded』类错误码。

**典型陷阱**：① `bStart` 用电平触发（一直保持 TRUE）只第一次有效，之后再启动必须先把 `bStart` 拉回 FALSE 再 TRUE。② Stop 之后通道里所有段都清掉了，再 Start 要先重新 `ItpLoadProgEx` 加载（如果不想重加载，用 `ItpEStopEx` + `ItpStepOnAfterEStopEx`）。③ `bStop` 触发停止 ≠ EStop——这是『正常工艺停车』，要求 NC 程序立即终止。要『停下后能继续』走 EStop 流程。

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

> 配套可导入文件：[`examples/P_Demo_ItpStartStopEx.TcPOU`](../examples/P_Demo_ItpStartStopEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbItpStartStopEx(
    bStart    := rtTrig.Q,
    bStop     := FALSE,
    tTimeOut  := T#2S,
    sNciToPlc := sNciToPlc_inst,
    bBusy     => bBusy_out,
    bErr      => bErr_out,
    nErrId    => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：HMI 上『启动加工』按钮按下时调 `bStart`，『紧急停车』时调 `bStop`。
- **价值**：PLC 单调用即可启停 NC 通道，不用直接操作 cyclic channel interface 的控制位。
- **替代方案对比**：① 走 ADS 命令直接发 NC 通道控制字 → 要查 NC ADS index、错了直接卡通道；② **本 FB**：标准启停接口，stop 优先级保证安全顺序。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.2.46
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3286293515.html
- **相关 FB / FC**：`ItpStartStop`（旧版本）、`ItpLoadProgEx`（启动前加载）、`ItpEStopEx`（暂停）

