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
        "FB_FileTell 返回已打开文件的当前指针位置（从文件头算起的字节偏移），输出到 `cbFilePos`。"
        "常与 `FB_FileSeek` 配合使用：先 Tell 保存位置 → 做完读 / 写 → Seek 回原位置。"
        "也用于估算文件大小（Seek 到末尾再 Tell）。"
    ),
    behavior=(
        "**调用方式**：周期调用，`bExecute` 上升沿触发一次查询。完成后 `cbFilePos` 给出当前指针字节偏移。\n\n"
        "**追加模式细节**：PDF 明确指出在 `FOPEN_MODEAPPEND` 模式下，`cbFilePos` 反映的是『最近一次 I/O 操作』后的位置，**不是**下次写入位置——下次写入永远在末尾。读操作后 Tell 反映读完位置；写操作后位置变化未必如直觉。\n\n"
        "**未做 I/O 时**：以 `a` / `a+` 打开且尚未读 / 写过，`cbFilePos = 0`（文件头），与 r/w/+ 模式一致。"
    ),
    pitfalls=[
        ("**追加模式下不是下次写位置**：在 `a` / `a+` 模式下 Tell 出来的位置只是最近一次 I/O 后的位置，**不是**下次写入位置（永远末尾）。要算文件大小用 Seek 到 SEEK_END 再 Tell。", False),
        ("**句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。", False),
        ("**>2 GB 限制**：`cbFilePos` 是 `UDINT`，理论 4 GB；但 Seek 是 `DINT` 限 2 GB，所以联合使用上限 2 GB。", True),
    ],
    var_desc={
        **_VD_FILE_ADS,
        "cbFilePos": "**输出**：当前文件指针字节偏移（从文件头起算）。追加模式下反映最近 I/O 后位置而非下次写位置。",
    },
    scenario="对一份大配方文件做断点续传读取：把 Tell 拿到的位置存到 retain，重启后 Seek 回原位置继续读。",
    value="封装 ADS 0x10007 命令；不用本 FB 要自己拼 ADS Read 命令。",
    alt=("- 手动维护一个本地 UDINT 跟踪每次读写后的偏移：能用但断电后会丢同步。"),
    xml_scen="读完一段后查询当前文件指针位置 cbCurrentPos 保存到 retain 变量，便于断电重启续读。",
    xml_val="替代手动跟踪偏移变量，直接从 OS 拿权威值。",
    xml_verify="在线置 bTellRequest := TRUE → 观察 cbCurrentPos 在 1-2 周期后非零；与刚读完的字节累计量一致。",
    xml_vars=[
        ("fbFileTell", "FB_FileTell", None, "FB_FileTell 实例"),
        ("hOpenedFile", "UINT", None, "已打开句柄"),
        ("bTellRequest", "BOOL", None, "在线写 TRUE 触发一次查询"),
        ("cbCurrentPos", "UDINT", None, "查询返回的当前指针偏移"),
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
        "    cbFilePos => cbCurrentPos\n"
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
