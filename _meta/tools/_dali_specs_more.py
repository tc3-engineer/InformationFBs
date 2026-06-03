#!/usr/bin/env python3
"""Generate additional anchor FBs across categories."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"
A_BASIC = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityMiddle,"
)
D_BASIC = "    nLampAddr        : BYTE := 0;\n\n"

SPECS = []

# Low-level special / addressing FBs
SPECS.append({
    "name": "FB_DALIV2Initialise",
    "section": "4.1.2.3.6.2",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142810443.html",
    "summary": (
        "**进入寻址初始化模式**——DALI 寻址流程的开端命令。本 FB 让灯具进入寻址模式（接受后续的 "
        "`SearchAddr` / `ProgramShortAddress` 等命令）。本命令必须在两次 200 ms 间隔内重发以"
        "确认（DALI 协议反误触发保护）。\n\n"
        "通常被 `FB_DALIV2AddressingRandomAddressing` 等高层 FB 内部使用；工程上很少直接调用。"
    ),
    "behavior": (
        "**调用方式**：`bStart` 上升沿；本 FB 下发 `INITIALISE` 命令（两次 200 ms 内）；灯具进入"
        "寻址模式持续 15 分钟（之后自动退出，需重发或用 `FB_DALIV2Terminate` 主动结束）。\n\n"
        "**寻址模式下灯具行为**：仅响应 `SearchAddr / ProgramShortAddress / Withdraw / "
        "VerifyShortAddress / QueryShortAddress / Terminate` 这几条寻址相关命令；普通调光命令被忽略。\n\n"
        "**广播模式的特殊语义**：`eAddrType := Broadcast` 让所有灯进入寻址模式；`eAddrType := Short` + "
        "`nAddr := X` 让短地址 X 的灯进入寻址模式（用于二分搜索单灯）；`eAddrType := Group` 让某组"
        "的灯进入。\n\n"
        "**典型陷阱**：① 寻址模式 15 分钟过长——开发调试时容易遗忘 `Terminate`；② 寻址模式期间下发"
        "普通调光命令灯不响应，调试时会迷惑；③ 通常通过高层 `AddressingRandomAddressing` 间接使用。"
    ),
    "pitfalls": [
        "寻址模式持续 15 分钟，开发期间务必用 `FB_DALIV2Terminate` 主动结束。",
        "寻址模式下灯具忽略普通命令，调试要注意。",
        "通常通过高层 FB 间接使用，工程很少直接调本 FB。",
    ],
    "scenario": "DALI 寻址流程的开端——通常由 `FB_DALIV2AddressingRandomAddressing` 内部使用。",
    "value": "暴露 DALI 寻址协议的初始化命令；为定制寻址流程提供基础。",
    "alternative": "通常用高层 `FB_DALIV2AddressingRandomAddressing` 间接调用。",
    "related": (
        "[`FB_DALIV2Randomise`](FB_DALIV2Randomise.md)、"
        "[`FB_DALIV2SearchAddr`](FB_DALIV2SearchAddr.md)、"
        "[`FB_DALIV2Terminate`](FB_DALIV2Terminate.md)、"
        "[`FB_DALIV2AddressingRandomAddressing`](../part102_addressing/FB_DALIV2AddressingRandomAddressing.md)"
    ),
    "tcpou_decls": D_BASIC,
    "tcpou_inputs_assigns": A_BASIC,
    "tcpou_scenario": "底层寻址：让所有灯进入寻址模式。",
    "tcpou_value": "底层寻址命令。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 把 eAddrType 改为 eDALIV2AddrTypeBroadcast 让全部灯进入寻址模式。\n"
        "3. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "4. 灯具应进入寻址模式（普通命令被忽略 15 分钟）。\n"
        "5. 用 P_Demo_FB_DALIV2Terminate 主动结束寻址模式。"
    ),
})

SPECS.append({
    "name": "FB_DALIV2Terminate",
    "section": "4.1.2.3.6.14",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142831243.html",
    "summary": "**结束寻址模式**——主动让所有处于寻址模式的灯具退出，恢复对普通调光命令的响应。",
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `TERMINATE` 命令；所有寻址模式中的灯具立即退出。\n\n"
        "**典型应用**：寻址流程结束 / 调试期间手动退出寻址模式 / 用 `FB_DALIV2Initialise` 后清理状态。\n\n"
        "**与寻址模式自动过期对比**：寻址模式 15 分钟自动过期；本 FB 让它立即结束。\n\n"
        "**典型陷阱**：① 本命令对所有处于寻址模式的灯都生效（无寻址参数，全广播效果）；"
        "② 部分定制寻址流程结束时忘了调本 FB，导致灯具 15 分钟不响应普通命令——是新手最常见调试陷阱。"
    ),
    "pitfalls": [
        "本命令是广播效果——结束所有寻址模式灯具。",
        "调试期间用 `FB_DALIV2Initialise` 后务必用本 FB 清理，否则灯具 15 分钟不响应。",
    ],
    "scenario": "寻址流程结束的清理命令；调试时手动退出寻址模式。",
    "value": "替代等待 15 分钟自动过期；立即恢复灯具正常工作。",
    "alternative": "等 15 分钟自动过期。",
    "related": (
        "[`FB_DALIV2Initialise`](FB_DALIV2Initialise.md)、"
        "[`FB_DALIV2Withdraw`](FB_DALIV2Withdraw.md)"
    ),
    "tcpou_decls": D_BASIC,
    "tcpou_inputs_assigns": A_BASIC,
    "tcpou_scenario": "结束寻址模式。",
    "tcpou_value": "调试清理用。",
    "tcpou_verify": (
        "1. 先用 P_Demo_FB_DALIV2Initialise 让灯具进入寻址模式。\n"
        "2. 在线 bTrigger 触发本 FB；等 bBusy 回 FALSE。\n"
        "3. 灯具应立即退出寻址模式，普通调光命令恢复响应。"
    ),
})

SPECS.append({
    "name": "FB_DALIV2Randomise",
    "section": "4.1.2.3.6.6",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142823179.html",
    "summary": (
        "**让灯具生成 24-bit 随机地址**——`FB_DALIV2Initialise` 之后的下一步：让所有处于寻址模式的灯"
        "在自己内部生成一个 24-bit 随机地址（`RANDOM ADDRESS` 寄存器）。这是 DALI 寻址协议的核心："
        "通过随机地址做二分搜索找出每盏灯并分配短地址。"
    ),
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `RANDOMISE` 命令（双指令防误触发）；灯具内部生成"
        "24-bit 伪随机数存入 `RANDOM ADDRESS` 寄存器。生成约 100 ms。\n\n"
        "**生成方式**：DALI 协议不规定具体随机算法；厂家自定（典型用灯具序列号 + 时间戳 hash）。"
        "理论上两盏灯生成相同地址的概率约 1/2^24（极低），但工程上应在 randomise 后用 `VerifyShortAddress` "
        "校验所有灯都不同。\n\n"
        "**典型应用**：DALI 寻址流程的第二步（Initialise → Randomise → SearchAddr 二分搜索）。"
        "通常由高层 `FB_DALIV2AddressingRandomAddressing` 内部使用。\n\n"
        "**典型陷阱**：本 FB 之前必须先 `Initialise` 让灯进入寻址模式；否则命令被普通灯具忽略。"
    ),
    "pitfalls": [
        "前置必须 `FB_DALIV2Initialise`。",
        "生成时间约 100 ms；Randomise 后等待再做 SearchAddr。",
        "通常通过高层 FB 间接使用。",
    ],
    "scenario": "DALI 寻址流程的第二步——通常由 `FB_DALIV2AddressingRandomAddressing` 内部使用。",
    "value": "暴露 DALI 寻址协议中的随机地址生成命令。",
    "alternative": "通过高层 FB 间接使用。",
    "related": (
        "[`FB_DALIV2Initialise`](FB_DALIV2Initialise.md)、"
        "[`FB_DALIV2SearchAddr`](FB_DALIV2SearchAddr.md)、"
        "[`FB_DALIV2QueryRandomAddress`](../part102_low_queries/FB_DALIV2QueryRandomAddress.md)"
    ),
    "tcpou_decls": D_BASIC,
    "tcpou_inputs_assigns": A_BASIC,
    "tcpou_scenario": "生成所有寻址模式灯具的随机地址。",
    "tcpou_value": "底层寻址命令。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 先用 P_Demo_FB_DALIV2Initialise 让灯进入寻址模式。\n"
        "3. 在线 bTrigger 触发本 FB；等 bBusy 回 FALSE。\n"
        "4. 用 P_Demo_FB_DALIV2QueryRandomAddress 应能读到非零的 24-bit 随机地址。"
    ),
})

SPECS.append({
    "name": "FB_DALIV2ProgramShortAddress",
    "section": "4.1.2.3.6.4",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142820107.html",
    "summary": (
        "**寻址过程中给当前已选中的灯写入短地址**——DALI 寻址流程中通过 `SearchAddr` 二分查找到"
        "一盏灯后，用本 FB 给它写入短地址。`nShortAddress` 经过 DALI 协议特殊编码（`(addr<<1)|1`）。\n\n"
        "**与 `FB_DALIV2SetShortAddress` 区别**：本 FB 用于寻址过程中（已 SELECT 一盏灯）写入第一个"
        "短地址；后者用于正常运行时改地址。"
    ),
    "inputs_desc": {"nShortAddress": "目标短地址（0..63）"},
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `PROGRAM SHORT ADDRESS` 命令带编码字节；当前 SELECT 的"
        "灯具更新短地址寄存器（EEPROM）。\n\n"
        "**前置条件**：本 FB 之前必须有 `FB_DALIV2SearchAddr` 序列把目标灯精确选中。否则命令对所有"
        "处于寻址模式但符合搜索条件的灯都生效，可能导致多灯同短地址。\n\n"
        "**典型应用**：DALI 寻址流程中分配第一个短地址。通常由高层 FB 内部使用。\n\n"
        "**典型陷阱**：① 没 SELECT 直接 ProgramShortAddress 多灯同地址；② 本命令是 SELECTED 灯"
        "的特定操作——不带 `nAddr` 参数走 broadcast。"
    ),
    "pitfalls": [
        "必须前置 `FB_DALIV2SearchAddr` 精确 SELECT 目标灯。",
        "本命令对当前 SELECTED 灯生效，与寻址命令的 nAddr 无关。",
        "通常通过高层 `AddressingRandomAddressing` 间接使用。",
    ],
    "scenario": "DALI 寻址流程中分配短地址——通常由高层 FB 内部使用。",
    "value": "暴露 DALI 寻址协议的短地址编程命令。",
    "alternative": (
        "1) `FB_DALIV2SetShortAddress`：正常运行时改地址；"
        "2) **本 FB**：寻址过程中分配。"
    ),
    "related": (
        "[`FB_DALIV2SetShortAddress`](../part102_low_config/FB_DALIV2SetShortAddress.md)、"
        "[`FB_DALIV2SearchAddr`](FB_DALIV2SearchAddr.md)、"
        "[`FB_DALIV2QueryShortAddress`](FB_DALIV2QueryShortAddress.md)"
    ),
    "tcpou_decls": D_BASIC + "    nNewShortAddr    : BYTE := 0;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nShortAddress    := nNewShortAddr,",
    "tcpou_scenario": "寻址过程中给 SELECT 灯写短地址 0。",
    "tcpou_value": "底层寻址命令。",
    "tcpou_verify": (
        "1. 必须先完成 Initialise + Randomise + SearchAddr 序列把目标灯 SELECT 上。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2VerifyShortAddress 应能用 short addr 0 验证到该灯。"
    ),
})


# === High-Level Sequencer ===
SPECS.append({
    "name": "FB_DALIV2Sequencer",
    "section": "4.1.1.1.2.10",
    "subdir": "part102_power_control",
    "category_display": "Part 102 / Power Control",
    "infosys": f"{INFOSYS_BASE}142922379.html",
    "summary": (
        "**DALI 序列化亮度场景执行 FB（high-level）**——按 `ST_DALIV2SequenceTable` 表里定义的多步"
        "亮度 + 时长，自动按顺序播放：第一步亮度 → 等 T1 → 第二步 → 等 T2... 直到最后一步。"
        "支持 `bToggle` 在开 / 关之间切换、`bRestart` 重新开始当前序列。\n\n"
        "适合复杂的多步定时灯效场景：舞台灯光秀、店铺橱窗循环展示、博物馆展品光照编程等。"
    ),
    "inputs_desc": {
        "bToggle": "上升沿在 ON（启动序列） / OFF（停止）之间切换",
        "bRestart": "上升沿重新开始当前序列",
        "tCycleActualLevelMasterDev": "后台读 master 亮度周期",
        "nMasterDevAddr": "master 设备短地址",
        "nAddr": "目标地址",
        "eAddrType": "寻址类型",
        "nOptions": "序列选项（保留 + 循环模式等）",
    },
    "outputs_desc": {
        "nActualLevelMasterDev": "master 当前亮度",
        "bSequenceActive": "序列正在播放",
        "nCurrentStep": "当前播放的步号",
        "bBusy": "命令派发中",
        "bError": "出错",
        "nErrorId": "错误号",
    },
    "behavior": (
        "**序列定义**：通过 `stSequenceTable` VAR_IN_OUT 提供——结构包含步数 `nSteps`、每步亮度数组 "
        "`arrLevel[0..49]`、每步停留时间数组 `arrTime[0..49]`。最多 50 步。\n\n"
        "**播放控制**：`bToggle = TRUE 上升沿` 启动序列从第 0 步开始；`bToggle = FALSE` 时序列停止"
        "（灯保持当前亮度，下次 toggle 重新开始）。`bRestart` 上升沿不影响 toggle 状态、重置回第 0 步。\n\n"
        "**循环模式**：`nOptions` 的 bit0 决定到最后一步后是否循环——0 = 一次性、播完停在最后一步；"
        "1..31 = 保留位。\n\n"
        "**典型应用**：店铺橱窗 24 小时光照编程（早晨渐亮、白天柔和、傍晚暖色、夜间动态）；"
        "舞台灯光秀（按音乐节拍预编好的灯效）；博物馆展品照明（白天展示 vs 夜间维护）。\n\n"
        "**典型陷阱**：① 序列时长之和超过你打算的总时间——序列结束后停在最后一步可能不是你想要的；"
        "② `bToggle = FALSE` 中断后没有暂停的概念，下次启动从头开始；③ 序列表用 retain 变量保持"
        "工程参数，避免每次开机重写。"
    ),
    "pitfalls": [
        "最多 50 步。",
        "`bToggle = FALSE` 是停止不是暂停。",
        "序列结束行为按 `nOptions` 决定。",
        "`stSequenceTable` 建议用 retain 变量。",
    ],
    "scenario": "店铺橱窗 24 小时光照编程：早 6 点渐亮、9-21 点零售模式、22 点降亮、24 点关。",
    "value": (
        "替代 PLC 自己写 50 个 TON + 状态机；序列表数据驱动，运维只改表不改代码。"
    ),
    "alternative": (
        "1) 自己写 TON + 状态机：代码长且漏边界；"
        "2) `FB_DALIV2Dimmer1Switch` 等：单事件触发型，不适合序列；"
        "3) **本 FB**：多步定时灯效标准方案。"
    ),
    "related": (
        "[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)、"
        "`ST_DALIV2SequenceTable`（DUT 结构）、"
        "[`FB_DALIV2Ramp`](FB_DALIV2Ramp.md)（单步线性渐变）"
    ),
    "tcpou_decls": (
        "    bSeqToggle       : BOOL;\n"
        "    bSeqRestart      : BOOL;\n"
        "    stSeqTable       : ST_DALIV2SequenceTable;\n"
        "    nGroupAddr       : BYTE := 1;\n"
        "    nMasterShortAddr : BYTE := 0;\n"
        "    bSeqRunning      : BOOL;\n"
        "    nStep            : BYTE;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bToggle                     := bSeqToggle,\n"
        "    bRestart                    := bSeqRestart,\n"
        "    tCycleActualLevelMasterDev  := T#2S,\n"
        "    nMasterDevAddr              := nMasterShortAddr,\n"
        "    nAddr                       := nGroupAddr,\n"
        "    eAddrType                   := eDALIV2AddrTypeGroup,\n"
        "    nOptions                    := 0,"
    ),
    "tcpou_scenario": "店铺橱窗序列灯效（需在 stSeqTable 配置具体步）。",
    "tcpou_value": "序列灯效数据驱动配置。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在 stSeqTable 配置：nSteps := 3 / arrLevel := [50, 200, 0] / arrTime := [T#5S, T#10S, T#3S]。\n"
        "3. 在线 bSeqToggle 一次上升沿。\n"
        "4. bSeqRunning 应 TRUE，灯组应按序：50 亮 5 秒 → 200 亮 10 秒 → 0（关）3 秒 → 停。\n"
        "5. nStep 应同步显示当前步号 0..2。"
    ),
})

# === Settings high-level ===
SPECS.append({
    "name": "FB_DALIV2GetSettings",
    "section": "4.1.1.1.3.1",
    "subdir": "part102_settings",
    "category_display": "Part 102 / Settings (High-Level)",
    "infosys": f"{INFOSYS_BASE}142927643.html",
    "summary": (
        "**批量读取灯具所有 DALI 配置寄存器**——一次调用读出灯具的 `ACTUAL DIM LEVEL`、`POWER ON LEVEL`、"
        "`SYSTEM FAILURE LEVEL`、`MIN VALUE`、`MAX VALUE`、`FADE RATE`、`FADE TIME`、`RANDOM ADDRESS`、"
        "`SHORT ADDRESS`、`SEARCH ADDRESS`、组归属、场景 0..15 值等约 30 项配置。结果填入 `ST_DALIV2DeviceSettings`。\n\n"
        "**工程上线后批量校验所有灯配置时的核心 FB**——比逐个调 `QueryXxx` 快得多。"
    ),
    "inputs_desc": {
        "bStart": "上升沿启动批量读取",
        "bAbort": "上升沿提前终止（已读的字段保留）",
        "nAddr": "目标短地址",
        "eAddrType": "应为 `eDALIV2AddrTypeShort`（广播无意义）",
        "eCommandPriority": "优先级（建议 Low）",
    },
    "outputs_desc": {
        "bBusy": "读取中",
        "bError": "出错",
        "nErrorId": "错误号",
        "bDone": "读取完成",
    },
    "behavior": (
        "**整体流程**：本 FB 内部依次调用约 30 条 DALI 查询命令；每条间隔约 30 ms（受 DALI 总线时间限制）；"
        "总耗时约 1 秒。结果实时填入 `stSettings` VAR_IN_OUT。\n\n"
        "**优先级**：建议 `Low`——读取期间约 30 条命令排队，用 Low 不影响主业务调光命令。\n\n"
        "**典型应用**：（1）工程上线批量检查所有灯配置是否符合设计文档；（2）HMI 维护页"
        "显示某灯具完整状态；（3）现场调试灯具行为异常时查全部寄存器找原因。\n\n"
        "**典型陷阱**：① 读取期间灯具被其它 FB 改配置 → 读到不一致的快照；② 广播无意义（多灯应答冲突）；"
        "③ `stSettings` 结构较大（约 30 字节），多个 FB 实例共用一个 stSettings 时要互斥访问。"
    ),
    "pitfalls": [
        "广播无意义——必须单灯。",
        "总耗时约 1 秒，避免在主循环里同步等。",
        "`stSettings` 较大，多 FB 共用需互斥。",
    ],
    "scenario": (
        "工程上线验收——按设计文档校验所有灯具配置是否正确。本 FB 循环对每盏 short addr 调用，"
        "PLC 把读到的 stSettings 与设计文档对比，不符的列入整改清单。"
    ),
    "value": "替代逐个调 ~30 条 QueryXxx FB；一次调用拿全部配置，HMI / 验收效率高。",
    "alternative": (
        "1) 逐个调 `FB_DALIV2QueryXxx`：代码冗长、效率低；"
        "2) **本 FB**：批量读取，标准方案。"
    ),
    "related": (
        "[`FB_DALIV2GetSettingsSingleDevice`](FB_DALIV2GetSettingsSingleDevice.md)、"
        "[`FB_DALIV2SetSettings`](FB_DALIV2SetSettings.md)、"
        "`ST_DALIV2DeviceSettings`（DUT 结构）"
    ),
    "tcpou_decls": (
        "    nLampAddr        : BYTE := 0;\n"
        "    bStartRead       : BOOL;\n"
        "    bAbortRead       : BOOL;\n"
        "    stSettings       : ST_DALIV2DeviceSettings;\n"
        "    bReadDone        : BOOL;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bStart           := bStartRead,\n"
        "    bAbort           := bAbortRead,\n"
        "    nAddr            := nLampAddr,\n"
        "    eAddrType        := eDALIV2AddrTypeShort,\n"
        "    eCommandPriority := eDALIV2CommandPriorityLow,"
    ),
    "tcpou_scenario": "上线验收：读 short addr 0 灯具的全部配置寄存器。",
    "tcpou_value": "一次拿全 ~30 项配置，HMI / 验收。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bStartRead 一次上升沿；fb.bBusy 应 TRUE 约 1 秒。\n"
        "3. bDone = TRUE 后检查 stSettings 各字段：MAX VALUE / MIN VALUE / FADE TIME / 短地址等。\n"
        "4. 与设计文档对比；不符项列入整改清单。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
