#!/usr/bin/env python3
"""Generate Part 102 low-level Power Control FBs."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

A_BASIC = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityMiddle,"
)
D_BASIC = "    nLampAddr        : BYTE := 0;\n\n"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

CAT_PC = "Part 102 / Low-Level / Power Control"
SUBDIR = "part102_low_power"

SPECS = []

# Simple "no-extra-param" power control commands (just bStart + addressing)
SIMPLE_FBS = [
    ("FB_DALIV2Off", "4.1.2.3.4.5", "142773131",
        "**关灯命令**——立即把目标 DALI 镇流器调到亮度 0（关）。无视 `MIN VALUE` 钳位（0 是关灯特例）。"
        "由 DALI 协议直接定义的标准命令。",
        "**调用方式**：`bStart` 上升沿；本 FB 下发 `OFF` 命令（DALI 字节 `100x xxx0 0000 0000`，"
        "`x` 由 `nAddr` 与 `eAddrType` 编码决定）。灯具收到立即关灯。\n\n"
        "**与 `DAPC = 0` 区别**：二者效果完全相同（都是关灯），但本 FB 用 DALI 协议显式 OFF 命令，"
        "语义更明确、网络流量略低（不需要额外的 DAPC 字节）。\n\n"
        "**典型应用**：消防联动一键关灯（应急联动信号触发本 FB 给广播地址）、定时关灯、HMI 关灯按钮。",
        ["与 `DAPC = 0` 等效；推荐用本 FB 因语义更清晰。",
         "广播下发关灯整线所有灯立即关；运行时慎用（影响用户）。",
         "本 FB 不带 FADE 渐变——`OFF` 命令是瞬时关，不受 `FADE TIME` 影响。"],
        "消防联动：消防中心一键触发，PLC 广播本 FB 给整楼层所有非应急灯，瞬间关闭节能。",
        "替代手动检查每盏灯亮度再下发 DAPC=0；DALI 标准 OFF 命令一句话搞定。",
        "1) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=0)`：等效；2) **本 FB**：语义清晰首选。",
        "[`FB_DALIV2DirectArcPowerControl`](FB_DALIV2DirectArcPowerControl.md)（等效但要传 0）、"
        "[`FB_DALIV2RecallMaxLevel`](FB_DALIV2RecallMaxLevel.md)（一键全亮）"),

    ("FB_DALIV2RecallMaxLevel", "4.1.2.3.4.7", "142776203",
        "**召回最大亮度命令**——灯具调到自身 `MAX VALUE` 寄存器配置的亮度（默认 254 即 100%）。"
        "受 `FADE TIME` 影响渐变。常用于一键全亮（应急、消防全亮、舞台开场）。",
        "**调用方式**：`bStart` 上升沿；本 FB 下发 `RECALL MAX LEVEL` 命令；灯具调到 `MAX VALUE` "
        "寄存器值（用 `FB_DALIV2SetMaxLevel` 配置）。\n\n"
        "**渐变时间**：受 `FADE TIME` 寄存器影响。`FADE TIME = 0` 瞬时；其它值按 DALI 时间表渐变。\n\n"
        "**与 `DAPC = 254` 区别**：DAPC 254 固定到 254；本 FB 调到 `MAX VALUE`（可能配置成 200 即 80%）。"
        "本 FB 更安全——不会越过配置的上限。\n\n"
        "**典型应用**：应急照明（消防 / 火警联动一键全亮）；舞台开场一键满载；办公区到达时间统一开灯。"
        "广播下发可让整线灯具同时全亮，但每盏灯按各自 `MAX VALUE` 配置（不同灯可能到不同绝对值）。\n\n"
        "**典型陷阱**：① 灯具 `MAX VALUE` 未配置时是默认 254，本 FB 与 DAPC=254 等效；② 渐变期间不要立即"
        "查询亮度，会读到中间值；③ 组寻址下若组成员 `MAX VALUE` 差别大，亮度看上去不一致。",
        ["渐变时长由 `FADE TIME` 决定；要瞬时全亮先设 `FADE TIME = 0`。",
         "实际亮度是 `MAX VALUE` 而非 254——工程配置 `MAX VALUE` 时要注意。"],
        "应急联动：火警触发，PLC 广播本 FB 给所有应急灯，自动全亮（按 `MAX VALUE` 配置，通常 254）。",
        "比 DAPC=254 更安全，自动应用 `MAX VALUE` 钳位。",
        "1) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=254)`：固定到 254，可能超过 `MAX VALUE` 被钳；"
        "2) **本 FB**：自动用 `MAX VALUE`，更符合工程意图。",
        "[`FB_DALIV2RecallMinLevel`](FB_DALIV2RecallMinLevel.md)、"
        "[`FB_DALIV2SetMaxLevel`](../part102_low_config/FB_DALIV2SetMaxLevel.md)、"
        "[`FB_DALIV2DirectArcPowerControl`](FB_DALIV2DirectArcPowerControl.md)"),

    ("FB_DALIV2RecallMinLevel", "4.1.2.3.4.8", "142777739",
        "**召回最小亮度命令**——灯具调到自身 `MIN VALUE` 寄存器配置的亮度（默认 1 即最低对数档约 0.1%）。"
        "受 `FADE TIME` 渐变。注意：本命令不会关灯（0 = 关是另一个命令）；最低也是 `MIN VALUE`。",
        "**调用方式**：`bStart` 上升沿；下发 `RECALL MIN LEVEL`；灯具调到 `MIN VALUE` 寄存器值。\n\n"
        "**典型应用**：夜间值班调暗（保留可视性）、自然光足时降低人工灯亮度、智能家居睡前调暗。\n\n"
        "**与 `DAPC = 1` 区别**：DAPC 1 固定到 1（约 0.1% 物理亮度，很可能根本看不见）；本 FB 调到"
        "灯具配置的 `MIN VALUE`（可能配为 30，即工程认可的最暗可见值）。\n\n"
        "**典型陷阱**：① 灯具 `MIN VALUE` 默认 1 时看上去几乎全黑，用户会以为灯坏了；上线前应根据现场"
        "设置合理的 `MIN VALUE`；② 本命令不关灯，长时间停在 MIN 时电源仍消耗。",
        ["实际亮度是 `MIN VALUE` 而非 1；工程配置 `MIN VALUE` 时要注意。",
         "本 FB 不关灯；要关用 `FB_DALIV2Off`。"],
        "智能家居睡前模式：用户说『睡眠模式』，PLC 广播本 FB 给卧室所有灯——按各灯 `MIN VALUE` "
        "（典型 1..30）调到最暗但不关，提供夜起照明。",
        "比 DAPC=1 更灵活——各灯 `MIN VALUE` 可独立配置成不同的夜间值。",
        "1) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=1)`：固定到 1；"
        "2) **本 FB**：按各灯 `MIN VALUE` 配置。",
        "[`FB_DALIV2RecallMaxLevel`](FB_DALIV2RecallMaxLevel.md)、"
        "[`FB_DALIV2SetMinLevel`](../part102_low_config/FB_DALIV2SetMinLevel.md)、"
        "[`FB_DALIV2Off`](FB_DALIV2Off.md)（关灯）"),

    ("FB_DALIV2StepDown", "4.1.2.3.4.9", "142779275",
        "**亮度递减一步命令**——灯具按当前 `FADE RATE` 步进减少一步亮度。最多减到 `MIN VALUE`，"
        "不关灯（要关用 `FB_DALIV2StepDownAndOff`）。",
        "**调用方式**：`bStart` 上升沿；下发 `STEP DOWN` 命令；灯具按内部 `FADE RATE` 步进一档"
        "（FADE RATE 决定每秒可触发的最大步数，本 FB 调用一次只触发一步）。\n\n"
        "**典型连续调光**：PLC 用 IL/ST 循环每 50 ms 调一次本 FB，配合 `FADE RATE = 7` 实现"
        "平滑的连续递减；用户长按 - 按钮触发该循环，松开停止。",
        ["不关灯——最低 `MIN VALUE`。要关灯用 `FB_DALIV2StepDownAndOff`。",
         "单步幅度由灯具 `FADE RATE` 决定；不同 `FADE RATE` 步幅不同。",
         "连续调光需要 PLC 循环触发；间隔太短可能命令缓冲区溢出。"],
        "面板长按减亮按钮：PLC 检测按钮持续按下，每 100 ms 调一次本 FB；松开停止。",
        "替代手写 DALI 字节命令；按 `FADE RATE` 自动应用 DALI 标准步进。",
        "1) `FB_DALIV2Down`：连续 `Down` 命令（200 ms 内连续步进）；2) `FB_DALIV2DirectArcPowerControl` "
        "+ 自算下个值：完全自定义；3) **本 FB**：单步精确调光。",
        "[`FB_DALIV2StepDownAndOff`](FB_DALIV2StepDownAndOff.md)、"
        "[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)、"
        "[`FB_DALIV2Down`](FB_DALIV2Down.md)、"
        "[`FB_DALIV2SetFadeRate`](../part102_low_config/FB_DALIV2SetFadeRate.md)"),

    ("FB_DALIV2StepDownAndOff", "4.1.2.3.4.10", "142780811",
        "**亮度递减一步并在最低时关灯**——与 `FB_DALIV2StepDown` 类似，但当亮度已是 `MIN VALUE` 时"
        "下一次调用直接关灯（亮度 0）。提供一致的『按钮按到底就关灯』UX。",
        "**调用方式**：`bStart` 上升沿；下发 `STEP DOWN AND OFF` 命令。灯具按 `FADE RATE` 步进一档；"
        "如果当前已是 `MIN VALUE`，则关灯。\n\n"
        "**与 `StepDown` 区别**：`StepDown` 最低停在 `MIN VALUE`；本 FB 在 `MIN VALUE` 状态下再调一次会关灯。\n\n"
        "**典型应用**：面板长按减亮按钮的『一直按到关』实现——用户按住按钮 PLC 每 100 ms 触发本 FB，"
        "亮度逐步下降到 `MIN VALUE`，再触发一次直接关灯，松开按钮即停止。这种 UX 在楼宇 / 家用照明非常常见。\n\n"
        "**典型陷阱**：① 用户期望『按一次关一次』时不要用本 FB，会一直递减；用 `FB_DALIV2Off`；"
        "② `MIN VALUE` 设得高（如 100）则用户感觉灯被『从中等亮度突然全黑』，体验不平滑——`MIN VALUE` 应"
        "设得较低（如 30 以下）配合本 FB。",
        ["在已是 `MIN VALUE` 状态下调用本 FB 灯会关——给用户『按到底关灯』的体验。",
         "其它行为同 `StepDown`。"],
        "智能面板：用户长按减亮按钮直到关灯——本 FB 替代『先 StepDown 到 MIN 然后再 Off』两步逻辑。",
        "一行命令实现『递减到底关灯』；PLC 端不需要检查当前亮度。",
        "1) `FB_DALIV2StepDown` + 应用层检查到 MIN 再调 `Off`：两次命令 + 状态检查；"
        "2) **本 FB**：一行命令搞定。",
        "[`FB_DALIV2StepDown`](FB_DALIV2StepDown.md)、"
        "[`FB_DALIV2Off`](FB_DALIV2Off.md)、"
        "[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)"),

    ("FB_DALIV2StepUp", "4.1.2.3.4.11", "142782347",
        "**亮度递增一步命令**——`StepDown` 的对应递增版本。最多递增到 `MAX VALUE`，不超过。",
        "**调用方式**：`bStart` 上升沿；下发 `STEP UP` 命令；按 `FADE RATE` 步进一档。\n\n"
        "**典型应用**：面板长按加亮按钮的实现——用户按住按钮 PLC 每 100 ms 触发本 FB 一次，"
        "亮度逐步递增，到达 `MAX VALUE` 自动停止；松开按钮 PLC 停止触发本 FB。\n\n"
        "**与 `Up` 区别**：`Up` 一次命令灯具内部连续步进约 200 ms（多步），适合调用频率较低的场景；"
        "本 FB 一次单步，适合调用频率较高（每 30..50 ms 一次）的细粒度控制。\n\n"
        "**典型陷阱**：① 单步幅度由 `FADE RATE` 决定，未配置时默认 7（约 28 步/秒），用户感觉合适；"
        "② 调用频率过高（< 30 ms 一次）可能命令缓冲区溢出。",
        ["最高 `MAX VALUE`，超过不变。", "单步由 `FADE RATE` 决定。"],
        "面板长按加亮按钮：每 100 ms 触发一次本 FB。",
        "DALI 标准步进，无需自算下个值。",
        "1) `FB_DALIV2Up`：连续 Up；2) **本 FB**：单步精确。",
        "[`FB_DALIV2StepDown`](FB_DALIV2StepDown.md)、"
        "[`FB_DALIV2Up`](FB_DALIV2Up.md)、"
        "[`FB_DALIV2OnAndStepUp`](FB_DALIV2OnAndStepUp.md)"),

    ("FB_DALIV2Up", "4.1.2.3.4.12", "142783883",
        "**连续递增亮度命令**——灯具持续按 `FADE RATE` 速率递增亮度，约 200 ms 后自动停止（一次 Up 命令"
        "对应约 200 ms 的连续步进）。要再次递增需再次调用。",
        "**调用方式**：`bStart` 上升沿；下发 `UP` 命令；灯具在约 200 ms 内按 `FADE RATE` 连续递增。\n\n"
        "**与 `StepUp` 区别**：`StepUp` 单步；本 FB 一次命令连续 200 ms 步进（约 7 步如 `FADE RATE = 7`）。\n\n"
        "**典型应用**：面板长按渐亮——PLC 检测按钮持续按下，每 200 ms 调一次本 FB，给用户『连续渐亮』感受。\n\n"
        "**命令缓冲区优势**：相比每 30 ms 触发一次 `StepUp`，本 FB 每 200 ms 触发一次即可，命令缓冲区占用"
        "降低约 6 倍——多按钮并发场景下显著节省 DALI 总线带宽。\n\n"
        "**典型陷阱**：① 触发频率超过 200 ms（如 500 ms）灯具会有断续感（亮度上升到 200 ms 自动停，等下次"
        "命令）；② 上限 `MAX VALUE`，到达后再触发不变化。",
        ["一次命令约 200 ms 连续步进；持续渐亮需周期性触发。", "上限 `MAX VALUE`。"],
        "面板长按渐亮按钮：PLC 每 200 ms 触发本 FB。",
        "比 `StepUp` 调用频率低（每 200 ms 一次 vs 每 30 ms 一次），命令缓冲区占用少。",
        "1) `FB_DALIV2StepUp`：单步；2) **本 FB**：连续 200 ms。",
        "[`FB_DALIV2Down`](FB_DALIV2Down.md)、"
        "[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)"),

    ("FB_DALIV2Down", "4.1.2.3.4.2", "142769547",
        "**连续递减亮度命令**——与 `FB_DALIV2Up` 对偶；约 200 ms 连续步进递减。",
        "**调用方式**：`bStart` 上升沿；下发 `DOWN` 命令；灯具按 `FADE RATE` 连续 200 ms 递减。\n\n"
        "**典型应用**：面板长按减亮按钮——PLC 每 200 ms 触发一次，提供平滑减亮的用户体验。\n\n"
        "**与 `StepDown` 区别**：本 FB 一次命令连续 200 ms 步进（约 7 步）；`StepDown` 单步。\n\n"
        "**典型陷阱**：① 下限 `MIN VALUE`，到达后再触发不变化（不会关灯）；要『减到底就关』用"
        "`FB_DALIV2StepDownAndOff`；② 触发频率应匹配 200 ms 步进窗口，过低断续感明显。",
        ["一次命令约 200 ms 连续步进。", "下限 `MIN VALUE`（不关灯）。"],
        "面板长按减亮：PLC 每 200 ms 触发本 FB。",
        "比 `StepDown` 触发频率低。",
        "1) `FB_DALIV2StepDown`：单步；2) **本 FB**：连续 200 ms。",
        "[`FB_DALIV2Up`](FB_DALIV2Up.md)、"
        "[`FB_DALIV2StepDown`](FB_DALIV2StepDown.md)"),

    ("FB_DALIV2OnAndStepUp", "4.1.2.3.4.6", "142774667",
        "**关灯状态下开灯+递增一步；亮灯状态下仅递增**——灯具从 OFF 调用时先开到 `MIN VALUE` 然后"
        "递增一步；亮灯状态下等同 `StepUp`。提供一致的『按钮加亮总能让灯出现』UX。",
        "**调用方式**：`bStart` 上升沿；下发 `ON AND STEP UP` 命令。\n\n"
        "**关灯状态下的行为细节**：DALI 协议规定此命令在 OFF 状态先把灯调到 `MIN VALUE`，"
        "然后按 `FADE RATE` 步进一档。所以最终亮度大约是 `MIN VALUE + (254/FADE_RATE_steps)`。\n\n"
        "**亮灯状态下的行为**：等同 `FB_DALIV2StepUp`——按 `FADE RATE` 单步递增，上限 `MAX VALUE`。\n\n"
        "**典型陷阱**：关灯状态下调用，灯具会跳到 `MIN VALUE`（典型 1，几乎不可见）+ 一步，用户可能觉得"
        "『按了没反应』；要让按按钮就明显开灯应该用 `FB_DALIV2DirectArcPowerControl` 直接设到中等亮度。"
        "工程上常做法是首次按键直接 DAPC=200，后续按键才用本 FB 递增。",
        ["关灯状态调用跳到 `MIN VALUE` + 一步，可能用户觉得反应不明显。",
         "亮灯状态等同 `StepUp`。"],
        "面板加亮按钮的开灯兼调光实现：灯关时按一下就开（且渐亮）；灯亮时按一下递增。",
        "一行命令处理两种状态；UX 一致。",
        "1) 应用层检测亮度然后选 `On` 或 `StepUp`：两步；2) **本 FB**：DALI 协议一行搞定。",
        "[`FB_DALIV2StepUp`](FB_DALIV2StepUp.md)、"
        "[`FB_DALIV2RecallMaxLevel`](FB_DALIV2RecallMaxLevel.md)"),
]

for name, section, topicid, summary, behavior, pitfalls, scenario, value, alt, related in SIMPLE_FBS:
    SPECS.append({
        "name": name,
        "section": section,
        "subdir": SUBDIR,
        "category_display": CAT_PC,
        "infosys": f"{INFOSYS_BASE}{topicid}.html",
        "summary": summary,
        "behavior": behavior,
        "pitfalls": pitfalls,
        "scenario": scenario,
        "value": value,
        "alternative": alt,
        "related": related,
        "tcpou_decls": D_BASIC,
        "tcpou_inputs_assigns": A_BASIC,
        "tcpou_scenario": scenario[:90].rstrip() + "...",
        "tcpou_value": "DALI 协议标准命令的轻量封装。",
        "tcpou_verify": (
            "1. 通信 FB 跑起；编译；登录。\n"
            "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
            "3. 观察 short addr 0 灯的物理亮度变化是否符合本命令描述。"
        ),
    })

# --- GoToScene (extra param nScene) ---
SPECS.append({
    "name": "FB_DALIV2GoToScene",
    "section": "4.1.2.3.4.4",
    "subdir": SUBDIR,
    "category_display": CAT_PC,
    "infosys": f"{INFOSYS_BASE}142772107.html",
    "summary": (
        "**触发场景调用命令**——灯具调到自身 `SCENE n` 寄存器存的亮度（n = `nScene`，0..15）。"
        "受 `FADE TIME` 渐变。配合 `FB_DALIV2SetScene` 使用——前者预设场景值，本 FB 触发。\n\n"
        "场景是 DALI 协议的核心概念之一——把『每盏灯在某状态下的亮度』预存到灯具内部，"
        "调用一条命令即可整片灯同时切到该状态。"
    ),
    "inputs_desc": {"nScene": "目标场景号（0..15）"},
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `GO TO SCENE n` 命令；灯具读取自身 `SCENE n` 寄存器值"
        "（用 `FB_DALIV2SetScene` 预设过），按该值调亮度。`FADE TIME` 决定渐变。\n\n"
        "**广播触发的力量**：`eAddrType := Broadcast` + `nScene := 0` 让全线所有灯同时切到场景 0——"
        "每盏灯的场景 0 值不同（房间灯到 254、走廊灯到 100、地面灯到 50），但一条命令同步生效。"
        "**这是 DALI 协议相对 0..10V / DMX 等更高级的核心特性之一**。\n\n"
        "**场景值的特殊语义**：`SCENE n = MASK (255)` 时本灯不参与该场景；`SCENE n = 0` 时本灯调用时被强制关灯。"
        "用 `FB_DALIV2RemoveFromScene` 设 MASK；用 `FB_DALIV2SetScene` 设具体亮度。\n\n"
        "**典型陷阱**：① `nScene > 15` 灯具忽略；② 场景未预设的灯调用本 FB 后亮度不变（MASK 默认）"
        "或被关灯（0 默认，取决于灯具）——上线前必须先用 `FB_DALIV2SetScene` 给所有相关灯配场景值。"
    ),
    "pitfalls": [
        "`nScene` 必须 0..15。",
        "调用前必须用 `FB_DALIV2SetScene` 预设每盏灯的该场景值，否则行为不确定。",
        "渐变时长由 `FADE TIME` 决定。",
    ],
    "scenario": (
        "会议室自动化：操作员触屏选『演示模式』，PLC 广播 GoToScene(nScene=1) 给整个会议室——"
        "所有灯按预设瞬间切到投影最舒适的亮度组合（投影区灯 200、其它区 50、窗边 0）。"
    ),
    "value": (
        "替代 PLC 程序里写一堆条件判断把每盏灯设到固定亮度的代码；预设场景使逻辑与"
        "亮度数值解耦，运维改场景不用改 PLC。"
    ),
    "alternative": (
        "1) PLC 直接发多个 DAPC 给每盏灯：能做但代码硬编码亮度数值，运维不便；"
        "2) **本 FB**：场景与代码解耦，运维只在 HMI 配场景值即可。"
    ),
    "related": (
        "[`FB_DALIV2SetScene`](../part102_low_config/FB_DALIV2SetScene.md)、"
        "[`FB_DALIV2RemoveFromScene`](../part102_low_config/FB_DALIV2RemoveFromScene.md)、"
        "[`FB_DALIV2QuerySceneLevel`](../part102_low_queries/FB_DALIV2QuerySceneLevel.md)"
    ),
    "tcpou_decls": D_BASIC + "    nSceneNumber     : BYTE := 1;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nScene           := nSceneNumber,",
    "tcpou_scenario": "触发会议室『演示模式』场景（场景 1）：广播本 FB 给所有灯同时切到该场景。",
    "tcpou_value": "替代 PLC 端硬编码各灯亮度；场景与代码解耦。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 必须先用 P_Demo_FB_DALIV2SetScene 给每盏灯配置场景 1 的目标亮度。\n"
        "3. 把 eAddrType 改为 eDALIV2AddrTypeBroadcast（默认 Short 仅触发一盏）。\n"
        "4. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "5. 所有灯应按各自场景 1 设定值调亮度（不同灯调到不同亮度）。"
    ),
})

# --- EnableDAPCSequence ---
SPECS.append({
    "name": "FB_DALIV2EnableDAPCSequence",
    "section": "4.1.2.3.4.3",
    "subdir": SUBDIR,
    "category_display": CAT_PC,
    "infosys": f"{INFOSYS_BASE}142770571.html",
    "summary": (
        "**启用 DAPC 序列模式命令**——告诉灯具接下来一段时间会收到连续多次 DAPC 命令"
        "（间隔 ≤ 200 ms），灯具进入连续接受模式：所有 DAPC 立即应用、不做 FADE TIME 渐变、"
        "不响应其它命令。常用于 PLC 自己写平滑长渐变（用 PLC 定时器每 100 ms 算一个目标亮度、"
        "通过 DAPC 下发）的场景。\n\n"
        "**注意时序**：本 FB 触发后必须在 200 ms 内开始连续 DAPC；超时灯具自动退出序列模式。"
    ),
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `ENABLE DAPC SEQUENCE` 命令；灯具进入序列模式持续 200 ms。\n\n"
        "**序列内的 DAPC 时序约束**：每两次 DAPC 命令间隔必须 ≤ 200 ms。超时灯具自动退出。退出后再 DAPC "
        "按普通模式（受 FADE TIME 影响）。\n\n"
        "**典型应用**：① PLC 自己实现非标准渐变曲线（如 S 曲线、三角波）——每 100 ms 算一个亮度发 DAPC；"
        "② 舞台特效——精确控制每帧亮度；③ 与音乐同步的呼吸效果。\n\n"
        "**典型陷阱**：① 启用后超 200 ms 没下 DAPC，灯具退出，下一次 DAPC 按普通模式生效（用户感知突变）；"
        "② 序列期间下发非 DAPC 命令（如 RecallMax）→ 灯具退出序列模式后处理，时序不确定。"
    ),
    "pitfalls": [
        "启用后必须 200 ms 内开始下 DAPC，且 DAPC 间隔 ≤ 200 ms。",
        "序列期间不要混入其它命令。",
        "渐变需要 PLC 端实现（FADE TIME 在序列模式被忽略）。",
    ],
    "scenario": "舞台音乐节奏调光——PLC 按 100 ms 节拍计算下一个亮度，通过 DAPC 下发；启用序列模式让灯具立即响应。",
    "value": "替代灯具自己的 FADE TIME 渐变（曲线固定、时间档位有限）；PLC 可实现任意自定义曲线。",
    "alternative": (
        "1) 单纯 DAPC 不启序列：每条 DAPC 经过 FADE TIME 渐变，多次 DAPC 看上去是断断续续的跳变；"
        "2) **本 FB** + 连续 DAPC：平滑连续的自定义曲线。"
    ),
    "related": (
        "[`FB_DALIV2DirectArcPowerControl`](FB_DALIV2DirectArcPowerControl.md)、"
        "[`FB_DALIV2SetFadeTime`](../part102_low_config/FB_DALIV2SetFadeTime.md)"
    ),
    "tcpou_decls": D_BASIC,
    "tcpou_inputs_assigns": A_BASIC,
    "tcpou_scenario": "启用 short addr 0 灯的 DAPC 序列模式，准备 PLC 自己实现平滑渐变。",
    "tcpou_value": "解锁 PLC 自定义渐变曲线的能力。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿启用序列模式。\n"
        "3. 紧接着每 100 ms 触发一次 P_Demo_FB_DALIV2DirectArcPowerControl（PLC 循环或定时器）"
        "亮度从 0 递增到 254。\n"
        "4. 灯应平滑渐亮（不被 FADE TIME 影响）。\n"
        "5. 停止下发 DAPC 后等 200 ms 序列模式自动退出。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
