# ItpStepOnAfterEStop

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks for compatibility with existing programs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3287964555.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpStepOnAfterEStop.TcPOU`](../examples/P_Demo_ItpStepOnAfterEStop.TcPOU) |

---

## 1. 功能简述

`ItpStepOnAfterEStop` 是 `ItpStepOnAfterEStopEx` 的旧版兼容 FB，EStop 后续接执行。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    nGrpId   : UDINT;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `nGrpId` | `UDINT` | ⚠️ 待人工确认（PDF 与 InfoSys 均未给该字段中文释义） |
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

无。

## 3. 行为说明

`ItpStepOnAfterEStop` 走 ADS 同步调用流程：在 `bExecute` 检测到上升沿时把命令打包发给 NCI、进入 `bBusy = TRUE` 状态等回包；NC 端接受后 `bBusy = FALSE`，若执行失败则 `bErr = TRUE` 并把错误号写入 `nErrId`。注意 PDF 原文明确指出 `bBusy` 监视的是 NC 端『接受』命令的时间，不是命令真正执行完成的时间——也就是说 `bBusy = FALSE` 不等于动作做完，只是 ADS 调用收到了应答。

复位规则：再次给 `bExecute` 一次上升沿，FB 会把 `bErr` 与 `nErrId` 复位为 FALSE/0 之后再发起新命令；想观察上一次的错误现场必须在再触发前读出来。`tTimeOut` 是 ADS 调用最长等待时间——超过这个值即使 NC 没回包也会强行返回，并把 `bErr = TRUE`、`nErrId` 设为 ADS 超时错误码。

**典型调用方式**：例程见 §6；本 FB 没有 VAR_IN_OUT 引脚——只通过 ADS 内部通道与 NC 通信，PLC 端只需要给好 VAR_INPUT 和接收 VAR_OUTPUT 即可。

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
- **本 FB 为旧版兼容**：仅给从 TwinCAT 2 移植的项目使用。新项目应使用 `ItpStepOnAfterEStopEx` 或 `ItpStepOnAfterEStopEx2`（带 `Ex` 后缀的版本），接口对新通道结构有完整支持。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ItpStepOnAfterEStop.TcPOU`](../examples/P_Demo_ItpStepOnAfterEStop.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbItpStepOnAfterEStop(
    bExecute := rtTrig.Q,
    nGrpId   := 0,
    tTimeOut := T#2S,
    bBusy    => bBusy_out,
    bErr     => bErr_out,
    nErrId   => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：从 TwinCAT 2 移植过来的项目，保持原 FB 接口不动。
- **价值**：移植成本低、行为兼容。
- **替代方案对比**：新项目直接使用对应 `*Ex` / `*Ex2` 版本（接口支持新通道结构）。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.4.21
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3287964555.html
- **相关 FB / FC**：见 §3 行为说明

