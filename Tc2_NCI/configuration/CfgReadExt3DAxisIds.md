# CfgReadExt3DAxisIds

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3283313419.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_CfgReadExt3DAxisIds.TcPOU`](../examples/P_Demo_CfgReadExt3DAxisIds.TcPOU) |

---

## 1. 功能简述

`CfgReadExt3DAxisIds` 是 `CfgRead3DAxisIds` 的扩展版本：除了读 X/Y/Z 三轴，还把辅助轴 Q1..Q5 的 AxisId 一并读回，存到 `NCI_EXT3DGROUP` 结构里。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    nGroupId : UDINT;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `nGroupId` | `UDINT` | 目标 NCI 通道（3D 组）的 GroupId |
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
    stExt3dGroup : NCI_EXT3DGROUP;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stExt3dGroup` | `NCI_EXT3DGROUP` | 扩展 3D 组 AxisId 结构（路径轴 X/Y/Z + 5 个辅助轴 Q1..Q5） |

## 3. 行为说明

`CfgReadExt3DAxisIds` 走 ADS 同步调用流程：在 `bExecute` 检测到上升沿时把命令打包发给 NCI、进入 `bBusy = TRUE` 状态等回包；NC 端接受后 `bBusy = FALSE`，若执行失败则 `bErr = TRUE` 并把错误号写入 `nErrId`。注意 PDF 原文明确指出 `bBusy` 监视的是 NC 端『接受』命令的时间，不是命令真正执行完成的时间——也就是说 `bBusy = FALSE` 不等于动作做完，只是 ADS 调用收到了应答。

复位规则：再次给 `bExecute` 一次上升沿，FB 会把 `bErr` 与 `nErrId` 复位为 FALSE/0 之后再发起新命令；想观察上一次的错误现场必须在再触发前读出来。`tTimeOut` 是 ADS 调用最长等待时间——超过这个值即使 NC 没回包也会强行返回，并把 `bErr = TRUE`、`nErrId` 设为 ADS 超时错误码。

**典型调用方式**：例程见 §6；本 FB 的 VAR_IN_OUT 引脚为 `stExt3dGroup : NCI_EXT3DGROUP`。VAR_IN_OUT 表示传引用，调用方在 PLC 端必须有一个对应类型的本地实例；对循环通道接口（`NCTOPLC_NCICHANNEL_REF` / `PLCTONC_NCICHANNEL_REF`）类型要在 System Manager 里Link 给 NCI 通道的对应接口（`AT %I*` / `AT %Q*`），不 Link 时 FB 拿到的镜像全 0。

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
- **同一 AxisId 同时属两个组会被 NC 拒绝**：动态换组必须先 `CfgReconfigAxis` 抽出原组再 `CfgAddAxisToGroup` 加新组。
- **组操作要求通道 IDLE**：通道正在执行 NC 程序时改组会被 NC 拒绝，先 `ItpStartStopEx(bStop := TRUE)` 停下。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CfgReadExt3DAxisIds.TcPOU`](../examples/P_Demo_CfgReadExt3DAxisIds.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbCfgReadExt3DAxisIds(
    bExecute     := rtTrig.Q,
    nGroupId     := 0,
    tTimeOut     := T#2S,
    stExt3dGroup := stExt3dGroup_inst,
    bBusy        => bBusy_out,
    bErr         => bErr_out,
    nErrId       => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：定制机床、柔性产线场景下，由 PLC 在运行时动态调整 NCI 通道的轴组成。
- **价值**：免去『改 XAE 配置 → 下载 → 重启 NC』流程，把组配置变成可在线生效的 PLC 操作。
- **替代方案对比**：① 在 XAE 静态配置组 → 不灵活；② 走原始 ADS 命令直接发 → 麻烦、要查 ADS index 表；③ 本 FB 提供命名清晰的 PLC 接口。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3283313419.html
- **相关 FB / FC**：`CfgRead3DAxisIds`（仅 X/Y/Z）、`ItpGetGroupAxisIds`

