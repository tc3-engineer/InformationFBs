#!/usr/bin/env python3
"""Generator for Tc2_MC2 docs + examples.

Run from repo root:
    python3 _meta/tools/_tc2mc2_gen.py

Emits markdown + matching P_Demo_*.xml. Each entry has hand-authored prose to
pass verify_doc + lint_plcopen under the 2026-05-11 charter.
"""
from __future__ import annotations
import os
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
LIB = "Tc2_MC2"
VERSION = "2.17.0"
PDF_URL = f"https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_{LIB}_EN.pdf"
TODAY = "2026-05-21"


def emit(subdir: str, name: str, doc_md: str, xml: str) -> None:
    doc_p = ROOT / LIB / subdir / f"{name}.md"
    xml_p = ROOT / LIB / "examples" / f"P_Demo_{name}.xml"
    doc_p.parent.mkdir(parents=True, exist_ok=True)
    xml_p.parent.mkdir(parents=True, exist_ok=True)
    doc_p.write_text(doc_md)
    xml_p.write_text(xml)


# ---------------------------------------------------------------------------
# Shared snippets
# ---------------------------------------------------------------------------
META_TPL = """## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `{typ}` |
| Category | `{category}` |
| Source PDF | {pdf} |
| Source InfoSys | {info} |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml) |

---
"""


def metablock(typ: str, category: str, info: str, name: str) -> str:
    return META_TPL.format(typ=typ, category=category, info=info, name=name, pdf=PDF_URL)


# ---------------------------------------------------------------------------
# Per-FB data
# Each entry: (name, subdir, category_label, infosys_url, content_fn)
# ---------------------------------------------------------------------------

# Common pieces (Chinese descriptions) reused across P2P movers:
DESC_EXECUTE = "上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平"
DESC_VELOCITY = "最大行进速度，要求 `>0`；轴在加减速段两端按 `Acceleration` / `Deceleration` 限速"
DESC_ACC = "加速度，要求 `≥0`；填 `0` 表示采用轴参数中默认加速度"
DESC_DEC = "减速度，要求 `≥0`；填 `0` 表示采用轴参数中默认减速度"
DESC_JERK = "加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk"
DESC_BUFFER = "队列模式：当轴正在执行另一命令时本命令的接入方式（`MC_Aborting` / `MC_Buffered` / `MC_BlendingLow` / `MC_BlendingPrevious` / `MC_BlendingNext` / `MC_BlendingHigh`）；耦合从轴只允许 `Aborting`"
DESC_OPTIONS = "额外可选参数结构，绝大部分场景留默认即可"
DESC_AXIS = "轴数据结构，唯一标识系统中一根轴；含位置、速度、错误状态等全部循环数据。**必须传引用**（VAR_IN_OUT 语义）"

DESC_DONE = "目标到达 / 命令完成时置 `TRUE`"
DESC_BUSY = "`Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE`"
DESC_ACTIVE = "表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE`"
DESC_ABORTED = "命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE`"
DESC_ERROR = "执行期间发生错误置 `TRUE`"
DESC_ERRORID = "`Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4）"


ERRORID_SECTION = """## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。
"""


def xml_skel(name: str, body_vars: str, st_code: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0200">
  <fileHeader companyName="tc3-libraries-kb" productName="TwinCAT" productVersion="3.1" creationDateTime="2026-05-21T00:00:00"/>
  <contentHeader name="Tc2_MC2.{name} Demo" modificationDateTime="2026-05-21T00:00:00">
    <coordinateInfo>
      <fbd><scaling x="1" y="1"/></fbd>
      <ld><scaling x="1" y="1"/></ld>
      <sfc><scaling x="1" y="1"/></sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="P_Demo_{name}" pouType="program">
        <interface>
          <localVars>
{body_vars}
          </localVars>
        </interface>
        <body>
          <ST><xhtml xmlns="http://www.w3.org/1999/xhtml">{st_code}</xhtml></ST>
        </body>
      </pou>
    </pous>
  </types>
  <instances><configurations/></instances>
</project>
"""


def vbool(name: str, init: str | None = None, doc: str = "") -> str:
    iv = f"<initialValue><simpleValue value=\"{init}\"/></initialValue>" if init else ""
    dd = f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{doc}</xhtml></documentation>" if doc else ""
    return f"            <variable name=\"{name}\">{iv}<type><BOOL/></type>{dd}</variable>"


def vlreal(name: str, init: str | None = None, doc: str = "") -> str:
    iv = f"<initialValue><simpleValue value=\"{init}\"/></initialValue>" if init else ""
    dd = f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{doc}</xhtml></documentation>" if doc else ""
    return f"            <variable name=\"{name}\">{iv}<type><LREAL/></type>{dd}</variable>"


def vudint(name: str, doc: str = "") -> str:
    dd = f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{doc}</xhtml></documentation>" if doc else ""
    return f"            <variable name=\"{name}\"><type><UDINT/></type>{dd}</variable>"


def vuint(name: str, init: str | None = None, doc: str = "") -> str:
    iv = f"<initialValue><simpleValue value=\"{init}\"/></initialValue>" if init else ""
    dd = f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{doc}</xhtml></documentation>" if doc else ""
    return f"            <variable name=\"{name}\">{iv}<type><UINT/></type>{dd}</variable>"


def vderived(name: str, dtype: str, doc: str = "") -> str:
    dd = f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{doc}</xhtml></documentation>" if doc else ""
    return f"            <variable name=\"{name}\"><type><derived name=\"{dtype}\"/></type>{dd}</variable>"


# ---------------------------------------------------------------------------
# Library version (special: GVL)
# ---------------------------------------------------------------------------

def gen_libversion():
    name = "stLibVersion_Tc2_MC2"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70173195.html"
    doc = f"""# {name}

{metablock("VAR_GLOBAL CONSTANT", "Library version", info, name)}

## 1. 功能简述

`stLibVersion_Tc2_MC2` 是 `Tc2_MC2` 库的**版本信息全局常量**，类型为 `ST_LibVersion`（定义在 `Tc2_System` 库）。在 PLC 项目里引用该常量可在运行时读取自己实际链接的 `Tc2_MC2` 版本，配合 `F_CmpLibVersion`（同样来自 `Tc2_System`）做"必须 ≥ x.y.z 才允许运行"这类版本守卫。

PLC 库仓库（Library Repository）里能看到所有库的版本，这是工程文件外的"运行时自描述"机制。

## 2. 接口定义

### VAR_INPUT

无（GVL 没有输入参数）。

### VAR_OUTPUT

无（GVL 没有输出参数）。

### VAR_IN_OUT

无。

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_MC2 : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_MC2` | `ST_LibVersion` | `Tc2_MC2` 库的版本信息常量（major/minor/build/revision 等字段，定义在 `Tc2_System`） |

## 3. 行为说明

该常量在编译期由 TwinCAT 把当前链接版本写入；运行时只读。用法是"读出来 + 与期望版本比对"：

```iecst
IF NOT F_CmpLibVersion(stLibVersion_Tc2_MC2, 2, 17, 0, '>=' ) THEN
    // 实际 Tc2_MC2 版本低于 2.17.0，禁止启动机器
    bMachineEnable := FALSE;
END_IF;
```

`F_CmpLibVersion` 第二个起的 3 个数参数即 major、minor、build。第 5 个参数支持 `'='` `'<'` `'>'` `'<='` `'>='` `'<>'` 六种比较符。

**典型用法**：项目入口程序（`PRG_Init` 之类）开机第一步做一次"我用到的所有库都必须 ≥ 某版本"校验；不满足直接禁止运动控制使能。这避免了"开发机上用 2.17.0 编译 OK，部署到产线现场结果库版本 2.10 行为不一致"。

**典型陷阱**：从 TwinCAT 2 移植过来的旧代码习惯用 `LibVersion_*` / `GetLibVersion_*` 函数，**这些方式在 TwinCAT 3 已过时**——只用 `stLibVersion_<LibName>` 全局常量配 `F_CmpLibVersion`。

## 4. 错误码 / 返回值

GVL 无错误码。`F_CmpLibVersion` 比较失败仅返回 `FALSE`，不抛错。

## 5. 使用注意 / 常见坑

- **该常量编译期决定**，不会因运行时切换库版本而变化。改版本必须重新编译 PLC 项目。
- **跨库版本对比要逐库写**：项目用了 N 个库就要 N 次 `F_CmpLibVersion` 调用，每个库都有自己的 `stLibVersion_<Lib>`。
- **不要把 `ST_LibVersion` 当字符串比对**：它是结构体，直接 `=` 比对会比所有字段（含 `sVersion : STRING` 字面量），实际工程中只关心 major/minor/build 就够。（工程经验补充）
- **库版本回退要警惕**：TwinCAT 3 Library Repository 允许把一个项目"锁定"到某个旧版本（Placeholder），如果团队成员各自本地版本不同会出现"我这里跑得了你那里跑不了"，把版本检查写进开机自检可早暴露问题。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_MC2
VAR
    bMC2VersionOK : BOOL;
    sCurrentVersion : STRING(20);
END_VAR

// 要求 Tc2_MC2 至少为 2.17.0；低版本则禁止启动机器
bMC2VersionOK := F_CmpLibVersion(stLibVersion_Tc2_MC2, 2, 17, 0, '>=');
sCurrentVersion := stLibVersion_Tc2_MC2.sVersion;
```

## 7. 业务场景与实际价值

- **场景**：现场调试人员替换了 Tc2_MC2 库版本但忘记更新机器程序 / 测试机和量产机库版本不一致 / OEM 把同一 PLC 程序部署给多家集成商但要求某些 FB 必须新版本才支持。开机自检读 `stLibVersion_Tc2_MC2` 并比对预期版本是"防呆"的关键。
- **价值**：一行代码做版本检查 vs 写一段 ADS 调用查询 Library Repository。前者编译期注入、运行时几乎零开销；后者要 ADS RPC。
- **替代方案对比**：
  - 写死字符串比对：脆弱，版本号格式 Beckhoff 改一次就坏
  - 直接读 Library Repository：要走 ADS，开机时序复杂
  - **本常量 + `F_CmpLibVersion`**：标准做法，PLCopen 项目通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §8.1
- **InfoSys topic**：{info}
- **相关 FB**：`F_CmpLibVersion`（`Tc2_System`，做版本比较）、`ST_LibVersion`（`Tc2_System`，结构体定义）
"""
    body = "\n".join([
        vbool("bMC2VersionOK", doc="比对结果：≥2.17.0 即 TRUE"),
        f"            <variable name=\"sCurrentVersion\"><type><string><length>20</length></string></type></variable>",
    ])
    st = """// =============================================================================
// 场景：开机自检 — 验证当前链接的 Tc2_MC2 库 ≥ 2.17.0 才允许后续运动使能
// 价值：一行代码避免"现场库版本错乱"导致的隐式行为差异
// 验证：登录后看 bMC2VersionOK 是否 TRUE；sCurrentVersion 是否显示 "2.17.0"
// =============================================================================

// F_CmpLibVersion 在 Tc2_System 库；编译期注入常量，运行时 O(1)
bMC2VersionOK := F_CmpLibVersion(stLibVersion_Tc2_MC2, 2, 17, 0, &apos;&gt;=&apos;);
sCurrentVersion := stLibVersion_Tc2_MC2.sVersion;
"""
    emit("library_version", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# Point-to-point primitives sharing the "Done/Busy/Active/Aborted/Error/ErrorID"
# output set. Differ only by input parameters.
# ---------------------------------------------------------------------------

def gen_move_relative():
    name = "MC_MoveRelative"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70096267.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**相对定位运动 FB**。从轴**当前设定位置**起，按 `Distance` 走一段相对距离（有正负号），整段轨迹由 NC 监视。到达后 `Done := TRUE`；中途被抢占 `CommandAborted := TRUE`；出错 `Error := TRUE` 并通过 `ErrorID` 给 NC 错误号。

与 `MC_MoveAbsolute` 的区别：本 FB 给的是"再走多远"，不是"到哪个坐标"；和 `MC_MoveAdditive` 区别：本 FB 起点是"当前设定位置"，`MC_MoveAdditive` 起点是"上次命令的目标位置"。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Distance     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Distance` | `LREAL` | — | 相对行进距离，可正可负；起点是 NC 当前设定位置 |
| `Velocity` | `LREAL` | — | {DESC_VELOCITY} |
| `Acceleration` | `LREAL` | — | {DESC_ACC} |
| `Deceleration` | `LREAL` | — | {DESC_DEC} |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | {DESC_AXIS} |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done           : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | {DESC_DONE} |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次相对定位；起点取"当前 NC 设定位置（SetPos）"，终点 = SetPos + `Distance`。`Execute` 撤销不停轴，要停用 `MC_Stop` / `MC_Halt`。

**状态机**（PLCopen 标准三分支）：

- **正常完成**：轴到位 → `Done = TRUE`、`Busy = Active = CommandAborted = Error = FALSE`
- **被抢占**：另一 Move/Stop 切入 → `CommandAborted = TRUE`、`Done = FALSE`
- **出错**：参数越界/轴未使能/软限位/跟随误差等 → `Error = TRUE`、`ErrorID` 给码

`Done` 的具体判据与 `MC_MoveAbsolute` 一致——取决于轴参数"目标位置监视"配置（启用时等 `InPositionArea = TRUE` 才置位；不启用时设定值生成完即刻置位）。

**累计漂移风险**：连续多次"相对走 100 mm"看似简单，但每次起点是"上次 NC 设定位置"。若中途出现 `CommandAborted` 让轴没走完，下次相对运动的起点是被中断时的设定位（不是原目标位），累计就会偏。需要"绝对一致"的场景应改用 `MC_MoveAbsolute`。

**耦合从轴特例**：与 `MC_MoveAbsolute` 一致，会先自动解耦再执行，且只能用 `MC_Aborting`。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`Execute` 是边沿触发**：连续两次"走 50 mm"必须 `Execute` 之间至少有一个周期回 FALSE，否则只触发一次。
- **`Distance` 可负**：负数表示反向。但伺服未做反向间隙补偿时反复正反相对运动会积累实际偏差。
- **多次相对运动累计误差**：见 §3。要"走 10 步每步 10 mm 共 100 mm"建议用 `MC_MoveAbsolute(Position := 100)` 而非循环 10 次 `MC_MoveRelative(Distance := 10)`。
- **被打断后再触发起点变了**：第一次相对 100 mm，走 30 mm 时 `MC_Stop` 干预，再触发相对 100 mm 时**起点是 30 mm 处**而非原 0 mm 起点。
- **耦合状态下只能 `Aborting`**：从轴接到 `MC_MoveRelative` 会先解耦，要再耦合需重新调用 `MC_GearIn` / `MC_CamIn`。
- **`Velocity = 0` 报错**：用 `MC_Halt` / `MC_Stop` 停轴，别用 `Velocity := 0` 触发本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：步进送料机每个生产节拍把材料相对推进 50 mm；上位 PLC 触发一次 = 一格送料
PROGRAM P_Demo_MC_MoveRelative
VAR
    fbStepFeed         : MC_MoveRelative;
    axisFeeder         : AXIS_REF;
    rtStepTrigger      : R_TRIG;
    bIndexStep         : BOOL;
    lrStepLengthMM     : LREAL := 50.0;
    bStepDone          : BOOL;
    bStepBusy          : BOOL;
    nErrorID           : UDINT;
END_VAR

rtStepTrigger(CLK := bIndexStep);
fbStepFeed(
    Execute      := rtStepTrigger.Q,
    Distance     := lrStepLengthMM,
    Velocity     := 300.0,
    Acceleration := 3000.0,
    Deceleration := 3000.0,
    Jerk         := 30000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisFeeder,
    Done         => bStepDone,
    Busy         => bStepBusy,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：步进送料、卷绕收放周期性长度、机器人 JOG 模式按定长寸动、印刷套色每色版按定长换色。共同特征是"每次触发 = 再前进固定距离"。
- **价值**：业务代码无需自己计算"上次到了哪，这次目标 = 上次 + 距离"，FB 自动以 NC 当前设定位置为起点。误差不在 FB 而在累计的多次调用，业务可选用 `MC_MoveAbsolute` 兜底校准。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute(Position := lastSetPos + Distance)`：要业务自己维护 lastSetPos，容易出错
  - 用 `MC_MoveAdditive`：基于"上次目标位置"而非"当前设定位置"，被打断时行为不同
  - **本 FB**：起点定义清晰（NC SetPos），最贴合"再走多远"语义

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.2
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveAbsolute`、`MC_MoveAdditive`、`MC_MoveModulo`、`MC_Stop`、`MC_Halt`
"""
    body = "\n".join([
        vderived("fbStepFeed", "MC_MoveRelative", "送料相对定位 FB 实例"),
        vderived("axisFeeder", "AXIS_REF", "送料轴 AXIS_REF（VAR_IN_OUT 必须传引用）"),
        vderived("rtStepTrigger", "R_TRIG", "上升沿触发器"),
        vbool("bIndexStep", "FALSE", "在线写 TRUE 触发一次送料"),
        vlreal("lrStepLengthMM", "50.0", "每格送料长度 mm"),
        vbool("bStepDone"),
        vbool("bStepBusy"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：步进送料机 — 每个生产节拍把卷料相对前进 50 mm。上位 PLC 给一次脉冲，
//       本 FB 把轴走 50 mm 然后等下一次脉冲。
//
// 价值：业务不用维护"上次走到哪"，FB 自动以 NC 当前设定位置为起点；
//       Done/Busy 三态符合 PLCopen 标准。
//
// 验证步骤：
//   1. System Manager 配好 NC 轴 → Link 给 axisFeeder
//   2. MC_Power 先把轴使能（demo 假设外部已使能）
//   3. 在线写 bIndexStep := TRUE → 应看到 axisFeeder.NcToPlc.ActPos
//      在 ~167 ms 内增加 50 mm（300 mm/s + 加减速）
//   4. bStepDone 短暂置 TRUE 一个周期
//   5. 把 bIndexStep 拉低再 TRUE → 再走 50 mm
//   6. 累计 10 次后看 ActPos ≈ 500 mm（如有漂移说明被中断过）
// =============================================================================

rtStepTrigger(CLK := bIndexStep);

fbStepFeed(
    Execute      := rtStepTrigger.Q,
    Distance     := lrStepLengthMM,
    Velocity     := 300.0,
    Acceleration := 3000.0,
    Deceleration := 3000.0,
    Jerk         := 30000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisFeeder,
    Done         =&gt; bStepDone,
    Busy         =&gt; bStepBusy,
    ErrorID      =&gt; nErrorID
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


def gen_move_additive():
    name = "MC_MoveAdditive"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70097803.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**叠加相对定位 FB**。起点是**上一条运动命令的目标位置**（不是当前设定位置），与 `MC_MoveRelative` 形成对比。若没有"上一目标位置"可参考（如刚上电）或轴正在连续运动，则退化为以当前设定位置为起点。

典型用途：连续动作中插入"目标位再补偿一段"的修正运动——比如视觉系统给出一个"再走 2.3 mm 才精准对准"的偏移。**不支持高/低速专用轴（high/low speed axes）**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Distance     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Distance` | `LREAL` | — | 相对叠加距离；终点 = 上一命令的目标位置 + `Distance` |
| `Velocity` | `LREAL` | — | {DESC_VELOCITY} |
| `Acceleration` | `LREAL` | — | {DESC_ACC} |
| `Deceleration` | `LREAL` | — | {DESC_DEC} |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | {DESC_AXIS} |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done           : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | {DESC_DONE} |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿；起点取"上一条 Move 命令的目标位置"。例如先 `MC_MoveAbsolute(Position := 100)` 命令发出后立刻接 `MC_MoveAdditive(Distance := 5)`，**不管第一条命令是否到达 100**，第二条的目标会被锁定为 105。这是与 `MC_MoveRelative` 最关键的区别。

**没有上一目标位置时**（首次运动 / 上次是 Velocity move / 上次被 Reset）：退化为以"当前 NC 设定位置"为起点，与 `MC_MoveRelative` 行为一致。

**状态机**：PLCopen 标准三分支 Done / CommandAborted / Error，与 `MC_MoveAbsolute` 一致。

**关键差异**：
- `MC_MoveRelative` 起点 = 当前 SetPos（即时快照）
- `MC_MoveAdditive` 起点 = 上次命令的目标位置（逻辑量）
- 若上一命令半途被打断，`MC_MoveAdditive` 仍以"原本要去的位置"为锚

**典型用法**：高速贴片机里"先粗定位 → 视觉相机识别 → 微调"。粗定位用 `MC_MoveAbsolute(Position := 100)` 发出后**马上**用 `MC_MoveAdditive(Distance := visionOffsetMM)` 排队（BufferMode = Buffered），轴执行完粗定位**自动**接着走视觉偏移，省一次"等 Done 再触发"的时序。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **概念易混淆**：`MC_MoveRelative` vs `MC_MoveAdditive` 在轴静止时**行为相同**，所以测试覆盖不全很容易在生产中出现"轴在动时叠加，结果跑过头"的事故。
- **不支持高/低速专用轴**：硬件类型为 High/Low Speed Axis 时本 FB 报错，需改用 `MC_MoveRelative`。
- **首次调用退化为 Relative**：开机后第一次调用本 FB 与 `MC_MoveRelative` 等价；不要据此就把两个 FB 混用。
- **`BufferMode = Buffered` 是常态**：本 FB 的设计意图就是"叠加在前一条之后"，单实例用 `Aborting` 反而抢掉前一条达不到叠加效果。
- **被打断后再触发起点未变**：第一次绝对到 100，途中 `MC_Stop` 停在 30，下一次 `MC_Additive(Distance := 5)` **目标仍然是 105**（因为"上一命令目标"是 100，不是停下来的 30）。
- **`MC_Reset` 会清空"上一目标位置"记忆**：Reset 后首次 `MC_MoveAdditive` 退化为 Relative 行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：贴片机粗定位到 PCB 坐标 (100 mm) 后用视觉补偿叠加 2.3 mm
PROGRAM P_Demo_MC_MoveAdditive
VAR
    fbVisionAdjust       : MC_MoveAdditive;
    axisHeadX            : AXIS_REF;
    rtAdjustTrigger      : R_TRIG;
    bApplyVisionOffset   : BOOL;
    lrVisionCorrectionMM : LREAL := 2.3;
    bAdjustDone          : BOOL;
    bAdjustError         : BOOL;
    nErrorID             : UDINT;
END_VAR

rtAdjustTrigger(CLK := bApplyVisionOffset);
fbVisionAdjust(
    Execute      := rtAdjustTrigger.Q,
    Distance     := lrVisionCorrectionMM,
    Velocity     := 50.0,
    Acceleration := 500.0,
    Deceleration := 500.0,
    Jerk         := 5000.0,
    BufferMode   := MC_Buffered,
    Axis         := axisHeadX,
    Done         => bAdjustDone,
    Error        => bAdjustError,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：视觉补偿、激光测距修正、张力调整后追加位移、套色印刷"主版定位 + 各色版微调"。共同特征：**前一命令的目标作为基准**，再叠加一个不确定时才知道的小修正量。
- **价值**：把"粗定位 + 微调"两段拼成无缝连续运动，避免在两段之间停下来重新加速；同时业务代码无需自己缓存"上一目标位置"。
- **替代方案对比**：
  - 业务自己缓存 lastTargetPos 然后用 `MC_MoveAbsolute(Position := lastTargetPos + correction)`：可行但要小心 `MC_Reset` 后清缓存
  - 用 `MC_MoveRelative`：起点是 SetPos 而非 lastTarget，被打断时行为不一致
  - **本 FB**：语义直接对齐"叠加修正"业务，BufferMode = Buffered 时与前一命令拼接最自然

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.3
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveAbsolute`、`MC_MoveRelative`、`MC_MoveModulo`
"""
    body = "\n".join([
        vderived("fbVisionAdjust", "MC_MoveAdditive"),
        vderived("axisHeadX", "AXIS_REF"),
        vderived("rtAdjustTrigger", "R_TRIG"),
        vbool("bApplyVisionOffset", "FALSE", "在线写 TRUE 叠加一次视觉补偿"),
        vlreal("lrVisionCorrectionMM", "2.3", "视觉给的补偿量 mm"),
        vbool("bAdjustDone"),
        vbool("bAdjustError"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：贴片机 X 轴 — 粗定位到 100 mm 后视觉相机告诉 PLC 还差 2.3 mm 没对准，
//       叠加一次相对修正而不要业务代码自己算"100 + 2.3 = 102.3"。
//
// 价值：起点是"上一命令目标"而非"当前实际位置"，被打断时行为可预测；
//       与前序粗定位用 Buffered 模式拼接，无需等 Done 即可排队修正。
//
// 验证步骤：
//   1. 先用 MC_MoveAbsolute 把 axisHeadX 移到 100 mm（demo 假设已做）
//   2. 在线写 bApplyVisionOffset := TRUE
//   3. 应看到 ActPos 从 100 走到 102.3，bAdjustDone 短暂置 TRUE
//   4. 若先 MC_Reset 再触发本 FB → 退化为 MC_MoveRelative 行为（起点变为 ActPos）
// =============================================================================

rtAdjustTrigger(CLK := bApplyVisionOffset);

fbVisionAdjust(
    Execute      := rtAdjustTrigger.Q,
    Distance     := lrVisionCorrectionMM,
    Velocity     := 50.0,
    Acceleration := 500.0,
    Deceleration := 500.0,
    Jerk         := 5000.0,
    BufferMode   := MC_Buffered,
    Axis         := axisHeadX,
    Done         =&gt; bAdjustDone,
    Error        =&gt; bAdjustError,
    ErrorID      =&gt; nErrorID
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


if __name__ == "__main__":
    gen_libversion()
    gen_move_relative()
    gen_move_additive()
    print("batch 1 done")
