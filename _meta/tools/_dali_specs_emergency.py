#!/usr/bin/env python3
"""Generate Part 202 (Emergency Lighting) FBs."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

SPECS = []

# Emergency lighting high-level FBs
SPECS.append({
    "name": "FB_DALIV2EmergencyLightingDT",
    "section": "4.1.1.3.1",
    "subdir": "part202_emergency_high",
    "category_display": "Part 202 / Emergency Lighting / High-Level",
    "infosys": f"{INFOSYS_BASE}142935307.html",
    "summary": (
        "**DALI 应急照明耐久性测试（Duration Test，high-level）**——按 IEC 62386 Part 202 应急灯标准，"
        "本 FB 触发一次完整的应急耐久性测试：让灯具切换到应急模式（电池供电），亮 `nDurationMinutes` "
        "分钟（通常 60、90 或 180 分钟），过程中监测电池电压；测试结束后报告通过 / 失败。\n\n"
        "**应急照明法规强制要求**：商业建筑应急灯必须定期做 Duration Test（通常每年 1 次），"
        "本 FB 是 PLC 端自动测试方案。"
    ),
    "inputs_desc": {
        "bStart": "上升沿启动 Duration Test",
        "bAbort": "上升沿提前终止（电池可能未充满需重新充）",
        "nDurationMinutes": "测试时长（分钟），合法值取决于灯具配置",
        "nAddr": "目标应急灯地址",
        "eAddrType": "寻址类型",
    },
    "outputs_desc": {
        "bBusy": "测试进行中",
        "bError": "测试错误（灯具无响应等）",
        "nErrorId": "错误号",
        "bDone": "测试完成",
        "bTestResult": "测试结果：TRUE = 通过（电池能维持 `nDurationMinutes`）/ FALSE = 失败（电池过早耗尽）",
        "nDurationDoneMinutes": "实际坚持的分钟数",
    },
    "behavior": (
        "**整体流程**：本 FB 调 IEC 62386 Part 202 标准 `START DURATION TEST` 命令，灯具切换到应急模式"
        "（与主电断开，电池供电）按当前 `EMERGENCY LEVEL` 亮 `nDurationMinutes` 分钟；过程中本 FB "
        "周期性查询灯具状态；测试结束后读取 `QUERY DURATION TEST RESULT` 得到 PASS / FAIL。\n\n"
        "**测试期间灯具行为**：灯具与主电隔离，电池供电；亮度由灯具内部 `EMERGENCY LEVEL` 配置决定"
        "（通常等同 `MAX VALUE`）；测试完成自动切回主电、电池开始充电（充满需几小时）。\n\n"
        "**法规依据**：欧洲 EN 50172 / 中国 GB 17945 等应急灯标准要求商业建筑应急灯定期做 Duration "
        "Test 验证电池容量；本 FB 提供自动化方案。\n\n"
        "**典型陷阱**：① 测试期间灯具断开主电，断电恢复后电池要充几小时——大量同时测试会让备用照明"
        "失能；标准做法是按楼层分批测试；② `bAbort` 仅停止测试，电池可能没完全测完不应认作通过；"
        "③ 测试结果存在灯具内部直到下次测试覆盖——一定要在 `bDone = TRUE` 时记录 `bTestResult`。"
    ),
    "pitfalls": [
        "测试期间灯具与主电断开几小时（含充电），按楼层分批测试避免全局应急照明失能。",
        "测试结果只有 PASS / FAIL，电池实际容量见 `nDurationDoneMinutes`。",
        "`bAbort` 不算通过，需重测。",
        "测试结果存在灯具内部，下次测试覆盖——必须 PLC 端记录历史。",
    ],
    "scenario": (
        "商场应急照明年检——按 EN 50172 / GB 17945 法规要求，应急灯每年至少做 1 次完整 Duration Test。"
        "PLC 定时（每年 1 次）按楼层分批触发本 FB，自动完成测试并把结果写入审计日志。"
    ),
    "value": (
        "替代手动测试（断电 + 计时 + 检查每盏灯）；自动化测试 + 审计日志，满足法规检查。"
    ),
    "alternative": (
        "1) `FB_DALIV2EmergencyLightingFT`：Function Test（短测，几秒检查电池）；"
        "2) 厂家专用测试软件：能做但需要笔记本接入现场；"
        "3) **本 FB**：PLC 集成自动化方案。"
    ),
    "related": (
        "[`FB_DALIV2EmergencyLightingFT`](FB_DALIV2EmergencyLightingFT.md)（Function Test）、"
        "[`FB_DALIV2FileLogging`](FB_DALIV2FileLogging.md)（测试日志记录）、"
        "[`FB_DALIV2GetSettingsType01`](FB_DALIV2GetSettingsType01.md)（应急灯配置查询）"
    ),
    "tcpou_decls": (
        "    bStartTest       : BOOL;\n"
        "    bAbortTest       : BOOL;\n"
        "    nLampAddr        : BYTE := 0;\n"
        "    bTestDone        : BOOL;\n"
        "    bTestPass        : BOOL;\n"
        "    nDurationMin     : UINT;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bStart           := bStartTest,\n"
        "    bAbort           := bAbortTest,\n"
        "    nDurationMinutes := 60,\n"
        "    nAddr            := nLampAddr,\n"
        "    eAddrType        := eDALIV2AddrTypeShort,"
    ),
    "tcpou_scenario": "商场应急照明年检：触发 short addr 0 应急灯做 60 分钟 Duration Test。",
    "tcpou_value": "自动化应急照明测试，满足法规审计要求。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录；应急灯连主电正常充电。\n"
        "2. 在线 bStartTest 一次上升沿；bBusy 应保持 TRUE 60 分钟。\n"
        "3. 过程中观察灯具应切到应急模式（与主电断开）持续亮。\n"
        "4. bDone = TRUE 后读 bTestPass：TRUE = 电池容量合格。\n"
        "5. nDurationDoneMinutes 应等于 60；若 < 60 = 电池容量不足。\n"
        "6. 记录 bTestPass + 测试时间到审计日志。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
