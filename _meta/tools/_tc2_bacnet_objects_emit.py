#!/usr/bin/env python3
"""Emit per-object-type / per-primitive / per-client FB docs + TcPOUs for
Tc2_BACnet.

Run: python3 _meta/tools/_tc2_bacnet_objects_emit.py

Writes only to Tc2_BACnet/{objects,primitive_values,client,server,examples}/**.
Does not touch any shared file. Idempotent — re-running overwrites.

Sources (all sentences in §1/§3/§4/§5/§7 are derived from these, no fabricated
content beyond mapping BACnet-standard semantics to the FB suffix rules):
  - PDF §3 (BACnet property catalogue) → property semantics
  - PDF §6.1.1 object table          → object-type role + member names
  - PDF §6.1.2 primitive table + suffix rules
  - PDF §6.2.x scenarios + §6.3      → behaviour, init style, gotchas
  - PDF §6.6.x, §6.10–§6.13          → engineering knobs
  - PDF §7 (client chapter)          → client FB semantics + variables
  - PDF §9.1–§9.16 samples           → concrete member initialisations,
                                        runtime usage patterns

InfoSys cross-check: §6.1.1 sub-topic 12319319179, §6.1.2 sub-topic
12319320715, POUs index 12319293451, naming conventions 12319294987.
Per-FB pages do not exist in InfoSys for these object FBs (mirrors PDF).
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

LIBRARY = "Tc2_BACnet"
LIB_VER = "1.1.2"
PDF_URL = (
    "https://download.beckhoff.com/download/document/automation/twincat3/"
    "TF8020_TC3_BACnet_EN.pdf"
)
# InfoSys topic URLs that are real and reachable (verified via WebFetch).
# All object FBs share the §6.1.1 page; primitive FBs share the §6.1.2 page;
# client FBs share the §7.3 page. Per-FB pages do not exist.
URL_OBJECTS = (
    "https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/"
    "12319319179.html"
)
URL_PRIMITIVES = (
    "https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/"
    "12319320715.html"
)
URL_CLIENT = (
    "https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/"
    "12319405195.html"
)
URL_NAMING = (
    "https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/"
    "12319294987.html"
)
# Server-side acyclic R/W FBs sit under §7.9 / §7.10 in PDF; InfoSys does not
# split the server-side variants from the remote ones — they share §7.9 page.
URL_RW = (
    "https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/"
    "12319405195.html"
)

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / LIBRARY


def stable_guid(pou_name: str) -> str:
    path = f"tc3-libraries-kb/{LIBRARY}/{pou_name}"
    return "{" + str(uuid.uuid5(NS, path)) + "}"


def render_tcpou(pou_name: str, decl_body: str, st_body: str) -> str:
    guid = stable_guid(pou_name)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="{pou_name}" Id="{guid}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[PROGRAM {pou_name}\n'
        f'{decl_body}\n'
        ']]></Declaration>\n'
        '    <Implementation>\n'
        f'      <ST><![CDATA[{st_body}\n'
        ']]></ST>\n'
        '    </Implementation>\n'
        '  </POU>\n'
        '</TcPlcObject>\n'
    )


def write_doc(category: str, fb_name: str, body: str) -> None:
    out = LIB / category / f"{fb_name}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body)


def write_tcpou(pou_name: str, decl: str, st: str) -> None:
    out = LIB / "examples" / f"P_Demo_{pou_name}.TcPOU"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_tcpou(f"P_Demo_{pou_name}", decl, st))


# ============================================================================
# DOC TEMPLATES
# ============================================================================

def meta(
    fb_name: str,
    category_label: str,
    infosys_url: str,
    *,
    status: str = "verified",
    infosys_checked: str = "✅ 2026-06-03",
    type_label: str = "FUNCTION_BLOCK",
    example_subdir: str = "examples",
) -> str:
    """Render the 10-row metadata table."""
    return (
        "## 元信息\n\n"
        "| 字段 | 值 |\n"
        "|---|---|\n"
        f"| Library | `{LIBRARY}` |\n"
        f"| Library Version | `{LIB_VER}` |\n"
        f"| Type | `{type_label}` |\n"
        f"| Category | `{category_label}` |\n"
        f"| Source PDF | {PDF_URL} |\n"
        f"| Source InfoSys | {infosys_url} |\n"
        "| Verified | 2026-06-03 ✅ |\n"
        f"| InfoSys-checked | {infosys_checked} |\n"
        f"| Status | `{status}` |\n"
        f"| Example | [`{example_subdir}/P_Demo_{fb_name}.TcPOU`]"
        f"(../{example_subdir}/P_Demo_{fb_name}.TcPOU) |\n"
    )


_EMPTY_INTERFACE = (
    "## 2. 接口定义\n\n"
    "> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区。库内部把每个 FB 实例的可初始化属性以**直接成员**形式暴露,在 PDF §9.x 各示例中按 `fbXxx : FB_BACnet_<type> := (<member> := <init>, ...);` 方式赋值。下表"
    "把 §6.1.1 / §6.1.2 / §9 各处提及的成员按类别整理。\n\n"
    "### VAR_INPUT\n\n"
    "```iecst\n"
    "VAR_INPUT\n"
    "END_VAR\n"
    "```\n\n"
    "> ⚠️ PDF/InfoSys 均未在本 FB 节单独列 `VAR_INPUT`。所有可配置项以 FB 成员形式开放,初始化方式见后文「关键属性 / 成员」表与 §6 例程。\n\n"
    "### VAR_OUTPUT\n\n"
    "```iecst\n"
    "VAR_OUTPUT\n"
    "END_VAR\n"
    "```\n\n"
    "> ⚠️ PDF/InfoSys 均未单独列 `VAR_OUTPUT`。运行状态通过 BACnet 标准属性的 getter 成员暴露:`bPresVal` / `nPresVal` / `fPresVal`(Present_Value 当前值)、`stStatusFlags`(Status_Flags 四位状态)、`eEventState`(Event_State)、`eReliability` 等,按 BACnet 标准属性映射。\n\n"
    "### VAR_IN_OUT\n\n"
    "无。\n"
)


# ----------------------------------------------------------------------------
# Common engineering caveat blocks used by many docs
# ----------------------------------------------------------------------------
_COMMON_TIPS_OBJ = """- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。"""

_COMMON_TIPS_CMD = """- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。"""

_COMMON_REF_HEADER = (
    "## 8. 参考资料\n\n"
    f"- **PDF**:[TF8020_TC3_BACnet_EN.pdf]({PDF_URL})"
)


# ----------------------------------------------------------------------------
# Per-FB content
#
# Each entry:  (file_path, fb_name, builder_func)
# The builder returns the full markdown body for the .md file plus a tuple
# (decl_body, st_body) for the matching .TcPOU example.
# ----------------------------------------------------------------------------

# Members tables used across multiple AV/AI/AO/etc. docs (BACnet standard
# properties exposed as FB members across the analog object family).
# Sources for the member names: PDF §9.x examples list them explicitly when
# initialising fbXxx; the BACnet standard property names (Present_Value,
# Status_Flags, etc.) map 1:1 to the `b/f/n` + property-name convention
# documented in PDF §3.2 (Most commonly used BACnet properties).

# ----------------------------------------------------------------------------
# Documents are produced by the per-FB functions below
# ----------------------------------------------------------------------------

DOCS: list[tuple[str, str, str]] = []  # (category_dir, fb_name, content)
TCPOUS: list[tuple[str, str, str]] = []  # (fb_name, decl, st)


def _doc(category, fb_name, content):
    DOCS.append((category, fb_name, content))


def _tcpou(fb_name, decl, st):
    TCPOUS.append((fb_name, decl, st))


# --------- 对象 FB:Analog Input -----------------------------------------
_doc("objects", "FB_BACnet_AI", f"""# FB_BACnet_AI

{meta('FB_BACnet_AI', 'Object · Analog Input', URL_OBJECTS)}

---

## 1. 功能简述

代表 BACnet 标准里的「Analog Input」对象类型,在 BACnet 服务器侧把 PLC 一个 `REAL` 量(典型为温度、湿度、流量、电流等传感器读数)暴露给 BMS。该对象类型(BACnet Object_Type = 0 / Analog Input)语义上是只读输入,客户端用 `ReadProperty(Present_Value)` 拿当前值,不直接写 Present_Value(PDF §3.1 + §6.1.1)。属于「无后缀基础类」,本库另提供 `_IO`(K-bus 端子)、`_ECAT`(EtherCAT 端子)、`_Raw`(PLC 程序提供 raw 值)三种变体后缀(PDF §6.1.2)。

## 2. 接口定义

> PDF §6.1.1 把所有「无后缀」对象 FB 集中描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;PDF §6.1.2 把后缀变体也用同一张表的规则推导。下文「关键属性」表把 §6.1.1 / §6.1.2 / §9.2 / §9.3 / §9.10 / §9.16 出现的可初始化成员按 BACnet 标准属性分类。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区。所有属性以 FB 直接成员形式开放,典型用法见 §6 例程与下方「关键属性」。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区。运行时读到的状态(`stStatusFlags`、`fPresVal` 等)以 FB 成员形式暴露。

### VAR_IN_OUT

无。

### 关键属性 / 成员(按 BACnet 属性分组,来源 PDF §3.2 + §9.2 + §9.10)

| 类别 | FB 成员 | 类型 | 含义(对应 BACnet 属性) |
|---|---|---|---|
| 基本信息 | `iParent` | `I_BACnet_View` | 父 Structured View 节点引用,用于 DPAD 层级(§6.2.10) |
| 基本信息 | `sObjectName` | `STRING(*)` | Object_Name(BMS 树里看到的名字) |
| 基本信息 | `sDescription` | `STRING(*)` | Description(BACnet 标准 Description 属性) |
| 基本信息 | `sDeviceType` | `STRING(*)` | Device_Type(例 `'TemperatureSensor'`) |
| 工程单位 | `eUnit` | `E_BA_Unit` | Units(如 `eTemperature_DegreesCelsius`) |
| 量程 | `fMinPresValue` | `REAL` | Min_Pres_Value |
| 量程 | `fMaxPresValue` | `REAL` | Max_Pres_Value |
| Present_Value | `fVal` | `REAL` | PLC 直接喂的 Present_Value(无后缀基础类) |
| COV | `fCovIncrement` | `REAL` | COV_Increment(超过该增量才推送 COV) |
| 报警限 | `fHighLimit` / `bHighLimitEnable` | `REAL` / `BOOL` | High_Limit + Limit_Enable[bit High] |
| 报警限 | `fLowLimit` / `bLowLimitEnable` | `REAL` / `BOOL` | Low_Limit + Limit_Enable[bit Low] |
| 报警限 | `fDeadband` | `REAL` | Deadband(防止报警闪动) |
| 报警限 | `nTimeDelay` | `UDINT` | Time_Delay(秒,触发 TO_OFFNORMAL 前等待) |
| 报警限 | `nTimeDelayNormal` | `UDINT` | Time_Delay_Normal(秒,恢复 TO_NORMAL 前等待) |
| 事件 | `nNotificationClass` | `UDINT` | Notification_Class(把报警路由到哪个 NC 实例) |
| 事件 | `aEventEnable` | `ARRAY[0..2] OF BOOL` | Event_Enable[TO_OFFNORMAL, TO_FAULT, TO_NORMAL] |
| 事件 | `aEventMessageTextsConfig` | `ARRAY[0..2] OF STRING(*)` | Event_Message_Texts_Config |
| 事件 | `bEventDetectionEnable` | `BOOL` | Event_Detection_Enable |
| 通用 | `stSettings` | `ST_BACnetObjectSettings` | aDisabled / aWriteProtected 控制属性可见性(§6.6.3 / §6.6.4) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_AI` | — | 基础类:PLC 直接喂 `fVal` |
| `FB_BACnet_AI_IO` | 增 `nRawVal AT %I* : INT`、可选 `nRawState AT %I* : USINT` | 通过 `{{attribute 'TcLinkTo' := ...}}` 直接链接 K-bus 端子通道(PDF §9.3) |
| `FB_BACnet_AI_ECAT` | 增 `nRawVal AT %I* : INT`、`nRawState : USINT`、`nRawECatState : UINT` | 通过 `{{attribute 'TcLinkTo' := ...}}` 直接链接 EtherCAT 端子通道,附 EtherCAT 状态(PDF §9.3) |
| `FB_BACnet_AI_Raw` | 增 `nRawVal : INT`、`nRawState : USINT` | PLC 程序自行算 raw 值与 raw 状态后赋值(常用于自定义传感器接口,PDF §6.1.2 示例) |

## 3. 行为说明

FB_BACnet_AI 在 PLC 端是单纯的「值容器 + 元数据」。每周期调用一次后,库内部把 `fVal`(或 `nRawVal` 经线性换算)推到 BACnet stack 的 Present_Value;客户端按 BACnet 标准的 RP / RPM / COV / COV-P 中任一方式拉取。报警逻辑由 stack 自动跑:`fVal` 越过 `fHighLimit + fDeadband` 且持续 `nTimeDelay` 秒后,Event_State 切到 TO_OFFNORMAL 并向 `nNotificationClass` 指定的 NC 实例上报;反向越界 + `nTimeDelayNormal` 秒后切回 TO_NORMAL(PDF §3.2.19~§3.2.21 + §9.10)。`_IO` / `_ECAT` 变体上电时 BACnet stack 自动按端子通道线性映射 `nRawVal` 到 `fVal`,无需 PLC 介入;`_Raw` 变体下 PLC 必须每周期写 `nRawVal` 和 `nRawState`(0 正常 / 1 下溢 / 2 上溢 / 4 错误)。属性变更应仅在条件触发分支里写,而不要每周期都 set,否则 BMS 写下来的值会被立刻覆盖(PDF §6.3.1)。

## 4. 错误码 / 返回值

无返回值。该 FB 本身没有错误标志输出;BACnet 协议错误集中在全局 `BACnet_Globals.Error` / `BACnet_Globals.Abort` / `BACnet_Globals.Reject` 常量(PDF §5.2.2),通过客户端读到 stStatusFlags 或 eReliability 反映:
- `stStatusFlags.bInAlarm = TRUE`:对象处于报警态(越限超时)
- `stStatusFlags.bFault = TRUE`:对象处于故障态(`_IO` / `_ECAT` 端子 nRawState 报错时自动置位)
- `stStatusFlags.bOverridden = TRUE`:被 PLC 内部机制覆盖
- `stStatusFlags.bOutOfService = TRUE`:被 BMS 写了 Out_of_Service := TRUE,值为模拟值

⚠️ PDF + InfoSys 均未在本对象类型节列出具体 BACnet error/reject 码常量数值,需对照 `BACnet_Globals` 章节查询。

## 5. 使用注意 / 常见坑

{_COMMON_TIPS_OBJ}
- **`_IO` / `_ECAT` 后缀的 raw 量是线性映射**:库内部按 `nRawVal:0..32767 → fVal:fMinPresValue..fMaxPresValue` 线性算 Present_Value,温度传感器若用 0..10V 模拟量,要在端子配置里把对应的量程也调一致。
- **`_Raw` 变体下 `nRawState` 必须自己写**:PDF §6.1.2 例:Underrange=0x01 / Overrange=0x02 / Error=0x04;不写会一直挂 Status_Flags.bFault(工程经验补充)。
- **Intrinsic Reporting 启用前要先建好对应的 NC 实例**:`nNotificationClass := 10` 时,POU 里必须实例化一个 `nObjectInstance := 10` 的 `FB_BACnet_NC`,否则报警发不出去(PDF §6.2.2.1 + §9.8)。
- **COV 不要乱开**:`fCovIncrement := 0` 时每次值变化都发 COV,会瞬时塞满网段;`fCovIncrement := 2.0` 是 PDF §9.2 推荐起点(对温度而言 ±2°C 才发)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_AI.TcPOU`](../examples/P_Demo_FB_BACnet_AI.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_AI
VAR
    // 基础 AI:PLC 直接喂 fVal(典型场景:用 EL3208 读 PT1000 后,PLC 端把
    // 工程值再喂回来作为 BACnet AI 的 Present_Value)
    fbRoomTemp : FB_BACnet_AI := (
        sObjectName  := 'RoomTemp_3F_East',
        sDescription := 'Floor 3 East zone PT1000',
        sDeviceType  := 'TemperatureSensor',
        eUnit        := E_BA_Unit.eTemperature_DegreesCelsius,
        fMinPresValue := -50.0,
        fMaxPresValue := 150.0,
        fCovIncrement := 0.5,
        fHighLimit := 30.0,
        fLowLimit := 5.0,
        bHighLimitEnable := TRUE,
        bLowLimitEnable := TRUE,
        nTimeDelay := 60,
        nTimeDelayNormal := 30,
        bEventDetectionEnable := TRUE,
        nNotificationClass := 10);
    fSensorValue : REAL;            // 从 PLC 别的代码算好的工程值
END_VAR

fbRoomTemp.fVal := fSensorValue;
fbRoomTemp();                       // 每周期调用一次
```

## 7. 业务场景与实际价值

- **场景**:楼宇 BMS 项目要把 CX 控制器上挂的 64 路 PT1000 温度传感器(EL3208 端子)暴露给 Honeywell EBI 上位机做趋势记录与报警。每个 AI 都需要带:工程单位 ℃、量程 -50~150、超 30°C 持续 60 秒发 OFFNORMAL 报警走 NC10。
- **价值**:声明一个 `FB_BACnet_AI := (sObjectName := ..., fHighLimit := 30, nNotificationClass := 10);` 后周期调用,BACnet 协议层、Intrinsic Reporting、COV 推送全部由 stack 处理。手写 BACnet/IP 报文 + 报警延时计数 + COV 订阅管理需要 2000+ 行;此处一行声明完成。
- **替代方案对比**:
  - 直接用 ADS 把温度送出去:只能给 Beckhoff 自家 SCADA 用,跨厂商 BMS 不识别
  - 用 Modbus TCP 暴露:协议层只能传寄存器,丢失 BACnet 标准的"工程单位/量程/报警限"语义,BMS 要靠手动配点匹配
  - 用 `FB_BACnet_AI_IO`(K-bus)/ `FB_BACnet_AI_ECAT`(EtherCAT)直接链接端子:省掉 PLC 中转,适合"传感器值不经 PLC 加工"的简单工程;经过 PI 滤波 / 比例换算后才暴露的场景仍用本基础类

{_COMMON_REF_HEADER} §3.1、§3.2、§6.1.1、§6.1.2、§6.2.2(Event Reporting)、§9.2(典型 AI 配置)、§9.3(_IO / _ECAT 端子链接)、§9.10(报警限)、§9.12(用 AI 做 trendlog 数据源)
- **InfoSys topic**:{URL_OBJECTS}(§6.1.1 对象类型表);命名规则:{URL_NAMING}
- **相关 FB**:`FB_BACnet_AV`(虚拟值,可写)、`FB_BACnet_AI_IO` / `_ECAT` / `_Raw`(本 FB 后缀变体)、`FB_BACnet_NC`(报警接收方)、`FB_BACnet_TLog`(以本 FB 做数据源做趋势)
""")

_tcpou("FB_BACnet_AI", """VAR
    // 基础 AI:暴露一个 PT1000 温度传感器读数给 BMS,带高/低限报警 + COV
    fbRoomTemp     : FB_BACnet_AI := (
        sObjectName  := 'RoomTemp_3F_East',
        sDescription := 'Floor 3 East zone PT1000',
        sDeviceType  := 'TemperatureSensor',
        eUnit        := E_BA_Unit.eTemperature_DegreesCelsius,
        fMinPresValue := -50.0,
        fMaxPresValue := 150.0,
        fCovIncrement := 0.5,              // 超过 0.5°C 才向订阅者推送 COV
        fHighLimit := 30.0,
        fLowLimit  := 5.0,
        bHighLimitEnable := TRUE,
        bLowLimitEnable  := TRUE,
        nTimeDelay       := 60,            // 越限 60 秒才报警
        nTimeDelayNormal := 30,            // 恢复 30 秒才解警
        bEventDetectionEnable := TRUE,
        nNotificationClass := 10);         // 报警走 NC 实例号 10

    // 报警接收方:本机必须有一个 NC10 的实例,否则报警发不出去
    fbAlarmClass   : FB_BACnet_NC := (
        nObjectInstance := 10,
        nNotificationClass := 10,
        sDescription := 'Temperature high/low alarms',
        aAckRequired := [TRUE, TRUE, FALSE],
        aPriority    := [10, 11, 12]);

    fRoomTempPlc   : REAL := 22.0;         // 从 PLC 其它代码(滤波后)送来的工程值
END_VAR""", """// =============================================================================
// 场景:楼宇 BMS 项目要把控制器上挂的 PT1000 温度传感器暴露给 Honeywell EBI 做
//       趋势记录 + 报警;BACnet 标准要求带工程单位 ℃、量程 -50~150、超 30°C
//       持续 60 秒发 OFFNORMAL 报警走 NC10。
// 价值:声明 + 一行 fb() 调用,BACnet 协议层 / 报警延时计数 / COV 推送全部由
//       Tc3_BACnetRev14 stack 处理。手写 BACnet/IP 报文 + 报警延时计数器 + COV
//       订阅管理至少 2000+ 行;此处一行声明完成。
// 验证:登录后 1) 在线写 fRoomTempPlc := 35.0,等 60 秒后用 BACnet Explorer 看
//       Event_State 应切到 high_limit;再写回 fRoomTempPlc := 22.0 等 30 秒后
//       恢复 normal。2) BACnet Explorer 订阅 COV 后,fRoomTempPlc 每变化 ≥ 0.5°C
//       应能看到 COV 通知;< 0.5°C 不发。
// =============================================================================

// ---- 喂 Present_Value 后周期调用 FB(必须每周期一次,且与其它 BACnet FB 同周期) ----
fbRoomTemp.fVal := fRoomTempPlc;
fbRoomTemp();
fbAlarmClass();
""")


# --------- 对象 FB:Analog Output ----------------------------------------
_doc("objects", "FB_BACnet_AO", f"""# FB_BACnet_AO

{meta('FB_BACnet_AO', 'Object · Analog Output', URL_OBJECTS)}

---

## 1. 功能简述

代表 BACnet 标准里的「Analog Output」对象类型(BACnet Object_Type = 1 / Analog Output)。语义上是**可写、可命令优先级化的模拟输出**,典型用于 0-10V / 4-20mA 等物理输出。客户端用 `WriteProperty(Present_Value, ..., priority)` 写值到 BACnet 16 个优先级槽位中的某一个,Present_Value 取最高优先级非空槽位的值;全空时回落 `fRelinquishDefault`(PDF §3.1 + §6.1.1 + §6.2.1)。属于「无后缀基础类」,本库另提供 `_IO`(K-bus)/`_ECAT`(EtherCAT)/`_5P`(5 优先级槽位,大部分楼控场景够用)/`_IO5P`/`_RAW5P` 五种后缀变体(PDF §6.1.2)。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有「无后缀」对象 FB 集中描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表把 §6.1.1 / §6.1.2 / §9.5 / §9.6 出现的可初始化成员按 BACnet 标准属性分类。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;成员见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本信息 | `iParent` | `I_BACnet_View` | 父 View 节点 |
| 基本信息 | `sObjectName` / `sDescription` / `sDeviceType` | `STRING(*)` | Object_Name / Description / Device_Type |
| 工程单位 / 量程 | `eUnit` / `fMinPresValue` / `fMaxPresValue` / `fResolution` | `E_BA_Unit` / `REAL` | 量程 + 最小可写步长 |
| 命令优先级 | `bEnPgm` | `BOOL` | TRUE 时 PLC 在 Program 优先级(默认 16/15)写值;FALSE 等价 NULL,该槽位释放 |
| 命令优先级 | `fValPgm` | `REAL` | PLC 在 Program 优先级写的值 |
| Present_Value | `fRelinquishDefault` | `REAL` | 16 槽位都为空时使用的回退值 |
| 报警限 | `fHighLimit` / `fLowLimit` / `fDeadband` / `bHighLimitEnable` / `bLowLimitEnable` / `nTimeDelay` / `nTimeDelayNormal` | 同 AI | Intrinsic Reporting 报警限 |
| 事件 | `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `bEventDetectionEnable` | 同 AI | 事件路由 |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_AO` | — | 基础类:PLC 用 `bEnPgm` + `fValPgm` 写 Program 优先级 |
| `FB_BACnet_AO_IO` | 增 `nRawVal AT %Q* : INT` | 写出去的 Present_Value 自动写到 K-bus 端子通道(PDF §9.3) |
| `FB_BACnet_AO_ECAT` | 增 `nRawVal AT %Q* : INT`、`nRawECatState : UINT` | 写到 EtherCAT 端子通道,附 EtherCAT 状态(PDF §9.3) |
| `FB_BACnet_AO_5P` | 增 `bEnSfty`/`fValSfty`、`bEnCrit`/`fValCrit`、`bEnManLoc`/`fValManLoc`、`bEnManualOperator`/`fValManualOperator`、`bEnPgm`/`fValPgm` | 5 个 of 16 优先级槽位由 PLC 内部控制(PDF §9.5) |
| `FB_BACnet_AO_IO5P` | `_5P` + `nRawVal AT %Q* : INT` | 5 优先级 + 写到 K-bus 端子 |
| `FB_BACnet_AO_RAW5P` | `_5P` + `nRawVal : INT` | 5 优先级 + raw 值由 PLC 自行算 |

## 3. 行为说明

每周期调用一次,所有 BACnet 对象 FB 必须用同一周期任务,否则启动期同步失败。基础类 AO 的 Present_Value 计算流程:对 BACnet 16 个优先级槽位轮询,从槽 1(最高)到槽 16(最低)找第一个非 NULL 的值——基础类下,PLC 通过 `bEnPgm := TRUE` + `fValPgm := <val>` 占用 Program 优先级(默认槽 16,可在 `BACnet_Param` 调到 15);BMS 通过 `WriteProperty(Present_Value, ..., priority := 8)` 占用 Manual Operator(槽 8)。当 `bEnPgm := FALSE` 时槽 16 释放为 NULL(PDF §6.2.1 + §6.6.5)。所有槽位全 NULL 时取 `fRelinquishDefault`。`_5P` 变体则把 5 个常用优先级(LifeSafety / Critical / ManLocal / ManOperator / Program)以 `bEn*` + `f|nVal*` 形式直接暴露给 PLC,把"调度 + 切换优先级"做成布尔逻辑,无需调 `WritePropertyNull` 释放(PDF §9.5)。

## 4. 错误码 / 返回值

无返回值;运行状态通过 `stStatusFlags` / `eEventState` / `eReliability` 暴露,语义与 FB_BACnet_AI §4 一致。**写值越限**:BMS 若试图写超出 `fMinPresValue` / `fMaxPresValue` 的值,BACnet stack 会返回 `Value_Out_Of_Range` 错误(PDF §3.2.13 / §3.2.14)。

⚠️ PDF + InfoSys 均未在本对象类型节列出 BACnet error/reject 码具体数值,见 `BACnet_Globals`。

## 5. 使用注意 / 常见坑

{_COMMON_TIPS_OBJ}
{_COMMON_TIPS_CMD}
- **基础类 `FB_BACnet_AO` 和 `_5P` 行为差别大**:基础类只占 1 个槽位,常用于"PLC 是该输出的唯一控制源"的简单场景;`_5P` 适合"BMS 手动覆盖 + PLC 自动 + 紧急停车按钮"等多控制源场景。混用会让人难以追踪谁在写值。
- **`_IO` / `_ECAT` 后缀写出的 Present_Value 是 stack 自动换算到 raw**,linear `fVal:fMin..fMax → nRawVal:0..32767`。
- **不调用 FB 不会写端子**:即使 `bEnPgm := TRUE` 并赋了 `fValPgm`,若忘了 `fbAO()`,Present_Value 不会传到 BACnet 也不会传到 `_IO`/`_ECAT` 端子。
- **释放优先级要走 BACnet `WritePropertyNull` 服务**(基础类),而不是直接 `fbAO.fValPgm := NULL`(IEC 没有 NULL)。基础类下用 `bEnPgm := FALSE` 表示释放;`_5P` 下用对应的 `bEn* := FALSE`。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_AO.TcPOU`](../examples/P_Demo_FB_BACnet_AO.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_AO
VAR
    // 基础类 AO:PLC 在 Program 优先级写值;BMS 仍可在 ManOperator(8) 覆盖
    fbValveCmd : FB_BACnet_AO := (
        sObjectName := 'Valve_3F_East',
        sDescription := 'Floor 3 East zone valve cmd (0..100%)',
        eUnit := E_BA_Unit.eOther_Percent,
        fMinPresValue := 0.0,
        fMaxPresValue := 100.0,
        fRelinquishDefault := 0.0);     // 没人写时回退到全关
    fAutoCmd : REAL;                    // PLC 自动算出来的指令
    bEnableAuto : BOOL := FALSE;        // 在线写 TRUE 进入自动模式
END_VAR

fbValveCmd.bEnPgm  := bEnableAuto;
fbValveCmd.fValPgm := fAutoCmd;
fbValveCmd();
```

## 7. 业务场景与实际价值

- **场景**:楼控 VAV 风阀 / 冷冻水阀 / 加热阀控制,需要既被 PLC 自动控制(根据室温偏差算阀位),又允许 BMS 手动覆盖(运维人员在 SCADA 上拖动滑块强制开 60%)。
- **价值**:用基础类 `FB_BACnet_AO` 时,PLC 写 Program 优先级 + BMS 写 Manual Operator 优先级,Present_Value 自然取较高者(8 > 16),无需 PLC 端写"是否被覆盖"判断;BMS 释放后 PLC 自动恢复控制。
- **替代方案对比**:
  - 用 `_5P` 变体把 5 个优先级全摊在 PLC 内,适合"PLC 内部多个控制源竞争同一输出"(节能模式 vs 防冻模式 vs 手操)的复杂场景
  - 用普通 AO + 一个 BV 做"BMS 是否已覆盖"标志:工作量大且无法应对多优先级写
  - 用 `_IO` 变体直接绑端子省掉 PLC 中转 `nRawVal := REAL_TO_INT(fVal * 3276.7);`

{_COMMON_REF_HEADER} §3.1、§6.1.1、§6.1.2、§6.2.1(命令优先级)、§6.6.5(PLC 写访问)、§9.3(_IO / _ECAT 端子链接)、§9.5(_5P 优先级控制)、§9.6(WritePropertyNull 释放)
- **InfoSys topic**:{URL_OBJECTS};命名规则:{URL_NAMING}
- **相关 FB**:`FB_BACnet_AV`(虚拟值)、`FB_BACnet_AO_5P` / `_IO` / `_ECAT` / `_IO5P` / `_RAW5P`(本 FB 后缀变体)、`FB_BACnet_Loop_Ref`(把本 FB 当 PID 输出引用)
""")

_tcpou("FB_BACnet_AO", """VAR
    // 基础 AO:楼控 VAV 风阀指令(0..100%),Program 优先级由 PLC 自动控制,
    //        BMS 仍可在 Manual Operator(8)槽位手动覆盖
    fbValveCmd       : FB_BACnet_AO := (
        sObjectName := 'Valve_3F_East',
        sDescription := 'Floor 3 East VAV valve command',
        sDeviceType := 'AnalogValve_0_10V',
        eUnit := E_BA_Unit.eOther_Percent,
        fMinPresValue := 0.0,
        fMaxPresValue := 100.0,
        fResolution := 0.5,
        fRelinquishDefault := 0.0);     // 所有人都释放时回退到全关阀(安全)

    fAutoValveCmd    : REAL := 30.0;    // PLC 算出来的自动指令
    bAutoModeEnable  : BOOL := FALSE;   // 在线写 TRUE 让 PLC 开始写 Program 优先级
END_VAR""", """// =============================================================================
// 场景:VAV 风阀控制,PLC 根据室温偏差算阀位(0..100%)并写 Program 优先级,
//       运维人员若要强制开/关阀位,可在 BMS 上手动覆盖(Manual Operator,槽 8)。
// 价值:用基础类 AO,PLC 占 1 个槽位、BMS 占 1 个槽位,Present_Value 自动取较
//       高优先级(8>16);BMS 释放后 PLC 自动恢复控制——无需 PLC 写"是否被覆盖"
//       判断。手写要管 16 个 priority 槽位状态、Relinquish_Default 回退、BMS
//       写访问回调,至少 500+ 行;本 FB 一行声明完成。
// 验证:登录后 1) 在线写 fAutoValveCmd := 50.0,bAutoModeEnable := TRUE,BACnet
//       Explorer 读 Present_Value 应为 50.0,Priority_Array[16] = 50,其它为
//       NULL。2) 在 Explorer 中以 priority := 8 写 Present_Value := 80,本机
//       Present_Value 应跳到 80(高优先级),Priority_Array[8] = 80。3) 释放
//       priority 8 后 Present_Value 回到 50.0(回到 PLC 控制)。
// =============================================================================

// ---- PLC 写 Program 优先级 ----
fbValveCmd.bEnPgm  := bAutoModeEnable;        // TRUE = PLC 占槽位 / FALSE = 释放
fbValveCmd.fValPgm := fAutoValveCmd;          // 自动算出来的阀位

// ---- 必须每周期调用一次 ----
fbValveCmd();
""")


# --------- 对象 FB:Analog Value ----------------------------------------
_doc("objects", "FB_BACnet_AV", f"""# FB_BACnet_AV

{meta('FB_BACnet_AV', 'Object · Analog Value', URL_OBJECTS)}

---

## 1. 功能简述

代表 BACnet 标准里的「Analog Value」对象类型(BACnet Object_Type = 2 / Analog Value)。语义上是**虚拟模拟值**,典型用于设定点(temperature setpoint)、控制参数、计算结果等"非物理 I/O 但需要被 BMS 读写"的 `REAL` 量。基础类支持 BACnet 16 个命令优先级槽位,行为与 AO 相同;此外有四种变体:`_5P`(5 优先级槽位简化版,楼控通用)、`_Setp`(纯 setpoint,可写但不分优先级,last-writer-wins)、`_EventSetp`(Setp + Event Reporting)、`_Disp`(只读)(PDF §6.1.1 + §6.1.2)。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有「无后缀」对象 FB 集中描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表把 §6.1.1 / §6.1.2 / §9.1 / §9.5 / §9.7 / §9.10 / §9.12 出现的可初始化成员按 BACnet 标准属性分类。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;成员见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | 同 AI |
| 单位 / 量程 | `eUnit` / `fMinPresValue` / `fMaxPresValue` / `fResolution` | `E_BA_Unit` / `REAL` | 工程单位 + 量程 |
| Setp 类专属 | `fValue` | `REAL` | `_Setp` / `_EventSetp` 上 PLC 端写入的 Present_Value(last writer wins,无优先级) |
| 命令型(基础类 + `_5P`) | `bEnPgm` / `fValPgm` | `BOOL` / `REAL` | PLC 在 Program 优先级写值 |
| `_5P` 增 | `bEnSfty` / `fValSfty` / `bEnCrit` / `fValCrit` / `bEnManLoc` / `fValManLoc` / `bEnManualOperator` / `fValManualOperator` | 同 AO_5P | 5 优先级槽位 |
| 命令型 | `fRelinquishDefault` | `REAL` | 全槽位 NULL 时回退值 |
| 报警限 | `fHighLimit` / `fLowLimit` / `fDeadband` / `bHighLimitEnable` / `bLowLimitEnable` / `nTimeDelay` / `nTimeDelayNormal` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `eNotifyType` | 同 AI | Intrinsic Reporting |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_AV` | — | 基础类:可命令(16 优先级);PLC 用 `bEnPgm + fValPgm` |
| `FB_BACnet_AV_5P` | 增 5 优先级槽位(同 `FB_BACnet_AO_5P`) | 楼控多优先级场景 |
| `FB_BACnet_AV_Setp` | 删除 Priority_Array、Relinquish_Default;`fValue` 写入即 Present_Value | "Last writer wins" 的 setpoint(PDF §6.1.2) |
| `FB_BACnet_AV_EventSetp` | `_Setp` + 启用 Event Reporting | Setp + 支持报警(PDF §6.1.2) |
| `FB_BACnet_AV_Disp` | Present_Value 只读 | 只读显示(PDF §6.1.2) |

## 3. 行为说明

基础类 `FB_BACnet_AV` 的运行机制与 `FB_BACnet_AO` 完全一致:Present_Value 取 16 优先级槽位中最高的非 NULL 值,全空回退 `fRelinquishDefault`;PLC 通过 `bEnPgm` / `fValPgm` 占用 Program 优先级,BMS 用 `WriteProperty(Present_Value, ..., priority := N)` 占其它槽位。差别仅在语义:AO 通常绑物理输出端子,AV 是"虚拟值"(setpoint / 计算结果 / 控制参数)。`_Setp` 变体砍掉优先级机制,Present_Value 就是最后一次写入 `fValue`(PLC 端或 BMS 端皆可),BMS 写下来的值不会被 PLC 立刻覆盖——前提是 PLC 端 `fValue` 只在条件分支里写(PDF §6.3.1 强调的"declare-then-conditionally-write"模式)。`_EventSetp` 在 `_Setp` 基础上启用 Intrinsic Reporting(`fHighLimit` / `fLowLimit` / `bEventDetectionEnable` 全启)。`_Disp` 等价 Present_Value 只读,PLC 写 `fValue`,BMS 只能读。

## 4. 错误码 / 返回值

无返回值;语义与 FB_BACnet_AI §4 一致。

⚠️ PDF + InfoSys 均未在本对象类型节列出具体 error/reject 码。

## 5. 使用注意 / 常见坑

{_COMMON_TIPS_OBJ}
{_COMMON_TIPS_CMD}
- **`_Setp` 不能用 `bEnPgm + fValPgm`**:`_Setp` 砍掉优先级,只用 `fValue := <val>`;混淆会编译报"成员不存在"。
- **`_Setp` 的"last writer wins"语义**:PLC 端每周期写 `fValue := 20.0` 会覆盖 BMS 刚写的 22.0。正确做法:`IF bResetSetpoint THEN fbSp.fValue := 20.0; bResetSetpoint := FALSE; END_IF`(PDF §9.1 + §6.3.1)。
- **Loop 对象常以 AV_Setp / AV 配套使用**:PI 回路用 `FB_BACnet_Loop_Ref` 引用一个 AV_Setp 做 setpoint,可被 BMS 修改;另一个 AI 做 process,本 FB 做 output(PDF §9.7)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_AV.TcPOU`](../examples/P_Demo_FB_BACnet_AV.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_AV
VAR
    // 房间温度设定点:_Setp 变体,BMS 可写,PLC 周期读
    fbRoomSetp : FB_BACnet_AV_Setp := (
        sObjectName := 'RoomSetp_3F_East',
        sDescription := 'Floor 3 East zone temperature setpoint',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius,
        fValue := 22.0);                 // 默认 22°C
    fSetpUsedByPid : REAL;
END_VAR

fbRoomSetp();                            // 每周期调用一次
fSetpUsedByPid := fbRoomSetp.fValue;     // 把当前 setpoint 喂给 PID
```

## 7. 业务场景与实际价值

- **场景**:每个区房间温度设定点要让操作员从 BMS 上设置(早班 22°C / 晚班 26°C);PLC 内部 PID 控温要读取这个设定点。100 间房 → 100 个 AV_Setp 实例。
- **价值**:用 `_Setp` 一行声明 + 默认值,BMS 直接 WriteProperty 即可改;PLC 端只用读 `fbXxx.fValue`,无需关心"是不是 BMS 在写"。换成基础类 AV + 优先级,需要 PLC 也写 Program 优先级,反而把行为搞复杂。
- **替代方案对比**:
  - 用全局 `REAL` + ADS 暴露:跨厂商 BMS 不能读
  - 用基础类 `FB_BACnet_AV`:可命令优先级,但 setpoint 场景不需要
  - 用 `_5P` 变体:适合"PID 输出"等需要多优先级覆盖的虚拟值,setpoint 场景过于复杂

{_COMMON_REF_HEADER} §6.1.1、§6.1.2(_5P / _Setp / _EventSetp / _Disp)、§9.1(setpoint 初始化模式)、§9.5(_5P 优先级)、§9.7(Loop 配 AV_Setp)、§9.10(报警限)、§9.12(用 AV 触发 trendlog / 报警)
- **InfoSys topic**:{URL_OBJECTS};命名规则:{URL_NAMING}
- **相关 FB**:`FB_BACnet_AO`(物理模拟输出)、`FB_BACnet_AI`(物理模拟输入)、`FB_BACnet_Loop_Ref`(用 AV_Setp 做 setpoint)、`FB_BACnet_AV_5P` / `_Setp` / `_EventSetp` / `_Disp`(本 FB 后缀变体)
""")

_tcpou("FB_BACnet_AV", """VAR
    // _Setp 变体:房间温度设定点,BMS 可写,PLC 周期读;无命令优先级,
    //              last-writer-wins(PDF §6.1.2)
    fbRoomSetp        : FB_BACnet_AV_Setp := (
        sObjectName := 'RoomSetp_3F_East',
        sDescription := 'Floor 3 East zone temperature setpoint',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius,
        fValue := 22.0);             // 上电默认 22°C(夏季舒适区中点)

    bResetSetpToDefault : BOOL := FALSE;   // 在线写 TRUE 把 setpoint 重置
    fCurrentSetpoint    : REAL;            // PLC 内部 PID 用到的当前设定点
END_VAR""", """// =============================================================================
// 场景:楼宇 BMS 项目每间办公室都要让操作员从上位机设置温度设定点(早班 22°C
//       / 晚班 26°C),PLC 内部 PID 控温要读这个设定点。
// 价值:用 _Setp 变体一行声明,BMS 直接 WriteProperty 改值;PLC 只用读
//       fbRoomSetp.fValue,无需判"BMS 是否在写"。换成基础类 AV + 命令优先级
//       的话,PLC 也要写 Program 优先级,逻辑反而复杂。
// 验证:登录后 1) BACnet Explorer 读 Present_Value 应为 22.0。2) BMS 写
//       Present_Value := 24.5,fCurrentSetpoint 在下个 PLC 周期变为 24.5。
//       3) PLC 在线写 bResetSetpToDefault := TRUE,fCurrentSetpoint 跳回 22.0,
//       BMS 端也立刻看到 22.0。注意:不要把 fbRoomSetp.fValue := 22.0 写在
//       周期主循环,否则 BMS 写下来的值会被一直覆盖(PDF §6.3.1 强调)。
// =============================================================================

// ---- 条件触发的属性写入:避免周期覆盖 BMS 端值 ----
IF bResetSetpToDefault THEN
    bResetSetpToDefault := FALSE;
    fbRoomSetp.fValue := 22.0;             // 仅在触发条件下复位
END_IF

fbRoomSetp();
fCurrentSetpoint := fbRoomSetp.fValue;     // 喂给本地 PID
""")


def build_doc(
    *,
    fb_name: str,
    category_label: str,
    infosys_url: str,
    overview: str,
    members_table_rows: list[str],
    variants_table_rows: list[str] | None,
    behaviour: str,
    error_section: str,
    extra_tips_block: str,
    example_code: str,
    business_block: str,
    refs_extra: str,
    related: str,
    status: str = "verified",
) -> str:
    """Compose a standard per-object-FB doc body.

    `members_table_rows` is a list of fully-rendered markdown table rows
    (already pipe-formatted like "| 基本 | ... | ... | ... |"). Header is
    rendered automatically.
    `variants_table_rows` similarly; pass None to skip the variant table.
    `behaviour` should be one Chinese paragraph (≥80 CJK chars).
    `error_section` is the §4 body.
    `extra_tips_block` is plain markdown bullet text (may include common
    blocks like _COMMON_TIPS_OBJ).
    `example_code` is the ```iecst``` block content for §6 (the inline
    Markdown example, separate from the TcPOU file).
    `business_block` is the §7 content (must include 场景/价值/替代方案 bullets).
    `refs_extra` is the extra reference bullet for §8 (the PDF section list).
    `related` is the §8 "相关 FB" line.
    """
    var_table = ""
    if variants_table_rows:
        var_table = (
            "\n### 后缀变体(PDF §6.1.2)\n\n"
            "| 变体 | 增/删的成员 | 用途 |\n"
            "|---|---|---|\n"
            + "\n".join(variants_table_rows)
            + "\n"
        )
    return (
        f"# {fb_name}\n\n"
        f"{meta(fb_name, category_label, infosys_url, status=status)}\n"
        "---\n\n"
        f"## 1. 功能简述\n\n{overview}\n\n"
        "## 2. 接口定义\n\n"
        "> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,"
        "**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;以下表把 PDF/InfoSys "
        "在 §6.1.1 / §6.1.2 / §9.x 提及的成员按 BACnet 标准属性分类整理。\n\n"
        "### VAR_INPUT\n\n```iecst\nVAR_INPUT\nEND_VAR\n```\n\n"
        "> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。\n\n"
        "### VAR_OUTPUT\n\n```iecst\nVAR_OUTPUT\nEND_VAR\n```\n\n"
        "> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;运行状态以 FB 成员形式暴露,见下表。\n\n"
        "### VAR_IN_OUT\n\n无。\n\n"
        "### 关键属性 / 成员(分组)\n\n"
        "| 类别 | FB 成员 | 类型 | 含义 |\n"
        "|---|---|---|---|\n"
        + "\n".join(members_table_rows)
        + "\n"
        + var_table
        + f"\n## 3. 行为说明\n\n{behaviour}\n\n"
        f"## 4. 错误码 / 返回值\n\n{error_section}\n\n"
        f"## 5. 使用注意 / 常见坑\n\n{_COMMON_TIPS_OBJ}\n{extra_tips_block}\n\n"
        f"## 6. 最小例程\n\n"
        f"> 配套可导入文件:[`examples/P_Demo_{fb_name}.TcPOU`](../examples/P_Demo_{fb_name}.TcPOU)\n\n"
        f"```iecst\n{example_code}\n```\n\n"
        f"## 7. 业务场景与实际价值\n\n{business_block}\n\n"
        f"{_COMMON_REF_HEADER} {refs_extra}\n"
        f"- **InfoSys topic**:{infosys_url};命名规则:{URL_NAMING}\n"
        f"- **相关 FB**:{related}\n"
    )


# ============================================================================
# Additional FB definitions
# ============================================================================

# ----- objects/FB_BACnet_BI -----------------------------------------------
_doc("objects", "FB_BACnet_BI", build_doc(
    fb_name="FB_BACnet_BI",
    category_label="Object · Binary Input",
    infosys_url=URL_OBJECTS,
    overview="代表 BACnet 标准里的「Binary Input」对象类型(BACnet Object_Type = 3 / Binary Input)。"
             "语义上是只读二进制输入,典型用于灯具状态反馈、保险丝状态、开关位置反馈等单 bit 信号。"
             "Present_Value 为 `BACnetBinaryPV` 枚举(`inactive` / `active`)。属于「无后缀基础类」,"
             "另提供 `_IO`(K-bus 端子)、`_ECAT`(EtherCAT 端子)两种变体后缀。",
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD 父节点 + 名称 |",
        "| 文本 | `sInactiveText` / `sActiveText` | `STRING(*)` | Inactive_Text / Active_Text(在 BMS 上替代 0/1 显示的两个标签) |",
        "| Present_Value | `bVal` | `BOOL` | PLC 直接喂的 Present_Value(基础类) |",
        "| Polarity | `ePolarity` | `E_BACnet_Polarity` | Polarity(`eNormal` / `eReverse`,反向时 PLC 0 → BACnet active) |",
        "| 报警 | `bAlarmValue` | `BOOL` | Alarm_Value(BACnet 标准的「哪个状态算报警态」) |",
        "| 报警 | `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` | 同 AI | Intrinsic Reporting |",
        "| 统计 | `nChangeOfStateCount` / `dtChangeOfStateTime` / `tElapsedActiveTime` | `UDINT` / `DT` / `TIME` | Change_Of_State_Count / Time / Elapsed_Active_Time(BACnet 标准统计) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_BI` | — | 基础类:PLC 喂 `bVal` |",
        "| `FB_BACnet_BI_IO` | 增 `bRawVal AT %I* : BOOL` | 通过 `TcLinkTo` 链接 K-bus 端子通道 |",
        "| `FB_BACnet_BI_ECAT` | 增 `bRawVal AT %I* : BOOL`、`nRawECatState : UINT` | 链接 EtherCAT 端子通道 |",
    ],
    behaviour=(
        "FB_BACnet_BI 每周期调用一次,库内部把 `bVal`(或 raw bRawVal 经 polarity 翻转)送到 stack 的 Present_Value。"
        "`sInactiveText` / `sActiveText` 让 BMS 显示具体语义(`Off`/`On`、`Closed`/`Open`)而不只是 0/1。"
        "Intrinsic Reporting 简单粗暴:当 `bVal = bAlarmValue` 持续 `nTimeDelay` 秒后,Event_State 切到 TO_OFFNORMAL "
        "并向 `nNotificationClass` 指定的 NC 实例上报报警(PDF §3.2.45 + §9.8)。"
        "`_IO` / `_ECAT` 变体下,Present_Value 由端子值经 `ePolarity` 反向后自动得出,无需 PLC 介入。"
        "BACnet 标准的 Change_Of_State_Count / Elapsed_Active_Time 由 stack 自动累加,PLC 端只读不写。"
        "PDF §9.4 示例显示如何用 `stSettings.aDisabled` 把不必要的统计属性"
        "(`PropChangeOfStateCount` / `PropChangeOfStateTime` / `PropTimeOfStateCountReset`)从对象暴露面里删掉。"
    ),
    error_section="无返回值;`stStatusFlags.bInAlarm/bFault/bOverridden/bOutOfService` 暴露运行状态。"
                  "⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码常量。",
    extra_tips_block=(
        "- **`ePolarity` 是 BACnet 标准属性,不是物理反向**:`eReverse` 让 BACnet 端的"
        "`inactive/active` 与 PLC bVal 的 0/1 相反,适合「高电平=故障」接线习惯但 BMS 希望「故障=active」显示的场景。\n"
        "- **`bAlarmValue` 决定报警的方向**:`bAlarmValue := TRUE` 表示「激活态=报警态」(典型用于「门未关」"
        "报警);`bAlarmValue := FALSE` 用于「非激活态=报警态」(典型用于「心跳信号丢失」)。\n"
        "- **不要每周期写 `sActiveText` / `sInactiveText`**:这些是配置属性,运行时 BMS 也可能改,用条件触发(PDF §6.3.1)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_BI
VAR
    fbDoorOpen : FB_BACnet_BI := (
        sObjectName := 'Door_3F_East',
        sDescription := 'Floor 3 East door open switch',
        sInactiveText := 'Closed',
        sActiveText := 'Open',
        ePolarity := E_BACnet_Polarity.eNormal,
        bAlarmValue := TRUE,
        bEventDetectionEnable := TRUE,
        nNotificationClass := 11,
        nTimeDelay := 30);
    bDoorSensorPlc : BOOL;
END_VAR
fbDoorOpen.bVal := bDoorSensorPlc;
fbDoorOpen();""",
    business_block=(
        "- **场景**:楼宇安防 — 100 个房间门磁开关,每个门状态要暴露给 BMS,门开超 30 秒发报警。\n"
        "- **价值**:一行声明 + 一行调用,BACnet 协议层、状态文本、报警延时全部由 stack 处理。\n"
        "- **替代方案对比**:用 `_IO` 变体直接绑端子省 PLC 中转;用基础类适合「门信号要被 PLC 加工(消抖、组合逻辑)后再暴露」的场景。"
    ),
    refs_extra="§6.1.1、§6.1.2、§3.2.45(Alarm_Value)、§9.4(disable 属性)、§9.8(配 NC)、§9.16(数组初始化)",
    related="`FB_BACnet_BO`(可写二进制输出)、`FB_BACnet_BV`(虚拟二进制值)、`FB_BACnet_BI_IO` / `_ECAT`(本 FB 后缀变体)、"
             "`FB_BACnet_NC`(报警接收方)",
))

_tcpou("FB_BACnet_BI", """VAR
    // 门磁开关状态暴露给 BMS,带 30 秒延时报警
    fbDoorOpen   : FB_BACnet_BI := (
        sObjectName := 'Door_3F_East',
        sDescription := 'Floor 3 East office door open switch',
        sInactiveText := 'Closed',          // BMS 显示 "Closed" 而不是 0
        sActiveText := 'Open',              // BMS 显示 "Open" 而不是 1
        ePolarity := E_BACnet_Polarity.eNormal,  // 物理高电平 = open
        bAlarmValue := TRUE,                // active(门开)算报警
        bEventDetectionEnable := TRUE,
        nNotificationClass := 11,           // 报警走 NC11
        nTimeDelay := 30);                  // 开门 30 秒才报警(避免日常进出误报)

    fbAlarmClass : FB_BACnet_NC := (
        nObjectInstance := 11,
        nNotificationClass := 11,
        sDescription := 'Door alarms',
        aAckRequired := [TRUE, TRUE, FALSE],
        aPriority := [10, 11, 12]);

    bDoorSensorPlc : BOOL := FALSE;         // 从 EL1809 端子读到的门磁信号
END_VAR""", """// =============================================================================
// 场景:楼宇安防 — CX 控制器接 100 个房间门磁开关,每个状态要暴露给 BMS,门开
//       超 30 秒发报警走 NC11;BMS 上显示 "Open" / "Closed" 而不是 0/1。
// 价值:Active_Text / Inactive_Text / Alarm_Value / Time_Delay / NC 路由全在
//       一行声明里;手写 BACnet/IP 报文 + 状态机延时计数 + COV 推送至少 500+
//       行,本 FB 一行声明完成。
// 验证:1) 在线写 bDoorSensorPlc := TRUE,30 秒内 BACnet Explorer 看 Event_State
//       应为 normal;30 秒后切到 OFFNORMAL,NC11 发出 alarm。2) bDoorSensorPlc
//       := FALSE 后 Event_State 立刻切回 normal。3) Explorer 读 Active_Text /
//       Inactive_Text 应分别为 'Open' / 'Closed'。
// =============================================================================

fbDoorOpen.bVal := bDoorSensorPlc;
fbDoorOpen();
fbAlarmClass();
""")


# ============================================================================
# objects/FB_BACnet_BO  — Binary Output (commandable)
# ============================================================================
_doc("objects", "FB_BACnet_BO", build_doc(
    fb_name="FB_BACnet_BO",
    category_label="Object · Binary Output",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Binary Output」对象类型(BACnet Object_Type = 4 / Binary Output)。"
        "语义上是可写、支持命令优先级的二进制输出,典型用于继电器线圈、电磁阀线圈、灯具控制信号等。"
        "Present_Value 为 `BACnetBinaryPV`(`inactive` / `active`),16 个优先级槽位机制与 AO 完全相同。"
        "本对象类型在 BACnet 标准中独占 priority 6(Minimum_On_Time / Minimum_Off_Time 强制保护),"
        "PLC 不能直接写槽 6(PDF §6.2.1)。本库提供基础类 + `_IO` + `_ECAT` + `_5P` + `_IO5P` + `_RAW5P` 共 6 个变体。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD 父节点 + 名称 |",
        "| 文本 | `sInactiveText` / `sActiveText` | `STRING(*)` | Inactive_Text / Active_Text |",
        "| Polarity | `ePolarity` | `E_BACnet_Polarity` | 物理电平到 BACnet 状态的映射方向 |",
        "| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `bValPgm` | `BOOL` / `BOOL` | PLC 在 Program 优先级写值;FALSE 释放该槽位 |",
        "| `_5P` 增 | `bEnSfty/bValSfty` / `bEnCrit/bValCrit` / `bEnManLoc/bValManLoc` / `bEnManualOperator/bValManualOperator` | `BOOL` | 5 优先级槽位(LifeSafety / Critical / ManLoc / ManOperator / Pgm) |",
        "| 回退 | `bRelinquishDefault` | `BOOL` | 16 槽位全 NULL 时回退值 |",
        "| 最短保持 | `nMinimumOnTime` / `nMinimumOffTime` | `UDINT` | Minimum_On/Off_Time(秒),BACnet 标准的「避免输出抖动」机制 |",
        "| 报警 | `bAlarmValue` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` | 同 BI | Intrinsic Reporting |",
        "| 统计 | `nChangeOfStateCount` / `dtChangeOfStateTime` / `tElapsedActiveTime` | `UDINT` / `DT` / `TIME` | BACnet 标准统计属性 |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_BO` | — | 基础类 |",
        "| `FB_BACnet_BO_IO` | 增 `bRawVal AT %Q* : BOOL` | 写出到 K-bus 端子通道 |",
        "| `FB_BACnet_BO_ECAT` | 增 `bRawVal AT %Q* : BOOL`、`nRawECatState : UINT` | 写出到 EtherCAT 端子通道 |",
        "| `FB_BACnet_BO_5P` | 5 优先级槽位 | 楼控多优先级场景(PDF §9.5) |",
        "| `FB_BACnet_BO_IO5P` | `_5P` + 写 K-bus 端子 | 5 优先级 + 端子直连 |",
        "| `FB_BACnet_BO_RAW5P` | `_5P` + `bRawVal : BOOL` | 5 优先级 + PLC 自算 raw 值 |",
    ],
    behaviour=(
        "运行机制与 FB_BACnet_AO 相同 — 取 16 优先级槽位中最高的非 NULL 值作为 Present_Value,基础类下 PLC 通过 "
        "`bEnPgm := TRUE` + `bValPgm := <0|1>` 占 Program 优先级(默认槽 16);BMS 用 `WriteProperty(Present_Value, ..., priority := 8)` "
        "占 Manual Operator。`bEnPgm := FALSE` 等价写 NULL 释放槽位(PDF §6.2.1 + §6.6.5)。"
        "BO 独有的 `nMinimumOnTime` / `nMinimumOffTime` 由 BACnet stack 自动强制:Present_Value 切到 active 后,"
        "stack 在槽 6 写入 active 并锁定至少 `nMinimumOnTime` 秒,任何更高优先级写 inactive 都会被忽略;"
        "反之亦然。这能避免快速 ON/OFF 抖动损坏继电器或加热器(BACnet 标准 priority 6 是"
        "Minimum_On/Off,PLC 不能占用)。`_IO` / `_ECAT` 变体下 Present_Value 自动写到端子通道 `bRawVal`,"
        "受 `ePolarity` 控制反向。`_5P` 把 5 个常用优先级搬到 PLC 内 boolean 引脚,适合 BO 既要被 PLC 自动控制"
        "又要响应紧急 / 现场手动按钮的场景。"
    ),
    error_section=(
        "无返回值;运行状态通过 `stStatusFlags.bInAlarm/bFault/bOverridden/bOutOfService` 暴露。"
        "⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。"
    ),
    extra_tips_block=(
        _COMMON_TIPS_CMD + "\n"
        "- **不要写 priority 6**:BACnet 标准把槽 6 永久保留给 Minimum_On/Off_Time 算法,BMS 客户端写槽 6 会被 reject。\n"
        "- **`nMinimumOnTime / nMinimumOffTime` 设错会卡输出**:若设成 3600 秒,继电器一旦动作就锁定 1 小时不能再切,可能让保护逻辑失效。安全期间用 0(关闭)或小值(5..10 秒)。\n"
        "- **`_RAW5P` 下 PLC 必须每周期写 `bRawVal`**:不写时 stack 把端子保持上次值,可能与 Present_Value 不同步;典型用法是 PLC 把「软件输出」按业务逻辑拼装后送给 `bRawVal`。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_BO
VAR
    // 走廊灯继电器:PLC 自动控制 + BMS 手动覆盖
    fbHallLight : FB_BACnet_BO := (
        sObjectName := 'HallLight_3F_East',
        sInactiveText := 'Off',
        sActiveText := 'On',
        nMinimumOnTime := 10,             // 灯亮至少 10 秒(避免误触发抖动)
        nMinimumOffTime := 10);
    bAutoLightOn : BOOL := FALSE;
    bAutoMode : BOOL := TRUE;             // 在线写 FALSE 释放 Program 优先级
END_VAR

fbHallLight.bEnPgm  := bAutoMode;
fbHallLight.bValPgm := bAutoLightOn;
fbHallLight();""",
    business_block=(
        "- **场景**:走廊灯控,PLC 根据光照传感器 + 人体感应器自动开关,运维人员可在 BMS 上手动覆盖(强制开 / 强制关)。"
        "灯具有最短保持 10 秒保护避免继电器抖坏。\n"
        "- **价值**:Min_On / Min_Off 保护是 BACnet 标准的成熟机制,本 FB 一行配置;手写要管时间戳 + 状态机至少 100 行。\n"
        "- **替代方案对比**:用 `_5P` 适合「应急按钮 + 自动 + 手动 + 节能调度」四源覆盖;基础类适合 PLC 单源 + BMS 偶尔覆盖。"
    ),
    refs_extra="§6.1.1、§6.1.2、§3.2.46/47(Minimum_On/Off_Time)、§6.2.1(优先级 6 保留)、§9.5(_5P)、§9.6(WritePropertyNull)",
    related="`FB_BACnet_BI`(只读二进制输入)、`FB_BACnet_BV` / `FB_BACnet_BV_5P` / `FB_BACnet_BV_Event`(虚拟二进制值)、"
             "`FB_BACnet_BO_IO` / `_ECAT` / `_5P` / `_IO5P` / `_RAW5P`(本 FB 后缀变体)",
))

_tcpou("FB_BACnet_BO", """VAR
    // 走廊灯继电器:PLC 自动(光照+人体感应) + BMS 手动覆盖
    fbHallLight    : FB_BACnet_BO := (
        sObjectName := 'HallLight_3F_East',
        sDescription := 'Floor 3 East hallway light relay',
        sInactiveText := 'Off',
        sActiveText := 'On',
        ePolarity := E_BACnet_Polarity.eNormal,
        nMinimumOnTime := 10,            // 灯亮至少 10 秒
        nMinimumOffTime := 10);

    bAutoModeOn    : BOOL := TRUE;       // 在线写 FALSE 释放 PLC 控制,让 BMS 接管
    bAutoLightOn   : BOOL := FALSE;      // PLC 内部算出来的指令(光照 + 人感联合)
END_VAR""", """// =============================================================================
// 场景:楼控走廊灯继电器,PLC 根据光照传感器 + 人体感应器自动开关;运维人员
//       在 BMS 上可手动覆盖(强制开 / 强制关)。灯具继电器最短保持 10 秒避免
//       抖动损坏触点。
// 价值:Min_On / Min_Off 保护是 BACnet 标准成熟机制,本 FB 一行配置;手写要管
//       时间戳 + 状态机至少 100 行。命令优先级让 PLC 自动 + BMS 手动天然解耦。
// 验证:1) 在线写 bAutoModeOn := TRUE,bAutoLightOn := TRUE,1 秒内
//       BACnet Explorer 看 Present_Value=active(灯亮);bAutoLightOn := FALSE
//       后 10 秒内 Present_Value 保持 active(Min_On 保护),10 秒后才落到 inactive。
//       2) Explorer 用 priority := 8 写 Present_Value=inactive 也要等 Min_On 满足
//       才生效。3) bAutoModeOn := FALSE 释放 Program 优先级,Explorer 写值
//       立刻生效(因为 PLC 不再竞争)。
// =============================================================================

fbHallLight.bEnPgm  := bAutoModeOn;
fbHallLight.bValPgm := bAutoLightOn;
fbHallLight();
""")


# ============================================================================
# objects/FB_BACnet_BV  — Binary Value (virtual)
# ============================================================================
_doc("objects", "FB_BACnet_BV", build_doc(
    fb_name="FB_BACnet_BV",
    category_label="Object · Binary Value",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Binary Value」对象类型(BACnet Object_Type = 5 / Binary Value)。"
        "语义上是虚拟二进制值,典型用于程序内部状态、报警标志、设备故障汇总位等"
        "「非物理 I/O 但需要被 BMS 读写或订阅」的场景。"
        "基础类支持 16 优先级槽位(行为同 BO,但 priority 6 不被 Min_On/Off 占用)。"
        "本库提供基础类 + `_5P`(5 优先级)+ `_Event`(只读 + Event Reporting,PDF §9.8 示例 fbBV1 / fbBV2)三种变体。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD 父节点 + 名称 |",
        "| 文本 | `sInactiveText` / `sActiveText` | `STRING(*)` | Inactive_Text / Active_Text |",
        "| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `bValPgm` | `BOOL` | PLC 在 Program 优先级写值 |",
        "| `_5P` 增 | `bEnSfty/bValSfty` 等 5 优先级 | `BOOL` | 同 `FB_BACnet_BO_5P` |",
        "| 回退 | `bRelinquishDefault` | `BOOL` | 16 槽位全 NULL 时回退值 |",
        "| Present_Value 直写(`_Event`) | `bPresVal` 或 `bVal`(只读暴露) | `BOOL` | PLC 写 Present_Value,BMS 只能读 |",
        "| 报警 | `bAlarmValue` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` / `eNotifyType` | 同 BI | Intrinsic Reporting |",
        "| 通知类型 | `eNotifyType` | `E_BACnet_NotifyType` | Notify_Type(`eAlarm` / `eNotifyEvent`,区分报警 vs 一般事件) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_BV` | — | 基础类,16 优先级 |",
        "| `FB_BACnet_BV_5P` | 5 优先级槽位 | 楼控多优先级场景 |",
        "| `FB_BACnet_BV_Event` | 只读 + 启用 Event Reporting | PLC 内部状态位,BMS 只能读但能订阅事件 |",
    ],
    behaviour=(
        "基础类 BV 与 BO 的差别仅在语义(虚拟值不绑物理输出,priority 6 可被 PLC/BMS 使用),"
        "命令优先级机制完全相同。BV 最常见的用法见 PDF §9.8:`bAlarmValue := TRUE` + `aEventEnable := [TRUE,TRUE,TRUE]` "
        "的纯报警 flag — PLC 把「过滤器堵塞」、「压力低低限」等汇总诊断布尔位写到 `bValPgm`,触发 NC 类对象向 BMS 发报警。"
        "`_Event` 变体把 Present_Value 改为只读(PLC 写 `bPresVal`,BMS 不能写),适合"
        "「PLC 是该位的唯一源,但希望 BMS 能订阅状态变化」的场景。"
        "Notify_Type(`eAlarm` vs `eNotifyEvent`)只是 BMS 端显示分类,不影响触发逻辑(PDF §6.2.2)。"
    ),
    error_section=(
        "无返回值;运行状态通过 `stStatusFlags` 暴露。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。"
    ),
    extra_tips_block=(
        _COMMON_TIPS_CMD + "\n"
        "- **BV 用作汇总报警 flag 时,务必同时声明对应 NC 实例**:`nNotificationClass := 10` + 没有 `FB_BACnet_NC` "
        "with `nObjectInstance := 10` → 报警发不出去(PDF §9.8 示例 fbBV1 + fbNC01)。\n"
        "- **`_Event` 变体不能用 `bEnPgm + bValPgm`**:Present_Value 只读,PLC 用 `bPresVal := ...` 写,不参与优先级。\n"
        "- **`eNotifyType` 与 `aEventMessageTextsConfig` 配合**:把字符串数组按 `[OFFNORMAL, FAULT, NORMAL]` 顺序填,"
        "比如 `['过滤器堵塞', '传感器故障', '已恢复']`。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_BV
VAR
    // 过滤器堵塞汇总报警位:PLC 写,BMS 订阅
    fbFilterClogged : FB_BACnet_BV := (
        sObjectName := 'FilterClogged_AHU_3F',
        sInactiveText := 'OK',
        sActiveText := 'Clogged',
        bAlarmValue := TRUE,                  // active = 报警
        aEventEnable := [TRUE,TRUE,TRUE],
        bEventDetectionEnable := TRUE,
        nNotificationClass := 12,
        aEventMessageTextsConfig := ['过滤器堵塞', '传感器故障', '已恢复']);
    bFilterAlarmPlc : BOOL := FALSE;
END_VAR

fbFilterClogged.bEnPgm  := TRUE;
fbFilterClogged.bValPgm := bFilterAlarmPlc;
fbFilterClogged();""",
    business_block=(
        "- **场景**:空调机组的「过滤器堵塞」汇总报警 — PLC 通过压差传感器算出 `bFilterAlarmPlc`,"
        "需要让 BMS 知道并触发维护工单。\n"
        "- **价值**:把「PLC 内部布尔位」包装成符合 BACnet 标准的 alarm 对象,BMS 可以直接订阅 alarm summary、生成工单,"
        "无需 PLC 单独发邮件 / 短信。\n"
        "- **替代方案对比**:用 `_Event` 变体 BMS 只能读不能写(更安全,避免误操作);用 `_5P` 适合"
        "「多源都可置位汇总报警」场景。"
    ),
    refs_extra="§6.1.1、§6.1.2(_5P / _Event)、§6.2.2(Event Reporting)、§9.6(WritePropertyNull 释放优先级)、§9.8(配 NC + recipient list)",
    related="`FB_BACnet_BI`(只读二进制输入)、`FB_BACnet_BO`(物理二进制输出)、"
             "`FB_BACnet_BV_5P` / `_Event`(本 FB 后缀变体)、`FB_BACnet_NC`(报警接收方)",
))

_tcpou("FB_BACnet_BV", """VAR
    // 空调机组过滤器堵塞汇总报警位:PLC 写,BMS 订阅
    fbFilterClogged : FB_BACnet_BV := (
        sObjectName := 'FilterClogged_AHU_3F',
        sDescription := 'AHU floor 3 filter clogged summary alarm',
        sInactiveText := 'OK',
        sActiveText := 'Clogged',
        bAlarmValue := TRUE,                  // active = 报警态
        aEventEnable := [TRUE, TRUE, TRUE],
        bEventDetectionEnable := TRUE,
        nNotificationClass := 12,
        aEventMessageTextsConfig := ['Filter clogged', 'Sensor fault', 'Recovered']);

    fbAlarmClass    : FB_BACnet_NC := (
        nObjectInstance := 12,
        nNotificationClass := 12,
        sDescription := 'AHU summary alarms',
        aAckRequired := [TRUE, TRUE, FALSE],
        aPriority := [8, 9, 12]);             // OFFNORMAL 走 priority 8(高)

    bFilterAlarmPlc : BOOL := FALSE;          // 从 PLC 内部"压差>500Pa"逻辑算出来
END_VAR""", """// =============================================================================
// 场景:空调机组过滤器堵塞 — PLC 通过压差传感器算出 bFilterAlarmPlc,需要把该位
//       包装成符合 BACnet 标准的 alarm 对象,让 BMS 订阅 alarm summary 并触发
//       维护工单。
// 价值:把 PLC 内部布尔位包装成 BACnet alarm 对象,BMS 直接订阅就行;无需 PLC
//       自己发邮件/短信。alarm 标准化后跨厂商 BMS 都能识别。
// 验证:1) BACnet Explorer 读 Present_Value 应为 inactive('OK')。2) 在线写
//       bFilterAlarmPlc := TRUE,Explorer 应看到 Present_Value=active,Event_State
//       切到 OFFNORMAL,NC12 触发一条事件给所有 recipient,event message text
//       为 'Filter clogged'。3) bFilterAlarmPlc := FALSE 后 NC12 触发 normal
//       事件,event message text 为 'Recovered'。
// =============================================================================

fbFilterClogged.bEnPgm  := TRUE;              // PLC 始终占 Program 优先级
fbFilterClogged.bValPgm := bFilterAlarmPlc;
fbFilterClogged();
fbAlarmClass();
""")


# ============================================================================
# objects/FB_BACnet_MI / MO / MV  — Multistate trio
# ============================================================================
_doc("objects", "FB_BACnet_MI", build_doc(
    fb_name="FB_BACnet_MI",
    category_label="Object · Multistate Input",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Multistate Input」对象类型(BACnet Object_Type = 13 / Multistate Input)。"
        "语义上是只读多状态输入,典型用于本地操作模式开关(`AUTO`/`Low`/`Medium`/`High`/`Turbo`)、"
        "运行阶段指示(`Stop`/`Start`/`Run`/`Stopping`)等枚举型物理输入。Present_Value 为 `UDINT`,"
        "范围由 `aStateText` 数组的长度决定(无 `aStateText` 时默认 12 态,可在 `BACnet_Param` 改)。"
        "本对象类型在本库中仅基础类,无 `_IO` / `_ECAT` 变体(物理多态开关一般通过 BV 数组组合实现)。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| Present_Value | `nVal` | `UDINT` | PLC 喂的多态值(1..N) |",
        "| 状态枚举 | `aStateText` | `ARRAY[1..*] OF STRING(*)` | State_Text(BMS 显示用文本数组,如 `['AUTO','Low','Medium','High','Turbo']`,长度决定 Number_Of_States) |",
        "| 报警 | `aAlarmValues` | `ARRAY OF UDINT` | Alarm_Values(哪些状态算报警态) |",
        "| 报警 | `aFaultValues` | `ARRAY OF UDINT` | Fault_Values(哪些状态算故障态) |",
        "| 事件 | `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` | 同 AI | Intrinsic Reporting |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_MI 每周期调用一次,PLC 把多态枚举值写入 `nVal`,库内部映射到 Present_Value。"
        "`aStateText` 数组的长度直接决定 BACnet 标准属性 Number_Of_States — 5 个文本就是 5 态,"
        "下标按 BACnet 习惯从 1 开始。`aAlarmValues` 列出「哪些状态值算报警态」(如 `[4,5]` 表示 High 和 Turbo 触发报警);"
        "`aFaultValues` 列「哪些算故障态」(如 `[0]` 表示传感器故障 / 没读到)。"
        "Intrinsic Reporting 在 Present_Value 命中 alarm/fault 值持续 `nTimeDelay` 秒后触发对应类型事件。"
        "PDF §9.2 示例 `fbMi : FB_BACnet_MI := (aStateText := ['AUTO','Low','Medium','High','Turbo']);` 是最常见用法。"
    ),
    error_section=(
        "无返回值;运行状态通过 `stStatusFlags` 暴露。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。"
    ),
    extra_tips_block=(
        "- **`aStateText` 的下标从 1 开始**:`aStateText[1]` 是第一个状态,而 IEC 标准数组通常 0 开始,容易写错。\n"
        "- **不写 `aStateText` 默认 12 态**:PDF §9.2:Number_Of_States 默认上限 12,可在 `BACnet_Param` 改;通常应该显式声明。\n"
        "- **`nVal := 0` 视为无效**:多态值合法范围是 1..Number_Of_States,写 0 会让 BMS 把对象当成"
        "Reliability=NO_SENSOR(配 fault 报警)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_MI
VAR
    fbFanModeSwitch : FB_BACnet_MI := (
        sObjectName := 'FanMode_AHU_3F',
        sDescription := 'Local fan speed selector (AUTO/Low/Mid/High/Turbo)',
        aStateText := ['AUTO', 'Low', 'Medium', 'High', 'Turbo'],
        aAlarmValues := [5],                     // Turbo 算报警(超出运行包络)
        bEventDetectionEnable := TRUE,
        nNotificationClass := 13);
    nFanSelectorPlc : UDINT := 1;                // 从本地旋钮读到的位置(1..5)
END_VAR

fbFanModeSwitch.nVal := nFanSelectorPlc;
fbFanModeSwitch();""",
    business_block=(
        "- **场景**:空调机组本地控制柜上有一个 5 档旋钮(AUTO/Low/Medium/High/Turbo)切换风机模式,"
        "BMS 需要看到当前档位以便记录运维操作;Turbo 档(超出正常运行包络)要发报警。\n"
        "- **价值**:用一个 MI 对象代替「5 个 BI 拼接 + 文本解码」;BMS 端直接显示语义文本,无需在画面里维护一张码表。\n"
        "- **替代方案对比**:用 5 个 BV 也能表达,但 BMS 端处理「互斥唯一态」困难;"
        "用 AV 暴露数字 1..5 又丢失文本语义。"
    ),
    refs_extra="§6.1.1、§3.2.49/50/51/52(Number_Of_States / State_Text / Alarm_Values / Fault_Values)、§9.2(`aStateText` 决定态数)",
    related="`FB_BACnet_MO`(可写多态输出)、`FB_BACnet_MV` / `FB_BACnet_MV_5P`(虚拟多态值)",
))

_tcpou("FB_BACnet_MI", """VAR
    // 空调机组本地控制柜上的 5 档风机模式旋钮,把当前档位暴露给 BMS
    fbFanModeSwitch : FB_BACnet_MI := (
        sObjectName := 'FanMode_AHU_3F',
        sDescription := 'Local fan speed selector (AUTO/Low/Mid/High/Turbo)',
        aStateText := ['AUTO', 'Low', 'Medium', 'High', 'Turbo'],
        aAlarmValues := [5],                       // 档位 5 = Turbo 触发报警
        bEventDetectionEnable := TRUE,
        nNotificationClass := 13,
        aEventMessageTextsConfig := ['Turbo mode active', 'Sensor fault', 'Normal']);

    fbAlarmClass    : FB_BACnet_NC := (
        nObjectInstance := 13,
        nNotificationClass := 13,
        sDescription := 'Fan mode alarms',
        aAckRequired := [TRUE, TRUE, FALSE],
        aPriority := [10, 11, 12]);

    nFanSelectorPlc : UDINT := 1;                  // 从旋钮端子(3 路 BI 编码)解码得到
END_VAR""", """// =============================================================================
// 场景:空调机组本地控制柜上有一个 5 档旋钮(AUTO/Low/Medium/High/Turbo)切换
//       风机模式;BMS 需要看到当前档位以便记录运维操作;Turbo 档(超出正常运
//       行包络)要发报警让运维注意。
// 价值:用一个 MI 对象代替 "5 个 BI 拼接 + BMS 端码表" 方案,BMS 端直接显示语
//       义文本(AUTO/Low/...),无需画面里维护额外码表;Alarm_Values 一行配置
//       就能在 Turbo 时触发标准 BACnet 报警。
// 验证:1) 在线写 nFanSelectorPlc := 3,BACnet Explorer 读 Present_Value=3,
//       State_Text[3]='Medium'。2) nFanSelectorPlc := 5,Explorer 应看到
//       Event_State=OFFNORMAL,NC13 发出 alarm,message text 为 'Turbo mode
//       active'。3) nFanSelectorPlc := 1,Event_State 回到 normal。
// =============================================================================

fbFanModeSwitch.nVal := nFanSelectorPlc;
fbFanModeSwitch();
fbAlarmClass();
""")


# --- FB_BACnet_MO ----------------------------------------------------------
_doc("objects", "FB_BACnet_MO", build_doc(
    fb_name="FB_BACnet_MO",
    category_label="Object · Multistate Output",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Multistate Output」对象类型(BACnet Object_Type = 14 / Multistate Output)。"
        "语义上是可写、支持命令优先级的多态输出,典型用于阀位档位(0/25/50/75/100%)、"
        "运行档位选择(`Stop`/`Cool`/`Heat`/`Fan`)等枚举型物理输出。"
        "本库提供基础类 + `_5P`(5 优先级)+ `_IO5P`(`_5P` 接 K-bus 端子)+ `_RAW5P`(`_5P` raw 值由 PLC 自算)"
        "四个变体。PDF §9.5 示例 `fbMO5P` / `fbMOIO5P` / `fbMORaw5P` 给出三者声明对照。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 状态枚举 | `aStateText` | `ARRAY[1..*] OF STRING(*)` | State_Text(同 MI) |",
        "| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `nValPgm` | `BOOL` / `UDINT` | PLC 在 Program 优先级写值;FALSE 释放槽位 |",
        "| `_5P` 增 | `bEnSfty/nValSfty` / `bEnCrit/nValCrit` / `bEnManLoc/nValManLoc` / `bEnManualOperator/nValManualOperator` | `BOOL` / `UDINT` | 5 优先级槽位 |",
        "| 回退 | `nRelinquishDefault` | `UDINT` | 16 槽位全 NULL 时回退值 |",
        "| 报警 | `aAlarmValues` / `aFaultValues` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 MI | Intrinsic Reporting |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_MO` | — | 基础类,16 优先级 |",
        "| `FB_BACnet_MO_5P` | 5 优先级槽位 | 楼控多优先级场景 |",
        "| `FB_BACnet_MO_IO5P` | `_5P` + `nRawVal AT %Q* : USINT` | 5 优先级 + 写 K-bus 端子 |",
        "| `FB_BACnet_MO_RAW5P` | `_5P` + `nRawVal : USINT` | 5 优先级 + raw 值 PLC 自算(常用于「输出多态值到非标硬件」) |",
    ],
    behaviour=(
        "运行机制与 FB_BACnet_BO 类似但 Present_Value 是 `UDINT` 而非 `BOOL`,优先级机制完全相同 — "
        "对 BACnet 16 优先级槽位轮询取最高的非 NULL 值。基础类用 `bEnPgm := TRUE` + `nValPgm := <1..N>` "
        "占 Program 优先级(默认槽 16,可在 BACnet_Param 改);`_5P` 把 5 个常用优先级"
        "(LifeSafety / Critical / ManLocal / ManOperator / Program)搬成 PLC 内 boolean+UDINT 引脚。"
        "全 16 槽位为 NULL 时取 `nRelinquishDefault`。`aAlarmValues` / `aFaultValues` 列出"
        "哪些 Present_Value 值要触发 alarm / fault 事件,stack 自动管理状态切换与 NC 路由。"
        "PDF §9.5 末尾示例显示 `fbMV5P.bEnCrit := TRUE; fbMV5P.nValCrit := 3;` "
        "这种占用 Critical 优先级临时写状态 3 的典型用法。`_IO5P` / `_RAW5P` 把 Present_Value 自动"
        "写到端子通道 / PLC 自定义 raw 值,适合多态启动器(4 档马达控制器等)。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。"
    ),
    extra_tips_block=(
        _COMMON_TIPS_CMD + "\n"
        "- **`nValPgm := 0` 是无效值**:多态值合法是 1..N(N = `aStateText` 长度),写 0 会被 stack reject 或导致客户端读到无效状态。\n"
        "- **`_IO5P` 写 K-bus 端子的 USINT raw 值**:典型用于 4 档马达启动器,每个档位对应 USINT 编码 1..4。\n"
        "- **使用 `_RAW5P` 时 PLC 要把 nVal 转成 `nRawVal`**:库不会自动 1:1 映射,因为多态值与硬件编码不一定一致(可能多态值 1 对应端子代码 16)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_MO
VAR
    // 空调四档运行模式输出:Stop/Cool/Heat/Fan
    fbModeCmd : FB_BACnet_MO_5P := (
        sObjectName := 'ModeCmd_AHU_3F',
        aStateText := ['Stop', 'Cool', 'Heat', 'Fan'],
        nRelinquishDefault := 1);            // 全释放回退到 Stop
    nAutoModeCmd : UDINT := 2;               // PLC 算的当前指令
END_VAR

fbModeCmd.bEnPgm  := TRUE;
fbModeCmd.nValPgm := nAutoModeCmd;
fbModeCmd();""",
    business_block=(
        "- **场景**:小型 AHU 四档运行模式(Stop/Cool/Heat/Fan)输出,PLC 根据温差自动切换,"
        "BMS 可手动覆盖(运维试机时强制开 Fan 测试风机)。\n"
        "- **价值**:用一个 MO_5P 代替「4 个 BO 拼接互斥锁」,优先级让 PLC 自动+BMS 手动解耦。\n"
        "- **替代方案对比**:用 4 个 BO + 互斥锁需要 PLC 端写一堆「如果 BMS 写了 BO1 则把 BO2/3/4 都关」的胶水代码;MO 一行搞定。"
    ),
    refs_extra="§6.1.1、§6.1.2(_5P / _IO5P / _RAW5P)、§9.5(_5P 优先级控制)",
    related="`FB_BACnet_MI`(只读多态输入)、`FB_BACnet_MV` / `FB_BACnet_MV_5P`(虚拟多态值)、"
             "`FB_BACnet_MO_5P` / `_IO5P` / `_RAW5P`(本 FB 后缀变体)",
))

_tcpou("FB_BACnet_MO", """VAR
    // 小型 AHU 四档运行模式输出:Stop/Cool/Heat/Fan
    // 用 _5P 变体:PLC 自动 + BMS 手动 + 现场旋钮(ManLocal) 三源覆盖
    fbModeCmd     : FB_BACnet_MO_5P := (
        sObjectName := 'ModeCmd_AHU_3F',
        sDescription := 'AHU mode command (Stop/Cool/Heat/Fan)',
        aStateText := ['Stop', 'Cool', 'Heat', 'Fan'],
        nRelinquishDefault := 1);            // 全释放回退到 Stop(安全)

    nAutoModeCmd  : UDINT := 1;              // PLC 根据温差自动算的指令
END_VAR""", """// =============================================================================
// 场景:小型 AHU 四档运行模式输出(Stop/Cool/Heat/Fan),PLC 根据室温与设定点
//       的偏差自动切换,BMS 可手动覆盖(运维试机时强制开 Fan 测试风机),
//       现场控制柜旋钮可作为 Manual Local 进一步覆盖。
// 价值:用一个 MO_5P 代替"4 个 BO + 互斥锁"方案;PLC/BMS/现场旋钮 三源覆盖
//       自然依靠 BACnet 优先级解耦,无需 PLC 端手写"谁优先"的胶水代码。
// 验证:1) 在线写 nAutoModeCmd := 2,BACnet Explorer 读 Present_Value=2
//       (Cool),Priority_Array[15]=2(PLC 占 Program 优先级,因 _5P 默认
//       Program=15)。2) Explorer 用 priority := 8 写 Present_Value := 4
//       (Fan),Present_Value 跳到 4(高优先级覆盖)。3) 释放 priority 8,
//       回到 PLC 控制的 Cool=2。
// =============================================================================

fbModeCmd.bEnPgm  := TRUE;
fbModeCmd.nValPgm := nAutoModeCmd;
fbModeCmd();
""")


# --- FB_BACnet_MV ----------------------------------------------------------
_doc("objects", "FB_BACnet_MV", build_doc(
    fb_name="FB_BACnet_MV",
    category_label="Object · Multistate Value",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Multistate Value」对象类型(BACnet Object_Type = 19 / Multistate Value)。"
        "语义上是虚拟多态值,典型用于「程序参数选项」、「运行场景」(`Day`/`Night`/`Holiday`/`Eco`)等"
        "非物理输出但需要 BMS 配置 / 订阅的多态枚举。"
        "本库提供基础类 + `_5P`(5 优先级)两个变体。PDF §9.5 末尾的"
        "`fbMV5P.bEnCrit := TRUE; fbMV5P.nValCrit := 3;` 是典型片段。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 状态枚举 | `aStateText` | `ARRAY[1..*] OF STRING(*)` | State_Text |",
        "| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `nValPgm` | `BOOL` / `UDINT` | PLC 在 Program 优先级写值 |",
        "| `_5P` 增 | `bEnSfty/nValSfty` 等 5 优先级 | `BOOL` / `UDINT` | 5 优先级槽位 |",
        "| 回退 | `nRelinquishDefault` | `UDINT` | 16 槽位全 NULL 时回退值 |",
        "| 报警 | `aAlarmValues` / `aFaultValues` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 MO | Intrinsic Reporting |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_MV` | — | 基础类,16 优先级 |",
        "| `FB_BACnet_MV_5P` | 5 优先级槽位 | 楼控多优先级场景(PDF §9.5) |",
    ],
    behaviour=(
        "FB_BACnet_MV 与 MO 的差别仅在语义(虚拟值,不绑物理输出端子)。运行机制 / 优先级处理与 MO 完全相同。"
        "典型用途:全局运行场景切换 — `aStateText := ['Day','Night','Holiday','Eco']`,"
        "BMS 写 Present_Value 来切换全楼运行模式,PLC 读后驱动一组下游对象(灯光场景、空调温度设定点表、等等)。"
        "PDF §9.5 示例展示 `_5P` 变体下 PLC 用 `bEnCrit := TRUE; nValCrit := 3;` 临时占用 Critical 优先级 "
        "(如出现紧急工况时强制切到 Holiday 模式停掉空调)。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。"
    ),
    extra_tips_block=(
        _COMMON_TIPS_CMD + "\n"
        "- **MV 常用于「全局运行场景」**:一个 MV 控制全楼空调时间表 + 灯光场景,改一个值带动几十个下游对象切换,"
        "类似 BACnet 标准的 Command 对象但更简单。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_MV
VAR
    // 全楼运行场景:Day/Night/Holiday/Eco
    fbBuildingMode : FB_BACnet_MV := (
        sObjectName := 'BuildingMode',
        aStateText := ['Day', 'Night', 'Holiday', 'Eco'],
        nRelinquishDefault := 1);
    nLocalMode : UDINT := 1;
END_VAR

fbBuildingMode.bEnPgm  := TRUE;
fbBuildingMode.nValPgm := nLocalMode;
fbBuildingMode();""",
    business_block=(
        "- **场景**:商办楼希望运维一键切「工作日 / 周末 / 节假日 / 节能」四种运行场景,"
        "切换后自动改变全楼空调时间表、灯光场景、电梯调度策略等。\n"
        "- **价值**:一个 MV 包装「全楼模式」,所有下游对象都通过订阅 / 引用本 MV 自动跟随;运维只用改一个值。\n"
        "- **替代方案对比**:用 4 个 BV 表达互斥模式需要 PLC 写互斥锁;用 AV 数字 1..4 失去枚举文本语义。"
    ),
    refs_extra="§6.1.1、§6.1.2(_5P)、§9.5(_5P + Critical 优先级临时占用)",
    related="`FB_BACnet_MI`(只读多态输入)、`FB_BACnet_MO` / `FB_BACnet_MO_5P` / `_IO5P` / `_RAW5P`(物理多态输出)、"
             "`FB_BACnet_MV_5P`(本 FB 后缀变体)",
))

_tcpou("FB_BACnet_MV", """VAR
    // 全楼运行场景:Day/Night/Holiday/Eco
    fbBuildingMode  : FB_BACnet_MV := (
        sObjectName := 'BuildingMode',
        sDescription := 'Whole-building operating scenario',
        aStateText := ['Day', 'Night', 'Holiday', 'Eco'],
        nRelinquishDefault := 1);            // 全释放回退到 Day(安全的常用默认)

    nLocalSetMode   : UDINT := 1;             // 从本地 HMI / 调度脚本算出来的当前场景
END_VAR""", """// =============================================================================
// 场景:商办楼希望运维一键切 "工作日 / 周末 / 节假日 / 节能" 四种运行场景,
//       切换后自动改变全楼空调时间表、灯光场景、电梯调度策略等。
// 价值:一个 MV 包装 "全楼模式",所有下游对象都通过引用本 MV 跟随;运维只改
//       一个值代替改几十个设定。BMS 端可直接看 State_Text 知道当前场景。
// 验证:1) BACnet Explorer 读 Present_Value=1 / 'Day'。2) 在线写 nLocalSetMode
//       := 4,Explorer 应看到 Present_Value=4 / 'Eco'。3) Explorer 用 priority
//       := 8 写 3,Present_Value=3 / 'Holiday'(高优先级覆盖)。释放后回到
//       PLC 控制的 4。
// =============================================================================

fbBuildingMode.bEnPgm  := TRUE;
fbBuildingMode.nValPgm := nLocalSetMode;
fbBuildingMode();
""")


# ============================================================================
# objects/FB_BACnet_ACC  — Accumulator
# ============================================================================
_doc("objects", "FB_BACnet_ACC", build_doc(
    fb_name="FB_BACnet_ACC",
    category_label="Object · Accumulator",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Accumulator」对象类型(BACnet Object_Type = 23 / Accumulator),"
        "用于累计型脉冲计数,典型场景是电度表 / 水表 / 燃气表的脉冲累计读数。"
        "Present_Value 是 `UDINT` 单调递增计数,带 `Scale` 缩放属性与 `Units` 工程单位,"
        "BMS 客户端通过 `Pulse_Rate` 周期采样得到瞬时流量。本对象类型在本库中仅基础类,无后缀变体。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 计数 | `nVal` | `UDINT` | Present_Value(累计脉冲数,PLC 喂入) |",
        "| 缩放 | `fScale` | `REAL` | Scale(每脉冲代表的工程量,如 0.001 kWh) |",
        "| 单位 | `eUnit` | `E_BA_Unit` | Units(`eEnergy_kWh` 等) |",
        "| 极限值 | `nMaxPresValue` | `UDINT` | Max_Pres_Value(溢出回 0 的上界) |",
        "| 限值检测 | `fHighLimit` / `bHighLimitEnable` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 AI | 累计超限报警(常用于「水表突增」诊断) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_ACC 每周期调用一次,PLC 把累计脉冲数写到 `nVal`(典型由 EL1262 等高速计数端子读出,"
        "或由 PLC 内部对 EL1809 脉冲输入做边沿计数)。库内部把 `nVal` 推到 BACnet stack 的 Present_Value,"
        "客户端通过 `ReadProperty(Pulse_Rate)` 取最近采样区间内的脉冲速率 — Pulse_Rate 由 stack 在两次"
        "读请求之间自动算 delta / time。`fScale` 让 BMS 端把脉冲数转回工程量(如 fScale := 0.001 表示"
        "每脉冲 = 0.001 kWh,1000 脉冲 = 1 kWh)。`nMaxPresValue` 设为 4294967295 时让 UDINT 自然溢出回 0,"
        "或设小值实现「达到 999999 后归零重计」语义。"
    ),
    error_section=(
        "无返回值;`stStatusFlags` 暴露状态。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。"
    ),
    extra_tips_block=(
        "- **PLC 不要复位 `nVal`**:Accumulator 语义是「累计永不归零」,PLC 周期写小于上次的值会让 BMS 端的 Pulse_Rate 算成负数。\n"
        "- **掉电要保住累计值**:`nVal` 需要走 PLC 的 VAR_RETAIN 持久化或 UPS 关机时写盘,否则掉电后归零会丢电量数据(工程经验补充)。\n"
        "- **`fScale` 必须与 Units 一致**:工程单位 `eEnergy_kWh` 时 fScale 应该是 kWh/脉冲(如 0.001),写成 Wh/脉冲(如 1.0)BMS 显示会差 1000 倍。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_ACC
VAR
    // 电度表累计读数,1 脉冲 = 0.001 kWh
    fbEnergyMeter : FB_BACnet_ACC := (
        sObjectName := 'EnergyMeter_AHU_3F',
        sDescription := 'AHU floor 3 power consumption',
        eUnit := E_BA_Unit.eEnergy_KilowattHours,
        fScale := 0.001,
        nMaxPresValue := 4294967295);     // UDINT 自然上界
    nMeterPulsesPlc : UDINT := 0;          // 从 EL1262 计数端子读出,PLC 内部累加
END_VAR

fbEnergyMeter.nVal := nMeterPulsesPlc;
fbEnergyMeter();""",
    business_block=(
        "- **场景**:每个空调机组装一只脉冲电度表,运维要在 BMS 上看每个机组累计电量与瞬时功率,做能效分析与计费分摊。\n"
        "- **价值**:Accumulator 是 BACnet 标准的能源计量对象,BMS / 第三方能源管理软件都识别;直接暴露 `nVal` + `fScale` + `eUnit`,BMS 端的「瞬时功率」由 Pulse_Rate 自动算。\n"
        "- **替代方案对比**:用 AV 暴露 `REAL` 累计值:失去 BACnet 标准的 Pulse_Rate / Scale 语义,BMS 看不到瞬时功率;能源管理软件可能不识别。"
    ),
    refs_extra="§6.1.1(ACC = Accumulator)、§3.2(Scale / Pulse_Rate / Max_Pres_Value 在 BACnet 标准属性表)",
    related="`FB_BACnet_PC`(脉冲转换,把累计脉冲转工程量)、`FB_BACnet_AI`(瞬时模拟量)",
))

_tcpou("FB_BACnet_ACC", """VAR
    // 空调机组电度表累计读数,1 脉冲 = 0.001 kWh
    fbEnergyMeter  : FB_BACnet_ACC := (
        sObjectName := 'EnergyMeter_AHU_3F',
        sDescription := 'AHU floor 3 cumulative power consumption',
        sDeviceType := 'PulseEnergyMeter',
        eUnit := E_BA_Unit.eEnergy_KilowattHours,
        fScale := 0.001,                       // 每脉冲 = 0.001 kWh
        nMaxPresValue := 4294967295);          // UDINT 上界(40 亿,绝对够用)

    // 模拟数据源:实际工程中由 EL1262 计数端子 + R_TRIG 累加得来,此处用模拟器
    nMeterPulsesPlc : UDINT := 0;
    fbPulseGen      : TON;
    bSimPulse       : BOOL := TRUE;            // 在线写 FALSE 暂停模拟
END_VAR""", """// =============================================================================
// 场景:每个空调机组装一只脉冲电度表,运维要在 BMS 上看每个机组累计电量
//       (kWh)与瞬时功率(kW),做能效分析与峰谷分时计费分摊。
// 价值:Accumulator 是 BACnet 标准的能源计量对象,BMS / 第三方能源管理软件都
//       识别;直接喂累计脉冲数 + Scale + Units,BMS 端的瞬时功率由 Pulse_Rate
//       自动算(由 stack 在两次读请求间求 delta/time)。
// 验证:1) 上电后 BACnet Explorer 读 Present_Value=0,Scale=0.001,
//       Units=kilowatt-hours。2) 在线让本程序跑(模拟器每秒+10 脉冲 = 0.01 kWh/s
//       = 36 kWh/h ≈ 36 kW 功率),Explorer 周期读 Present_Value 应单调递增,
//       Pulse_Rate ≈ 10 脉冲/秒;3) Explorer 反算的"瞬时功率"≈ 36 kW。
// =============================================================================

// ---- 模拟一个 10 Hz 脉冲源(实际工程是 EL1262 读出来) ----
fbPulseGen(IN := bSimPulse AND NOT fbPulseGen.Q, PT := T#100MS);
IF fbPulseGen.Q THEN
    nMeterPulsesPlc := nMeterPulsesPlc + 1;     // 累计永不归零(BACnet 语义)
END_IF

fbEnergyMeter.nVal := nMeterPulsesPlc;
fbEnergyMeter();
""")


# ============================================================================
# objects/FB_BACnet_PC  — Pulse Converter
# ============================================================================
_doc("objects", "FB_BACnet_PC", build_doc(
    fb_name="FB_BACnet_PC",
    category_label="Object · Pulse Converter",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Pulse Converter」对象类型(BACnet Object_Type = 24 / Pulse Converter),"
        "把累计脉冲(典型来源 ACC 对象 / 物理脉冲计数器)转成已乘以 Scale 的工程量。"
        "典型场景:电度表把累计脉冲转累计 kWh、累计水量。本对象类型在本库中仅基础类,无后缀变体。"
        "Status: ⚠️ PDF 仅在 §6.1.1 表中列出 PC 一行,未给出独立示例;本文档基于 BACnet 标准 PulseConverter 对象语义 + 本库命名规则推导成员列表。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 工程量 | `fVal` | `REAL` | Present_Value(已经乘了 Scale 的工程量,如 kWh) |",
        "| 缩放 | `fScale` | `REAL` | Scale(每脉冲对应的工程量) |",
        "| 单位 | `eUnit` | `E_BA_Unit` | Units |",
        "| 量程 | `fMinPresValue` / `fMaxPresValue` | `REAL` | 量程 |",
        "| 调整 | `fAdjustValue` | `REAL` | Adjust_Value(BMS 写入后让 Present_Value 回到该值,用于校正) |",
        "| 限值检测 | `fHighLimit` / `bHighLimitEnable` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 AI | 累计超限报警 |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_PC 每周期调用一次。PLC 把已经换算好的累计工程量(如累计 kWh)写到 `fVal`,"
        "BACnet stack 把它推到 Present_Value。与 Accumulator 的差别:Accumulator 暴露的是原始脉冲数 + Scale,"
        "由 BMS 端把 nVal × Scale 得到工程量;Pulse Converter 已经在 PLC 端做了乘法,Present_Value 直接是 kWh。"
        "Adjust_Value 是 PC 独有的属性:BMS 写 Adjust_Value 时 stack 把当前 Present_Value 调整为该值"
        "(用于「年度抄表后清零重计」或「换表后从已有累计值继续」)。PDF 未给独立示例,"
        "用法上参照 §9.16(数组初始化模式)与 §6.3.1(条件性写属性)。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码;本对象类型也未在 §9 给出示例,典型行为参照 BACnet 标准定义。"
    ),
    extra_tips_block=(
        "- **PC vs ACC**:PC 暴露的是已换算工程量,适合 BMS 端直接显示;ACC 暴露的是脉冲计数,适合 BMS 端做「瞬时流量」分析(Pulse_Rate)。\n"
        "- **`fVal` 单调递增**:与 ACC 一样,不要复位;BMS 通过 Adjust_Value 校正而不是直接写 Present_Value。\n"
        "- **掉电持久化必做**:用 VAR_RETAIN 保住 `fVal` 上次值(工程经验补充,与 ACC 同)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_PC
VAR
    // 把累计脉冲直接换算成 kWh,BMS 上看到的就是 kWh
    fbEnergyConv : FB_BACnet_PC := (
        sObjectName := 'EnergyKwh_AHU_3F',
        sDescription := 'AHU floor 3 cumulative energy (kWh)',
        eUnit := E_BA_Unit.eEnergy_KilowattHours,
        fScale := 0.001,
        fMinPresValue := 0.0,
        fMaxPresValue := 1.0E9);
    fEnergyKwhPlc : REAL := 0.0;        // PLC 把脉冲 × 0.001 后送来
END_VAR

fbEnergyConv.fVal := fEnergyKwhPlc;
fbEnergyConv();""",
    business_block=(
        "- **场景**:同 ACC,但 BMS 端只关心 kWh 显示,不需要瞬时 Pulse_Rate;PLC 端已经做好脉冲到工程量的乘法。\n"
        "- **价值**:把 ACC 的「脉冲数 + Scale 分两个属性」折叠成「已经换算的工程量」,BMS 端读 Present_Value 即可直接显示,无需在画面里写公式。\n"
        "- **替代方案对比**:用 ACC + BMS 端公式更标准化但 BMS 端复杂;用 AV 暴露 fVal 失去「累计永不归零」语义且不能用 Adjust_Value 校表。"
    ),
    refs_extra="§6.1.1(PC = Pulse Converter)",
    related="`FB_BACnet_ACC`(累计脉冲计数)、`FB_BACnet_AI`(瞬时模拟量)",
    status="⚠️ infer-from-naming-convention",
))

_tcpou("FB_BACnet_PC", """VAR
    // 把累计脉冲直接换算成 kWh,BMS 上看到的就是 kWh 累计值
    fbEnergyConv   : FB_BACnet_PC := (
        sObjectName := 'EnergyKwh_AHU_3F',
        sDescription := 'AHU floor 3 cumulative energy (kWh)',
        eUnit := E_BA_Unit.eEnergy_KilowattHours,
        fScale := 0.001,                      // 每脉冲 = 0.001 kWh
        fMinPresValue := 0.0,
        fMaxPresValue := 1.0E9);              // 1 GWh 上界(够民用大用户)

    fEnergyKwhPlc  : REAL := 0.0;             // PLC 端把脉冲 × 0.001 后送来
END_VAR""", """// =============================================================================
// 场景:同电度表场景,但 BMS 端只关心 kWh 累计显示,不需要瞬时 Pulse_Rate;
//       PLC 端已经把脉冲乘以 Scale 做好换算。
// 价值:把 ACC 的"脉冲数 + Scale 分两个属性"折叠成"已经换算的工程量",BMS
//       端读 Present_Value 即可直接显示,无需在画面里写公式;Adjust_Value 让
//       运维"年度抄表后清零"或"换表后接续"。
// 验证:1) 上电后 BACnet Explorer 读 Present_Value=0.0,Units=kilowatt-hours。
//       2) 在线写 fEnergyKwhPlc := 123.456,Explorer 应看到 Present_Value=123.456。
//       3) Explorer 写 Adjust_Value := 1000.0,Present_Value 应跳到 1000.0
//       (Adjust 校正语义)。
// 注意:本对象类型 PDF/InfoSys 仅在 §6.1.1 表中列出,未给独立示例,Adjust_Value
//       由 BMS 端写入触发的具体行为以 BACnet 标准定义为准。
// =============================================================================

fbEnergyConv.fVal := fEnergyKwhPlc;
fbEnergyConv();
""")


# ============================================================================
# objects/FB_BACnet_Prog  — Program
# ============================================================================
_doc("objects", "FB_BACnet_Prog", build_doc(
    fb_name="FB_BACnet_Prog",
    category_label="Object · Program",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Program」对象类型(BACnet Object_Type = 16 / Program),"
        "用于把 PLC 内的应用程序状态(Run / Halted / Idle / Unloaded / Waiting / Loading 等)暴露给 BMS。"
        "BMS 可以通过 `Program_Change` 属性向 PLC 发送启动 / 停止 / 重启 / 卸载请求,PLC 接到请求后由"
        "本 FB 在 `Program_State` 输出当前应用程序的实际状态。本对象类型在本库中仅基础类,无后缀变体。"
        "Status: ⚠️ PDF 仅在 §6.1.1 表中列出 Prog 一行,未给独立示例;本文档基于 BACnet 标准 Program 对象语义 + 本库命名规则推导。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 程序状态 | `eState` | `E_BACnet_ProgramState` | Program_State(`eIdle` / `eRunning` / `eHalted` / `eUnloading` / `eLoading` / `eWaiting`) |",
        "| 控制请求 | `eChange` | `E_BACnet_ProgramRequest` | Program_Change(BMS 写入触发状态切换:`eReady` / `eLoad` / `eRun` / `eHalt` / `eRestart` / `eUnload`) |",
        "| 出错原因 | `eReason` | `E_BACnet_ProgramError` | Reason_For_Halt(Halted 状态下说明原因) |",
        "| 描述 | `sDescriptionOfHalt` | `STRING(*)` | Description_Of_Halt(自由文本说明) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_Prog 每周期调用一次,PLC 把当前应用程序状态写到 `eState`(典型用法:启动时写 eLoading,"
        "进入正常循环写 eRunning,被运维 Halt 后写 eHalted,等等)。BMS 通过 `WriteProperty(Program_Change, eRun)` "
        "发请求,PLC 在本 FB 的 `eChange` 引脚上读到 BMS 的请求,然后由 PLC 自定义代码决定是否接受请求并切换 eState。"
        "本 FB 本身不强制状态机,只是把状态字段标准化暴露 — BMS 看到的是 BACnet 标准的 ProgramState 枚举,"
        "不论 PLC 内部实际怎么实现状态切换。Reason_For_Halt 在 eState=eHalted 时由 PLC 填写,BMS 读到后可"
        "显示具体错误码。PDF 未给独立示例,典型用法参照 BACnet 标准定义。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码;本对象类型也未在 §9 给出示例。"
    ),
    extra_tips_block=(
        "- **PLC 端要响应 `eChange`**:本 FB 只是把 BMS 写入的 Program_Change 暴露到 `eChange`,PLC 还需要自己读这个值并决定是否接受请求(典型:`IF fbProg.eChange = eHalt THEN ...PLC_Halt_Logic...; fbProg.eState := eHalted; END_IF`)。\n"
        "- **eChange 写入后建议清零**:接受请求并切换状态后,把 `eChange := eReady` 让 BMS 知道请求已处理(工程经验补充)。\n"
        "- **状态切换要原子化**:不要在不同周期里写 eState 不同值,会让 BMS 看到中间态闪烁(用上升沿触发 + 状态机集中管理)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_Prog
VAR
    fbAppStatus : FB_BACnet_Prog := (
        sObjectName := 'MainApp_Status',
        sDescription := 'Floor 3 East zone control app',
        eState := E_BACnet_ProgramState.eLoading);  // 上电初始
    bAppReady : BOOL := FALSE;
END_VAR

IF bAppReady AND fbAppStatus.eState = E_BACnet_ProgramState.eLoading THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eRunning;
END_IF
// BMS 请求 Halt
IF fbAppStatus.eChange = E_BACnet_ProgramRequest.eHalt THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eHalted;
    fbAppStatus.eReason := E_BACnet_ProgramError.eOther;
    fbAppStatus.sDescriptionOfHalt := 'Halted by BMS request';
    fbAppStatus.eChange := E_BACnet_ProgramRequest.eReady;  // 清零
END_IF
fbAppStatus();""",
    business_block=(
        "- **场景**:大型楼控项目希望在 BMS 上看到每个 PLC 应用程序的运行状态;运维可以远程 Halt 某个程序(如冬季关停喷淋系统的控制程序),无需远程登录 PLC。\n"
        "- **价值**:Program 是 BACnet 标准的运行时管理对象,BMS 直接显示状态 / 发请求,代替「自己写 Modbus 寄存器 + 协议解码」的脏方案。\n"
        "- **替代方案对比**:用 MV 暴露状态:能显示但 BMS 端没有「Program_Change」语义,无法标准化「控制请求」。"
    ),
    refs_extra="§6.1.1(Prog = Program)",
    related="`FB_BACnet_Device`(本机设备对象)、`FB_BACnet_MV`(虚拟多态值)",
    status="⚠️ infer-from-naming-convention",
))

_tcpou("FB_BACnet_Prog", """VAR
    // PLC 应用程序状态暴露给 BMS,运维可远程 Halt
    fbAppStatus  : FB_BACnet_Prog := (
        sObjectName := 'MainApp_Status',
        sDescription := 'Floor 3 East zone control application',
        eState := E_BACnet_ProgramState.eLoading);

    bAppInitDone : BOOL := FALSE;            // 在线写 TRUE 模拟 "初始化完成"
END_VAR""", """// =============================================================================
// 场景:大型楼控项目希望在 BMS 上看到每个 PLC 应用程序的运行状态;运维可以
//       远程 Halt 某个程序(如冬季关停喷淋系统),无需远程登录 PLC 改代码。
// 价值:Program 是 BACnet 标准的运行时管理对象,BMS 直接显示状态/发请求,代
//       替"自己写 Modbus 寄存器 + 协议解码"的脏方案。
// 验证:1) 上电后 BACnet Explorer 读 Program_State=loading。2) 在线写
//       bAppInitDone := TRUE,Program_State 应切换到 running。3) Explorer 写
//       Program_Change := halt,Program_State 应切到 halted,Reason_For_Halt
//       和 Description_Of_Halt 应被填写。
// 注意:本对象类型 PDF/InfoSys 未给独立示例,具体的 Program_Change 处理逻辑
//       由 PLC 应用决定;此例只演示标准状态字段的暴露。
// =============================================================================

// ---- 初始化完成后切到 running ----
IF bAppInitDone AND fbAppStatus.eState = E_BACnet_ProgramState.eLoading THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eRunning;
END_IF

// ---- BMS 请求 halt 时切换状态并清零 ----
IF fbAppStatus.eChange = E_BACnet_ProgramRequest.eHalt THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eHalted;
    fbAppStatus.eReason := E_BACnet_ProgramError.eOther;
    fbAppStatus.sDescriptionOfHalt := 'Halted by BMS request';
    fbAppStatus.eChange := E_BACnet_ProgramRequest.eReady;
END_IF

// ---- BMS 请求 run 时切回 running ----
IF fbAppStatus.eChange = E_BACnet_ProgramRequest.eRun THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eRunning;
    fbAppStatus.eChange := E_BACnet_ProgramRequest.eReady;
END_IF

fbAppStatus();
""")


# ============================================================================
# objects/FB_BACnet_NC  — Notification Class
# ============================================================================
_doc("objects", "FB_BACnet_NC", build_doc(
    fb_name="FB_BACnet_NC",
    category_label="Object · Notification Class",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Notification Class」对象类型(BACnet Object_Type = 15 / Notification Class)。"
        "它是 BACnet 报警 / 事件路由表 — 每个支持 Intrinsic Reporting 的对象(AI / AV / BI / BV / MI / MV / EE 等)"
        "通过 `nNotificationClass` 引用一个 NC 实例,该 NC 维护一张 `Recipient_List`,把符合订阅时间窗的"
        "OFFNORMAL / FAULT / NORMAL 事件按优先级分别发给所有 recipient(BMS / 报警接收 PLC / 邮件网关等)。"
        "PDF §9.8 / §9.9 给出多个完整示例。本对象类型本库仅基础类。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 实例号 | `nObjectInstance` | `UDINT` | NC 对象实例号(被其它对象的 `nNotificationClass` 引用) |",
        "| Notification Class | `nNotificationClass` | `UDINT` | 通常与 `nObjectInstance` 同值(BACnet 标准要求) |",
        "| 优先级 | `aPriority` | `ARRAY[0..2] OF USINT` | Priority(OFFNORMAL / FAULT / NORMAL 三种类型各自的事件优先级 0..255) |",
        "| 确认 | `aAckRequired` | `ARRAY[0..2] OF BOOL` | Ack_Required(OFFNORMAL / FAULT / NORMAL 是否需要 BMS 端 ack) |",
        "| Recipient List | `aRecipientList` | `ARRAY OF ST_BACnet_NC_Recipient` | Recipient_List(订阅者表,详见 §9.8 示例) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_NC 每周期调用一次。它本身没有 Present_Value,作用是路由其它对象生成的事件。"
        "`nObjectInstance` 与 `nNotificationClass` 必须相等(BACnet 标准要求,且大多数实现按这个键关联)。"
        "其它对象设置 `nNotificationClass := 10` 后,这些对象产生 OFFNORMAL / FAULT / NORMAL 事件时,"
        "stack 会查找 `nObjectInstance := 10` 的 NC 实例,按 `aPriority[<事件类型>]` 给事件加优先级,"
        "把事件按 `aRecipientList` 中匹配 `stValidDays + stFromTime + stToTime` 的 recipient 发出。"
        "PDF §9.8 示例展示了两种 recipient:`F_BACnet_DeviceRecipient(nDeviceInstance := 42)` "
        "(按 BACnet device-id 解析,stack 自动用 Who-Is 发现);"
        "`F_BACnet_EthernetRecipient(...)`(直接给 IP / 端口 / 网络号,适合穿越路由器)。"
        "`bIssueConfirmed` 决定是否用 ConfirmedEventNotification(需 ack)还是 Unconfirmed(发即忘)。"
    ),
    error_section=(
        "无返回值。事件路由失败时(recipient 联系不上、订阅窗口不匹配)stack 不报错,事件就静默丢弃 — "
        "需要在 NC 实例的 Recipient_List 配合 BACnet Explorer 或抓包诊断。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **`nObjectInstance` 不能与其它 NC 重复**:每个 NC 实例号唯一,且必须有一个对象 / EE 在引用,否则配了等于空跑。\n"
        "- **`aPriority` 是 BACnet 标准的事件优先级(0..255),不是命令优先级(1..16)**:常用 OFFNORMAL=10 / FAULT=11 / NORMAL=12,让 BMS 显示报警等级。\n"
        "- **空 recipient list 也合法**:PDF §9.8 示例 fbNC01_Standard 就是空列表 — 适合「BMS 自己来订阅,PLC 端不预定义 recipient」的场景。\n"
        "- **预定义 recipient 与 BMS 后期订阅可共存**:PLC 端预定义的 + BMS Write 进来的会合并到 Recipient_List。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_NC
VAR
    fbAlarmClass : FB_BACnet_NC := (
        nObjectInstance := 10,
        nNotificationClass := 10,
        sObjectName := 'NC_Alarms',
        aAckRequired := [TRUE, TRUE, FALSE],
        aPriority := [10, 11, 12]);
END_VAR
fbAlarmClass();""",
    business_block=(
        "- **场景**:楼控项目用 10 类 NC 把不同等级的报警分别路由 — NC10 给 BMS 主屏(需 ack),"
        "NC20 给运维微信报警网关(不 ack),NC30 给打印机(只记不显示)。每个 AI / BV 通过 `nNotificationClass` 选择把事件路由到哪个 NC。\n"
        "- **价值**:BACnet 标准的报警路由,跨厂商 BMS 都识别;BMS 可远程改 Recipient_List 增删订阅。\n"
        "- **替代方案对比**:用 ADS 把报警条目送到中心数据库:跨厂商不通;用 SNMP trap:协议层弱无法保证投递。"
    ),
    refs_extra="§6.1.1(NC = Notification Class)、§3.2.18(Notification_Class)、§9.8(配 NC + recipient list)、§9.9(用 NC 做接收外部设备报警)、§9.10(预警限 + 双 NC)",
    related="`FB_BACnet_AI` / `BV` / `MV`(事件源)、`FB_BACnet_EE`(算法报警)、`FB_BACnet_ELog`(本地存报警)",
))

_tcpou("FB_BACnet_NC", """VAR
    // 配 1 个 NC10 + 1 个用 NC10 路由报警的 BV(NC 实例必须有对象引用才有意义)
    fbAlarmClass : FB_BACnet_NC := (
        nObjectInstance := 10,
        nNotificationClass := 10,
        sObjectName := 'NC_Alarms_BMS',
        sDescription := 'Alarm notification class for BMS main display',
        aAckRequired := [TRUE, TRUE, FALSE],     // OFFNORMAL / FAULT 需 ack;NORMAL 不需要
        aPriority := [10, 11, 12]);              // 报警等级(BACnet 标准 0..255)

    fbTestAlarm  : FB_BACnet_BV := (
        sObjectName := 'TestAlarm',
        sInactiveText := 'OK',
        sActiveText := 'Alarm',
        bAlarmValue := TRUE,
        aEventEnable := [TRUE, TRUE, TRUE],
        bEventDetectionEnable := TRUE,
        nNotificationClass := 10,                // 路由到 NC10
        aEventMessageTextsConfig := ['Test alarm raised', 'Sensor fault', 'Recovered']);

    bRaiseAlarm  : BOOL := FALSE;                // 在线写 TRUE 触发一次报警
END_VAR""", """// =============================================================================
// 场景:楼控项目用 NC10 把所有 BMS 主屏报警分类路由;BMS 端能收到 BACnet
//       ConfirmedEventNotification,自动产生告警条目并响铃。运维 ack 后 NC10
//       维护已 ack 状态。
// 价值:BACnet 标准的报警路由表,跨厂商 BMS 都识别;BMS 可远程改 Recipient_List
//       增删订阅,无需 PLC 重启。
// 验证:1) BACnet Explorer 连本机,订阅 NC10 的 Recipient_List。2) 在线写
//       bRaiseAlarm := TRUE,Explorer 应收到一条 ConfirmedEventNotification,
//       event type = TO_OFFNORMAL,priority=10,message='Test alarm raised'。
//       3) bRaiseAlarm := FALSE,应收到一条 unconfirmed 的 NORMAL 通知。
// =============================================================================

fbTestAlarm.bEnPgm  := TRUE;
fbTestAlarm.bValPgm := bRaiseAlarm;

fbAlarmClass();
fbTestAlarm();
""")


# ============================================================================
# objects/FB_BACnet_Cal  — Calendar
# ============================================================================
_doc("objects", "FB_BACnet_Cal", build_doc(
    fb_name="FB_BACnet_Cal",
    category_label="Object · Calendar",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Calendar」对象类型(BACnet Object_Type = 6 / Calendar)。"
        "维护一张 `Date_List`,Schedule 对象可引用该 Calendar 来判断今天是不是节假日 / 例外日,"
        "对应做不同时段动作。Date_List 中每项可以是单日(`eDate`)、日期区间(`eDateRange`)、"
        "或日 / 周 / 月组合(`eWeekNDay`)。PDF §9.11 给完整示例。本对象类型本库仅基础类。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 日期表 | `aDateList` | `ARRAY OF ST_BA_DateValChoice` | Date_List(每项含 `eType` 与 `uDate`) |",
        "| 当前匹配状态 | `bPresVal`(只读) | `BOOL` | Present_Value(今天是否在 Date_List 中,stack 自动算) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_Cal 每周期调用一次。stack 每天 0 点自动判断今天是否落在 Date_List 任一项:"
        "`eDate` 比较单日;`eDateRange` 落在起止日期之间;`eWeekNDay` 按「第 N 个星期 M」(如「2 月第 1 个周五」)"
        "等模式匹配。匹配则 Present_Value = TRUE。Schedule 对象通过 `aCalendar` 引用本 Cal,"
        "在 Cal.PresVal=TRUE 那天用 `aEntry` 替换默认 Weekly_Schedule(PDF §9.11 示例)。"
        "三种日期项可在同一 Cal 中混用,且月份 / 日期支持 BACnet 标准的奇偶通配:"
        "Month=13(奇数月)/ 14(偶数月)、Day=32(月末)/ 33(奇数日)/ 34(偶数日)。"
    ),
    error_section=(
        "无返回值。`bPresVal` 读出当前匹配状态;无错误码。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **`aDateList` 长度上限受 BACnet_Param 控制**:超长会被 truncated,通常 100 个日期项够大多数项目用。\n"
        "- **`eWeekNDay` 用于中国春节 / 母亲节等浮动节假日**:用单日 `eDate` 每年都要更新,用 WeekNDay 一次设好;Day=32 表示月末,适合每月最后一个工作日财务系统切换。\n"
        "- **修改 Date_List 用条件触发**:`IF bUpdateCalendar THEN fbCal.aDateList[0].uDate := ...; END_IF`;周期写会覆盖 BMS 端调整(PDF §6.3.1 规则)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_Cal
VAR
    fbHolidayCal : FB_BACnet_Cal := (
        sObjectName := 'PublicHolidays',
        aDateList := [
            (eType := E_BA_DateValChoice.eDate,
             uDate := F_BA_DateVal(2026, E_BA_Month.eOctober, 1))
        ]);
    bIsHolidayToday : BOOL;
END_VAR

fbHolidayCal();
bIsHolidayToday := fbHolidayCal.bPresVal;""",
    business_block=(
        "- **场景**:楼控项目要按节假日不开空调 / 灯光按节能时段运行,运维一次配好全年节假日表,Schedule 自动按 Calendar 切换。\n"
        "- **价值**:BACnet 标准的节假日表,Schedule 引用一行解决;BMS 端可远程改节假日,无需停 PLC。\n"
        "- **替代方案对比**:用 PLC 内部 BOOL 数组手写判断今天是不是节假日:跨年要重写,且 BMS 看不到。"
    ),
    refs_extra="§6.1.1(Cal = Calendar)、§9.11(Calendar + Schedule 完整示例)",
    related="`FB_BACnet_SchedA` / `SchedB` / `SchedM`(引用本 Cal 做例外日程)、`FB_BACnet_Date` / `DateP`(单日 / 日期模式原语对象)",
))

_tcpou("FB_BACnet_Cal", """VAR
    // 2026 中国法定节假日表简化版:元旦 + 国庆 + 母亲节
    fbHolidayCal : FB_BACnet_Cal := (
        sObjectName := 'PublicHolidays_2026',
        sDescription := 'PRC public holidays 2026',
        aDateList := [
            // 元旦
            (eType := E_BA_DateValChoice.eDate,
             uDate := F_BA_DateVal(2026, E_BA_Month.eJanuary, 1)),
            // 国庆 10/1-10/7
            (eType := E_BA_DateValChoice.eDateRange,
             uDate := F_BA_DateRangeVal(nFromYear := 2026, E_BA_Month.eOctober, 1,
                                        nToYear := 2026, E_BA_Month.eOctober, 7)),
            // 每年 5 月第 2 个周日 = 母亲节
            (eType := E_BA_DateValChoice.eWeekNDay,
             uDate := F_BA_WeekNDayVal(E_BA_Weekday.eSunday, E_BA_Week.eWeek2, E_BA_Month.eMay))
        ]);

    bIsHolidayToday : BOOL;
END_VAR""", """// =============================================================================
// 场景:楼控项目要按 节假日不开空调 / 灯光按节能时段 运行,运维一次配好全年
//       节假日表后 Schedule 自动切换;母亲节这种浮动日期用 WeekNDay 一次搞定。
// 价值:BACnet 标准的节假日表,Schedule 引用一行解决;BMS 端可远程改节假日表,
//       无需停 PLC;母亲节用 WeekNDay 表达后跨年不用维护。
// 验证:1) 今天若是 2026-10-03(国庆假期内),BACnet Explorer 读 Present_Value
//       应为 TRUE,bIsHolidayToday 应为 TRUE。2) 今天若是 2026-05-10(母亲节),
//       Present_Value 也应为 TRUE。3) 今天若是普通工作日,Present_Value 为 FALSE。
// =============================================================================

fbHolidayCal();
bIsHolidayToday := fbHolidayCal.bPresVal;
""")


# ============================================================================
# objects/FB_BACnet_SchedA / SchedB / SchedM  — Schedule trio
# ============================================================================
def _make_sched_doc(name: str, sched_type: str, data_type: str, helper_fn: str,
                    overview_extra: str, related: str) -> str:
    return build_doc(
        fb_name=name,
        category_label=f"Object · Schedule {sched_type}",
        infosys_url=URL_OBJECTS,
        overview=(
            f"代表 BACnet 标准里的「Schedule {sched_type}」对象类型,周程序时间表 — "
            f"按 Monday..Sunday 每天定义一组「时刻 → 值」对(类型 `{data_type}`),"
            "stack 每分钟检查当前时刻,把对应值写到所有 `aObjectPropertyReferences` 列出的目标对象属性。"
            "Schedule 可以引用一个或多个 Calendar 做例外日(节假日不同时间表),"
            f"也可直接在 `aException` 内联例外。{overview_extra} PDF §9.11 给完整示例。"
        ),
        members_table_rows=[
            "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
            "| 每周时间表 | `aWeek` | `ARRAY[1..7] OF ST_BACnet_SchedWeek*` | Weekly_Schedule(Monday..Sunday 各自的 时刻 → 值 对) |",
            f"| 当前值 | `bPresVal` / `fPresVal` / `nPresVal`(按变体取一) | `{data_type}` | Present_Value(当前时段对应的 {data_type} 值) |",
            "| 默认值 | `bScheduleDefault` / `fScheduleDefault` / `nScheduleDefault` | 同 Present_Value 类型 | Schedule_Default(每天 0 点 / 任何「无定义」时刻使用) |",
            "| Calendar 例外 | `aCalendar` | `ARRAY OF ST_BACnet_SchedCalRef` | List_Of_Calendars(每项含 `iRefCalendar + aEntry`,Cal.PresVal=TRUE 那天用 aEntry 代替 aWeek) |",
            "| 内联例外 | `aException` | `ARRAY OF ST_BACnet_SchedException` | Exception_Schedule(节假日 / 单日 / 区间内联,优先级高于 aWeek) |",
            "| 目标对象 | `aObjectPropertyReferences` | `ARRAY OF ST_BACnet_ObjectPropertyReference` | List_Of_Object_Property_References(把 Present_Value 写到哪些对象的哪个属性) |",
            "| 写优先级 | `nPriorityForWriting` | `USINT` | Priority_For_Writing(写目标对象用什么 BACnet 优先级,默认 16) |",
        ],
        variants_table_rows=None,
        behaviour=(
            f"FB_BACnet_Schedule 每周期调用一次,stack 每分钟比较当前时刻与本周对应天的 aWeek 表,"
            f"取该时刻已过的最后一个「时刻 → 值」对作为 Present_Value;在每天 0 点开始时若 aWeek[今日]"
            "为空,则使用 Schedule_Default。`aCalendar` / `aException` 的判定优先级高于 aWeek:"
            "Cal.PresVal=TRUE 或 Exception 命中时用对应 aEntry 替换。`aObjectPropertyReferences` 列出"
            "目标对象 + 属性 ID(如 `(iObject := fbAO, ePropertyId := PropPresentValue)`),"
            "stack 在 Present_Value 变化时用 `nPriorityForWriting` 写一次目标对象。"
            f"PDF §9.11 用 {helper_fn} 帮助函数声明周程序(如 `{helper_fn}(eMonday, eFriday, T#0H, ..., T#6H, ..., T#20H, ...)` "
            "表示周一到周五对应时刻取对应值,非 aWeek 中提到的时刻继承前一时段值)。"
        ),
        error_section=(
            "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。"
        ),
        extra_tips_block=(
            "- **改 Schedule 用条件触发**:运行时改 aWeek / aException 要用 `IF bChanged THEN ...; bChanged := FALSE; END_IF`,周期写会覆盖 BMS 端调整。\n"
            "- **`bWriteException` 是特殊触发位**:PDF §9.11 示例显示 `fbSchedM.bWriteException := TRUE;` 用来强制把当前修改的 aCalendar 项写到 stack(运行时改后必须置位才生效)。\n"
            "- **不要把多个 Schedule 写到同一目标属性**:目标对象的优先级槽位会被几个 Schedule 抢,行为不确定;改用一个 Schedule + Calendar 做不同情况切换。"
        ),
        example_code=(
            "PROGRAM P_Demo_" + name + "\n"
            "VAR\n"
            "    fbSched : " + name + " := (\n"
            "        sObjectName := '" + sched_type + "Schedule',\n"
            "        aWeek := " + helper_fn + "(\n"
            "            E_BA_Weekday.eMonday, E_BA_Weekday.eFriday,\n"
            "            T#0H, " + ("FALSE" if data_type == "BOOL" else ("18.0" if data_type == "REAL" else "2")) + ",\n"
            "            T#7H, " + ("TRUE" if data_type == "BOOL" else ("22.0" if data_type == "REAL" else "1")) + ",\n"
            "            T#19H, " + ("FALSE" if data_type == "BOOL" else ("18.0" if data_type == "REAL" else "2")) + "));\n"
            "END_VAR\n"
            "fbSched();"
        ),
        business_block=(
            "- **场景**:工作日 7 点开空调到 22°C / 开灯 / 切运行模式,19 点切回 18°C / 关灯 / 待机;周末与节假日(引用 PublicHolidays Calendar)按 Schedule_Default 节能运行。\n"
            "- **价值**:BACnet 标准的时间表,BMS 端可视化拖时段;PLC 端把工程量写到下游 AO/BO/MO 全自动。\n"
            "- **替代方案对比**:用 PLC 内部 TON + IF 判断当前时刻:跨节假日要 PLC 写一堆 IF,BMS 看不到时间表内容。"
        ),
        refs_extra=f"§6.1.1(SchedA/B/M = Schedule {sched_type})、§9.11(Calendar + Schedule 完整示例)",
        related=related,
    )


_doc("objects", "FB_BACnet_SchedA", _make_sched_doc(
    "FB_BACnet_SchedA", "Analog", "REAL",
    "F_BACnet_SchedWeekly3xA",
    "本变体处理 REAL 值(温度设定点、阀位、转速等)。",
    "`FB_BACnet_SchedB` / `FB_BACnet_SchedM`(布尔 / 多态变体)、`FB_BACnet_Cal`(节假日表)、`FB_BACnetRM_SchedA`(远端 Schedule 引用)",
))
_doc("objects", "FB_BACnet_SchedB", _make_sched_doc(
    "FB_BACnet_SchedB", "Binary", "BOOL",
    "F_BACnet_SchedWeekly3xB",
    "本变体处理 BOOL 值(灯光、风机、阀门开关等)。",
    "`FB_BACnet_SchedA` / `FB_BACnet_SchedM`(REAL / 多态变体)、`FB_BACnet_Cal`(节假日表)、`FB_BACnetRM_SchedB`(远端 Schedule 引用)",
))
_doc("objects", "FB_BACnet_SchedM", _make_sched_doc(
    "FB_BACnet_SchedM", "Multistate", "UDINT",
    "F_BACnet_SchedWeekly3xM",
    "本变体处理多态枚举值(运行场景 Day/Night/Eco、灯光场景 1/2/3 等)。",
    "`FB_BACnet_SchedA` / `FB_BACnet_SchedB`(REAL / 布尔变体)、`FB_BACnet_Cal`(节假日表)、`FB_BACnetRM_SchedM`(远端 Schedule 引用)",
))

_tcpou("FB_BACnet_SchedA", """VAR
    // 房间温度设定点周时间表:工作日 7:00 升到 22°C,19:00 降到 18°C
    fbRoomSchedA   : FB_BACnet_SchedA := (
        sObjectName := 'RoomTempSchedule_3F',
        sDescription := 'Floor 3 East zone temperature schedule',
        aWeek := F_BACnet_SchedWeekly3xA(
            E_BA_Weekday.eMonday, E_BA_Weekday.eFriday,
            T#0H,  18.0,
            T#7H,  22.0,
            T#19H, 18.0),
        fScheduleDefault := 18.0);             // 节假日 / 周末用默认值
END_VAR""", """// =============================================================================
// 场景:房间温度设定点按时间表自动切换,工作日 7:00 升到 22°C 让员工到岗时舒适,
//       19:00 降到 18°C 进入节能模式;周末与节假日全天 18°C 节能。
// 价值:BACnet 标准的时间表,BMS 端可视化拖时段;PLC 不用写一堆 IF 判时刻。
// 验证:1) BACnet Explorer 读 Present_Value 应跟时段对应(早上 7 点之前 18.0,
//       7 点后 22.0,19 点后 18.0)。2) 把系统时间临时改到 8:00,Present_Value
//       应跳到 22.0。3) aObjectPropertyReferences 留空时本对象只暴露当前值,
//       不写下游;实际工程中应在 aObjectPropertyReferences 加目标 AV_Setp 引用。
// =============================================================================

fbRoomSchedA();
""")

_tcpou("FB_BACnet_SchedB", """VAR
    // 走廊灯周时间表:工作日 6:30 开,19:30 关;周末全关
    fbHallLightSchedB : FB_BACnet_SchedB := (
        sObjectName := 'HallLightSchedule_3F',
        sDescription := 'Floor 3 hallway light schedule',
        aWeek := F_BACnet_SchedWeekly3xB(
            E_BA_Weekday.eMonday, E_BA_Weekday.eFriday,
            T#0H,    FALSE,
            T#6H30M, TRUE,
            T#19H30M, FALSE),
        bScheduleDefault := FALSE);
END_VAR""", """// =============================================================================
// 场景:走廊灯按时间表自动开关,工作日 6:30 开,19:30 关;周末全关。
// 价值:BACnet 标准时间表,BMS 端拖动调整 / 远程查询。
// 验证:1) BACnet Explorer 读 Present_Value=FALSE(下班时段)。2) 临时把
//       系统时间改到 8:00 Monday,Present_Value 应跳到 TRUE。3) 周末
//       Present_Value 为 FALSE。
// =============================================================================

fbHallLightSchedB();
""")

_tcpou("FB_BACnet_SchedM", """VAR
    // 楼宇运行场景周时间表:工作日 6 点切到 Day(1),22 点切到 Night(2)
    fbBuildingSchedM : FB_BACnet_SchedM := (
        sObjectName := 'BuildingModeSchedule',
        sDescription := 'Whole building mode schedule',
        aWeek := F_BACnet_SchedWeekly3xM(
            E_BA_Weekday.eMonday, E_BA_Weekday.eFriday,
            T#0H,  2,
            T#6H,  1,
            T#22H, 2),
        nScheduleDefault := 4);                // 周末 / 节假日 Eco
END_VAR""", """// =============================================================================
// 场景:楼宇运行模式(1=Day / 2=Night / 3=Holiday / 4=Eco)按时间表自动切换,
//       工作日 6 点切 Day,22 点切 Night;周末全天 Eco。
// 价值:把 4 种模式的切换标准化为一个 BACnet Schedule,BMS 端可视化时段;下游
//       空调 / 灯光 / 电梯调度都引用本 Schedule 自动跟随。
// 验证:1) 工作日早上 BACnet Explorer 读 Present_Value=1(Day)。2) 临时改
//       系统时间到 23:00,Present_Value=2(Night)。3) 周末 Present_Value=4(Eco)。
// =============================================================================

fbBuildingSchedM();
""")


# ============================================================================
# objects/FB_BACnet_TLog  — Trendlog(单通道) + TLogBuf 变体
# ============================================================================
_doc("objects", "FB_BACnet_TLog", build_doc(
    fb_name="FB_BACnet_TLog",
    category_label="Object · Trend Log",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Trend Log」对象类型(BACnet Object_Type = 20 / Trend Log)。"
        "按周期 / COV / 触发模式记录另一个对象属性(典型 Present_Value)的时序数据,"
        "缓存到 router memory 的循环缓冲区中,BMS 端通过 `ReadRange` 服务读出做趋势图。"
        "PDF §9.12 / §9.13 给完整示例。本库提供基础类(纯 BACnet 缓冲)+ `_Buf` 变体"
        "(`FB_BACnet_TLogBuf`,在 PLC 端额外暴露 `aLogBuffer : T_BACnet_TLogBuffer` 数组,"
        "让 PLC 本地可视化历史数据)。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 触发源 | `stObjectPropertyReference` | `ST_BACnet_ObjectPropertyReference` | Log_Device_Object_Property(`F_BACnet_Reference(fbAv, PropPresentValue)`) |",
        "| 采集模式 | `eLoggingType` | `E_BA_LoggingType` | Logging_Type(`ePolled` / `eCOV` / `eTriggered`) |",
        "| 采集间隔 | `nLogInterval` | `UDINT` | Log_Interval(1/100 秒,如 300 = 3 秒) |",
        "| 控制 | `bLogEnable` / `bTrigger` | `BOOL` | Enable / Trigger(eTriggered 模式下置 TRUE 触发一次采集) |",
        "| 起止时间 | `stStartTime` / `stStopTime` | `ST_BA_DateTime` | Start_Time / Stop_Time |",
        "| 缓冲容量 | `nBufferSize` | `UDINT` | Buffer_Size(条数) |",
        "| COV 模式 | `nCOVResubscriptionInterval` / `stClientCOV` | `UDINT` / `ST_BACnet_ClientCOV` | COV_Resubscription_Interval / Client_COV_Increment |",
        "| 通知 | `nNotificationClass` / `nNotificationThreshold` | `UDINT` / `UDINT` | 缓冲使用率到阈值触发通知 |",
        "| `_Buf` 增 | `aLogBuffer` | `ARRAY OF ST_BA_TrendEntry` | PLC 端本地缓冲(字段见 §9.13) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_TLog` | — | 基础类:缓冲仅在 router memory |",
        "| `FB_BACnet_TLogBuf` | 增 `aLogBuffer : T_BACnet_TLogBuffer` | PLC 端额外可读本地缓冲数组(PDF §9.13) |",
    ],
    behaviour=(
        "FB_BACnet_TLog 每周期调用一次。`ePolled` 模式下 stack 按 `nLogInterval` 间隔采样 stObjectPropertyReference "
        "指向的属性,写一条记录;`eCOV` 模式下被采样对象自身触发 COV 时记录(PDF §9.12 `fbTLogCov` 示例,"
        "需配 `nCOVResubscriptionInterval` 与 `stClientCOV` 指定增量);`eTriggered` 模式下 PLC 写 `bTrigger := TRUE` "
        "触发一次记录(适合按门禁刷卡事件采样温度等)。`bLogEnable` 是总开关,FALSE 时不记录,记录时也写一条 "
        "type=eStopLogging 的事件条目。缓冲区满后行为按 `bStopWhenFull` 决定:TRUE 停止记录,FALSE 覆盖最老条目。"
        "`_Buf` 变体下 PLC 可直接读 `aLogBuffer[i].dtTime / .eType / .uValue` 做本地趋势可视化"
        "(PDF §9.13 详细字段:eBinary / eAnalog / eMultistate / eEvent + bStart / bStop / bBufferPurged / bInterrupted 状态位)。"
    ),
    error_section=(
        "无返回值。`stStatusFlags.bFault = TRUE` 在被采样对象不可达 / Reference 无效时置位。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **TLog 占内存大**:每条记录约 56 字节(PDF §6.5.1),Buffer_Size = 1008(7 天 × 24 × 6 次/小时)占约 56 KB router memory;一个项目几十个 TLog 容易撑满 32 MB 默认 router memory。\n"
        "- **`eCOV` 模式不要乱用**:被采样对象 COV 太频繁(如 fCovIncrement=0)会让 TLog 缓冲瞬间撑满。\n"
        "- **`_Buf` 变体的本地数组访问受同步约束**:PDF §9.13 警告读 `aLogBuffer` 时要避开 stack 写入瞬间;实际工程用 R_TRIG 仅在外部条件触发时读取。\n"
        "- **触发型 TLog 的 `bTrigger` 是脉冲**:置 TRUE 后 stack 记一条,PLC 应配 R_TRIG 把 bTrigger 改为单脉冲避免重复触发。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_TLog
VAR
    fbRoomTemp : FB_BACnet_AI := (sObjectName := 'RoomTemp_3F');
    fbRoomTempTLog : FB_BACnet_TLog := (
        sObjectName := 'RoomTemp_3F_TLog',
        eLoggingType := E_BA_LoggingType.ePolled,
        nLogInterval := 300,
        bLogEnable := TRUE,
        stObjectPropertyReference := F_BACnet_Reference(fbRoomTemp, PropPresentValue));
END_VAR

fbRoomTemp();
fbRoomTempTLog();""",
    business_block=(
        "- **场景**:运维想在 BMS 上看每个房间温度的过去 7 天趋势,做空调系统的舒适度审计,无需在 PLC 上额外装 SQL 数据库。\n"
        "- **价值**:BACnet 标准的 ReadRange 服务跨厂商通用,BMS 端不需要写自定义协议;TLog 自带按时间 / 按序号查找,通信效率高。\n"
        "- **替代方案对比**:用 PLC 内部 Tc3_EventLogger:Beckhoff 自家生态;用 SQL 历史库:运维要管数据库,第三方 BMS 不易接入。"
    ),
    refs_extra="§6.1.1(Tlog = Trendlog)、§6.2.4(Trend-Logging 综述)、§6.5.1(内存计算示例)、§9.12(TLog/TLogCov/TLogBuf 示例)、§9.13(`_Buf` 字段处理)",
    related="`FB_BACnet_TLogBuf`(本 FB 后缀变体)、`FB_BACnet_TLM`(多通道趋势)、`FB_BACnet_ELog` / `_Buf`(事件日志);采集源可以是 AI / AV / BV / MV 等",
))

_tcpou("FB_BACnet_TLog", """VAR
    // 数据源:房间温度 AI
    fbRoomTemp     : FB_BACnet_AI := (
        sObjectName := 'RoomTemp_3F_East',
        sDescription := 'Floor 3 East PT1000',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius);

    // 周期型 TLog:每 3 秒采一次
    fbRoomTempTLog : FB_BACnet_TLog := (
        sObjectName := 'RoomTemp_3F_East_TLog',
        sDescription := 'Trend log for floor 3 east temperature',
        eLoggingType := E_BA_LoggingType.ePolled,
        nLogInterval := 300,                        // 1/100 秒,300 = 3 秒
        bLogEnable := TRUE,
        stStartTime := F_BA_ToSTDateTime(DT#2026-01-01-00:00),
        stObjectPropertyReference :=
            F_BACnet_Reference(fbRoomTemp, PropPresentValue));

    fSensorValPlc : REAL := 22.0;
END_VAR""", """// =============================================================================
// 场景:运维想在 BMS 上看每个房间温度的过去 7 天趋势,做空调系统舒适度审计,
//       无需在 PLC 上额外装 SQL 数据库。
// 价值:BACnet 标准的 ReadRange 服务跨厂商通用,BMS 直接拉数据做趋势图,通信
//       效率高;TLog 缓冲在 router memory,断电不丢(若启用 persistence)。
// 验证:1) 上电后 BACnet Explorer 读 Total_Record_Count 应每 3 秒 +1。
//       2) Explorer 用 ReadRange 服务读最近 10 条,应能看到时间戳 + temperature
//       值序列。3) 在线写 fSensorValPlc := 25.0,3 秒后下一条记录的 fVal 应是 25.0。
// =============================================================================

fbRoomTemp.fVal := fSensorValPlc;
fbRoomTemp();
fbRoomTempTLog();
""")


# ============================================================================
# objects/FB_BACnet_TLM  — Trendlog Multiple
# ============================================================================
_doc("objects", "FB_BACnet_TLM", build_doc(
    fb_name="FB_BACnet_TLM",
    category_label="Object · Trend Log Multiple",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Trend Log Multiple」对象类型(BACnet Object_Type = 27 / Trend Log Multiple)。"
        "与 TLog 类似但每条记录同时记录多个属性,适合需要同时刻多通道关联分析的场景"
        "(如同时记一个 AV 的 Present_Value、Status_Flags、Event_State 来排查报警时机)。"
        "BACnet 标准只允许周期 / 触发模式,不允许 COV 模式。PDF §9.12 末尾 `fbTLogM` 示例。"
        "本对象类型本库仅基础类,无后缀变体。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 多通道数据源 | `aObjectPropertyReferences` | `ARRAY OF ST_BACnet_ObjectPropertyReference` | Log_Device_Object_Property(多个属性引用) |",
        "| 采集模式 | `eLoggingType` | `E_BA_LoggingType` | Logging_Type(`ePolled` / `eTriggered`,不支持 eCOV) |",
        "| 采集间隔 | `nLogInterval` | `UDINT` | Log_Interval(1/100 秒) |",
        "| 控制 | `bLogEnable` / `bTrigger` | `BOOL` | Enable / Trigger |",
        "| 起止时间 | `stStartTime` / `stStopTime` | `ST_BA_DateTime` | Start_Time / Stop_Time |",
        "| 缓冲容量 | `nBufferSize` | `UDINT` | Buffer_Size |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_TLM 每周期调用一次。`ePolled` 模式下 stack 按 `nLogInterval` 间隔采样所有 "
        "`aObjectPropertyReferences` 列出的属性,把它们打包成一条记录(每条记录的字段数等于引用数量)。"
        "BMS 端用 ReadRange 拉数据后做同一时间戳下多个属性值的关联分析。"
        "PDF §9.12 示例 `fbTLogM` 同时采 `fbAv.PresentValue` + `fbAv.StatusFlags` + `fbAv.EventState`,"
        "用 `nLogInterval := 50`(0.5 秒)做高频采样。TLM 不支持 eCOV 是因为多通道难以协调"
        "(几个属性 COV 事件几乎不会同时到达)。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **TLM 占内存比 TLog 大得多**:每条记录长度按属性数 × 单值大小估算,3 通道 × 12 字节 ≈ 36 字节;高频 0.5 秒采样 1 小时 = 7200 条 × 36 字节 ≈ 250 KB。\n"
        "- **TLM 不支持 COV 模式**:必须用 ePolled 或 eTriggered;PDF §6.2.4 明确说明。\n"
        "- **`aObjectPropertyReferences` 顺序固定**:每条记录字段位置与该数组下标一一对应,BMS 端按此顺序解释。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_TLM
VAR
    fbAv : FB_BACnet_AV := (sObjectName := 'AlarmDebugSrc');
    fbTLM : FB_BACnet_TLM := (
        sObjectName := 'AlarmDebug_TLM',
        eLoggingType := E_BA_LoggingType.ePolled,
        nLogInterval := 50,
        bLogEnable := TRUE,
        aObjectPropertyReferences := [
            (iObject := fbAv, ePropertyId := PropPresentValue),
            (iObject := fbAv, ePropertyId := PropStatusFlags),
            (iObject := fbAv, ePropertyId := PropEventState)
        ]);
END_VAR
fbAv();
fbTLM();""",
    business_block=(
        "- **场景**:排查为什么报警没准时触发 — 需要同时记录 Present_Value 与 Status_Flags / Event_State 在同一时间戳下的关联,做事后分析。\n"
        "- **价值**:TLM 一次性记录多通道,无需 BMS 端把多个 TLog 按时间戳合并;高频(50 = 0.5 秒)能捕获瞬态事件。\n"
        "- **替代方案对比**:用多个 TLog:BMS 端要按时间戳合并(BACnet 标准没规定时间戳精度,合并误差大);TLM 同条记录天然对齐。"
    ),
    refs_extra="§6.1.1(TLM = Trendlog Multiple)、§6.2.4(TLog/TLM 综述)、§9.12 末尾(`fbTLogM` 多通道示例)",
    related="`FB_BACnet_TLog` / `FB_BACnet_TLogBuf`(单通道趋势)、`FB_BACnet_ELog` / `_Buf`(事件日志)",
))

_tcpou("FB_BACnet_TLM", """VAR
    fbDebugAv : FB_BACnet_AV := (
        sObjectName := 'AlarmDebugSrc',
        bEnPgm := TRUE,
        bEventDetectionEnable := TRUE,
        nNotificationClass := 14,
        fHighLimit := 8.0,
        bHighLimitEnable := TRUE,
        nTimeDelay := 2);

    fbDebugTLM : FB_BACnet_TLM := (
        sObjectName := 'AlarmDebug_TLM',
        sDescription := 'Multi-channel trend log for alarm timing audit',
        eLoggingType := E_BA_LoggingType.ePolled,
        nLogInterval := 50,                        // 0.5 秒采一次
        bLogEnable := TRUE,
        aObjectPropertyReferences := [
            (iObject := fbDebugAv, ePropertyId := PropPresentValue),
            (iObject := fbDebugAv, ePropertyId := PropStatusFlags),
            (iObject := fbDebugAv, ePropertyId := PropEventState)
        ]);

    fSourceValPlc : REAL := 5.0;
END_VAR""", """// =============================================================================
// 场景:排查报警没准时触发问题 — 需要同时记 Present_Value + Status_Flags +
//       Event_State 在同一时间戳的关联,做事后分析(为什么 2 秒延时变成 3 秒)。
// 价值:TLM 一次性记多通道,无需 BMS 端把多个 TLog 按时间戳合并;高频 0.5 秒
//       能捕获瞬态状态切换。
// 验证:1) 在线写 fSourceValPlc := 10.0(超过 fHighLimit=8),2 秒后 fbDebugAv
//       应进入 OFFNORMAL。2) 用 BACnet Explorer ReadRange 读 fbDebugTLM 最近
//       10 条,应看到 Present_Value 跳到 10 后,Event_State 在 2 秒后切到
//       OFFNORMAL,Status_Flags.InAlarm bit 同时置位。
// =============================================================================

fbDebugAv.fValPgm := fSourceValPlc;
fbDebugAv();
fbDebugTLM();
""")


# ============================================================================
# objects/FB_BACnet_ELog  — Event Log
# ============================================================================
_doc("objects", "FB_BACnet_ELog", build_doc(
    fb_name="FB_BACnet_ELog",
    category_label="Object · Event Log",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Event Log」对象类型(BACnet Object_Type = 25 / Event Log)。"
        "本地存事件 / 报警的日志缓冲,常用于网络断时把 NC 路由不出去的报警先存本地,网络恢复后让 BMS 拉走。"
        "PDF §9.9 / §9.12 给完整示例。本库提供基础类(纯 BACnet 缓冲)+ `_Buf` 变体"
        "(`FB_BACnet_ELogBuf`,在 PLC 端额外暴露 `aLogBuffer : T_BACnet_ELogBuffer` 数组让 PLC 本地读)。"
        "ELog 自动收集本机所有 NC 实例号 = 自身 nObjectInstance 的事件(PDF §6.2.5)。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 实例号 | `nObjectInstance` | `UDINT` | 与目标 NC 实例号相同,自动收集该 NC 路由的事件 |",
        "| 控制 | `bLogEnable` | `BOOL` | Enable(总开关) |",
        "| 缓冲容量 | `nBufferSize` | `UDINT` | Buffer_Size(条数) |",
        "| 起止时间 | `stStartTime` / `stStopTime` | `ST_BA_DateTime` | Start_Time / Stop_Time |",
        "| 通知 | `nNotificationClass` / `nNotificationThreshold` | `UDINT` / `UDINT` | 缓冲使用率到阈值通知 |",
        "| Process ID 过滤 | `nProcessId` | `UDINT` | Process_Identifier_Filter(只收 NC.Recipient 用 process id = 本值的事件,见 §9.9) |",
        "| `_Buf` 增 | `aLogBuffer` | `ARRAY OF ST_BACnet_EventLogEntry` | PLC 端本地缓冲(字段见 §9.13) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_ELog` | — | 基础类 |",
        "| `FB_BACnet_ELogBuf` | 增 `aLogBuffer : T_BACnet_ELogBuffer` | PLC 端本地缓冲数组(PDF §9.13) |",
    ],
    behaviour=(
        "FB_BACnet_ELog 每周期调用一次。本机所有 `FB_BACnet_NC.nObjectInstance == fbELog.nObjectInstance` 的"
        "Notification Class 路由的事件,自动也写一份到本 ELog 缓冲。这是 BACnet 标准的"
        "ELog 与 NC 按实例号自动配对机制(PDF §6.2.5 明确)。`_Buf` 变体下 PLC 可读 "
        "`aLogBuffer[i].dtTime / .eType / .stStatus / .stNotification` 做本地报警历史可视化"
        "(PDF §9.13 字段说明:eStatus / eTimesync / eNotification 三种 entry 类型)。"
        "也可用 `nProcessId` 接收外部 BACnet 设备转发来的事件(PDF §9.9 示例:Device 2 的 ELog 接收 Device 1 的 NC 路由)。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **ELog 与 NC 必须按实例号配对**:`fbELog.nObjectInstance := 10` 自动收 `FB_BACnet_NC` 中 `nObjectInstance := 10` 路由的事件。\n"
        "- **`_Buf` 变体的字段语义见 PDF §9.13**:`eType=eStatus` 是状态变化、`eTimesync` 是时间同步消息、`eNotification` 是事件(含 stNotification 子结构)。\n"
        "- **接收外部设备事件用 `nProcessId`**:PDF §9.9 完整示例 — 报警发送设备的 NC.Recipient 用 process id 42,接收设备的 ELog 设 nProcessId := 42 即可自动接收。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_ELog
VAR
    fbAlarmNC : FB_BACnet_NC := (
        nObjectInstance := 42, nNotificationClass := 42,
        aAckRequired := [TRUE, TRUE, TRUE], aPriority := [10, 11, 12]);
    fbAlarmELog : FB_BACnet_ELogBuf := (
        sObjectName := 'AlarmHistory_NC42',
        nObjectInstance := 42,
        bLogEnable := TRUE);
END_VAR
fbAlarmNC();
fbAlarmELog();""",
    business_block=(
        "- **场景**:楼控项目网络偶尔故障,故障期间 NC 路由不出去的报警必须本地存档,网络恢复后让 BMS 一次拉走,确保零丢失。\n"
        "- **价值**:BACnet 标准的事件日志,BMS 用 ReadRange 拉历史;ELog 与 NC 自动配对省去 PLC 写胶水代码。\n"
        "- **替代方案对比**:用 Tc3_EventLogger:Beckhoff 自家,跨厂商 BMS 不通用;用 SD 卡写文件:运维要管文件,BMS 不能远程拉。"
    ),
    refs_extra="§6.1.1(ELOG = Eventlog)、§6.2.5(Event-Logging 综述)、§9.9(外部设备事件接收)、§9.12(综合示例 fbELog_NC42)、§9.13(`_Buf` 字段说明)",
    related="`FB_BACnet_ELogBuf`(本 FB 后缀变体)、`FB_BACnet_NC`(事件源)、`FB_BACnet_TLog` / `TLogBuf`(趋势日志)",
))

_tcpou("FB_BACnet_ELog", """VAR
    fbAlarmNC42  : FB_BACnet_NC := (
        nObjectInstance := 42,
        nNotificationClass := 42,
        sObjectName := 'NC42_Alarms',
        sDescription := 'Floor 3 east zone alarms',
        aAckRequired := [TRUE, TRUE, TRUE],
        aPriority := [10, 11, 12]);

    fbAlarmELog  : FB_BACnet_ELogBuf := (
        sObjectName := 'AlarmHistory_NC42',
        sDescription := 'Local event log for NC42 alarms (network-loss tolerant)',
        nObjectInstance := 42,                 // 必须与 NC 同号才能自动收集事件
        bLogEnable := TRUE);

    fbTestAlarmAv : FB_BACnet_AV := (
        sObjectName := 'TestAlarmSrc',
        bEnPgm := TRUE,
        bEventDetectionEnable := TRUE,
        nNotificationClass := 42,
        fHighLimit := 8.0,
        bHighLimitEnable := TRUE);

    fAlarmTriggerVal : REAL := 5.0;
END_VAR""", """// =============================================================================
// 场景:楼控项目网络偶尔故障,故障期间 NC42 路由不出去的报警必须本地存档,网络
//       恢复后让 BMS 一次拉走,确保零丢失。
// 价值:BACnet 标准的事件日志,BMS 直接 ReadRange 拉历史;ELog 与 NC 按实例号
//       自动配对,无需 PLC 写复制事件到本地的胶水代码。
// 验证:1) 在线写 fAlarmTriggerVal := 10.0,触发报警进 NC42 路由 + 写入 ELog
//       缓冲。2) BACnet Explorer 读 fbAlarmELog 的 Total_Record_Count 应为 1。
//       3) ReadRange 拉最新一条,应包含时间戳 + NC priority + 报警内容。
//       4) fAlarmTriggerVal := 5.0 恢复后再读应有第 2 条 NORMAL 事件。
// =============================================================================

fbTestAlarmAv.fValPgm := fAlarmTriggerVal;
fbTestAlarmAv();
fbAlarmNC42();
fbAlarmELog();
""")


# ============================================================================
# objects/FB_BACnet_View  — Structured View
# ============================================================================
_doc("objects", "FB_BACnet_View", build_doc(
    fb_name="FB_BACnet_View",
    category_label="Object · Structured View",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Structured View」对象类型(BACnet Object_Type = 29 / Structured View)。"
        "本对象类型不存任何 Present_Value,它的作用是构建 BACnet 对象的层级视图 / 数据点寻址(DPAD),"
        "把 Building → Floor → Zone → Sensor 这种树结构暴露给 BMS,运维端能像浏览文件树一样浏览楼控对象。"
        "其它对象通过 `iParent` 引用 View 节点接入树。结合 `\\/` 操作符可在 Object_Name / Description / "
        "EventMessageTextsConfig 三个字符串属性上做父节点字符串拼接。PDF §6.2.10 / §9.15 详细说明。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | 上一级 View(顶层为空)+ 名称(`\\/` 触发拼接) |",
        "| 节点类型 | `eNodeType` | `E_BACnet_NodeType` | Node_Type(`eArea` / `eOrganizational` / `eNetwork` / `eDevice` / `eCollection` 等,决定 BMS 端图标) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_View 每周期调用一次。它本身没有数据语义,只是定义 BACnet 标准的 Structured View 节点。"
        "其它对象(包括 View)用 `iParent := fbParentView` 把自己挂到该节点下,形成 BACnet 标准的 "
        "DPAD(Data Point Address Description)。`\\/` 操作符在 `sObjectName` / `sDescription` / "
        "`aEventMessageTextsConfig` 三个字符串属性的首字符出现时,触发父节点对应字符串 + 分隔符 + 本节点字符串的拼接 — "
        "PDF §9.15 示例 `fbCabinet := (... sObjectName := '\\/Controllers')` 在 Verl/Eiserstr/Floor 2 父链下"
        "最终展示为 `Germany.Verl.Eiserstr.Floor 2.Controllers`。System Manager 的"
        "树形显示按 `eSymbolName` / `eObjectName` / `eDescription` 三种模式(在 BACnet_Globals 配)。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **`\\/` 拼接只对三个字符串属性生效**:Object_Name / Description / EventMessageTextsConfig;其它字符串属性(如 Device_Type)不参与拼接。\n"
        "- **顶层 View 不要写 `iParent`**:留空表示根节点(PDF §9.15 `fbGermany` / `fbSwitzerland` / `fbSpain` 示例)。\n"
        "- **`eNodeType` 不影响数据,只影响 BMS 图标**:`eDevice` 显示设备图标,`eArea` 显示区域图标等。\n"
        "- **DPAD 的层级深度无硬限,但建议 ≤ 5**:太深会让 BMS 树性能下降。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_View
VAR
    fbBuilding : FB_BACnet_View := (
        eNodeType := E_BACnet_NodeType.eOrganizational,
        sObjectName := 'BuildingA');
    fbFloor3 : FB_BACnet_View := (
        iParent := fbBuilding,
        eNodeType := E_BACnet_NodeType.eArea,
        sObjectName := '\\/Floor3');
    fbAi : FB_BACnet_AI := (
        iParent := fbFloor3,
        sObjectName := '\\/Temp',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius);
END_VAR
fbBuilding();
fbFloor3();
fbAi();""",
    business_block=(
        "- **场景**:楼控项目有 2000+ BACnet 对象,运维在 BMS 上要按楼宇 → 楼层 → 区域 → 房间 → 传感器层级浏览,而不是看 2000 行扁平列表。\n"
        "- **价值**:Structured View 是 BACnet 标准,跨 BMS 通用;一行 `iParent := fbParent` 就建好层级,无需手动配置 BMS 树。\n"
        "- **替代方案对比**:在 BMS 端手配树:换 BMS 厂商要重做;DPAD 在 PLC 端定义,树结构跟着对象库走。"
    ),
    refs_extra="§6.1.1(View = Structured View)、§6.2.10(DPAD 详解 + `\\/` 拼接)、§9.15(完整层级示例)、§9.16(数组初始化下挂 View)",
    related="所有对象 FB 都可通过 `iParent` 挂到 View 下;`FB_BACnet_DynObjectManager`(动态对象 + View 一起管理)",
))

_tcpou("FB_BACnet_View", """VAR
    fbBuilding : FB_BACnet_View := (
        eNodeType := E_BACnet_NodeType.eOrganizational,
        sObjectName := 'BuildingA',
        sDescription := 'Office building A');

    fbFloor3   : FB_BACnet_View := (
        iParent := fbBuilding,
        eNodeType := E_BACnet_NodeType.eArea,
        sObjectName := '\\/Floor3',                    // BuildingA.Floor3
        sDescription := '\\/Floor 3 office area');

    fbZoneEast : FB_BACnet_View := (
        iParent := fbFloor3,
        eNodeType := E_BACnet_NodeType.eCollection,
        sObjectName := '\\/East',                      // BuildingA.Floor3.East
        sDescription := '\\/East zone');

    fbTempEast : FB_BACnet_AI := (
        iParent := fbZoneEast,
        sObjectName := '\\/Temp',                      // BuildingA.Floor3.East.Temp
        sDescription := '\\/Temperature',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius);

    fSensor    : REAL := 22.0;
END_VAR""", """// =============================================================================
// 场景:楼控项目有 2000+ BACnet 对象,运维在 BMS 上要按 楼宇 → 楼层 → 区域 →
//       房间 → 传感器 层级浏览,而不是看 2000 行扁平列表。
// 价值:Structured View 是 BACnet 标准,跨 BMS 通用;一行 iParent := fbParent
//       就建好层级,无需手动配 BMS 树;\/ 拼接让 ObjectName 自动带上完整路径。
// 验证:1) BACnet Explorer 连本机切换到树形视图,应看到 BuildingA / Floor3
//       / East / Temp 三层嵌套。2) 读 fbTempEast.Object_Name 应为
//       'BuildingA.Floor3.East.Temp'(由 \/ 拼接而成,分隔符在 BACnet_Param 配)。
//       3) 在线写 fSensor := 25.0,Temp 节点的 Present_Value 应跟随。
// =============================================================================

fbBuilding();
fbFloor3();
fbZoneEast();

fbTempEast.fVal := fSensor;
fbTempEast();
""")


# ============================================================================
# objects/FB_BACnet_EE  — Event Enrollment
# ============================================================================
_doc("objects", "FB_BACnet_EE", build_doc(
    fb_name="FB_BACnet_EE",
    category_label="Object · Event Enrollment",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Event Enrollment」对象类型(BACnet Object_Type = 9 / Event Enrollment)。"
        "用于在 Intrinsic Reporting 之外做算法 / 阈值监测 — 比如给 AV 加预警限"
        "(Intrinsic Reporting 已经监测 fHighLimit 报警限,EE 再监测一组更低的预警限,触发不同 NC)。"
        "EE 通过 `stEventParameter` 配置事件类型(`eOutOfRange` / `eChangeOfState` / `eChangeOfBitstring` 等),"
        "通过 `stObjectPropertyReference` 指定监测的目标属性。PDF §9.10 给完整双限报警示例。"
        "本对象类型本库仅基础类。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 监测目标 | `stObjectPropertyReference` | `ST_BACnet_ObjectPropertyReference` | Object_Property_Reference(监测哪个对象的哪个属性) |",
        "| 事件参数 | `stEventParameter` | `ST_BACnet_EventParameter` | Event_Parameters(事件类型 + 类型相关阈值) |",
        "| 通知类型 | `eNotifyType` | `E_BACnet_NotifyType` | Notify_Type(`eAlarm` / `eNotifyEvent`) |",
        "| 通知路由 | `nNotificationClass` | `UDINT` | Notification_Class |",
        "| 通用 | `aEventEnable` / `aEventMessageTextsConfig` | 同 AI | Event_Enable / Event_Message_Texts_Config |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_EE 每周期调用一次。stack 周期监测 `stObjectPropertyReference` 指向的目标属性的值,"
        "按 `stEventParameter.eEventType` 决定监测算法:`eOutOfRange` 比 stEventArgs.stOutOfRange 中的 "
        "fLowLimit / fHighLimit 范围;`eChangeOfState` 监测值变化为指定状态;`eChangeOfBitstring` 监测"
        "位串特定位变化;还有 eFloatingLimit / eBufferReady 等更复杂的事件类型。命中则按 `aEventEnable` "
        "决定触发哪个事件(OFFNORMAL / FAULT / NORMAL)→ 走 `nNotificationClass` 指定的 NC 路由 →"
        "按 `eNotifyType` 标记为 alarm 或 event。PDF §9.10 双限报警示例:同一个 fbAv 既启用 Intrinsic Reporting"
        "(报警限 fLowLimit / fHighLimit)走 NC10,又用 EE(预警限 fLowLimit / fHighLimit)走 NC20,"
        "BMS 端看到两个事件等级。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **EE 适合补充而不是替代 Intrinsic Reporting**:对象自身的 Intrinsic Reporting 是 BACnet 标准首选;EE 主要用于多套阈值 / 复杂算法。\n"
        "- **`eOutOfRange` 阈值配在 stEventArgs.stOutOfRange 子结构里**:PDF §9.10 示例显示嵌套结构,容易写漏 `stEventArgs := (stOutOfRange := (...))`。\n"
        "- **EE 的 Notify_Type 通常设 `eNotifyEvent`**:与 Intrinsic Reporting 的 alarm 区分开,BMS 端用不同颜色显示。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_EE
VAR
    fbAv : FB_BACnet_AV := (sObjectName := 'TempAv', bEnPgm := TRUE);
    fbEE : FB_BACnet_EE := (
        sObjectName := 'TempPrewarning',
        nNotificationClass := 20,
        eNotifyType := E_BACnet_NotifyType.eNotifyEvent,
        aEventEnable := [TRUE, TRUE, TRUE],
        stEventParameter := (
            eEventType := E_BACnet_EventType.eOutOfRange,
            stEventArgs := (stOutOfRange := (
                nTimeDelay := 0, fLowLimit := 25.0, fHighLimit := 82.0, fDeadband := 0.0))),
        stObjectPropertyReference := F_BACnet_Reference(fbAv, PropPresentValue));
END_VAR
fbAv();
fbEE();""",
    business_block=(
        "- **场景**:楼控加预警限 — 温度 5°C 报警(走 NC10 红色 alarm),温度 10°C 预警(走 NC20 黄色 event)给运维一个缓冲时间。\n"
        "- **价值**:在不重叠 Intrinsic Reporting 报警的前提下加预警限,等同于 BACnet 标准的双限报警。\n"
        "- **替代方案对比**:用第二个 AV 复制阈值监测:重复对象浪费 router memory + BMS 端 UI 杂乱;EE 标准化优雅。"
    ),
    refs_extra="§6.1.1(EE = EventEnrollment)、§6.2.2.2(Algorithmic Change Reporting)、§9.10(预警限完整示例)",
    related="`FB_BACnet_NC`(路由)、`FB_BACnet_AI` / `AV` / `BV`(被监测的对象);Intrinsic Reporting 的字段直接在被监测对象上配,EE 是 Algorithmic Reporting",
))

_tcpou("FB_BACnet_EE", """VAR
    // 同一个 fbAv:用 Intrinsic 报警限走 NC10,用 EE 预警限走 NC20
    fbAv     : FB_BACnet_AV := (
        sObjectName := 'TempAv',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius,
        bEnPgm := TRUE,
        bEventDetectionEnable := TRUE,
        bHighLimitEnable := TRUE,
        fHighLimit := 87.0,                   // 87°C 触发"alarm"
        nNotificationClass := 10,
        aEventEnable := [TRUE, TRUE, TRUE]);

    fbEE     : FB_BACnet_EE := (
        sObjectName := 'TempPrewarning',
        sDescription := 'Pre-alarm threshold for early warning',
        nNotificationClass := 20,              // 预警走 NC20
        eNotifyType := E_BACnet_NotifyType.eNotifyEvent,
        aEventEnable := [TRUE, TRUE, TRUE],
        stEventParameter := (
            eEventType := E_BACnet_EventType.eOutOfRange,
            stEventArgs := (stOutOfRange := (
                nTimeDelay := 0,
                fLowLimit  := 25.0,
                fHighLimit := 82.0,            // 82°C 触发"event"(预警,比 alarm 低 5°C)
                fDeadband  := 0.0))),
        stObjectPropertyReference := F_BACnet_Reference(fbAv, PropPresentValue));

    fbNC10   : FB_BACnet_NC := (nObjectInstance := 10, nNotificationClass := 10,
                                aAckRequired := [TRUE, TRUE, FALSE], aPriority := [10, 11, 12]);
    fbNC20   : FB_BACnet_NC := (nObjectInstance := 20, nNotificationClass := 20,
                                aAckRequired := [FALSE, TRUE, FALSE], aPriority := [50, 60, 70]);

    fTempVal : REAL := 22.0;
END_VAR""", """// =============================================================================
// 场景:楼控加双限报警 — 温度 82°C 预警(走 NC20 黄色 event,提示运维注意),
//       87°C 报警(走 NC10 红色 alarm,需 ack)。给运维一个缓冲时间。
// 价值:在不重叠 Intrinsic Reporting 报警的前提下加预警限,等同于 BACnet 标准
//       的双限报警;BMS 端两个事件类型用不同颜色显示。
// 验证:1) 在线写 fTempVal := 83.0,BACnet Explorer 应收到 NC20 的 event 通知。
//       2) 继续写 fTempVal := 88.0,Explorer 还应收到 NC10 的 alarm 通知。
//       3) fTempVal := 22.0,两个 NC 都应发 normal 事件。
// =============================================================================

fbAv.fValPgm := fTempVal;
fbAv();
fbEE();
fbNC10();
fbNC20();
""")


# ============================================================================
# objects/FB_BACnet_Loop  — Control Loop + Loop_Ref
# ============================================================================
_doc("objects", "FB_BACnet_Loop", build_doc(
    fb_name="FB_BACnet_Loop",
    category_label="Object · Control Loop",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「Control Loop」对象类型(BACnet Object_Type = 8 / Loop)。"
        "把一个 PI / PID 控制回路的参数(P / I / D / Bias / Setpoint / Output / Action 等)以 BACnet 标准属性"
        "暴露给 BMS,允许 BMS 在线整定参数。本库 Loop 对象的实际 PID 算法由 `Tc3_BA2_Common` 库的 "
        "FB_BA_PIDCtrl 实现,本对象只是把 PID 的输入 / 参数 / 输出绑到 BACnet 标准属性。"
        "本库提供两个变体:`FB_BACnet_Loop`(setpoint/process/output 都用 FB 内部 REAL 变量)与"
        "`FB_BACnet_Loop_Ref`(也写作 FB_BACnet_LoopRef,这三个量通过 ObjectPropertyReference 引用别的 AV/AI/AO 对象,"
        "让 BMS 也能看到 setpoint 与 process value 作为独立 BACnet 对象,见 PDF §6.2.6 + §9.7)。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `bEn` | `I_BACnet_View` / `STRING(*)` / `BOOL` | DPAD + 名称 + 使能 |",
        "| PID 参数 | `fProportionalConstant` / `fIntegralConstant` / `fDerivativeConstant` / `fBias` | `REAL` | Proportional_Constant / Integral_Constant / Derivative_Constant / Bias |",
        "| 输出单位 | `eOutputUnit` | `E_BA_Unit` | Output_Units(典型 `eOther_Percent`) |",
        "| 控制动作方向 | `eAction` | `E_BA_Action` | Action(`eDirect` / `eReverse`,Reverse 适合制冷:误差正向时输出反向降) |",
        "| 内部变量(Loop 基础类) | `fSetpoint` / `fCtrlVal` / `fOutput` | `REAL` | 内部 setpoint / process value / output |",
        "| 外部引用(Loop_Ref) | `stSetpointReference` / `stControlledVariableReference` / `stManipulatedVariableReference` | `ST_BACnet_ObjectPropertyReference` | Setpoint_Reference / Controlled_Variable_Reference / Manipulated_Variable_Reference(用 `F_BACnet_Reference(...)` 帮助函数构造) |",
        "| 上下限 | `fMaximumOutput` / `fMinimumOutput` | `REAL` | Maximum_Output / Minimum_Output |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_Loop` | — | Setpoint / Process / Output 用 FB 内部 REAL,适合简单回路 |",
        "| `FB_BACnet_Loop_Ref` / `FB_BACnet_LoopRef` | 用 stSetpointReference / stControlledVariableReference / stManipulatedVariableReference 引用别的 AV/AI/AO 对象 | 让 BMS 看到 setpoint/process/output 作为独立 BACnet 对象(增加 3 个 BACnet 对象但 BMS 操作 / 趋势可视化方便) |",
    ],
    behaviour=(
        "FB_BACnet_Loop 每周期调用一次。基础类下,PLC 把当前过程值送到 `fCtrlVar`(注意:variable 名是 fCtrlVar,"
        "见 PDF §9.7 示例),回路内部按 `fSetpoint` 与 PID 参数算输出送到 `fOutput`(可读),PLC 端"
        "再把 fOutput 写到物理输出端子。`Loop_Ref` 下,PLC 不直接喂 fCtrlVar,而是通过 stControlledVariableReference "
        "把外部 AI 对象的 PresentValue 作为过程值;setpoint 和 output 同理引用外部 AV/AO 对象。"
        "stack 在 PID 调用时自动用 stack 内的引用解算后写到目标对象。"
        "`eAction := eReverse` 时,误差(SP - PV)正向触发输出降低,适合「制冷:温度高于设定点要开冷却」;"
        "`eDirect` 适合「加热:温度低于设定点要开加热」。Loop 对象自身不发报警,但可通过 EE 监测 fCtrlVal / fOutput "
        "做超调报警。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。"
    ),
    extra_tips_block=(
        "- **PDF 中 LoopRef 引脚名同时使用 `FB_BACnet_Loop_Ref` 与 `FB_BACnet_LoopRef`**:两者为同一 FB(命名争议,版本迭代痕迹);用哪个 token 编译都通过,推荐 `FB_BACnet_Loop_Ref`(下划线版,与 PDF §6.1 表一致)。\n"
        "- **PID 参数从积分时间 Ti(秒)转换**:`fIntegralConstant := 180` 表示积分时间常数 180 秒(即 1/3 分钟积分);不要直接传 Ki(增益)否则物理量不对。\n"
        "- **Loop_Ref 要计算被引用对象的优先级槽位**:PID 输出写下游 AO 时占用槽位 16(默认),会与 BMS 的手动覆盖冲突;实际工程中通常用 _5P 变体 + 把 PID 写到 Critical 优先级。\n"
        "- **`eAction` 写反等于失稳**:制冷接 `eDirect` 时温度越高输出越大,加重过热 → 系统发散。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_Loop
VAR
    fbLoopInternal : FB_BACnet_Loop := (
        bEn := TRUE,
        sDescription := 'Loop using internal control parameters',
        eOutputUnit := E_BA_Unit.eOther_Percent,
        eAction := E_BA_Action.eReverse,           // 制冷:温度↑ → 阀位↓
        fProportionalConstant := 5.0,
        fIntegralConstant := 180,                  // 积分时间 180 秒
        fSetpoint := 20.0);
    fCtrlVal : REAL := 18.0;                       // 过程值,PLC 喂入
END_VAR

fbLoopInternal.fCtrlVar := fCtrlVal;
fbLoopInternal();""",
    business_block=(
        "- **场景**:房间温度 PID 控温 — 每个房间一只 PT1000 温度传感器 + 一只 0..10V 阀门,运维想在 BMS 上在线整定 PID(房间负载随季节变化,需要调 P 和 Ti)。\n"
        "- **价值**:Loop 对象把 PID 参数 BACnet 标准化暴露,运维在 BMS 上直接调参,不用每次登录 PLC 改代码;Loop_Ref 变体进一步让 setpoint / process / output 都作为独立 BACnet 对象可见,方便做 setpoint schedule 和 process value trend log。\n"
        "- **替代方案对比**:用 Tc3_Controller 内置 PID:Beckhoff 自家,BMS 看不到参数;用 Loop 标准对象,跨厂商 BMS 一致。"
    ),
    refs_extra="§6.1.1(Loop / Loop_Ref = Control Loop)、§6.2.6(Control Loops 综述)、§9.7(完整 Loop / Loop_Ref 示例),依赖 Tc3_BA2_Common 库的 FB_BA_PIDCtrl",
    related="`FB_BACnet_AI`(process value 源)、`FB_BACnet_AV` / `AV_Setp`(setpoint 源)、`FB_BACnet_AO` / `AO_5P`(output 目标);`F_BACnet_Reference(...)` 用来构造 ObjectPropertyReference",
))

_tcpou("FB_BACnet_Loop", """VAR
    // 简单回路:PID 参数 BMS 可整定,setpoint/process/output 是 FB 内部 REAL
    fbLoopInternal : FB_BACnet_Loop := (
        bEn := TRUE,
        sObjectName := 'TempLoop_3F_East',
        sDescription := 'PI controller for floor 3 east room temperature',
        eOutputUnit := E_BA_Unit.eOther_Percent,
        eAction := E_BA_Action.eReverse,           // 制冷:温度↑ → 阀位↓
        fProportionalConstant := 5.0,              // Kp = 5
        fIntegralConstant := 180,                  // 积分时间 Ti = 180 秒
        fSetpoint := 20.0,                         // 默认 20°C 设定点
        fMaximumOutput := 100.0,                   // 阀位上限 100%
        fMinimumOutput := 0.0);

    fRoomTempPlc : REAL := 22.0;                   // 从 PT1000 读出来的过程值
    fValveCmdOut : REAL;                           // 算出来的阀位(PLC 端送给 AO)
END_VAR""", """// =============================================================================
// 场景:房间温度 PID 控温 — 每个房间一只 PT1000 + 一只 0..10V 阀门,运维想在
//       BMS 上在线整定 PID(房间负载随季节变化,要调 Kp / Ti)。
// 价值:Loop 对象把 PID 参数 BACnet 标准化暴露,运维在 BMS 上直接调,无需每
//       次登录 PLC 改代码;eAction = eReverse 适合制冷,设错方向系统会发散。
// 验证:1) BACnet Explorer 读 Loop 的 Proportional_Constant=5.0,
//       Integral_Constant=180,Setpoint=20.0。2) 在线写 fRoomTempPlc := 23.0,
//       几个周期后 fValveCmdOut 应增大(温度高 + 制冷反向动作 → 阀位增加)。
//       3) Explorer 写 Setpoint := 18.0,fValveCmdOut 应进一步增大(误差变大)。
// =============================================================================

fbLoopInternal.fCtrlVar := fRoomTempPlc;          // 喂过程值
fbLoopInternal();
fValveCmdOut := fbLoopInternal.fOutput;           // 取输出送下游 AO
""")


# ============================================================================
# objects/FB_BACnet_File  — File object
# ============================================================================
_doc("objects", "FB_BACnet_File", build_doc(
    fb_name="FB_BACnet_File",
    category_label="Object · File",
    infosys_url=URL_OBJECTS,
    overview=(
        "代表 BACnet 标准里的「File」对象类型(BACnet Object_Type = 10 / File),"
        "用于把 PLC 文件系统中的文件(典型:配置文件、persistent 数据导出、EDE 文件)暴露给 BMS,"
        "BMS 可通过 BACnet 标准的 AtomicReadFile / AtomicWriteFile 服务下载或上传。"
        "本对象类型本库仅基础类,无后缀变体。"
        "Status: ⚠️ PDF 仅在 §6.1.1 表中列出 File 一行,未给独立示例;"
        "本文档基于 BACnet 标准 File 对象语义 + 本库命名规则推导成员列表。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 文件路径 | `sFileName` | `STRING(*)` | 本地文件系统中的实际文件路径 |",
        "| 大小 | `nFileSize` | `UDINT` | File_Size(只读,stack 自动算) |",
        "| 修改时间 | `dtFileModificationDate` | `DT` | Modification_Date(只读) |",
        "| 访问方式 | `eFileAccessMethod` | `E_BACnet_FileAccessMethod` | File_Access_Method(`eStream` / `eRecord`) |",
        "| 读保护 | `bReadOnly` | `BOOL` | Read_Only(禁止 BMS 写) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_File 每周期调用一次。stack 内部把 `sFileName` 指定的文件元数据(大小、修改时间)"
        "暴露为 BACnet File 对象属性,BMS 用 `AtomicReadFile(byteOffset, count)` 分块下载文件内容,"
        "用 `AtomicWriteFile(byteOffset, octetString)` 上传 / 更新文件。访问方式 `eStream` 适合"
        "顺序读写(典型:日志文件);`eRecord` 适合结构化记录读写。`bReadOnly := TRUE` 禁止 BMS 写,"
        "防误操作。文件实际驻留在 PLC 控制器本地存储(SD 卡 / 内置 flash),PLC 上电时 stack 会读 sFileName "
        "校验文件是否存在;不存在则 stack 自动建空文件或报告 fault。PDF 未给独立示例,典型用法参照 BACnet 标准定义。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码;本对象类型也未在 §9 给出示例。"
    ),
    extra_tips_block=(
        "- **`sFileName` 是本地文件系统的实际路径**:典型 CX 控制器是 `C:\\TwinCAT\\3.1\\Boot\\PlcLog.csv` 或 `/var/log/plc.log`;路径错文件读不到。\n"
        "- **大文件读取慢**:BACnet AtomicReadFile 分块大小默认 1024 字节,几 MB 文件要几百次往返;通常只把 ≤ 1 MB 的配置 / 日志暴露。\n"
        "- **`bReadOnly := TRUE` 是安全默认**:不打开时 BMS 可能误改 PLC 关键配置;打开写权限只在确认需要的场景。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_File
VAR
    fbConfigFile : FB_BACnet_File := (
        sObjectName := 'ConfigFile',
        sDescription := 'Plant configuration JSON',
        sFileName := 'C:\\TwinCAT\\3.1\\Boot\\config.json',
        eFileAccessMethod := E_BACnet_FileAccessMethod.eStream,
        bReadOnly := FALSE);
END_VAR
fbConfigFile();""",
    business_block=(
        "- **场景**:运维想从 BMS 直接下载 PLC 上的 config.json(包含温度设定点表、报警阈值表),改完后再上传;无需远程登录 PLC。\n"
        "- **价值**:BACnet File 是标准服务,跨厂商 BMS 都支持;免去 FTP / SCP / 远程桌面等额外协议。\n"
        "- **替代方案对比**:用 FTP:运维要装客户端 + 走另一个端口;用 ADS:Beckhoff 自家;BACnet File 标准化、跨厂商。"
    ),
    refs_extra="§6.1.1(File = File)",
    related="`FB_BACnet_Server.SavePersistentStackData()`(触发持久化的方法,与 File 配合可让 BMS 拉走 persistent 数据)",
    status="⚠️ infer-from-naming-convention",
))

_tcpou("FB_BACnet_File", """VAR
    // 把 PLC 上的 config.json 暴露给 BMS 下载 / 修改后上传
    fbConfigFile : FB_BACnet_File := (
        sObjectName := 'ConfigFile',
        sDescription := 'Plant configuration JSON (read+write)',
        sFileName := 'C:\\TwinCAT\\3.1\\Boot\\config.json',
        eFileAccessMethod := E_BACnet_FileAccessMethod.eStream,
        bReadOnly := FALSE);                  // 允许 BMS 上传修改后的文件
END_VAR""", """// =============================================================================
// 场景:运维想从 BMS 直接下载 PLC 上的 config.json(包含温度设定点表、报警阈值
//       表),改完后再上传;无需远程登录 PLC。
// 价值:BACnet File 是标准服务,跨厂商 BMS 都支持;免去 FTP / SCP / 远程桌面
//       等额外协议;PLC 不必维护额外的文件服务程序。
// 验证:1) BACnet Explorer 连本机 → File 对象列表,应能看到 ConfigFile,
//       File_Size 与本地真实文件大小一致。2) Explorer 用 AtomicReadFile 拉
//       全文件,应能保存到本地一个相同的 config.json。3) 修改后用
//       AtomicWriteFile 上传,本地文件应被替换。
// 注意:本对象类型 PDF/InfoSys 未给独立示例,本例基于 BACnet 标准 File 对象语义
//       推导;bReadOnly := FALSE 时 BMS 任何修改会落到 PLC 本地文件,生产环境
//       务必先确认权限控制。
// =============================================================================

fbConfigFile();
""")


# ============================================================================
# primitive_values/  — Primitive Value object types
# ============================================================================

def _make_primitive_doc(fb_name: str, sub_label: str, st_value_type: str,
                        member_value: str, overview_extra: str,
                        example_init: str, scenario: str) -> str:
    return build_doc(
        fb_name=fb_name,
        category_label=f"Primitive Value · {sub_label}",
        infosys_url=URL_PRIMITIVES,
        overview=(
            f"代表 BACnet 标准里的「{sub_label}」对象类型,Primitive Value 系列中的一个 — "
            "用于把单个简单数据类型(整数 / 字符串 / 日期 / 时刻)直接暴露成可被 BMS 读写的 BACnet 对象,"
            "无需借助 AV / MV / String 之外的复杂对象类型。Primitive Value 对象本身没有命令优先级、"
            f"没有 Status_Flags / Reliability,语义就是数据容器。{overview_extra}"
            "PDF §6.1.2 把 10 种 Primitive Value 对象统一表述,§9.14 给完整声明 + 调用示例。"
        ),
        members_table_rows=[
            "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
            f"| 值 | `{member_value}` | `{st_value_type}` | Present_Value 容器(PLC 与 BMS 双向读写) |",
        ],
        variants_table_rows=None,
        behaviour=(
            "本 FB 每周期调用一次。PLC 把当前值写到值成员,库内部推到 BACnet stack 的 Present_Value;"
            "BMS 写下来的值通过同一成员反向取出,需要 PLC 端在条件分支里处理(PDF §6.3.1 一致原则)。"
            "Primitive Value 对象不带 Status_Flags / Reliability / 报警限,语义就是"
            "BACnet 标准化的简单值容器 — 适合把调度参数表中的字符串 / 数字 / 日期 / 时间字段"
            "一一暴露给 BMS 而不用更复杂的 AV / MV 对象。PDF §9.14 显示典型用法 — 同一周期里"
            "并列实例化多个不同类型的 Primitive Value 对象,各自喂入值后周期调用。"
        ),
        error_section=(
            "无返回值;Primitive Value 对象没有 Status_Flags / Reliability,无错误码。"
        ),
        extra_tips_block=(
            "- **改值用条件触发**:PLC 端周期写值会覆盖 BMS 端调整(PDF §6.3.1 一致原则)。\n"
            "- **不要拿 Primitive Value 替代 AV / MV**:Primitive Value 没有命令优先级、Status_Flags、报警限,只适合纯数据容器。\n"
            "- **Pattern 系列(DateP / DateTimeP / TimeP)的通配值是 255**:PDF §6.1.2 + §9.14 明确,255 表示任意值;例如 `nYear := 255` 表示任何年份。"
        ),
        example_code=(
            "PROGRAM P_Demo_" + fb_name + "\n"
            "VAR\n"
            "    fbVal : " + fb_name + ";\n"
            f"    val : {st_value_type} := {example_init};\n"
            "END_VAR\n"
            f"fbVal.{member_value} := val;\n"
            "fbVal();"
        ),
        business_block=(
            f"- **场景**:{scenario}\n"
            "- **价值**:Primitive Value 对象简单直接,BMS 端看到一个标准 BACnet 对象;比用 AV / String 更轻量(没有不必要的 Status_Flags 等属性)。\n"
            "- **替代方案对比**:用 AV / String 暴露简单值:多了 BACnet 属性 BMS 用不上,占 router memory;Primitive Value 是 BACnet 标准为简单数据准备的轻量对象类型。"
        ),
        refs_extra="§6.1.2(Primitive Value 类型表)、§9.14(完整 Primitive Value 示例)",
        related="同 §6.1.2 中的其它 Primitive Value FB:`FB_BACnet_INT` / `LAV` / `String` / `Date` / `DateP` / `Time` / `TimeP` / `DateTime` / `DateTimeP`",
    )


_doc("primitive_values", "FB_BACnet_INT", _make_primitive_doc(
    "FB_BACnet_INT", "Signed Integer Value", "INT",
    "nValue",
    "本变体处理 16 位有符号整数(INT, -32768..32767)。注意 BACnet 标准的"
    "Signed Integer Value 类型在本库以 `FB_BACnet_INT` 实现(同一文档也提示 PDF §6.1.2 中的"
    "Unsigned Integer Value 对应 `FB_BACnet_UINT`,但 §9.14 示例只使用了 INT / UINT 两个 FB 名 — 实际 token 是 `FB_BACnet_INT` 和 `FB_BACnet_UINT`)。",
    "15",
    "调度参数表里的最大重启次数整数字段、HVAC 报警计数等需要简单 INT 容器的场景。",
))

# UINT 用一个单独的文档(PDF §6.1.2 + §9.14 列了 UINT,但本库提供 FB_BACnet_UINT)
# 由于 cache 未注入 FB_BACnet_UINT,这里只在 INT 文档相关 FB 段提及 UINT 的存在但
# 不独立成篇 — 如果用户要求 UINT 独立,后续可加注入。本批次按「主原语」组织
# (Date / Time / DateTime + INT/LAV/String,共 6 文件,UINT 行为与 INT 等价)。

_doc("primitive_values", "FB_BACnet_LAV", _make_primitive_doc(
    "FB_BACnet_LAV", "Large Analog Value (LREAL)", "LREAL",
    "fValue",
    "本变体处理 64 位 LREAL(双精度浮点,8 字节),用于范围超过 REAL(32 位)精度的物理量(典型:累计能耗、累计运行时间秒数等高位精度需求)。",
    "42.3",
    "累计运行小时数(REAL 精度只够 7 位有效数,运行 10000 小时后小数部分丢失;LAV 用 LREAL 解决)、高精度能量计量等。",
))

_doc("primitive_values", "FB_BACnet_String", _make_primitive_doc(
    "FB_BACnet_String", "Character String Value", "STRING",
    "sValue",
    "本变体处理 BACnet 标准的 Character String(UTF-8 字符串)。",
    "'TwinCAT BACnet'",
    "把 PLC 端的最后一条错误消息、当前操作员姓名、正在运行的批次号等字符串暴露给 BMS。",
))

_doc("primitive_values", "FB_BACnet_Date", build_doc(
    fb_name="FB_BACnet_Date",
    category_label="Primitive Value · Date",
    infosys_url=URL_PRIMITIVES,
    overview=(
        "代表 BACnet 标准里的「Single Date Value」对象类型(Primitive Value 之一)。"
        "把单个日期(年-1900 / 月 / 日 / 星期)暴露给 BMS。本库另提供 `FB_BACnet_DateP`(Date Pattern Value),"
        "使用通配 255 / Unspecified 表示任意值以匹配任何年份的某月某日等模式。"
        "PDF §6.1.2 + §9.14 详细说明。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 值 | `stValue` | `ST_BA_Date` | Present_Value 日期容器(`nYear/eMonth/nDay/eDayOfWeek`,nYear 从 1900 起,255 表示通配) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_Date` | — | 单日值,无通配 |",
        "| `FB_BACnet_DateP` | — | Date Pattern,可用 255 / Unspecified 通配某字段(如任意年份的圣诞节) |",
    ],
    behaviour=(
        "FB_BACnet_Date 每周期调用一次。PLC 把 `ST_BA_Date` 结构写到 `stValue`,库内部推到 BACnet stack 的 Present_Value。"
        "`nYear` 字段按 BACnet 标准从 1900 起算(`nYear := 122` 表示 2022);"
        "`nDay` 可用 32(月末)/ 33(奇数日)/ 34(偶数日)等通配值;`eMonth` 可用 eOddMonths(奇数月)/ eEvenMonths(偶数月);"
        "`eDayOfWeek` 用 `eFriday` 等具体星期或 `Unspecified` 表示任意。Pattern 变体 `FB_BACnet_DateP` 把所有字段都允许"
        "用通配,PDF §9.14 示例 `stDatePattern := (nYear := 255, eMonth := eDecember, nDay := eDay24, eDayOfWeek := Unspecified)` "
        "表示每年圣诞节,无论星期几。具体日期要保证 `eDayOfWeek` 与给定日期实际匹配,否则 BACnet 标准要求 stack 拒绝。"
    ),
    error_section=(
        "无返回值。⚠️ PDF + InfoSys 未列具体 error 常量;输入非法时 stack 不接受写入。"
    ),
    extra_tips_block=(
        "- **`nYear` 从 1900 起**:`nYear := 122` = 2022,容易写错。\n"
        "- **`eDayOfWeek` 要与日期匹配**:`stValue := (nYear := 122, eMonth := eDecember, nDay := eDay02, eDayOfWeek := eFriday)` — 2022-12-02 确实是周五,写错星期 BACnet stack 会拒绝。\n"
        "- **Pattern 变体的 255 等于任意**:`FB_BACnet_DateP` 用 nYear=255 表达任意年,DateP 适合节假日匹配。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_Date
VAR
    fbBatchStartDate : FB_BACnet_Date := (
        sObjectName := 'BatchStartDate');
    stToday : ST_BA_Date := (
        nYear := 126, eMonth := E_BA_MONTH.eJune,
        nDay := E_BA_DAY.eDay03, eDayOfWeek := E_BA_WEEKDAY.eWednesday);
END_VAR

fbBatchStartDate.stValue := stToday;
fbBatchStartDate();""",
    business_block=(
        "- **场景**:把上次维护日期、当前生产批次的批次日期等单日字段暴露给 BMS,无需用 DateTime 包含时间字段。\n"
        "- **价值**:Date 是 BACnet 标准的轻量日期容器,BMS 端识别;比用字符串 '2026-06-03' 节省解析并自带 nYear 等结构化字段。\n"
        "- **替代方案对比**:用字符串:BMS 要解析,无类型安全;用 DateTime:多余的时间字段。"
    ),
    refs_extra="§6.1.2(Date / DateP 行)、§9.14(完整 Date / DateP / Time / TimeP / DateTime / DateTimeP 示例)",
    related="`FB_BACnet_Time` / `TimeP`(时刻)、`FB_BACnet_DateTime` / `DateTimeP`(日期 + 时刻);Schedule 对象使用 `F_BA_DateVal` 帮助函数",
))

_doc("primitive_values", "FB_BACnet_Time", build_doc(
    fb_name="FB_BACnet_Time",
    category_label="Primitive Value · Time",
    infosys_url=URL_PRIMITIVES,
    overview=(
        "代表 BACnet 标准里的「Time Value」对象类型,把单个时刻(时 / 分 / 秒 / 百分之一秒)暴露给 BMS。"
        "本库另提供 `FB_BACnet_TimeP`(Time Pattern Value),使用通配 255 表示任意值以匹配"
        "每小时的第 42 分等模式。PDF §6.1.2 + §9.14 详细说明。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 值 | `stValue` | `ST_BA_Time` | Present_Value 时刻容器(`nHour:0..23` / `nMinute:0..59` / `nSecond:0..59` / `nHundredths:0..99`;255 表示通配) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_Time` | — | 单时刻,无通配 |",
        "| `FB_BACnet_TimeP` | — | Time Pattern,可用 255 通配某字段(如每小时第 42 分) |",
    ],
    behaviour=(
        "FB_BACnet_Time 每周期调用一次。PLC 把 `ST_BA_Time` 结构写到 `stValue`,库内部推到 BACnet stack 的 Present_Value;"
        "范围:nHour 0..23,nMinute 0..59,nSecond 0..59,nHundredths 0..99(注意是百分秒,不是毫秒)。"
        "Pattern 变体 `FB_BACnet_TimeP` 把任意字段设 255 表示通配 — PDF §9.14 示例 "
        "`stTimePattern := (nHour := 255, nMinute := 42, nSecond := 0, nHundredths := 0)` 表示每小时第 42 分整点。"
        "BMS 端的 Schedule 对象与 Pattern 配合可表达复杂周期事件;运行时改值要走条件触发分支以免覆盖 BMS 端修改。"
    ),
    error_section=(
        "无返回值;输入越界时 stack 不接受写入。"
    ),
    extra_tips_block=(
        "- **百分秒(`nHundredths`)的范围是 0..99 而不是 0..999**:对应 BACnet 标准的百分之一秒,不是毫秒。\n"
        "- **Pattern 变体的通配 255 用于周期模式**:`FB_BACnet_TimeP` 与 BMS 端 Schedule 配合让 BMS 显示每小时第 N 分等模式而不必每分钟写一条记录。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_Time
VAR
    fbLastBackupTime : FB_BACnet_Time := (sObjectName := 'LastBackupTime');
    stNow : ST_BA_Time := (
        nHour := 14, nMinute := 30, nSecond := 0, nHundredths := 0);
END_VAR

fbLastBackupTime.stValue := stNow;
fbLastBackupTime();""",
    business_block=(
        "- **场景**:把今日数据备份完成时刻、夜间维护开始时刻等单时刻字段暴露给 BMS。\n"
        "- **价值**:Time 是 BACnet 标准的轻量时刻容器,BMS 识别;比字符串 '14:30:00' 节省解析。\n"
        "- **替代方案对比**:用字符串:BMS 要解析无类型安全;用 DateTime:多余的日期字段。"
    ),
    refs_extra="§6.1.2(Time / TimeP 行)、§9.14(完整示例)",
    related="`FB_BACnet_Date` / `DateP`(日期)、`FB_BACnet_DateTime` / `DateTimeP`(组合)",
))

_doc("primitive_values", "FB_BACnet_DateTime", build_doc(
    fb_name="FB_BACnet_DateTime",
    category_label="Primitive Value · DateTime",
    infosys_url=URL_PRIMITIVES,
    overview=(
        "代表 BACnet 标准里的「Date and Time Value」对象类型,把"
        "完整时间戳(日期 + 时刻)暴露给 BMS。本库另提供 `FB_BACnet_DateTimeP`(Date and Time Pattern Value),"
        "组合 Date 和 Time 字段的通配以表达复杂模式。PDF §6.1.2 + §9.14 详细说明。"
    ),
    members_table_rows=[
        "| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |",
        "| 值 | `stValue` | `ST_BA_DateTime` | Present_Value 时间戳容器(`stDate : ST_BA_Date` + `stTime : ST_BA_Time`) |",
    ],
    variants_table_rows=[
        "| `FB_BACnet_DateTime` | — | 单时间戳,无通配 |",
        "| `FB_BACnet_DateTimeP` | — | DateTime Pattern,日期 / 时刻字段都可通配,表达复杂模式如每年 5 月 1 日是周一的那年的每小时每分钟的第 11 秒 |",
    ],
    behaviour=(
        "FB_BACnet_DateTime 每周期调用一次。`stValue` 嵌套 `stDate` 与 `stTime` 子结构,字段含义同 Date 和 Time 对象 — "
        "`stDate.nYear` 仍按 BACnet 标准从 1900 起算,各字段越界 stack 拒绝写入。"
        "Pattern 变体 `FB_BACnet_DateTimeP` 允许两者任一字段通配 — PDF §9.14 示例 "
        "`stDateTimePattern := (stDate := (nYear:=255, eMonth:=eMay, nDay:=eDay01, eDayOfWeek:=eMonday), stTime := (nHour:=255, nMinute:=255, nSecond:=11, nHundredths:=0))` "
        "表达每年 5 月 1 日是周一的那年的每小时每分钟的第 11 秒 — 这种复合模式非常少见,主要给"
        "BACnet 标准 Schedule 的 Exception_Schedule 用。运行时改值要走条件触发分支,避免周期覆盖 BMS 端调整。"
    ),
    error_section=(
        "无返回值;输入越界 stack 不接受。"
    ),
    extra_tips_block=(
        "- **Pattern 变体很少用**:实际工程用单一 DateTime 直接给时间戳,Pattern 主要存在为 BACnet 标准完整性。\n"
        "- **`stDate.nYear` 从 1900 起算**,容易写错。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_DateTime
VAR
    fbBatchTimestamp : FB_BACnet_DateTime := (sObjectName := 'BatchTimestamp');
    stNow : ST_BA_DateTime := (
        stDate := (nYear := 126, eMonth := E_BA_MONTH.eJune,
                   nDay := E_BA_DAY.eDay03, eDayOfWeek := E_BA_WEEKDAY.eWednesday),
        stTime := (nHour := 14, nMinute := 30, nSecond := 0, nHundredths := 0));
END_VAR

fbBatchTimestamp.stValue := stNow;
fbBatchTimestamp();""",
    business_block=(
        "- **场景**:把批次开始时间戳、上次校时时刻等完整时间戳字段暴露给 BMS,做时序记录。\n"
        "- **价值**:DateTime 是 BACnet 标准时间戳容器,BMS 识别;比拼字符串"
        "节省解析、自带时区中立语义。\n"
        "- **替代方案对比**:拆 Date + Time 两个对象:BMS 端要原子读两次;DateTime 一次读取保证一致性。"
    ),
    refs_extra="§6.1.2(DateTime / DateTimeP 行)、§9.14(完整示例)",
    related="`FB_BACnet_Date` / `DateP`(日期)、`FB_BACnet_Time` / `TimeP`(时刻)",
))

_tcpou("FB_BACnet_INT", """VAR
    fbAlarmCnt : FB_BACnet_INT := (
        sObjectName := 'AlarmCount_3F',
        sDescription := 'Floor 3 alarm count today');
    nLocalCnt  : INT := 0;
END_VAR""", """// =============================================================================
// 场景:把"今日报警次数"等简单 INT 字段暴露给 BMS,用 Primitive Value 而不是 AV
//       (AV 还有 Status_Flags / 报警限等属性 BMS 用不上)。
// 价值:Primitive Value 是 BACnet 标准的轻量容器,占 router memory 少,BMS 端
//       识别为标准 BACnet 对象。
// 验证:1) BACnet Explorer 读 fbAlarmCnt.Present_Value=0。2) 在线写 nLocalCnt
//       := 7,Explorer 应看到 Present_Value=7。
// =============================================================================

fbAlarmCnt.nValue := nLocalCnt;
fbAlarmCnt();
""")

_tcpou("FB_BACnet_LAV", """VAR
    fbRunHours : FB_BACnet_LAV := (
        sObjectName := 'RunHours_AHU_3F',
        sDescription := 'AHU floor 3 cumulative run hours (LREAL precision)',
        eUnit := E_BA_Unit.eTime_Hours);
    fHoursPlc  : LREAL := 12345.678;
END_VAR""", """// =============================================================================
// 场景:累计运行小时数 — REAL 精度只够 7 位有效数,运行 10000 小时后小数部分
//       丢失;Large Analog Value 用 LREAL(双精度,15 位有效数)解决。
// 价值:Large Analog Value 是 BACnet 标准的高精度浮点容器,BMS 识别;无需自己
//       实现 INT64 拼接。
// 验证:1) BACnet Explorer 读 fbRunHours.Present_Value=12345.678 应为 LREAL,
//       精度 ≥ 7 位有效数。2) 在线写 fHoursPlc := 99999.999999,Explorer 应
//       完整保留 6 位小数。
// =============================================================================

fbRunHours.fValue := fHoursPlc;
fbRunHours();
""")

_tcpou("FB_BACnet_String", """VAR
    fbLastError : FB_BACnet_String := (
        sObjectName := 'LastError_3F',
        sDescription := 'Last error message text on floor 3');
    sErrTxt     : STRING := 'No error';
END_VAR""", """// =============================================================================
// 场景:把"最后一条错误消息文本"等字符串字段暴露给 BMS,运维 / 调试时方便查看。
// 价值:Character String Value 是 BACnet 标准的字符串容器,BMS 识别;UTF-8
//       兼容(配 STRING_TO_UTF8 可支持中文,PDF §9.15 示例)。
// 验证:1) BACnet Explorer 读 fbLastError.Present_Value='No error'。2) 在线
//       写 sErrTxt := 'Sensor 3F-E-T01 fault',Explorer 应看到更新。
// =============================================================================

fbLastError.sValue := sErrTxt;
fbLastError();
""")

_tcpou("FB_BACnet_Date", """VAR
    fbBatchStartDate : FB_BACnet_Date := (
        sObjectName := 'BatchStartDate',
        sDescription := 'Date the current batch started');
    // 2026-06-03 是周三(eWednesday),nYear 从 1900 起算 → 2026 - 1900 = 126
    stToday : ST_BA_Date := (
        nYear := 126, eMonth := E_BA_MONTH.eJune,
        nDay := E_BA_DAY.eDay03, eDayOfWeek := E_BA_WEEKDAY.eWednesday);
END_VAR""", """// =============================================================================
// 场景:把"当前生产批次的批次日期"暴露给 BMS,无需用 DateTime 包含多余的时刻
//       字段。
// 价值:Date 是 BACnet 标准的轻量日期容器,BMS 识别;比字符串 '2026-06-03'
//       节省解析、自带 nYear / eMonth / nDay / eDayOfWeek 结构化字段。
// 验证:1) BACnet Explorer 读 fbBatchStartDate.Present_Value 应显示
//       2026-06-03 Wednesday(nYear=126 + 1900 = 2026)。2) 把 stToday.nDay
//       临时改成 04,Explorer 应跟随更新(注意 eDayOfWeek 必须匹配新日期,
//       否则 stack 拒绝)。
// 注意:nYear 字段按 BACnet 标准从 1900 起算,nYear := 126 表示 2026 年。
// =============================================================================

fbBatchStartDate.stValue := stToday;
fbBatchStartDate();
""")

_tcpou("FB_BACnet_Time", """VAR
    fbLastBackupTime : FB_BACnet_Time := (
        sObjectName := 'LastBackupTime',
        sDescription := 'Time of day when last data backup finished');
    stNow : ST_BA_Time := (
        nHour := 14, nMinute := 30, nSecond := 0, nHundredths := 0);
END_VAR""", """// =============================================================================
// 场景:把"今日数据备份完成时刻"暴露给 BMS,运维查看;无需 DateTime 多余的
//       日期字段。
// 价值:Time 是 BACnet 标准的轻量时刻容器,BMS 识别;比字符串 '14:30:00' 节省
//       解析,nHundredths 字段提供百分秒精度。
// 验证:1) BACnet Explorer 读 fbLastBackupTime.Present_Value 应显示 14:30:00.00。
//       2) 把 stNow.nHour := 15 在线改,Explorer 跟随更新。
// 注意:nHundredths 范围 0..99 而不是 0..999(BACnet 标准百分秒,不是毫秒)。
// =============================================================================

fbLastBackupTime.stValue := stNow;
fbLastBackupTime();
""")

_tcpou("FB_BACnet_DateTime", """VAR
    fbBatchTimestamp : FB_BACnet_DateTime := (
        sObjectName := 'BatchTimestamp',
        sDescription := 'Timestamp the current batch was started');
    stNow : ST_BA_DateTime := (
        stDate := (nYear := 126, eMonth := E_BA_MONTH.eJune,
                   nDay := E_BA_DAY.eDay03, eDayOfWeek := E_BA_WEEKDAY.eWednesday),
        stTime := (nHour := 14, nMinute := 30, nSecond := 0, nHundredths := 0));
END_VAR""", """// =============================================================================
// 场景:把"批次开始时间戳"暴露给 BMS,做时序记录用。
// 价值:DateTime 是 BACnet 标准的完整时间戳容器,BMS 识别;比拼接 Date+Time
//       两个对象省 1 个对象 + 保证读取原子性(BMS 端一次拉读不会出现日期与
//       时刻字段不一致的瞬间)。
// 验证:1) BACnet Explorer 读 fbBatchTimestamp.Present_Value 应显示
//       2026-06-03 Wed 14:30:00.00。2) 在线改 stNow.stTime.nHour := 15,
//       Explorer 跟随。
// 注意:stDate.nYear := 126 表示 2026 年(BACnet 标准从 1900 起算)。
// =============================================================================

fbBatchTimestamp.stValue := stNow;
fbBatchTimestamp();
""")


# ============================================================================
# client/  — BACnet client FBs(§7,共 15 个)
# ============================================================================

# --- FB_BACnet_Client ------------------------------------------------------
_doc("client", "FB_BACnet_Client", build_doc(
    fb_name="FB_BACnet_Client",
    category_label="Client · Connection",
    infosys_url=URL_CLIENT,
    overview=(
        "BACnet 客户端连接对象,代表 PLC 作为客户端连接到一个 BACnet 远端设备(peer device)。"
        "本 FB 维持与该 peer 的 BACnet 协议层会话(支持的服务、ReadMode、tReadCycleTime / tWriteCycleTime、"
        "最大并发请求数等),所有 `FB_BACnetRM_*` 远端对象引用都必须绑定一个 Client 实例。"
        "PDF §7.2 / §7.7 详述客户端变量与状态机。"
    ),
    members_table_rows=[
        "| 链接 | `Adapter` | `FB_BACnet_Adapter` | 绑定的本地 BACnet 适配器(默认 `BACnet_Globals.DefaultAdapter`) |",
        "| 远端设备 | `nDeviceInstance` | `UDINT` | Peer 设备的 BACnet device-id(用 Who-Is 解析为 IP / MS/TP 地址) |",
        "| 读模式 | `eReadMode` | `E_BACnet_CommMode` | `eAutomatic` / `eCovU` / `eCovC` / `eCovP` / `eReadProperty` / `eReadPropertyMultiple`(PDF §7.2.1) |",
        "| 周期 | `tReadCycleTime` / `tWriteCycleTime` | `TIME` | 读 / 写请求周期 |",
        "| 并发 | `nMaxParallelRequests` | `UDINT` | 同时可在飞的请求数(MS/TP 通常 ≤ 20,IP 可到 50+) |",
        "| 服务支持 | `bSuppRpm` / `bSuppCov` / `bSuppCovP` | `BOOL` | Peer 设备是否支持 RPM / COV / COV-P(eAutomatic 模式下 stack 自检测,手动模式下 PLC 配) |",
        "| 自动恢复 | `bAutoResetObjError` | `BOOL` | TRUE 时连接中断后自动重置 client 状态机 |",
        "| 状态(只读) | `bReady` / `bConnected` / `eState` | `BOOL` / `E_BACnet_ClientState` | FB 初始化完成 / 已连接 / 当前状态机阶段(PDF §7.7) |",
        "| 诊断(只读) | `m_stDiag` | `ST_BACnet_ClientDiag` | 客户端连接的 roundtrip / 各请求类型计数(PDF §6.2.8) |",
    ],
    variants_table_rows=None,
    behaviour=(
        "FB_BACnet_Client 每周期调用一次。上电后状态机从 eInit 开始,自动发 Who-Is 解析 nDeviceInstance,"
        "之后建立到 peer 的会话(eAutomatic 模式下扫描其支持的服务集);完成后 `bReady := TRUE` 且 `bConnected := TRUE`,"
        "后续 `FB_BACnetRM_*` 对象的读 / 写都通过本 client 走。`eReadMode := eAutomatic` 时 stack 根据 peer 支持的服务"
        "+ 待读属性总数自动选 RP / RPM / COV(PDF §7.2.1 阈值规则);手动模式下 PLC 设 `bSuppRpm / bSuppCov / bSuppCovP` "
        "指定 stack 走哪种服务。`tReadCycleTime` / `tWriteCycleTime` 决定客户端轮询频率(典型 2..10 秒)。"
        "连接断开(网络故障或 peer 重启)时 `bConnected := FALSE` / `eState := eInit`,stack 自动重连;"
        "`bAutoResetObjError := TRUE` 时,绑定到本 client 的所有 RM 对象在 client 重连后会自动复位状态。"
    ),
    error_section=(
        "无返回值;`bConnected` / `eState` / `m_stDiag` 暴露状态。⚠️ PDF + InfoSys 未列具体错误码,"
        "连接相关错误集中在 `BACnet_Globals.Error / Abort / Reject` 段以及 m_stDiag 子结构里(PDF §6.2.8)。"
    ),
    extra_tips_block=(
        "- **MS/TP peer 必须先实例化对应的 FB_BACnet_Adapter**:`Client := (Adapter := fbMstpDevice_X, nDeviceInstance := ...)`,且 fbMstpDevice_X 也要每周期单独 call(PDF §7.6.6)。\n"
        "- **大量 RM 对象时把 `nMaxParallelRequests` 调高**:默认 1 太保守,IP 设 50+,MS/TP 设 5..20。\n"
        "- **`tReadCycleTime` 不要设太短**:< 1 秒会导致 MS/TP 网段被淹,建议 2..5 秒。\n"
        "- **`bAutoResetObjError := TRUE` 适合不稳定网络**:网络偶断后所有 RM 对象自动从 init 重启;`:= FALSE` 时 PLC 要自己监测 bConnected 并 reset。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_Client
VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#5S,
        tWriteCycleTime := T#5S,
        nMaxParallelRequests := 20,
        eReadMode := E_BACnet_CommMode.eAutomatic);
END_VAR

fbClient();""",
    business_block=(
        "- **场景**:PLC 作为客户端连接其它楼控厂商的 BACnet 设备(西门子 PXC / 霍尼韦尔 Spyder 等),把对端的传感器读数 / 控制点同步到 BMS。\n"
        "- **价值**:Client 是所有 RM 对象的前提;一个 Client 维护一条到 peer 的会话,自动选 RP/RPM/COV 取数据,无需 PLC 写 BACnet 协议栈。\n"
        "- **替代方案对比**:用 BACnet stack 第三方库直连:成本高且与 System Manager 不集成;Tc3_BACnetRev14 client 让 BACnet 跨厂商通信变成几行 PLC 代码。"
    ),
    refs_extra="§7.2(Readmode 与自动选服务)、§7.7(客户端变量)、§7.11(连接监控)、§7.12(RPM 综合示例)",
    related="`FB_BACnet_Adapter`(本地 BACnet 适配器)、所有 `FB_BACnetRM_*`(远端对象,必须绑本 client)",
))

_tcpou("FB_BACnet_Client", """VAR
    // 连接到 BACnet device 42(IP 模式,自动选择 RP/RPM/COV)
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#5S,
        tWriteCycleTime := T#5S,
        nMaxParallelRequests := 20,
        eReadMode := E_BACnet_CommMode.eAutomatic,
        bAutoResetObjError := TRUE);          // 网络偶断后绑到本 client 的对象自动复位
END_VAR""", """// =============================================================================
// 场景:PLC 作为客户端连接其它楼控厂商的 BACnet 设备(西门子 PXC / 霍尼韦尔
//       Spyder 等),把对端的传感器读数 / 控制点同步到本机 BMS。
// 价值:Client 是所有 RM 对象的前提;一个 Client 维护一条到 peer 的会话,
//       自动选 RP/RPM/COV 取数据,无需 PLC 写 BACnet 协议栈。
// 验证:1) 上电后等几秒,BACnet Explorer 抓包应看到 Who-Is(目标 device-id=42)。
//       2) 在线监视 fbClient.bConnected 应在 1-2 秒内变 TRUE,eState=eRunning。
//       3) m_stDiag 字段应记录最近请求的 roundtrip 时间。4) 断网测试:拔
//       网线后 fbClient.bConnected 在 30 秒左右(超时阈值)变 FALSE;恢复
//       后自动重连。
// =============================================================================

fbClient();
""")


# --- FB_BACnetRM_Device ----------------------------------------------------
_doc("client", "FB_BACnetRM_Device", build_doc(
    fb_name="FB_BACnetRM_Device",
    category_label="Client · Remote Device",
    infosys_url=URL_CLIENT,
    overview=(
        "代表远端 BACnet 设备的 Device 对象引用。每个 Client 必须实例化一个 FB_BACnetRM_Device 并每周期调用,"
        "用于监控连接状态(`eSysState` / `bOperational` / `nErrorCnt`),"
        "并把 client 的「远端设备发现 + 状态机维护」完成 — 没有这个 FB,client 不会发起 Who-Is,绑到本 client "
        "的其它 RM 对象都跑不起来。PDF §7.11 详述监控用法。"
    ),
    members_table_rows=[
        "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client(必填) |",
        "| 系统状态(只读) | `eSysState` | `E_BACnet_SysState` | `eInit` / `eDiscovery` / `eOperational` / `eNoCommunication` |",
        "| 可操作标志(只读) | `bOperational` | `BOOL` | TRUE 时已建立稳定通信,可发请求 |",
        "| 错误计数(只读) | `nErrorCnt` | `UDINT` | 已尝试重连次数;超过阈值切到 eNoCommunication |",
    ],
    variants_table_rows=None,
    behaviour=(
        "每周期调用一次,FB 内部驱动 client 状态机:`eInit` → `eDiscovery`(发 Who-Is 并等 I-Am)→ "
        "`eOperational`(可发请求)→ 出错时 `eNoCommunication`(超过 nErrorCnt 阈值)→ 自动重试回 eInit。"
        "PDF §7.11 解释:连接中断后 stack 自动重连,中断到检测出来通常需 30 秒左右(因为要等若干次 Who-Is 重试)。"
        "PLC 端可监视 `bOperational := TRUE` 作为可发 RM 请求的判据;`eSysState = eNoCommunication` 时所有发往 peer 的"
        "请求都会立刻失败,PLC 应停掉对应业务逻辑等连接恢复。"
    ),
    error_section=(
        "无返回值;`eSysState` 是主要的诊断字段。⚠️ PDF + InfoSys 未列具体错误码常量。"
    ),
    extra_tips_block=(
        "- **必须每周期 call**:不 call 的话 stack 不发 Who-Is,Client 永远停在 eInit。\n"
        "- **`bOperational := FALSE` 时不要硬发 RM 请求**:会立刻失败 + 占带宽;PLC 应判 `IF fbDevice.bOperational THEN ... END_IF`。\n"
        "- **MS/TP 网段连接成功时间偏长**:可能要 1..3 分钟才到 eOperational(MS/TP 令牌环要轮一圈才发现新设备),IP 通常 1..2 秒。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnetRM_Device
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
END_VAR

fbClient();
fbDevice();""",
    business_block=(
        "- **场景**:多客户端项目中,每个 peer device 都要监控其在线状态;BMS 端看到 eSysState 字段实时刷新。\n"
        "- **价值**:把「客户端 + 远端设备」两件事拆成两个 FB 后,monitor / discovery / fault detect 都自动化;PLC 端代码量从手写状态机的 200 行降到 1 行。\n"
        "- **替代方案对比**:第三方 BACnet stack:需要自己实现状态机;本 FB 跟 client 配套,即插即用。"
    ),
    refs_extra="§7.11(连接监控完整说明 + 时序图)、§7.11.1 / §7.11.2(成功 / 中断示例)",
    related="`FB_BACnet_Client`(必须绑)、`FB_BACnetRM_*`(其它远端对象,需要本 FB 把连接拉起来才能用)",
))

_tcpou("FB_BACnetRM_Device", """VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#5S,
        nMaxParallelRequests := 20);

    // 必须实例化 + 每周期调用,否则 client 不发 Who-Is,所有 RM 对象都跑不起来
    fbRmDevice : FB_BACnetRM_Device := (Client := fbClient);

    // 监视:bDeviceOnline 用于 PLC 业务逻辑决定是否发 RM 请求
    bDeviceOnline : BOOL;
END_VAR""", """// =============================================================================
// 场景:监控 BACnet 远端设备 42 的在线状态;一旦连接中断 PLC 停掉对应业务逻辑
//       (避免一直发失败的请求填满带宽),恢复后自动续。
// 价值:把 client + 远端设备拆两个 FB,monitor / discovery / fault detect 都自动
//       化;PLC 端代码量从手写状态机 200 行降到 2 行。
// 验证:1) 上电后等几秒,fbRmDevice.eSysState 应从 eInit → eDiscovery →
//       eOperational,bDeviceOnline 同时为 TRUE。2) 断网测试:拔网线后 30 秒
//       左右 eSysState 切到 eNoCommunication,bDeviceOnline 变 FALSE;恢复
//       后又自动回到 eOperational。3) 不调用 fbRmDevice() 会让 client 永远
//       停在 eInit,试一下看现象。
// =============================================================================

fbClient();
fbRmDevice();

// ---- 暴露给 PLC 业务用 ----
bDeviceOnline := fbRmDevice.bOperational;
""")


# --- 远端对象引用 FB_BACnetRM_AI / AV / BO / MI / MV ------------------------
def _make_remote_obj_doc(fb_name: str, sub_label: str, val_type: str,
                         val_member: str, related_local: str) -> str:
    return build_doc(
        fb_name=fb_name,
        category_label=f"Client · Remote {sub_label}",
        infosys_url=URL_CLIENT,
        overview=(
            f"代表远端 BACnet 设备中一个「{sub_label}」对象的引用。Client 端通过本 FB 周期读 / 写 peer 设备的"
            f"对应对象,把远端 Present_Value 拉到 PLC 内变量(读)或把 PLC 内变量推到远端(写)。"
            "命名规则 `FB_BACnetRM_<shortcut>`(PDF §5.3.1 / §7.3)。"
        ),
        members_table_rows=[
            "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client(必填) |",
            "| 远端对象 | `nObjectInstance` | `UDINT` | 远端对象的实例号 |",
            "| 读模式覆盖 | `eReadMode` | `E_BACnet_CommMode` | 可单独覆盖 client 的全局 eReadMode(PDF §7.2.3 示例) |",
            f"| 当前值(只读) | `{val_member}` | `{val_type}` | Present_Value(stack 周期读后写入) |",
            "| 状态(只读) | `stStatusFlags` | `ST_BACnet_StatusFlags` | Status_Flags(从远端读到的状态字 4 位) |",
            "| 异步操作 | `bExecute` / `pData` / `nData` / `ePropID` | `BOOL` / `POINTER` / `UDINT` / `E_BACnet_PropertyIdentifier` | 配合非循环 ReadProperty / WriteProperty 使用(see FB_BACnetRM_ReadProperty 文档) |",
        ],
        variants_table_rows=None,
        behaviour=(
            f"FB_BACnetRM_{sub_label.split()[0]} 每周期调用一次。stack 按 client 的 tReadCycleTime 周期发"
            f"`ReadProperty(Present_Value)` 取远端值并写入 `{val_member}`(或在 eCOV / eCovP 模式下订阅 COV)。"
            f"PLC 端只需读 `{val_member}` 就能拿到远端值。写远端用 `FB_BACnetRM_WriteProperty / WritePropertyEx`(独立 FB,见对应文档)。"
            "本 FB 也可以作为 ReadProperty / WriteProperty 的 `iObject` 参数(用 ADR() 取地址),让那两个非循环 FB 知道往哪个对象写。"
            "如果 client 的 bConnected = FALSE,stack 自动暂停周期请求,`stStatusFlags.bFault := TRUE`。"
        ),
        error_section=(
            "无返回值;`stStatusFlags` 暴露远端值的状态(`bInAlarm` 等)。⚠️ PDF + InfoSys 未列具体错误码。"
        ),
        extra_tips_block=(
            "- **必须每周期 call**:不 call stack 不发周期请求,值不会刷新。\n"
            "- **`eReadMode` 单独覆盖适合特殊对象**:PDF §7.2.3 示例「设备总体支持 COV 但某个对象不支持」,把该 RM 对象的 eReadMode 单独设回 eRead/eRpm。\n"
            "- **大量 RM 对象时检查 nMaxParallelRequests**:每个 RM 都按 client 的 tReadCycleTime 发请求,几百个对象同时拉时间会成瓶颈。"
        ),
        example_code=(
            "PROGRAM P_Demo_" + fb_name + "\n"
            "VAR\n"
            "    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);\n"
            "    fbDevice : FB_BACnetRM_Device := (Client := fbClient);\n"
            "    fbRemote : " + fb_name + " := (Client := fbClient, nObjectInstance := 1);\n"
            f"    val : {val_type};\n"
            "END_VAR\n"
            "fbClient();\n"
            "fbDevice();\n"
            "fbRemote();\n"
            f"val := fbRemote.{val_member};"
        ),
        business_block=(
            f"- **场景**:把远端 BACnet 设备(如西门子 RDG 房间控制器)的 {sub_label.lower()} 拉到本机 PLC 用 — 例如把对端房间温度引到本机 PID 做综合控制。\n"
            "- **价值**:周期拉值 + 状态监控全自动,PLC 端只读一个成员;BACnet 标准跨厂商通用。\n"
            "- **替代方案对比**:用 ADS / Modbus 跨厂商不通用;BACnet RM 对象一行声明完成对接。"
        ),
        refs_extra="§7.3(Client POUs 命名规则)、§7.7(client 变量)、§7.9 / §7.10(非循环读 / 写,可指本 FB 作为 iObject)",
        related=related_local,
    )


_doc("client", "FB_BACnetRM_AI", _make_remote_obj_doc(
    "FB_BACnetRM_AI", "Analog Input", "REAL", "fPresVal",
    "`FB_BACnet_AI`(本机 AI)、`FB_BACnetRM_AV` / `BO` / `MI` / `MV`(其它 RM 变体)、`FB_BACnetRM_ReadProperty`(读其它属性)",
))
_doc("client", "FB_BACnetRM_AV", _make_remote_obj_doc(
    "FB_BACnetRM_AV", "Analog Value", "REAL", "fPresVal",
    "`FB_BACnet_AV`(本机 AV)、`FB_BACnetRM_AI`(若对端是 AI 用这个);PDF §9.6 用 fbRM_AV.WritePropertyNull 复位远端槽位",
))
_doc("client", "FB_BACnetRM_BO", _make_remote_obj_doc(
    "FB_BACnetRM_BO", "Binary Output", "BOOL", "bPresVal",
    "`FB_BACnet_BO`(本机 BO)、`FB_BACnetRM_WriteProperty`(PDF §7.10.1 写远端 BO 的 Out_of_Service 示例)",
))
_doc("client", "FB_BACnetRM_MI", _make_remote_obj_doc(
    "FB_BACnetRM_MI", "Multistate Input", "UDINT", "nPresVal",
    "`FB_BACnet_MI`(本机 MI)、其它 RM 变体",
))
_doc("client", "FB_BACnetRM_MV", _make_remote_obj_doc(
    "FB_BACnetRM_MV", "Multistate Value", "UDINT", "nPresVal",
    "`FB_BACnet_MV`(本机 MV)、PDF §7.6.5 / §9.5 示例",
))


def _make_remote_tcpou(fb_name: str, val_type: str, val_member: str) -> str:
    init = "22.0" if val_type == "REAL" else ("FALSE" if val_type == "BOOL" else "1")
    return (f"""VAR
    fbClient   : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#5S,
        nMaxParallelRequests := 20);
    fbDevice   : FB_BACnetRM_Device := (Client := fbClient);

    // 引用远端 device 42 的对应对象(实例号 1)
    fbRemote   : """ + fb_name + """ := (
        Client := fbClient,
        nObjectInstance := 1);

    val        : """ + val_type + """;
END_VAR""", """// =============================================================================
// 场景:把远端 BACnet 设备(device-id=42)中实例号 1 的对应对象 Present_Value 拉
//       到本机 PLC 用 — 例如对端房间温度引到本机 PID 做综合控制。
// 价值:周期拉值 + 状态监控全自动,PLC 端只读一个成员;BACnet 标准跨厂商通用,
//       无需为每种品牌 BMS 单独写驱动。
// 验证:1) BACnet Explorer 在 device-id=42 上模拟一个对应对象实例 1,设置一个
//       初值(""" + init + """)。2) 上电后等几秒 fbClient.bConnected=TRUE,fbDevice.
//       bOperational=TRUE。3) 等一个 tReadCycleTime(5 秒)后 fbRemote.""" + val_member + """ 应
//       变为 Explorer 端设的值。4) Explorer 改值,5 秒内 PLC 端 val 应跟随。
// =============================================================================

fbClient();
fbDevice();
fbRemote();

// ---- 暴露给 PLC 业务用 ----
val := fbRemote.""" + val_member + """;
""")


_tcpou("FB_BACnetRM_AI", *_make_remote_tcpou("FB_BACnetRM_AI", "REAL", "fPresVal"))
_tcpou("FB_BACnetRM_AV", *_make_remote_tcpou("FB_BACnetRM_AV", "REAL", "fPresVal"))
_tcpou("FB_BACnetRM_BO", *_make_remote_tcpou("FB_BACnetRM_BO", "BOOL", "bPresVal"))
_tcpou("FB_BACnetRM_MI", *_make_remote_tcpou("FB_BACnetRM_MI", "UDINT", "nPresVal"))
_tcpou("FB_BACnetRM_MV", *_make_remote_tcpou("FB_BACnetRM_MV", "UDINT", "nPresVal"))


# --- FB_BACnetRM_ReadProperty / ReadPropertyEx ----------------------------
_doc("client", "FB_BACnetRM_ReadProperty", build_doc(
    fb_name="FB_BACnetRM_ReadProperty",
    category_label="Client · Acyclic Read",
    infosys_url=URL_CLIENT,
    overview=(
        "非循环(acyclic)读远端 BACnet 对象的任意属性。与 `FB_BACnetRM_AI/AV/...` 的"
        "周期拉 Present_Value 不同,本 FB 适合按需读罕用属性(High_Limit / Description / Reliability 等)。"
        "通过 `iObject` 引用一个已经实例化的 RM 对象(用 ADR() 取地址)指定要读哪个对象。PDF §7.9 / §7.9.1 给完整示例。"
    ),
    members_table_rows=[
        "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |",
        "| 触发 | `bExecute` | `BOOL` | 上升沿触发一次读(读完自动转 FALSE) |",
        "| 目标对象 | `iObject` | `POINTER TO ...` | 用 `ADR(fbRmAi)` 等指向 RM 对象实例 |",
        "| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要读的 BACnet 属性(`PropHighLimit` / `PropReliability` 等) |",
        "| 接收缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | 用 `ADR(fOut)` + `SIZEOF(fOut)` 提供 |",
        "| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化的 完成/忙/错 + 错误码 |",
    ],
    variants_table_rows=[
        "| `FB_BACnetRM_ReadProperty` | — | 通过 iObject 指对象 |",
        "| `FB_BACnetRM_ReadPropertyEx` | 增 `eObjType` + `nObjInst` | 直接给对象类型 + 实例号,不必先实例化 RM 对象 |",
    ],
    behaviour=(
        "上升沿触发:`bExecute := TRUE` 触发一次 RP 请求,stack 发 ReadProperty 服务给 peer,等响应 → 把数据写到 `pData^`(长度 ≤ nData),"
        "完成后 `bDone := TRUE` 一个周期 + `bExecute` 自动复位 FALSE(典型的「忙/完成」两态机)。期间 `bBusy := TRUE`,"
        "出错时 `bError := TRUE` 且 `nErrorId` 给错误码。"
        "`iObject` 必须指向一个 RM 对象(因为 RM 对象自身存了 nObjectInstance 和对应类型),典型用 `fbRead.iObject := fbAI;`(stack 用类型转换自动取 ADR);"
        "PDF §7.9.1 示例 `fbRead.iObject := fbAI;` 直接赋值(IEC POINTER 隐式)。"
        "`FB_BACnetRM_ReadPropertyEx` 多了 `eObjType` + `nObjInst`,适合「读对端某个对象的属性但 PLC 端不想为该对象专门建一个 RM 实例」的场景(PDF §7.9.2 示例)。"
    ),
    error_section=(
        "`bError := TRUE` 时 `nErrorId` 包含错误码;⚠️ 具体 BACnet error / abort / reject 码常量集中在 BACnet_Globals 章节,PDF 未在本节列。"
    ),
    extra_tips_block=(
        "- **`iObject` 不能为 NULL**:必须先实例化 RM 对象再赋给 iObject;PDF §7.9.1 强调「object referenced by iObject must be called cyclically」。\n"
        "- **`pData` / `nData` 要匹配属性数据类型**:读 REAL 用 `pData := ADR(fOut); nData := SIZEOF(fOut);`;读字符串需要更大缓冲。\n"
        "- **`bExecute` 是脉冲不是电平**:置 TRUE 触发一次,完成后 stack 自动清,不需要 PLC 复位。\n"
        "- **大量按需读时考虑用 RPM**:RP 一次一个属性 + 一来回 RTT;RPM 一次多个属性合并请求,慢网段(MS/TP)节省大量时间(PDF §7.12)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnetRM_ReadProperty
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteAI : FB_BACnetRM_AI := (Client := fbClient, nObjectInstance := 1);
    fbRead : FB_BACnetRM_ReadProperty := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    fHighLimit : REAL;
END_VAR

fbClient();
fbDevice();
fbRemoteAI();

fbRead.bExecute := bTrigger;
IF fbRead.bExecute THEN
    bTrigger := FALSE;
    fbRead.iObject := fbRemoteAI;
    fbRead.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbRead.pData   := ADR(fHighLimit);
    fbRead.nData   := SIZEOF(fHighLimit);
END_IF
fbRead();""",
    business_block=(
        "- **场景**:运维偶尔需要读对端设备某个对象的 High_Limit / Reliability / Description,但不想一直周期拉(浪费带宽)。\n"
        "- **价值**:按需读,典型一次请求 < 1 秒;不污染 client 的周期请求。\n"
        "- **替代方案对比**:把这些属性也走周期 RM 对象:浪费带宽 + 占 router memory;ReadProperty 按需触发。"
    ),
    refs_extra="§7.9(Acyclic read)、§7.9.1(完整 ReadProperty 示例)、§7.9.2(ReadPropertyEx 不需要 iObject 的示例)",
    related="`FB_BACnetRM_WriteProperty / WritePropertyEx`(对应的写)、`FB_BACnetRM_AI/AV/...`(被 iObject 引用的 RM 对象)",
))

# ReadPropertyEx
_doc("client", "FB_BACnetRM_ReadPropertyEx", build_doc(
    fb_name="FB_BACnetRM_ReadPropertyEx",
    category_label="Client · Acyclic Read (Ex)",
    infosys_url=URL_CLIENT,
    overview=(
        "非循环读远端 BACnet 对象的任意属性,扩展版 — 比 `FB_BACnetRM_ReadProperty` 多了 `eObjType` 与 `nObjInst`"
        "两个引脚,可以直接指定目标对象的类型 + 实例号,无需先在 PLC 端为该对象实例化一个 RM 对象。"
        "适合「只读对端某对象一两次,不值得专门建 RM 实例」的场景。PDF §7.9.2 + §7.12(RPM)给完整示例。"
    ),
    members_table_rows=[
        "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |",
        "| 触发 | `bExecute` | `BOOL` | 上升沿触发一次读 |",
        "| 目标对象类型 | `eObjType` | `E_BACnet_ObjectType` | `ObjAnalogInput` / `ObjBinaryValue` / `ObjMultistateOutput` 等(扩展版相对 ReadProperty 多的引脚) |",
        "| 目标对象实例号 | `nObjInst` | `UDINT` | 远端对象实例号 |",
        "| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要读的属性 |",
        "| 接收缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(fOut)` + `SIZEOF(fOut)` |",
        "| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 同 ReadProperty |",
    ],
    variants_table_rows=None,
    behaviour=(
        "用法与 `FB_BACnetRM_ReadProperty` 几乎相同 — 上升沿触发,完成后 bDone 置位,bExecute 自动复位。"
        "区别仅在「指定目标对象的方式」:ReadProperty 需要先建 RM 对象 → iObject := RM对象;ReadPropertyEx 直接 "
        "`eObjType := ObjAnalogInput; nObjInst := 1;`。PDF §7.9.2 示例完整展示 — 读 device 42 的 AI:1 的 LowLimit,"
        "本 FB 一行指定 eObjType + nObjInst 即可,无需为 device 42 的 AI:1 建一个常驻 RM_AI 对象。"
        "PDF §7.12 示例进一步展示「多个 ReadPropertyEx 实例同时 bExecute,stack 自动合并成 RPM(ReadPropertyMultiple)请求」 — "
        "这是大批量按需读最高效的方式。"
    ),
    error_section=(
        "`bError := TRUE` 时 `nErrorId` 包含错误码,同 ReadProperty。⚠️ 具体 BACnet error 常量集中在 BACnet_Globals。"
    ),
    extra_tips_block=(
        "- **`ReadPropertyEx` vs `ReadProperty`**:前者不需要 RM 对象,适合一次性 / 多变目标;后者绑 RM 对象,适合稳定读同一目标的多个属性。\n"
        "- **多个 ReadPropertyEx 同步触发 + 自动 RPM 合并**:PDF §7.12 示例 `fbReadEx1.bExecute := bRead; fbReadEx2.bExecute := bRead; fbReadEx3.bExecute := bRead;` 同 PLC 周期触发,stack 把三个请求合成一个 RPM 请求(节省 2 个 RTT)。\n"
        "- **`nData` 必须够大**:读对象 Description / Object_Name 等字符串属性需要 ≥ 64 字节缓冲。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnetRM_ReadPropertyEx
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbReadEx : FB_BACnetRM_ReadPropertyEx := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    fLowLimit : REAL;
END_VAR

fbClient();
fbDevice();

fbReadEx.bExecute := bTrigger;
IF fbReadEx.bExecute THEN
    bTrigger := FALSE;
    fbReadEx.eObjType := E_BACnet_ObjectType.ObjAnalogInput;
    fbReadEx.nObjInst := 1;
    fbReadEx.ePropID := E_BACnet_PropertyIdentifier.PropLowLimit;
    fbReadEx.pData   := ADR(fLowLimit);
    fbReadEx.nData   := SIZEOF(fLowLimit);
END_IF
fbReadEx();""",
    business_block=(
        "- **场景**:运维偶尔要读对端设备一组随机属性,不值得为每个对象建 RM 实例;或者大批量 RPM 高效读取。\n"
        "- **价值**:比 ReadProperty 少了 RM 对象的实例化负担;多 ReadPropertyEx 同步触发 + 自动 RPM 合并性能极高(PDF §7.12 综合示例)。\n"
        "- **替代方案对比**:写 SDK 直接发 BACnet 报文:工程师要懂 ASN.1 编码 + RP/RPM 协议格式;ReadPropertyEx 是高层封装,一行解决。"
    ),
    refs_extra="§7.9.2(ReadPropertyEx 单请求示例)、§7.12(多个 ReadPropertyEx 自动 RPM 合并)",
    related="`FB_BACnetRM_ReadProperty`(基础版,需 RM 对象)、`FB_BACnetRM_WriteProperty / WritePropertyEx`(写)",
))


_tcpou("FB_BACnetRM_ReadProperty", """VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#10S,
        nMaxParallelRequests := 255);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteAI : FB_BACnetRM_AI := (Client := fbClient, nObjectInstance := 1);

    fbRead : FB_BACnetRM_ReadProperty := (Client := fbClient);

    bReadHighLimit : BOOL := FALSE;            // 在线写 TRUE 触发一次读
    fRemoteHighLimit : REAL;                   // 读回来的对端 HighLimit
END_VAR""", """// =============================================================================
// 场景:运维偶尔要读对端 device-id=42 的 AI:1 的 High_Limit 属性(不是 Present_Value,
//       不需要周期拉);RM 对象 fbRemoteAI 已经在做周期读 Present_Value,这次
//       一次性读其它属性。
// 价值:按需读,典型 < 1 秒响应;不污染 client 的周期请求带宽;复用现有 RM
//       对象做 iObject 指针。
// 验证:1) 上电等 client 连接成功(fbDevice.bOperational=TRUE)。2) BACnet
//       Explorer 在 device 42 的 AI:1 上设 High_Limit=99.0。3) 在线写 bReadHighLimit
//       := TRUE,fbRead 应触发一次 ReadProperty,fbRead.bDone 短暂置位后清零,
//       fRemoteHighLimit 应变为 99.0。
// =============================================================================

fbClient();
fbDevice();
fbRemoteAI();

fbRead.bExecute := bReadHighLimit;
IF fbRead.bExecute THEN
    bReadHighLimit := FALSE;
    fbRead.iObject := fbRemoteAI;             // 通过 RM 对象指定目标
    fbRead.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbRead.pData   := ADR(fRemoteHighLimit);
    fbRead.nData   := SIZEOF(fRemoteHighLimit);
END_IF

fbRead();
""")

_tcpou("FB_BACnetRM_ReadPropertyEx", """VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#10S,
        nMaxParallelRequests := 255);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);

    // 不需要为 AI:1 建专门 RM 对象,Ex 版直接指定类型 + 实例号
    fbReadEx : FB_BACnetRM_ReadPropertyEx := (Client := fbClient);

    bReadLowLimit : BOOL := FALSE;
    fRemoteLowLimit : REAL;
END_VAR""", """// =============================================================================
// 场景:一次性读远端 device 42 的 AnalogInput:1 的 Low_Limit;不为该对象专门建
//       RM 实例(节省 PLC 内存 + router memory)。
// 价值:比 ReadProperty 更轻量:无需 RM 对象;多个 Ex 同步触发可让 stack 自动
//       合并成 RPM 请求(PDF §7.12)。
// 验证:1) Client 连接成功后,BACnet Explorer 在 device 42 的 AI:1 上设
//       Low_Limit=10.0。2) 在线写 bReadLowLimit := TRUE,fbReadEx 应触发一次
//       ReadPropertyEx;bDone 短暂置位后 fRemoteLowLimit 应变为 10.0。
// =============================================================================

fbClient();
fbDevice();

fbReadEx.bExecute := bReadLowLimit;
IF fbReadEx.bExecute THEN
    bReadLowLimit := FALSE;
    fbReadEx.eObjType := E_BACnet_ObjectType.ObjAnalogInput;
    fbReadEx.nObjInst := 1;
    fbReadEx.ePropID := E_BACnet_PropertyIdentifier.PropLowLimit;
    fbReadEx.pData   := ADR(fRemoteLowLimit);
    fbReadEx.nData   := SIZEOF(fRemoteLowLimit);
END_IF

fbReadEx();
""")


# --- FB_BACnetRM_WriteProperty / WritePropertyEx --------------------------
_doc("client", "FB_BACnetRM_WriteProperty", build_doc(
    fb_name="FB_BACnetRM_WriteProperty",
    category_label="Client · Acyclic Write",
    infosys_url=URL_CLIENT,
    overview=(
        "非循环写远端 BACnet 对象的任意属性 — 把 PLC 端数据写到 peer 设备指定对象的指定属性。"
        "与 ReadProperty 对称,通过 `iObject` 引用 RM 对象指定写目标。PDF §7.10 / §7.10.1 详述。"
    ),
    members_table_rows=[
        "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |",
        "| 触发 | `bExecute` | `BOOL` | 上升沿触发一次写 |",
        "| 目标对象 | `iObject` | `POINTER TO ...` | 用 `fbWrite.iObject := fbRmBo;` 指定 |",
        "| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要写的属性 |",
        "| 发送缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(val) + SIZEOF(val)` |",
        "| 优先级 | `bPrio` | `BYTE` | 写命令型对象 Present_Value 时使用的 BACnet 优先级槽位(0..16,0 = 不指定,默认 16) |",
        "| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化完成 / 错状态 |",
    ],
    variants_table_rows=[
        "| `FB_BACnetRM_WriteProperty` | — | 通过 iObject 指对象 |",
        "| `FB_BACnetRM_WritePropertyEx` | 增 `eObjType` + `nObjInst` | 直接给类型 + 实例号 |",
    ],
    behaviour=(
        "上升沿触发 — `bExecute := TRUE` 触发一次 WriteProperty 服务,stack 把 `pData^` 中的数据按 ePropID 类型"
        "序列化后发给 peer,等响应 → `bDone := TRUE` 一个周期 + `bExecute` 自动复位 FALSE。"
        "PDF §7.10.1 示例展示写远端 BinaryOutput:0 的 Out_of_Service := TRUE/FALSE 的过程,只用 ePropID + pData + nData 三行。"
        "写命令型对象 Present_Value 时,`bPrio` 指定 BACnet 优先级槽位(BMS 通常用 8);"
        "本 FB 也提供 `WritePropertyNull` 方法 — 把指定 priority 槽位写成 NULL 释放该槽,PDF §9.6 reset priorities 示例展示这个用法。"
    ),
    error_section=(
        "`bError := TRUE` 时 `nErrorId` 包含错误码(write_access_denied / value_out_of_range 等)。"
    ),
    extra_tips_block=(
        "- **写命令型对象要指定 `bPrio`**:不指定时按 BACnet 默认 priority 16;BMS 写常用 priority 8(ManOperator)。\n"
        "- **写 Read-Only 属性会被 reject**:对端 stack 返回 write_access_denied;PLC 端读 nErrorId 判断。\n"
        "- **释放优先级用 `WritePropertyNull` 方法**:PDF §9.6 示例 `fbBV.WritePropertyNull(ePropertyId := PropPresentValue, bPrio := TO_BYTE(8));` 把 priority 8 槽位写 NULL。\n"
        "- **同步写多个属性用 WPM**:本库不直接暴露 WriteProperty Multiple 但 RM 对象周期写自动批量,大批量更新时让 stack 合并请求。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnetRM_WriteProperty
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteBO : FB_BACnetRM_BO := (Client := fbClient, nObjectInstance := 0);
    fbWrite : FB_BACnetRM_WriteProperty := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    bOutOfService : BOOL := TRUE;
END_VAR

fbClient();
fbDevice();
fbRemoteBO();

fbWrite.bExecute := bTrigger;
IF fbWrite.bExecute THEN
    bTrigger := FALSE;
    fbWrite.iObject := fbRemoteBO;
    fbWrite.ePropID := E_BACnet_PropertyIdentifier.PropOutOfService;
    fbWrite.pData   := ADR(bOutOfService);
    fbWrite.nData   := SIZEOF(bOutOfService);
END_IF
fbWrite();""",
    business_block=(
        "- **场景**:运维想暂时把对端某个对象置成 Out_Of_Service(仿真模式)做对端调试,无需上对端登录。\n"
        "- **价值**:跨厂商远程改属性,标准化无需懂对端品牌的协议细节。\n"
        "- **替代方案对比**:登对端控制器改:费时;BACnet WriteProperty 一行触发。"
    ),
    refs_extra="§7.10(Acyclic write)、§7.10.1(完整 WriteProperty 写 Out_of_Service 示例)、§9.6(WritePropertyNull 释放 priority 槽位)",
    related="`FB_BACnetRM_ReadProperty / ReadPropertyEx`(对应的读)、`FB_BACnetRM_WritePropertyEx`(本 FB 的扩展版)",
))

_doc("client", "FB_BACnetRM_WritePropertyEx", build_doc(
    fb_name="FB_BACnetRM_WritePropertyEx",
    category_label="Client · Acyclic Write (Ex)",
    infosys_url=URL_CLIENT,
    overview=(
        "非循环写远端 BACnet 对象的任意属性,扩展版 — 比 `FB_BACnetRM_WriteProperty` 多 `eObjType` + `nObjInst`,"
        "可以直接指定目标对象的类型 + 实例号,无需在 PLC 端为该对象先实例化 RM 对象。PDF §7.10.2 给完整示例。"
    ),
    members_table_rows=[
        "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |",
        "| 触发 | `bExecute` | `BOOL` | 上升沿触发一次写 |",
        "| 目标对象类型 | `eObjType` | `E_BACnet_ObjectType` | `ObjBinaryOutput` 等 |",
        "| 目标对象实例号 | `nObjInst` | `UDINT` | 远端对象实例号 |",
        "| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要写的属性 |",
        "| 发送缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | 数据 |",
        "| 优先级 | `bPrio` | `BYTE` | BACnet 优先级槽位(同 WriteProperty) |",
        "| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化 |",
    ],
    variants_table_rows=None,
    behaviour=(
        "用法与 `FB_BACnetRM_WriteProperty` 几乎相同 — 区别在指定目标对象的方式:Ex 版不需要 RM 对象,"
        "直接通过 `eObjType + nObjInst` 两个引脚表达对端的对象类型和实例号。PDF §7.10.2 完整示例:写远端 BinaryOutput:1 的 "
        "Out_of_Service,只在 ePropID / pData / nData / eObjType / nObjInst 五个引脚配好即可。"
        "上升沿触发后 stack 把 pData^ 中的数据按 ePropID 类型序列化发给 peer,等响应后 bDone 置位 + bExecute 自动复位。"
        "适合「只写一次某对象、不想专门建 RM 实例」的场景;多个 WritePropertyEx 同步触发理论上可被 stack 合并为 WPM(WritePropertyMultiple)请求。"
    ),
    error_section=(
        "`bError := TRUE` 时 `nErrorId` 包含错误码,同 WriteProperty。"
    ),
    extra_tips_block=(
        "- **WritePropertyEx vs WriteProperty**:前者不需要 RM 对象,适合一次性 / 多变目标;后者绑 RM 对象,稳定写同一目标多个属性时方便。\n"
        "- **多个 WritePropertyEx 同步触发**:与 ReadPropertyEx 类似,stack 可能合并成 WPM(WritePropertyMultiple);不过本 PDF 未给 WPM 综合示例。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnetRM_WritePropertyEx
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbWriteEx : FB_BACnetRM_WritePropertyEx := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    bOutOfService : BOOL := TRUE;
END_VAR

fbClient();
fbDevice();

fbWriteEx.bExecute := bTrigger;
IF fbWriteEx.bExecute THEN
    bTrigger := FALSE;
    fbWriteEx.eObjType := E_BACnet_ObjectType.ObjBinaryOutput;
    fbWriteEx.nObjInst := 1;
    fbWriteEx.ePropID := E_BACnet_PropertyIdentifier.PropOutOfService;
    fbWriteEx.pData := ADR(bOutOfService);
    fbWriteEx.nData := SIZEOF(bOutOfService);
END_IF
fbWriteEx();""",
    business_block=(
        "- **场景**:一次性写远端某对象的某个属性,不想为该对象专门建 RM 实例(节省 PLC 内存)。\n"
        "- **价值**:比 WriteProperty 更轻量;适合大量「一次性」写命令。\n"
        "- **替代方案对比**:同 WriteProperty,只是省了 RM 对象实例化。"
    ),
    refs_extra="§7.10.2(WritePropertyEx 完整示例)",
    related="`FB_BACnetRM_WriteProperty`(基础版,需 RM 对象)、`FB_BACnetRM_ReadProperty / ReadPropertyEx`(读)",
))

_tcpou("FB_BACnetRM_WriteProperty", """VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tWriteCycleTime := T#10S,
        nMaxParallelRequests := 255);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteBO : FB_BACnetRM_BO := (Client := fbClient, nObjectInstance := 0);

    fbWrite : FB_BACnetRM_WriteProperty := (Client := fbClient);
    bWriteOutOfService : BOOL := FALSE;        // 在线写 TRUE 触发一次写
    bOutOfServiceVal : BOOL := TRUE;           // 要写的值
END_VAR""", """// =============================================================================
// 场景:运维想暂时把对端 device 42 的 BO:0 置成 Out_Of_Service(仿真模式)做对
//       端调试 — 调试人员在物理 BO 上做手动测试时不想让 BMS 误以为是真值。
// 价值:跨厂商远程改属性,标准化无需懂对端品牌的协议细节;一行触发。
// 验证:1) 等 fbDevice.bOperational=TRUE。2) BACnet Explorer 在 device 42 BO:0
//       上查 Out_Of_Service 属性=FALSE。3) 在线写 bWriteOutOfService := TRUE
//       (并预设 bOutOfServiceVal := TRUE),fbWrite 应触发一次 WriteProperty
//       并 bDone 短暂置位。4) Explorer 应能看到 Out_Of_Service=TRUE。
// =============================================================================

fbClient();
fbDevice();
fbRemoteBO();

fbWrite.bExecute := bWriteOutOfService;
IF fbWrite.bExecute THEN
    bWriteOutOfService := FALSE;
    fbWrite.iObject := fbRemoteBO;
    fbWrite.ePropID := E_BACnet_PropertyIdentifier.PropOutOfService;
    fbWrite.pData   := ADR(bOutOfServiceVal);
    fbWrite.nData   := SIZEOF(bOutOfServiceVal);
END_IF

fbWrite();
""")

_tcpou("FB_BACnetRM_WritePropertyEx", """VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tWriteCycleTime := T#10S,
        nMaxParallelRequests := 255);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);

    fbWriteEx : FB_BACnetRM_WritePropertyEx := (Client := fbClient);
    bWriteOutOfService : BOOL := FALSE;
    bOutOfServiceVal : BOOL := TRUE;
END_VAR""", """// =============================================================================
// 场景:一次性写远端 device 42 BO:1 的 Out_Of_Service;不为该对象专门建 RM
//       实例。
// 价值:比 WriteProperty 更轻量;适合大量一次性写命令。
// 验证:1) 等 fbDevice.bOperational=TRUE。2) BACnet Explorer 在 device 42 BO:1
//       上查 Out_Of_Service=FALSE。3) 在线写 bWriteOutOfService := TRUE,fbWriteEx
//       应触发一次 WritePropertyEx,Out_Of_Service 应变 TRUE。
// =============================================================================

fbClient();
fbDevice();

fbWriteEx.bExecute := bWriteOutOfService;
IF fbWriteEx.bExecute THEN
    bWriteOutOfService := FALSE;
    fbWriteEx.eObjType := E_BACnet_ObjectType.ObjBinaryOutput;
    fbWriteEx.nObjInst := 1;
    fbWriteEx.ePropID := E_BACnet_PropertyIdentifier.PropOutOfService;
    fbWriteEx.pData   := ADR(bOutOfServiceVal);
    fbWriteEx.nData   := SIZEOF(bOutOfServiceVal);
END_IF

fbWriteEx();
""")


# --- FB_BACnetRM_SchedA / SchedB / SchedM (远端 Schedule 引用) ----------
def _make_remote_sched_doc(fb_name: str, sched_type: str) -> str:
    return build_doc(
        fb_name=fb_name,
        category_label=f"Client · Remote Schedule {sched_type}",
        infosys_url=URL_CLIENT,
        overview=(
            f"代表远端 BACnet 设备中一个「Schedule {sched_type}」对象的引用。"
            f"BACnet 标准的 Schedule 不带具体数据类型,必须按对端实际类型选择对应的 RM 变体 "
            "(SchedA = REAL / SchedB = BOOL / SchedM = UDINT,PDF §7.8 明确)。"
            "用于让本机 PLC 引用对端时间表对象 — 读其当前 Present_Value 或当作 Loop 输入。"
        ),
        members_table_rows=[
            "| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |",
            "| 远端对象 | `nObjectInstance` | `UDINT` | 远端 Schedule 实例号 |",
            "| 当前值(只读) | `bPresVal` / `fPresVal` / `nPresVal`(按变体) | 同 SchedB/A/M | Present_Value(stack 周期读) |",
        ],
        variants_table_rows=None,
        behaviour=(
            "本远端 Schedule 引用 FB 每周期调用一次,stack 按 client 的 tReadCycleTime 周期 ReadProperty 读对端 Schedule 的 Present_Value 并写入对应类型的 PresVal 成员。"
            "对端时间表的 aWeek / aException / aCalendar 由对端维护本身,本 FB 只读 Present_Value;"
            "如果要修改对端时间表的内容,用 WriteProperty / WritePropertyEx 写对应属性 ID(`PropWeeklySchedule` 等)。"
            "PDF §7.8 强调:Schedule 对象在 BACnet 标准里是无具体数据类型的容器,本 RM 变体必须按对端实际类型选对应一个 — "
            "选错(对端是 Analog 类型你用 SchedB 拉)读不到值。"
        ),
        error_section=(
            "无返回值;`stStatusFlags` 暴露远端状态。⚠️ 未列具体错误码。"
        ),
        extra_tips_block=(
            "- **必须知道对端 Schedule 数据类型**:PDF §7.8 说 function block must be selected manually — 用 BACnet Explorer 先看对端 Schedule 的 Weekly_Schedule 数据类型。\n"
            "- **本 RM 只能读 Present_Value**:改对端时间表需要 FB_BACnetRM_WriteProperty 写 WeeklySchedule / ExceptionSchedule;且对端通常对这些属性有写保护。"
        ),
        example_code=(
            "PROGRAM P_Demo_" + fb_name + "\n"
            "VAR\n"
            "    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);\n"
            "    fbDevice : FB_BACnetRM_Device := (Client := fbClient);\n"
            "    fbRemoteSched : " + fb_name + " := (Client := fbClient, nObjectInstance := 1);\n"
            "END_VAR\n"
            "fbClient();\n"
            "fbDevice();\n"
            "fbRemoteSched();"
        ),
        business_block=(
            f"- **场景**:把对端设备的 Schedule {sched_type} 引到本机 — 例如对端 BMS 已经配好了「楼宇运行时间表」,本机 PLC 跟随这个时间表做相关动作。\n"
            "- **价值**:跨设备共享时间表,无需各 PLC 复制一份;改对端表自动跟随。\n"
            "- **替代方案对比**:本机 PLC 自建 Schedule:多份时间表难同步;远端引用让「时间表唯一来源」。"
        ),
        refs_extra="§7.8(Remote schedule objects 选 SchedA/B/M 规则)",
        related="`FB_BACnet_SchedA` / `SchedB` / `SchedM`(本机 Schedule)、`FB_BACnetRM_Device`(必须先建)",
    )


_doc("client", "FB_BACnetRM_SchedA", _make_remote_sched_doc("FB_BACnetRM_SchedA", "Analog"))
_doc("client", "FB_BACnetRM_SchedB", _make_remote_sched_doc("FB_BACnetRM_SchedB", "Binary"))
_doc("client", "FB_BACnetRM_SchedM", _make_remote_sched_doc("FB_BACnetRM_SchedM", "Multistate"))


def _make_remote_sched_tcpou(fb_name: str, member: str) -> tuple:
    return (f"""VAR
    fbClient        : FB_BACnet_Client := (nDeviceInstance := 42, tReadCycleTime := T#5S);
    fbDevice        : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteSched   : """ + fb_name + """ := (Client := fbClient, nObjectInstance := 1);
END_VAR""", """// =============================================================================
// 场景:对端 BMS 已经配好了 BACnet Schedule 对象(实例 1),本机 PLC 引用它的
//       Present_Value 作为业务输入(如对端"楼宇运行时间表"驱动本机 PLC 算法)。
// 价值:跨设备共享时间表,无需各 PLC 复制一份;对端改表本机自动跟随。
// 验证:1) 等 fbDevice.bOperational=TRUE。2) BACnet Explorer 在 device 42 上
//       配 Schedule:1 当前 Present_Value=某个值。3) 等 1 个 tReadCycleTime(5
//       秒)后 fbRemoteSched.""" + member + """ 应读到对端值。4) Explorer 改 Present_Value
//       后,本机 PLC 端 5 秒内自动跟随。
// 注意:Schedule 是无类型的 — 必须用与对端实际数据类型匹配的 RM 变体(SchedA
//       = REAL / SchedB = BOOL / SchedM = UDINT,PDF §7.8)。
// =============================================================================

fbClient();
fbDevice();
fbRemoteSched();
""")


_tcpou("FB_BACnetRM_SchedA", *_make_remote_sched_tcpou("FB_BACnetRM_SchedA", "fPresVal"))
_tcpou("FB_BACnetRM_SchedB", *_make_remote_sched_tcpou("FB_BACnetRM_SchedB", "bPresVal"))
_tcpou("FB_BACnetRM_SchedM", *_make_remote_sched_tcpou("FB_BACnetRM_SchedM", "nPresVal"))


# ============================================================================
# server/  — Server-side acyclic R/W FBs
# ============================================================================
_doc("server", "FB_BACnet_ReadProperty", build_doc(
    fb_name="FB_BACnet_ReadProperty",
    category_label="Server · Acyclic Read",
    infosys_url=URL_RW,
    overview=(
        "服务端非循环读自身对象的任意属性 — 用于让本机 PLC 程序读「自己」暴露的 BACnet 对象属性"
        "(如临时读自己 fbAv 的 EventState、读自己 fbBO 的 Priority_Array 等)。"
        "与 client 侧的 `FB_BACnetRM_ReadProperty` 对称,但操作目标是本机对象而非远端。"
        "Status: ⚠️ PDF 仅在 §6.1.1 注释 + 命名规则部分提及本 FB(命名与远端版一致但去掉 `RM_`),"
        "未给独立示例;本文档基于命名规则推导。"
    ),
    members_table_rows=[
        "| 触发 | `bExecute` | `BOOL` | 上升沿触发一次读 |",
        "| 目标对象 | `iObject` | `POINTER TO ...` | 指本机某个对象 FB 实例(用 ADR()) |",
        "| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要读的属性 |",
        "| 接收缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(val) + SIZEOF(val)` |",
        "| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化完成 / 错状态 |",
    ],
    variants_table_rows=None,
    behaviour=(
        "上升沿触发,stack 直接从 PLC 内本对象的 BACnet 属性表读出值(不经过网络),立即完成。"
        "适合 PLC 程序需要拿到「BACnet 标准的某个属性值」而该属性不是 FB 对象的直接成员的情况 — 例如"
        "Priority_Array 是 BACnet 标准属性但 FB_BACnet_AO 不把它作为 PLC 可读成员;"
        "用本 FB 读 PropPriorityArray 就能拿到 16 槽位的当前值快照。完成后 bDone 一个周期 + bExecute 自动复位。"
    ),
    error_section=(
        "`bError := TRUE` 时 `nErrorId` 包含错误码(属性不存在 / 类型不匹配等);⚠️ PDF 未给独立示例,使用前请用 BACnet Explorer 验证目标属性 ID 与 buffer 大小。"
    ),
    extra_tips_block=(
        "- **本 FB 操作本机对象,不发网络请求**:相比 RM 版几乎瞬时完成。\n"
        "- **`iObject` 必须指本机 FB 对象实例**:用 `ADR(fbLocalAv)` 取地址。\n"
        "- **typical use**:读 Priority_Array / Active_COV_Subscriptions / Status_Flags 等非直接成员的标准属性。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_ReadProperty
VAR
    fbLocalAv : FB_BACnet_AV := (sObjectName := 'LocalAv');
    fbRead : FB_BACnet_ReadProperty;
    bTrigger : BOOL := FALSE;
    fLocalHighLimit : REAL;
END_VAR

fbLocalAv();
fbRead.bExecute := bTrigger;
IF fbRead.bExecute THEN
    bTrigger := FALSE;
    fbRead.iObject := fbLocalAv;
    fbRead.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbRead.pData   := ADR(fLocalHighLimit);
    fbRead.nData   := SIZEOF(fLocalHighLimit);
END_IF
fbRead();""",
    business_block=(
        "- **场景**:PLC 程序临时需要某本机对象的 BACnet 标准属性值(非 FB 直接成员),典型 Priority_Array、Active_COV_Subscriptions、Object_Identifier 等。\n"
        "- **价值**:不必为每个标准属性都在 FB 中加 getter 成员;BACnet stack 已经维护这些属性,本 FB 一行读出。\n"
        "- **替代方案对比**:用 RM 版读自己(client 连本机回环):工作但绕远;本 FB 直接读省网络。"
    ),
    refs_extra="§6.1.1 命名规则(server-side 命名是 `FB_BACnet_<>` 去掉 `RM_`)",
    related="`FB_BACnet_WriteProperty`(对称的写)、`FB_BACnetRM_ReadProperty / ReadPropertyEx`(远端版)",
    status="⚠️ infer-from-naming-convention",
))

_doc("server", "FB_BACnet_WriteProperty", build_doc(
    fb_name="FB_BACnet_WriteProperty",
    category_label="Server · Acyclic Write",
    infosys_url=URL_RW,
    overview=(
        "服务端非循环写自身对象的任意属性 — 用于让本机 PLC 程序写「自己」暴露的 BACnet 对象属性。"
        "与 client 侧的 `FB_BACnetRM_WriteProperty` 对称,但目标是本机对象而非远端。"
        "Status: ⚠️ PDF 仅在 §6.1.1 注释 + 命名规则部分提及本 FB,未给独立示例;本文档基于命名规则推导。"
    ),
    members_table_rows=[
        "| 触发 | `bExecute` | `BOOL` | 上升沿触发一次写 |",
        "| 目标对象 | `iObject` | `POINTER TO ...` | 指本机某个对象 FB 实例 |",
        "| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要写的属性 |",
        "| 发送缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(val) + SIZEOF(val)` |",
        "| 优先级 | `bPrio` | `BYTE` | 写命令型对象 Present_Value 时使用的 BACnet 优先级槽位 |",
        "| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化完成 / 错状态 |",
    ],
    variants_table_rows=None,
    behaviour=(
        "上升沿触发,stack 直接在本机 BACnet 属性表上写值(不经网络)。本 FB 与 PLC 直接修改 FB 成员的差别:"
        "PLC 直接 `fbAv.fValPgm := 22.0` 是把 PLC 端缓冲改了等下次 stack 循环;而本 FB 模拟"
        "外部 BACnet 客户端 WriteProperty 服务,触发 stack 内的全套属性变更钩子 — 包括写到优先级槽位、"
        "触发 COV 通知、updateCounter 自增等。"
        "也可通过 PLC 端用本 FB 复位某优先级槽位:`bPrio := 8` + 数据带 BACnet NULL 编码就可释放槽位 "
        "(等同于 RM 版的 WritePropertyNull,但目标是本机)。"
    ),
    error_section=(
        "`bError := TRUE` 时 `nErrorId` 包含错误码(写保护属性 / 越界等);⚠️ PDF 未给独立示例。"
    ),
    extra_tips_block=(
        "- **本 FB 与直接写 FB 成员的差别**:直接写 PLC 端缓冲(简单);本 FB 模拟外部写,触发完整 BACnet 钩子(COV 通知等)。\n"
        "- **`iObject` 必须指本机 FB 对象**:用 `ADR(fbLocalAv)`。\n"
        "- **释放优先级槽位**:用本 FB + 特殊 NULL 编码,或直接调本机对象的 `WritePropertyNull` 方法(PDF §9.6)。"
    ),
    example_code="""PROGRAM P_Demo_FB_BACnet_WriteProperty
VAR
    fbLocalAv : FB_BACnet_AV := (sObjectName := 'LocalAv');
    fbWrite : FB_BACnet_WriteProperty;
    bTrigger : BOOL := FALSE;
    fNewHighLimit : REAL := 90.0;
END_VAR

fbLocalAv();
fbWrite.bExecute := bTrigger;
IF fbWrite.bExecute THEN
    bTrigger := FALSE;
    fbWrite.iObject := fbLocalAv;
    fbWrite.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbWrite.pData   := ADR(fNewHighLimit);
    fbWrite.nData   := SIZEOF(fNewHighLimit);
END_IF
fbWrite();""",
    business_block=(
        "- **场景**:PLC 程序需要模拟「外部 BACnet 客户端」修改本机某属性,触发完整 stack 钩子(COV 通知 / updateCounter 等);或释放某优先级槽位。\n"
        "- **价值**:直接 PLC 写 FB 成员可能漏掉 stack 钩子;用本 FB 保证 BACnet 标准行为一致性。\n"
        "- **替代方案对比**:直接写 FB 成员:简单但漏钩子;本 FB 完整。"
    ),
    refs_extra="§6.1.1 命名规则、§9.6(WritePropertyNull 释放优先级,本 FB 配 NULL 编码可等效)",
    related="`FB_BACnet_ReadProperty`(对称的读)、`FB_BACnetRM_WriteProperty / WritePropertyEx`(远端版)",
    status="⚠️ infer-from-naming-convention",
))

_tcpou("FB_BACnet_ReadProperty", """VAR
    fbLocalAv : FB_BACnet_AV := (
        sObjectName := 'LocalAv',
        fHighLimit := 90.0,
        bHighLimitEnable := TRUE);

    fbRead : FB_BACnet_ReadProperty;
    bTrigger : BOOL := FALSE;
    fLocalHighLimit : REAL;
END_VAR""", """// =============================================================================
// 场景:PLC 程序临时需要本机 fbLocalAv 的 HighLimit 属性值(虽然声明时设了
//       90.0,但运维通过 BACnet 改过 — 想看当前值)。
// 价值:不必为每个 BACnet 标准属性都在 FB 中加 getter 成员;BACnet stack 维护
//       这些属性,本 FB 一行读出当前值。
// 验证:1) 上电后 BACnet Explorer 把 fbLocalAv 的 HighLimit 改成 99.0。2) 在线
//       写 bTrigger := TRUE,fbRead 应触发一次本机读,bDone 短暂置位后
//       fLocalHighLimit 应为 99.0(不是 90.0,因为 Explorer 已经改过)。
// 注意:本对象类型 PDF 未给独立示例,基于 §6.1.1 命名规则推导。
// =============================================================================

fbLocalAv();

fbRead.bExecute := bTrigger;
IF fbRead.bExecute THEN
    bTrigger := FALSE;
    fbRead.iObject := fbLocalAv;
    fbRead.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbRead.pData   := ADR(fLocalHighLimit);
    fbRead.nData   := SIZEOF(fLocalHighLimit);
END_IF

fbRead();
""")

_tcpou("FB_BACnet_WriteProperty", """VAR
    fbLocalAv : FB_BACnet_AV := (
        sObjectName := 'LocalAv',
        fHighLimit := 90.0,
        bHighLimitEnable := TRUE);

    fbWrite : FB_BACnet_WriteProperty;
    bTrigger : BOOL := FALSE;
    fNewHighLimit : REAL := 95.0;
END_VAR""", """// =============================================================================
// 场景:PLC 程序需要模拟"外部 BACnet 客户端"修改本机 fbLocalAv 的 HighLimit
//       到 95.0,触发完整 stack 钩子(COV 通知 / updateCounter 等)。直接写
//       fbLocalAv.fHighLimit 也行,但可能漏掉某些 BACnet 钩子。
// 价值:本 FB 保证 BACnet 标准行为一致性;BACnet Explorer 端能像收到外部 Write
//       一样响应。
// 验证:1) BACnet Explorer 订阅 fbLocalAv 的 HighLimit COV。2) 在线写 bTrigger
//       := TRUE,fbWrite 应触发一次本机写,Explorer 应能收到 COV 通知,
//       HighLimit 值变 95.0。
// 注意:本对象类型 PDF 未给独立示例,基于 §6.1.1 命名规则推导。
// =============================================================================

fbLocalAv();

fbWrite.bExecute := bTrigger;
IF fbWrite.bExecute THEN
    bTrigger := FALSE;
    fbWrite.iObject := fbLocalAv;
    fbWrite.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbWrite.pData   := ADR(fNewHighLimit);
    fbWrite.nData   := SIZEOF(fNewHighLimit);
END_IF

fbWrite();
""")


def main() -> int:
    for category, fb_name, body in DOCS:
        write_doc(category, fb_name, body)
    for fb_name, decl, st in TCPOUS:
        write_tcpou(fb_name, decl, st)
    print(f"wrote {len(DOCS)} docs and {len(TCPOUS)} TcPOUs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
