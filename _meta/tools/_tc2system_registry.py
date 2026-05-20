# Tc2_System content registry. Per 2026-05-11 charter B/C/D/E rules.
# Each entry hand-curated against PDF v1.17.3 + InfoSys topic pages.

REG = {}


def _add(name, **kw):
    kw.setdefault("var_desc", {})
    kw.setdefault("pitfalls", [])
    kw.setdefault("related", [])
    kw.setdefault("status", "verified")
    kw.setdefault("return_kind", "NONE")
    kw.setdefault("xml_vars", [])
    kw.setdefault("xml_call", "")
    REG[name] = kw


# Common var descriptions used across file FBs
_VD_FILE_ADS = {
    "sNetId": "目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。",
    "hFile": "文件句柄，由 `FB_FileOpen` 调用成功后返回的 `hFile`。所有后续读 / 写 / 关闭都要传同一个句柄。",
    "bExecute": "上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。",
    "tTimeout": "ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。",
    "bBusy": "TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。",
    "bError": "TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。",
    "nErrId": "ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。",
}


# =================== File function blocks (14) ===================

_add(
    "FB_FileOpen",
    summary=(
        "FB_FileOpen 通过 ADS 异步打开或新建一个文件，并返回文件句柄 `hFile`。"
        "`hFile` 是后续 `FB_FileRead` / `FB_FileWrite` / `FB_FileGets` / `FB_FilePuts` / `FB_FileSeek` / `FB_FileTell` / `FB_FileClose` 操作的唯一入口标识。"
        "本 FB 必须周期调用，状态机走完 `bExecute` 上升沿 → `bBusy = TRUE` → `bBusy = FALSE` 且 `bError = FALSE` 才算成功，得到的 `hFile` 不为 0。\n\n"
        "**适用范围限制**：PDF 明确指出本 FB 不适合实时高频日志写入（每周期写一条会撑爆 ADS 队列），高吞吐量日志应改用 TF3500 TwinCAT Analytics Logger 这一付费产品。"
    ),
    behavior=(
        "**调用方式**：本 FB 是异步 ADS 调用包装，必须每个 PLC 周期调用一次直到 `bBusy` 复位为 FALSE。`bExecute` 上升沿后，`bBusy` 立刻置 TRUE 并启动一次 ADS 请求；ADS 应答返回后 `bBusy` 复位，`bError` 与 `nErrId` 给出结果，成功时 `hFile` 装载新句柄。\n\n"
        "**`nMode` 模式位掩码**（可以 OR 组合，类似 C 语言的 `fopen`）：\n\n"
        "- `FOPEN_MODEREAD`（r）：只读打开，文件必须存在，否则报错。\n"
        "- `FOPEN_MODEWRITE`（w）：只写打开，文件存在则被截断；不存在则新建。\n"
        "- `FOPEN_MODEAPPEND`（a）：追加写打开，写指针始终在末尾；不存在则新建。\n"
        "- `OR FOPEN_MODEPLUS`（+）：与 r / w / a 组合，得到读 + 写模式（r+ / w+ / a+）。`a+` 必须指定有效存储路径，否则报错 1804。\n"
        "- `FOPEN_MODEBINARY`（b） / `FOPEN_MODETEXT`（t）：二进制模式 / 文本模式。二进制按字节原样读写；文本模式在 Windows 上做 CR/LF ↔ LF 自动转换。\n\n"
        "**`ePath` 路径基准**：决定 `sPathName` 是绝对路径还是相对于某个 TwinCAT 系统路径。常用值：`PATH_GENERIC` 通用绝对路径、`PATH_BOOTPATH` TwinCAT Boot 目录、`PATH_GENERIC_USERDATA` 用户数据目录、`PATH_USERPATH1..4` 自定义路径。默认 `PATH_GENERIC`。\n\n"
        "**`hFile = 0` 的语义**：当 `bError = TRUE` 时 `hFile` 通常为 0，**不可**作为合法句柄传给后续读写。\n\n"
        "**`a+` 路径要求**：以 `FOPEN_MODEAPPEND OR FOPEN_MODEPLUS` 打开新文件时，PDF 明确指出必须能解析出有效路径，否则返回错误号 1804。\n\n"
        "**追加模式细节**：`a` / `a+` 模式下所有写操作都强制在文件末尾进行，`FB_FileSeek` 不能改变写位置（读位置可改）。"
    ),
    pitfalls=[
        ("**路径只能本地**：`sNetId` 即使填了远端 NetID，路径仍是『目标 PC 的本地路径』，不支持 UNC `\\\\server\\share\\...` 网络路径，PDF 明确指出。", False),
        ("**`hFile` 必须 `FB_FileClose`**：打开后未关闭会导致目标 PC 上文件句柄泄漏，长时间运行可能耗尽系统句柄；建议用结构化状态机或 `FB_FileLoad` / `FB_FileSave` 风格的封装。", False),
        ("**`a+` 模式必须能解析路径**：相对路径 + `PATH_GENERIC` 经常报 1804；切到 `PATH_GENERIC_USERDATA` 或填绝对路径解决。", False),
        ("**`tTimeout` 默认 5 秒太短**：大文件 / 远程网络 / 慢 SD 卡场景下 5 秒可能不够，建议至少 30 秒；写 100MB 以上文件用 60+ 秒。", True),
        ("**实时性陷阱**：每个 PLC 周期开一次文件并不会让 `hFile` 更早返回，反而把 ADS 队列堵满。建议把 `FB_FileOpen` 放在状态机的 `INIT` 步而不是 `MAIN` 循环。", True),
        ("**线程独占**：同一文件不要在多个任务里同时打开同一句柄；多个 FB_FileOpen 实例同时打开同一文件可能拿到不同句柄但底层文件锁冲突。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "sPathName": "要打开 / 新建的文件路径（绝对或相对于 `ePath` 基准）。**只能本地路径**，不支持 UNC / 网络路径。",
        "nMode": "打开模式位掩码（`FOPEN_MODEREAD` / `FOPEN_MODEWRITE` / `FOPEN_MODEAPPEND` / `FOPEN_MODEPLUS` / `FOPEN_MODEBINARY` / `FOPEN_MODETEXT`，可 OR 组合）。",
        "ePath": "TwinCAT 系统路径基准枚举（如 `PATH_GENERIC` / `PATH_BOOTPATH` / `PATH_GENERIC_USERDATA`）。默认 `PATH_GENERIC`。",
        "hFile": "**输出参数**：打开成功后的文件句柄，传给后续 `FB_FileRead` / `FB_FileWrite` / `FB_FileClose`。`bError = TRUE` 时通常为 0，不可使用。",
    },
    scenario="设备启动时打开一份配方 INI 文件准备读取，或在班次切换时新建一个 CSV 日志文件继续追加运行参数。",
    value="不用本 FB 时必须自己组装 ADS Write 命令（IndexGroup `0x10005` / IndexOffset 不同模式）并手动 wrap busy / done 状态机，约 40 行代码。本 FB 封装好了这套时序。",
    alt=(
        "- 直接调用 `ADSWRITE` / `ADSREAD` 操控文件 ADS 接口：能用但要自己跟踪 IndexGroup 与状态机，错一字节就挂。\n"
        "- TF3500 Analytics Logger：付费插件，性能远超本 FB，适合高吞吐日志。\n"
        "- `FB_FileLoad` / `FB_FilePuts` 一次性 API：场景固定（整文件读 / 单行写）时更简洁，但灵活性差。"
    ),
    xml_scen="设备启动后在 D 盘新建一份 CSV 文件 'D:/log/process.csv' 用于追加写入工艺参数；首次打开后保留 hFile 供后续 FB_FilePuts 使用。",
    xml_val="不用本 FB 需要自己拼 ADS Write 报文 + 跟 IndexGroup 0x10005 状态，本 FB 一行调用就拿到 hFile。",
    xml_verify="登录后置 bOpenRequest := TRUE → 观察 hOpenedFile 在 1-2 PLC 周期后非零；置 FALSE 后再次置 TRUE 重新打开；故意改 sFilePath 到不存在的盘符 → nErrIdLast = 0x70C。",
    xml_vars=[
        ("fbFileOpen", "FB_FileOpen", None, "FB_FileOpen 实例"),
        ("sFilePath", "T_MaxString", "'D:/log/process.csv'", "目标 CSV 文件本地绝对路径"),
        ("bOpenRequest", "BOOL", None, "在线写 TRUE 触发一次打开"),
        ("hOpenedFile", "UINT", None, "成功后存放文件句柄；0 = 未打开"),
        ("bOpenDone", "BOOL", None, "TRUE = 上次打开成功"),
        ("bOpenError", "BOOL", None, "TRUE = 上次打开失败"),
        ("nErrIdLast", "UDINT", None, "最近一次 ADS 错误号（0x70C / 0x70D / 0x745 等）"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "// 注：单次完整调用形式；nMode 用 'wa+' 组合 = 追加读写文本\n"
        "// FOPEN_MODEWRITE(2) OR FOPEN_MODEAPPEND(4) OR FOPEN_MODEPLUS(16) OR FOPEN_MODETEXT(64) = 86\n"
        "// 这里直接拼数字常量，避免引入额外的 enum 依赖\n"
        "fbFileOpen(\n"
        "    sNetId    := '',\n"
        "    sPathName := sFilePath,\n"
        "    nMode     := FOPEN_MODEAPPEND OR FOPEN_MODEPLUS OR FOPEN_MODETEXT,\n"
        "    ePath     := PATH_GENERIC,\n"
        "    bExecute  := bOpenRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bOpenError,\n"
        "    nErrId    => nErrIdLast,\n"
        "    hFile     => hOpenedFile\n"
        ");\n\n"
        "// 业务侧：把 bBusy 落沿当作 done\n"
        "bOpenDone := (NOT bBusyMon) AND (NOT bOpenError) AND (hOpenedFile <> 0);\n"
    ),
    related=["FB_FileClose", "FB_FileRead", "FB_FileWrite", "FB_FileGets", "FB_FilePuts", "FB_FileLoad", "FB_FileSeek", "FB_FileTell", "FB_FileDelete"],
)

_add(
    "FB_FileClose",
    summary=(
        "FB_FileClose 通过 ADS 异步关闭一个由 `FB_FileOpen` 打开的文件，把缓冲区落盘并释放句柄。"
        "每个成功的 `FB_FileOpen` 调用必须配对一次 `FB_FileClose`，否则目标 PC 上文件句柄持续被占用，长时间运行会耗尽系统句柄表。"
    ),
    behavior=(
        "**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿触发，ADS 异步关闭文件并刷盘。关闭后 `hFile` 在外部仍存有数值，但调用方必须主动清零以防误用：典型代码 `IF NOT bBusyMon AND NOT bErrMon THEN hFile := 0; END_IF;`。\n\n"
        "**关闭语义**：关闭操作会强制刷写 OS 文件缓冲，对于以 `FOPEN_MODEWRITE` 或 `FOPEN_MODEAPPEND` 打开的文件，未 Close 时落盘不保证，断电易导致写入丢失。\n\n"
        "**错误情况**：`hFile` 已经被关过、或不属于本 PC、或 ADS 通讯失败会导致 `bError = TRUE` 并在 `nErrId` 返回错误号。重复 Close 同一句柄通常返回错误而不会崩溃。"
    ),
    pitfalls=[
        ("**未关闭句柄泄漏**：长时间运行 / 频繁 Open 不 Close 的程序最终会耗尽 OS 句柄表，表现为后续 `FB_FileOpen` 永远 `bError = TRUE`。", False),
        ("**必须主动清零 `hFile` 本地变量**：FB 不会把外部 `hFile` 自动清零，重复传递已关闭的句柄给读 / 写会得到错误号。", False),
        ("**程序异常退出未 Close**：在线下载、PLC Reset、调试中断都不会自动 Close；建议把 Close 放在 `FB_Exit` / `FB_Reinit` 钩子中。", True),
        ("**断电不刷盘**：未 Close 时缓冲区可能仍在 OS 缓存，CX 突然断电会丢数据。建议关键日志写完一行就主动 Close，或配合 `FB_S_UPS_*` 在掉电时强制 Close。", True),
    ],
    var_desc={**_VD_FILE_ADS, "hFile": "要关闭的文件句柄，必须是 `FB_FileOpen` 成功返回的 `hFile`。"},
    scenario="班次结束时关闭整天累计的工艺日志文件，确保所有缓冲数据落盘以防夜间断电丢失。",
    value="封装好 ADS 关闭命令的 busy / done 状态机；不用本 FB 要自己组装 IndexGroup 0x10004 ADS Write 命令并跟踪状态。",
    alt=(
        "- `FB_FileLoad`：读模式下可以一次性读完并自动关闭，无须手动 Close。\n"
        "- 直接 `ADSWRITE`：能用但要自己跟状态。"
    ),
    xml_scen="把之前 FB_FileOpen 拿到的 hFile 安全关闭，把缓冲区数据强制刷盘。",
    xml_val="不用本 FB 就要自己拼 ADS Write 0x10004 命令并跟状态。",
    xml_verify="在线置 bCloseRequest := TRUE → 观察 bBusy 跳起后落下 → hOpenedFile 在业务侧被清零；故意传一个 0 句柄 → bCloseError = TRUE。",
    xml_vars=[
        ("fbFileClose", "FB_FileClose", None, "FB_FileClose 实例"),
        ("hOpenedFile", "UINT", None, "之前 FB_FileOpen 得到的句柄"),
        ("bCloseRequest", "BOOL", None, "在线写 TRUE 触发一次关闭"),
        ("bCloseDone", "BOOL", None, "TRUE = 关闭成功"),
        ("bCloseError", "BOOL", None, "TRUE = 关闭失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "// 单次完整调用：关闭文件并把本地句柄清零\n"
        "fbFileClose(\n"
        "    sNetId   := '',\n"
        "    hFile    := hOpenedFile,\n"
        "    bExecute := bCloseRequest,\n"
        "    tTimeout := T#10S,\n"
        "    bBusy    => bBusyMon,\n"
        "    bError   => bCloseError,\n"
        "    nErrId   => nErrIdLast\n"
        ");\n\n"
        "// 业务侧：busy 落沿且无错则视为关闭成功，清掉本地句柄\n"
        "bCloseDone := (NOT bBusyMon) AND (NOT bCloseError) AND bCloseRequest;\n"
        "IF bCloseDone THEN\n"
        "    hOpenedFile := 0;\n"
        "END_IF;\n"
    ),
    related=["FB_FileOpen", "FB_FileRead", "FB_FileWrite"],
)
