# ItpLoadProgEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `NCI POUs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3285406347.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpLoadProgEx.TcPOU`](../examples/P_Demo_ItpLoadProgEx.TcPOU) |

---

## 1. 功能简述

`ItpLoadProgEx` 把指定路径的 NC 程序（`.nc` 文件，ANSI 或 UTF-8 无 BOM）加载到 NCI 解释器。加载完成后才能用 `ItpStartStopEx` 启动通道执行。文件名给相对路径会落到默认目录（`C:\ProgramData\Beckhoff\TwinCAT\Mc\Nci`，TwinCAT 3.1 Build ≥4026）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    sPrg     : STRING(255);
    nLength  : UDINT;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平 |
| `sPrg` | `STRING(255)` | 要加载的 NC 程序文件名或完整路径；缺省路径下放 `*.nc` 文本即可（TwinCAT 3.1 Build ≥4026 → `C:\ProgramData\Beckhoff\TwinCAT\Mc\Nci`，更早版本 → `C:\TwinCAT\Mc\Nci`）。文本必须为 ANSI 或 UTF-8（无 BOM） |
| `nLength` | `UDINT` | `sPrg` 字符串实际长度，通常写 `LEN(sPrg)` |
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

**典型流程**：① 先 `CfgBuild3DGroup` / `CfgBuildExt3DGroup` 建好 3D 组（XAE 静态配置也行）。② 把 `.nc` 文件放到默认目录（TwinCAT 3.1 Build ≥4026 → `C:\ProgramData\Beckhoff\TwinCAT\Mc\Nci`，更早版本 → `C:\TwinCAT\Mc\Nci`）。③ 本 FB `bExecute` 上升沿 → ADS 调用 → `bBusy = TRUE` 等加载完成 → 成功后 `bBusy = FALSE`、文件加载到解释器。④ 用 `ItpStartStopEx` 启动通道执行。

**文件编码硬要求**：必须 ANSI 或 UTF-8（无 BOM）。UTF-8-BOM 在头部的 `EF BB BF` 三字节会被解释器当成 G-Code 中的非法字符，你看到的报错是『Syntax error at line 1』但其实是 BOM 字节作怪。VSCode 默认保存就是 UTF-8 with BOM，要改成 UTF-8。

**路径处理**：`sPrg` 给绝对路径（`C:\MyProgs\test.nc`）NC 会直接用；给相对路径或纯文件名会到默认目录下找。`nLength` 必须等于 `LEN(sPrg)`，否则 NC 会按错误长度读字符串，结果是文件名截断或带垃圾后缀。

**典型陷阱**：① `tTimeOut` 设太小（如 `T#100MS`）会在大 `.nc` 文件加载途中报超时；建议 `T#5S` 起步。② NC 程序里有 `#INCLUDE` 子程序时，必须先用 `ItpSetSubroutinePathEx` 设好查找路径，否则解释器报『找不到子程序』。

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

> 配套可导入文件：[`examples/P_Demo_ItpLoadProgEx.TcPOU`](../examples/P_Demo_ItpLoadProgEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
fbItpLoadProgEx(
    bExecute  := rtTrig.Q,
    sPrg      := '',
    nLength   := 0,
    tTimeOut  := T#2S,
    sNciToPlc := sNciToPlc_inst,
    bBusy     => bBusy_out,
    bErr      => bErr_out,
    nErrId    => nErrId_out
);
```

## 7. 业务场景与实际价值

- **场景**：加工程序按工件型号存在文件夹里（`part_001.nc`、`part_002.nc`...），PLC 根据上位机选的工件号加载对应程序。
- **价值**：加工程序与 PLC 工程解耦——上位机改工件、PLC 程序不动。新增工件只需放新 `.nc` 文件到默认目录。
- **替代方案对比**：① 在 XAE 静态配死 NC 程序文件名 → 换工件要重新部署 PLC；② 走 Tc2_PlcInterpolation 让 PLC 直接发段（不走 G-Code 文件）→ 适合简单几何，但工艺工程师不能用 CAM 软件出 G-Code 了；③ **本 FB**：CAM 出 G-Code → 放进 NCI 目录 → PLC 调本 FB 加载，工艺人员熟悉的 CNC 流程。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.2.29
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3285406347.html
- **相关 FB / FC**：`ItpLoadProg`（旧版本）、`ItpStartStopEx`（加载后启动）、`ItpSetSubroutinePathEx`（指定子程序路径）

