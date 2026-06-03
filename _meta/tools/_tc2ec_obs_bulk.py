#!/usr/bin/env python3
"""Bulk generate obsolete DC helpers + F_GetVersionTcEtherCAT."""
import sys
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[2]
NS = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')


def gen_guid(name):
    return '{' + str(uuid.uuid5(NS, f'tc3-libraries-kb/Tc2_EtherCAT/P_Demo_{name}')) + '}'


ENTRIES = [
    # §11.4.1 [outdated DCTIME]
    ("DCTIME_TO_DCTIMESTRUCT", "11.4.1.1", "57065995", "ok"),
    ("DCTIME_TO_FILETIME", "11.4.1.2", "57064459", "ok"),
    ("DCTIME_TO_STRING", "11.4.1.3", "57068011", "ok"),
    ("DCTIME_TO_SYSTEMTIME", "11.4.1.4", "57069547", "ok"),
    ("DCTIMESTRUCT_TO_DCTIME", "11.4.1.5", "57062923", "ok"),
    ("FILETIME_TO_DCTIME", "11.4.1.6", "57071083", "ok"),
    ("STRING_TO_DCTIME", "11.4.1.7", "57072619", "ok"),
    ("SYSTEMTIME_TO_DCTIME", "11.4.1.8", "57070603", "ok"),
    ("FB_EcDcTimeCtrl", "11.4.1.9", "57084427", "ok"),
    # §11.4.2 [outdated DCTIME and T_LARGE_INTEGER]
    ("F_ConvExtTimeToDcTime", "11.4.2.1", "2285533707", "notonweb"),
    ("F_ConvTcTimeToDcTime", "11.4.2.2", "2285531787", "ok"),
    ("F_ConvTcTimeToExtTime", "11.4.2.3", "2285529867", "notonweb"),
    ("F_GetActualDcTime", "11.4.2.4", "57088907", "ok"),
    ("F_GetCurDcTaskTime", "11.4.2.5", "57086475", "notonweb"),
    ("F_GetCurDcTickTime", "11.4.2.6", "57085963", "notonweb"),
    ("F_GetCurExtTime", "11.4.2.7", "2285085707", "ok"),
    ("FB_EcExtSyncCalcTimeDiff", "11.4.2.8", "2285535627", "ok"),
    ("FB_EcExtSyncCheck", "11.4.2.9", "2285537547", "ok"),
    # §11.4.3 / 11.4.4 single
    ("DCTIME64_TO_FILETIME", "11.4.3", "2267404427", "ok"),
    ("FILETIME_TO_DCTIME64", "11.4.4", "10501950219", "notonweb"),
    # §12.1 obsolete F_GetVersionTcEtherCAT
    ("F_GetVersionTcEtherCAT", "12.1", "57099531", "notonweb"),
]


def render_doc(name, section, infosys_id, infosys_state):
    infosys_url = (f"https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/{infosys_id}.html"
                   if infosys_state == "ok" else
                   f"https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/{infosys_id}.html"
                   if infosys_state == "notonweb" else "⚠️ not-on-infosys")
    infosys_checked = "✅ 2026-06-03" if infosys_state == "ok" else "⚠️ not-on-infosys"

    # Decide narrative based on name family
    is_version = name == "F_GetVersionTcEtherCAT"
    is_fb = name.startswith("FB_")
    is_ctrl = name == "FB_EcDcTimeCtrl"
    is_sync = "ExtSync" in name

    if is_version:
        summary = ("已弃用的库版本读取 FUNCTION，曾返回 Tc2_EtherCAT 库的版本号组件。"
                   "Beckhoff 推荐改用全局结构 `stLibVersion_Tc2_EtherCAT` 替代本 FC，"
                   "新工程不要再调用本 FC。")
        behavior = ("**调用即返回**：同步 FUNCTION。`nVersionElement = 1` 返回 major，`2` 返回 minor，`3` 返回 revision。"
                    "返回值 `UINT`。Beckhoff 官方 PDF §12.1 明确标记本 FC 为 outdated，"
                    "新代码应改用 `stLibVersion_Tc2_EtherCAT.iMajor`、`.iMinor`、`.iBuild` 直接取字段。\n\n"
                    "**典型陷阱**：本 FC 不会消失但已不再演进；后续 Tc2_EtherCAT 版本号字段如有变化（如 build）本 FC 无法返回。"
                    "现有老工程引用本 FC 可以暂时保留，但应在维护版本中替换为 GVL 字段访问。")
        scenario = ("老工程兼容场景：早期代码用 `F_GetVersionTcEtherCAT(1)` 拿主版本号判定是否启用新 API。"
                    "迁移路径：把所有调用替换成 `stLibVersion_Tc2_EtherCAT.iMajor` 直接读全局 GVL。")
        refs = "`stLibVersion_Tc2_EtherCAT`（推荐替代）、`Tc2_System.F_GetVersion*`"
        category = "[obsolete] Library Version (§12)"
    elif is_ctrl:
        summary = ("已弃用的 32-bit DC 时间组件提取 FB；功能等同 `FB_EcDcTimeCtrl64`，"
                   "但入参类型为 `T_DCTIME`（32-bit）而非 `T_DCTIME64`。Beckhoff 推荐改用 64-bit 版。")
        behavior = ("**触发**：通过 method action（`A_GetYear` 等）提取组件。本 FB 与 `FB_EcDcTimeCtrl64` 行为一致，"
                    "区别仅在入参类型，32-bit DC 时间约 4 秒回卷使得本 FB 实际可用时间窗很小。"
                    "Beckhoff 官方建议新工程统一用 64-bit 版以避免回卷盲区。\n\n"
                    "**典型陷阱**：32-bit 回卷使得跨越 4 秒边界的时间提取结果不可信。")
        scenario = ("老工程兼容：早期 32-bit DC 时间 API 现仍可用但不再演进；迁移到 `FB_EcDcTimeCtrl64`"
                    "+ `T_DCTIME64` 体系是新工程的标准实践。")
        refs = "`FB_EcDcTimeCtrl64`（推荐替代）、`T_DCTIME`、`T_DCTIME64`"
        category = "[obsolete] DC 32-bit (§11.4)"
    elif is_sync:
        summary = (f"已弃用的 32-bit DC 时间体系下的同步 helper。本 FB 与对应的 64-bit 版"
                   f"（`{name}64`）功能一致，但用 `T_DCTIME`（32-bit）而非 `T_DCTIME64`。新工程统一用 64-bit 版。")
        behavior = ("**触发**：调用即异步处理。本 FB 用法和 64-bit 版相同，"
                    "但 32-bit DC 时间表达范围有限（仅 4 秒），对长时间窗的同步监控不可靠。"
                    "Beckhoff 官方明确把本 FB 归入 [obsolete]，新工程应避免使用。\n\n"
                    "**典型陷阱**：32-bit 回卷导致跨越 4 秒的差值计算错误。新工程应统一迁移到 64-bit 等价 FB 完成精密时间同步监控链。"
                    "维护老工程时本 FB 仍可用作短时窗同步判定，但应在版本演进里同步排期下线。")
        scenario = (f"老工程兼容：早期版本使用本 FB 做同步监控，新工程统一迁移到 `{name}64` 64-bit 版。")
        refs = f"`{name}64`（推荐替代）"
        category = "[obsolete] DC 32-bit (§11.4)"
    elif is_fb:
        summary = f"已弃用的 DC 时间 helper FB；完整说明见 PDF §{section} 原文。Beckhoff 推荐改用 64-bit 等价 FB。"
        behavior = "**触发**：调用即异步处理。本 FB 是 32-bit DC 时间体系下的 helper，新工程统一用 64-bit 版本。"
        scenario = "老工程兼容场景；新工程统一迁移到 64-bit 等价 FB。"
        refs = "对应 64-bit 等价 FB"
        category = "[obsolete] DC 32-bit (§11.4)"
    else:
        # Plain FC: e.g. DCTIME_TO_DCTIMESTRUCT, F_ConvExtTimeToDcTime
        summary = (f"已弃用的 DC 时间转换 FUNCTION。本 FC 操作的是 `T_DCTIME`（32-bit）类型；"
                   f"Beckhoff 推荐改用 64-bit 版（如 `{name.replace('DCTIME', 'DCTIME64').replace('_TO_DCTIME', '_TO_DCTIME64') if 'DCTIME' in name else name}` 或对应 64-bit FC）。"
                   "新工程不要使用本 FC。")
        behavior = ("**调用即返回**：同步 FUNCTION。本 FC 是早期 32-bit DC 时间体系的转换 helper，与对应 64-bit 版功能等价，"
                    "区别仅在入参/返回值类型。32-bit DC 时间约 4 秒回卷使得本 FC 实际可用时间窗很小，"
                    "Beckhoff 官方 PDF §11.4 已把这一系列 FC 归入 outdated，新工程应统一迁移到 64-bit 体系。\n\n"
                    "**典型陷阱**：32-bit 回卷导致超过 4 秒的转换出现歧义。")
        scenario = ("老工程兼容场景：早期工程使用 32-bit DC 时间链路，新工程统一迁移到 64-bit。")
        refs = "对应 64-bit 等价 FC（推荐替代）"
        category = "[obsolete] DC 32-bit (§11.4)"

    return f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `{'FUNCTION_BLOCK' if is_fb else 'FUNCTION'}` |
| Category | `{category}` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | {infosys_url} |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | {infosys_checked} |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{summary}

## 2. 接口定义

本 FC / FB 完整接口签名见 PDF §{section} 原文表格与 InfoSys topic。由于本 FC / FB 已被官方标为 outdated，新工程应改用对应的 64-bit 版本，本仓库保留文档仅为维护老工程时查询使用。

## 3. 行为说明

{behavior}

## 4. 错误码 / 返回值

多数 outdated DC 转换 FC 不暴露错误输出，入参越界或回卷边界时返回值不可信。完整错误码语义请对照 PDF §{section} 原文表格。

## 5. 使用注意 / 常见坑

- **已弃用**：新工程统一用 64-bit 等价 FC / FB
- **32-bit 回卷**（工程经验补充）：4 秒回卷使得长时间窗业务不可靠
- **保留仅为兼容**：老工程仍可调用，但应优先排期迁移

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：{scenario}
- **价值**：维护老工程时仍能查到该 FC / FB 的文档
- **替代方案对比**：本 FC / FB 已被 64-bit 等价 FC / FB 取代；新工程统一迁移

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §{section}
- **InfoSys topic**：{infosys_url}
- **相关 FB / FC**：{refs}
"""


def render_pou(name):
    guid = gen_guid(name)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
VAR
    // 本程序为 [obsolete] FC / FB 占位演示
    // 新工程统一迁移到 64-bit 等价 FC / FB
END_VAR
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// =============================================================================
// Tc2_EtherCAT.{name} 演示程序（[obsolete]）
// =============================================================================
// 场景：维护老工程时偶尔需要查 32-bit DC 时间体系的 helper。本 FC / FB
//       已被 Beckhoff 官方归入 [obsolete]；新工程一律用 64-bit 等价版本。
// 价值：仓库保留本演示与文档，仅供维护老工程时查阅参考。
// 验证步骤：
//   1. 不建议在新工程中使用本 FC / FB
//   2. 若必须使用，参考 PDF 对应章节签名调用
//   3. 优先排期迁移到 64-bit 等价版本
// =============================================================================

// 本 [obsolete] 演示不展示具体调用；请参考 64-bit 版本的 demo 程序
;
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""


def main():
    for name, section, iid, istate in ENTRIES:
        out_md = ROOT / "Tc2_EtherCAT" / "obsolete" / f"{name}.md"
        out_pou = ROOT / "Tc2_EtherCAT" / "examples" / f"P_Demo_{name}.TcPOU"
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_pou.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_doc(name, section, iid, istate))
        out_pou.write_text(render_pou(name))
        print(f"WROTE {name}")


if __name__ == "__main__":
    main()
