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


_add(
    "FB_FileRead",
    summary=(
        "FB_FileRead 通过 ADS 从一个已经用 `FB_FileOpen` 打开的文件读取指定字节数到本地缓冲区。"
        "读取的起点是当前文件指针位置；调用结束后文件指针自动向前推进读取的字节数，下次再调可继续读后续内容。"
        "对于按记录顺序消费的二进制 / 文本文件，本 FB 是流式读取的主力。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次读取，`bBusy` 期间不响应新触发。读完后 `bBusy = FALSE`，`cbRead` 给出实际读到的字节数（**可能小于 `cbReadLen`**：到文件末尾或文本模式下提前遇到换行）。\n\n"
        "**缓冲区责任**：`pReadBuff` 由调用方提供，必须保证 `cbReadLen` 字节可写。常见写法 `pReadBuff := ADR(myBuffer)` + `cbReadLen := SIZEOF(myBuffer)`。本 FB 不做越界检查，越界会写坏邻近变量。\n\n"
        "**EOF 检测**：`bEOF` 输出为 TRUE 表示本次读到达文件末尾；与 `cbRead = 0` 共同用于循环退出条件。\n\n"
        "**文本 vs 二进制模式**：文本模式下 OS 会做 CR/LF → LF 转换，`cbRead` 是转换后的字节数，可能小于物理文件偏移推进量；要按字节精确读用 `FOPEN_MODEBINARY`。"
    ),
    pitfalls=[
        ("**`pReadBuff` 缓冲区越界**：`cbReadLen > SIZEOF(buffer)` 会让 FB 越界写本地变量，导致幽灵 bug 而无任何错误提示。**永远** `cbReadLen := SIZEOF(buf)`，不要手填常量。", False),
        ("**忘检 EOF 死循环**：在 while 中调用 `FB_FileRead` 必须用 `cbRead = 0 OR bEOF` 退出条件，否则文件末尾后会无限触发返回 0 字节。", False),
        ("**短读不是错误**：文本模式下可能 `cbRead < cbReadLen` 但 `bError = FALSE`，业务侧不能把『短读』当成错误。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`，`nErrId` 通常是 `0x70C`。", False),
        ("**大文件分段**：单次最大字节数受 ADS 报文上限限制（约 1 MB），更大文件要循环读多次。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "pReadBuff": "读入缓冲区起始地址，调用方用 `ADR(myVar)` 取地址。本 FB 不做边界检查，调用方负责保证 `cbReadLen` 字节可写。",
        "cbReadLen": "本次最多读取的字节数，应等于缓冲区大小 `SIZEOF(buf)`。",
        "cbRead": "**输出**：实际读到的字节数。`< cbReadLen` 可能因到达 EOF / 文本模式换行；`= 0` 通常代表 EOF。",
        "bEOF": "**输出**：TRUE = 本次读到达文件末尾。可与 `cbRead = 0` 联合作循环退出条件。",
    },
    scenario="启动时把存盘的配方 CSV 一次或分块读入内存数组，恢复上次班次的工艺参数。",
    value="封装好 ADS 0x10003 读命令的状态机 + EOF 检测；不用本 FB 要自己跟 ADS 流并解析二进制响应。",
    alt=(
        "- `FB_FileLoad`：整文件一次性读取，自动 Open/Close，对配置文件更省事。\n"
        "- `FB_FileGets`：按行读文本，自带换行截断。"
    ),
    xml_scen="从 D:/log/process.csv 末尾段每次读 256 字节到本地缓冲区，作为离线分析的预读窗口。",
    xml_val="不用本 FB 需要自己拼 ADS 读命令 + 跟 ADS 应答字节解析。",
    xml_verify="在线置 bReadRequest := TRUE → 观察 cbBytesRead 在 1-2 PLC 周期后非零；多次触发后到 EOF → bEofReached := TRUE 且 cbBytesRead = 0。",
    xml_vars=[
        ("fbFileRead", "FB_FileRead", None, "FB_FileRead 实例"),
        ("hOpenedFile", "UINT", None, "前置 FB_FileOpen 拿到的句柄"),
        ("aReadBuffer", "ARRAY[0..255] OF BYTE", None, "本地读入缓冲区（256 字节）"),
        ("bReadRequest", "BOOL", None, "在线写 TRUE 触发一次读取"),
        ("cbBytesRead", "UDINT", None, "本次实际读到的字节数"),
        ("bEofReached", "BOOL", None, "TRUE = 已到 EOF"),
        ("bReadError", "BOOL", None, "TRUE = 读失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "// 单次完整调用：读 256 字节到 aReadBuffer\n"
        "fbFileRead(\n"
        "    sNetId    := '',\n"
        "    hFile     := hOpenedFile,\n"
        "    pReadBuff := ADR(aReadBuffer),\n"
        "    cbReadLen := SIZEOF(aReadBuffer),\n"
        "    bExecute  := bReadRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bReadError,\n"
        "    nErrId    => nErrIdLast,\n"
        "    cbRead    => cbBytesRead,\n"
        "    bEOF      => bEofReached\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileClose", "FB_FileLoad", "FB_FileGets", "FB_FileSeek"],
)

_add(
    "FB_FileWrite",
    summary=(
        "FB_FileWrite 通过 ADS 把本地缓冲区指定字节数写入一个已经用 `FB_FileOpen` 打开的文件。"
        "起点是当前文件指针（追加模式下强制为末尾），写完后指针向前推进 `cbWrite` 字节。"
        "适用于二进制日志 / 数据流的写入；按行写文本用 `FB_FilePuts` 更方便。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次写入。`bBusy` 期间不响应新触发；完成后 `bBusy = FALSE`，`cbWrite` 给出实际写入的字节数。\n\n"
        "**缓冲区责任**：`pWriteBuff` 由调用方提供有效内存地址，`cbWriteLen` 表示要写的字节数，本 FB 不会越界读但会读 `cbWriteLen` 字节，必须保证缓冲区至少有这么多字节。\n\n"
        "**追加模式 vs 写模式**：`FOPEN_MODEAPPEND` 模式下不论指针在哪都从末尾追加；`FOPEN_MODEWRITE` 模式从当前指针位置覆盖式写入。\n\n"
        "**不自动 flush**：本 FB 写入完成只是写到 OS 缓冲，断电仍可能丢；落盘要靠 `FB_FileClose` 触发的 flush。"
    ),
    pitfalls=[
        ("**断电丢数据**：写完不 Close，OS 缓冲区里的数据断电就丢。关键日志写完立刻 Close 或挂 `FB_S_UPS_*` 在掉电时强制 Close。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`，错误号 `0x70C`。", False),
        ("**单次写入上限**：ADS 报文上限约 1 MB，超过要循环多次。", True),
        ("**追加模式下 Seek 无效**：`FB_FileSeek` 改写指针在 `a` / `a+` 模式下对写无效，写仍从末尾。要随机写必须用 `r+` / `w+`。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "pWriteBuff": "要写入的数据缓冲区起始地址，用 `ADR(myVar)`。",
        "cbWriteLen": "本次要写入的字节数。必须 ≤ 缓冲区实际大小。",
        "cbWrite": "**输出**：实际写入的字节数。正常情况 `= cbWriteLen`；< 该值可能因磁盘满或异常。",
    },
    scenario="把每 100 ms 采集到的工艺数据结构（约 64 字节）追加写入二进制流日志，供日终批处理分析。",
    value="封装好 ADS 0x10004 写命令的状态机；不用本 FB 要自己跟 ADS 应答与重发。",
    alt=(
        "- `FB_FilePuts`：按行写文本，自动加 / 不加换行视实现而定，文本日志更方便。\n"
        "- TF3500 Analytics Logger：付费、性能强，适合高吞吐二进制日志。"
    ),
    xml_scen="把一个 64 字节的工艺参数结构追加写到已打开的 D:/log/process.csv 文件末尾。",
    xml_val="封装 ADS 写命令的状态机，省 30 行手写。",
    xml_verify="在线置 bWriteRequest := TRUE → 观察 cbBytesWritten = SIZEOF(stProcessRecord)；故意改 hOpenedFile := 0 → bWriteError = TRUE 且 nErrIdLast = 0x70C。",
    xml_vars=[
        ("fbFileWrite", "FB_FileWrite", None, "FB_FileWrite 实例"),
        ("hOpenedFile", "UINT", None, "前置 FB_FileOpen 拿到的句柄"),
        ("stProcessRecord", "ARRAY[0..63] OF BYTE", None, "要写入的 64 字节工艺数据"),
        ("bWriteRequest", "BOOL", None, "在线写 TRUE 触发一次写入"),
        ("cbBytesWritten", "UDINT", None, "实际写入字节数"),
        ("bWriteError", "BOOL", None, "TRUE = 写失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbFileWrite(\n"
        "    sNetId     := '',\n"
        "    hFile      := hOpenedFile,\n"
        "    pWriteBuff := ADR(stProcessRecord),\n"
        "    cbWriteLen := SIZEOF(stProcessRecord),\n"
        "    bExecute   := bWriteRequest,\n"
        "    tTimeout   := T#10S,\n"
        "    bBusy      => bBusyMon,\n"
        "    bError     => bWriteError,\n"
        "    nErrId     => nErrIdLast,\n"
        "    cbWrite    => cbBytesWritten\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileClose", "FB_FilePuts", "FB_FileRead"],
)

_add(
    "FB_FileGets",
    summary=(
        "FB_FileGets 从已用文本模式打开的文件中读取一行文本到字符串 `sLine`，遇到换行符或字符串容量上限（`T_MaxString` = 255 字节）即停止。"
        "末尾的换行符**包含在内**返回，调用方需自行用 `MID` / `LEFT` 或 `FIND` 截掉。"
        "适用于按行处理 CSV / INI / 文本日志的场景。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次读取。读取过程：从当前文件指针开始向前扫描，遇到 LF（`16#0A`）即停止并把含换行的字符串返回；若先到 `T_MaxString` 长度上限则截断返回；若先到 EOF 则返回已读到的部分并把 `bEOF = TRUE`。\n\n"
        "**文件必须文本模式打开**：PDF 明确要求 `FOPEN_MODETEXT`，二进制模式下行为未定义。\n\n"
        "**`sLine` 自动空终止**：返回字符串带 null 终止符（C 风格），可直接当 IEC `STRING` 用。"
    ),
    pitfalls=[
        ("**换行符没去掉**：`sLine` 末尾带 `$N`（LF），后续比对 / 拼接前应当 `LEN := LEN(sLine); IF MID(sLine, 1, LEN) = '$N' THEN ...; END_IF`。", False),
        ("**必须文本模式**：二进制模式打开的文件喂给本 FB 行为未定义；常见症状是 `sLine` 中含 CR 字符。", False),
        ("**超长行被截断**：超过 255 字节的行只会返回前 255 字节，剩余在下次调用时返回；CSV 列数过多时要注意。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。", False),
    ],
    var_desc={**_VD_FILE_ADS, "sLine": "**输出**：读到的一行文本（含末尾 LF），最长 `T_MaxString`（255）字节。"},
    scenario="启动时逐行读取 D:/config/recipe.csv 文件，把每一行解析成一条配方记录恢复到内存中。",
    value="比 `FB_FileRead` + 自己扫换行省心；用 `FB_FileLoad` 全文件读再分割也行但占内存。",
    alt=(
        "- `FB_FileRead`：手动按字节读，自己找换行。\n"
        "- `FB_FileLoad`：一次性读全文，适合 < 几 KB 的小配置。"
    ),
    xml_scen="按行从 D:/config/recipe.csv 读出文本，每按一次 bReadLineRequest 读下一行；用作配方导入流程。",
    xml_val="不用本 FB 要 FB_FileRead + 手写扫描换行，约 20 行；本 FB 一次调用即可。",
    xml_verify="bReadLineRequest 升沿 → sLineRead 在 1-2 周期后被填充；多次触发直到 bEofReached = TRUE。",
    xml_vars=[
        ("fbFileGets", "FB_FileGets", None, "FB_FileGets 实例"),
        ("hOpenedFile", "UINT", None, "已打开的句柄（文本模式）"),
        ("sLineRead", "T_MaxString", None, "读到的一行文本"),
        ("bReadLineRequest", "BOOL", None, "在线写 TRUE 触发读下一行"),
        ("bEofReached", "BOOL", None, "TRUE = 已到 EOF（隐式：sLineRead 为空且 bBusy 落沿）"),
        ("bGetsError", "BOOL", None, "TRUE = 读失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "// 单次完整调用；读完后 sLineRead 含末尾换行，业务侧再去除\n"
        "fbFileGets(\n"
        "    sNetId   := '',\n"
        "    hFile    := hOpenedFile,\n"
        "    bExecute := bReadLineRequest,\n"
        "    tTimeout := T#10S,\n"
        "    bBusy    => bBusyMon,\n"
        "    bError   => bGetsError,\n"
        "    nErrId   => nErrIdLast,\n"
        "    sLine    => sLineRead\n"
        ");\n\n"
        "// 业务侧：bBusy 落沿且 sLineRead 为空字符串 = EOF（FB_FileGets 没显式 bEOF 输出）\n"
        "IF (NOT bBusyMon) AND (NOT bGetsError) AND (LEN(sLineRead) = 0) AND bReadLineRequest THEN\n"
        "    bEofReached := TRUE;\n"
        "END_IF;\n"
    ),
    related=["FB_FileOpen", "FB_FilePuts", "FB_FileRead"],
)

_add(
    "FB_FilePuts",
    summary=(
        "FB_FilePuts 把一个 `T_MaxString` 字符串写入已用文本模式打开的文件，写入长度为该字符串的有效字符数（直到 null 终止符，不含 null）。"
        "**不自动加换行符**：调用方需要换行的话自己在字符串末尾拼 `'$N'`。"
        "适用于按行追加文本日志 / CSV 行写入。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次写入。`sLine` 中的可见字符（直到 null）被写到当前文件指针位置或追加模式下的末尾。\n\n"
        "**字符串长度**：本 FB 写的字节数 = `LEN(sLine)`，不含尾部 null。\n\n"
        "**换行符**：PDF 没说本 FB 自动加 LF；要换行必须自己拼 `CONCAT(sData, '$N')`。文本模式下写 `$N`，OS 在 Windows 上会自动转成 CR+LF。\n\n"
        "**文件必须文本模式打开**：与 `FB_FileGets` 对应。"
    ),
    pitfalls=[
        ("**不自动加换行**：很多人误以为像 C 的 `fputs` 加换行，结果整个文件挤成一行。要换行自己 `sLine := CONCAT(sData, '$N')`。", False),
        ("**必须文本模式**：二进制模式打开的文件喂给本 FB 行为未定义。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`，错误号 `0x70C`。", False),
        ("**字符串截断**：`T_MaxString` 限 255 字节，超长行用 `FB_FileWrite` 写。", True),
    ],
    var_desc={**_VD_FILE_ADS, "sLine": "要写入的字符串（最长 `T_MaxString`，255 字节）。**不自动加换行**，要换行自己拼 `$N`。"},
    scenario="把每条工艺事件（时间戳 + 事件文本，约 80 字符）以 CSV 行格式追加写入 D:/log/events.csv。",
    value="比 `FB_FileWrite` + ADR + SIZEOF 更直观；纯字符串行写入主力。",
    alt=("- `FB_FileWrite`：能写任何字节，灵活但 verbose。\n- TF3500 Logger：付费、高吞吐。"),
    xml_scen="把 sEventLine ('2026-05-20T12:00:00,设备启动,OK') 追加写入 D:/log/events.csv（文本模式）。",
    xml_val="一行调用替代 FB_FileWrite + ADR + LEN，约省 5-8 行。",
    xml_verify="在线写 sEventLine 后置 bPutsRequest := TRUE → 用文本编辑器打开 events.csv 应见新行；bPutsError 始终 FALSE。",
    xml_vars=[
        ("fbFilePuts", "FB_FilePuts", None, "FB_FilePuts 实例"),
        ("hOpenedFile", "UINT", None, "已打开的句柄（文本模式追加）"),
        ("sEventLine", "T_MaxString", "'2026-05-20T12:00:00,event,OK$N'", "一行事件文本，末尾必须自己加 $N 换行"),
        ("bPutsRequest", "BOOL", None, "在线写 TRUE 触发一次写入"),
        ("bPutsError", "BOOL", None, "TRUE = 写失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "// 单次完整调用；sEventLine 末尾自己加了 $N 确保换行\n"
        "fbFilePuts(\n"
        "    sNetId   := '',\n"
        "    hFile    := hOpenedFile,\n"
        "    sLine    := sEventLine,\n"
        "    bExecute := bPutsRequest,\n"
        "    tTimeout := T#10S,\n"
        "    bBusy    => bBusyMon,\n"
        "    bError   => bPutsError,\n"
        "    nErrId   => nErrIdLast\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileGets", "FB_FileWrite"],
)

_add(
    "FB_FileLoad",
    summary=(
        "FB_FileLoad 是 `FB_FileOpen` + `FB_FileRead` + `FB_FileClose` 的一次性封装。"
        "给定路径和缓冲区，本 FB 自动以二进制模式打开文件、读取最多 `cbReadLen` 字节到缓冲区、然后自动关闭。"
        "适用于一次性把整份小配置 / 配方文件读进内存的场景，无需自己维护句柄。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发整个 Open/Read/Close 序列。完成后 `bBusy = FALSE`，`cbRead` 给出实际读到的字节数。\n\n"
        "**文件以二进制模式打开**（PDF 明确指出 implicit binary mode），所以读 CSV / 日志会保留 CR+LF 不做转换。\n\n"
        "**缓冲区责任**：`pReadBuff` + `cbReadLen` 由调用方负责保证有效；`cbReadLen` 通常 = 缓冲区 `SIZEOF`。\n\n"
        "**比手动三步省**：不用关心 `hFile` 生命周期；适合配方 / 配置 / 状态快照恢复。"
    ),
    pitfalls=[
        ("**只能读到 `cbReadLen` 字节**：文件超过该值的部分被丢弃，不会报错；要全文读，缓冲区必须 ≥ 文件大小。", False),
        ("**二进制模式**：Windows 文本文件的 CR+LF 不会被转换为 LF，对比文本时注意。", False),
        ("**`cbReadLen` > 缓冲区**：FB 不查越界，会越界写。永远 `cbReadLen := SIZEOF(buf)`。", False),
        ("**ADS 报文上限**：单次 ≈ 1 MB；超过应用 `FB_FileOpen` + 分段 `FB_FileRead`。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "sPathName": "要读取的文件本地路径。**只能本地路径**。",
        "pReadBuff": "本地缓冲区起始地址，`ADR(myVar)`。",
        "cbReadLen": "缓冲区容量字节数，应等于 `SIZEOF(buf)`。",
        "cbRead": "**输出**：实际读到的字节数；可能小于 `cbReadLen`（文件不够大）或 = `cbReadLen`（文件至少这么大但被截断）。",
    },
    scenario="设备启动后一次性把 D:/config/recipe.bin 配方文件（约 4 KB）读入 stRecipeBuffer 结构体，作为运行参数。",
    value="替代 Open + Read + Close 三步状态机，省约 25 行代码。",
    alt=("- 手动 Open/Read/Close 三段：灵活但啰嗦。\n- 配合 `FB_FileGets` 按行读：文本场景更适合。"),
    xml_scen="启动时从 D:/config/recipe.bin 把整份配方（≤ 256 字节）一次性读入本地缓冲区。",
    xml_val="封装 3 个 FB 的状态机，省 25 行。",
    xml_verify="在线置 bLoadRequest := TRUE → 观察 cbBytesLoaded ≈ 真实文件大小；故意指向不存在的文件 → bLoadError = TRUE 且 nErrIdLast = 0x70C。",
    xml_vars=[
        ("fbFileLoad", "FB_FileLoad", None, "FB_FileLoad 实例"),
        ("sRecipePath", "T_MaxString", "'D:/config/recipe.bin'", "配方文件路径"),
        ("aRecipeBuffer", "ARRAY[0..255] OF BYTE", None, "本地缓冲区"),
        ("bLoadRequest", "BOOL", None, "在线写 TRUE 触发一次读取"),
        ("cbBytesLoaded", "UDINT", None, "实际读到字节数"),
        ("bLoadError", "BOOL", None, "TRUE = 读失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbFileLoad(\n"
        "    sNetId    := '',\n"
        "    sPathName := sRecipePath,\n"
        "    pReadBuff := ADR(aRecipeBuffer),\n"
        "    cbReadLen := SIZEOF(aRecipeBuffer),\n"
        "    bExecute  := bLoadRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bLoadError,\n"
        "    nErrId    => nErrIdLast,\n"
        "    cbRead    => cbBytesLoaded\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileRead", "FB_FileClose"],
)


_add(
    "FB_FileSeek",
    summary=(
        "FB_FileSeek 把已打开文件的读 / 写指针移动到指定位置。"
        "`nSeekPos` + `eOrigin` 共同决定新位置：`SEEK_SET`（从文件头）、`SEEK_CUR`（从当前位置）、`SEEK_END`（从文件末尾，`nSeekPos` 通常为负）。"
        "适用于在大文件里跳到特定偏移读 / 写，或在循环日志里 wrap-around 写入。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次移动。\n\n"
        "**三种基准 `eOrigin`**：\n\n"
        "- `SEEK_SET`：`nSeekPos` 直接作为新指针位置（必须 ≥ 0）。\n"
        "- `SEEK_CUR`：新位置 = 当前指针 + `nSeekPos`（可正可负）。\n"
        "- `SEEK_END`：新位置 = 文件大小 + `nSeekPos`（通常 ≤ 0，正值会越过末尾）。\n\n"
        "**追加模式限制**：以 `FOPEN_MODEAPPEND` / `a+` 打开的文件，**写位置始终是末尾**，Seek 只能改读位置；写永远从末尾追加。\n\n"
        "**越界行为**：`nSeekPos` 超过文件末尾 PDF 未明确规定；通常成功但下次读会返回 0 字节 (`bEOF = TRUE`)。"
    ),
    pitfalls=[
        ("**追加模式下 Seek 对写无效**：典型坑：用户在 `a+` 模式下 Seek 到中间想覆盖一段数据，结果数据仍追加到末尾。要随机写必须用 `r+` / `w+`。", False),
        ("**`nSeekPos` 是 `DINT` 有符号**：`SEEK_CUR` / `SEEK_END` 可用负值；`SEEK_SET` 用负值是错误。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。", False),
        ("**>2 GB 文件**：`nSeekPos` 是 32 位有符号，上限 ≈ 2 GB；超大文件本 FB 不能定位到 2 GB 以后。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "nSeekPos": "新指针位置（相对 `eOrigin` 基准）。`SEEK_SET` 必须 ≥ 0；`SEEK_CUR` / `SEEK_END` 可为负。",
        "eOrigin": "基准点：`SEEK_SET`（文件头） / `SEEK_CUR`（当前位置） / `SEEK_END`（文件末尾）。默认 `SEEK_SET`。",
    },
    scenario="对二进制循环日志文件 wrap-around 写入：写到文件尾后 Seek 回头部继续写，实现固定大小的环形日志。",
    value="封装 ADS 0x10006 命令；不用本 FB 要自己拼 ADS Write 命令。",
    alt=("- `FB_FileTell`：搭配使用，先读位置再 seek 回。\n- `FB_FileClose` + 重 `FB_FileOpen`：粗暴但能用。"),
    xml_scen="读取已打开二进制日志中倒数第 512 字节窗口：用 SEEK_END + nSeekPos = -512 跳到该位置准备 FB_FileRead。",
    xml_val="替代手算文件长度 - 512 再用 SEEK_SET 的方案，简化 3-5 行代码。",
    xml_verify="在线置 bSeekRequest := TRUE → 观察 bBusy 跳动后落下；故意传 hOpenedFile = 0 → bSeekError = TRUE。",
    xml_vars=[
        ("fbFileSeek", "FB_FileSeek", None, "FB_FileSeek 实例"),
        ("hOpenedFile", "UINT", None, "已打开句柄"),
        ("bSeekRequest", "BOOL", None, "在线写 TRUE 触发一次 Seek"),
        ("bSeekError", "BOOL", None, "TRUE = 移动失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "// 跳到文件末尾向前 512 字节处准备读最后一段\n"
        "fbFileSeek(\n"
        "    sNetId   := '',\n"
        "    hFile    := hOpenedFile,\n"
        "    nSeekPos := -512,\n"
        "    eOrigin  := SEEK_END,\n"
        "    bExecute := bSeekRequest,\n"
        "    tTimeout := T#10S,\n"
        "    bBusy    => bBusyMon,\n"
        "    bError   => bSeekError,\n"
        "    nErrId   => nErrIdLast\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileTell", "FB_FileRead", "FB_FileWrite"],
)

_add(
    "FB_FileTell",
    summary=(
        "FB_FileTell 返回已打开文件的当前指针位置（从文件头算起的字节偏移），输出到 `nSeekPos`。"
        "常与 `FB_FileSeek` 配合使用：先 Tell 保存位置 → 做完读 / 写 → Seek 回原位置。"
        "也用于估算文件大小（Seek 到末尾再 Tell）。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次查询。完成后 `nSeekPos` 给出当前指针字节偏移。\n\n"
        "**追加模式细节**：PDF 明确指出在 `FOPEN_MODEAPPEND` 模式下，`nSeekPos` 反映的是『最近一次 I/O 操作』后的位置，**不是**下次写入位置——下次写入永远在末尾。读操作后 Tell 反映读完位置；写操作后位置变化未必如直觉。\n\n"
        "**未做 I/O 时**：以 `a` / `a+` 打开且尚未读 / 写过，`nSeekPos = 0`（文件头），与 r/w/+ 模式一致。"
    ),
    pitfalls=[
        ("**追加模式下不是下次写位置**：在 `a` / `a+` 模式下 Tell 出来的位置只是最近一次 I/O 后的位置，**不是**下次写入位置（永远末尾）。要算文件大小用 Seek 到 SEEK_END 再 Tell。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。", False),
        ("**>2 GB 限制**：`nSeekPos` 是 `UDINT`，理论 4 GB；但 Seek 是 `DINT` 限 2 GB，所以联合使用上限 2 GB。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "nSeekPos": "**输出**：当前文件指针字节偏移（从文件头起算）。追加模式下反映最近 I/O 后位置而非下次写位置。",
    },
    scenario="对一份大配方文件做断点续传读取：把 Tell 拿到的位置存到 retain，重启后 Seek 回原位置继续读。",
    value="封装 ADS 0x10007 命令；不用本 FB 要自己拼 ADS Read 命令。",
    alt=("- 手动维护一个本地 UDINT 跟踪每次读写后的偏移：能用但断电后会丢同步。"),
    xml_scen="读完一段后查询当前文件指针位置 nCurrentPos 保存到 retain 变量，便于断电重启续读。",
    xml_val="替代手动跟踪偏移变量，直接从 OS 拿权威值。",
    xml_verify="在线置 bTellRequest := TRUE → 观察 nCurrentPos 在 1-2 周期后非零；与刚读完的字节累计量一致。",
    xml_vars=[
        ("fbFileTell", "FB_FileTell", None, "FB_FileTell 实例"),
        ("hOpenedFile", "UINT", None, "已打开句柄"),
        ("bTellRequest", "BOOL", None, "在线写 TRUE 触发一次查询"),
        ("nCurrentPos", "DINT", None, "查询返回的当前指针偏移（出错时 = -1）"),
        ("bTellError", "BOOL", None, "TRUE = 查询失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbFileTell(\n"
        "    sNetId    := '',\n"
        "    hFile     := hOpenedFile,\n"
        "    bExecute  := bTellRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bTellError,\n"
        "    nErrId    => nErrIdLast,\n"
        "    nSeekPos => nCurrentPos\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileSeek"],
)

_add(
    "FB_EOF",
    summary=(
        "FB_EOF 检查已打开文件是否到达末尾。"
        "通过 `bEOF` 输出 TRUE/FALSE 表示当前文件指针是否在文件结束位置。"
        "搭配按行 / 按块循环读取使用，是循环退出的标准条件。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次查询。\n\n"
        "**判定时机**：本 FB 只反映**调用瞬间**的指针位置是否在 EOF；后续 read 移动指针后须重新调用才能更新。\n\n"
        "**与 `FB_FileRead.bEOF` 的关系**：`FB_FileRead` 本身在读到 EOF 时也会拉起 `bEOF`，本 FB 提供独立显式查询，适用于"
        "在 Seek 之后 / 读循环之间检查的场景。"
    ),
    pitfalls=[
        ("**EOF 不是实时**：本 FB 在 `bExecute` 升沿时查询一次，之后状态不会自动更新；要持续检测需周期性升沿（如配 RTRIG）。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。", False),
        ("**与 `FB_FileRead` 内置 bEOF 重叠**：若已经用 `FB_FileRead` 的 `bEOF`，可不必再用本 FB。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "bEOF": "**输出**：TRUE = 当前指针在文件末尾；FALSE = 还有数据可读。",
    },
    scenario="在按块循环读 D:/log/large.bin 时，每读 8 KB 用本 FB 显式检查一次是否到尾，作为循环退出条件。",
    value="语义比 `FB_FileRead.bEOF` 更清晰：不耦合读操作，专门检查指针位置。",
    alt=("- `FB_FileRead` 内置 `bEOF`：读和判断一步完成，更常用。\n- `FB_FileTell` + 自己比对文件大小：能用但需要先知道总大小。"),
    xml_scen="按块循环读完整个大日志文件，每读完一块就显式查询是否到达 EOF 作为退出条件。",
    xml_val="语义比 FB_FileRead 内置 bEOF 更清晰，专做检测。",
    xml_verify="读到中间时 bEofReached = FALSE；读到末尾 → bEofReached = TRUE。",
    xml_vars=[
        ("fbEof", "FB_EOF", None, "FB_EOF 实例"),
        ("hOpenedFile", "UINT", None, "已打开句柄"),
        ("bEofCheckRequest", "BOOL", None, "在线写 TRUE 触发一次查询"),
        ("bEofReached", "BOOL", None, "TRUE = 已到 EOF"),
        ("bEofError", "BOOL", None, "TRUE = 查询失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbEof(\n"
        "    sNetId   := '',\n"
        "    hFile    := hOpenedFile,\n"
        "    bExecute := bEofCheckRequest,\n"
        "    tTimeout := T#10S,\n"
        "    bBusy    => bBusyMon,\n"
        "    bError   => bEofError,\n"
        "    nErrId   => nErrIdLast,\n"
        "    bEOF     => bEofReached\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileRead", "FB_FileTell"],
)

_add(
    "FB_FileDelete",
    summary=(
        "FB_FileDelete 通过 ADS 异步删除目标 PC 本地文件系统中的一个文件。"
        "删除前不需要 Open；直接给路径 + `ePath` 基准即可。"
        "删除操作不可撤销——文件被立刻移到回收站之外的彻底删除。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次删除。完成后 `bBusy = FALSE`，成功时 `bError = FALSE`。\n\n"
        "**路径基准 `ePath`**：与 `FB_FileOpen` 一致，默认 `PATH_GENERIC`；要删 Boot 目录文件用 `PATH_BOOTPATH`。\n\n"
        "**不可恢复**：本 FB 调用 OS 删除 API，不进回收站，删完即丢。\n\n"
        "**正在被打开的文件**：如果文件还有 `hFile` 没 Close，Windows 通常拒绝删除（错误 32：文件被占用）。"
    ),
    pitfalls=[
        ("**误删风险**：路径错一个字符可能删掉重要文件且不可恢复。建议先用 `F_FileExists` 风格的检查再删（Tc2_System 没有直接的存在性查询，需通过 `FB_FileOpen` 尝试只读打开判断）。", False),
        ("**被占用文件删除失败**：打开未关闭的文件删不掉，`nErrId` 通常返回 OS 错误码（32 SHARING_VIOLATION）。", False),
        ("**通配符不支持**：`sPathName` 只能是单个文件名，不能 `*.log` 批删；批删要自己枚举目录。", True),
        ("**`PATH_GENERIC` 默认**：写相对路径时实际在 TwinCAT Boot 目录下，常意外删错文件。建议显式写绝对路径或选 `PATH_GENERIC_USERDATA`。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "sPathName": "要删除的文件路径（绝对或相对于 `ePath`）。",
        "ePath": "路径基准枚举。默认 `PATH_GENERIC`。",
    },
    scenario="每月清理一次过期的工艺日志文件，把上个月的 'D:/log/2026-04.csv' 删除腾空间。",
    value="封装 ADS 0x10008 命令；不用本 FB 要自己拼 ADS Write 命令。",
    alt=("- 直接 `ADSWRITE`：能用但要自己跟状态。\n- Windows 任务计划脚本：操作系统级，不依赖 PLC。"),
    xml_scen="清理过期日志：把 'D:/log/old.csv' 删除腾出磁盘空间。",
    xml_val="封装 ADS 删除命令的状态机。",
    xml_verify="在线写 sFileToDelete + bDeleteRequest := TRUE → 文件被删除；故意删不存在的文件 → bDeleteError = TRUE 且 nErrIdLast = 0x70C。",
    xml_vars=[
        ("fbFileDelete", "FB_FileDelete", None, "FB_FileDelete 实例"),
        ("sFileToDelete", "T_MaxString", "'D:/log/old.csv'", "要删除的文件路径"),
        ("bDeleteRequest", "BOOL", None, "在线写 TRUE 触发一次删除"),
        ("bDeleteError", "BOOL", None, "TRUE = 删除失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbFileDelete(\n"
        "    sNetId    := '',\n"
        "    sPathName := sFileToDelete,\n"
        "    ePath     := PATH_GENERIC,\n"
        "    bExecute  := bDeleteRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bDeleteError,\n"
        "    nErrId    => nErrIdLast\n"
        ");\n"
    ),
    related=["FB_FileOpen", "FB_FileRename", "FB_CreateDir", "FB_RemoveDir"],
)

_add(
    "FB_FileRename",
    summary=(
        "FB_FileRename 把目标 PC 本地文件系统中的一个文件改名（也可以同时变目录，本质上是 OS 的 rename / move 调用）。"
        "源路径 `sOldName` 和目的路径 `sNewName` 都相对于同一个 `ePath` 基准。"
        "适用于班次切换时把当日日志 'process.csv' 改名为 '20260520.csv' 归档。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次改名。完成后 `bBusy = FALSE`，成功 `bError = FALSE`。\n\n"
        "**同盘改名是原子操作**：在同一磁盘卷内改名是 OS 原子 rename，瞬间完成。\n\n"
        "**跨盘是复制 + 删除**：目标和源在不同盘符时，OS 会做复制然后删除，时间随文件大小线性增长。\n\n"
        "**目标已存在**：PDF 未明确目标存在时的行为，实测通常拒绝（错误 80 / FILE_EXISTS），建议先确保目标不存在。"
    ),
    pitfalls=[
        ("**目标已存在会失败**：覆盖目标需要先 `FB_FileDelete` 删除目标。", False),
        ("**跨盘改名很慢**：内部是复制 + 删除；大文件可能要数秒到数十秒，`tTimeout` 默认 5 秒可能不够。", False),
        ("**正在被打开的文件**：源文件 `hFile` 未 Close 时通常无法 rename（错误 32）。", False),
        ("**`PATH_GENERIC` 默认**：相对路径基准是 TwinCAT Boot 目录，建议显式用 `PATH_GENERIC_USERDATA` 或写绝对路径。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "sOldName": "源文件路径（绝对或相对 `ePath`）。",
        "sNewName": "目标文件路径（绝对或相对 `ePath`）。",
        "ePath": "路径基准枚举，同时作用于 `sOldName` 和 `sNewName`。默认 `PATH_GENERIC`。",
    },
    scenario="班次切换：把当日累计日志 'D:/log/process.csv' 改名为 'D:/log/20260520.csv' 归档，准备新建空文件继续记录。",
    value="封装 ADS rename 命令；替代 OS 命令行调用。",
    alt=("- OS shell `rename` 命令 + `WinExecute`：能但绕弯。\n- 复制内容到新文件 + 删旧文件：低效且非原子。"),
    xml_scen="班次切换：'process.csv' → '20260520.csv' 归档。",
    xml_val="原子 rename，省去复制+删除两步。",
    xml_verify="在线置 bRenameRequest := TRUE → 旧文件消失新文件出现；目标已存在时 bRenameError = TRUE。",
    xml_vars=[
        ("fbFileRename", "FB_FileRename", None, "FB_FileRename 实例"),
        ("sSourceName", "T_MaxString", "'D:/log/process.csv'", "源路径"),
        ("sTargetName", "T_MaxString", "'D:/log/20260520.csv'", "目标路径"),
        ("bRenameRequest", "BOOL", None, "在线写 TRUE 触发一次改名"),
        ("bRenameError", "BOOL", None, "TRUE = 改名失败"),
        ("nErrIdLast", "UDINT", None, "ADS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbFileRename(\n"
        "    sNetId   := '',\n"
        "    sOldName := sSourceName,\n"
        "    sNewName := sTargetName,\n"
        "    ePath    := PATH_GENERIC,\n"
        "    bExecute := bRenameRequest,\n"
        "    tTimeout := T#10S,\n"
        "    bBusy    => bBusyMon,\n"
        "    bError   => bRenameError,\n"
        "    nErrId   => nErrIdLast\n"
        ");\n"
    ),
    related=["FB_FileDelete", "FB_FileOpen", "FB_CreateDir"],
)

_add(
    "FB_CreateDir",
    summary=(
        "FB_CreateDir 在目标 PC 本地文件系统中创建一个新目录。"
        "只能创建**单级**目录——`sPathName` 中的父目录必须已存在；不能像 `mkdir -p` 一次性创建多级。"
        "适用于按日期 / 班次自动归档日志：每天上电时确保 'D:/log/<YYYYMMDD>' 目录存在。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次创建。完成后 `bBusy = FALSE`，成功时 `bError = FALSE`。\n\n"
        "**单级限制**：`D:/log/2026/05/20` 必须 `D:/log/2026` 与 `D:/log/2026/05` 已存在，本 FB 不会递归补建多级。要一次性建多级，调用方应当循环调用本 FB，从顶层目录开始逐层创建，遇到错误号 183（目录已存在）继续即可。\n\n"
        "**目录已存在**：PDF 未明确，实测通常返回错误（错误号 183 / ALREADY_EXISTS），调用方可以选择忽略此错误号视为已就绪状态。\n\n"
        "**`ePath` 路径基准**：与 `FB_FileOpen` 一致，建议用 `PATH_GENERIC` + 绝对路径或 `PATH_GENERIC_USERDATA` + 相对路径避免误建到 Boot 目录。"
    ),
    pitfalls=[
        ("**单级**：要建多级用循环或先 `FB_RemoveDir` 测试父目录。", False),
        ("**目录已存在**：报错号 183（ALREADY_EXISTS）；业务侧可视为『已就绪』。", False),
        ("**`PATH_GENERIC` 默认**：相对路径在 TwinCAT Boot 目录下，建议显式绝对路径。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "sPathName": "要创建的目录路径。父目录必须已存在（**不递归补建**）。",
        "ePath": "路径基准。默认 `PATH_GENERIC`。",
    },
    scenario="每日 0 点 PLC 自动确保 'D:/log/20260520' 目录存在，准备当天日志写入。",
    value="封装 ADS mkdir 命令的状态机。",
    alt=("- 提前手工建好年 / 月目录：可行但繁琐。\n- OS shell `mkdir`：能但绕弯。"),
    xml_scen="每天 0 点确保 'D:/log/20260520' 目录存在，存放当天日志。",
    xml_val="一次调用即可，省去 OS 命令转发。",
    xml_verify="在线置 bCreateDirRequest := TRUE → 目标目录出现；目录已存在时 bCreateDirError = TRUE 且 nErrIdLast = 183。",
    xml_vars=[
        ("fbCreateDir", "FB_CreateDir", None, "FB_CreateDir 实例"),
        ("sDirToCreate", "T_MaxString", "'D:/log/20260520'", "要创建的目录路径"),
        ("bCreateDirRequest", "BOOL", None, "在线写 TRUE 触发一次创建"),
        ("bCreateDirError", "BOOL", None, "TRUE = 创建失败"),
        ("nErrIdLast", "UDINT", None, "ADS / OS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbCreateDir(\n"
        "    sNetId    := '',\n"
        "    sPathName := sDirToCreate,\n"
        "    ePath     := PATH_GENERIC,\n"
        "    bExecute  := bCreateDirRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bCreateDirError,\n"
        "    nErrId    => nErrIdLast\n"
        ");\n"
    ),
    related=["FB_RemoveDir", "FB_FileOpen"],
)

_add(
    "FB_RemoveDir",
    summary=(
        "FB_RemoveDir 从目标 PC 本地文件系统中删除一个目录。"
        "**只能删空目录**——目录里如果还有文件 / 子目录，删除会失败。"
        "适用于归档完成后清理临时目录，或定期清理空目录。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次删除。\n\n"
        "**只删空目录**：PDF 明确指出『A directory containing files cannot be deleted』。要递归删除整个目录树，需要先枚举所有内容用 `FB_FileDelete` 删完再删目录。Tc2_System 本身不带目录枚举 API（Walk / FindFirstFile 之类），递归清理需通过 ADS 文件枚举接口或调 OS shell 完成。\n\n"
        "**目录不存在**：报错（OS 错误号 2 / FILE_NOT_FOUND）。\n\n"
        "**目录被占用**：进程当前工作目录在该目录、或目录里某文件被打开未关闭，删除会返回 SHARING_VIOLATION（错误号 32）；调用前应当确保所有 `FB_FileOpen` 已 Close。"
    ),
    pitfalls=[
        ("**非空目录无法删**：要清空目录树需自己写递归（Tc2_System 不带 Walk API），或调 OS shell。", False),
        ("**`PATH_GENERIC` 默认**：相对路径在 Boot 目录下，建议显式绝对路径。", True),
        ("**目录被占用**：进程 cwd 在该目录或某文件被打开未关 → 删除失败（错误 32 / SHARING_VIOLATION）。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "sPathName": "要删除的目录路径。**目录必须为空**。",
        "ePath": "路径基准。默认 `PATH_GENERIC`。",
    },
    scenario="月底归档完成后删掉空的临时目录 'D:/log/tmp_archive'，整理磁盘结构。",
    value="封装 ADS rmdir 命令；非空目录的递归清空需要自己处理。",
    alt=("- 直接 OS shell `rmdir /s`：能递归但绕弯。\n- 自写递归：枚举 + 删文件 + 删目录三步。"),
    xml_scen="月底归档完成后清理空临时目录 'D:/log/tmp_archive'。",
    xml_val="一次调用即可。",
    xml_verify="目录为空时调用 → 目录消失；目录非空 → bRemoveDirError = TRUE。",
    xml_vars=[
        ("fbRemoveDir", "FB_RemoveDir", None, "FB_RemoveDir 实例"),
        ("sDirToRemove", "T_MaxString", "'D:/log/tmp_archive'", "要删除的（空）目录路径"),
        ("bRemoveDirRequest", "BOOL", None, "在线写 TRUE 触发一次删除"),
        ("bRemoveDirError", "BOOL", None, "TRUE = 删除失败"),
        ("nErrIdLast", "UDINT", None, "ADS / OS 错误号"),
        ("bBusyMon", "BOOL", None, "ADS 通讯中"),
    ],
    xml_call=(
        "fbRemoveDir(\n"
        "    sNetId    := '',\n"
        "    sPathName := sDirToRemove,\n"
        "    ePath     := PATH_GENERIC,\n"
        "    bExecute  := bRemoveDirRequest,\n"
        "    tTimeout  := T#10S,\n"
        "    bBusy     => bBusyMon,\n"
        "    bError    => bRemoveDirError,\n"
        "    nErrId    => nErrIdLast\n"
        ");\n"
    ),
    related=["FB_CreateDir", "FB_FileDelete"],
)


# =================== Watchdog function blocks (2) ===================

_add(
    "FB_PcWatchdog",
    summary=(
        "FB_PcWatchdog 启用 IPC 主板上的硬件看门狗（仅限特定主板：IP-4GVI63、CB1050、CB2050、CB3050、CB1051、CB2051、CB3051）。"
        "`bEnable = TRUE` 后必须以**短于** `tTimeOut` 的周期持续调用本 FB；一旦超时未喂狗，硬件强制重启整台 PC。"
        "用于在 PLC / Windows 死循环或卡死时自动恢复系统。"
    ),
    behavior=(
        "**调用方式**：必须在循环任务里每个周期调用一次。`bEnable = TRUE` 且 `tTimeOut ≥ 1s` 时启用；后续每次调用相当于『喂狗』重置超时计数。\n\n"
        "**超时窗口**：`tTimeOut` 范围 1–255 秒。一旦超过该时长无新的 FB 调用，硬件触发整机重启（**不是** PLC 重启，是整台 PC 立即冷启动）。\n\n"
        "**禁用方式**：`bEnable = FALSE` 或 `tTimeOut = 0` 关闭看门狗。在断点调试、PLC Reset、TwinCAT Stop、切换 Config 模式、激活配置前**必须**显式禁用，否则在调试中超时将导致 PC 重启（PDF NOTICE 明确警告）。\n\n"
        "**硬件依赖**：本 FB 直接读写主板看门狗芯片，只在 PDF 列出的主板型号上生效；其他主板调用无实际效果。\n\n"
        "**用途**：典型用法是在 PLC MAIN 程序末尾调用一次，超时定为 5–10 秒。PLC 程序一旦卡死（死循环、外部 ADS 死锁），看门狗 5 秒后强制 PC 重启，配合开机自启动 TwinCAT 即可实现无人值守自动恢复。"
    ),
    pitfalls=[
        ("**调试时务必禁用**：断点停 PLC 立即触发超时重启 PC，会丢失整个调试现场。建议加 `IF NOT bDebugMode THEN bEnable := TRUE; END_IF;`。", False),
        ("**`tTimeOut` 不能太短**：< 2 秒在 Windows 任务繁忙时容易误触发；建议 5–10 秒。", True),
        ("**仅限指定主板**：列表外的主板调用本 FB 无效，系统仍可能卡死。要更广兼容性用 `FB_PcWatchDog_BAPI`。", False),
        ("**不能停 PLC 不喂狗**：PLC Stop / Reset / 配置激活前必须显式禁用，否则停 PLC 后看门狗仍跑，超时即重启。", False),
        ("**重启不可逆**：硬件复位等同断电，所有未持久化数据丢失；要保数据建议配 `FB_S_UPS_*`（Tc2_SUPS 库）。", True),
    ],
    var_desc={
        "tTimeOut": "看门狗超时时长（1–255 秒）。范围外行为未定义。",
        "bEnable": "TRUE 启用看门狗；FALSE 禁用。每周期保持 TRUE 即每周期喂狗。",
    },
    scenario="生产线 7×24 无人值守，PLC 主程序末尾启用 8 秒看门狗。一旦 PLC 任务卡死（外部 ADS 死锁或第三方 DLL 异常），8 秒后整机自动重启恢复。",
    value="替代外置硬件看门狗模块（需额外接线 + IO 资源），用主板内置芯片实现相同功能。不用本 FB 时只能依赖外部 watchdog timer 或人工巡检。",
    alt=(
        "- 外置看门狗模块（接 DI/DO）：需额外接线，但兼容性广。\n"
        "- `FB_PcWatchDog_BAPI`：基于 BIOS-API，主板支持面更广，超时上限 15300 秒。\n"
        "- 软件看门狗（PLC 内部计时）：能检测部分卡死，但无法处理 PLC 自身崩溃。"
    ),
    xml_scen="生产线 7×24 无人值守：PLC 主任务末尾启用 8 秒硬件看门狗。PLC 一旦卡死 8 秒，主板自动冷启动恢复。",
    xml_val="替代外置看门狗硬件 + 接线 + IO；省一组 DO 通道。",
    xml_verify="正常运行 → bEnableWatchdog := TRUE 后持续每周期调用 → PC 正常；故意让 PLC 死循环 8 秒（在线 IF bForceHang THEN WHILE TRUE DO ; END_WHILE; END_IF）→ PC 自动重启。注意：调试时务必先 bEnableWatchdog := FALSE！",
    xml_vars=[
        ("fbPcWatchdog", "FB_PcWatchdog", None, "FB_PcWatchdog 实例"),
        ("bEnableWatchdog", "BOOL", "FALSE", "在线置 TRUE 启用；调试前先置 FALSE"),
        ("tWatchdogTimeout", "TIME", "T#8S", "8 秒超时窗口"),
    ],
    xml_call=(
        "// 单次完整调用：必须每个 PLC 周期都跑到这一行才算喂狗\n"
        "fbPcWatchdog(\n"
        "    tTimeOut := tWatchdogTimeout,\n"
        "    bEnable  := bEnableWatchdog\n"
        ");\n"
    ),
    related=["FB_PcWatchDog_BAPI", "FB_S_UPS_CB3011"],
)

_add(
    "FB_PcWatchDog_BAPI",
    summary=(
        "FB_PcWatchDog_BAPI 通过 BIOS-API 启用 IPC 或 Embedded PC 的硬件看门狗，兼容所有支持 BIOS-API 的 Beckhoff 工控机。"
        "相比 `FB_PcWatchdog` 上限只能 255 秒，本 FB 的 `nWatchdogTimeS` 可达 15300 秒（255 分钟），适用于慢周期任务的恢复场景。"
        "通过 `bExecute` 上升沿启用，`nWatchdogTimeS ≥ 1` 才生效。"
    ),
    behavior=(
        "**调用方式**：必须在循环任务里周期调用，调用周期需短于 `nWatchdogTimeS`。`bExecute = TRUE` 触发设置 + 喂狗动作。\n\n"
        "**超时窗口**：`nWatchdogTimeS` 范围 1–15300 秒（约 4.25 小时）。超时后整机硬件复位。\n\n"
        "**ADS 调用本质**：本 FB 通过 ADS 向 BIOS-API 设备发送写命令实现，所以有 `sNetID` / `tTimeout` 参数；本机用空 NetID。\n\n"
        "**禁用方式**：`bExecute = FALSE` 或 `nWatchdogTimeS = 0`。在调试 / PLC Stop / 切换配置前同样**必须**显式禁用，否则会触发重启（PDF NOTICE 警告）。\n\n"
        "**与 `FB_PcWatchdog` 区别**：本 FB 走 BIOS-API，主板支持更广；`FB_PcWatchdog` 直接读写芯片寄存器，只在特定主板生效。新工程优先选本 FB。"
    ),
    pitfalls=[
        ("**调试务必禁用**：与 `FB_PcWatchdog` 一致——断点 / Reset 前 `bExecute := FALSE`。", False),
        ("**`nWatchdogTimeS` 上限 15300 秒**：超出范围行为未定义，建议留 ≥ 10% 余量。", False),
        ("**BIOS 不支持时静默失败**：老主板没有 BIOS-API 调用返回错误但不实际启用看门狗，需要在测试台先验证有效性。", True),
        ("**调用周期必须短于超时**：每分钟一次的慢任务用 60 秒超时是边缘情况，建议至少 2 倍冗余（设 120 秒）。", True),
    ],
    var_desc={
        "sNetID": "目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。",
        "nWatchdogTimeS": "看门狗超时时长，单位**秒**。范围 1–15300。",
        "bExecute": "TRUE 启用并喂狗；FALSE 禁用。",
        "tTimeout": "ADS 调用超时（不同于看门狗超时），默认 `DEFAULT_ADS_TIMEOUT`。",
    },
    scenario="慢工艺循环（如长达 10 分钟的烘干 / 热处理）的安全监护：超时 20 分钟，一旦工艺循环卡死自动重启。",
    value="比 `FB_PcWatchdog` 兼容主板更广 + 超时上限大 60 倍；现代工程的首选看门狗。",
    alt=(
        "- `FB_PcWatchdog`：限定主板，超时 ≤ 255 秒。\n"
        "- 外置硬件看门狗：接线复杂但与 BIOS / OS 无关。"
    ),
    xml_scen="慢工艺循环监护：超时设 600 秒（10 分钟），主循环每秒喂一次狗。卡死 10 分钟后 PC 自动重启。",
    xml_val="兼容主板更广，超时上限远超 FB_PcWatchdog。",
    xml_verify="bEnableSlowWatchdog := TRUE → PC 正常；故意让 PLC 卡死超过 600 秒 → PC 自动重启。调试前务必 FALSE。",
    xml_vars=[
        ("fbPcWatchdogBapi", "FB_PcWatchDog_BAPI", None, "FB_PcWatchDog_BAPI 实例"),
        ("bEnableSlowWatchdog", "BOOL", "FALSE", "在线置 TRUE 启用看门狗"),
        ("nSlowWatchdogTimeSec", "UDINT", "600", "看门狗超时 600 秒（10 分钟）"),
        ("bBapiError", "BOOL", None, "TRUE = ADS 调用失败（BIOS 可能不支持）"),
    ],
    xml_call=(
        "fbPcWatchdogBapi(\n"
        "    sNetID         := '',\n"
        "    nWatchdogTimeS := nSlowWatchdogTimeSec,\n"
        "    bExecute       := bEnableSlowWatchdog,\n"
        "    tTimeout       := T#5S\n"
        ");\n"
    ),
    related=["FB_PcWatchdog"],
)


# =================== Memory functions (4) ===================

_add(
    "MEMCPY",
    summary=(
        "MEMCPY 把源内存地址 `srcAddr` 开始的 `n` 个字节复制到目的地址 `destAddr`。"
        "**直接操作物理内存**：参数错误（地址非法、越界、源 / 目标重叠）可能导致系统崩溃或破坏其他变量，PDF NOTICE 段明确警告。"
        "返回值是实际复制的字节数（成功 = `n`，参数非法 = 0）。\n\n"
        "**重叠未定义**：源和目的重叠时行为未定义；要安全复制重叠区域必须用 `MEMMOVE`。"
    ),
    ftype="FUNCTION",
    behavior=(
        "**调用方式**：同步函数，返回时复制已完成。无任何状态机或异步等待。\n\n"
        "**参数语义**：`destAddr` / `srcAddr` 通常用 `ADR(myVar)` 取得；`n` 通常用 `SIZEOF(myVar)` 取得。如果两者类型不一致（如 `ADR(stA)` 与 `SIZEOF(stB)`），编译器无法检测错误，会导致越界。\n\n"
        "**返回值**：返回实际复制字节数；若 `destAddr == 0` 或 `srcAddr == 0` 或 `n == 0`，返回 0 表示未做任何操作。\n\n"
        "**性能**：底层是 C `memcpy`，速度接近内存带宽峰值；远快于自己写 `FOR i := 0 TO n-1 DO dst[i] := src[i]; END_FOR;` 循环（后者每字节有边界检查）。\n\n"
        "**重叠时**：源和目的内存区域重叠时行为未定义（PDF 明确）；典型例子是数组元素整体前移 / 后移，必须改用 `MEMMOVE`。"
    ),
    pitfalls=[
        ("**重叠区域未定义**：要前 / 后移数组元素必须用 `MEMMOVE`，不能用 MEMCPY。", False),
        ("**不查边界**：参数错可能写坏邻近变量或崩 PLC。永远 `destAddr := ADR(dst); n := SIZEOF(dst)` 并确保 `SIZEOF(src) >= n`。", False),
        ("**`destAddr == 0`**：地址为 0 返回 0；不要把未初始化的指针传入，建议先 `IF p <> 0 THEN MEMCPY(...); END_IF;`。", False),
        ("**绕过类型安全**：MEMCPY 抹平所有类型信息，写错结构布局不会被编译器发现。建议优先 `:=` 赋值（同类型）或用 `__VARIANT` 接口。", True),
        ("**对齐**：在 Arm 平台上对非对齐地址的 MEMCPY 可能比 x86 慢；对齐对齐到 4 / 8 字节边界。", True),
    ],
    var_desc={
        "destAddr": "目标内存区域起始地址（`PVOID`）。用 `ADR(dstVar)`；不可为 0。",
        "srcAddr": "源内存区域起始地址（`PVOID`）。用 `ADR(srcVar)`；不可为 0。",
        "n": "要复制的字节数。常用 `SIZEOF(dstVar)`，并确保源至少有这么多字节。",
    },
    return_kind="NONE",
    return_text=(
        "本函数返回 `UDINT`：\n\n"
        "| 返回值 | 含义 |\n|---|---|\n"
        "| `0` | 参数非法（`destAddr == 0` 或 `srcAddr == 0` 或 `n == 0`），未复制任何字节 |\n"
        "| `> 0` | 实际复制的字节数（成功时 = `n`） |\n"
    ),
    scenario="把刚 `FB_FileRead` 读到的 256 字节缓冲区一次性拷贝到工艺参数结构体里，避免逐字段赋值的繁琐。",
    value="一行代码替代手写 256 次 BYTE 赋值循环；速度快、代码短。",
    alt=(
        "- 手写 FOR 循环：可读但慢 5–10 倍且容易写错下标。\n"
        "- `MEMMOVE`：支持重叠区域，慢约 10%。\n"
        "- `:=` 整体赋值（同类型）：编译器自动展开，更类型安全，但跨类型不行。"
    ),
    xml_scen="把 FB_FileRead 读到的 256 字节 ARRAY 整块拷到工艺参数结构体；避免逐字段赋值。",
    xml_val="一行调用替代 256 次手写赋值；约快 5-10 倍。",
    xml_verify="在线触发 bCopyRequest := TRUE → 观察 nBytesCopied = SIZEOF(stProcessParams)；故意把 pSrc 设 0 → nBytesCopied = 0。",
    xml_vars=[
        ("aRawBuffer", "ARRAY[0..255] OF BYTE", None, "FB_FileRead 已填充的源缓冲区"),
        ("stProcessParams", "ARRAY[0..255] OF BYTE", None, "目标缓冲区（业务上是工艺参数结构体）"),
        ("bCopyRequest", "BOOL", None, "在线写 TRUE 触发一次拷贝"),
        ("nBytesCopied", "UDINT", None, "实际复制字节数；与 SIZEOF 一致才算成功"),
        ("rtCopy", "R_TRIG", None, "上升沿检测，避免每周期都拷"),
    ],
    xml_call=(
        "// 用 R_TRIG 限定为上升沿触发一次，避免每个 PLC 周期都做无效拷贝\n"
        "rtCopy(CLK := bCopyRequest);\n"
        "IF rtCopy.Q THEN\n"
        "    nBytesCopied := MEMCPY(\n"
        "        destAddr := ADR(stProcessParams),\n"
        "        srcAddr  := ADR(aRawBuffer),\n"
        "        n        := SIZEOF(stProcessParams)\n"
        "    );\n"
        "END_IF;\n"
    ),
    related=["MEMMOVE", "MEMSET", "MEMCMP"],
)

_add(
    "MEMMOVE",
    summary=(
        "MEMMOVE 把源内存地址开始的 `n` 个字节复制到目的地址。"
        "与 `MEMCPY` 的唯一区别是**支持源 / 目的重叠**：典型用途是把数组元素整体前移或后移。"
        "代价是内部多一层缓冲拷贝，速度比 MEMCPY 慢约 5–15%；不重叠时优先用 MEMCPY。"
    ),
    ftype="FUNCTION",
    behavior=(
        "**调用方式**：同步函数，返回时复制完成。\n\n"
        "**重叠区域处理**：内部检测 `srcAddr` 与 `destAddr` 的位置关系，若 `dst > src`（向右移）则**从尾向头**复制，反之**从头向尾**复制，保证不会覆盖未读的字节。\n\n"
        "**返回值**：返回实际复制字节数；参数非法（任一地址为 0 或 `n == 0`）返回 0。\n\n"
        "**典型用法**：数组左移一位 `MEMMOVE(ADR(arr[0]), ADR(arr[1]), (SIZEOF(arr) - SIZEOF(arr[0])));`——把 `arr[1..N]` 拷到 `arr[0..N-1]`，此时源和目的明显重叠，MEMCPY 不能用。\n\n"
        "**性能折损**：不重叠时也能用，但每次调用都做一次方向检测，比 MEMCPY 略慢。"
    ),
    pitfalls=[
        ("**不重叠用 MEMCPY 更快**：MEMMOVE 永远做方向检测；明确知道不重叠时用 MEMCPY 省 5–15% 时间。", False),
        ("**仍不查边界**：和 MEMCPY 一样越界会写坏邻近变量，永远用 `SIZEOF` + 确认源足够大。", False),
        ("**`destAddr / srcAddr == 0`**：返回 0 不复制；调用方应先做指针非空检查。", False),
        ("**对齐 / Arm**：与 MEMCPY 一致，对齐到 4 / 8 字节边界可提速。", True),
    ],
    var_desc={
        "destAddr": "目标内存区域起始地址（`PVOID`）。允许与 `srcAddr` 重叠。",
        "srcAddr": "源内存区域起始地址（`PVOID`）。允许与 `destAddr` 重叠。",
        "n": "要复制的字节数。",
    },
    return_kind="NONE",
    return_text=(
        "本函数返回 `UDINT`：\n\n"
        "| 返回值 | 含义 |\n|---|---|\n"
        "| `0` | 参数非法（地址为 0 或 `n == 0`），未复制任何字节 |\n"
        "| `> 0` | 实际复制的字节数（成功时 = `n`） |\n"
    ),
    scenario="环形缓冲区移位：把样本数组的最新一个元素挤到末尾，前面元素整体左移一格。",
    value="MEMCPY 在重叠区域行为未定义；MEMMOVE 保证正确移位，替代 5–10 行手写 FOR 循环。",
    alt=(
        "- 手写 FOR 循环：可读但慢且容易写错方向。\n"
        "- MEMCPY：不重叠时更快，重叠时**不能**用。"
    ),
    xml_scen="环形采样缓冲区左移：每次新采样到来时，把 aSamples[1..9] 整体左移到 aSamples[0..8]，aSamples[9] 留给新值。",
    xml_val="MEMCPY 在重叠区行为未定义；MEMMOVE 保证正确。",
    xml_verify="在线 bShiftRequest := TRUE 触发一次 → 观察 aSamples[0] 等于之前的 aSamples[1] 值。",
    xml_vars=[
        ("aSamples", "ARRAY[0..9] OF LREAL", None, "环形采样缓冲（10 个）"),
        ("lrNewSample", "LREAL", "0.0", "新采样值（在线写入）"),
        ("bShiftRequest", "BOOL", None, "在线写 TRUE 触发一次移位"),
        ("nBytesShifted", "UDINT", None, "实际移位字节数"),
        ("rtShift", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "// 上升沿检测，避免周期性误触发\n"
        "rtShift(CLK := bShiftRequest);\n"
        "IF rtShift.Q THEN\n"
        "    // 把 aSamples[1..9] 整体左移到 aSamples[0..8]；源和目的重叠，必须 MEMMOVE\n"
        "    nBytesShifted := MEMMOVE(\n"
        "        destAddr := ADR(aSamples[0]),\n"
        "        srcAddr  := ADR(aSamples[1]),\n"
        "        n        := SIZEOF(aSamples) - SIZEOF(aSamples[0])\n"
        "    );\n"
        "    // 末尾位置填新采样\n"
        "    aSamples[9] := lrNewSample;\n"
        "END_IF;\n"
    ),
    related=["MEMCPY", "MEMSET", "MEMCMP"],
)

_add(
    "MEMSET",
    summary=(
        "MEMSET 把目的地址开始的 `n` 个字节全部填充为 `fillByte` 的值。"
        "典型用法是清零（`fillByte := 0`）一个结构体或缓冲区；速度远快于手写 FOR 循环逐字段赋零。"
        "**直接操作物理内存**，参数错误可能崩溃，PDF NOTICE 明确警告。"
    ),
    ftype="FUNCTION",
    behavior=(
        "**调用方式**：同步函数，返回时填充完成。\n\n"
        "**参数语义**：`destAddr` 通常 `ADR(myVar)`；`n` 通常 `SIZEOF(myVar)`。`fillByte` 是单字节值（`USINT`），每个字节都被写为该值——清零用 `0`，清成全 1 用 `16#FF`。\n\n"
        "**返回值**：返回实际写入字节数；`destAddr == 0` 或 `n == 0` 时返回 0。\n\n"
        "**性能**：底层是 C `memset`，速度接近内存带宽峰值；远快于手写循环。"
    ),
    pitfalls=[
        ("**只能填充 1 字节模式**：不能直接用 MEMSET 把 `WORD` 数组填充为某个 16 位值；要填 `0xAAAA` 这种 pattern 必须循环填或自己实现。", False),
        ("**不查边界**：`n > SIZEOF(buf)` 会写坏邻近变量。永远 `n := SIZEOF(buf)`。", False),
        ("**清零结构体陷阱**：结构体里有 STRING / 类对象时，MEMSET 0 会破坏其内部状态（null terminator 被覆盖到中间）。结构体清零优先用 `myStruct := DEFAULT_VALUE_OF_TYPE;` 整体赋值。", True),
        ("**浮点数清零是 0.0**：把 LREAL 数组用 MEMSET 0 填充结果是 +0.0（IEEE 754 全 0 字节）；要填 NaN / Inf 必须用循环或 MEMCPY 一个预制 pattern。", True),
    ],
    var_desc={
        "destAddr": "要填充的内存起始地址（`PVOID`）。用 `ADR(buf)`。",
        "fillByte": "填充字节值（`USINT` 范围 0–255）。清零用 0；全 1 用 `16#FF`。",
        "n": "要填充的字节数。常用 `SIZEOF(buf)`。",
    },
    return_kind="NONE",
    return_text=(
        "本函数返回 `UDINT`：\n\n"
        "| 返回值 | 含义 |\n|---|---|\n"
        "| `0` | 参数非法（`destAddr == 0` 或 `n == 0`），未填充任何字节 |\n"
        "| `> 0` | 实际填充的字节数（成功时 = `n`） |\n"
    ),
    scenario="设备启动时把一个 1 KB 的工艺数据缓冲区一次性清零，避免冷启动残留旧数据污染逻辑。",
    value="一行代码替代 1024 次 BYTE 赋零循环；速度快约 5–10 倍。",
    alt=(
        "- 手写 FOR 循环逐字节赋零：慢且代码冗长。\n"
        "- 结构体整体赋值 `myStruct := (default)`：编译器自动展开，更类型安全。"
    ),
    xml_scen="设备启动时一次性清零 1 KB 工艺缓冲区，避免冷启动残留旧数据。",
    xml_val="一行调用替代 1024 次 FOR 赋零；快 5-10 倍。",
    xml_verify="bClearRequest := TRUE → 观察 aBigBuffer 全部归零；nBytesCleared = 1024。",
    xml_vars=[
        ("aBigBuffer", "ARRAY[0..1023] OF BYTE", None, "1 KB 工艺缓冲区"),
        ("bClearRequest", "BOOL", None, "在线写 TRUE 触发一次清零"),
        ("nBytesCleared", "UDINT", None, "实际清零字节数"),
        ("rtClear", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "rtClear(CLK := bClearRequest);\n"
        "IF rtClear.Q THEN\n"
        "    nBytesCleared := MEMSET(\n"
        "        destAddr := ADR(aBigBuffer),\n"
        "        fillByte := 0,\n"
        "        n        := SIZEOF(aBigBuffer)\n"
        "    );\n"
        "END_IF;\n"
    ),
    related=["MEMCPY", "MEMMOVE", "MEMCMP"],
)

_add(
    "MEMCMP",
    summary=(
        "MEMCMP 比较两个内存区域的前 `n` 字节，返回 `-1` / `0` / `1` 三态表示大小关系。"
        "比较方式与 C `memcmp` 一致：逐字节无符号比较，遇到第一个不同字节即返回结果。"
        "适用于结构体批量相等性检查、二进制数据 diff 等场景。"
    ),
    ftype="FUNCTION",
    behavior=(
        "**调用方式**：同步函数，返回三态值。\n\n"
        "**返回值语义**：\n\n"
        "- `-1`：在第一个不同字节处，`pBuf1` 的值**小于** `pBuf2`；\n"
        "- ` 0`：前 `n` 字节完全相同；\n"
        "- ` 1`：在第一个不同字节处，`pBuf1` 的值**大于** `pBuf2`。\n\n"
        "**逐字节无符号比较**：把字节当作 `USINT` (0–255) 比较；不区分有符号 / 浮点；要比较 LREAL 等浮点用专门的浮点比较（考虑 NaN）。\n\n"
        "**直接操作物理内存**：参数非法（地址 0、n 越界）可能崩溃，PDF NOTICE 警告。\n\n"
        "**典型应用场景**：判等比手写循环灵活，可比较任意类型 / 结构体 / 数组的内存映像；返回三态语义还适用于排序键比较场景。"
    ),
    pitfalls=[
        ("**不可用于浮点比较**：`+0.0` 和 `-0.0` 字节不同但数值相等；NaN 与自身字节相同但 `NaN != NaN`。", False),
        ("**不可用于含 padding 的结构体**：编译器对齐 padding 字节内容未初始化，比较结果不稳定。要比较结构体先 MEMSET 0 再赋值。", False),
        ("**`pBuf1 / pBuf2 == 0`**：PDF 未明确，实测通常返回 0（视为相等）；调用方应自检指针非空。", True),
        ("**返回类型 `DINT`**：不要把返回值当 BOOL 直接用 `IF MEMCMP(...) THEN`——0 = 相等才是 FALSE，反直觉。", False),
    ],
    var_desc={
        "pBuf1": "第一块内存起始地址。",
        "pBuf2": "第二块内存起始地址。",
        "n": "要比较的字节数。",
    },
    return_kind="NONE",
    return_text=(
        "本函数返回 `DINT`：\n\n"
        "| 返回值 | 含义 |\n|---|---|\n"
        "| `-1` | `pBuf1` 在第一个不同字节处小于 `pBuf2` |\n"
        "| `0`  | 前 `n` 字节完全相同 |\n"
        "| `1`  | `pBuf1` 在第一个不同字节处大于 `pBuf2` |\n"
    ),
    scenario="检查 200 字节的工艺参数结构体是否与上次保存的一致——一致则跳过持久化，避免无变化时的频繁写盘。",
    value="一行函数比手写循环 + 早返判等省约 8 行；速度快约 5–10 倍。",
    alt=(
        "- 手写 FOR 循环逐字节比：慢且冗长。\n"
        "- 结构体 `=` 运算符（IEC 不支持）：要 Beckhoff 拓展支持。"
    ),
    xml_scen="检查工艺参数结构体（200 字节）是否与上次落盘的版本一致，一致则跳过持久化写盘。",
    xml_val="一行调用替代 200 次手写逐字节比对。",
    xml_verify="同步两份缓冲区 → 在线触发 bCompareRequest → nCmpResult = 0；故意改 stCurrent 中一个字节 → nCmpResult = 1 或 -1。",
    xml_vars=[
        ("stCurrent", "ARRAY[0..199] OF BYTE", None, "本次工艺参数缓冲（200 字节）"),
        ("stLastSaved", "ARRAY[0..199] OF BYTE", None, "上次落盘版本"),
        ("bCompareRequest", "BOOL", None, "在线写 TRUE 触发一次比较"),
        ("nCmpResult", "DINT", None, "比较结果：-1 / 0 / 1"),
        ("bParamsChanged", "BOOL", None, "TRUE = 与上次不同，需要落盘"),
        ("rtCmp", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "rtCmp(CLK := bCompareRequest);\n"
        "IF rtCmp.Q THEN\n"
        "    nCmpResult := MEMCMP(\n"
        "        pBuf1 := ADR(stCurrent),\n"
        "        pBuf2 := ADR(stLastSaved),\n"
        "        n     := SIZEOF(stCurrent)\n"
        "    );\n"
        "    // 业务侧：非 0 即视为有变化\n"
        "    bParamsChanged := (nCmpResult <> 0);\n"
        "END_IF;\n"
    ),
    related=["MEMCPY", "MEMMOVE", "MEMSET"],
)


# =================== I/O port access (2) ===================

_add(
    "F_IOPortRead",
    summary=(
        "F_IOPortRead 直接读取 PC 内一个 I/O 端口（不是工业 IO 模块，是 x86 主板 I/O 总线上的端口地址）。"
        "适用于直接控制 PC 主板硬件（如蜂鸣器、并口、串口寄存器），是与硬件低层打交道的桥梁。"
        "`eSize` 指定读取宽度（1 / 2 / 4 字节）；返回值是读到的 32 位无符号整数。"
    ),
    ftype="FUNCTION",
    behavior=(
        "**调用方式**：同步函数，立刻返回读到的值。\n\n"
        "**端口宽度 `eSize`**：`E_IOAccessSize` 枚举，常用值 `IOAS_BYTE`（1 字节）、`IOAS_WORD`（2 字节）、`IOAS_DWORD`（4 字节）。读 1 字节时高位字节为 0。\n\n"
        "**端口地址**：典型值是 LPT 端口 `0x378`、串口寄存器 `0x3F8`、PC 蜂鉣器 `0x61` 等 16 位 I/O 空间地址。读地址不会破坏硬件，但写地址（`F_IOPortWrite`）可能损坏，PDF NOTICE 警告。\n\n"
        "**只在 PC / IPC 上有效**：CX 之类的嵌入式控制器可能没有标准的 x86 I/O 端口空间，调用此函数行为未定义。"
    ),
    pitfalls=[
        ("**端口地址必须正确**：错误的端口地址可能读到不相关硬件状态或 0xFF；查 PC 主板手册或设备 datasheet 确认。", False),
        ("**`eSize` 不当**：用 `IOAS_DWORD` 读 8 位端口可能跨端口读取，结果不可靠。匹配硬件实际宽度。", False),
        ("**实时性影响**：直接 I/O 端口操作绕过 OS，可能阻塞 PLC 任务调度；高频调用慎用。", True),
        ("**Embedded PC / Arm 平台**：CX Arm 系列没有 x86 风格 I/O 端口空间，本函数无意义。", True),
    ],
    var_desc={
        "nAddr": "I/O 端口地址（16 位 I/O 空间，如 `16#378` LPT、`16#61` 蜂鉣器）。",
        "eSize": "读取宽度枚举（`IOAS_BYTE` / `IOAS_WORD` / `IOAS_DWORD`），决定读 1 / 2 / 4 字节。",
    },
    return_kind="NONE",
    return_text=(
        "本函数返回 `DWORD`：读到的端口值，高位未读字节为 0（如读 1 字节时高 24 位 = 0）。\n"
    ),
    scenario="读取 LPT 并口当前输入状态做硬件诊断；或读 PC 主板 GPIO 寄存器查询机柜门开关。",
    value="替代 OS 级 DDK 调用 / 写驱动；PLC 一行代码直读硬件端口。",
    alt=(
        "- 写 Windows 驱动 `inp` / `outp`：能用但要内核态权限。\n"
        "- TwinCAT IO Driver（标准 EtherCAT 终端）：现代工程首选，避免直接端口操作。"
    ),
    xml_scen="读取 LPT 端口 0x378 的当前 8 位输入状态做硬件诊断（无 EtherCAT 终端时的应急通道）。",
    xml_val="替代写 Windows 驱动 inp/outp，PLC 一行调用直读硬件端口。",
    xml_verify="bReadRequest := TRUE 一次 → 观察 nPortValue 反映 LPT 引脚状态；改变并口外部输入再触发 → nPortValue 改变。",
    xml_vars=[
        ("nLptPortAddress", "UDINT", "16#378", "LPT1 默认 I/O 端口地址"),
        ("nPortValue", "DWORD", None, "读到的端口值"),
        ("bReadRequest", "BOOL", None, "在线写 TRUE 触发一次读取"),
        ("rtRead", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "// 上升沿检测，避免每周期读耗 CPU\n"
        "rtRead(CLK := bReadRequest);\n"
        "IF rtRead.Q THEN\n"
        "    nPortValue := F_IOPortRead(\n"
        "        nAddr := nLptPortAddress,\n"
        "        eSize := IOAS_BYTE\n"
        "    );\n"
        "END_IF;\n"
    ),
    related=["F_IOPortWrite", "LPTSIGNAL"],
)

_add(
    "F_IOPortWrite",
    summary=(
        "F_IOPortWrite 直接写一个值到 PC 主板的 I/O 端口。"
        "**可能损坏硬件或数据**：PDF NOTICE 明确警告——写错端口可能导致系统崩溃、硬件损坏甚至 SSD 数据丢失。"
        "正确使用前必须明确目标端口的硬件含义。"
    ),
    ftype="FUNCTION",
    behavior=(
        "**调用方式**：同步函数，写入立刻完成并返回 BOOL 表示是否调用成功（不代表硬件实际反应正确）。\n\n"
        "**端口宽度 `eSize`**：与 `F_IOPortRead` 一致：`IOAS_BYTE` / `IOAS_WORD` / `IOAS_DWORD`。\n\n"
        "**返回值**：`TRUE` = 调用层面成功（API 接受了请求）；`FALSE` = API 调用本身失败（如权限不足）。返回 TRUE 不等于硬件按预期工作。\n\n"
        "**只在 PC / IPC 上有效**：Embedded Arm 控制器无标准 x86 I/O 端口空间。\n\n"
        "**PC 蜂鉣器示例**：PDF 用 PC 蜂鉣器（端口 0x42 / 0x43 / 0x61）演示 `FB_Speaker` 的实现，是本函数最常见的合法用例。"
    ),
    pitfalls=[
        ("**写错端口可能毁硬件**：随意试探地址极其危险，可能写入 BIOS / 芯片组寄存器导致永久损坏。**永远**查硬件 datasheet 确认地址。", False),
        ("**返回 TRUE 不等于硬件响应**：API 接受不代表硬件按预期；要验证效果需用 `F_IOPortRead` 回读或外部测量。", False),
        ("**多任务竞争**：同一端口被多个任务同时写，结果不可预期；需要用 `TestAndSet` 或全局互斥保护。", True),
        ("**TwinCAT IO Driver 更安全**：标准 EtherCAT 终端有硬件级保护，远比直接端口写安全。新工程不建议用本函数。", True),
    ],
    var_desc={
        "nAddr": "I/O 端口地址（16 位 I/O 空间）。",
        "eSize": "写入宽度（`IOAS_BYTE` / `IOAS_WORD` / `IOAS_DWORD`）。",
        "nValue": "要写入的值（最大 32 位，高位被 `eSize` 截断）。",
    },
    return_kind="BOOL",
    scenario="实现 PC 蜂鉣器报警声：通过写主板蜂鉣器控制端口产生固定频率声波，用于声音提示。",
    value="不依赖外部 EtherCAT 蜂鉣模块，纯软件触发 PC 内部蜂鉣器；省一个硬件通道。",
    alt=(
        "- EtherCAT 数字输出 + 外置蜂鉣器：硬件方案，更可靠但要额外接线。\n"
        "- Windows `Beep()` 通过 WinAPI：可行但 PLC 调 WinAPI 要写 wrapper。"
    ),
    xml_scen="实现简易 PC 蜂鉣器报警：通过写主板端口 0x61 控制扬声器产生短促提示音（PDF FB_Speaker 示例）。",
    xml_val="不用外置蜂鉣硬件，软件直接驱动 PC 主板内置蜂鉣器。",
    xml_verify="bBeepRequest := TRUE → PC 主板蜂鉣器发出短促提示音；bWriteOk 应为 TRUE。注意：用错端口可能损坏硬件！",
    xml_vars=[
        ("nPcSpeakerPort", "UDINT", "16#61", "PC 蜂鉣器控制端口"),
        ("nValueToWrite", "DWORD", "16#03", "蜂鉣器使能位（PDF 示例中的开启值）"),
        ("bBeepRequest", "BOOL", None, "在线写 TRUE 触发一次写入"),
        ("bWriteOk", "BOOL", None, "TRUE = API 接受写入"),
        ("rtBeep", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "// 上升沿触发：避免连续写端口（连续写蜂鉣器会持续响）\n"
        "// 警告：端口地址 0x61 是 PC 蜂鉣器控制；其它地址可能损坏硬件\n"
        "rtBeep(CLK := bBeepRequest);\n"
        "IF rtBeep.Q THEN\n"
        "    bWriteOk := F_IOPortWrite(\n"
        "        nAddr  := nPcSpeakerPort,\n"
        "        eSize  := IOAS_BYTE,\n"
        "        nValue := nValueToWrite\n"
        "    );\n"
        "END_IF;\n"
    ),
    related=["F_IOPortRead", "LPTSIGNAL"],
)


# =================== General functions (20) ===================

_add(
    "F_CmpLibVersion",
    ftype="FUNCTION",
    summary=(
        "F_CmpLibVersion 把当前安装的库版本（通过 `stLibVersion_<libname>` 全局常量传入）与代码中要求的最小版本（major / minor / build / revision 四元组）做比较，返回 `-1` / `0` / `+1` 表示『装的版本低于 / 等于 / 高于』要求版本。"
        "用于库级版本守门：在工程编译期或运行启动时检查依赖库版本，避免因下层库降级导致接口不兼容的隐蔽 bug。"
    ),
    behavior=(
        "**返回值语义**：\n\n"
        "- `-1`：当前库版本低于要求版本，应当告警或拒绝启动；\n"
        "- ` 0`：当前库版本恰好等于要求版本；\n"
        "- `+1`：当前库版本高于要求版本，通常仍兼容。\n\n"
        "**版本比较顺序**：按字典序——先比 major，相等再比 minor，再 build，最后 revision。任一位较高即返回 +1，较低返回 -1。\n\n"
        "**输入约束**：`stVersion` 必须传入对应库的 `stLibVersion_<libname>`，跨库混用没意义。\n\n"
        "**典型用法**：在 PLC `INIT` 任务或 `FB_init` 中检查依赖，不满足时设置全局错误标志拒绝启动 MAIN 任务，避免后续逻辑跑在错误的库版本上。"
    ),
    pitfalls=[
        ("**版本号比较不区分 release / debug**：本函数只比四元组数字，不关心库的内部构建标识。", False),
        ("**不能比较跨库**：`stLibVersion_Tc2_System` 不能用本函数对照 `stLibVersion_Tc2_Math` 的要求。", False),
        ("**库未引用时编译错误**：`stLibVersion_<libname>` 是常量，库未被工程引用时编译期就报错，不是运行期错误。", True),
        ("**`>= 0` 才算满足要求**：忘了取 `>= 0` 而只判 `= 0` 会拒绝高版本，反而是常见 bug。", False),
    ],
    var_desc={
        "stVersion": "目标库的版本常量，按 `stLibVersion_<libname>` 命名传入（类型 `ST_LibVersion`）。",
        "iMajor": "要求的 major 主版本号。",
        "iMinor": "要求的 minor 次版本号。",
        "iBuild": "要求的 build 构建号。",
        "iRevision": "要求的 revision 修订号。",
    },
    return_kind="NONE",
    return_text=(
        "本函数返回 `DINT`：\n\n"
        "| 返回值 | 含义 | 处理建议 |\n|---|---|---|\n"
        "| `-1` | 装的版本低于要求 | 告警 / 拒绝启动 |\n"
        "| `0`  | 装的版本恰好等于要求 | 视业务需要继续或告警 |\n"
        "| `+1` | 装的版本高于要求 | 通常兼容，继续 |\n"
    ),
    scenario="集成商交付前的版本守门：MAIN 启动时校验 Tc2_System ≥ 3.3.8.0，低版本直接置位 bSystemBlocked 拒绝运行 MAIN，避免依赖新 API 但库没升级的隐蔽崩溃。",
    value="替代『先跑起来出错再查依赖』的低效方式，编译 + 启动时显式守门。",
    alt=(
        "- 检查 `stLibVersion.iMajor` 等字段手写比较：能用但要写 4 个 `IF` 分支，易写反。\n"
        "- 不检查：风险大，库降级后逻辑可能挂在不可预测的地方。"
    ),
    xml_scen="MAIN 启动时检查 Tc2_System 是否 ≥ 3.3.8.0；低版本置位 bSystemBlocked，拒绝运行业务逻辑。",
    xml_val="一行守门替代 4 段 IF 链；启动早期发现版本问题。",
    xml_verify="在线观察 nCmpResult：装的是更新版本时 = 1；改 iMajorRequired := 99 → -1 → bSystemBlocked := TRUE。",
    xml_vars=[
        ("iMajorRequired", "UINT", "3", "要求 major"),
        ("iMinorRequired", "UINT", "3", "要求 minor"),
        ("iBuildRequired", "UINT", "8", "要求 build"),
        ("iRevisionRequired", "UINT", "0", "要求 revision"),
        ("nCmpResult", "DINT", None, "比较结果：-1 / 0 / +1"),
        ("bSystemBlocked", "BOOL", None, "TRUE = 版本不满足，拒绝启动 MAIN"),
    ],
    xml_call=(
        "// 启动期一次性比较；只要 >= 0 即视为满足要求\n"
        "nCmpResult := F_CmpLibVersion(\n"
        "    stVersion := stLibVersion_Tc2_System,\n"
        "    iMajor    := iMajorRequired,\n"
        "    iMinor    := iMinorRequired,\n"
        "    iBuild    := iBuildRequired,\n"
        "    iRevision := iRevisionRequired\n"
        ");\n\n"
        "// 版本不足直接锁住业务逻辑\n"
        "bSystemBlocked := (nCmpResult &lt; 0);\n"
    ),
    related=["stLibVersion_Tc2_System"],
)

_add(
    "F_CheckMemoryArea",
    ftype="FUNCTION",
    summary=(
        "F_CheckMemoryArea 返回一个变量所在的内存区域类别（`E_TcMemoryArea` 枚举）：静态区（编译期分配）、动态区（`__NEW` 堆）、未知 / 非法地址等。"
        "用于诊断指针来源、检测野指针、判断变量是否仍存活——尤其在动态分配 / 释放复杂的场景下，避免使用已经 `__DELETE` 的变量。"
    ),
    behavior=(
        "**返回值**：`E_TcMemoryArea` 枚举，常见值：\n\n"
        "- `eTcMA_Static`：静态分配区（普通 `VAR` / `VAR_GLOBAL`）；\n"
        "- `eTcMA_Dynamic`：动态分配区（`__NEW` 出来的）；\n"
        "- `eTcMA_Retain`：retain 持久化区；\n"
        "- `eTcMA_Unknown` / `eTcMA_Invalid`：地址不属于任何已知区域（如 0 指针或越界）。\n\n"
        "具体枚举值见 InfoSys `E_TcMemoryArea` topic。\n\n"
        "**典型用法**：在通用接口里收到 `PVOID` 指针时，先 `F_CheckMemoryArea` 确认地址合法再解引用，避免野指针崩 PLC。\n\n"
        "**与 `F_GetMappingStatus` 的区别**：本函数判断变量所在的内存类别（静态 / 动态 / 持久化），`F_GetMappingStatus` 判断变量是否被映射到 IO 链。两者关注点不同，常配合使用以诊断变量来源与生命周期。\n\n"
        "**调试技巧**：复现野指针崩溃时，在通用接口入口统一加守护，命中 `eTcMA_Unknown` 即记录调用上下文便于定位。"
    ),
    pitfalls=[
        ("**不检测对象生命周期**：`__DELETE` 后的内存区域可能仍然『属于动态区』，本函数不能判断对象是否还活着。要管理生命周期需自己加引用计数或 owner 字段。", False),
        ("**性能开销**：每次调用要扫描内存映射表，循环里频繁调用会拖累实时性。建议只在边界场景（接口入口）调用。", True),
        ("**`nSize` 必须正确**：传入的 `nSize` 错可能误判跨区域；用 `SIZEOF(myVar)` 取最安全。", False),
    ],
    var_desc={
        "pData": "要检查的变量内存地址，通常 `ADR(myVar)`。",
        "nSize": "变量字节数，通常 `SIZEOF(myVar)`。",
    },
    return_kind="NONE",
    return_text="本函数返回 `E_TcMemoryArea`：枚举常量，具体值见 InfoSys 的 `E_TcMemoryArea` 类型 topic。\n",
    scenario="动态对象池管理：分发指针前先 `F_CheckMemoryArea` 确认指向动态区且非 0，避免业务侧拿到静态地址用 `__DELETE` 释放（会崩溃）。",
    value="替代『假设调用方传对了』的盲信心态；在出 bug 前定位。",
    alt=("- 自己维护 owner 字段 + 引用计数：更准确但要写状态机。\n- 不检查：野指针崩溃风险。"),
    xml_scen="启动时分别检查一个静态局部变量和一个 __NEW 出来的动态变量所在内存区域，演示 F_CheckMemoryArea 的诊断用法。",
    xml_val="替代靠崩溃 / 拷贝调试日志定位野指针的低效方法。",
    xml_verify="bCheckRequest := TRUE 触发一次 → 观察 eAreaStatic = eTcMA_Static（或对应枚举），eAreaDynamic = eTcMA_Dynamic。",
    xml_vars=[
        ("nStaticCounter", "USINT", "0", "静态局部变量（编译期分配）"),
        ("pDynamicValue", "POINTER TO LREAL", None, "动态分配指针（__NEW）"),
        ("eAreaStatic", "E_TcMemoryArea", None, "静态变量的内存区"),
        ("eAreaDynamic", "E_TcMemoryArea", None, "动态变量的内存区"),
        ("eAreaNull", "E_TcMemoryArea", None, "空指针的内存区（应为 Unknown）"),
        ("pNull", "PVOID", "0", "空指针测试用"),
        ("bCheckRequest", "BOOL", None, "在线写 TRUE 触发一次诊断"),
        ("rtCheck", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "rtCheck(CLK := bCheckRequest);\n"
        "IF rtCheck.Q THEN\n"
        "    // 1) 静态变量\n"
        "    eAreaStatic := F_CheckMemoryArea(pData := ADR(nStaticCounter), nSize := SIZEOF(nStaticCounter));\n\n"
        "    // 2) 动态分配；若未分配则先 __NEW\n"
        "    IF pDynamicValue = 0 THEN\n"
        "        pDynamicValue := __NEW(LREAL);\n"
        "    END_IF;\n"
        "    IF pDynamicValue &lt;&gt; 0 THEN\n"
        "        eAreaDynamic := F_CheckMemoryArea(pData := pDynamicValue, nSize := SIZEOF(LREAL));\n"
        "    END_IF;\n\n"
        "    // 3) 空指针\n"
        "    eAreaNull := F_CheckMemoryArea(pData := pNull, nSize := 1);\n"
        "END_IF;\n"
    ),
    related=["F_GetMappingStatus", "F_GetStructMemberAlignment"],
)

_add(
    "F_CreateIPv4Addr",
    ftype="FUNCTION",
    summary=(
        "F_CreateIPv4Addr 把 IPv4 地址的 4 个字节数组（`T_IPv4AddrArr`，4 字节）格式化为字符串（如 `'172.16.7.199'`）。"
        "字节顺序是网络字节序（高字节在前）。"
        "适用于把数字形式的 IP 转成 HMI 显示字符串、日志记录、或拼接 URL 等场景。"
    ),
    behavior=(
        "**输入字节顺序**：`nIds[0]` = IP 第一段，`nIds[3]` = IP 最后一段；与点分十进制阅读顺序一致。\n\n"
        "**返回值**：`T_IPv4Addr` 字符串，固定格式 `D.D.D.D`，每段 0–255，无前导零。\n\n"
        "**典型用法**：从 ADS / DHCP 接口拿到 4 字节 IP 后转字符串显示，或把工程配置中的 4 字节数组转字符串写入配置文件。\n\n"
        "**反向操作**：`F_ScanIPv4AddrIds` 是本函数的反向——字符串→字节数组。"
    ),
    pitfalls=[
        ("**只支持 IPv4**：要 IPv6 字符串拼接需要自己实现或用 `F_FormatStringArray`（其他库）。", False),
        ("**字节序**：传入数组应是网络字节序而不是主机字节序；x86 是小端，如果直接强转 `DWORD` 会颠倒。", False),
        ("**返回值是固定 `T_IPv4Addr` 类型**（约 16 字节字符串），不要赋给 `STRING(7)` 等过短类型。", True),
    ],
    var_desc={
        "nIds": "IPv4 地址的 4 字节数组（`T_IPv4AddrArr`），网络字节序。",
    },
    return_kind="NONE",
    return_text="本函数返回 `T_IPv4Addr`（字符串）：格式 `'D.D.D.D'`，每段 0–255。\n",
    scenario="HMI 显示远端 PLC IP：从 ADS 读到 4 字节 IP 数组后用本函数转成 `'192.168.1.10'` 显示。",
    value="替代手写 `CONCAT(USINT_TO_STRING(...))` 4 次 + 3 个点号；一行代码搞定。",
    alt=("- 手拼字符串：约 4-6 行。\n- `F_FormatStringArray`：通用但更复杂。"),
    xml_scen="HMI 显示远端 PLC IP：从配置数组拿到 4 字节 IPv4 转成 '172.16.7.199' 写到本地字符串变量供 HMI 读。",
    xml_val="一行替代 4 段 CONCAT。",
    xml_verify="在线改 aIpBytes 任一字节 → sIpDisplay 跟着变；aIpBytes := [192,168,1,1] → sIpDisplay = '192.168.1.1'。",
    xml_vars=[
        ("aIpBytes", "T_IPv4AddrArr", "[172, 16, 7, 199]", "IPv4 4 字节数组（网络字节序）"),
        ("sIpDisplay", "T_IPv4Addr", "''", "格式化后的 HMI 显示字符串"),
    ],
    xml_call=(
        "// 每周期格式化一次；4 字节 IP 转 'D.D.D.D' 字符串\n"
        "sIpDisplay := F_CreateIPv4Addr(nIds := aIpBytes);\n"
    ),
    related=["F_ScanIPv4AddrIds", "F_CreateMacAddr"],
)

_add(
    "F_ScanIPv4AddrIds",
    ftype="FUNCTION",
    summary=(
        "F_ScanIPv4AddrIds 是 `F_CreateIPv4Addr` 的反向操作：把 `'172.16.7.199'` 这样的 IPv4 字符串解析成 4 字节数组（`T_IPv4AddrArr`）。"
        "字符串非法时（空串、`'0.0.0.0'`、格式错）返回全零数组——调用方应当通过『非空且非全零』的双重判断检测错误。"
    ),
    behavior=(
        "**解析方式**：从左到右扫描，遇 `.` 或字符串末尾即把当前段写入对应字节，4 段全部填好后返回。\n\n"
        "**错误检测**：PDF 明确给出错误条件——若输入既不是空串、也不是 `'0.0.0.0'`，但返回数组所有字节为 0，则说明解析失败（格式不合法）。调用方必须做此双重检查。\n\n"
        "**网络字节序**：输出与 `F_CreateIPv4Addr` 一致——`aIds[0]` = 第一段。"
    ),
    pitfalls=[
        ("**全零返回有歧义**：`'0.0.0.0'` 合法，错串也返回 0；要区分必须比较输入字符串是否为合法格式。", False),
        ("**只支持 IPv4**：IPv6 字符串解析需要其他库。", False),
        ("**超长 / 含字母**：超过段值 255 或含字母时本函数返回 0，调用方需做合法性校验。", True),
        ("**前导 / 尾部空格**：未明确，建议预先 `TRIM`。", True),
    ],
    var_desc={"sIPv4": "IPv4 字符串（`T_IPv4Addr`），如 `'172.16.7.199'`。"},
    return_kind="NONE",
    return_text="本函数返回 `T_IPv4AddrArr`：4 字节数组（网络字节序）。返回全零 + 输入非 `''` / `'0.0.0.0'` 表示解析失败。\n",
    scenario="操作员在 HMI 输入远端 PLC IP 字符串，PLC 解析成 4 字节供 ADS 调用使用。",
    value="一行替代手写 split + 字符串转数字 4 次循环。",
    alt=("- 手写按 `.` split + `STRING_TO_USINT` 4 次：约 8-12 行。\n- 调用方自己解析：易错。"),
    xml_scen="HMI 输入字符串 IP → PLC 解析成 4 字节数组，再喂给 ADS 调用。带合法性双重校验。",
    xml_val="一行替代手写 split + STRING_TO_USINT 8-12 行。",
    xml_verify="在线改 sUserInput := '192.168.1.100' → aIpParsed = [192,168,1,100]；改成 'abc' → aIpParsed = [0,0,0,0] 且 bParseError = TRUE。",
    xml_vars=[
        ("sUserInput", "T_IPv4Addr", "'172.16.7.199'", "HMI 输入的 IP 字符串"),
        ("aIpParsed", "T_IPv4AddrArr", None, "解析后的 4 字节数组"),
        ("bParseError", "BOOL", None, "TRUE = 非空且全零，解析失败"),
    ],
    xml_call=(
        "// 每周期解析一次；用双重判断检错（全零 + 非合法 0.0.0.0 串）\n"
        "aIpParsed := F_ScanIPv4AddrIds(sIPv4 := sUserInput);\n\n"
        "// 错误判定：非空 / 非 0.0.0.0 但返回全零\n"
        "bParseError := (sUserInput &lt;&gt; '') AND (sUserInput &lt;&gt; '0.0.0.0')\n"
        "             AND (aIpParsed[0] = 0) AND (aIpParsed[1] = 0)\n"
        "             AND (aIpParsed[2] = 0) AND (aIpParsed[3] = 0);\n"
    ),
    related=["F_CreateIPv4Addr"],
)

_add(
    "F_CreateMacAddr",
    ftype="FUNCTION",
    summary=(
        "F_CreateMacAddr 把 6 字节 MAC 地址数组（`T_MacAddrArr`）格式化为字符串（如 `'01-02-03-04-05-06'`）。"
        "可选分隔符 `sSeparator`（默认 `'-'`，常见也用 `':'`）和大小写控制 `bLoCase`（FALSE = 大写 `ABCDEF`，TRUE = 小写 `abcdef`）。"
    ),
    behavior=(
        "**输入**：`aMacAddr` 是 6 字节数组，按硬件 OUI 顺序排列（如 `[0x1C, 0x2C, 0x3C, 0x4C, 0x5C, 0x6C]`）。\n\n"
        "**格式化规则**：每字节转 2 位 16 进制，用 `sSeparator` 拼接。`sSeparator` 长度限 1 字符，超出未定义。\n\n"
        "**返回值**：`T_MacAddr` 字符串，17 字符（6×2 + 5 分隔符），固定长度。\n\n"
        "**典型应用场景**：HMI 网络信息页显示本机 / 远端网卡 MAC、把 MAC 写入工艺日志、生成设备唯一标识用于绑定 license。\n\n"
        "**与 `F_CreateIPv4Addr` 的关系**：风格一致——字节数组 → 字符串；不同点是 MAC 字节没有网络字节序与主机字节序之分（按硬件 OUI 顺序）。"
    ),
    pitfalls=[
        ("**`sSeparator` 限 1 字符**：传 `'::'` 等行为未定义。", False),
        ("**字节序**：按硬件顺序传入；与 IP 不同，MAC 没有『网络字节序』反转。", False),
        ("**大小写不一致**：业务侧切换 `bLoCase` 后 HMI 显示可能与日志记录不一致；建议全工程统一。", True),
    ],
    var_desc={
        "aMacAddr": "6 字节 MAC 地址数组（`T_MacAddrArr`）。",
        "sSeparator": "字节之间的分隔符（1 字符），默认 `'-'`，常用也填 `':'`。",
        "bLoCase": "TRUE 用小写 `abcdef`，FALSE 用大写 `ABCDEF`。默认 FALSE。",
    },
    return_kind="NONE",
    return_text="本函数返回 `T_MacAddr`（字符串，17 字符）：如 `'01-02-03-04-05-06'`。\n",
    scenario="HMI 显示本机网卡 MAC：从 ADS 读取本机 MAC 6 字节，转成 `'1C-2C-3C-4C-5C-6C'` 显示在『网络信息』页面。",
    value="替代手写 6 次 BYTE_TO_HEX + 5 次拼接；一行调用。",
    alt=("- 手拼字符串：约 8-10 行。\n- `F_FormatStringArray`：通用但更复杂。"),
    xml_scen="HMI 显示本机网卡 MAC：从 ADS 读取 6 字节 MAC 转 '1C-2C-3C-4C-5C-6C' 字符串。",
    xml_val="替代手写 6 次 hex 转换 + 5 次拼接 8-10 行。",
    xml_verify="改 aMacBytes 任一字节 → sMacDisplay 跟着变；bUseLowerCase := TRUE → 输出转小写。",
    xml_vars=[
        ("aMacBytes", "T_MacAddrArr", "[16#1C, 16#2C, 16#3C, 16#4C, 16#5C, 16#6C]", "6 字节 MAC 地址"),
        ("sSeparatorChar", "STRING(1)", "'-'", "分隔符：'-' 或 ':'"),
        ("bUseLowerCase", "BOOL", "FALSE", "TRUE 用小写"),
        ("sMacDisplay", "T_MacAddr", "''", "格式化后的 MAC 字符串"),
    ],
    xml_call=(
        "// 每周期格式化一次\n"
        "sMacDisplay := F_CreateMacAddr(\n"
        "    aMacAddr   := aMacBytes,\n"
        "    sSeparator := sSeparatorChar,\n"
        "    bLoCase    := bUseLowerCase\n"
        ");\n"
    ),
    related=["F_CreateIPv4Addr"],
)


_add(
    "F_GetCpuCoreIndex",
    ftype="FUNCTION",
    summary=(
        "F_GetCpuCoreIndex 给定任务索引 `nTaskIndex`，返回该任务运行的 CPU 核心索引。"
        "若传 0，则返回当前调用任务自己所在的核心。无效任务索引返回 `-1`。"
        "用于诊断 PLC 任务的实际 CPU 绑定，配合 `F_GetCpuCoreInfo` 读取该核的基时与负载上限。"
    ),
    behavior=(
        "**返回值含义**：`-1` 表示传入的 `nTaskIndex` 无效；`≥ 0` 是 CPU 核心索引，对应 TwinCAT SYSTEM 节点 Real-time 子节点 Core 列里的数值。\n\n"
        "**典型用法**：多任务工程在线检查每个 PLC 任务的 CPU 分布是否符合预期；如果发现两个高频任务挤在同一核，可在 SYSTEM → Real-time 配置里重新分配。\n\n"
        "**自查方便**：传 0 即可得到当前任务的核心，无需先查任务索引。\n\n"
        "**与 `F_GetCpuCoreInfo` 区别**：本函数只返回核索引，`F_GetCpuCoreInfo` 进一步读出该核的详细配置参数。"
    ),
    pitfalls=[
        ("**任务索引 0 是『自身』而不是『任务 0』**：调用方要查特定任务必须先用 `GETCURTASKINDEXEX` 拿到任务索引再传入。", False),
        ("**返回 -1**：任务索引无效（超出 1..n 范围或任务未配置）；不要把 -1 当成『核心 0』使用。", False),
        ("**Real-time 配置变更**：把任务从 Isolated CPU 切到 Shared CPU 不重启 TwinCAT 时，本函数返回值可能与配置面板显示一致但行为已变。", True),
    ],
    var_desc={"nTaskIndex": "任务索引。`0` = 当前调用任务；`1..n` = 指定任务。"},
    return_kind="NONE",
    return_text="本函数返回 `DINT`：CPU 核心索引（≥ 0）；`-1` 表示任务索引无效。\n",
    scenario="启动时记录每个 PLC 任务的 CPU 绑定到日志，便于上线后远程诊断 CPU 调度问题。",
    value="替代去 SYSTEM 面板逐个看；PLC 代码自助查询。",
    alt=("- 看 SYSTEM 面板：要登工程在线。\n- 自己写 Windows API：太复杂。"),
    xml_scen="启动时记录当前 PLC 主任务所在 CPU 核心，写到全局变量供 HMI 显示。",
    xml_val="替代登工程查 Real-time 面板。",
    xml_verify="在线观察 nCurrentCore 应与 TwinCAT SYSTEM Real-time 面板里 MAIN 任务的 Core 列一致。",
    xml_vars=[
        ("nCurrentCore", "DINT", None, "当前任务所在 CPU 核心索引"),
    ],
    xml_call=(
        "// 0 表示查询调用方自身所在核心，无需先查任务索引\n"
        "nCurrentCore := F_GetCpuCoreIndex(nTaskIndex := 0);\n"
    ),
    related=["F_GetCpuCoreInfo", "GETCURTASKINDEXEX", "F_GetTaskInfo"],
)

_add(
    "F_GetCpuCoreInfo",
    ftype="FUNCTION",
    summary=(
        "F_GetCpuCoreInfo 读取指定 CPU 核心的详细配置信息（基时 / 核心负载上限等）到一个 `ST_CpuCoreInfo` 结构。"
        "返回 `HRESULT`，成功 `S_OK`，无效核心索引返回 `0x9811070B`（参数无效）。"
        "用于运行期诊断 CPU 配置是否符合工艺时序要求。"
    ),
    behavior=(
        "**调用方式**：同步函数，立即返回。`pInfo` 指向调用方分配的 `ST_CpuCoreInfo` 实例。\n\n"
        "**输入约束**：`nCpuCoreIndex` 必须是 TwinCAT 已分配给 PLC 的核心索引（从 `F_GetCpuCoreIndex` 得来）；超出范围返回 `0x9811070B`。\n\n"
        "**输出结构**：`ST_CpuCoreInfo` 包含基时 baseTime（PLC 周期最小单位，单位 100ns）、核心负载上限百分比等字段；具体见 InfoSys `ST_CpuCoreInfo` topic。\n\n"
        "**典型用法**：上电后诊断各核基时一致性，避免跨核任务在不同 baseTime 下产生周期错位。"
    ),
    pitfalls=[
        ("**`pInfo` 必须指向有效 `ST_CpuCoreInfo`**：传 0 或类型错误会读 / 写错地址。永远 `pInfo := ADR(myInfo)`。", False),
        ("**`HRESULT` 解读**：`SUCCEEDED(hr)` 才看 `pInfo^`；失败时 `pInfo^` 内容未定义。", False),
        ("**仅在 TwinCAT v3.1.4024.11 以上可用**（PDF 明确），老版本编译报错。", True),
    ],
    var_desc={
        "nCpuCoreIndex": "要查询的 CPU 核心索引。",
        "pInfo": "`POINTER TO ST_CpuCoreInfo` —— 调用方分配的结构体地址。",
    },
    return_kind="HRESULT",
    scenario="MAIN 启动时读取本核 baseTime，与工艺要求的 1 ms 周期比较，不匹配时告警。",
    value="替代登工程查 Real-time 面板；PLC 代码自助验证 CPU 配置。",
    alt=("- 看 SYSTEM Real-time 面板：登工程才能看。\n- 凭经验默认 1 ms：不可靠。"),
    xml_scen="启动时读取当前核心 baseTime，与工艺要求 1 ms 比较，不匹配则告警。",
    xml_val="替代登工程查 Real-time 面板，PLC 自助验证。",
    xml_verify="在线观察 hrResult = 0；改 nCoreIndex := 99 → hrResult = 0x9811070B。",
    xml_vars=[
        ("nCoreIndex", "DINT", None, "要查询的核心索引（先从 F_GetCpuCoreIndex 拿）"),
        ("stCoreInfo", "ST_CpuCoreInfo", None, "读取到的核心信息结构"),
        ("hrResult", "HRESULT", None, "调用结果：S_OK = 0 / 失败码"),
        ("bCfgOk", "BOOL", None, "TRUE = baseTime 与工艺要求一致"),
    ],
    xml_call=(
        "// 先拿当前核心索引，再查详情\n"
        "nCoreIndex := F_GetCpuCoreIndex(nTaskIndex := 0);\n"
        "hrResult := F_GetCpuCoreInfo(\n"
        "    nCpuCoreIndex := nCoreIndex,\n"
        "    pInfo         := ADR(stCoreInfo)\n"
        ");\n\n"
        "// HRESULT 0 是 S_OK；上层业务判定 baseTime 是否匹配工艺要求\n"
        "// （此处只示意，实际字段名以 ST_CpuCoreInfo 定义为准）\n"
        "bCfgOk := (hrResult = 0);\n"
    ),
    related=["F_GetCpuCoreIndex", "F_GetTaskInfo"],
)

_add(
    "F_GetMappingPartner",
    ftype="FUNCTION",
    summary=(
        "F_GetMappingPartner 返回 PLC 变量映射伙伴端（mapping partner）的对象 ID（`OTCID` 类型）。"
        "若一个 PLC 变量与 IO 链 / NC / 其他 PLC 映射，本函数返回对端对象 ID；用于在运行期诊断映射拓扑。"
    ),
    behavior=(
        "**返回值**：`OTCID` 是 32 位无符号对象 ID，非 0 表示映射伙伴的对象 ID，`0` 表示该变量未映射或映射伙伴不存在。\n\n"
        "**典型用法**：在线诊断某 PLC 变量是否真的与硬件 IO 通道挂上，避免『PLC 写值但 IO 不动』的隐蔽错配。\n\n"
        "**与 `F_GetMappingStatus` 区别**：本函数返回对端 ID（具体是谁），`F_GetMappingStatus` 返回映射状态（是否映射）。两者常配合使用。\n\n"
        "**输入约束**：`p` 用 `ADR(myVar)`，`n` 用 `SIZEOF(myVar)`；尺寸错误可能误判跨变量。"
    ),
    pitfalls=[
        ("**`OTCID = 0`**：未映射 / 映射伙伴不存在；调用方要区分『未配置』与『配置错误』需配合 `F_GetMappingStatus`。", False),
        ("**实时性影响**：每次调用扫映射表，高频循环里别用。", True),
        ("**`OTCID` 解读**：需要查 TwinCAT 对象表才知道具体是哪个 IO / NC / PLC 对象；本函数只给 ID。", False),
    ],
    var_desc={
        "p": "PLC 变量地址（`ADR(myVar)`）。",
        "n": "变量字节数（`SIZEOF(myVar)`）。",
    },
    return_kind="NONE",
    return_text="本函数返回 `OTCID`（`UDINT`）：映射伙伴对象 ID；`0` 表示未映射。\n",
    scenario="启动时检查关键 IO 输入变量是否真的映射到了对应 EtherCAT 终端，未映射立即报告而不是等到执行时出错。",
    value="替代靠『手动比对 IO 配置文件』的低效方式。",
    alt=("- 看 TwinCAT IO 配置树：登工程才能看。\n- 不检查：故障难定位。"),
    xml_scen="MAIN 启动时检查关键输入变量是否映射到 EtherCAT 终端；未映射立即报警。",
    xml_val="替代手动比对 IO 配置树。",
    xml_verify="未映射变量 → nPartnerId = 0；映射变量 → nPartnerId 非零。",
    xml_vars=[
        ("bMonitoredInput", "BOOL", None, "应当映射到某 EtherCAT DI 通道的关键输入"),
        ("nPartnerId", "OTCID", None, "对端对象 ID；0 = 未映射"),
        ("bMappedOk", "BOOL", None, "TRUE = 已映射"),
    ],
    xml_call=(
        "nPartnerId := F_GetMappingPartner(\n"
        "    p := ADR(bMonitoredInput),\n"
        "    n := SIZEOF(bMonitoredInput)\n"
        ");\n\n"
        "// 非零即视为已挂上 IO 链\n"
        "bMappedOk := (nPartnerId &lt;&gt; 0);\n"
    ),
    related=["F_GetMappingStatus", "F_CheckMemoryArea"],
)

_add(
    "F_GetMappingStatus",
    ftype="FUNCTION",
    summary=(
        "F_GetMappingStatus 返回 PLC 变量的映射状态枚举（`EPlcMappingStatus`）：未映射、已映射、部分映射。"
        "用于在线诊断 IO / NC / 跨 PLC 映射的真实状态，比单纯读 IO 配置树更准确。"
    ),
    behavior=(
        "**返回值 `EPlcMappingStatus`**：\n\n"
        "- `MS_Unmapped`：变量未参与任何映射；\n"
        "- `MS_Mapped`：变量整体映射到某个伙伴；\n"
        "- `MS_Partial`：变量部分字节映射（典型于结构体里只映射了部分字段）。\n\n"
        "**与 `F_GetMappingPartner` 区别**：本函数只回三态状态，`F_GetMappingPartner` 进一步告诉对端是谁。两者配合使用：先用本函数过滤出非 `MS_Mapped` 的变量，再用 `F_GetMappingPartner` 看具体对端 ID 定位问题。\n\n"
        "**典型用法**：上线前一次性扫描所有重要变量的映射状态，把 `MS_Partial` 或 `MS_Unmapped` 项汇总成报告写入诊断日志。`MS_Partial` 通常是工程配置错误（结构体只挂了部分字段），需要工程师立即修复，运行期再发现就晚了。\n\n"
        "**调用开销**：每次调用扫一遍映射表，开销与系统映射条目数成正比，避免在 PLC MAIN 循环里高频调用。"
    ),
    pitfalls=[
        ("**`MS_Partial` 容易忽略**：结构体里只映射几个字段时返回 `MS_Partial`，要不要算『映射完成』取决于业务。", False),
        ("**实时性影响**：与 `F_GetMappingPartner` 一致，每次调用扫表。", True),
        ("**`nSize` 错误**：传错可能跨越多个变量造成误判。永远 `SIZEOF(myVar)`。", False),
    ],
    var_desc={
        "p": "PLC 变量地址（`ADR(myVar)`）。",
        "n": "变量字节数（`SIZEOF(myVar)`）。",
    },
    return_kind="NONE",
    return_text="本函数返回 `EPlcMappingStatus`：`MS_Unmapped` / `MS_Mapped` / `MS_Partial`。\n",
    scenario="启动后扫描所有 IO 变量的映射状态，把任何 `MS_Unmapped` / `MS_Partial` 项写入告警日志便于运维定位。",
    value="替代手工比对 IO 配置树。",
    alt=("- 看配置树：登工程才能看。\n- `F_GetMappingPartner` 配合：得到更详细的对端 ID。"),
    xml_scen="启动时扫描一个关键 IO 输入变量的映射状态，未完全映射即告警。",
    xml_val="自动化映射诊断。",
    xml_verify="未映射 → eMapStatus = MS_Unmapped；正常映射 → MS_Mapped。",
    xml_vars=[
        ("bMonitoredInput", "BOOL", None, "应映射的关键输入变量"),
        ("eMapStatus", "EPlcMappingStatus", None, "映射状态枚举"),
        ("bMappingOk", "BOOL", None, "TRUE = 已完全映射"),
    ],
    xml_call=(
        "eMapStatus := F_GetMappingStatus(\n"
        "    p := ADR(bMonitoredInput),\n"
        "    n := SIZEOF(bMonitoredInput)\n"
        ");\n\n"
        "// 只把『完全映射』算 OK；部分映射或未映射都视为异常\n"
        "bMappingOk := (eMapStatus = MS_Mapped);\n"
    ),
    related=["F_GetMappingPartner"],
)

_add(
    "F_GetStructMemberAlignment",
    ftype="FUNCTION",
    summary=(
        "F_GetStructMemberAlignment 返回当前 TwinCAT runtime 使用的结构体成员对齐字节数（1 / 2 / 4 / 8）。"
        "对齐设置直接影响结构体内存布局（padding 字节数）：x86 通常 8，Arm 通常 4。"
        "用于跨平台序列化 / 反序列化、与 PC 端 C / C# 程序对接时校验布局一致性。"
    ),
    behavior=(
        "**返回值**：`BYTE` 类型，值为 1 / 2 / 4 / 8，表示结构体成员的对齐边界。\n\n"
        "**对齐影响**：例如 `BYTE + LREAL` 结构体在 8 字节对齐下 SIZEOF = 16（7 字节 padding），在 1 字节对齐下 SIZEOF = 9 无 padding。\n\n"
        "**典型用法**：跨平台数据交换时校验 PLC 与 PC 端结构体布局一致；若 PC 端用 `#pragma pack(1)` 而 PLC 是 8 字节对齐，必须用 `MEMCPY` + 手算偏移，不能直接 `MEMCPY` 整个结构。"
    ),
    pitfalls=[
        ("**编译期常量**：本值由 TwinCAT 版本和目标平台决定，运行期不会变。", True),
        ("**ALIGN pragma 不影响本函数**：变量级的 `{attribute 'pack_mode' := '1'}` 不改全局返回值；要看实际 SIZEOF 才能知道结构体真布局。", True),
        ("**跨平台序列化必须显式打包**：依赖默认对齐做跨平台 IPC 极其脆弱；建议每个字段单独 `MEMCPY` 或用 protobuf / JSON。", True),
    ],
    var_desc={},
    return_kind="NONE",
    return_text="本函数返回 `BYTE`：对齐字节数（1 / 2 / 4 / 8）。\n",
    scenario="MAIN 启动时记录当前平台对齐到日志，便于跨平台部署时一眼看出 x86 vs Arm 的差异。",
    value="替代凭经验猜对齐；运行期实测最准。",
    alt=("- 凭经验：x86 = 8，Arm = 4——大多数对但偶尔会错。\n- 看 PDF：要找特定版本。"),
    xml_scen="启动时记录当前平台对齐字节数到全局诊断变量；跨平台部署时一眼看出差异。",
    xml_val="实测最准，替代凭经验猜。",
    xml_verify="在 x86 工控机上观察 nAlignBytes = 8；在 Arm CX 上观察 = 4。",
    xml_vars=[
        ("nAlignBytes", "BYTE", None, "当前平台对齐字节数（1 / 2 / 4 / 8）"),
    ],
    xml_call=(
        "// 一次调用即可，平台对齐不会运行期改变\n"
        "nAlignBytes := F_GetStructMemberAlignment();\n"
    ),
    related=["MEMCPY", "F_CheckMemoryArea"],
)

_add(
    "F_GetTaskInfo",
    ftype="FUNCTION",
    summary=(
        "F_GetTaskInfo 返回当前调用任务的 `PlcTaskSystemInfo` 结构，包含任务索引、周期时间、优先级、最大执行时长、抖动统计等字段。"
        "用于运行期监控任务负载、检测超周期、性能瓶颈分析。"
    ),
    behavior=(
        "**调用方式**：同步函数，立即返回 `PlcTaskSystemInfo` 结构副本。\n\n"
        "**结构字段**：`PlcTaskSystemInfo` 包含 `taskIndex`、`cycleTime`（任务设置的周期）、`lastExecTime`（上次实际执行时间）、`maxExecTime`、`minExecTime`、`cycleTimeExceeded`（超周期标志）、`priority` 等。\n\n"
        "**典型用法**：MAIN 周期里调用本函数把 `lastExecTime` 存到 HMI 可视化变量，运维直接看到 PLC 任务的实际开销。\n\n"
        "**性能监控模式**：在 MAIN 任务里调用本函数取 `maxExecTime`，与 `cycleTime` 做比，超过 80% 即报警，能在真正超周期之前提前预警。配合 `F_GetCpuCoreIndex` 可知道任务被分配到哪个 CPU 核。\n\n"
        "**调用即得**：本函数无任何输入参数，返回值是结构体副本；不需要额外的状态机或异步等待。"
    ),
    pitfalls=[
        ("**返回的是『调用所在任务』的信息**：不能查别的任务；要查其他任务用 ADS 读 `Task` 节点。", False),
        ("**结构副本开销**：`PlcTaskSystemInfo` 不算大，但每个 PLC 周期调用一次额外几十纳秒。", True),
        ("**`cycleTimeExceeded` 一次性触发**：建议自己加 latch，否则错过一拍可能漏报。", True),
    ],
    var_desc={},
    return_kind="NONE",
    return_text="本函数返回 `PlcTaskSystemInfo`：包含 cycleTime / lastExecTime / maxExecTime / cycleTimeExceeded / priority 等字段的结构体。\n",
    scenario="HMI 监控页显示 PLC MAIN 任务的实际周期、最大执行时间、抖动；运维一眼看出是否超周期。",
    value="替代登工程看实时面板。",
    alt=("- 登工程 Real-time 面板：远程不方便。\n- ADS Read：可以但要拼报文。"),
    xml_scen="每周期把 MAIN 任务的最大执行时间存到 HMI 可视化变量；运维直接看到是否超周期。",
    xml_val="替代登工程开 Real-time 面板远程观察。",
    xml_verify="加重 PLC 负载（如批量 MEMCPY）→ 观察 stMyTaskInfo.maxExecTime 增大。",
    xml_vars=[
        ("stMyTaskInfo", "PlcTaskSystemInfo", None, "本任务系统信息"),
    ],
    xml_call=(
        "// 每周期更新一次任务信息到 HMI 可视化变量\n"
        "stMyTaskInfo := F_GetTaskInfo();\n"
    ),
    related=["F_GetCpuCoreIndex", "GETCURTASKINDEXEX"],
)

_add(
    "F_RaiseException",
    ftype="FUNCTION",
    summary=(
        "F_RaiseException 在 PLC 代码中主动抛出一个运行时异常，异常码由 `ExceptionCode`（来自 `__SYSTEM.ExceptionCode` 枚举或自定义 `UDINT`）指定。"
        "在 `__TRY` 块外抛会被 TwinCAT 异常处理捕获并停止 PLC；在 `__TRY` 内可被 `__CATCH` 捕获。"
        "用于实现自定义错误流程、断言失败、不可恢复错误中止。"
    ),
    behavior=(
        "**`__TRY` 内 vs 外**：\n\n"
        "- `__TRY` 块外抛出：异常进入 TwinCAT 全局异常处理，PLC 停止执行。\n"
        "- `__TRY` 块内抛出：可在 `__CATCH(exc)` 块中捕获并处理，PLC 不停。\n\n"
        "**异常码**：可用 `__SYSTEM.ExceptionCode` 枚举（如 `RTSEXCPT_DIVIDEBYZERO`），也可自定义 `UDINT` 值。\n\n"
        "**典型用法**：在断言失败（如关键参数越界、状态机进入不可达分支）时主动抛异常，让 PLC 显式停在错误现场而不是隐蔽继续。\n\n"
        "**控制流影响**：调用本函数后控制流立即转移到最近的 `__CATCH` 块或全局异常处理器；调用点之后的代码**不会执行**。所以本函数不需要返回值——它要么终止任务要么进入捕获块。\n\n"
        "**与 IEC 11 标准的关系**：`__TRY` / `__CATCH` / `__FINALLY` / `__ENDTRY` 是 CODESYS / TwinCAT 拓展，不是 IEC 61131-3 标准，跨厂商不可移植。"
    ),
    pitfalls=[
        ("**`__TRY` 外抛出会立刻停 PLC**：必须确保 demo / 测试代码包裹在 `__TRY` / `__CATCH` 里，否则一抛异常生产环境直接停机。", False),
        ("**异常码冲突**：自定义码建议在高位段（如 `16#80000000+`）避免与 TwinCAT 内置 `__SYSTEM.ExceptionCode` 冲突。", True),
        ("**捕获后状态恢复**：`__CATCH` 内可读 `__SYSTEM.LastException` 检查；处理完需主动恢复局部状态。", True),
        ("**与 `bError` / `nErrId` 共存**：业务可恢复错误用 `bError`，不可恢复或编程错误才用本函数。", True),
    ],
    var_desc={"ExceptionCode": "异常码（`UDINT`）。可用 `__SYSTEM.ExceptionCode` 枚举或自定义 `UDINT` 值。"},
    return_kind="NONE",
    return_text="本函数无返回值（抛异常后控制流转移）。\n",
    scenario="在状态机进入『不可能到达』的 default 分支时主动 `F_RaiseException`，让 PLC 显式停在现场，便于事后分析比静默继续更好。",
    value="替代 `printf` 日志 + 静默继续的弱断言；真正强制中止。",
    alt=("- `bError := TRUE` + 业务流程跳转：可恢复错误用这个。\n- `RETURN`：静默退出，调试难。"),
    xml_scen="在状态机的 default 分支（不可达）主动抛异常，让 PLC 停在现场便于事后分析。用 __TRY/__CATCH 演示捕获 + 恢复模式。",
    xml_val="替代 printf 日志 + 静默继续，真正强制中止。",
    xml_verify="bTriggerAssertion := TRUE → 观察 nExceptionCaught 非零且 nCounterCatch 递增；恢复执行流。",
    xml_vars=[
        ("bTriggerAssertion", "BOOL", None, "在线写 TRUE 触发一次断言失败"),
        ("nExceptionCaught", "UDINT", None, "捕获到的异常码"),
        ("nCounterCatch", "UDINT", None, "进入 __CATCH 的次数"),
        ("nCounterAfter", "UDINT", None, "异常处理后继续执行的次数"),
        ("rtTrig", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "rtTrig(CLK := bTriggerAssertion);\n"
        "IF rtTrig.Q THEN\n"
        "    __TRY\n"
        "        // 模拟『不可达分支』的断言失败\n"
        "        F_RaiseException(ExceptionCode := 16#80000001);\n"
        "    __CATCH(nExceptionCaught)\n"
        "        // 捕获后记录并恢复\n"
        "        nCounterCatch := nCounterCatch + 1;\n"
        "    __ENDTRY\n"
        "END_IF;\n\n"
        "// 异常处理完后业务继续\n"
        "nCounterAfter := nCounterAfter + 1;\n"
    ),
    related=[],
)

_add(
    "F_SplitPathName",
    ftype="FUNCTION",
    summary=(
        "F_SplitPathName 把一个完整路径字符串（如 `'C:\\BC\\INCLUDE\\file.txt'`）拆成 4 个分量：盘符 / 目录 / 文件名 / 扩展名，输出到 4 个 `VAR_IN_OUT` 字符串。"
        "返回 `BOOL`：`TRUE` 成功，`FALSE` 失败（路径格式不合法）。"
        "适用于配方 / 日志路径预处理：根据扩展名分发、根据目录归类。"
    ),
    behavior=(
        "**输出 4 个分量**：\n\n"
        "- `sDrive`：盘符 + 冒号（如 `'C:'`），3 字符 STRING；\n"
        "- `sDir`：目录路径，**含**前导和尾随反斜杠（如 `'\\BC\\INCLUDE\\'`），`T_MaxString`；\n"
        "- `sFileName`：文件名主体（不含扩展名），`T_MaxString`；\n"
        "- `sExt`：扩展名**含**点号（如 `'.txt'`），`T_MaxString`。\n\n"
        "**返回值**：`TRUE` = 拆分成功；`FALSE` = 路径格式错（缺少盘符或非法字符）。\n\n"
        "**调用方负责分配输出字符串**：4 个 `VAR_IN_OUT` 都由调用方提供本地变量，FB 把结果写进去。`sDrive` 必须分配 `STRING(3)` 容量，其他 3 个 `T_MaxString`（约 255 字节）。\n\n"
        "**调用例子**：完整路径 `'C:\\\\BC\\\\INCLUDE\\\\file.txt'` 拆分后 `sDrive = 'C:'`、`sDir = '\\\\BC\\\\INCLUDE\\\\'`、`sFileName = 'file'`、`sExt = '.txt'`。\n\n"
        "**纯字符串处理**：本函数同步函数，立即返回；不做文件系统访问，路径不存在或无效路径不报错，只检查格式。"
    ),
    pitfalls=[
        ("**`sDir` 含尾随 `\\`**：拼新路径时不要重复加 `\\`，否则得到 `'C:\\dir\\\\file.txt'` 双斜杠。", False),
        ("**`sExt` 含点号**：业务比较扩展名要用 `'.csv'` 而不是 `'csv'`。", False),
        ("**Linux 风格 `/` 路径**：PDF 没明确，实测 Windows 上 `/` 也能被识别为分隔符，但建议统一用 `\\`。", True),
        ("**`VAR_IN_OUT` 必须先分配本地变量**：不能传匿名表达式。", False),
    ],
    var_desc={
        "sPathName": "完整路径字符串，格式 `'X:\\DIR\\SUBDIR\\FILENAME.EXT'`。",
        "sDrive": "**输出**：盘符（如 `'C:'`），3 字符。",
        "sDir": "**输出**：目录路径（如 `'\\BC\\INCLUDE\\'`），含前后反斜杠。",
        "sFileName": "**输出**：文件名主体（不含扩展名）。",
        "sExt": "**输出**：扩展名（如 `'.txt'`），含点号。",
    },
    return_kind="BOOL",
    scenario="读到一份新的工艺文件路径 `'D:\\Recipes\\Apr\\BatchA.csv'`，根据 `sExt = '.csv'` 走 CSV 解析分支，根据 `sDir` 把文件名记录到对应月份归档表。",
    value="替代手写 `RIGHT` / `FIND` / `MID` 4 段：一行得到 4 分量。",
    alt=("- 手写字符串扫描：约 15-20 行。"),
    xml_scen="读到工艺文件路径 → 拆出扩展名 .csv 走 CSV 解析分支；按目录归档到月份表。",
    xml_val="一行替代 15-20 行字符串扫描。",
    xml_verify="改 sFullPath 为不同路径 → 4 个分量自动更新；非法路径 → bSplitOk = FALSE。",
    xml_vars=[
        ("sFullPath", "T_MaxString", "'D:\\Recipes\\Apr\\BatchA.csv'", "完整路径"),
        ("sDriveOut", "STRING(3)", "''", "盘符输出"),
        ("sDirOut", "T_MaxString", "''", "目录输出"),
        ("sFileBase", "T_MaxString", "''", "文件名输出"),
        ("sFileExt", "T_MaxString", "''", "扩展名输出"),
        ("bSplitOk", "BOOL", None, "TRUE = 拆分成功"),
    ],
    xml_call=(
        "// 单次完整调用；VAR_IN_OUT 必须传本地变量\n"
        "bSplitOk := F_SplitPathName(\n"
        "    sPathName := sFullPath,\n"
        "    sDrive    := sDriveOut,\n"
        "    sDir      := sDirOut,\n"
        "    sFileName := sFileBase,\n"
        "    sExt      := sFileExt\n"
        ");\n"
    ),
    related=["FB_FileOpen"],
)


_add(
    "SETBIT32",
    ftype="FUNCTION",
    summary=(
        "SETBIT32 把 32 位输入值 `inVal32` 中指定位号 `bitNo` 设为 1，返回修改后的值；原值不被改写。"
        "`bitNo` 范围 0-31，**超出范围会内部 modulo 32**（如 `bitNo = 32` 实际作用于 bit 0）。"
        "适用于位掩码 / 状态字 / 标志组合的纯函数式拼装。"
    ),
    behavior=(
        "**算法**：返回值 = `inVal32 OR (1 SHL (bitNo MOD 32))`。\n\n"
        "**modulo 行为**：`bitNo` 超过 31 时自动 mod 32，PDF 明确指出。但依赖此行为容易出 bug，建议调用方自己保证范围。\n\n"
        "**纯函数**：不修改 `inVal32`；要更新原变量需 `myVar := SETBIT32(myVar, 5)`。\n\n"
        "**与 IEC `BIT_OPERATIONS`**：本函数等价于 `inVal32 OR SHL(DWORD#1, bitNo)`，但更直观、可读性更好。\n\n"
        "**示例**：`SETBIT32(16#00000000, 31) = 16#80000000`（PDF 原文示例）。\n\n"
        "**典型应用场景**：组合多个 BOOL 状态到 DWORD 状态字给 HMI 一次读取、组装 EtherCAT 控制字、维护错误码位标志等。语义比直接位掩码运算清晰，新手代码可读性大幅提升。"
    ),
    pitfalls=[
        ("**modulo 32 隐藏 bug**：`bitNo = 33` 实际改 bit 1，可能掩盖上层逻辑的越界错误。建议自己用 `IF bitNo &gt; 31 THEN ... ; END_IF;` 显式校验。", False),
        ("**`bitNo` 是 `SINT`**：负数行为未定义（实测仍 mod 32 但要看二进制补码）。", True),
        ("**返回值不写回原变量**：忘记 `:= SETBIT32(...)` 是常见错误，结果原变量没变。", False),
    ],
    var_desc={
        "inVal32": "要操作的 32 位值。",
        "bitNo": "位号 0-31。超出自动 mod 32。",
    },
    return_kind="NONE",
    return_text="本函数返回 `DWORD`：把 `bitNo` 位置 1 后的新值（原值不变）。\n",
    scenario="拼装设备状态字：根据多个布尔状态依次置位组成一个 32 位状态字写到 HMI，比 `dwStatus := dwStatus OR 16#02` 这种魔法数字可读性强得多。",
    value="可读性比 OR + 移位强；避免魔法数字。",
    alt=("- `dwVal OR SHL(1, bitNo)`：等价但难读。\n- 自己写 `IF/ELSE` 分支：冗长。"),
    xml_scen="拼装设备状态字：根据 bMotorReady / bDoorClosed 等多个状态位置位组合成 32 位状态字。",
    xml_val="可读性强，省魔法数字。",
    xml_verify="bMotorReady := TRUE → 观察 dwStatusWord bit0 = 1；bDoorClosed := TRUE → bit1 = 1。",
    xml_vars=[
        ("bMotorReady", "BOOL", "FALSE", "电机就绪"),
        ("bDoorClosed", "BOOL", "FALSE", "安全门已关"),
        ("dwStatusWord", "DWORD", "0", "组合后的状态字（HMI 显示）"),
    ],
    xml_call=(
        "// 每周期重新组合：先清零再按状态置位\n"
        "dwStatusWord := 0;\n"
        "IF bMotorReady THEN\n"
        "    dwStatusWord := SETBIT32(inVal32 := dwStatusWord, bitNo := 0);\n"
        "END_IF;\n"
        "IF bDoorClosed THEN\n"
        "    dwStatusWord := SETBIT32(inVal32 := dwStatusWord, bitNo := 1);\n"
        "END_IF;\n"
    ),
    related=["CSETBIT32", "CLEARBIT32", "GETBIT32"],
)

_add(
    "CSETBIT32",
    ftype="FUNCTION",
    summary=(
        "CSETBIT32 是 `SETBIT32` 的『C 风格』变体：根据 `bitVal` 决定把 `bitNo` 位**设为 1 还是 0**，省去自己判断走 SETBIT32 还是 CLEARBIT32 的分支。"
        "返回修改后的 32 位值。"
    ),
    behavior=(
        "**算法**：`bitVal = TRUE` → 同 `SETBIT32`；`bitVal = FALSE` → 同 `CLEARBIT32`。\n\n"
        "**`bitNo` modulo 32**：与 `SETBIT32` 一致。\n\n"
        "**纯函数**：要更新原变量需 `myVar := CSETBIT32(myVar, 5, bFlag)`。\n\n"
        "**示例**：`CSETBIT32(16#80000000, 15, TRUE) = 16#80008000`（PDF 原文）。\n\n"
        "**典型用法**：根据 BOOL 旗标动态置位 / 清位，例如『读到 DI 高电平 → 把状态字 bit5 置 1，低电平 → 清 0』。把 32 个 BOOL 通道打包到 DWORD 状态字时尤其方便，可以省掉 IF / ELSE 分支。\n\n"
        "**与 `SETBIT32` / `CLEARBIT32` 关系**：本函数 = 两者的合成；旗标 TRUE 走 SETBIT32 路径，FALSE 走 CLEARBIT32 路径。可读性更高的同时函数调用开销也相同。"
    ),
    pitfalls=[
        ("**`bitVal` 必须明确**：传 BOOL 表达式时确保结果非 NULL / 未初始化。", True),
        ("**`bitNo` 同 SETBIT32 的 modulo 32**：负数 / 越界要小心。", False),
        ("**返回值不写回原变量**：与 SETBIT32 同坑。", False),
    ],
    var_desc={
        "inVal32": "要操作的 32 位值。",
        "bitNo": "位号 0-31。",
        "bitVal": "TRUE 置 1；FALSE 清 0。",
    },
    return_kind="NONE",
    return_text="本函数返回 `DWORD`：根据 `bitVal` 把 `bitNo` 位设为 1 或 0 后的新值。\n",
    scenario="把 32 个 DI 通道的实时状态打包到一个 DWORD 状态字（每位对应一通道），HMI 一次读取就拿到全部 32 通道状态。",
    value="替代 SETBIT32 / CLEARBIT32 二选一的 IF 分支。",
    alt=("- IF + SETBIT32 / CLEARBIT32：2 倍代码量。"),
    xml_scen="把 32 个 DI 通道实时状态打包到一个 DWORD（每位对应一通道），HMI 一次读取拿全部状态。",
    xml_val="替代 IF + SETBIT/CLEARBIT 二选一，代码量减半。",
    xml_verify="aDigitalInputs[5] := TRUE → 观察 dwPackedDi bit5 = 1；TRUE → FALSE → bit5 = 0。",
    xml_vars=[
        ("aDigitalInputs", "ARRAY[0..31] OF BOOL", None, "32 个 DI 通道"),
        ("dwPackedDi", "DWORD", "0", "打包后的状态字"),
        ("i", "INT", None, "循环变量"),
    ],
    xml_call=(
        "// 每周期把 32 个 BOOL 打包到一个 DWORD\n"
        "dwPackedDi := 0;\n"
        "FOR i := 0 TO 31 DO\n"
        "    dwPackedDi := CSETBIT32(\n"
        "        inVal32 := dwPackedDi,\n"
        "        bitNo   := TO_SINT(i),\n"
        "        bitVal  := aDigitalInputs[i]\n"
        "    );\n"
        "END_FOR;\n"
    ),
    related=["SETBIT32", "CLEARBIT32", "GETBIT32"],
)

_add(
    "GETBIT32",
    ftype="FUNCTION",
    summary=(
        "GETBIT32 读取 32 位值 `inVal32` 中指定位号 `bitNo` 的状态，返回 `BOOL`（`TRUE` = 1，`FALSE` = 0）。"
        "原值不变；纯读操作。"
        "用于解码状态字 / 标志组合，反向操作是 `SETBIT32` / `CLEARBIT32` / `CSETBIT32`。"
    ),
    behavior=(
        "**算法**：返回值 = `(inVal32 AND (1 SHL (bitNo MOD 32))) <> 0`。\n\n"
        "**`bitNo` modulo 32**：超出范围自动 mod 32（PDF 明确）。\n\n"
        "**示例**：`GETBIT32(16#04, 2) = TRUE`（PDF 原文）。\n\n"
        "**与 IEC `BIT_OPERATIONS` 关系**：本函数等价于 `(inVal32 AND SHL(DWORD#1, bitNo)) <> 0`，但更直观。\n\n"
        "**典型应用场景**：解码 HMI 命令字（DWORD 各位对应不同命令）、解析 EtherCAT 状态字 Statusword、提取错误码各位标志、检查打包到 DWORD 的多通道 DI 状态等。语义比直接位掩码运算清晰，避免新手把 `AND` 结果误当 BOOL。\n\n"
        "**反向操作**：`SETBIT32` / `CLEARBIT32` / `CSETBIT32` 是配套的『写位』函数，本函数是『读位』。"
    ),
    pitfalls=[
        ("**`bitNo` modulo 32 隐藏 bug**：同 SETBIT32。", False),
        ("**`bitNo` 是 `SINT`**：负数行为未定义。", True),
        ("**返回 BOOL 而不是 INT**：直接当数字算术会编译错。要数字用 `BOOL_TO_INT(GETBIT32(...))`。", False),
    ],
    var_desc={
        "inVal32": "要读取的 32 位值。",
        "bitNo": "位号 0-31。",
    },
    return_kind="NONE",
    return_text="本函数返回 `BOOL`：TRUE = 该位为 1；FALSE = 该位为 0。\n",
    scenario="解码 HMI 命令字：读到一个 DWORD 命令字后用 `GETBIT32` 提取每位含义（bit0 = 启动、bit1 = 停止、bit2 = 复位 等）。",
    value="替代 AND + 移位 + 非零比较；可读性强。",
    alt=("- `(dwVal AND SHL(1, bitNo)) <> 0`：等价但难读。"),
    xml_scen="解码 HMI 命令字：DWORD 中 bit0=启动 / bit1=停止 / bit2=复位，逐位提取成 BOOL 喂给业务状态机。",
    xml_val="比 AND + 移位 + 比较可读得多。",
    xml_verify="在线写 dwCommandWord := 1 → bCmdStart = TRUE；写 5（bit0+bit2）→ bCmdStart + bCmdReset = TRUE。",
    xml_vars=[
        ("dwCommandWord", "DWORD", "0", "HMI 写入的命令字"),
        ("bCmdStart", "BOOL", None, "bit0 = 启动"),
        ("bCmdStop", "BOOL", None, "bit1 = 停止"),
        ("bCmdReset", "BOOL", None, "bit2 = 复位"),
    ],
    xml_call=(
        "// 每周期解码命令字\n"
        "bCmdStart := GETBIT32(inVal32 := dwCommandWord, bitNo := 0);\n"
        "bCmdStop  := GETBIT32(inVal32 := dwCommandWord, bitNo := 1);\n"
        "bCmdReset := GETBIT32(inVal32 := dwCommandWord, bitNo := 2);\n"
    ),
    related=["SETBIT32", "CLEARBIT32", "CSETBIT32"],
)

_add(
    "CLEARBIT32",
    ftype="FUNCTION",
    summary=(
        "CLEARBIT32 把 32 位值 `inVal32` 中指定位号 `bitNo` 清零，返回新值；原值不变。"
        "与 `SETBIT32` 完全对称（一个置 1、一个置 0），共同构成位操作工具集。"
    ),
    behavior=(
        "**算法**：返回值 = `inVal32 AND NOT (1 SHL (bitNo MOD 32))`。\n\n"
        "**`bitNo` modulo 32**：同 SETBIT32。\n\n"
        "**纯函数**：要更新原变量需 `myVar := CLEARBIT32(myVar, 5)`。\n\n"
        "**示例**：`CLEARBIT32(16#C0000000, 31) = 16#40000000`（PDF 原文）。\n\n"
        "**典型用法**：复位错误标志、清理状态字的某些位、在状态机切换分支前清掉前一个分支留下的位标志。\n\n"
        "**与 `SETBIT32` 对称**：两个函数共同构成位操作工具集；`CSETBIT32` 是『二合一』变体。三者搭配可以替代所有 `OR` / `AND NOT` 位运算的常见场景，让代码可读性大幅提升。\n\n"
        "**性能**：底层是单条 CPU 位指令，几乎无开销，可以放心在 PLC 主循环里高频调用。"
    ),
    pitfalls=[
        ("**`bitNo` modulo 32**：同 SETBIT32。", False),
        ("**返回值不写回原变量**：与 SETBIT32 同坑。", False),
        ("**`bitNo` 是 `SINT`**：负数未定义。", True),
    ],
    var_desc={
        "inVal32": "要操作的 32 位值。",
        "bitNo": "位号 0-31。",
    },
    return_kind="NONE",
    return_text="本函数返回 `DWORD`：把 `bitNo` 位清零后的新值。\n",
    scenario="错误恢复时清掉状态字中所有错误位，保留运行状态位；用 CLEARBIT32 比 NOT + AND 直观。",
    value="可读性比 AND + NOT 强。",
    alt=("- `dwVal AND NOT SHL(1, bitNo)`：等价但难读。"),
    xml_scen="错误恢复：清掉状态字中所有错误位（bit16-23），保留运行状态位 0-15。",
    xml_val="可读性比 AND NOT 强。",
    xml_verify="dwStatus := 16#FFFFFFFF; bResetRequest := TRUE → 观察 dwStatus 高 8 位被逐一清零。",
    xml_vars=[
        ("dwStatusWord", "DWORD", "16#FFFFFFFF", "初始状态字"),
        ("bResetErrorBits", "BOOL", None, "在线写 TRUE 触发一次错误位清零"),
        ("i", "INT", None, "循环变量"),
        ("rtReset", "R_TRIG", None, "上升沿检测"),
    ],
    xml_call=(
        "// 上升沿触发一次清错：把状态字 bit16-23 全部清零\n"
        "rtReset(CLK := bResetErrorBits);\n"
        "IF rtReset.Q THEN\n"
        "    FOR i := 16 TO 23 DO\n"
        "        dwStatusWord := CLEARBIT32(\n"
        "            inVal32 := dwStatusWord,\n"
        "            bitNo   := TO_SINT(i)\n"
        "        );\n"
        "    END_FOR;\n"
        "END_IF;\n"
    ),
    related=["SETBIT32", "CSETBIT32", "GETBIT32"],
)

_add(
    "GETCURTASKINDEXEX",
    ftype="FUNCTION",
    summary=(
        "GETCURTASKINDEXEX 返回当前调用任务的索引：`-1` = Windows 上下文（非实时）、`0` = 实时上下文但非循环 PLC 任务（如 `FB_init` 初始化）、`1..n` = 循环 PLC 任务索引。"
        "比老版 `GETCURTASKINDEX` 多一层 Windows / 非循环上下文识别能力。"
    ),
    behavior=(
        "**返回值三态**：\n\n"
        "- `-1`：Windows 上下文调用（如 HMI 写入触发的 PLC 函数、非实时线程）。\n"
        "- `0`：实时上下文但**非**循环 PLC 任务——典型场景是 `FB_init` 方法的自动调用、初始化阶段。\n"
        "- `1..n`：当前循环 PLC 任务的索引（与 SYSTEM 节点里的任务编号一致）。\n\n"
        "**典型用法**：写库代码时根据上下文做不同行为——例如初始化阶段（返回 0）跳过实时校验，循环任务里才执行业务。HMI 触发的同步 PLC 函数（通过 ADS 进入 PLC 上下文）会返回 -1，业务可借此识别『不是我自己循环里调的』。\n\n"
        "**与 `GETCURTASKINDEX` 区别**：老版 `GETCURTASKINDEX`（功能块，3.1.7 节）只返回循环任务索引 1..n，无法区分 Windows / FB_init 上下文，被本函数取代。新工程优先用本函数。\n\n"
        "**实时性**：函数调用本身开销几十纳秒，可以放心在 PLC 循环里调用。"
    ),
    pitfalls=[
        ("**`-1` 不等于错误**：是 Windows 上下文的合法返回值，业务侧要明确区分。", False),
        ("**`0` 不等于『任务 0』**：是『非循环实时上下文』的标记，与 `F_GetCpuCoreIndex(0)` 的『0 = 自身』语义不同。", False),
        ("**频繁调用开销**：实时性敏感的循环里限频调用。", True),
    ],
    var_desc={},
    return_kind="NONE",
    return_text="本函数返回 `DINT`：`-1` Windows、`0` 实时非循环、`1..n` 循环任务索引。\n",
    scenario="编写通用库时根据上下文决定行为：`FB_init` 里返回 0 时跳过 ADS 调用（ADS 在 init 阶段不可用），循环任务里才发 ADS。",
    value="替代盲调用导致初始化阶段崩溃。",
    alt=("- 用 `GETCURTASKINDEX` 老版：分不清 -1 / 0。\n- 自己加 `bInited` 标志：可行但要状态机。"),
    xml_scen="编写通用 FB 时根据上下文区分初始化阶段（返回 0）与循环阶段（返回 1..n），跳过不能在 init 阶段做的调用。",
    xml_val="替代盲调用导致 init 期崩溃。",
    xml_verify="观察 nMyTaskIdx：循环任务里 ≥ 1；FB_init 内调用 = 0；从 HMI / Windows 调 PLC 函数 = -1。",
    xml_vars=[
        ("nMyTaskIdx", "DINT", None, "当前任务上下文"),
        ("eContext", "INT", None, "0=Win, 1=Init, 2=Cyclic"),
    ],
    xml_call=(
        "nMyTaskIdx := GETCURTASKINDEXEX();\n\n"
        "// 简单分类\n"
        "IF nMyTaskIdx &lt; 0 THEN\n"
        "    eContext := 0;        // Windows 上下文\n"
        "ELSIF nMyTaskIdx = 0 THEN\n"
        "    eContext := 1;        // 实时非循环（FB_init）\n"
        "ELSE\n"
        "    eContext := 2;        // 循环 PLC 任务\n"
        "END_IF;\n"
    ),
    related=["F_GetCpuCoreIndex", "F_GetTaskInfo"],
)

_add(
    "LPTSIGNAL",
    ftype="FUNCTION",
    summary=(
        "LPTSIGNAL 在 Centronics 并口（LPT 端口）的指定引脚上输出高 / 低电平。"
        "适用于用示波器观察 PLC 任务执行时序的低成本调试手段，或控制并口连接的简单外设。"
        "返回 `BOOL`：`TRUE` 调用成功，`FALSE` 失败。"
    ),
    behavior=(
        "**端口地址**：`PortAddr` 是 LPT 端口 I/O 地址，典型 LPT1 = `16#378`、LPT2 = `16#278`。\n\n"
        "**引脚号**：`PinNo` 0-7 对应数据线 D0-D7。\n\n"
        "**电平**：`OnOff = TRUE` 输出高电平，`FALSE` 输出低电平。\n\n"
        "**示例**：`LPTSIGNAL(16#378, 7, TRUE)` 把 LPT1 端口的 bit7（D7 引脚）拉高。\n\n"
        "**底层实现**：本函数实际是 `F_IOPortWrite` 的封装，针对并口数据线做了简化。\n\n"
        "**典型应用场景**：用外接示波器观测 PLC 任务的实际执行时序——在任务入口拉高、出口拉低，示波器看到的方波周期即为真实任务周期、占空比即为执行时间占比。这是低成本但极有效的实时性调试手段。\n\n"
        "**与现代替代方案**：新工程优先用 EtherCAT 数字输出终端（如 EL2008）做时序观测，硬件兼容性更广；本函数仅在已有 LPT 接口的工控机上仍有用。"
    ),
    pitfalls=[
        ("**老硬件依赖**：现代工控机大多没有 LPT 物理端口；要调试时序优先用 EtherCAT 数字输出。", True),
        ("**端口地址错误**：写到错误地址可能影响其他设备；查 BIOS 确认 LPT 实际地址。", False),
        ("**实时性影响**：每次调用涉及 OS I/O，慎在高频循环里用。", True),
        ("**多任务竞争**：同时写同一 LPT 端口会冲突，需要互斥保护。", True),
    ],
    var_desc={
        "PortAddr": "LPT 端口地址（16 位 I/O 空间）。LPT1 通常 `16#378`。",
        "PinNo": "引脚号 0-7，对应数据线 D0-D7。",
        "OnOff": "TRUE 输出高；FALSE 输出低。",
    },
    return_kind="BOOL",
    scenario="用示波器观察 MAIN 任务的实际周期：在 MAIN 入口和出口各调一次 `LPTSIGNAL` 拉高 / 拉低 LPT D7，示波器上即可看到周期波形。",
    value="比加 print 日志直观；硬件级时序观察。",
    alt=("- EtherCAT 数字输出 + DO 终端：更现代但要硬件。\n- 加日志统计：精度差。"),
    xml_scen="用示波器观察 MAIN 任务实际周期：入口拉高 D7、出口拉低 D7，示波器看到的方波周期 = 实际任务周期。",
    xml_val="硬件级时序观察，比日志统计精度高。",
    xml_verify="示波器接 LPT1 D7 引脚 → 看到周期性方波；周期与 SYSTEM 配的任务周期一致。",
    xml_vars=[
        ("bLptOk1", "BOOL", None, "入口拉高调用结果"),
        ("bLptOk2", "BOOL", None, "出口拉低调用结果"),
    ],
    xml_call=(
        "// MAIN 入口拉高 LPT D7 引脚\n"
        "bLptOk1 := LPTSIGNAL(\n"
        "    PortAddr := 16#378,\n"
        "    PinNo    := 7,\n"
        "    OnOff    := TRUE\n"
        ");\n\n"
        "// ... 此处写业务逻辑（被示波器观察） ...\n\n"
        "// MAIN 出口拉低\n"
        "bLptOk2 := LPTSIGNAL(\n"
        "    PortAddr := 16#378,\n"
        "    PinNo    := 7,\n"
        "    OnOff    := FALSE\n"
        ");\n"
    ),
    related=["F_IOPortRead", "F_IOPortWrite"],
)

_add(
    "TestAndSet",
    ftype="FUNCTION",
    summary=(
        "TestAndSet 是一个原子操作：检查 BOOL 标志 `Flag` 是否为 FALSE；若是，把它设为 TRUE 并返回 TRUE（拿到锁）；若已经是 TRUE，直接返回 FALSE（锁已被占）。"
        "整个操作不会被其他任务打断，可实现轻量级信号量 / 互斥锁，用于多任务共享数据保护。"
    ),
    behavior=(
        "**原子语义**：本函数在硬件层面用 CPU 原子指令实现，保证『读 → 比 → 写』三步不可中断。多任务同时调用时仅一个能拿到锁。\n\n"
        "**典型用法**：临界区保护——拿锁 → 操作共享数据 → 还锁（手动 `Flag := FALSE;`）。\n\n"
        "**`Flag` 是 `VAR_IN_OUT`**：必须传一个实际变量（通常 `VAR_GLOBAL`），不能传表达式。\n\n"
        "**与信号量的关系**：本函数是『一次性锁』，不带计数；要实现可重入或计数信号量需要自己封装。\n\n"
        "**释放是普通赋值**：业务侧主动 `myFlag := FALSE` 即释放锁，**无对应的『TestAndClear』**。"
    ),
    pitfalls=[
        ("**忘记释放锁导致死锁**：拿了锁不还，其他任务永远拿不到。建议把 `TestAndSet` + 临界操作 + `Flag := FALSE` 放在一个 IF 块里，避免 RETURN / 异常路径漏掉释放。", False),
        ("**非可重入**：同一任务再次拿同一锁会返回 FALSE（自己锁自己），不像 Windows CriticalSection。", False),
        ("**不能跨 PLC**：仅本地 CPU 内有效，跨 PLC 共享变量请用 ADS 锁或文件锁。", False),
        ("**长时间持锁损害实时性**：临界区代码要短小，长时间持锁会阻塞其他任务。", True),
    ],
    var_desc={"Flag": "要测试并置位的 BOOL 标志（`VAR_IN_OUT`）。TRUE → 已被占，FALSE → 空闲。"},
    return_kind="BOOL",
    scenario="MAIN 任务（1 ms 周期）和 SLOW 任务（100 ms 周期）共享一个工艺参数结构体；用 `TestAndSet` 保护更新过程，防止 SLOW 任务读到 MAIN 写一半的脏数据。",
    value="替代关中断 / 禁任务调度；比 `__SLEEP` 节省 CPU。",
    alt=("- 关中断：影响 OS 调度。\n- 双缓冲 + 原子指针交换：性能更好但代码复杂。"),
    xml_scen="MAIN 与 SLOW 任务共享一组工艺参数；用 TestAndSet 保护短临界区写入，避免脏读。",
    xml_val="替代关中断；CPU 友好。",
    xml_verify="并发任务下观察 nDataInconsistency 永远 = 0；故意改成不加锁版本 → 偶尔出现脏读。",
    xml_vars=[
        ("bGlobalLock", "BOOL", "FALSE", "全局互斥标志（应放在 GVL，这里 demo 用本地）"),
        ("bAcquiredLock", "BOOL", None, "本周期是否成功拿到锁"),
        ("aSharedParams", "ARRAY[0..7] OF DINT", None, "受保护的共享数组"),
        ("nWriteValue", "DINT", "0", "本周期要写入的值"),
        ("nBlockedCnt", "DINT", None, "未拿到锁的次数（用于诊断争用）"),
    ],
    xml_call=(
        "// 状态/计数标志按周期刷新：本周期默认未持锁\n"
        "bAcquiredLock := FALSE;\n\n"
        "IF TestAndSet(Flag := bGlobalLock) THEN\n"
        "    bAcquiredLock := TRUE;\n"
        "    // === 临界区开始：原子地更新共享数据 ===\n"
        "    aSharedParams[0] := nWriteValue;\n"
        "    aSharedParams[1] := nWriteValue + 1;\n"
        "    aSharedParams[2] := nWriteValue + 2;\n"
        "    // === 临界区结束 ===\n"
        "    bGlobalLock := FALSE;   // 显式释放\n"
        "ELSE\n"
        "    // 没拿到锁，记一次争用次数\n"
        "    nBlockedCnt := nBlockedCnt + 1;\n"
        "END_IF;\n"
    ),
    related=[],
)


# =================== [Obsolete] (3) ===================

_add(
    "F_GetVersionTcSystem",
    ftype="FUNCTION",
    status="verified · deprecated",
    summary=(
        "**⚠️ 已废弃**：F_GetVersionTcSystem 读取 PLC 库版本信息的某个元素（major / minor / revision），每次调用只能返回一个分量。"
        "PDF 与 InfoSys 都明确建议**改用全局常量 `stLibVersion_Tc2_System`**——一次性拿到完整版本结构，无需多次调用，更安全可读。"
        "保留本函数仅为兼容老代码；新工程禁用。"
    ),
    behavior=(
        "**已废弃，不建议在新代码中使用。**\n\n"
        "**原始行为**：根据 `nVersionElement` 取版本结构里的一个字段：\n\n"
        "- `1` = major（主版本号）\n"
        "- `2` = minor（次版本号）\n"
        "- `3` = revision（修订号）\n\n"
        "**返回值 `UINT`**：对应字段值；越界 `nVersionElement` 行为未明确，建议不要传 1-3 之外的值。\n\n"
        "**替代方案**：直接读 `stLibVersion_Tc2_System.iMajor` / `.iMinor` / `.iBuild` / `.iRevision` 字段，一次性获取所有信息，避免 3 次函数调用。本函数在新工程中应当完全避免使用。"
    ),
    pitfalls=[
        ("**已废弃**：PDF / InfoSys 明确建议改用 `stLibVersion_Tc2_System` 全局常量。新工程不要用本函数。", False),
        ("**只返回 3 个字段**：原始版本结构是 4 字段（major/minor/build/revision），本函数没有访问 build 的方式。", False),
        ("**多次调用**：要拿完整版本必须调 3 次；用常量结构一行搞定。", True),
    ],
    var_desc={"nVersionElement": "要读的版本字段：1 = major、2 = minor、3 = revision。"},
    return_kind="NONE",
    return_text="本函数返回 `UINT`：对应字段的数值。无 build 字段访问能力。\n",
    scenario="**仅老代码维护场景**：维护一份多年前写的工程，看见用了 `F_GetVersionTcSystem` 时知道它在干什么。新工程一律改用 `stLibVersion_Tc2_System.iMajor` 等。",
    value="无新价值；已被全局常量取代。",
    alt=(
        "- `stLibVersion_Tc2_System.iMajor / iMinor / iBuild / iRevision`：**推荐**，一次读所有字段。\n"
        "- `F_CmpLibVersion`：直接比对版本，省去手算。"
    ),
    xml_scen="对照演示：分别用废弃的 F_GetVersionTcSystem 和现代的 stLibVersion_Tc2_System 读 major，对比两者结果应当一致。",
    xml_val="提醒读者切换到现代写法。",
    xml_verify="观察 nMajorOld = nMajorNew；若不一致说明工程引用的库版本与当前运行不一致。",
    xml_vars=[
        ("nMajorOld", "UINT", None, "废弃方式读到的 major"),
        ("nMajorNew", "UINT", None, "现代方式读到的 major"),
        ("bMatched", "BOOL", None, "TRUE = 两种方式结果一致"),
    ],
    xml_call=(
        "// 废弃方式（仅演示，不要在新代码用）\n"
        "nMajorOld := F_GetVersionTcSystem(nVersionElement := 1);\n\n"
        "// 现代方式：一行直接读全局常量字段\n"
        "nMajorNew := stLibVersion_Tc2_System.iMajor;\n\n"
        "// 应当一致\n"
        "bMatched := (nMajorOld = nMajorNew);\n"
    ),
    related=["stLibVersion_Tc2_System", "F_CmpLibVersion"],
)

_add(
    "GETSYSTEMTIME",
    ftype="FUNCTION_BLOCK",
    status="verified · deprecated",
    summary=(
        "**⚠️ 已废弃**：GETSYSTEMTIME 是功能块，读取系统时间戳（64 位整数，每单位 100ns，1601-01-01 以来的累计计数）。"
        "PDF 明确指出**改用 `F_GetSystemTime` 函数**——只需一个返回值而不是两个输出，调用更简洁。"
        "保留本 FB 仅为兼容老代码。"
    ),
    behavior=(
        "**已废弃，不建议在新代码中使用。**\n\n"
        "**原始行为**：每次调用都更新 64 位时间戳，拆成 `timeLoDW`（低 32 位）和 `timeHiDW`（高 32 位）两个 `UDINT` 输出。\n\n"
        "**时间起点**：1601-01-01 00:00:00 UTC，与 Windows FILETIME 一致。\n\n"
        "**单位**：100 ns。要换算成秒需 `/ 10_000_000`。\n\n"
        "**替代方案**：`F_GetSystemTime()` 函数直接返回 `T_FILETIME64` 结构（含 64 位整数字段），无需手动拼装高低 32 位。\n\n"
        "**为何废弃**：FB 形式调用啰嗦（要先实例化），返回两个分量需手动拼成 64 位。函数版本一行调用更优。"
    ),
    pitfalls=[
        ("**已废弃**：用 `F_GetSystemTime()` 函数替代。", False),
        ("**手拼高低 32 位**：要得到完整 64 位需 `nFull := SHL(TO_ULINT(timeHiDW), 32) OR TO_ULINT(timeLoDW)`，易写错。", False),
        ("**FB 实例化开销**：函数版本无需实例化，更省内存。", True),
    ],
    var_desc={
        "timeLoDW": "**输出**：时间戳低 32 位。",
        "timeHiDW": "**输出**：时间戳高 32 位。",
    },
    scenario="**仅老代码维护场景**：维护用了 GETSYSTEMTIME 的工程时知道含义。新工程一律改 `F_GetSystemTime()` 函数。",
    value="无新价值；已被函数版本取代。",
    alt=("- `F_GetSystemTime()`：**推荐**，一行调用，返回完整 64 位结构。"),
    xml_scen="对照演示：调用废弃的 GETSYSTEMTIME 与现代 F_GetSystemTime()，两者拼出的 64 位时间戳应当一致。",
    xml_val="提醒切换到现代写法。",
    xml_verify="观察 ulFullTimeOld = ulFullTimeNew（或差距 ≤ 1 个 PLC 周期）。",
    xml_vars=[
        ("fbGetSystemTime", "GETSYSTEMTIME", None, "废弃 FB 实例（仅演示）"),
        ("nTimeLo", "UDINT", None, "废弃方式低 32 位"),
        ("nTimeHi", "UDINT", None, "废弃方式高 32 位"),
        ("ulFullTimeOld", "ULINT", None, "废弃方式拼装的 64 位"),
    ],
    xml_call=(
        "// 废弃方式：先调 FB，再手动拼接两个 UDINT 成 ULINT\n"
        "fbGetSystemTime(\n"
        "    timeLoDW => nTimeLo,\n"
        "    timeHiDW => nTimeHi\n"
        ");\n"
        "ulFullTimeOld := SHL(TO_ULINT(nTimeHi), 32) OR TO_ULINT(nTimeLo);\n\n"
        "// 现代写法（注释，需 Tc2_System 提供 F_GetSystemTime 函数）：\n"
        "// stFt := F_GetSystemTime();\n"
        "// ulFullTimeNew := stFt.dwHighDateTime ... 等\n"
    ),
    related=["GETTASKTIME"],
)

_add(
    "GETTASKTIME",
    ftype="FUNCTION_BLOCK",
    status="verified · deprecated",
    summary=(
        "**⚠️ 已废弃**：GETTASKTIME 是功能块，读取**当前任务的预期启动时间**（64 位时间戳，1601-01-01 起算，单位 100 ns）。"
        "PDF 明确建议**改用 `F_GetTaskTime` 函数**。"
        "保留本 FB 仅为兼容老代码；新工程禁用。"
    ),
    behavior=(
        "**已废弃，不建议在新代码中使用。**\n\n"
        "**与 `GETSYSTEMTIME` 区别**：GETSYSTEMTIME 返回当前实际时刻；本 FB 返回当前 PLC 任务的『预期启动时间』——这个时刻是 TwinCAT 调度器为本周期任务规划的开始时间，可能略早于 `GETSYSTEMTIME`（任务延迟时差更大）。\n\n"
        "**返回 64 位拆两段**：与 GETSYSTEMTIME 同结构（`timeLoDW` + `timeHiDW`）。\n\n"
        "**典型用法**：测量任务延迟 / 抖动——`GETSYSTEMTIME - GETTASKTIME` 即为本周期任务实际延迟。\n\n"
        "**替代方案**：`F_GetTaskTime()` 函数。"
    ),
    pitfalls=[
        ("**已废弃**：用 `F_GetTaskTime()` 函数替代。", False),
        ("**返回的是『预期启动』而不是『当前实际』**：与 GETSYSTEMTIME 不同；测量抖动时要两者差值。", False),
        ("**手拼高低 32 位**：同 GETSYSTEMTIME 的坑。", False),
    ],
    var_desc={
        "timeLoDW": "**输出**：任务启动时间戳低 32 位。",
        "timeHiDW": "**输出**：任务启动时间戳高 32 位。",
    },
    scenario="**仅老代码维护场景**：维护用了 GETTASKTIME 的工程。新工程改用 `F_GetTaskTime()` 函数。",
    value="无新价值；已被函数版本取代。",
    alt=("- `F_GetTaskTime()`：**推荐**，一行调用。\n- `F_GetTaskInfo()`：获取更全的任务信息（含 lastExecTime 等）。"),
    xml_scen="对照演示：调用废弃 GETTASKTIME 与现代写法，两者拼出的任务启动时间戳应一致。",
    xml_val="提醒切换到现代写法。",
    xml_verify="观察 ulTaskStartOld 与 ulTaskStartNew 应当一致。",
    xml_vars=[
        ("fbGetTaskTime", "GETTASKTIME", None, "废弃 FB 实例（仅演示）"),
        ("nTaskTimeLo", "UDINT", None, "低 32 位"),
        ("nTaskTimeHi", "UDINT", None, "高 32 位"),
        ("ulTaskStartOld", "ULINT", None, "拼装的 64 位任务启动时刻"),
    ],
    xml_call=(
        "// 废弃方式\n"
        "fbGetTaskTime(\n"
        "    timeLoDW => nTaskTimeLo,\n"
        "    timeHiDW => nTaskTimeHi\n"
        ");\n"
        "ulTaskStartOld := SHL(TO_ULINT(nTaskTimeHi), 32) OR TO_ULINT(nTaskTimeLo);\n\n"
        "// 现代写法：ulTaskStartNew := F_GetTaskTime();\n"
    ),
    related=["GETSYSTEMTIME"],
)


# =================== Global constants (1) ===================

_add(
    "Constants",
    ftype="VAR_GLOBAL",
    summary=(
        "Tc2_System 库提供一组全局常量集中定义在 `Constants`（章节 6.1）中，覆盖 ADS 端口号、ADS 状态码、ADS 索引组、文件打开模式等多类常量。"
        "应用代码不要硬编码这些数字，应直接引用对应的常量符号，提升可读性并避免维护时数字写错。"
    ),
    behavior=(
        "**常量分组**：\n\n"
        "**1. ADS 端口号（`AMSPORT_*`）**：标识 TwinCAT 各服务的端口。常用：\n\n"
        "- `AMSPORT_R0_PLC_RTS1` = 801 （TwinCAT 2.x PLC Runtime 1，老版兼容）\n"
        "- `AMSPORT_R0_PLC_TC3` = 851 （TwinCAT 3 PLC Runtime，新版默认）\n"
        "- `AMSPORT_R0_NC` = 500 （NC Server）\n"
        "- `AMSPORT_R0_IO` = 300 （IO Server）\n"
        "- `AMSPORT_LOGGER` = 100 （日志服务器）\n"
        "- `AMSPORT_R3_SYSSERV` = 10000 （System Service）\n\n"
        "**2. ADS 状态码（`ADSSTATE_*`）**：标识 ADS 对象当前状态：`ADSSTATE_RUN` = 5、`ADSSTATE_STOP` = 6、`ADSSTATE_CONFIG` = 15、`ADSSTATE_RECONFIG` = 16 等。\n\n"
        "**3. ADS 索引组（`ADSIGRP_*`）**：标识 ADS 数据访问的索引组：`ADSIGRP_SYMTAB` = `16#F000`、`ADSIGRP_SYM_INFOBYNAME` 等。\n\n"
        "**4. 其他**：文件打开模式（`FOPEN_MODE*`）、Default ADS 超时（`DEFAULT_ADS_TIMEOUT`）等。\n\n"
        "**全部常量见 PDF §6.1**。本节列出最常用的；完整列表逐条搬运过来意义不大，建议查 PDF 或 InfoSys 对应章节。"
    ),
    pitfalls=[
        ("**不要硬编码数字**：写 `nPort := 801` 不如 `nPort := AMSPORT_R0_PLC_RTS1` 直观；后续维护看到 851 还是 801 一目了然。", False),
        ("**TwinCAT 2 vs 3 PLC 端口**：851 是 TC3 默认，老工程的 801 / 811 是 TC2，跨版本通讯要核对。", False),
        ("**常量值不可改**：`VAR_GLOBAL CONSTANT` 编译期定下，运行期赋值会报错。", True),
    ],
    var_desc={},
    return_kind="NONE",
    return_text=(
        "本节是 `VAR_GLOBAL CONSTANT` 集合，无返回值。\n\n"
        "**核心常量速查**：\n\n"
        "| 常量名 | 值 | 说明 |\n|---|---|---|\n"
        "| `AMSPORT_R0_PLC_TC3` | 851 | TwinCAT 3 PLC Runtime 默认端口 |\n"
        "| `AMSPORT_R0_PLC_RTS1` | 801 | TwinCAT 2 PLC Runtime 1（兼容） |\n"
        "| `AMSPORT_R0_NC` | 500 | NC Server |\n"
        "| `AMSPORT_LOGGER` | 100 | 日志服务器 |\n"
        "| `ADSSTATE_RUN` | 5 | ADS 对象运行中 |\n"
        "| `ADSSTATE_STOP` | 6 | ADS 对象停止 |\n"
        "| `ADSSTATE_CONFIG` | 15 | TwinCAT 配置模式 |\n"
        "| `DEFAULT_ADS_TIMEOUT` | T#5S | 默认 ADS 调用超时 |\n"
        "| `FOPEN_MODEREAD` | 1 | 只读 |\n"
        "| `FOPEN_MODEWRITE` | 2 | 只写 |\n"
        "| `FOPEN_MODEAPPEND` | 4 | 追加 |\n"
        "| `FOPEN_MODEPLUS` | 16 | 读写 |\n"
        "| `FOPEN_MODEBINARY` | 32 | 二进制模式 |\n"
        "| `FOPEN_MODETEXT` | 64 | 文本模式 |\n"
    ),
    scenario="MAIN 中调用 ADSREAD 时用 `nPort := AMSPORT_R0_PLC_TC3` 而不是硬编码 851；新人接手代码也能立刻明白这是 TC3 的 PLC 端口。",
    value="替代魔法数字；可读性大幅提升。",
    alt=("- 自定义常量：可行但重复造轮子。\n- 硬编码：可维护性最差。"),
    xml_scen="演示直接引用 Constants 中的几个常用符号，把它们写到本地变量便于 HMI 监控显示。",
    xml_val="替代硬编码 851 / 5 / T#5S 等魔法数字。",
    xml_verify="观察 nPlcPort = 851，eRunningState = 5（ADSSTATE_RUN），tDefaultTimeout = T#5S。",
    xml_vars=[
        ("nPlcPort", "UINT", None, "本机 TC3 PLC 端口号"),
        ("eRunningState", "UINT", None, "ADS Running 状态码"),
        ("tDefaultTimeout", "TIME", None, "默认 ADS 超时"),
        ("nFileTextAppendMode", "DWORD", None, "文本追加打开模式位掩码"),
    ],
    xml_call=(
        "// 直接引用 Tc2_System.Constants 里的全局常量\n"
        "nPlcPort            := AMSPORT_R0_PLC_TC3;\n"
        "eRunningState       := ADSSTATE_RUN;\n"
        "tDefaultTimeout     := DEFAULT_ADS_TIMEOUT;\n"
        "nFileTextAppendMode := FOPEN_MODEAPPEND OR FOPEN_MODETEXT;\n"
    ),
    related=["stLibVersion_Tc2_System", "FB_FileOpen", "F_CmpLibVersion"],
)


# =================== Library version (1) ===================

_add(
    "stLibVersion_Tc2_System",
    ftype="VAR_GLOBAL CONSTANT",
    syntax_decl=(
        "VAR_GLOBAL CONSTANT\n"
        "    stLibVersion_Tc2_System : ST_LibVersion;\n"
        "END_VAR"
    ),
    summary=(
        "`stLibVersion_Tc2_System` 是 Tc2_System 库的版本全局常量（`ST_LibVersion` 类型）。"
        "每个 Beckhoff PLC 库都按统一命名规则提供同名常量 `stLibVersion_<library>`。"
        "结合 `F_CmpLibVersion` 函数可在启动期做库版本守门，避免依赖错版本的库导致接口不兼容。"
    ),
    behavior=(
        "**类型结构 `ST_LibVersion`**：包含 4 个字段——\n\n"
        "- `iMajor : UINT` 主版本号\n"
        "- `iMinor : UINT` 次版本号\n"
        "- `iBuild : UINT` 构建号\n"
        "- `iRevision : UINT` 修订号\n\n"
        "另外还有 `sVersion : STRING` 字符串形式版本和 `sLibName : STRING` 库名等字段（具体见 `ST_LibVersion` topic）。\n\n"
        "**编译期常量**：由 Beckhoff 在发布库时写死；引用本库后该常量自动可用，无需自己赋值。\n\n"
        "**使用模式**：\n\n"
        "1. **直读字段**：`nMyMajor := stLibVersion_Tc2_System.iMajor;`\n"
        "2. **比对版本**：`nCmp := F_CmpLibVersion(stLibVersion_Tc2_System, 3, 3, 8, 0); IF nCmp < 0 THEN ... END_IF;`\n"
        "3. **HMI 显示**：直接读 `sVersion` 字符串字段。\n\n"
        "**统一规则**：所有 Beckhoff 库都遵循 `stLibVersion_<libname>` 命名，跨库守门只需把库名换掉。"
    ),
    pitfalls=[
        ("**不要写 `stLibVersion_Tc2_System := ...`**：常量赋值编译报错。", True),
        ("**字段名 `iMajor` 而不是 `nMajor`**：早期版本可能不同；以 PDF 当前版本为准。", True),
        ("**库未引用时编译错误**：常量编译期就需要存在，库未加进项目会直接编译失败。", True),
        ("**与运行时实际加载的库版本**：通常一致，但热更新场景下可能不同步；正常工程不会遇到。", True),
    ],
    var_desc={},
    return_kind="NONE",
    return_text="本节是 `VAR_GLOBAL CONSTANT`，无返回值。访问方式：直接 `stLibVersion_Tc2_System.iMajor` 等。\n",
    scenario="集成商交付前的版本守门：MAIN 启动时读 `stLibVersion_Tc2_System.iMajor / iMinor / iBuild / iRevision` 写入诊断日志，便于事后追溯；同时用 `F_CmpLibVersion` 拒绝低版本启动。",
    value="替代 `F_GetVersionTcSystem` 的多次调用；一次拿到完整结构。",
    alt=(
        "- `F_GetVersionTcSystem`：废弃，多次调用且只能拿 3 个字段。\n"
        "- 手工记录在文档：易过期、不可信。"
    ),
    xml_scen="启动时把 Tc2_System 版本各字段抓出来写到本地诊断变量，HMI 显示『库版本：x.y.z.r』。",
    xml_val="替代 F_GetVersionTcSystem 多次调用，一次拿全。",
    xml_verify="观察 nLibMajor / nLibMinor / nLibBuild / nLibRevision 与库发布版本一致（v1.17.3 对应字段）。",
    xml_vars=[
        ("nLibMajor", "UINT", None, "库主版本号"),
        ("nLibMinor", "UINT", None, "库次版本号"),
        ("nLibBuild", "UINT", None, "库构建号"),
        ("nLibRevision", "UINT", None, "库修订号"),
    ],
    xml_call=(
        "// 启动期一次性抓取库版本各字段；这些是编译期常量，每周期读开销可忽略\n"
        "nLibMajor    := stLibVersion_Tc2_System.iMajor;\n"
        "nLibMinor    := stLibVersion_Tc2_System.iMinor;\n"
        "nLibBuild    := stLibVersion_Tc2_System.iBuild;\n"
        "nLibRevision := stLibVersion_Tc2_System.iRevision;\n"
    ),
    related=["F_CmpLibVersion", "F_GetVersionTcSystem", "Constants"],
)
