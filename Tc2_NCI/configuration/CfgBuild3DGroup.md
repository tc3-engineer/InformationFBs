# CfgBuild3DGroup

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3282424587.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_CfgBuild3DGroup.TcPOU`](../examples/P_Demo_CfgBuild3DGroup.TcPOU) |

---

## 1. 功能简述

`CfgBuild3DGroup` 把最多 3 根 PTP 轴（X/Y/Z）组合成一个 NCI 3D 插补组，是 PLC 端动态建立 CNC 通道的入口 FB。`bExecute` 上升沿触发一次配置 ADS 调用，成功后 NC 端就有了一个由这 3 根轴组成的 3D 组、可供解释器加载 G-Code 或 Tc2_PlcInterpolation 直接发段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    nGroupId : UDINT;
    nXAxisId : UDINT;
    nYAxisId : UDINT;
    nZAxisId : UDINT;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `nGroupId` | `UDINT` | 目标 NCI 通道（3D 组）的 GroupId |
| `nXAxisId` | `UDINT` | X 路径轴的 NC AxisId（在 System Manager 的 NC 配置里看到的 ID） |
| `nYAxisId` | `UDINT` | Y 路径轴的 NC AxisId |
| `nZAxisId` | `UDINT` | Z 路径轴的 NC AxisId |
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

**调用前提**：在 System Manager 的 NC 配置里已建好 X/Y/Z 三根 PTP 轴并已使能 NC 通道；在 NCI 通道节点下『把这 3 根 PTP 轴加入新 3D 组』可以在 XAE 里静态配置，也可以由本 FB 在 PLC 里运行时动态配置。

**时序**：`bExecute` 上升沿 → FB 把『建组』ADS 命令发给 NC → `bBusy = TRUE` 等回包 → 成功则 `bBusy = FALSE`，3D 组立即生效，后续解释器或 Tc2_PlcInterpolation 即可在该组上发段；失败则 `bErr = TRUE`，`nErrId` 含 NC 错误码（典型：组已存在、AxisId 不存在、轴在别的组里、轴非 Ready）。

**复位规则**：再次给 `bExecute` 上升沿会把 `bErr` / `nErrId` 复位为 FALSE/0 之后再发起新命令；想看上一次错误必须在再触发前读出来。`tTimeOut` 是 ADS 调用最长等待时间。

**典型陷阱**：① 已有同 `nGroupId` 的组未撤销就再 build，NC 返回错误；先用 `CfgReconfigGroup` 撤销旧组。② 同一 AxisId 不能同时属于两个组，必须先用 `CfgReconfigAxis` 把它从原组里抽出来。③ 三根轴必须都已 `MC_Power` 使能并处于 Standstill，否则 NC 拒绝把它们绑到 3D 组。④ 配组成功不代表能立刻发段，还要保证通道处于 IDLE（通过 `ItpGetStateInterpreter` 查）。

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

> 配套可导入文件：[`examples/P_Demo_CfgBuild3DGroup.TcPOU`](../examples/P_Demo_CfgBuild3DGroup.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbCfgBuild3DGroup(
    bExecute := rtTrig.Q,
    nGroupId := 0,
    nXAxisId := 0,
    nYAxisId := 0,
    nZAxisId := 0,
    tTimeOut := T#2S,
    bBusy    => bBusy_out,
    bErr     => bErr_out,
    nErrId   => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：定制机床每次开机由 PLC 自检后再决定『今天这一组』要绑哪三根轴——例如某 CNC 有 X1/X2 双 X 主轴可换、由 PLC 根据当前任务类型动态选 X1+Y+Z 还是 X2+Y+Z 组成 3D 插补组。
- **价值**：免去『进 XAE 改组配置 → 下载 → 重启 NC』流程，开机自动配组、运行时也能动态切换。
- **替代方案对比**：① 在 XAE 静态配组 → 部署后不能改，每个轴组合都要单独工程；② 走 ADS Write 命令直接发『build group』ADS index → 麻烦、要查 ADS index/sub-index 表；③ **本 FB**：单调用、参数显式、`bErr/nErrId` 报错，最直接。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3282424587.html
- **相关 FB / FC**：`CfgBuildExt3DGroup`（含辅助轴）、`CfgReconfigGroup`（撤组）、`CfgRead3DAxisIds`（读组内轴）

