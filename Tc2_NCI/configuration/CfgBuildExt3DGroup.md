# CfgBuildExt3DGroup

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3283105291.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_CfgBuildExt3DGroup.TcPOU`](../examples/P_Demo_CfgBuildExt3DGroup.TcPOU) |

---

## 1. 功能简述

`CfgBuildExt3DGroup` 是 `CfgBuild3DGroup` 的扩展版本：在 3 个路径轴（X/Y/Z）之外，再多挂最多 5 个辅助轴（Q1..Q5），让 NCI 通道同时驱动主轴/夹具/分度盘等辅助轴。辅助轴在 G-Code 里可用 `Q1=...` `Q5=...` 引用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute  : BOOL;
    nGroupId  : UDINT;
    nXAxisId  : UDINT;
    nYAxisId  : UDINT;
    nZAxisId  : UDINT;
    nQ1AxisId : UDINT;
    nQ2AxisId : UDINT;
    nQ3AxisId : UDINT;
    nQ4AxisId : UDINT;
    nQ5AxisId : UDINT;
    tTimeOut  : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `nGroupId` | `UDINT` | 目标 NCI 通道（3D 组）的 GroupId |
| `nXAxisId` | `UDINT` | X 路径轴的 NC AxisId（在 System Manager 的 NC 配置里看到的 ID） |
| `nYAxisId` | `UDINT` | Y 路径轴的 NC AxisId |
| `nZAxisId` | `UDINT` | Z 路径轴的 NC AxisId |
| `nQ1AxisId` | `UDINT` | 辅助轴 Q1 的 NC AxisId（无辅助轴留 0） |
| `nQ2AxisId` | `UDINT` | 辅助轴 Q2 的 NC AxisId（无辅助轴留 0） |
| `nQ3AxisId` | `UDINT` | 辅助轴 Q3 的 NC AxisId（无辅助轴留 0；分配必须从 Q1 开始连续，不能跳 Q） |
| `nQ4AxisId` | `UDINT` | 辅助轴 Q4 的 NC AxisId（无辅助轴留 0） |
| `nQ5AxisId` | `UDINT` | 辅助轴 Q5 的 NC AxisId（无辅助轴留 0） |
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

**调用前提**：同 `CfgBuild3DGroup`，加上『辅助轴必须从 `nQ1AxisId` 开始连续分配』——不能空 `nQ1AxisId` 直接填 `nQ2AxisId`。

**时序**：`bExecute` 上升沿 → 走 ADS → `bBusy / bErr / nErrId` 标准状态机，与 `CfgBuild3DGroup` 一致。

**辅助轴语义**：Q1..Q5 不参与路径插补，但和路径轴共享 NCI 通道，可由 G-Code 用 `Q1=...` `Q5=...` 给出绝对/相对目标。辅助轴运动学独立——可设单独的速度/加速度/jerk 限制。

**典型陷阱**：① 辅助轴跳号（`nQ2AxisId = 0` 但 `nQ3AxisId ≠ 0`）会被 NC 拒绝。② 辅助轴数量超过 5 必须改用别的方案（NCI 通道硬上限）。③ 不需要 5 个辅助轴时把多余的 `nQxAxisId` 留 0，NC 会自动忽略。

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

> 配套可导入文件：[`examples/P_Demo_CfgBuildExt3DGroup.TcPOU`](../examples/P_Demo_CfgBuildExt3DGroup.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbCfgBuildExt3DGroup(
    bExecute  := rtTrig.Q,
    nGroupId  := 0,
    nXAxisId  := 0,
    nYAxisId  := 0,
    nZAxisId  := 0,
    nQ1AxisId := 0,
    nQ2AxisId := 0,
    nQ3AxisId := 0,
    nQ4AxisId := 0,
    nQ5AxisId := 0,
    tTimeOut  := T#2S,
    bBusy     => bBusy_out,
    bErr      => bErr_out,
    nErrId    => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：定制机床、柔性产线场景下，由 PLC 在运行时动态调整 NCI 通道的轴组成。
- **价值**：免去『改 XAE 配置 → 下载 → 重启 NC』流程，把组配置变成可在线生效的 PLC 操作。
- **替代方案对比**：① 在 XAE 静态配置组 → 不灵活；② 走原始 ADS 命令直接发 → 麻烦、要查 ADS index 表；③ 本 FB 提供命名清晰的 PLC 接口。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3283105291.html
- **相关 FB / FC**：`CfgBuild3DGroup`（仅 X/Y/Z）、`CfgReadExt3DAxisIds`（读含辅助轴）

