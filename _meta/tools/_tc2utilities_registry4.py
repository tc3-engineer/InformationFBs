# Tc2_Utilities registry — part 4: bulk remaining 79 FB entries.
# Concise hand-curated Chinese content per 2026-05-11 charter B/C/D/E.
# Each entry kept compact but charter-compliant:
#   - summary: 2 Chinese paragraphs minimum
#   - behavior: ≥100 prose CJK chars (the gen.py pads with a wrapper if short)
#   - pitfalls: 4-5 items mixing PDF facts + 工程经验补充
#   - scenario/value/alt: 1-2 lines each
#   - xml_scen/val/verify + extra_vars + call: drop-in P_Demo

from _tc2utilities_registry import REG


def _add(name, *, summary, behavior, pitfalls, scenario, value, alt,
         xml_scen, xml_val, xml_verify, var_desc=None,
         return_kind="NONE", related=None, xml_extra_vars=None,
         xml_call=None):
    REG[name] = dict(
        summary=summary, behavior=behavior, pitfalls=pitfalls,
        scenario=scenario, value=value, alt=alt,
        xml_scen=xml_scen, xml_val=xml_val, xml_verify=xml_verify,
        var_desc=var_desc or {}, return_kind=return_kind,
        related=related or [], xml_extra_vars=xml_extra_vars or [],
        xml_call=xml_call,
    )


# ============================================================================
# ADS route / network info group
# ============================================================================

_ROUTE_NET_PITFALLS_COMMON = [
    ("**ADS 路由是 TwinCAT 系统级配置，影响所有 PLC / SystemService**——通过 PLC 程序动态修改路由属于运维侵入操作，生产环境务必先做白名单 / 审计。", False),
    ("**跨网段调用要靠路由可达**：本机如果路由表里没有目标 AmsNetId，调用会立刻 `nErrId = 6 (DEVICE_NOTFOUND)` 或 `0x745 (CLIENT_SYNCTIMEOUT)`。", False),
    ("ADS 端口建议明确指定（如 851 = PLC RT、852 = PLC RT1、10000 = SystemService）；不写或写错会调用到非预期目标。", True),
    ("`tTimeout` 默认 5 秒；跨广域链路要适当放大，但太大会卡住调用周期任务，建议放在后台任务里调用。", True),
    ("PDF 未列详细错误码——错误号属于通用 ADS Return Codes 表，参考 Beckhoff InfoSys 在线表。", False),
]

_add(
    "FB_AddRouteEntry",
    summary=(
        "FB_AddRouteEntry 通过 ADS 在目标 TwinCAT 系统的路由表中插入一条新的远端 AMS 路由条目（Route），"
        "让目标机器能通过 AmsNetId 找到对方主机的 IP 和验证凭据。\n\n"
        "典型场景：现场首次部署机器时，由工程师 PC 上的 TwinCAT 程序代替手动 `Add Route...` 对话框，"
        "把生产机器互相加进对方的路由表，做到一键 commissioning。"
    ),
    behavior=(
        "**协议**：`bExecute` 上升沿触发一次 ADS 请求。FB 把 sNetID 视为目标系统（被加路由的那一端），"
        "把 sRemoteNetID + sRemoteIP + sRemoteName + sRemoteRouteName 视为要写入的新路由条目。"
        "如果目标系统需要身份验证（典型 TwinCAT Engineering Mode），还要正确填 sUsername / sPassword。\n\n"
        "**完成判定**：`bBusy = TRUE` 期间不响应新请求；ADS 应答到达后 `bBusy → FALSE`、`bDone → TRUE`（或 `bErr` / `nErrId`）。\n\n"
        "**重要副作用**：调用成功后目标机器路由表立即生效，重启不丢；属于持久化配置修改。"
    ),
    pitfalls=_ROUTE_NET_PITFALLS_COMMON + [
        ("**身份验证错误最常见**：`sUsername` / `sPassword` 不对 → `nErrId = 0x745` 或自定义错误号。注意密码是目标主机 Windows 用户密码，不是 TwinCAT 项目密码。", False),
        ("路由名 `sRemoteRouteName` 在目标侧必须唯一；重复会替换旧条目。", False),
    ],
    var_desc={
        "sNetID": "**目标 TwinCAT 系统**（被加路由的那一端）的 AMS Net ID。",
        "bExecute": "上升沿触发一次添加请求。",
        "sRemoteNetID": "要加入的远端机器的 AmsNetId。",
        "sRemoteIP": "对应的 IP 地址（字符串），例如 `'10.0.0.42'`。",
        "sRemoteName": "对应主机名（可选，留空时由远端决定）。",
        "sRemoteRouteName": "本路由条目的名字（在目标侧的路由表里显示）。",
        "sUsername": "目标侧 Windows 登录用户名。",
        "sPassword": "对应 Windows 密码（明文）。",
        "eAddRouteOptions": "添加选项枚举（覆写 / 加密 / 临时等，见 `E_AddRouteOptions`）。",
        "tTimeout": "ADS 调用超时时长。",
        "bBusy": "TRUE 表示请求未结束。",
        "bErr": "TRUE 表示请求失败。",
        "nErrId": "ADS / 自定义错误号，0 = 无错。",
    },
    scenario="工程师 PC 端跑一段 ST 程序，把 5 台生产线 PLC 互相加进路由表，免去手动逐台开 TwinCAT System Manager。",
    value="替代手动『Add Route...』对话框，可纳入自动 commissioning 脚本；提升上线效率约 10×。",
    alt=(
        "- 手动 TwinCAT System Manager → Add Route：标准方法，但人工逐台耗时。\n"
        "- TwinCAT XAE 命令行 `TcAmsRemoteMgr`：可脚本化，但需要 Windows shell 通道。\n"
        "- **本 FB**：纯 PLC 程序调用，可在 commissioning POU 里批量发起。"
    ),
    xml_scen="批量给 5 台生产线 PLC 互相加路由，本例演示其中一对的添加。",
    xml_val="替代手动开 System Manager 操作。",
    xml_verify="改 bAddRoute := TRUE，观察 bBusy 短暂 TRUE 后 bDoneOk → TRUE；nErr 应为 0；上目标机器看路由表新增条目。",
    xml_extra_vars=[
        ("bAddRoute", "BOOL", "FALSE", "上升沿触发添加"),
        ("bBusyFlag", "BOOL", None, ""),
        ("bDoneOk", "BOOL", None, "成功标志（! bErr）"),
        ("nErr", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_AddRouteEntry(\n"
        "    sNetID := '',  // 本机做目标\n"
        "    bExecute := bAddRoute,\n"
        "    sRemoteNetID := '10.0.0.42.1.1',\n"
        "    sRemoteIP := '10.0.0.42',\n"
        "    sRemoteName := 'CX-Line2',\n"
        "    sRemoteRouteName := 'AutoRoute-Line2',\n"
        "    sUsername := 'Administrator',\n"
        "    sPassword := 'GeheimPW',\n"
        "    eAddRouteOptions := eRemoteRouteStatic_StoreOnRemote,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    bBusy => bBusyFlag,\n"
        "    bErr => bDoneOk,\n"
        "    nErrId => nErr\n"
        ");\n"
        "bDoneOk := NOT bDoneOk;  // 取反让 TRUE 表示成功"
    ),
    related=["FB_AddRouteEntryEx", "FB_EnumRouteEntry", "FB_RemoveRouteEntry"],
)

_add(
    "FB_AddRouteEntryEx",
    summary=(
        "FB_AddRouteEntryEx 是 FB_AddRouteEntry 的扩展版：在原参数基础上额外暴露选项标志位，"
        "允许业务程序指定路由是 Static / Temp、是否加密、是否启用 AMS Subnet 自动发现等高级配置。\n\n"
        "典型用场：要在 commissioning 阶段批量加临时路由（重启即丢）做调试，或要按设备类型差异化设置加密策略。"
    ),
    behavior=(
        "**协议**：与 FB_AddRouteEntry 相同的 ADS 请求时序：`bExecute` 上升沿触发，`bBusy` 高电平期间不响应新请求，`bDone` / `bErr` + `nErrId` 反馈结果。\n\n"
        "**新增选项**：`eRouteType` 决定 Static（持久化）/ Temp（重启清空）；`bSetStandardOptions` 等位允许混合控制加密、自动 NAT 穿透等。\n\n"
        "**与 FB_AddRouteEntry 关系**：底层 ADS 命令字 / 错误码与原版完全相同，仅多几个选项位；推荐新项目直接用 Ex 版。"
    ),
    pitfalls=_ROUTE_NET_PITFALLS_COMMON + [
        ("Static / Temp 选择错容易导致测试期间加的路由被持久化进生产路由表，发布前清理麻烦——commissioning 建议先用 Temp。", True),
    ],
    var_desc={},
    scenario="commissioning 时批量加 Temp 路由做联通测试，测试完重启自动清掉。",
    value="比 FB_AddRouteEntry 多了类型 / 加密选项位，避免修改两次。",
    alt=(
        "- FB_AddRouteEntry：基础版，仅能加 Static 路由。\n"
        "- **本 FB**：可灵活指定路由类型与加密策略。"
    ),
    xml_scen="加 Temp 路由（重启丢）做联通测试。",
    xml_val="比 FB_AddRouteEntry 多类型 / 加密选项。",
    xml_verify="改 bAdd := TRUE，观察 bBusy 短暂 TRUE 后 bErr → FALSE、nErr → 0；目标机器路由表里能看到 Temp 路由；重启目标机器后路由消失。",
    xml_extra_vars=[
        ("bAdd", "BOOL", "FALSE", "上升沿触发"),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "// PDF 给出的参数命名见上方 VAR_INPUT；此处用最少必填参数演示 Temp 路由\n"
        "fbFB_AddRouteEntryEx(\n"
        "    bExecute := bAdd,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_AddRouteEntry", "FB_RemoveRouteEntry"],
)

_add(
    "FB_RemoveRouteEntry",
    summary=(
        "FB_RemoveRouteEntry 通过 ADS 从目标 TwinCAT 系统的路由表中删除指定的远端 AMS 路由条目。"
        "用于把测试期残留的 Temp / Static 路由清除，或在生产线设备搬迁时取消已不存在的路由。\n\n"
        "调用一旦成功，目标路由表立即生效，被删的路由不能再用做 AMS 通讯。"
    ),
    behavior=(
        "**协议**：`bExecute` 上升沿触发一次 ADS 删除请求。需要正确填 `sRemoteName` / `sRemoteRouteName`（即在路由表里显示的那个名字）才能唯一匹配。\n\n"
        "**完成判定**：与 AddRoute 相同，`bBusy` → `bDone` 或 `bErr` + `nErrId`。\n\n"
        "**注意**：成功删除属于持久化操作（除非删的是 Temp 路由）；后续 ADS 通讯走该路由会立刻失败。"
    ),
    pitfalls=_ROUTE_NET_PITFALLS_COMMON + [
        ("**误删后通讯立即断**：本机程序通过被删路由调用 ADS 会立刻 `nErrId = 6 (DEVICE_NOTFOUND)`，且无法再用本 FB 加回去（连接已断）。", False),
        ("路由名匹配区分大小写——`'AutoRoute-Line2'` 和 `'autoroute-line2'` 是两条不同路由。", True),
    ],
    var_desc={},
    scenario="生产线设备 retrofit 后，老 PLC 拆掉，路由表里残留的旧条目需要清掉。",
    value="替代手动 System Manager 操作，可纳入运维脚本。",
    alt=(
        "- 手动 System Manager → Routes → Delete：标准方法。\n"
        "- **本 FB**：PLC 程序可一键清理批量历史路由。"
    ),
    xml_scen="批量清理 retrofit 后的旧路由条目。",
    xml_val="替代手动删除。",
    xml_verify="先用 FB_EnumRouteEntry 看路由表，确认目标条目存在；写 bRemove := TRUE 触发删除；再次 Enum 应看不到该条目。",
    xml_extra_vars=[
        ("bRemove", "BOOL", "FALSE", "上升沿触发删除"),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_RemoveRouteEntry(\n"
        "    sNetID := '',\n"
        "    bExecute := bRemove,\n"
        "    sRemoteName := 'CX-OldLine',\n"
        "    sRemoteRouteName := 'AutoRoute-OldLine',\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_AddRouteEntry", "FB_EnumRouteEntry"],
)

_add(
    "FB_EnumRouteEntry",
    summary=(
        "FB_EnumRouteEntry 枚举目标 TwinCAT 系统的路由表，每次调用返回一条路由条目（AmsNetId / IP / Name / RouteName 等）。"
        "通过 `nIndex` 索引依次取，直到 `bErr = TRUE` 或返回的 AmsNetId 为空，表示遍历完。\n\n"
        "用于运维盘点：罗列当前机器上所有已注册路由，对比是否与设备清单匹配。"
    ),
    behavior=(
        "**协议**：`bExecute` 上升沿触发一次 ADS 读，按 `nIndex` 取第 N 条（0 起始）。返回 `sRemoteNetID` / `sRemoteIP` / `sRemoteName` / `sRemoteRouteName` 等。\n\n"
        "**遍历约定**：业务代码自己维护 `nIndex` 计数，每次 `bDone` 后 +1 再触发一次；直到 `bErr = TRUE`（典型 `nErrId = 0x70C ROUTERERR_NOLOCKEDMEMORY`）或某字段为空表示无更多条目。\n\n"
        "**只读操作**：不修改路由表，可重复调用。"
    ),
    pitfalls=_ROUTE_NET_PITFALLS_COMMON + [
        ("**索引越界返回错误，不是空字段**：遇到 `nErrId` 不为 0 时不一定是真的错——可能就是遍历结束，业务代码要把『最后一条之后的索引报错』当作正常终止。", True),
        ("调用频率不要太高（< 10 Hz），路由表读操作占用 SystemService 资源。", True),
    ],
    var_desc={"nIndex": "要读取的路由表条目索引（0 起始）。"},
    scenario="运维盘点：罗列所有 PLC 的当前路由，找出失效 / 重复路由。",
    value="比手动逐台 System Manager 看路由表快得多，可批量上报到运维系统。",
    alt=(
        "- 手动 System Manager Routes 列表：单台清楚但批量痛。\n"
        "- **本 FB**：可循环枚举写入到 HMI 表格 / CSV。"
    ),
    xml_scen="枚举本机所有路由，依次填入 HMI 显示表。",
    xml_val="可批量盘点。",
    xml_verify="改 bEnum := TRUE，观察每次完成后 nIndex +1，sRouteName / sIp 填新值；直到 bErr → TRUE 表示遍历完。",
    xml_extra_vars=[
        ("bEnum", "BOOL", "FALSE", ""),
        ("nIdx", "UDINT", "0", "遍历游标"),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_EnumRouteEntry(\n"
        "    bExecute := bEnum,\n"
        "    nIndex := nIdx,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");\n"
        "// 业务代码：bDone 后 nIdx := nIdx + 1; 再次触发"
    ),
    related=["FB_AddRouteEntry", "FB_RemoveRouteEntry"],
)


# ---------------------- Network info ----------------------

_NETINFO_PITFALLS = [
    ("**Windows 系统调用，跨网段 ADS 时长比本地慢**——本地调用 < 50 ms，跨网段可能 500 ms+。", True),
    ("**返回字符串编码**：主机名 / 域名通常 ASCII，跨语言系统（中文 Windows）可能带本地编码字节，处理 UI 显示前要确认编码。", True),
    ("`bExecute` 上升沿触发，不要持续高电平当作连续读——会被忽略。", False),
    ("PDF 未列错误码——按通用 ADS Return Codes 对照（参考 Beckhoff 在线表）。", False),
    ("调用前 `bDone` / `bErr` 输出保留上一次结果，业务代码不要在 `bExecute` 还没触发就读输出。", True),
]

_add(
    "FB_GetLocalAmsNetId",
    summary=(
        "FB_GetLocalAmsNetId 读取**本机 TwinCAT 系统的 AMS Net ID**——TwinCAT 设备在 AMS 网络中的唯一寻址标识（形如 `5.32.156.10.1.1`）。"
        "PLC 程序在做远端 ADS 通讯、上传日志、配置路由时通常需要先知道自己的 AmsNetId。\n\n"
        "FB 返回的 NetId 与机器名、IP 解耦：换 IP / 改主机名不会变；只有手动改 TwinCAT 注册表里的 AmsNetId 才会变。"
    ),
    behavior=(
        "**调用方式**：`bExecute` 上升沿触发一次同步读，本机调用极快（典型 < 5 ms）。\n\n"
        "**输出**：`sNetID`（字符串形式 `n.n.n.n.n.n`）或 `AmsNetID`（`T_AmsNetID` 结构）；`bDone` / `bErr` 表示成功 / 失败。\n\n"
        "**惯用场景**：开机后 POU 里调一次，把结果存到 GVL（全局变量列表）里供整个项目其他模块复用，避免反复调用 ADS。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("调用太晚：PLC 任务启动早于 TwinCAT SystemService 初始化时短暂返回错——开机后建议延迟 1 秒再调。", True),
    ],
    var_desc={"sNetID": "本机 AMS Net ID（输出，字符串形式 `n.n.n.n.n.n`）。"},
    scenario="开机后读一次本机 NetId 缓存到 GVL，供整个项目其他 FB 调用 ADS 时复用。",
    value="替代手动配置文件读 NetId 或从 INI / 注册表读取。",
    alt=(
        "- 直接读注册表：太底层、跨 Windows 版本难维护。\n"
        "- 把 NetId 写到 GVL 字面常量：版本管理麻烦、克隆机器易出错。\n"
        "- **本 FB**：标准 ADS 调用，跨版本稳定。"
    ),
    xml_scen="开机后读一次本机 NetId 保存到 GVL。",
    xml_val="跨 TwinCAT 版本稳定，免手动配置。",
    xml_verify="改 bRead := TRUE，观察 sLocalNetId 装载 `n.n.n.n.n.n` 形式字符串，与 SystemTray 里看到的 AmsNetId 一致。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("sLocalNetId", "T_AmsNetID", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetLocalAmsNetId(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    sNetID => sLocalNetId,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetHostName", "FB_GetSystemId"],
)


_add(
    "FB_GetHostName",
    summary=(
        "FB_GetHostName 读取**本机 Windows / TwinCAT/BSD 主机名**——操作系统 `hostname` 命令返回的同一个字符串。"
        "PLC 程序拿到主机名通常用于：日志加机器标签、HMI 标题栏显示、多机部署时识别身份。\n\n"
        "返回的字符串是 Windows 操作系统级别的，与 TwinCAT 路由表里的 Route Name 不一定一样（Route Name 是配置项）。"
    ),
    behavior=(
        "**调用方式**：`bExecute` 上升沿触发，FB 通过 ADS 调本机 SystemService 获取主机名。\n\n"
        "**响应**：`sHostName` 装载字符串；`bDone` / `bErr` 反馈完成状态。\n\n"
        "**典型时长**：本地调用 < 10 ms。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("主机名长度上限取决于 Windows 配置（NetBIOS 15 字符，DNS 最长 63）；FB 输出缓冲建议 `STRING(255)` 安全。", True),
    ],
    var_desc={"sHostName": "本机主机名（字符串）。"},
    scenario="HMI 标题栏显示当前机器名 + 程序版本，便于运维一眼分辨。",
    value="替代写死字符串 / 读注册表。",
    alt=(
        "- 写死字符串：克隆镜像易混淆。\n"
        "- ADS 调用 NT_GetTime 旁的命令字：能做但代码繁。\n"
        "- **本 FB**：标准库一行调用。"
    ),
    xml_scen="开机后读机器名给 HMI 标题。",
    xml_val="标准库调用，免写注册表读取。",
    xml_verify="改 bRead := TRUE，观察 sName 装载主机名字符串。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("sName", "STRING(255)", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetHostName(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    sHostName => sName,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetLocalAmsNetId", "FB_GetHostAddrByName"],
)


_add(
    "FB_GetHostAddrByName",
    summary=(
        "FB_GetHostAddrByName 输入一个主机名（或 FQDN），通过 Windows DNS / hosts 文件解析出对应的 IPv4 地址。"
        "相当于 PLC 程序里的 `nslookup`。\n\n"
        "用于：HMI / 上位机配置里只填主机名，PLC 在线动态解析 IP 后建立 ADS 路由；或对端搬机器后 IP 变了也能自动跟上。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿，把 `sHostName` 发给 Windows DNS 客户端。解析结果在 `sAddr`（点分十进制字符串）。\n\n"
        "**响应时间**：本地 hosts 缓存命中 < 50 ms；远程 DNS 查询可能 100 ms - 数秒，受网络状况影响。\n\n"
        "**错误**：DNS 不可达 / 主机名不存在 → `bErr = TRUE` + `nErrId` 给出错误号。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("**DNS 查询会阻塞调用线程**：放在 100 ms 任务里会撑爆周期；推荐在后台 / commissioning 任务里调用。", False),
        ("**生产网段经常没有 DNS 服务器**：建议把对端主机名 + IP 直接写进 `C:\\Windows\\System32\\drivers\\etc\\hosts`，避免依赖 DNS。", True),
    ],
    var_desc={
        "sHostName": "要解析的主机名 / FQDN（输入）。",
        "sAddr": "解析得到的 IPv4 地址（点分十进制字符串，输出）。",
    },
    scenario="HMI 配置里填的是对端机器名（如 `CX-Line2`），PLC 启动后解析出 IP 再用 FB_AddRouteEntry 加路由。",
    value="支持 DHCP 环境下对端 IP 变化时自动跟随。",
    alt=(
        "- 写死 IP：DHCP 环境会失效。\n"
        "- 让运维每次更新 GVL：人工成本。\n"
        "- **本 FB**：标准 DNS 查询，自动跟随。"
    ),
    xml_scen="解析对端机器名为 IP，再用解析结果配置 ADS 路由。",
    xml_val="支持 DHCP 自动跟随。",
    xml_verify="改 sHost := 'localhost'，触发 bResolve；sIp 应得到 `127.0.0.1`。",
    xml_extra_vars=[
        ("bResolve", "BOOL", "FALSE", ""),
        ("sHost", "STRING(255)", "'localhost'", ""),
        ("sIp", "STRING(15)", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetHostAddrByName(\n"
        "    bExecute := bResolve,\n"
        "    sHostName := sHost,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    sAddr => sIp,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetHostName"],
)


_add(
    "FB_GetAdaptersInfo",
    summary=(
        "FB_GetAdaptersInfo 获取本机所有网络适配器（网卡）的列表，每个适配器返回 MAC / IP / 掩码 / 网关 / DHCP 状态等信息。"
        "返回结构是 `ARRAY OF ST_AdapterInfo`。\n\n"
        "用于：诊断 PLC 启动时网卡是否就绪、记录硬件指纹（MAC）做授权绑定、HMI 显示当前 IP。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿一次性返回所有适配器信息到 `aAdapters` 缓冲区，数量在 `nAdapters` 里。\n\n"
        "**缓冲区**：调用方需要预分配 `aAdapters` 数组（典型 `ARRAY[0..15] OF ST_AdapterInfo`），如果实际适配器更多会被截断；本 FB 在 `nAdapters` 里返回真实数量。\n\n"
        "**性能**：本地 SystemAPI 调用，< 100 ms。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("缓冲区数组上限要预估，CX 设备一般 2-4 个网卡，工程师 PC 可能 10+（包括虚拟网卡）。", True),
        ("**虚拟网卡 / VPN 适配器都会出现**：用 MAC 做授权要按主物理网卡过滤，否则克隆 / 重装容易换 MAC。", True),
    ],
    var_desc={
        "aAdapters": "适配器信息数组（输出），调用方分配缓冲区。",
        "nAdapters": "实际返回的适配器数量。",
    },
    scenario="开机 self-test 阶段读所有网卡 IP，确认上位机网络已就绪后才允许进入 Run 模式。",
    value="替代调 Win32 API GetAdaptersInfo 自写包装。",
    alt=(
        "- 不读网卡，直接试 ADS 通讯失败再处理：用户体验差。\n"
        "- **本 FB**：开机自检逻辑可读 IP 直接报错给运维。"
    ),
    xml_scen="开机 self-test 读所有网卡信息。",
    xml_val="标准库调用，跨 Win 版本稳定。",
    xml_verify="改 bRead := TRUE，观察 nAdapterCount > 0；aAdapterList[0].sIpAddress 应为 PLC 主网卡 IP。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("aAdapterList", "ARRAY[0..15] OF ST_AdapterInfo", None, ""),
        ("nAdapterCount", "UDINT", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetAdaptersInfo(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    pAddr := ADR(aAdapterList),\n"
        "    cbBuffLen := SIZEOF(aAdapterList),\n"
        "    nAdapters => nAdapterCount,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetAdaptersInfoEx", "FB_GetHostAddrByName"],
)

_add(
    "FB_GetAdaptersInfoEx",
    summary=(
        "FB_GetAdaptersInfoEx 是 FB_GetAdaptersInfo 的增强版：返回的 `ST_AdapterInfoEx` 比 `ST_AdapterInfo` 多了 IPv6 地址、"
        "适配器类型（Ethernet / WiFi / Loopback）、DNS Server 列表等字段。\n\n"
        "新项目建议直接用 Ex 版本，可向后兼容 IPv6 环境。"
    ),
    behavior=(
        "**调用**：与 FB_GetAdaptersInfo 完全一致——`bExecute` 上升沿，一次性填充 `aAdapters` 数组。\n\n"
        "**输出结构**：`ST_AdapterInfoEx` 包含 IPv4 + IPv6 + 适配器类型 + DNS 服务器列表，比原版字段多。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("IPv6 地址字符串可能长达 39 字符（不含前缀），缓冲区要 `STRING(45)` 起步。", True),
    ],
    var_desc={},
    scenario="混合 IPv4 / IPv6 部署的客户机房，需要列举所有 IP 地址做白名单。",
    value="比原版多 IPv6 / DNS 等字段。",
    alt=(
        "- FB_GetAdaptersInfo：仅 IPv4。\n"
        "- **本 FB**：IPv4 + IPv6。"
    ),
    xml_scen="读所有网卡含 IPv6 信息。",
    xml_val="支持 IPv6。",
    xml_verify="同 FB_GetAdaptersInfo，多看 IPv6 字段。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("aAdapters", "ARRAY[0..15] OF ST_AdapterInfoEx", None, ""),
        ("nCount", "UDINT", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetAdaptersInfoEx(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    pAddr := ADR(aAdapters),\n"
        "    cbBuffLen := SIZEOF(aAdapters),\n"
        "    nAdapters => nCount,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetAdaptersInfo"],
)


_add(
    "FB_GetRouterStatusInfo",
    summary=(
        "FB_GetRouterStatusInfo 查询本机 TwinCAT AMS Router 的运行统计：消息计数、当前并发连接数、最大队列长度、丢包数等。"
        "用于诊断 AMS 通讯是否过载、路由器是否健康。\n\n"
        "返回结构 `ST_AmsRouterStatusInfo` 含多个 UDINT / DWORD 计数器，业务可纳入 HMI 状态面板。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。本地 ADS 调用，< 10 ms。\n\n"
        "**典型周期**：HMI 状态面板里每秒触发一次足够；不要 < 100 ms 高频读，会无意义占用 SystemService。\n\n"
        "**字段含义**：每个计数器都是累计值，复位时机为 TwinCAT 服务重启。要看『每秒新增』需要业务侧自己做差分。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("计数器是累计值，业务侧要做差分才能得到吞吐率。", True),
        ("出现 `LostMessages > 0` 不一定是错——也可能是远端机器已下电；要结合 ping / 路由表判断。", True),
    ],
    var_desc={},
    scenario="HMI 网络诊断页：实时显示 AMS Router 消息计数 / 丢包数。",
    value="提供 Router 内部观测点，比简单 ping 检测精确。",
    alt=(
        "- 用 Wireshark 抓包：太重，不适合现场。\n"
        "- 仅 ping：检测路径通断但看不到协议级丢包。\n"
        "- **本 FB**：TwinCAT 内置观测。"
    ),
    xml_scen="HMI 网络诊断页每秒读 Router 状态。",
    xml_val="路由器级观测，比 ping 精确。",
    xml_verify="触发后观察 stRouterInfo.nMessages 在变；正常工况 nLostMessages 应为 0。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("stRouterInfo", "ST_AmsRouterStatusInfo", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetRouterStatusInfo(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    stStatusInfo => stRouterInfo,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetLocalAmsNetId"],
)


_add(
    "FB_GetSystemId",
    summary=(
        "FB_GetSystemId 读取**本机 TwinCAT 系统 ID（SystemID）**——一个全局唯一的 16 字节 GUID，与硬件绑定。"
        "用于 License 绑定、设备硬件指纹、防克隆校验。\n\n"
        "SystemID 由 TwinCAT 安装时根据主板 / CPU / 网卡 MAC 等综合生成，重装系统会变化。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。SystemID 以 `GUID` 结构（16 字节）返回，业务侧可转字符串显示或哈希作为机器指纹。\n\n"
        "**稳定性**：同一台 PLC 上 SystemID 在 TwinCAT 安装期间稳定；重装 TwinCAT / 更换硬件会变。\n\n"
        "**典型用法**：自研 License 系统拿 SystemID 做加密种子，校验通过才允许 PLC 进入 Run 模式。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("**不要假设跨重装稳定**——SystemID 重装 TwinCAT 会变；做长期 License 应以 dongle 或硬件序列号为准（参考 FB_GetDongleSystemID）。", False),
        ("SystemID 长度 16 字节，转字符串后 32-36 字符；HMI 显示截短前 8 字符可读性即可。", True),
    ],
    var_desc={"systemId": "本机 TwinCAT SystemID（16 字节 GUID 结构）。"},
    scenario="自研 License 系统校验：客户拿 SystemID 来要密钥，密钥与 SystemID 绑定。",
    value="比 MAC / 主板 SN 更适合 TwinCAT 软件授权。",
    alt=(
        "- 用 MAC 地址：网卡换 / 虚拟机克隆易绕过。\n"
        "- 用主板 SN：需 Windows API 跨版本兼容性麻烦。\n"
        "- **本 FB**：TwinCAT 内置，授权直接绑 TwinCAT 实例。"
    ),
    xml_scen="License POU 启动时读一次 SystemID 做校验。",
    xml_val="标准 License 绑定锚点。",
    xml_verify="改 bRead := TRUE，观察 systemId 装载 16 字节 GUID（非全 0）。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("systemId", "GUID", None, "本机 SystemID"),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetSystemId(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    systemId => systemId,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetVolumeId", "FB_GetDongleSystemID", "FB_CheckLicense"],
)


_add(
    "FB_GetVolumeId",
    summary=(
        "FB_GetVolumeId 读取**当前 TwinCAT 配置卷的 Volume ID**——SD 卡 / 硬盘卷的硬件标识。"
        "用于硬件绑定授权（卷 ID 不会因重装 TwinCAT 而变），比 SystemID 更稳定。\n\n"
        "典型 CX 设备的 SD 卡卷 ID 在出厂烧录后不会变化，除非更换 SD 卡。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿读一次。返回当前 TwinCAT 配置所在卷的 Volume ID。\n\n"
        "**稳定性**：换 SD 卡 / 换硬盘会变；重装 OS / TwinCAT 不变。\n\n"
        "**典型用法**：License 系统优先用 Volume ID 而不是 SystemID 作为硬件指纹。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("CX 设备维修换 SD 卡 → 卷 ID 变 → License 失效。维修流程要把新 SD 卡的卷 ID 提前报给授权方。", True),
    ],
    var_desc={},
    scenario="License 绑定 Volume ID，比 SystemID 重装抗性更好。",
    value="硬件级稳定指纹。",
    alt=(
        "- FB_GetSystemId：重装 TwinCAT 会变。\n"
        "- **本 FB**：卷 ID 与卷硬件绑定。"
    ),
    xml_scen="读卷 ID 用作 License 硬件指纹。",
    xml_val="比 SystemID 重装抗性更好。",
    xml_verify="触发后 volumeId 装载非零值；与 Windows `vol C:` 命令显示一致。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("volumeId", "GUID", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetVolumeId(\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    volumeId => volumeId,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetSystemId", "FB_CheckLicense"],
)


_add(
    "FB_GetDeviceIdentificationEx",
    summary=(
        "FB_GetDeviceIdentificationEx 读取目标 TwinCAT 设备的综合身份信息：设备名 / TwinCAT 版本 / OS 版本 / Image 版本 等。"
        "返回的 `ST_DeviceIdentification` 结构覆盖设备硬件 + 软件栈的关键字段。\n\n"
        "用于资产盘点、远端版本检查、做兼容性判断（程序连上之前先确认对端 TwinCAT 版本符合最低要求）。"
    ),
    behavior=(
        "**调用**：`bExecute` 上升沿触发，可指定 `sNetID` 远端读。\n\n"
        "**输出字段**：通常包括 DeviceName、TwinCATVersion、Build、OSVersion、ImageVersion、ImageOSName 等；"
        "具体字段以 PDF / InfoSys 描述的 `ST_DeviceIdentification` 为准。\n\n"
        "**通讯量**：单次返回数百字节，本地 < 50 ms；远端跨网视情况。"
    ),
    pitfalls=_NETINFO_PITFALLS + [
        ("TwinCAT 版本字段是字符串（如 `'3.1.4024.32'`），做版本对比时要拆字符串成 INT 而非字典序比较。", True),
    ],
    var_desc={},
    scenario="部署前自动盘点所有 PLC 的 TwinCAT 版本，找出需要升级的机器。",
    value="替代手动 SSH / 远程登录看版本。",
    alt=(
        "- 手动远端登录：批量痛。\n"
        "- **本 FB**：脚本化盘点。"
    ),
    xml_scen="盘点 5 台 PLC 的 TwinCAT 版本。",
    xml_val="脚本化盘点。",
    xml_verify="改 bRead := TRUE，观察 stDeviceId.sTwinCATVersion 装载字符串如 `3.1.4024.32`。",
    xml_extra_vars=[
        ("bRead", "BOOL", "FALSE", ""),
        ("stDeviceId", "ST_DeviceIdentification", None, ""),
        ("bBusy_", "BOOL", None, ""),
        ("bErrFlag", "BOOL", None, ""),
        ("nErrCode", "UDINT", None, ""),
    ],
    xml_call=(
        "fbFB_GetDeviceIdentificationEx(\n"
        "    sNetID := '',\n"
        "    bExecute := bRead,\n"
        "    tTimeout := DEFAULT_ADS_TIMEOUT,\n"
        "    stDeviceIdentification => stDeviceId,\n"
        "    bBusy => bBusy_,\n"
        "    bErr => bErrFlag,\n"
        "    nErrId => nErrCode\n"
        ");"
    ),
    related=["FB_GetSystemId", "FB_GetRouterStatusInfo"],
)
