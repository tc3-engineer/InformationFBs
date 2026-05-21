# -*- coding: utf-8 -*-
"""Per-FB content registry for Tc2_IoFunctions (70 entries)."""

# Common ADS pitfalls reused across the General IO / Lightbus / CANopen / SERCOS FBs
ADS_PITFALLS = [
    ('ADS 错误号需要查 Beckhoff 在线 **ADS Return Codes** 表理解，本 FB 自身不附带具体码表。', False),
    ('触发输入（如 `bExecute` / `START` / `RESET` 等）必须给上升沿一次性触发，不能持续给 TRUE。持续高电平时只有第一次进入会启动一次新请求，之后不会重新触发。', True),
    ('不要在 `BUSY = TRUE` 期间修改其它输入参数，结果未定义。等 `BUSY` 落回 FALSE 后再准备下一次的入参。', True),
    ('现场总线设备未上电 / 未通讯时 `ERRID` 会带 `0x06` (port not found) 或硬件接口特有错误号，不一定是 ADS 通讯本身问题。', True),
]


# =========================
# Per-FB registry
# =========================
REG = {}


# ---------------- General IO FBs (13) ----------------

REG['IOF_DeviceReset'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '对指定 I/O 设备（例如现场总线卡 / 耦合器接口卡）执行在线复位，等价于在 TwinCAT System Manager 中右键 **I/O → Devices → Device xyz** 菜单选择 *Reset Device*。'
        '复位会让设备重新走完上电握手、清掉先前积累的错误状态。`RESET` 上升沿触发一次，FB 通过 `BUSY` / `ERR` / `ERRID` 反映异步结果。'
    ),
    behavior=(
        '`RESET` 上升沿触发一次复位命令：`BUSY := TRUE`，FB 把 reset 请求经 ADS 发到 `DEVICEID` 标识的 I/O 设备驱动。'
        '设备复位完成后 ADS 回复，`BUSY := FALSE`，若成功 `ERR := FALSE`、`ERRID := 0`；若失败 `ERR := TRUE`、`ERRID` 给出 ADS 错误号。'
        '命令超时由 `TMOUT` 控制（默认 5 秒），超时返回 `0x745` (ADSERR_CLIENT_SYNCTIMEOUT)。'
        '**触发语义**：必须上升沿；`RESET` 维持高电平不会重复发命令，需要再次复位时先回 FALSE 再回 TRUE。'
        '**典型用法**：现场总线偶发卡死 / 出现一长串硬件错误后调用一次让总线恢复；不要循环周期调用，复位本身会暂时打断 IO 通讯几十毫秒到几秒。'
    ),
    var_desc={
        'RESET': '上升沿触发一次设备复位命令；调用期间保持高电平，完成后由用户决定何时清零。',
    },
    pitfalls=ADS_PITFALLS + [
        ('**复位会短暂中断 IO 通讯**：调用瞬间该设备的过程映像数据会失效，依赖其输入的逻辑必须能容忍 1-3 秒空窗；不要在运动中的关键回路里复位。', True),
        ('**不要做自动循环复位**：若某设备频繁报错而触发循环复位，会掩盖真正的硬件故障并打乱诊断；应人工触发 + 报警。', False),
    ],
    scenario=(
        '印刷机老线现场总线（例如 Profibus FC310x 卡）偶发通讯抖动 → 触发 `IOF_DeviceReset` 让该总线主站重新初始化，比断电重启 PLC 整机轻量。'
        '也用于固件升级后由 PLC 程序触发一次复位让新固件生效，或把运维工单上的「在线复位 IO 卡」做成 HMI 按钮。'
    ),
    value='把 System Manager 里需要手点的 *Reset Device* 操作做成 PLC 程序里可触发的一次调用，方便从 HMI 按钮触发，也方便诊断故障树自动执行。',
    alt=(
        '- 手点 System Manager 菜单：能做但需要人值守 + 工程模式，不适合现场\n'
        '- 断电重启 PLC：能复位但代价大（所有 IO 同时停摆 + 程序重启）\n'
        '- 调 `ADSWRTCTL` 给驱动发 control code：底层做法，需要查 ADS 索引 group/offset，繁琐\n'
        '- **本 FB**：一行调用即得 System Manager 同等效果，是程序里复位 IO 设备的标准方式'
    ),
    related=['IOF_GetDeviceCount', 'IOF_GetDeviceIDByName', 'IOF_GetDeviceType'],
    xml_scen='Profibus 卡 FC3101 在长时间运行后偶发通讯故障，HMI 上按「复位 Profibus 主站」按钮触发本 FB，让总线重新走一遍上电流程。',
    xml_val='把 System Manager 的「在线复位」做成 PLC 接口，可被 HMI / SCADA 触发；不用工程模式登录工控机。',
    xml_verify='登录后把 nProfibusDeviceId 设为 System Manager 显示的 Device Id（例如 1），在线写 bResetProfibusReq := TRUE → bResetBusy 短暂置 TRUE → 几百毫秒后回 FALSE，期间 Profibus 端子的输入数据会闪一下；nLastResetErrId 非 0 查 ADS Return Codes。',
    xml_vars=[
        ('fbResetIoDevice', 'IOF_DeviceReset', None, 'I/O 设备复位 FB 实例'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机用空串；远端填 AMS Net ID'),
        ('nProfibusDeviceId', 'UDINT', '1', 'System Manager 中 Profibus 主站的 Device Id'),
        ('bResetProfibusReq', 'BOOL', 'FALSE', 'HMI 按钮：复位 Profibus 主站请求（上升沿触发）'),
        ('tResetCmdTimeout', 'TIME', 'T#5S', 'ADS 复位命令超时'),
        ('bResetBusy', 'BOOL', None, 'FB 工作中'),
        ('bResetErrorFlag', 'BOOL', None, '复位命令出错'),
        ('nLastResetErrId', 'UDINT', None, 'ADS 错误号'),
    ],
    xml_call=(
        '// 单次调用形式：bResetProfibusReq 上升沿触发；HMI 应在 bResetBusy 落回后复位 bResetProfibusReq\n'
        'fbResetIoDevice(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nProfibusDeviceId,\n'
        '    RESET    := bResetProfibusReq,\n'
        '    TMOUT    := tResetCmdTimeout,\n'
        '    BUSY     => bResetBusy,\n'
        '    ERR      => bResetErrorFlag,\n'
        '    ERRID    => nLastResetErrId\n'
        ');\n'
    ),
)


REG['IOF_GetBoxAddrByName'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '已知 box（slave / 模块 / 站）名字 + 所属设备的 DeviceId，查询该 box 的现场总线地址。'
        '对 Profibus 返回站地址，对 Beckhoff Lightbus 返回光纤环里的物理模块号；若现场总线本身无地址概念，返回 TwinCAT 内部的逻辑地址。'
        'box 名字是工程师在 System Manager 配置时给的，调用者把这个名字传入即可，FB 经 ADS 异步查询。'
    ),
    behavior=(
        '`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 把 (DEVICEID, BOXNAME) 通过 ADS 发到 I/O 子系统。'
        'TwinCAT I/O 驱动维护一张 box 名 ↔ 地址的查找表，返回结果填到 `BOXADDR`。'
        '成功时 `ERR := FALSE`、`ERRID := 0`、`BOXADDR` 有效；失败时 `ERR := TRUE`、`ERRID` 含 ADS 错误号，`BOXADDR` 不可用。'
        '**触发语义**：必须上升沿，持续 TRUE 不会重复触发。'
        '**典型用法**：工程图纸里 box 取了名字（例如 "Drive_X1"），但同事在 Profibus 配置时把站号改过，PLC 程序里用名字而非站号去定位 box 就能避免与 hardcode 站号绑死。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('**`BOXNAME` 大小写敏感**：System Manager 配置时用的具体大小写要原样传入，不然 ADS 返回 box not found。', True),
        ('**返回的 `BOXADDR` 是 `UINT`**：Profibus 站号最大 125；Lightbus 光纤环最大约 254，都在 UINT 范围内；若现场总线允许更大编址要确认是否够用。', True),
    ],
    scenario='灌装线工程：6 台 Profibus 设备名字定义为 Fill1..Fill6，工程师在调试时偶尔会改 Profibus 站号。PLC 启动诊断脚本用名字查站号、写到诊断日志，避免硬编码站号被改后断链。',
    value='把 "名字 → 站号" 的查找做成 PLC 可调用接口，省去手抄 System Manager 配置表的工作，也保证 PLC 程序与现场配置同步。',
    alt=(
        '- 硬编码站号：简单但与现场配置不同步\n'
        '- 用 `IOF_GetBoxNameByAddr` 反向查再缓存：可行，但需要先有有效站号\n'
        '- **本 FB**：直接用名字查站号，最常用'
    ),
    related=['IOF_GetBoxAddrByNameEx', 'IOF_GetBoxNameByAddr', 'IOF_GetBoxCount'],
    xml_scen='调试期间 Profibus 现场总线下挂 6 台变频器 (Drive1..Drive6)，运维要在 PLC 启动时核对每台的站号，与工程图纸做比对存档。',
    xml_val='查表逻辑封装在一次调用里：业务代码只关心名字，不必读 System Manager 配置。',
    xml_verify='登录后 sQueryBoxName 写 "Drive3" → 在线写 bStartLookup := TRUE → 观察 bLookupBusy 短暂 TRUE → 回 FALSE 后 nResolvedBoxAddr 显示 Drive3 的 Profibus 站号；若 bLookupError = TRUE，nLastErrCode 给出错误号（常见 0x6 = 名字找不到）。',
    xml_vars=[
        ('fbResolveBoxAddr', 'IOF_GetBoxAddrByName', None, 'box 名字 → 现场总线地址 FB 实例'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机空串'),
        ('nProfibusDeviceId', 'UDINT', '1', 'Profibus 主站的 Device Id'),
        ('sQueryBoxName', 'T_MaxString', "'Drive3'", '要查的 box 名（与 System Manager 配置一致，区分大小写）'),
        ('bStartLookup', 'BOOL', 'FALSE', '上升沿触发查询'),
        ('tLookupTimeout', 'TIME', 'T#5S', 'ADS 超时'),
        ('bLookupBusy', 'BOOL', None, 'FB 工作中'),
        ('bLookupError', 'BOOL', None, '查询失败'),
        ('nLastErrCode', 'UDINT', None, 'ADS 错误号'),
        ('nResolvedBoxAddr', 'UINT', None, '查得的现场总线站地址'),
    ],
    xml_call=(
        '// 单次调用形式，bStartLookup 上升沿触发\n'
        'fbResolveBoxAddr(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nProfibusDeviceId,\n'
        '    BOXNAME  := sQueryBoxName,\n'
        '    START    := bStartLookup,\n'
        '    TMOUT    := tLookupTimeout,\n'
        '    BUSY     => bLookupBusy,\n'
        '    ERR      => bLookupError,\n'
        '    ERRID    => nLastErrCode,\n'
        '    BOXADDR  => nResolvedBoxAddr\n'
        ');\n'
    ),
)


REG['IOF_GetBoxAddrByNameEx'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '与 `IOF_GetBoxAddrByName` 同源，区别是用 **设备名字** 代替 `DEVICEID` 来定位现场总线主站。'
        '当工程里多个总线（例如同时有 2 块 Profibus 卡 + 1 块 EtherCAT 主站）且 DeviceId 经常因为重新分配而变化时，用设备名字更稳定。'
        '同样异步、`START` 上升沿触发、通过 `BUSY/ERR/ERRID` 报告状态。'
    ),
    behavior=(
        '`START` 上升沿触发：`BUSY := TRUE`，FB 经 ADS 把 (DEVICENAME, BOXNAME) 发到 I/O 子系统，让 TwinCAT 先查设备再查 box，最后返回 `BOXADDR`。'
        '执行流程相当于内部串行调用 `IOF_GetDeviceIDByName` + `IOF_GetBoxAddrByName`，但只占一次 ADS 调用。'
        '**`DEVICENAME` / `BOXNAME` 大小写敏感**，与 System Manager 配置完全一致。'
        '失败原因：设备名找不到 / box 名找不到 / 现场总线未启动 / ADS 超时。'
        '与不带 Ex 版本相比，本 FB 的优势是工程文件改 DeviceId 不会让程序断链——只要名字不改就行。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('**`DEVICENAME` 也大小写敏感**：与 box 名一样要原样传入。', True),
        ('比 `IOF_GetBoxAddrByName` 多一次内部查找，**执行时间略长**（一两个 PLC 周期之差，可忽略）。', True),
    ],
    scenario='大型车间有 2 块 Profibus 主站卡（DP1、DP2），DeviceId 在某次工程文件合并后被重新编号导致原程序断链。改用本 FB 后用设备名字调用，DeviceId 怎么变都没事。',
    value='与硬件配置解耦：现场总线名字稳定，DeviceId 可变。比硬编码 DeviceId 鲁棒。',
    alt=(
        '- `IOF_GetBoxAddrByName` + 硬编码 DeviceId：简单但 DeviceId 变化即断链\n'
        '- `IOF_GetDeviceIDByName` + `IOF_GetBoxAddrByName` 两步：完全等价但消耗两个 FB 实例\n'
        '- **本 FB**：一次调用搞定两步查找'
    ),
    related=['IOF_GetBoxAddrByName', 'IOF_GetDeviceIDByName', 'IOF_GetBoxCount'],
    xml_scen='生产线有 2 路 Profibus（命名 DP_Master_Left / DP_Master_Right），需要根据线路 ID 动态选总线再查 box；用设备名字调用避免硬编码 DeviceId。',
    xml_val='用名字代替 ID，工程改动不需要重编程序。',
    xml_verify='登录后 sActiveBusName := "DP_Master_Right"、sQueryBoxName := "Pump5"，在线写 bStartLookup := TRUE → bLookupBusy 短暂 TRUE → 回 FALSE 后 nResolvedBoxAddr 显示 Pump5 在右侧 Profibus 上的站号。',
    xml_vars=[
        ('fbResolveBoxAddrByDevName', 'IOF_GetBoxAddrByNameEx', None, '用设备名+box 名查站号'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机空串'),
        ('sActiveBusName', 'T_MaxString', "'DP_Master_Right'", '当前选用的 Profibus 主站名'),
        ('sQueryBoxName', 'T_MaxString', "'Pump5'", '要查的 box 名'),
        ('bStartLookup', 'BOOL', 'FALSE', '上升沿触发'),
        ('tLookupTimeout', 'TIME', 'T#5S', 'ADS 超时'),
        ('bLookupBusy', 'BOOL', None, '工作中'),
        ('bLookupError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('nResolvedBoxAddr', 'UINT', None, '查得站号'),
    ],
    xml_call=(
        'fbResolveBoxAddrByDevName(\n'
        '    NETID      := sTargetNetId,\n'
        '    DEVICENAME := sActiveBusName,\n'
        '    BOXNAME    := sQueryBoxName,\n'
        '    START      := bStartLookup,\n'
        '    TMOUT      := tLookupTimeout,\n'
        '    BUSY       => bLookupBusy,\n'
        '    ERR        => bLookupError,\n'
        '    ERRID      => nLastErrCode,\n'
        '    BOXADDR    => nResolvedBoxAddr\n'
        ');\n'
    ),
)


REG['IOF_GetBoxCount'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '读取指定 I/O 设备（现场总线主站）下挂的有效 box（slave / 模块 / 站）数量。'
        '`START` 上升沿触发一次查询，结果以 `BOXCOUNT` 输出，通过 `BUSY/ERR/ERRID` 反映异步状态。'
        '可用于上电时核对实际在线节点数与工程配置是否一致；若不一致立即报警或拒绝启动。'
    ),
    behavior=(
        '`START` 上升沿：`BUSY := TRUE`，FB 经 ADS 向 `DEVICEID` 对应的现场总线主站查询当前活动 slave 数量。'
        '主站维护配置 box 列表 + 在线 box 列表，**本 FB 返回的是 ‹‹已配置且当前在线›› 的数量**——掉线节点不会被算进去，因此可作为简易的"在线节点检查"。'
        '完成后 `BUSY := FALSE`、`BOXCOUNT` 含数量。'
        '执行时长几十毫秒，可放在上电诊断序列里阻塞调用一次。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('返回值 **只算在线 box**：若工程配置 8 个 box 但只有 5 个上电，会返回 5——需要与工程配置数对比识别离线节点。', True),
        ('返回类型在 PDF 中既写过 `BOXCOUNT : UDINT` 也提到 `UINT`（描述列写 "The number of boxes"，无单位）；以 VAR 区为准（`UDINT`）。', True),
    ],
    scenario='印刷机上电自检：工程配置 12 台 Profibus 设备 → 调本 FB 看是否得到 12 → 否则报警 "Profibus 节点数不符，可能有设备掉线"，拒绝继续启动。',
    value='把 "现场是否有节点掉线" 做成可调用接口，几毫秒拿到结果；不必逐个 box 单独诊断。',
    alt=(
        '- 逐 box 调 `IOF_GetBoxNetId`：能做但占多个 FB 调用周期\n'
        '- 让总线主站自己报告 diagnostic state：信息丰富但解析复杂\n'
        '- **本 FB**：一次拿到节点总数，做"是否齐全"判断最快'
    ),
    related=['IOF_GetBoxAddrByName', 'IOF_GetBoxNameByAddr', 'IOF_GetDeviceCount'],
    xml_scen='上电自检阶段，PLC 程序需要确认 Profibus 总线下挂 12 台设备全部在线，否则拒绝进入"运行"状态。',
    xml_val='把"在线节点数核对"做成 30 行自检脚本里的一行调用。',
    xml_verify='登录后写 bRequestBoxCount := TRUE → bCountBusy 短暂 TRUE → 回 FALSE 后 nActiveBoxCount 显示实际在线节点数；与工程配置数 nExpectedBoxCount 对比，nActiveBoxCount < nExpectedBoxCount 时 bNodeMissingAlarm 置 TRUE。',
    xml_vars=[
        ('fbReadBoxCount', 'IOF_GetBoxCount', None, '读现场总线 box 计数'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nProfibusDeviceId', 'UDINT', '1', 'Profibus 主站 Device Id'),
        ('bRequestBoxCount', 'BOOL', 'FALSE', '上升沿触发计数请求'),
        ('tCountTimeout', 'TIME', 'T#5S', 'ADS 超时'),
        ('nExpectedBoxCount', 'UDINT', '12', '工程配置的目标节点数'),
        ('bCountBusy', 'BOOL', None, 'FB 工作中'),
        ('bCountError', 'BOOL', None, 'ADS 失败'),
        ('nLastErrCode', 'UDINT', None, 'ADS 错误号'),
        ('nActiveBoxCount', 'UDINT', None, '查得的在线节点数'),
        ('bNodeMissingAlarm', 'BOOL', None, '在线节点数不足报警'),
    ],
    xml_call=(
        'fbReadBoxCount(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nProfibusDeviceId,\n'
        '    START    := bRequestBoxCount,\n'
        '    TMOUT    := tCountTimeout,\n'
        '    BUSY     => bCountBusy,\n'
        '    ERR      => bCountError,\n'
        '    ERRID    => nLastErrCode,\n'
        '    BOXCOUNT => nActiveBoxCount\n'
        ');\n'
        '\n'
        '// 完成后核对：在线节点不足即报警（必须在 FB 调用之后用其输出）\n'
        'IF NOT bCountBusy AND NOT bCountError THEN\n'
        '    bNodeMissingAlarm := nActiveBoxCount &lt; nExpectedBoxCount;\n'
        'END_IF;\n'
    ),
)


REG['IOF_GetBoxNameByAddr'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '与 `IOF_GetBoxAddrByName` 反向：已知现场总线站地址 + 所属 DeviceId，查询该 box 在 System Manager 配置时被命名的字符串。'
        '常用于把"出错的 box 站号"翻译成人类可读的"出错设备名字"做到 HMI / 报警日志里。'
    ),
    behavior=(
        '`START` 上升沿触发一次反向查询：`BUSY := TRUE`，FB 经 ADS 把 (DEVICEID, BOXADDR) 发到 I/O 子系统。'
        '主站查内部 box 注册表，返回 box 名字到 `BOXNAME`（`T_MaxString`，最大 255 字节）。'
        '执行成功 `ERR := FALSE`、`BOXNAME` 含工程命名；'
        '若 BOXADDR 是无效站号 / 该地址下没配 box，`ERR := TRUE`、`ERRID` 含错误码、`BOXNAME` 空串。'
        '名字字符串编码取决于 System Manager 配置时输入的编码（一般 ASCII；含中文需要 UTF-8 兼容字符串处理）。'
        '触发语义为上升沿一次性，重复触发要先把 `START` 拉低再拉高；不会循环触发。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('**`BOXNAME : T_MaxString`** 是 255 字节缓冲；接收侧 STRING 长度要够，否则会被截断。', True),
        ('若同一现场总线上存在重名 box（System Manager 允许重名以方便复制配置），返回的是第一个匹配项，不一定是预期项。', True),
    ],
    scenario='Profibus 报警："Slave at station 17 failed"。直接把"17"显示给操作员意义不大；调本 FB 把 17 翻译成 "Drive_PaintPump_Left" 显示在 HMI 上，操作员立刻知道哪台设备。',
    value='把数字 ID 翻译成人类可读名字，HMI 报警 / 工单日志可读性大幅提升。',
    alt=(
        '- 维护一份 PLC 静态查表：station 号 → 名字。手维护、易出错\n'
        '- 操作员翻图纸：低效\n'
        '- **本 FB**：自动从 TwinCAT 配置取名字，永远与工程同步'
    ),
    related=['IOF_GetBoxAddrByName', 'IOF_GetBoxNetId', 'IOF_GetBoxCount'],
    xml_scen='Profibus 出错诊断 FB 报"站 17 出错"，本程序把站号翻译成名字写进报警字符串 → HMI 显示"Drive_PaintPump_Left 离线"而不是"slave 17 fail"。',
    xml_val='让报警日志直接可读，减少现场抢修时翻图纸的时间。',
    xml_verify='登录后 nFailedStationAddr := 17，在线写 bStartResolve := TRUE → bResolveBusy 短暂 TRUE → 回 FALSE 后 sResolvedDeviceName 显示该站号对应的工程命名（如 "Drive_PaintPump_Left"）。',
    xml_vars=[
        ('fbResolveBoxName', 'IOF_GetBoxNameByAddr', None, '站号 → 名字 FB 实例'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nProfibusDeviceId', 'UDINT', '1', 'Profibus 主站 Device Id'),
        ('nFailedStationAddr', 'UINT', '17', '诊断 FB 报的离线站号'),
        ('bStartResolve', 'BOOL', 'FALSE', '上升沿触发查询'),
        ('tResolveTimeout', 'TIME', 'T#5S', 'ADS 超时'),
        ('bResolveBusy', 'BOOL', None, '工作中'),
        ('bResolveError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('sResolvedDeviceName', 'T_MaxString', None, '查得的工程命名字符串'),
    ],
    xml_call=(
        'fbResolveBoxName(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nProfibusDeviceId,\n'
        '    BOXADDR  := nFailedStationAddr,\n'
        '    START    := bStartResolve,\n'
        '    TMOUT    := tResolveTimeout,\n'
        '    BUSY     => bResolveBusy,\n'
        '    ERR      => bResolveError,\n'
        '    ERRID    => nLastErrCode,\n'
        '    BOXNAME  => sResolvedDeviceName\n'
        ');\n'
    ),
)


REG['IOF_GetBoxNetId'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '一部分 box（例如带固件的智能模块）会在 TwinCAT 配置时被分配自己的 AMS Net ID，这样 PLC 程序可以经 ADS 直接调用该 box 内部的固件功能。'
        '本 FB 已知主站 DeviceId + box 在现场总线上的地址，反查该 box 的 AMS Net ID（如有）。'
    ),
    behavior=(
        '`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 把 (DEVICEID, BOXADDR) 发到 I/O 子系统。'
        '若该 box 在工程配置时被分配过 AMS Net ID，结果通过 `BoxNetId` 输出（字符串形式如 "1.2.3.4.5.6"）。'
        '若 box 未配 AMS Net ID 或硬件不支持，`ERR := TRUE`、`ERRID` 给出错误号，`BoxNetId` 为空串。'
        '查询结果可直接作为后续 ADS 调用的目标 NetId 参数使用，无需手抄字符串到 PLC 程序。'
        '触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再决定下一次是否重新触发。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('**并非所有 box 都有 AMS Net ID**：只有带固件 / 智能型 box（如 FC310x、CP9030）才会分配。普通无源 IO 设备无此项。', True),
        ('`BOXADDR : WORD` 与其他 box FB 的 `BOXADDR : UINT` 类型不同——VAR 区里 PDF 明确写 WORD，调用方注意类型转换。', True),
    ],
    scenario='Profibus 主卡 FC3101 自带 AMS Net ID，要从 PLC 调用 FC3101 内部固件功能（例如读总线统计）需要先拿到它的 NetId。',
    value='避免在 System Manager 里手抄 NetId 写死在 PLC 程序里——以工程改动后两端不同步为代价。',
    alt=(
        '- 手抄 NetId 写常量：简单但工程改动易断链\n'
        '- 用 box 名字查 NetId：需要更多步骤\n'
        '- **本 FB**：站号直接查 NetId，最直接'
    ),
    related=['IOF_GetDeviceNetId', 'IOF_GetBoxAddrByName', 'IOF_GetBoxNameByAddr'],
    xml_scen='调试时要从 PLC 通过 ADS 读 FC3101 主卡的总线诊断数据。需要先查得该卡作为 box 在系统里分配的 AMS Net ID。',
    xml_val='避免硬编码 NetId；工程改动也能自适应。',
    xml_verify='登录后 nFc310xBoxAddr := 0 (Profibus 主站自身)，在线写 bStartLookupBoxNetId := TRUE → 回 FALSE 后 sFc310xBoxNetId 显示 FC3101 卡的 AMS Net ID。',
    xml_vars=[
        ('fbLookupBoxNetId', 'IOF_GetBoxNetId', None, 'box AMS Net ID 查询 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nProfibusDeviceId', 'UDINT', '1', 'Profibus 主站 Device Id'),
        ('nFc310xBoxAddr', 'WORD', '0', '目标 box 的现场总线地址（WORD 类型）'),
        ('bStartLookupBoxNetId', 'BOOL', 'FALSE', '上升沿触发查询'),
        ('tLookupTimeout', 'TIME', 'T#5S', 'ADS 超时'),
        ('bLookupBusy', 'BOOL', None, '工作中'),
        ('bLookupError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('sFc310xBoxNetId', 'T_AmsNetId', None, '查得的 box AMS Net ID'),
    ],
    xml_call=(
        'fbLookupBoxNetId(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nProfibusDeviceId,\n'
        '    BOXADDR  := nFc310xBoxAddr,\n'
        '    START    := bStartLookupBoxNetId,\n'
        '    TMOUT    := tLookupTimeout,\n'
        '    BUSY     => bLookupBusy,\n'
        '    ERR      => bLookupError,\n'
        '    ERRID    => nLastErrCode,\n'
        '    BoxNetId => sFc310xBoxNetId\n'
        ');\n'
    ),
)


REG['IOF_GetDeviceCount'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '读取本机 TwinCAT 系统中**配置且当前激活**的 I/O 设备总数（一个 I/O 设备 = 一块现场总线主站卡或一个虚拟 IO 接口）。'
        '`START` 上升沿触发一次，结果以 `DEVICECOUNT` 输出。'
    ),
    behavior=(
        '`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 调用 I/O 子系统返回当前激活的 I/O 设备数（典型值 1-10）。'
        '此处"激活"的含义是 System Manager 配置中未被 Disable、且底层驱动加载成功的 I/O 设备。'
        '完成后 `BUSY := FALSE`、`DEVICECOUNT` 含数量。'
        '可与 `IOF_GetDeviceIDs` 配合：先用本 FB 取设备数 N，再申请 N+1 个 WORD 的数组传给 `IOF_GetDeviceIDs` 拿到所有 ID 列表。'
        '触发语义为上升沿一次性，重复触发要先把 `START` 拉低再拉高。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('结果只算"激活"设备：System Manager 中被 Disabled 的不计入。', True),
        ('上电后 IO 设备启动有先后，启动尚未完成时调本 FB 可能拿到比预期少的数字；建议放在上电延时 5 秒后调用。', True),
    ],
    scenario='上电诊断脚本：要枚举所有 I/O 设备做巡检 → 先调本 FB 拿到总数 N → 再调 `IOF_GetDeviceIDs` 拿到 N 个 ID → 逐个 ID 调 `IOF_GetDeviceType` / `IOF_GetDeviceName` 做日志。',
    value='把"系统里有几块现场总线卡"做成可程序化查询，避免硬编码"我知道有 3 块"。',
    alt=(
        '- 硬编码已知设备数：工程改动不同步\n'
        '- 看 System Manager：人工不可程序化\n'
        '- **本 FB**：标准入口'
    ),
    related=['IOF_GetDeviceIDs', 'IOF_GetDeviceIDByName', 'IOF_GetDeviceName'],
    xml_scen='PLC 上电自检：列出所有现场总线 / IO 设备到诊断日志，第一步先取总数。',
    xml_val='为 IO 枚举循环提供准确循环上限，避免越界访问。',
    xml_verify='登录后写 bRequestDeviceCount := TRUE → bCountBusy 短暂 TRUE → 回 FALSE 后 nActiveDeviceCount 显示工程里激活的设备数（典型 1-3）。',
    xml_vars=[
        ('fbReadDeviceCount', 'IOF_GetDeviceCount', None, 'IO 设备计数 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('bRequestDeviceCount', 'BOOL', 'FALSE', '上升沿触发'),
        ('tCountTimeout', 'TIME', 'T#5S', 'ADS 超时'),
        ('bCountBusy', 'BOOL', None, '工作中'),
        ('bCountError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('nActiveDeviceCount', 'UDINT', None, '查得设备总数'),
    ],
    xml_call=(
        'fbReadDeviceCount(\n'
        '    NETID       := sTargetNetId,\n'
        '    START       := bRequestDeviceCount,\n'
        '    TMOUT       := tCountTimeout,\n'
        '    BUSY        => bCountBusy,\n'
        '    ERR         => bCountError,\n'
        '    ERRID       => nLastErrCode,\n'
        '    DEVICECOUNT => nActiveDeviceCount\n'
        ');\n'
    ),
)


REG['IOF_GetDeviceIDByName'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '已知 I/O 设备名字，查它的 DeviceId。设备名字是工程师在 System Manager 配置时输入的字符串，DeviceId 由 TwinCAT 系统自动分配（用户不可改）。'
        '该 FB 让 PLC 程序通过"稳定的名字"得到"可能变化的 ID"，便于后续把 ID 用于其它 `IOF_*` 调用。'
    ),
    behavior=(
        '`START` 上升沿：`BUSY := TRUE`，FB 经 ADS 在 TwinCAT I/O 子系统的设备注册表里查名字 → ID。'
        '成功 `DEVICEID` 输出有效；失败 `ERR := TRUE`、`ERRID` 给错误号（常见 `0x6` 名字找不到）。'
        '工程改动重新分配 ID 后，本 FB 仍按名字找得到正确 ID——前提是名字保持不变。'
        '建议把所有 `IOF_*` 调用入口都先经过本 FB 解析 ID 再用。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('**`DEVICENAME` 大小写敏感**。', True),
        ('多块同类型设备命名时若有空格 / 特殊字符要小心；建议命名只用 `A-Z 0-9 _`。', True),
    ],
    scenario='工程多块现场总线卡，部分被禁用 / 重新分配后 DeviceId 改变。用名字查 ID 让 PLC 程序与硬件解耦。',
    value='避免硬编码 DeviceId 导致工程改动后断链；名字查询是工程上的标准做法。',
    alt=(
        '- 硬编码 DeviceId：易断链\n'
        '- **本 FB**：标准做法'
    ),
    related=['IOF_GetDeviceCount', 'IOF_GetDeviceName', 'IOF_GetDeviceNetId'],
    xml_scen='程序需要按设备名字定位 Profibus 主站做后续操作，避免硬编码 ID。',
    xml_val='与工程配置同步：改 ID 不影响 PLC 程序，只要名字不改。',
    xml_verify='登录后 sLookupDeviceName := "DP_Master_Main"，在线写 bStartLookupDeviceId := TRUE → 回 FALSE 后 nLookedUpDeviceId 显示 System Manager 中分配给该设备的 Device Id。',
    xml_vars=[
        ('fbLookupDeviceId', 'IOF_GetDeviceIDByName', None, '设备名 → ID FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('sLookupDeviceName', 'T_MaxString', "'DP_Master_Main'", '设备名字（区分大小写）'),
        ('bStartLookupDeviceId', 'BOOL', 'FALSE', '上升沿触发'),
        ('tLookupTimeout', 'TIME', 'T#5S', '超时'),
        ('bLookupBusy', 'BOOL', None, '工作中'),
        ('bLookupError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('nLookedUpDeviceId', 'UDINT', None, '查得 Device Id'),
    ],
    xml_call=(
        'fbLookupDeviceId(\n'
        '    NETID      := sTargetNetId,\n'
        '    DEVICENAME := sLookupDeviceName,\n'
        '    START      := bStartLookupDeviceId,\n'
        '    TMOUT      := tLookupTimeout,\n'
        '    BUSY       => bLookupBusy,\n'
        '    ERR        => bLookupError,\n'
        '    ERRID      => nLastErrCode,\n'
        '    DEVICEID   => nLookedUpDeviceId\n'
        ');\n'
    ),
)


REG['IOF_GetDeviceIDs'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '一次性读取所有激活 I/O 设备的 DeviceId 列表，写入用户提供的 WORD 数组。'
        '第 0 个 WORD 是 ID 总数，后续依次为每个设备的 ID。'
        '`START` 上升沿触发。'
    ),
    behavior=(
        '调用前用户准备一个 `ARRAY[1..N] OF WORD` 缓冲区（N ≥ 设备总数 + 1）并把 `LEN` 设为字节长度。'
        '`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 把 ID 表读到 `DESTADDR` 指向的缓冲区。'
        '完成后 `BUSY := FALSE`，缓冲区里：第 1 个 WORD = 数量，第 2..N+1 WORD = 各设备 ID。'
        '常见调用顺序：先 `IOF_GetDeviceCount` 取总数 → 申请相应大小数组 → 调本 FB → 遍历 ID 列表做枚举诊断。'
        '触发语义为上升沿一次性；调用者需要在 `BUSY` 落回后再读缓冲区，否则可能读到旧数据。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('**缓冲区大小要够**：若工程实际有 5 个设备，至少给 6 个 WORD（第一个存计数）；不够会 ADS 报错或返回截断数据。', True),
        ('**`DESTADDR : PVOID`** 必须用 `ADR(arrBuffer)` 取得；`LEN` 是字节数（`SIZEOF(arrBuffer)`）不是 WORD 个数。', True),
        ('PDF 中 `LEN` VAR 表写 `UDINT`，描述表写 "UINT"——以 VAR 区为准（UDINT）。', True),
    ],
    scenario='上电诊断脚本：枚举所有 IO 设备做巡检 → 用本 FB 一次拿到所有 ID → for 循环逐个调 `IOF_GetDeviceType` 写日志。',
    value='避免多次 ADS 调用逐个取 ID；一次拿全部。',
    alt=(
        '- 多次调 `IOF_GetDeviceIDByName`：需先知道所有名字\n'
        '- **本 FB**：一次拿全部 ID'
    ),
    related=['IOF_GetDeviceCount', 'IOF_GetDeviceType', 'IOF_GetDeviceName'],
    xml_scen='上电自检：一次性读出所有现场总线 / IO 设备的 ID，后续 for 循环遍历做巡检。',
    xml_val='减少 ADS 调用次数，从 N 次降到 1 次。',
    xml_verify='登录后写 bStartReadAllIds := TRUE → bReadBusy 短暂 TRUE → 回 FALSE 后 aDeviceIdBuffer[1] 是数量，aDeviceIdBuffer[2..] 是各 ID。',
    xml_vars=[
        ('fbReadAllDeviceIds', 'IOF_GetDeviceIDs', None, 'FB：一次性读所有 IO 设备 ID'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('aDeviceIdBuffer', 'ARRAY[1..201] OF WORD', None, 'ID 缓冲（最多 200 设备）'),
        ('bStartReadAllIds', 'BOOL', 'FALSE', '上升沿触发'),
        ('tReadTimeout', 'TIME', 'T#5S', '超时'),
        ('bReadBusy', 'BOOL', None, '工作中'),
        ('bReadError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        '// LEN 用 SIZEOF 自动算字节数；DESTADDR 用 ADR(数组)\n'
        'fbReadAllDeviceIds(\n'
        '    NETID    := sTargetNetId,\n'
        '    LEN      := SIZEOF(aDeviceIdBuffer),\n'
        '    DESTADDR := ADR(aDeviceIdBuffer),\n'
        '    START    := bStartReadAllIds,\n'
        '    TMOUT    := tReadTimeout,\n'
        '    BUSY     => bReadBusy,\n'
        '    ERR      => bReadError,\n'
        '    ERRID    => nLastErrCode\n'
        ');\n'
        '\n'
        '// 完成后 aDeviceIdBuffer[1] = 数量，aDeviceIdBuffer[2..] 是各 ID（必须等 bReadBusy 落回再读结果）\n'
    ),
)


REG['IOF_GetDeviceInfoByName'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '已知 I/O 设备名字，一次性返回该设备的 **DeviceId + AMS Net ID**（如有）。'
        '比单独调用 `IOF_GetDeviceIDByName` 与 `IOF_GetDeviceNetId` 省一次 ADS 往返。'
    ),
    behavior=(
        '`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 把名字发到 I/O 子系统查询。'
        '成功后 `DEVICEID` 与 `DEVICENETID` 同时有效，可一起用于后续 ADS 调用或其它 `IOF_*` 接口。'
        '若该设备未配 AMS Net ID，`DEVICENETID` 是空串；这不算错误，`ERR := FALSE`。'
        '若设备名字找不到，`ERR := TRUE`、`ERRID` 给出 ADS 错误号。'
        '触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再决定下一次是否重新触发。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('返回的 `DEVICENETID` 可能为空串——并非所有 IO 设备都分配了 AMS Net ID。', True),
        ('**`DEVICENAME` 大小写敏感**。', True),
    ],
    scenario='想从 PLC 调用某 IO 设备的固件功能 → 需要它的 AMS Net ID + DeviceId 配套：直接用本 FB 一次取齐，避免两次 ADS 往返。',
    value='节省 ADS 调用次数；接口聚合一次返回所有"设备身份"字段。',
    alt=(
        '- `IOF_GetDeviceIDByName` + `IOF_GetDeviceNetId` 两步：能做但慢\n'
        '- **本 FB**：一次完成'
    ),
    related=['IOF_GetDeviceIDByName', 'IOF_GetDeviceNetId', 'IOF_GetDeviceType'],
    xml_scen='程序要对 Profibus 主卡调用 ADS 读总线诊断；需要同时拿到它的 DeviceId（用于其他 IOF_ 接口）和 AMS Net ID（用于 ADSREAD）。',
    xml_val='一个 FB 实例代替两个，节省调用周期。',
    xml_verify='登录后 sQueryDeviceName := "DP_Master_Main"，在线写 bStartFetchInfo := TRUE → 回 FALSE 后同时填出 nDeviceIdOut + sDeviceNetIdOut。',
    xml_vars=[
        ('fbFetchDeviceInfo', 'IOF_GetDeviceInfoByName', None, '一次取 DeviceId + NetId'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('sQueryDeviceName', 'T_MaxString', "'DP_Master_Main'", '设备名字'),
        ('bStartFetchInfo', 'BOOL', 'FALSE', '上升沿触发'),
        ('tFetchTimeout', 'TIME', 'T#5S', '超时'),
        ('bFetchBusy', 'BOOL', None, '工作中'),
        ('bFetchError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('nDeviceIdOut', 'UDINT', None, 'Device Id'),
        ('sDeviceNetIdOut', 'T_AmsNetId', None, '设备 AMS Net ID（可能为空）'),
    ],
    xml_call=(
        'fbFetchDeviceInfo(\n'
        '    NETID       := sTargetNetId,\n'
        '    DEVICENAME  := sQueryDeviceName,\n'
        '    START       := bStartFetchInfo,\n'
        '    TMOUT       := tFetchTimeout,\n'
        '    BUSY        => bFetchBusy,\n'
        '    ERR         => bFetchError,\n'
        '    ERRID       => nLastErrCode,\n'
        '    DEVICEID    => nDeviceIdOut,\n'
        '    DEVICENETID => sDeviceNetIdOut\n'
        ');\n'
    ),
)


REG['IOF_GetDeviceName'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '已知 DeviceId，反查工程师在 System Manager 配置时给该 I/O 设备起的名字。'
        '常用于诊断脚本中把"设备 ID 5 出错"翻译成"DP_Master_Right 出错"。'
    ),
    behavior=(
        '`START` 上升沿触发一次反查：`BUSY := TRUE`，FB 经 ADS 把名字读到 `DEVICENAME`（`T_MaxString`，最大 255 字节）。'
        '与 `IOF_GetBoxNameByAddr` 类似，本 FB 是 **设备级** 翻译，前者是 **box 级** 翻译——两者用法相同但作用对象不同。'
        '若 DeviceId 不存在或对应设备未启用，`ERR := TRUE`、`ERRID` 给出 ADS 错误号。'
        '触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后才能信任 `DEVICENAME` 内容。'
        '常用于上电诊断 + 报警字符串拼接：把"出错的 DeviceId 数字"翻译成工程命名做到 HMI 日志可读。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('返回的 `DEVICENAME` 编码取决于 System Manager 输入；含 ASCII 之外的字符需注意 STRING 长度。', True),
    ],
    scenario='诊断日志：原本只能写 "Device 5 fail"，调本 FB 后写 "Device 5 (DP_Master_Right) fail"，运维更直接。',
    value='把数字 ID 翻译成人类可读名字。',
    alt=(
        '- 维护静态查表：易过期\n'
        '- **本 FB**：自动同步'
    ),
    related=['IOF_GetDeviceIDByName', 'IOF_GetDeviceType', 'IOF_GetBoxNameByAddr'],
    xml_scen='IO 巡检脚本枚举所有 Device Id 后，对每个 ID 调本 FB 拿名字写到日志。',
    xml_val='可读诊断日志。',
    xml_verify='登录后 nLookupDeviceId := 1，在线写 bStartGetName := TRUE → 回 FALSE 后 sDeviceNameOut 显示 System Manager 命名。',
    xml_vars=[
        ('fbGetDeviceName', 'IOF_GetDeviceName', None, 'ID → 名字 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nLookupDeviceId', 'UDINT', '1', '要查的 Device Id'),
        ('bStartGetName', 'BOOL', 'FALSE', '上升沿触发'),
        ('tGetNameTimeout', 'TIME', 'T#5S', '超时'),
        ('bGetNameBusy', 'BOOL', None, '工作中'),
        ('bGetNameError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('sDeviceNameOut', 'T_MaxString', None, '设备名'),
    ],
    xml_call=(
        'fbGetDeviceName(\n'
        '    NETID      := sTargetNetId,\n'
        '    DEVICEID   := nLookupDeviceId,\n'
        '    START      := bStartGetName,\n'
        '    TMOUT      := tGetNameTimeout,\n'
        '    BUSY       => bGetNameBusy,\n'
        '    ERR        => bGetNameError,\n'
        '    ERRID      => nLastErrCode,\n'
        '    DEVICENAME => sDeviceNameOut\n'
        ');\n'
    ),
)


REG['IOF_GetDeviceNetId'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '部分 I/O 设备（如 FC310x Profibus 卡 / CP9030 通讯卡）在 System Manager 配置时会被分配自己的 AMS Net ID，用以让 PLC 经 ADS 直接调用该卡的固件功能。'
        '本 FB 已知 DeviceId，反查该 AMS Net ID。'
    ),
    behavior=(
        '`START` 上升沿触发一次反查：`BUSY := TRUE`，FB 经 ADS 查 I/O 子系统的 NetId 注册表。'
        '成功时 `DeviceNetId` 含字符串（如 "1.2.3.4.5.6"），该 NetId 可直接作为后续 ADS 调用的目标参数使用。'
        '若该设备未配 NetId 或硬件不支持（普通 KL 耦合器 / EtherCAT 主站常无），`ERR := TRUE`、`ERRID` 给出错误号。'
        '触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再使用 `DeviceNetId` 字符串。'
        '与 `IOF_GetDeviceInfoByName` 相比，本 FB 只返回 NetId 一个字段；若同时还需要 DeviceId，用 ByName 版本更省调用。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('不是所有 IO 设备都有 AMS Net ID——纯 EtherCAT 主站 / 普通 KL 端子耦合器一般没有。', True),
    ],
    scenario='程序需要对 FC310x Profibus 卡调用 ADS 读总线诊断字 → 先查得卡的 AMS Net ID 再调 ADSREAD。',
    value='避免硬编码 NetId；工程改动也同步。',
    alt=(
        '- 硬编码 NetId：工程改动易断链\n'
        '- 用 `IOF_GetDeviceInfoByName` 一次取齐 ID + NetId：更通用\n'
        '- **本 FB**：已经有 DeviceId 时最直接'
    ),
    related=['IOF_GetDeviceInfoByName', 'IOF_GetDeviceIDByName', 'IOF_GetBoxNetId'],
    xml_scen='FC310x Profibus 主卡的 ADS 诊断接口需要它的 AMS Net ID。',
    xml_val='程序与工程配置同步。',
    xml_verify='登录后 nLookupDeviceId := 1（FC310x 的 Device Id），在线写 bStartLookupNetId := TRUE → 回 FALSE 后 sDeviceNetIdOut 显示该卡的 AMS Net ID。',
    xml_vars=[
        ('fbGetDeviceNetId', 'IOF_GetDeviceNetId', None, 'DeviceId → AMS Net ID'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nLookupDeviceId', 'UDINT', '1', '目标 Device Id'),
        ('bStartLookupNetId', 'BOOL', 'FALSE', '上升沿触发'),
        ('tLookupTimeout', 'TIME', 'T#5S', '超时'),
        ('bLookupBusy', 'BOOL', None, '工作中'),
        ('bLookupError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('sDeviceNetIdOut', 'T_AmsNetId', None, '查得的 AMS Net ID'),
    ],
    xml_call=(
        'fbGetDeviceNetId(\n'
        '    NETID       := sTargetNetId,\n'
        '    DEVICEID    := nLookupDeviceId,\n'
        '    START       := bStartLookupNetId,\n'
        '    TMOUT       := tLookupTimeout,\n'
        '    BUSY        => bLookupBusy,\n'
        '    ERR         => bLookupError,\n'
        '    ERRID       => nLastErrCode,\n'
        '    DeviceNetId => sDeviceNetIdOut\n'
        ');\n'
    ),
)


REG['IOF_GetDeviceType'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '已知 DeviceId，查该 I/O 设备的设备类型（枚举 `IODEVICETYPES`）。'
        '类型常量定义在库的全局枚举里，例如 Profibus master / EtherCAT master / Lightbus / KL coupler 等。'
        '常用于上电巡检判定每块 IO 卡的种类决定后续诊断策略。'
    ),
    behavior=(
        '`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 查 I/O 子系统的设备类型字段，返回到 `IODeviceType`。'
        '完成后可对枚举值做 CASE 分支，对不同总线类型走不同诊断流程。'
        '枚举常量定义在库的全局类型 `IODEVICETYPES` 中，包含 Profibus master / EtherCAT master / Lightbus / KL coupler 等条目。'
        '触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后才能信任 `IODeviceType` 值。'
        '若 DeviceId 无效或对应设备未启用，`ERR := TRUE`、`ERRID` 给出 ADS 错误号。'
    ),
    pitfalls=ADS_PITFALLS + [
        ('`IODEVICETYPES` 枚举在 PDF §5.x（具体常量列表见 PDF），上百种值；判定逻辑建议 CASE 而不是 IF=A OR IF=B。', True),
    ],
    scenario='上电诊断 for 循环：对每个 DeviceId 调本 FB 看是否 Profibus → 是的话执行 Profibus 专属诊断流程；EtherCAT 设备走另一支。',
    value='让通用诊断脚本支持多种总线，按类型分流。',
    alt=(
        '- 按名字 string match："PB" / "EC"：脆弱\n'
        '- **本 FB**：枚举型号精确匹配'
    ),
    related=['IOF_GetDeviceIDs', 'IOF_GetDeviceName', 'IOF_GetDeviceCount'],
    xml_scen='IO 巡检：循环遍历 Device Id，对每个 ID 判断是 Profibus / EtherCAT / KL coupler 决定下一步诊断分支。',
    xml_val='通用诊断脚本支持多总线。',
    xml_verify='登录后 nLookupDeviceId := 1，在线写 bStartReadType := TRUE → 回 FALSE 后 eDeviceTypeOut 显示枚举值（与 PDF 中 IODEVICETYPES 表对照）。',
    xml_vars=[
        ('fbGetDeviceType', 'IOF_GetDeviceType', None, '设备类型查询 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nLookupDeviceId', 'UDINT', '1', '目标 Device Id'),
        ('bStartReadType', 'BOOL', 'FALSE', '上升沿触发'),
        ('tReadTimeout', 'TIME', 'T#5S', '超时'),
        ('bReadBusy', 'BOOL', None, '工作中'),
        ('bReadError', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('eDeviceTypeOut', 'IODEVICETYPES', None, '设备类型枚举'),
    ],
    xml_call=(
        'fbGetDeviceType(\n'
        '    NETID        := sTargetNetId,\n'
        '    DEVICEID     := nLookupDeviceId,\n'
        '    START        := bStartReadType,\n'
        '    TMOUT        := tReadTimeout,\n'
        '    BUSY         => bReadBusy,\n'
        '    ERR          => bReadError,\n'
        '    ERRID        => nLastErrCode,\n'
        '    IODeviceType => eDeviceTypeOut\n'
        ');\n'
    ),
)


# ---------------- ASI master terminal (8 FBs) ----------------

ASI_PITFALLS = [
    ('**必须循环调用 `FB_ASI_ParameterControl`**，它是所有 ASI FB 的后台通讯调度器。不调它，其它所有 ASI FB 都不会动。', False),
    ('`stParameterBuffer : ST_ParameterBuffer` 是全局共享缓冲：所有 ASI FB 实例 + `FB_ASI_ParameterControl` 必须传同一个实例，否则后台调度无法工作。', True),
    ('`stParameter_IN` / `stParameter_OUT` 必须 **链到 System Manager 中 ASI 主端子（如 KL6201 / EL6201）的过程数据**——通过 AT %I* / AT %Q* 映射；不链则 ASI 通讯通道根本没建立。', True),
    ('`bBusy = TRUE` 只表示 *命令被接受*，**不是命令被执行**。具体执行是否完成需要看 `bErr` + `iErrornumber` 在 `bBusy` 落回后的状态。', True),
    ('ASI 命令专用错误码（`bErrornumber` / `iErrornumber`）见 ASI 主端子文档（KL6201/EL6201 手册）——PDF 未列入本节，调用方需要查 ASI master 错误码表。', True),
]

REG['FB_ASI_Addressing'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AS-Interface（ASI / AS-i）现场总线上为 slave 重新编址：把 slave 当前地址（`iOldAddress`）改成新地址（`iNewAddress`）。'
        '常用于现场更换 slave 后写新地址（新出厂的 ASI slave 地址默认 0）。'
        '本 FB 与其它 ASI FB 一样，依赖 `FB_ASI_ParameterControl` 在后台调度通讯。'
    ),
    behavior=(
        '`bStart` 上升沿触发：FB 把"编址命令"放到 `stParameterBuffer` 共享缓冲里等 `FB_ASI_ParameterControl` 取走、经过 ASI 主端子的过程数据发到 slave。'
        '`bBusy := TRUE`（命令已被接受、放入队列），slave 接收后修改自己的地址并应答。'
        '完成后 `bBusy := FALSE`；若过程出错 `bErr := TRUE`、`bErrornumber` 给出 ASI 主端子的错误码（参见 KL6201 手册的命令错误码表）。'
        '**注意**：ASI slave 地址范围 1..31（标准 ASI）或 1A..31B（A/B 扩展）。新出厂 slave 地址 = 0，必须先用本 FB 编址才能正常通讯。'
    ),
    var_desc={
        'iOldAddress': '当前 slave 地址。新出厂 slave 默认地址为 0。范围：标准 ASI = 0..31，A/B 扩展 = 0..62 (0x00..0x3E)。',
        'iNewAddress': '要写入 slave 的新地址。',
        'bStart': '上升沿触发一次编址命令；调用期间保持高电平，完成后由用户清零。',
        'stParameterBuffer': 'ASI FB 共享后台通讯缓冲；所有 ASI FB 实例 + `FB_ASI_ParameterControl` 必须 IN_OUT 传入同一实例。',
        'bErrornumber': 'ASI 主端子返回的命令专用错误码（DWORD）。具体值参见 KL6201 / EL6201 手册的 ASI master command error 表。0 = 无错。',
    },
    pitfalls=ASI_PITFALLS + [
        ('一次只能给一台未编址的 slave 编址：若总线上有多个地址 0 的 slave 同时上电，编址会失败或随机命中其中一台。**实际现场操作流程**：先单独接入一台新 slave 编址 → 断开 → 再接下一台。', True),
        ('编址成功后 slave 把新地址保存到自己 EEPROM，下次上电用新地址；不要反复编址（EEPROM 寿命）。', True),
    ],
    scenario='更换故障的 ASI 流量计：取下旧 slave（旧地址 5），装新 slave（出厂默认 0），用本 FB 把它从 0 编址为 5。这样工程程序的引用关系不变。',
    value='不必拆机柜插 ASI 编址手持工具——直接 PLC 程序 + HMI 按钮完成现场更换设备。',
    alt=(
        '- 手持 ASI 编址器：要拆下 slave 接到手持器上编址再装回，繁琐\n'
        '- **本 FB**：直接在线编址，机柜不动手'
    ),
    related=['FB_ASI_ParameterControl', 'FB_ASI_SlaveDiag', 'FB_ASI_ReadParameter'],
    xml_scen='线上替换故障 ASI 流量计：新设备出厂地址 0，需要在线把它编址为故障 slave 原来的地址 5。',
    xml_val='完全在 PLC 程序里完成现场设备替换，不用 ASI 手持工具。',
    xml_verify='登录前确认 stAsiInProcessImg / stAsiOutProcessImg 已链到 ASI 主端子；fbAsiParamControl 已加入 PlcTask 循环；在线写 iCurrentAddr := 0、iAddressToAssign := 5、bStartAddressing := TRUE → fbAsiAddressing.bBusy 短暂 TRUE → 回 FALSE 后看 fbAsiAddressing.bErr：FALSE 表示编址成功；用 FB_ASI_SlaveDiag 在地址 5 上读应能查到该 slave。',
    xml_vars=[
        ('fbAsiAddressing', 'FB_ASI_Addressing', None, 'ASI 编址 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, 'ASI 后台调度 FB（必须循环调用）'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '所有 ASI FB 共享的后台缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, 'ASI 主端子输入过程数据（链到 %I*）'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, 'ASI 主端子输出过程数据（链到 %Q*）'),
        ('iCurrentAddr', 'BYTE', '0', '当前地址（新出厂默认 0）'),
        ('iAddressToAssign', 'BYTE', '5', '要分配的新地址'),
        ('bStartAddressing', 'BOOL', 'FALSE', '上升沿触发一次编址'),
    ],
    xml_call=(
        '// 后台调度 FB 必须每周期调用 — 这是所有 ASI FB 工作的前提\n'
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        '// 单次调用形式：bStartAddressing 上升沿触发\n'
        'fbAsiAddressing(\n'
        '    iOldAddress       := iCurrentAddr,\n'
        '    iNewAddress       := iAddressToAssign,\n'
        '    bStart            := bStartAddressing,\n'
        '    stParameterBuffer := stAsiParamBuffer\n'
        ');\n'
    ),
)


REG['FB_ASI_SlaveDiag'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AS-Interface slave 周期诊断。读取指定 slave 的错误 / 超时计数器（物理错、超时、应答、退出数据交换、数据交换失败），或读取整个 ASI 总线的"已识别 slave 列表 (LES)" / "已激活 slave 列表 (LAS)"。'
        '通过 `bCycleMode` 控制单次读或连续读。'
    ),
    behavior=(
        '`bStart` 上升沿触发一次诊断命令；命令类型由其它输入位决定：'
        '`iCounter` ∈ {1..5} 表示读哪一种计数器（1: PhysicalFault, 2: Timeout, 3: Response, 4: LeaveDataExch, 5: DataExchFailed）；'
        '`bReadLES` = TRUE 时读 LES（List of Existing Slaves，已识别 slave 位图）；'
        '`bReadLAS` = TRUE 时读 LAS（List of Activated Slaves，已激活 slave 位图）。'
        '`bCycleMode = TRUE` 时持续读，`bBusy` 仅在 `bStart` 撤销后才落回；常用于看板循环刷新计数器；'
        '`bCycleMode = FALSE` 时单次读，命令完成 `bBusy` 落回。'
        '计数器值通过 `iCounterValue` 输出；位图通过 `iSlaveList`（DWORD = 32 bit 位图）输出。'
        '**`bCounterReset` 在 PDF 描述列出现但不在 VAR_INPUT 中**——是 PDF 列名混淆，不要使用，请用 `FB_ASI_WriteParameter` 实现复位。'
    ),
    var_desc={
        'iSlaveaddress': '目标 slave 地址 (1..31 标准 / A/B 扩展 0..62)。',
        'iCounter': '诊断计数器选择：1 = PhysicalFaultCounter（物理层错误），2 = TimeoutCounter（超时），3 = ResponseCounter（应答），4 = Leave-DataExchCounter（退出数据交换），5 = DataExch-FailedCounter（数据交换失败）。',
        'bReadLES': 'TRUE = 读 LES (List of Existing Slaves)，返回总线上识别到的 slave 位图。',
        'bReadLAS': 'TRUE = 读 LAS (List of Activated Slaves)，返回当前激活通讯的 slave 位图。',
        'bCyleMode': '`bCycleMode`（PDF 拼写错误为 `bCyleMode`）：0 = 单次读，1 = 连续读（`bBusy` 仅在 `bStart` 回 FALSE 后才落回）。',
        'iCounterValue': '当前所选 slave 的计数器值（仅当 `iCounter` ≠ 0 时有效）。',
        'iSlaveList': '所有 slave 的 LES / LAS 位图（DWORD，每个 bit 对应一个 slave 地址）。',
    },
    pitfalls=ASI_PITFALLS + [
        ('**`bCyleMode` 是 PDF 拼写错误**（应为 `bCycleMode`）；调用时用 PDF 写的名字 `bCyleMode` 才能通过编译。', True),
        ('PDF 描述里出现 `bCounterReset` 字段但 VAR_INPUT 中**没有**此字段，是 PDF 文档错误；本 FB 不支持复位计数器。', True),
        ('`iSlaveList` 是 DWORD 位图，bit N 对应 slave N（注意 ASI 标准地址 1..31，bit 0 通常保留 / 不使用）。', True),
    ],
    scenario='ASI 总线长期运行：周期读 slave 12 的 PhysicalFaultCounter 监控物理层抖动，超过阈值报警；同时读 LAS 看是否所有期望 slave 还在数据交换。',
    value='把 ASI 主端子的诊断字段做成可程序化访问，便于 SCADA 趋势曲线与报警。',
    alt=(
        '- 直接读 ASI 主端子寄存器：底层繁琐\n'
        '- 用专门的 ASI 诊断工具：在线但无法接 PLC\n'
        '- **本 FB**：标准方式'
    ),
    related=['FB_ASI_ParameterControl', 'FB_ASI_Addressing', 'FB_ASI_ReadParameter'],
    xml_scen='ASI 总线下挂 8 台 slave，运维要求 PLC 周期读 slave 5 的物理错计数器，超过 100 时报警；并定期读 LAS 确认所有 slave 在通讯。',
    xml_val='让 SCADA 能拿到 ASI 主端子的内部诊断字段，做趋势 + 报警。',
    xml_verify='登录后 iTargetAsiSlaveAddr := 5、iSelectedCounterType := 1（物理错计数器）、bEnableCyclicRead := TRUE（连续读模式）、bStartDiag := TRUE，观察 iLatestCounterValue 实时刷新；切 bReadActivatedList := TRUE、bReadIdentifiedList := FALSE 时 iActiveSlaveBitmap 显示当前激活 slave 位图。',
    xml_vars=[
        ('fbAsiSlaveDiag', 'FB_ASI_SlaveDiag', None, 'ASI slave 诊断 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, '后台调度（必须循环调用）'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '共享缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, '链到 %I*'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, '链到 %Q*'),
        ('iTargetAsiSlaveAddr', 'BYTE', '5', '目标 slave 地址'),
        ('iSelectedCounterType', 'INT', '1', '1=PhysicalFault 2=Timeout 3=Response 4=LeaveDX 5=DXFailed'),
        ('bReadIdentifiedList', 'BOOL', 'FALSE', '读 LES'),
        ('bReadActivatedList', 'BOOL', 'TRUE', '读 LAS'),
        ('bEnableCyclicRead', 'BOOL', 'TRUE', '0=单次读 1=连续读 (PDF: bCyleMode)'),
        ('bStartDiag', 'BOOL', 'FALSE', '上升沿触发'),
        ('iLatestCounterValue', 'WORD', None, '最新计数器值'),
        ('iActiveSlaveBitmap', 'DWORD', None, 'LES / LAS 位图'),
        ('nAsiCmdError', 'DWORD', None, 'ASI 主端子错误号'),
    ],
    xml_call=(
        '// 后台调度必须循环调用\n'
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        '// PDF VAR 名是 bCyleMode（拼写错误），保持原名调用\n'
        'fbAsiSlaveDiag(\n'
        '    iSlaveaddress     := iTargetAsiSlaveAddr,\n'
        '    iCounter          := iSelectedCounterType,\n'
        '    bReadLES          := bReadIdentifiedList,\n'
        '    bReadLAS          := bReadActivatedList,\n'
        '    bCyleMode         := bEnableCyclicRead,\n'
        '    bStart            := bStartDiag,\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    iCounterValue     => iLatestCounterValue,\n'
        '    iErrornumber      => nAsiCmdError,\n'
        '    iSlaveList        => iActiveSlaveBitmap\n'
        ');\n'
    ),
)


REG['FB_ASI_ReadParameter'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '读取 AS-Interface slave 的参数值（4 bit 参数槽位）。常用于读 slave 配置参数（如传感器灵敏度档位）。'
        '支持单次读或周期读 (`bCycleMode = 1`)。'
    ),
    behavior=(
        '`bStart` 上升沿触发：FB 把"读参数"命令放入 `stParameterBuffer`，'
        '`FB_ASI_ParameterControl` 在每个 PLC 周期把缓冲里的命令取走、经 ASI 主端子的过程数据发到目标 slave。'
        '`bCycleMode = 1` (Cyclic) 时持续读，`bBusy` 仅在 `bStart` 回 FALSE 后才落回；'
        '`bCycleMode = 0` (Acyclic) 时单次读完即停，`bBusy` 自动落回。'
        'ASI 标准 slave 的参数是 4 bit，所以 `iParameterReadvalue : BYTE` 实际只用低 4 bit。'
        '出错时 `bErr := TRUE`、`iErrornumber` 给出 ASI 主端子的命令错误号；具体错误码表见 KL6201 / EL6201 手册。'
    ),
    var_desc={
        'iParameternumber': 'ASI 参数编号（slave 内部参数索引）。具体含义因 slave 而异，参见各 slave 手册。',
        'bCycleMode': '0 = 单次读（Acyclic），1 = 连续读（Cyclic，`bBusy` 仅在 `bStart` 回 FALSE 后落回）。',
        'bStart': '上升沿触发一次读命令。',
        'iParameterReadvalue': '读得的 ASI slave 参数值（实际只用低 4 bit）。',
    },
    pitfalls=ASI_PITFALLS + [
        ('ASI slave 参数槽是 4 bit；返回 BYTE 但只低 4 bit 有效。', True),
        ('参数编号含义因 slave 厂家不同，请查 slave 手册。', True),
    ],
    scenario='读 ASI 光电传感器 slave 12 的灵敏度档位（参数 0），用于 HMI 显示当前传感器配置。',
    value='把 ASI 参数读做成程序接口，避免反复用 ASI 配置工具。',
    alt=(
        '- ASI 配置工具：手动\n'
        '- 直接读 ASI 主端子寄存器：底层繁琐\n'
        '- **本 FB**：标准'
    ),
    related=['FB_ASI_WriteParameter', 'FB_ASI_ParameterControl', 'FB_ASI_SlaveDiag'],
    xml_scen='HMI 显示 ASI 传感器 slave 12 的灵敏度档位（4 bit 参数）。',
    xml_val='参数显示可读化。',
    xml_verify='登录后 iTargetParamNumber := 0、bEnableCyclicRead := FALSE、bStartReadParam := TRUE → fbAsiReadParam.bBusy 短暂 TRUE → 回 FALSE 后 iParamValueReadback 显示该 slave 参数（低 4 bit 有效）。',
    xml_vars=[
        ('fbAsiReadParam', 'FB_ASI_ReadParameter', None, 'ASI slave 参数读 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, '后台调度'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '共享缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, '链到 %I*'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, '链到 %Q*'),
        ('iTargetParamNumber', 'WORD', '0', '要读的参数编号'),
        ('bEnableCyclicRead', 'BOOL', 'FALSE', '0=单次 1=循环'),
        ('bStartReadParam', 'BOOL', 'FALSE', '上升沿触发'),
        ('iParamValueReadback', 'BYTE', None, '读得的参数值（低 4 bit）'),
        ('nAsiCmdError', 'DWORD', None, 'ASI 错误号'),
    ],
    xml_call=(
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        'fbAsiReadParam(\n'
        '    iParameternumber    := iTargetParamNumber,\n'
        '    bCycleMode          := bEnableCyclicRead,\n'
        '    bStart              := bStartReadParam,\n'
        '    stParameterBuffer   := stAsiParamBuffer,\n'
        '    iParameterReadvalue => iParamValueReadback,\n'
        '    iErrornumber        => nAsiCmdError\n'
        ');\n'
    ),
)


REG['FB_ASI_WriteParameter'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '写 AS-Interface slave 的参数槽（4 bit）。常用于改变 slave 配置（如改变光电传感器的输出极性 / 灵敏度档位）。'
    ),
    behavior=(
        '`bStart` 上升沿触发一次写参数命令：FB 把"写参数"命令排到 `stParameterBuffer`，'
        '`FB_ASI_ParameterControl` 在下一个周期取走经 ASI 主端子的过程数据下发到目标 slave。'
        '`bBusy := TRUE` 直到命令被 ASI 主端子接受（这只是"接受"，不代表 slave 已经把参数烧进 EEPROM）。'
        '完成后 `bBusy := FALSE`；slave 把新参数保存到自己 EEPROM（部分新型 slave 也支持只写 RAM 而不写 EEPROM）。'
        '`iParametervalue` 是 DWORD 但 ASI 标准只用低 4 bit。'
        '错误时 `bErr := TRUE`、`bErrornumber` 给出 ASI 主端子的命令错误号（参见 KL6201 / EL6201 手册）。'
    ),
    var_desc={
        'iParameternumber': 'ASI 参数编号（slave 内部参数索引）。',
        'iParametervalue': '要写入的参数值（DWORD，但 ASI 标准只用低 4 bit）。',
        'bStart': '上升沿触发一次写命令。',
        'bErrornumber': 'ASI 主端子返回的命令专用错误码（DWORD）。',
    },
    pitfalls=ASI_PITFALLS + [
        ('参数写入会保存到 slave EEPROM，**不要循环写**（EEPROM 寿命）。', False),
        ('改某些参数后 slave 行为可能立刻变化（例如输出极性反转）；写之前确保下游设备做好准备。', True),
    ],
    scenario='ASI 光电传感器 slave 5 的输出极性需要在调试期间在线翻转：改参数 1 即可。比拆下来在传感器上拨码开关方便。',
    value='免拆装在线改 slave 配置。',
    alt=(
        '- 拨码 / 旋钮：要拆\n'
        '- ASI 配置工具：在线但要带工具\n'
        '- **本 FB**：PLC 程序内即可'
    ),
    related=['FB_ASI_ReadParameter', 'FB_ASI_ParameterControl', 'FB_ASI_Addressing'],
    xml_scen='ASI 光电传感器 slave 5 调试期间需要在线翻转输出极性（写参数 1 = 1）。',
    xml_val='不拆机柜改 slave 配置。',
    xml_verify='登录后 iTargetParamNumber := 1、iNewParamValue := 1（翻转极性）、bStartWriteParam := TRUE → fbAsiWriteParam.bBusy 短暂 TRUE → 回 FALSE 后 nAsiCmdError = 0 表示写入成功；再用 FB_ASI_ReadParameter 读回该参数应为 1。',
    xml_vars=[
        ('fbAsiWriteParam', 'FB_ASI_WriteParameter', None, 'ASI slave 参数写 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, '后台调度'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '共享缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, '链到 %I*'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, '链到 %Q*'),
        ('iTargetParamNumber', 'WORD', '1', '要写的参数编号'),
        ('iNewParamValue', 'DWORD', '1', '新参数值（低 4 bit）'),
        ('bStartWriteParam', 'BOOL', 'FALSE', '上升沿触发'),
        ('nAsiCmdError', 'DWORD', None, '错误号'),
    ],
    xml_call=(
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        'fbAsiWriteParam(\n'
        '    iParameternumber  := iTargetParamNumber,\n'
        '    iParametervalue   := iNewParamValue,\n'
        '    bStart            := bStartWriteParam,\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    bErrornumber      => nAsiCmdError\n'
        ');\n'
    ),
)


REG['FB_ASI_Processdata_digital'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '读 / 写 AS-Interface slave 的数字过程数据（4 bit 数据槽）。'
        '支持单次 / 连续模式、读 / 写选择、屏蔽访问 (`bmaskAccess`)。'
        '可作通用 ASI 数字 IO 访问入口，比把 slave 数据直接链到 PLC 任务输入 / 输出更灵活（按需访问）。'
    ),
    behavior=(
        '`bStart` 上升沿触发一次过程数据访问命令，FB 把命令排入 `stParameterBuffer` 让后台调度器送到 ASI 主端子。'
        '`bParametermode = 0` 表示读，`= 1` 表示写；`bCycleMode = 0` 表示单次操作，`= 1` 表示连续操作。'
        '`bCommMode` 与 `bRegComm` 在当前固件中 **必须保持 0**（PDF 备注：currently always 0），用于保留未来扩展。'
        '`bmaskAccess = 1` 走屏蔽访问模式，仅在某些扩展 slave 上有意义；普通 slave 保持 0。'
        '`iSlavevalue` 是写入数据（4 bit），`iReadValue` 是读出数据，`iParametergroup` 输出当前 slave 的参数分组信息。'
        '完成后 `bBusy := FALSE`；出错 `bErr := TRUE`、`iErrornumber` 给出 ASI 命令错误码。'
    ),
    var_desc={
        'iSlaveaddress': 'slave 地址。',
        'iSlavevalue': '写入 slave 的数字数据（4 bit）。',
        'bParametermode': '0 = 读，1 = 写。',
        'bCycleMode': '0 = 单次，1 = 连续（`bBusy` 仅在 `bStart` 撤销后落回）。',
        'bCommMode': 'PDF: currently always 0（保留为未来扩展，当前固件不可改）。',
        'bRegComm': 'PDF: currently always 0（同上，保留）。',
        'bmaskAccess': '0 = 普通访问，1 = 屏蔽访问（部分扩展 slave 用）。',
        'bStart': '上升沿触发一次访问。',
        'iReadValue': '读出的 slave 数据。',
        'iParametergroup': '当前 slave 的参数分组信息（WORD）。',
    },
    pitfalls=ASI_PITFALLS + [
        ('`bCommMode` / `bRegComm` **当前固件版本必须保持 0**，写其它值未定义。', True),
        ('循环模式 `bCycleMode = 1` 会占用大量 ASI 主端子调度时间，不建议同时对多个 slave 启用循环模式。', True),
    ],
    scenario='ASI 数字 IO slave 7 上挂 4 个数字按钮，需要在 PLC 程序里按需读取；用本 FB 比把数据链到 %I* 更灵活。',
    value='按需读写 ASI 数字数据，节省过程映像。',
    alt=(
        '- 链到 %I* / %Q*：永远刷新但占过程映像\n'
        '- **本 FB**：按需读写'
    ),
    related=['FB_ASI_ReadParameter', 'FB_ASI_ParameterControl', 'FB_ReadInput_analog'],
    xml_scen='ASI slave 7 是 4 路数字输入；按需读取这 4 个状态而不占用永久过程映像。',
    xml_val='节省 PLC 过程映像；按需访问。',
    xml_verify='登录后 iTargetAsiSlaveAddr := 7、bIsWriteMode := FALSE、bEnableCyclicMode := FALSE、bStartTransfer := TRUE → 回 FALSE 后 iReadbackDataNibble 显示该 slave 4 个数字输入状态（低 4 bit）。',
    xml_vars=[
        ('fbAsiProcessDataDigital', 'FB_ASI_Processdata_digital', None, 'ASI 数字过程数据 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, '后台调度'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '共享缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, '链到 %I*'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, '链到 %Q*'),
        ('iTargetAsiSlaveAddr', 'BYTE', '7', 'slave 地址'),
        ('iValueToWrite', 'WORD', '0', '写入数据（4 bit 有效）'),
        ('bIsWriteMode', 'BOOL', 'FALSE', '0=读 1=写'),
        ('bEnableCyclicMode', 'BOOL', 'FALSE', '0=单次 1=连续'),
        ('bMaskedAccess', 'BOOL', 'FALSE', '0=普通 1=屏蔽访问'),
        ('bStartTransfer', 'BOOL', 'FALSE', '上升沿触发'),
        ('iReadbackDataNibble', 'WORD', None, '读得数据'),
        ('iParamGroupInfo', 'WORD', None, '参数分组'),
        ('nAsiCmdError', 'DWORD', None, '错误号'),
    ],
    xml_call=(
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        '// bCommMode 与 bRegComm 在当前固件中必须保持 FALSE（PDF: currently always 0）\n'
        'fbAsiProcessDataDigital(\n'
        '    iSlaveaddress     := iTargetAsiSlaveAddr,\n'
        '    iSlavevalue       := iValueToWrite,\n'
        '    bParametermode    := bIsWriteMode,\n'
        '    bCycleMode        := bEnableCyclicMode,\n'
        '    bCommMode         := FALSE,\n'
        '    bRegComm          := FALSE,\n'
        '    bmaskAccess       := bMaskedAccess,\n'
        '    bStart            := bStartTransfer,\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    iReadValue        => iReadbackDataNibble,\n'
        '    iParametergroup   => iParamGroupInfo,\n'
        '    iErrornumber      => nAsiCmdError\n'
        ');\n'
    ),
)


REG['FB_ASI_ParameterControl'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '所有 ASI FB 的后台通讯调度器。必须循环调用（每个 PLC 周期一次）。'
        '它从共享的 `stParameterBuffer` 取出待执行命令、调度到 ASI 主端子的过程数据（`stParameter_IN` / `stParameter_OUT`）发送、把响应填回缓冲。'
        '没有本 FB 在 task 里跑，其它 ASI FB 全部不工作。'
    ),
    behavior=(
        '每次任务周期被调用：'
        '① 看 `stParameterBuffer` 里是否有挂起的 ASI 命令（来自其它 ASI FB）；'
        '② 有则把命令写到 `stParameter_OUT`（ASI 主端子下行过程数据）；'
        '③ 读 `stParameter_IN`（ASI 主端子上行过程数据）拿到响应；'
        '④ 把响应回填到 `stParameterBuffer`，让发起命令的 ASI FB 在下一个周期读到 `bBusy = FALSE`。'
        '**调用契约**：放在 PlcTask 循环最末或最前，**每周期调一次**，所有 ASI FB 实例必须传同一个 `stParameterBuffer`。'
    ),
    var_desc={
        'stParameter_IN': 'ASI 主端子（KL6201 / EL6201）输入过程数据；用 `AT %I*` 链到 System Manager。',
        'stParameter_OUT': 'ASI 主端子（KL6201 / EL6201）输出过程数据；用 `AT %Q*` 链到 System Manager。',
    },
    pitfalls=ASI_PITFALLS + [
        ('**这是 ASI 库的中枢，必须每个 PLC 周期循环调用**，否则所有 ASI 操作都卡住在 `bBusy = TRUE`。', False),
        ('多个 ASI 主端子时（极少见但有）需要为每个端子分别实例化本 FB + 独立的 `stParameterBuffer`，不能共用。', True),
    ],
    scenario='任何使用 ASI 的工程：本 FB 是整个 ASI 库的中枢，必须循环调用一次。',
    value='把 ASI 通讯调度集中到一个 FB 实例，业务侧只需调用 `FB_ASI_*` 系列即可异步发命令。',
    alt=(
        '- 不调用：所有 ASI FB 都卡住\n'
        '- **本 FB**：必须有'
    ),
    related=['FB_ASI_Addressing', 'FB_ASI_SlaveDiag', 'FB_ASI_ReadParameter'],
    xml_scen='任何用 ASI 库的程序：本 FB 是后台调度器，整个程序周期调用一次让其它 ASI FB 工作。',
    xml_val='调度集中化，业务侧异步用命令式 API。',
    xml_verify='登录后只要 PlcTask 在跑就会调用本 FB；可观察 stAsiParamBuffer 的内部字段（vendor-specific）周期更新；如果调用其它 ASI FB 时永远停在 bBusy = TRUE，多半是本 FB 没循环调用。',
    xml_vars=[
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, 'ASI 库后台调度器（必须循环调用）'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '所有 ASI FB 共享的缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, 'ASI 主端子过程输入（链到 %I*）'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, 'ASI 主端子过程输出（链到 %Q*）'),
    ],
    xml_call=(
        '// 这一个 FB 是 ASI 库的中枢。\n'
        '// 必须放在 PlcTask 主循环中、每个周期都调用一次。\n'
        '// 没有它，其它任何 FB_ASI_* 实例都不会工作（永远卡在 bBusy = TRUE）。\n'
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
    ),
)


REG['FB_ReadInput_analog'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '读取 AS-Interface 模拟量 slave 的某通道值。'
        '常用于 ASI 模拟传感器（如温度 / 压力变送器）的现场总线接入。'
        '通过 `bValid` 表示读到的值是否有效（slave 是否在线、是否已采样），`bOverflow` 表示是否超量程。'
    ),
    behavior=(
        '`bStart` 上升沿触发一次读取命令：FB 把"读模拟通道"命令排入 `stParameterBuffer`，'
        '`FB_ASI_ParameterControl` 在后台调度到 ASI 主端子，按 ASI 模拟 profile 经过几个 ASI 周期完成采样并回报。'
        '完成后 `iReadValue` 含 16 bit 模拟值（具体单位 / 量程由 slave 手册决定）。'
        '`bValid = TRUE` 表示该 slave 在线且通道有有效采样，业务侧应先判 `bValid` 再用 `iReadValue`，否则可能读到旧值或未初始化值。'
        '`bOverflow = TRUE` 表示 slave 报告的 over-range 超量程标志。'
        '`bCycleMode = 1` 模式下循环读，常用于把传感器数据周期性更新到 HMI。'
        '出错时 `bErr := TRUE`、`iErrornumber` 给出 ASI 命令错误码。'
    ),
    var_desc={
        'iSlaveaddress': '目标 ASI 模拟量 slave 地址。',
        'iChannel': '通道号（多通道 slave 用 0..3 等）。',
        'bCycleMode': '0 = 单次，1 = 连续读。',
        'bStart': '上升沿触发。',
        'bValid': 'TRUE = 读到的 `iReadValue` 有效（slave 在线 + 已采样）；FALSE = 数据未就绪 / slave 离线。',
        'bOverflow': 'TRUE = slave 报告 over-range（超量程）。',
        'iReadValue': '模拟值（16 bit；具体单位 / 量程由 slave 手册决定）。',
    },
    pitfalls=ASI_PITFALLS + [
        ('**`bValid` 是真伪标志**，业务侧必须先判 `bValid` 再用 `iReadValue`，否则读到旧值。', True),
        ('ASI 模拟传输使用专门的 ASI Analog Profile，slave 必须支持；普通数字 slave 不能用本 FB 读。', True),
    ],
    scenario='ASI 总线下挂温度变送器 slave 14（通道 0 是温度），周期读取送到 HMI 显示。',
    value='ASI 模拟量访问标准方式；自带 `bValid` / `bOverflow` 让数据可信度可判。',
    alt=(
        '- 直接读 ASI 主端子原始字：底层繁琐\n'
        '- **本 FB**：标准入口'
    ),
    related=['FB_WriteOutput_analog', 'FB_ASI_ParameterControl', 'FB_ASI_Processdata_digital'],
    xml_scen='ASI slave 14 是温度变送器，通道 0 是温度，HMI 显示需要循环读。',
    xml_val='把 ASI 模拟值做成可读的 PLC 变量。',
    xml_verify='登录后 iAsiAnalogSlaveAddr := 14、iAnalogChannelNo := 0、bEnableCyclicRead := TRUE、bStartAnalogRead := TRUE → bAnalogValueValid 在 slave 在线时应为 TRUE，iAnalogReadValue 实时显示传感器值；断开 slave 模拟 → bAnalogValueValid 落到 FALSE。',
    xml_vars=[
        ('fbAsiAnalogRead', 'FB_ReadInput_analog', None, 'ASI 模拟输入 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, '后台调度'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '共享缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, '链到 %I*'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, '链到 %Q*'),
        ('iAsiAnalogSlaveAddr', 'BYTE', '14', '目标 slave 地址'),
        ('iAnalogChannelNo', 'BYTE', '0', '通道号'),
        ('bEnableCyclicRead', 'BOOL', 'TRUE', '0=单次 1=循环'),
        ('bStartAnalogRead', 'BOOL', 'FALSE', '上升沿触发'),
        ('bAnalogValueValid', 'BOOL', None, '读得值是否有效'),
        ('bOverRangeFlag', 'BOOL', None, '超量程标志'),
        ('iAnalogReadValue', 'WORD', None, '模拟读值'),
        ('nAsiCmdError', 'DWORD', None, '错误号'),
    ],
    xml_call=(
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        'fbAsiAnalogRead(\n'
        '    iSlaveaddress     := iAsiAnalogSlaveAddr,\n'
        '    iChannel          := iAnalogChannelNo,\n'
        '    bCycleMode        := bEnableCyclicRead,\n'
        '    bStart            := bStartAnalogRead,\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    bValid            => bAnalogValueValid,\n'
        '    bOverflow         => bOverRangeFlag,\n'
        '    iReadValue        => iAnalogReadValue,\n'
        '    iErrornumber      => nAsiCmdError\n'
        ');\n'
    ),
)


REG['FB_WriteOutput_analog'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '写 AS-Interface 模拟量 slave 的某通道输出值（如 ASI 模拟阀位 / 模拟显示器）。'
        '与 `FB_ReadInput_analog` 配套。'
    ),
    behavior=(
        '`bStart` 上升沿触发一次写命令：FB 把"写模拟通道"命令排入 `stParameterBuffer`，'
        '`FB_ASI_ParameterControl` 在后台调度经 ASI 主端子下发到目标 slave。'
        '`bCycleMode = 1` 模式下持续写（连续刷新输出值），常用于把 PID 输出实时送给 ASI 调节阀。'
        '在 `bCycleMode = 1` 时业务侧改 `iSlavevalue` 后大约 1-2 个 ASI 周期反映到 slave 实际输出。'
        '`bCycleMode = 0` 单次模式下命令执行完 `bBusy` 自动落回。'
        '出错时 `bErr := TRUE`、`bErrornumber` 给出 ASI 命令错误码（参见 KL6201 / EL6201 手册）。'
    ),
    var_desc={
        'iSlaveaddress': 'slave 地址。',
        'iChannel': '通道号。',
        'iSlavevalue': '要写入的模拟值（16 bit）。',
        'bCycleMode': '0 = 单次，1 = 连续刷新。',
        'bStart': '上升沿触发。',
    },
    pitfalls=ASI_PITFALLS + [
        ('连续模式下输出值改变会异步刷出去，业务侧改 `iSlavevalue` 后大约 1-2 个 ASI 周期反映到 slave。', True),
    ],
    scenario='ASI 调节阀 slave 18（通道 0 控制阀位 0-100%），由 PID 输出连续写入。',
    value='ASI 模拟输出标准方式。',
    alt=(
        '- 直接写 ASI 主端子原始字：底层繁琐\n'
        '- **本 FB**：标准'
    ),
    related=['FB_ReadInput_analog', 'FB_ASI_ParameterControl'],
    xml_scen='ASI 模拟调节阀 slave 18，通道 0 接收 0..32767 表示阀位 0-100%；PID 输出连续写入。',
    xml_val='与 PID 配套使用，构成闭环。',
    xml_verify='登录后 iAsiAnalogSlaveAddr := 18、iAnalogChannelNo := 0、iValveSetpoint := 16384（约 50%）、bEnableCyclicWrite := TRUE、bStartAnalogWrite := TRUE → 阀位应在 1-2 个 ASI 周期后变化到 50%；改 iValveSetpoint 看是否跟随。',
    xml_vars=[
        ('fbAsiAnalogWrite', 'FB_WriteOutput_analog', None, 'ASI 模拟输出 FB'),
        ('fbAsiParamControl', 'FB_ASI_ParameterControl', None, '后台调度'),
        ('stAsiParamBuffer', 'ST_ParameterBuffer', None, '共享缓冲'),
        ('stAsiInProcessImg', 'ST_Parameter_IN', None, '链到 %I*'),
        ('stAsiOutProcessImg', 'ST_Parameter_OUT', None, '链到 %Q*'),
        ('iAsiAnalogSlaveAddr', 'BYTE', '18', '目标 slave'),
        ('iAnalogChannelNo', 'BYTE', '0', '通道'),
        ('iValveSetpoint', 'WORD', '16384', '阀位设定值 0..32767'),
        ('bEnableCyclicWrite', 'BOOL', 'TRUE', '0=单次 1=循环'),
        ('bStartAnalogWrite', 'BOOL', 'FALSE', '上升沿触发'),
        ('nAsiCmdError', 'DWORD', None, '错误号'),
    ],
    xml_call=(
        'fbAsiParamControl(\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    stParameter_IN    := stAsiInProcessImg,\n'
        '    stParameter_OUT   := stAsiOutProcessImg\n'
        ');\n'
        '\n'
        'fbAsiAnalogWrite(\n'
        '    iSlaveaddress     := iAsiAnalogSlaveAddr,\n'
        '    iChannel          := iAnalogChannelNo,\n'
        '    iSlavevalue       := iValveSetpoint,\n'
        '    bCycleMode        := bEnableCyclicWrite,\n'
        '    bStart            := bStartAnalogWrite,\n'
        '    stParameterBuffer := stAsiParamBuffer,\n'
        '    bErrornumber      => nAsiCmdError\n'
        ');\n'
    ),
)


# ---------------- AX200x Profibus (5 FBs) ----------------

AX2000_PITFALLS = [
    ('AX2000 是 1990s-2000s 的 Kollmorgen 老型号伺服；现代工程基本用 AX5000 (EtherCAT) + Tc2/Tc3 NCI 替代。本系列 FB 仅用于维护老线。', False),
    ('**`stPZDIN` / `stPZDOUT` 必须链到 System Manager 中 AX2000 在 Profibus 上的 PZD（过程数据）映射区**，否则数据交换不通。', True),
    ('AX2000 通讯通过 Profibus FC310x / EL6731 主站；调用任何 AX2000 FB 前先确保 Profibus 主站本身已正常。', True),
    ('错误号 `iErrorId` 是 AX2000 驱动器返回的"驱动器错误号"，与 ADS 错误号无关。具体含义见 AX2000 / S300 手册的 Fault Code 表。', True),
]

REG['FB_AX2000_Parameter'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AX2000 Profibus 伺服驱动器的参数读 / 写功能块，使用 Profibus DP-V1 PKW 机制访问驱动器内部参数（如位置环增益、加减速时间、电流限）。'
        '注意：写参数改变运行模式时，必须把 `FB_AX2000_AXACT` 的 "STOP" 输入保持 TRUE。'
    ),
    behavior=(
        '`bStartRead` 上升沿触发一次读 PKW；`bStartWrite` 上升沿触发一次写 PKW。'
        '不要同时拉高两者，会冲突。'
        '`iPnu` 选择参数号（如 PNU 0x03A2 = velocity loop integral time）；'
        '`nAxis` 是双轴 / 三轴扩展时的轴号；'
        '`iLength` 区分 2 字节或 4 字节参数（按 PNU 列表决定）。'
        '`bBusy = TRUE` 直到驱动器应答；完成后 `iReadValue` 含读得的参数值（仅 `bStartRead` 路径）。'
        '出错时 `iErrorId` 给出 AX2000 驱动器错误号——这是 PROFIDRIVE 的 PKW 错误码体系，不是 ADS 错误号。'
        '`tTimeOut` 是 ADS 调用超时；PKW 本身在 Profibus 上需要多个 DP cycle 完成，超时建议 ≥ 2 秒。'
    ),
    var_desc={
        'iSlaveAddress': 'AX2000 在 Profibus 上的站地址。',
        'iPnu': 'PROFIDRIVE PKW 参数号（PNU）；可用值参见 AX2000 手册的 PKW 参数列表。',
        'nAxis': '轴号（多轴扩展用）。',
        'iLength': '参数长度（2 或 4 字节）。',
        'iSubIndex': 'PKW 子索引（数组型参数访问元素用）。',
        'iParameterValue': '要写入或读出的参数值。',
        'iFC310xDeviceId': 'Profibus 主站卡（FC310x）的 Device Id。',
        'bStartRead': '上升沿启动读 PKW。',
        'bStartWrite': '上升沿启动写 PKW；改运行模式时需 `FB_AX2000_AXACT.STOP = TRUE`。',
        'iReadValue': '读 PKW 返回的参数值。',
        'iErrorId': 'AX2000 驱动器 PKW 错误码（不是 ADS 错误号；具体见 AX2000 手册）。',
    },
    pitfalls=AX2000_PITFALLS + [
        ('改运行模式（如位置 → 速度）时必须先让 `FB_AX2000_AXACT.bStop = TRUE` 把驱动器停下，否则写参数被驱动器拒绝。', False),
        ('PKW 是慢速通道（DP 每个周期只能传一个参数读/写），不要循环周期读参数；上电时一次性配置即可。', True),
    ],
    scenario='AX2000 维护：上电时把当前位置环增益从默认值改为工程定制值（例如 PNU 0x03A2 = 30）。',
    value='让 PLC 程序在上电时把驱动器参数写到一致状态，替换工人手拨 Kollmorgen 调试软件。',
    alt=(
        '- Kollmorgen 调试软件 Drive.exe：能写但要插串口 / 工程模式\n'
        '- 改用现代 EL72xx + Tc2/Tc3 NCI：投资大但更可靠\n'
        '- **本 FB**：维护老线最现实做法'
    ),
    related=['FB_AX2000_AXACT', 'FB_AX2000_Reference', 'FB_AX200X_Profibus'],
    xml_scen='AX2000 老线伺服维护：上电时把位置环积分时间 (PNU 0x03A2) 写为工程定制值 30，避免每次重启都要拨调试软件。',
    xml_val='把驱动器关键参数纳入 PLC 程序版本控制；工程师不需要带笔记本到现场。',
    xml_verify='登录后 iAx2000SlaveStation := 5、iParamPnu := 16#03A2、iParamWriteVal := 30、bWritePkwReq := TRUE → 触发上升沿 → fbAx2000Param.bBusy 短暂 TRUE → 回 FALSE 后 iLastDriveError = 0 表示成功；再 bReadPkwReq 上升沿读回参数验证 iLastReadbackValue = 30。',
    xml_vars=[
        ('fbAx2000Param', 'FB_AX2000_Parameter', None, 'AX2000 PKW 参数访问 FB'),
        ('iAx2000SlaveStation', 'BYTE', '5', 'AX2000 Profibus 站号'),
        ('iParamPnu', 'WORD', '16#03A2', '参数号 PNU'),
        ('iAxisNumber', 'BYTE', '1', '轴号'),
        ('iParamByteLen', 'BYTE', '4', '参数字节长度 (2 或 4)'),
        ('iParamSubIdx', 'BYTE', '0', '子索引'),
        ('iParamWriteVal', 'DWORD', '30', '要写入的值'),
        ('iProfibusMasterDevId', 'WORD', '1', 'FC310x Device Id'),
        ('bReadPkwReq', 'BOOL', 'FALSE', '上升沿读 PKW'),
        ('bWritePkwReq', 'BOOL', 'FALSE', '上升沿写 PKW'),
        ('tPkwTimeout', 'TIME', 'T#2S', 'ADS 超时'),
        ('bPkwBusy', 'BOOL', None, '工作中'),
        ('iLastDriveError', 'DWORD', None, '驱动器错误号'),
        ('iLastReadbackValue', 'DINT', None, '读 PKW 返回值'),
    ],
    xml_call=(
        'fbAx2000Param(\n'
        '    iSlaveAddress   := iAx2000SlaveStation,\n'
        '    iPnu            := iParamPnu,\n'
        '    nAxis           := iAxisNumber,\n'
        '    iLength         := iParamByteLen,\n'
        '    iSubIndex       := iParamSubIdx,\n'
        '    iParameterValue := iParamWriteVal,\n'
        '    iFC310xDeviceId := iProfibusMasterDevId,\n'
        '    bStartRead      := bReadPkwReq,\n'
        '    bStartWrite     := bWritePkwReq,\n'
        '    tTimeOut        := tPkwTimeout,\n'
        '    bBusy           => bPkwBusy,\n'
        '    iErrorId        => iLastDriveError,\n'
        '    iReadValue      => iLastReadbackValue\n'
        ');\n'
    ),
)


REG['FB_AX2000_AXACT'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AX2000 Profibus 伺服轴动作命令 FB：启动 / 停止 / 短停 / 错误复位、设定速度 / 位置 / motion-task。'
        '**必须循环调用**（必须每个 PLC 周期调用一次，PDF 明确说明）。'
    ),
    behavior=(
        '本 FB 是 AX2000 的核心动作接口，必须循环调用让 PZD 过程数据保持实时刷新到驱动器。'
        '`bStart` 上升沿发动作命令；动作类型由其它输入位决定：'
        '`iVelocity` / `iPosition` 表示直接 motion 指令的速度与目标位置；'
        '`imotion_tasknumber` / `imotion_blocktype` 用于调驱动器内已存的 motion-task；'
        '`bStop` 上升沿正常停车并禁能；`bShortStop` 短停（保持使能）；`bErrorResume` 复位 AX2000 错误。'
        '`bBusy = TRUE` 直到驱动器接受命令；`bError` 表示驱动器报错（具体故障码不在本 FB 输出，需读驱动器 PNU）；`bTimeOutErr` 表示 PLC 与驱动器之间的 ADS / Profibus 超时。'
        '`stPZDIN` / `stPZDOUT` 是 IN_OUT 的 Profibus 过程数据结构，必须在 System Manager 中链到 AX2000 站的 PZD 区域，且每周期循环调用本 FB 才能让数据流动。'
    ),
    var_desc={
        'iVelocity': '目标速度（典型单位 μm/s 或者驱动器配置的工程单位）。',
        'iPosition': '目标位置（典型单位 μm 或度，依驱动器配置）。',
        'imotion_tasknumber': '驱动器内存里预存的 motion-task 块编号；若用直接指令则忽略。',
        'imotion_blocktype': 'motion-task 类型（位运算 flag，可选项参见 AX2000 手册）。',
        'bStart': '上升沿向驱动器发 start 命令。',
        'bStop': '上升沿正常停车，并把驱动器置 disable。',
        'bShortStop': '上升沿短停，但保持 enable。',
        'bErrorResume': '上升沿复位 AX2000 错误（不复位 PLC-Profibus 之间的 TimeOut 错）。',
        'stPZDIN': 'Profibus 过程数据：驱动器 → PLC 方向；链到 System Manager 中 AX2000 的 PZD IN 区。',
        'stPZDOUT': 'Profibus 过程数据：PLC → 驱动器方向；链到 System Manager 中 AX2000 的 PZD OUT 区。',
        'bError': 'TRUE = AX2000 驱动器报故障；具体故障号需读驱动器 PNU。',
        'bTimeOutErr': 'TRUE = PLC ↔ 驱动器之间的 ADS / Profibus 通讯超时。',
    },
    pitfalls=AX2000_PITFALLS + [
        ('**必须每周期循环调用**：本 FB 是 PZD 数据交换的载体，不调用驱动器会丢失通讯心跳进入超时故障。', False),
        ('改运行模式（如位置 ↔ 速度）必须先 `bStop` 让驱动器禁能，不能在运动中改。', False),
    ],
    scenario='AX2000 老线运动控制：印刷套筒定位伺服，上电后等位置就绪信号 → bStart 发位置指令到 12000 μm。',
    value='把 PROFIDRIVE 状态机 + PZD 编码全部封装；业务侧只关心 motion 指令。',
    alt=(
        '- 直接读写 PZD 字节：协议繁琐\n'
        '- 现代 NCI + EL72xx：投资大但更可靠\n'
        '- **本 FB**：维护老线必用'
    ),
    related=['FB_AX2000_Parameter', 'FB_AX2000_Reference', 'FB_AX200X_Profibus'],
    xml_scen='AX2000 印刷套筒伺服：上电后位置就绪即下发位置指令 12000 μm + 速度 1500 μm/s。',
    xml_val='封装 PROFIDRIVE 协议状态机，避免手撸 PZD 协议。',
    xml_verify='登录后 stAx2000PzdIn / stAx2000PzdOut 已链到 AX2000 PZD；在线写 bMotionStartReq := TRUE → fbAx2000Action.bBusy 短暂 TRUE → 驱动器开始定位；监视 stAx2000PzdIn 中位置实时反馈应趋向 iMotionTargetPosition。',
    xml_vars=[
        ('fbAx2000Action', 'FB_AX2000_AXACT', None, 'AX2000 动作 FB（必须循环调用）'),
        ('stAx2000PzdIn', 'ST_PZD_IN', None, '驱动器 → PLC PZD（链到 %I*）'),
        ('stAx2000PzdOut', 'ST_PZD_OUT', None, 'PLC → 驱动器 PZD（链到 %Q*）'),
        ('iTargetVelocity', 'DWORD', '1500', '目标速度 μm/s'),
        ('iMotionTargetPosition', 'DINT', '12000', '目标位置 μm'),
        ('iMotionTaskNum', 'WORD', '0', '存内 motion-task 号；0 表示用直接指令'),
        ('iMotionBlockType', 'WORD', '16#2000', 'motion-task 类型 (默认 SI 单位)'),
        ('bMotionStartReq', 'BOOL', 'FALSE', '上升沿启动 motion'),
        ('bMotionStopReq', 'BOOL', 'FALSE', '上升沿正常停车'),
        ('bMotionShortStopReq', 'BOOL', 'FALSE', '上升沿短停'),
        ('bMotionErrorReset', 'BOOL', 'FALSE', '上升沿复位 AX2000 错误'),
        ('tMotionTimeout', 'TIME', 'T#5S', 'PZD 通讯超时'),
        ('bMotionBusy', 'BOOL', None, '工作中'),
        ('bMotionErrFlag', 'BOOL', None, '驱动器故障'),
        ('bMotionTimeoutErrFlag', 'BOOL', None, '通讯超时'),
    ],
    xml_call=(
        '// 必须每周期循环调用以维持 PZD 通讯\n'
        'fbAx2000Action(\n'
        '    iVelocity          := iTargetVelocity,\n'
        '    iPosition          := iMotionTargetPosition,\n'
        '    imotion_tasknumber := iMotionTaskNum,\n'
        '    imotion_blocktype  := iMotionBlockType,\n'
        '    bStart             := bMotionStartReq,\n'
        '    bStop              := bMotionStopReq,\n'
        '    bShortStop         := bMotionShortStopReq,\n'
        '    bErrorResume       := bMotionErrorReset,\n'
        '    tTimeOut           := tMotionTimeout,\n'
        '    stPZDIN            := stAx2000PzdIn,\n'
        '    stPZDOUT           := stAx2000PzdOut,\n'
        '    bBusy              => bMotionBusy,\n'
        '    bError             => bMotionErrFlag,\n'
        '    bTimeOutErr        => bMotionTimeoutErrFlag\n'
        ');\n'
    ),
)


REG['FB_AX2000_JogMode'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AX2000 Profibus 伺服点动模式：以基础速度 (`iBasicVelo`) × 驱动器内部 v-jog mode 因子 持续运行。'
        '常用于调试期间手动移动轴。'
    ),
    behavior=(
        '`bStart` 上升沿启动点动；`bStop` 上升沿停止。'
        '点动期间通过 PZD 持续发送 jog 指令到驱动器；驱动器按 `iBasicVelo` × 内部 v-jog 因子计算实际速度。'
        '点动通常用于调试 / 维护，工程切换到自动后应该用 `FB_AX2000_AXACT`。'
        '`stPZDIN` / `stPZDOUT` IN_OUT 与 AXACT 一致：必须链到 PZD 区且循环调用。'
        '`bBusy` 表示命令处理中；`bErr` / `bTimeOutErr` 表示驱动器故障 / 通讯超时。'
    ),
    var_desc={
        'iBasicVelo': '基础速度（INT，单位由驱动器配置；最终速度 = iBasicVelo × v-jog factor）。',
        'bStart': '上升沿启动点动。',
        'bStop': '上升沿停止点动。',
    },
    pitfalls=AX2000_PITFALLS + [
        ('点动模式仅供调试，正常工艺要用 `FB_AX2000_AXACT` 的 motion-task 模式。', True),
        ('实际速度 = `iBasicVelo` × v-jog factor，因子需在驱动器里配置；不要把 `iBasicVelo` 想当然作物理速度。', True),
    ],
    scenario='AX2000 维护：把轴点动到机械零位附近，工人按 HMI 上的 jog+ / jog- 按钮。',
    value='不用拆驱动器接调试软件即可手动移动轴。',
    alt=(
        '- 用驱动器面板按钮：要打开机柜\n'
        '- Drive.exe 调试软件：要插串口 / 网线\n'
        '- **本 FB**：HMI 按钮即可'
    ),
    related=['FB_AX2000_AXACT', 'FB_AX2000_Reference', 'FB_AX2000_Parameter'],
    xml_scen='AX2000 调试期间通过 HMI 手动点动伺服轴，基础速度 100。',
    xml_val='调试人员不用打开柜门接调试软件。',
    xml_verify='登录后 stAx2000PzdIn / stAx2000PzdOut 已链到 PZD；按 bJogPositiveReq := TRUE → 轴开始正方向点动；松开 → 调 bJogStopReq := TRUE → 轴停止。',
    xml_vars=[
        ('fbAx2000Jog', 'FB_AX2000_JogMode', None, 'AX2000 点动 FB'),
        ('stAx2000PzdIn', 'ST_PZD_IN', None, 'PZD 输入'),
        ('stAx2000PzdOut', 'ST_PZD_OUT', None, 'PZD 输出'),
        ('iJogBasicSpeed', 'INT', '100', '点动基础速度'),
        ('bJogPositiveReq', 'BOOL', 'FALSE', 'HMI 按钮：点动正方向'),
        ('bJogStopReq', 'BOOL', 'FALSE', 'HMI 按钮：停点动'),
        ('tJogTimeout', 'TIME', 'T#5S', '超时'),
        ('bJogBusy', 'BOOL', None, '工作中'),
        ('bJogErrFlag', 'BOOL', None, '驱动器故障'),
        ('bJogTimeoutErrFlag', 'BOOL', None, '通讯超时'),
    ],
    xml_call=(
        '// 循环调用以维持 PZD 通讯\n'
        'fbAx2000Jog(\n'
        '    bStart      := bJogPositiveReq,\n'
        '    bStop       := bJogStopReq,\n'
        '    iBasicVelo  := iJogBasicSpeed,\n'
        '    tTimeOut    := tJogTimeout,\n'
        '    stPZDIN     := stAx2000PzdIn,\n'
        '    stPZDOUT    := stAx2000PzdOut,\n'
        '    bBusy       => bJogBusy,\n'
        '    bErr        => bJogErrFlag,\n'
        '    bTimeOutErr => bJogTimeoutErrFlag\n'
        ');\n'
    ),
)


REG['FB_AX2000_Reference'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AX2000 Profibus 伺服回参考 / 设定参考点 FB。'
        '可设定当前位置为参考点 (`bSetRefPoint`)，或启动 / 停止 homing 找参考点 (`bCalibrStart` / `bCalibrStop`)。'
    ),
    behavior=(
        '`bSetRefPoint` 上升沿 → 把当前位置标记为参考点（零位）。'
        '`bCalibrStart` 上升沿 → 启动 homing：驱动器按内部配置的 homing 方法（限位回、Z 脉冲、原点感应器等）找参考点；速度由 `iCalVelo` × v-jog factor 决定。'
        '`bCalibrStop` 上升沿 → 中止 homing。'
        '完成 / 出错通过 `bBusy` 落回 + `bErr` 反映。'
        '与其它 AX2000 FB 一样，本 FB 通过 PZD 与驱动器交换，因此 `stPZDIN` / `stPZDOUT` 必须链到 System Manager 的 PZD 区，且必须循环调用。'
    ),
    var_desc={
        'bSetRefPoint': '上升沿把当前位置设为参考点（零位）。',
        'bCalibrStart': '上升沿启动 homing 找参考点。',
        'bCalibrStop': '上升沿中止 homing。',
        'iCalVelo': 'homing 基础速度（最终速度 = iCalVelo × v-jog factor）。',
    },
    pitfalls=AX2000_PITFALLS + [
        ('homing 方法（用限位 / Z 脉冲 / 感应器）在驱动器侧配置，本 FB 不能切换方法。', True),
        ('homing 可能撞到机械限位；调试时务必先观察 limit switch 信号正确接入。', True),
    ],
    scenario='AX2000 印刷套筒维修后重新对零：先用 jog 移到接近原点 → `bCalibrStart` 让伺服找精确零位。',
    value='把 homing 流程做成程序接口，可在 HMI 一键触发。',
    alt=(
        '- 手动 jog + 看尺读数：人工操作易错\n'
        '- 驱动器面板 homing：要打开机柜\n'
        '- **本 FB**：HMI 触发'
    ),
    related=['FB_AX2000_AXACT', 'FB_AX2000_JogMode', 'FB_AX200X_Profibus'],
    xml_scen='维修后重新对零：HMI 按钮触发本 FB 启动 homing，伺服按机械原点感应器找零位。',
    xml_val='homing 程序化，工人按一键完成。',
    xml_verify='登录后 stAx2000PzdIn / stAx2000PzdOut 已链；在线写 bHomingStartReq := TRUE → fbAx2000Ref.bBusy 短暂 TRUE → 驱动器开始 homing → 找到零位后 bBusy 落回 FALSE，bHomingErrFlag = FALSE 表示成功。',
    xml_vars=[
        ('fbAx2000Ref', 'FB_AX2000_Reference', None, 'AX2000 回零 FB'),
        ('stAx2000PzdIn', 'ST_PZD_IN', None, 'PZD 输入'),
        ('stAx2000PzdOut', 'ST_PZD_OUT', None, 'PZD 输出'),
        ('bSetRefPointReq', 'BOOL', 'FALSE', 'HMI：设定当前为零位'),
        ('bHomingStartReq', 'BOOL', 'FALSE', 'HMI：启动 homing'),
        ('bHomingStopReq', 'BOOL', 'FALSE', 'HMI：停 homing'),
        ('iHomingVelocity', 'WORD', '50', 'homing 基础速度'),
        ('bHomingBusy', 'BOOL', None, '工作中'),
        ('bHomingErrFlag', 'BOOL', None, '驱动器故障'),
    ],
    xml_call=(
        'fbAx2000Ref(\n'
        '    bSetRefPoint := bSetRefPointReq,\n'
        '    bCalibrStart := bHomingStartReq,\n'
        '    bCalibrStop  := bHomingStopReq,\n'
        '    iCalVelo     := iHomingVelocity,\n'
        '    stPZDIN      := stAx2000PzdIn,\n'
        '    stPZDOUT     := stAx2000PzdOut,\n'
        '    bBusy        => bHomingBusy,\n'
        '    bErr         => bHomingErrFlag\n'
        ');\n'
    ),
)


REG['FB_AX200X_Profibus'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'AX2000 综合 FB：整合 AXACT + JogMode + Reference 的功能（不含参数读写）。'
        '所有 motion / jog / homing 的入口都在这里，按 `iRunningMode` 切换：0 = Digital speed，1 = Motiontask，2 = JogMode，3 = Calibration。'
    ),
    behavior=(
        '`bInit` 上升沿在驱动器内部置 operation mode 2（positioning）作为初始化。'
        '`iRunningMode` 切换当前动作类型：'
        '0 = Digital speed（用 `iDigitalSpeed` 直接给速度），'
        '1 = Motiontask（执行 `imotion_tasknumber` 内存中存的 motion 块），'
        '2 = JogMode（用 `iJogModeBasicValue` 点动），'
        '3 = Calibration（用 `iCalVelo` homing）。'
        '`bStart` / `bStop` / `bShortStop` / `bErrorResume` 与 AXACT 一致。'
        '`bMode_DigitalSpeed` 初始化时把驱动器置入 Digital speed 模式而非默认的 positioning 模式。'
        '本 FB 内部循环调用 AXACT/JogMode/Reference 的功能，外部只需要调本一个 FB。'
    ),
    var_desc={
        'bInit': '上升沿初始化驱动器到指定 operation mode。',
        'bMode_DigitalSpeed': '初始化时是否切到 Digital speed 模式（否则默认 positioning）。',
        'iDigitalSpeed': 'Digital speed 模式下的直接速度指令。',
        'iVelocity': 'Motiontask 模式下的运行速度。',
        'iPosition': 'Motiontask 模式下的目标位置。',
        'iRunningMode': '0=Digital speed, 1=Motiontask, 2=JogMode, 3=Calibration。',
        'iJogModeBasicValue': 'JogMode 基础速度。',
        'iCalVelo': 'Calibration (homing) 基础速度。',
        'bSetRefPoint': '上升沿设当前为参考点。',
    },
    pitfalls=AX2000_PITFALLS + [
        ('**本 FB 是综合接口，便于新工程使用**；维护时若发现某一动作有问题，可拆分调用单独的 AXACT/JogMode/Reference 来排查。', True),
        ('参数读写不在本 FB 内——需要 `FB_AX2000_Parameter` 配套。', True),
    ],
    scenario='AX2000 新接入工程：用一个 FB 涵盖 motion 全功能，业务程序按 iRunningMode 切动作类型。',
    value='单一接口，减少业务程序中维护多个 AX2000 FB 实例的复杂度。',
    alt=(
        '- 分别用 AXACT / JogMode / Reference 三个 FB：灵活但更多代码\n'
        '- **本 FB**：综合接口'
    ),
    related=['FB_AX2000_AXACT', 'FB_AX2000_JogMode', 'FB_AX2000_Reference', 'FB_AX2000_Parameter'],
    xml_scen='AX2000 综合控制：一个 FB 涵盖初始化 + jog + motion + homing。',
    xml_val='单一接口，业务代码简洁。',
    xml_verify='登录后 bDriveInitReq := TRUE 一次完成初始化；切 iRunMode := 1 (Motiontask) + bStartCmd := TRUE → 伺服按 iPositionTarget 定位。',
    xml_vars=[
        ('fbAx2000All', 'FB_AX200X_Profibus', None, 'AX2000 综合 FB'),
        ('stAx2000PzdIn', 'ST_PZD_IN', None, 'PZD 输入'),
        ('stAx2000PzdOut', 'ST_PZD_OUT', None, 'PZD 输出'),
        ('bDriveInitReq', 'BOOL', 'FALSE', '上升沿初始化'),
        ('bUseDigitalSpeedMode', 'BOOL', 'FALSE', '初始化为 Digital speed'),
        ('iDigitalSpeedCmd', 'DWORD', '0', 'Digital speed 指令'),
        ('iVelocityCmd', 'DWORD', '1500', 'Motion 速度'),
        ('iPositionTarget', 'DINT', '12000', '目标位置'),
        ('iRunMode', 'BYTE', '1', '0=DS 1=MT 2=Jog 3=Cal'),
        ('iMotionTaskNum', 'WORD', '0', 'motion-task 号'),
        ('iMotionBlockType', 'WORD', '16#2000', 'motion-task 类型'),
        ('iJogBaseVelo', 'INT', '100', 'Jog 基础速度'),
        ('iCalVelocity', 'WORD', '50', 'Homing 速度'),
        ('bSetRefPointReq', 'BOOL', 'FALSE', '设置零位'),
        ('bStartCmd', 'BOOL', 'FALSE', '上升沿启动'),
        ('bStopCmd', 'BOOL', 'FALSE', '上升沿停止'),
        ('bShortStopCmd', 'BOOL', 'FALSE', '短停'),
        ('iAx2000Station', 'BYTE', '5', 'AX2000 站号'),
        ('iFC310xDevId', 'WORD', '1', 'FC310x DeviceId'),
        ('bErrResumeReq', 'BOOL', 'FALSE', '复位错误'),
        ('tCmdTimeout', 'TIME', 'T#5S', '超时'),
    ],
    xml_call=(
        '// 必须循环调用维持 PZD 通讯\n'
        'fbAx2000All(\n'
        '    bInit              := bDriveInitReq,\n'
        '    bMode_DigitalSpeed := bUseDigitalSpeedMode,\n'
        '    iDigitalSpeed      := iDigitalSpeedCmd,\n'
        '    iVelocity          := iVelocityCmd,\n'
        '    iPosition          := iPositionTarget,\n'
        '    iRunningMode       := iRunMode,\n'
        '    imotion_tasknumber := iMotionTaskNum,\n'
        '    imotion_blocktype  := iMotionBlockType,\n'
        '    iJogModeBasicValue := iJogBaseVelo,\n'
        '    iCalVelo           := iCalVelocity,\n'
        '    bSetRefPoint       := bSetRefPointReq,\n'
        '    bStart             := bStartCmd,\n'
        '    bStop              := bStopCmd,\n'
        '    bShortStop         := bShortStopCmd,\n'
        '    iSlaveAddress      := iAx2000Station,\n'
        '    iFC310xDeviceId    := iFC310xDevId,\n'
        '    bErrorResume       := bErrResumeReq,\n'
        '    tTimeOut           := tCmdTimeout\n'
        ');\n'
    ),
)


# ---------------- Beckhoff Lightbus (3 FBs) ----------------

LB_PITFALLS = [
    ('Beckhoff Lightbus 是早期光纤总线，**TwinCAT 3 已不再支持** Lightbus 主站硬件（C1220 ISA / FC200x PCI）。PDF 明确说 "not supported by TwinCAT 3 at present"。', False),
    ('本系列 FB 仅供老工程升级到 TwinCAT 3 后做"代码兼容性参考"，**实际运行需要 TwinCAT 2 或更早**。', False),
    ('ADS 错误号见 Beckhoff **ADS Return Codes** 在线表；具体光纤错误码 PDF 未列入本节。', True),
]

REG['IOF_LB_BreakLocationTest'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'Beckhoff Lightbus（光纤总线）断纤定位测试。'
        '在光纤环里 walking 测试，若没有断纤则 `BOXNO` 返回当前环内模块总数；若有断纤则 `BREAK := TRUE` 且 `BOXNO` 返回断点前最后一个能通讯到的模块号。'
        '若 `BOXNO = 0xFF` 表示断点紧靠接收端，无法定位具体模块。'
    ),
    behavior=(
        '`START` 上升沿触发一次测试：`BUSY := TRUE`，FB 经 ADS 把 walking 测试命令发到 Lightbus 主站。'
        '主站在光纤环里按顺序探测每个模块的应答，直到无应答为止。'
        '完成后 `BUSY := FALSE`，结果：'
        '`BREAK = FALSE` 时 `BOXNO` = 环内模块总数（用于核对配置）；'
        '`BREAK = TRUE` 时 `BOXNO` = 断点前最后一个能通讯的模块号；若 `BOXNO = 0xFF` 表示接收端正面就断了。'
        'Lightbus 模块号是从发射器开始数 1, 2, ..., N。'
    ),
    var_desc={
        'BREAK': 'TRUE = 检测到断纤；FALSE = 光纤环正常。',
        'BOXNO': 'BREAK=FALSE 时是模块总数；BREAK=TRUE 时是断点前最后能通讯的模块号；0xFF 表示接收端直接断纤。',
    },
    pitfalls=LB_PITFALLS + [
        ('断纤定位是诊断功能，不要循环周期调用——会占用 Lightbus 主站带宽。', True),
        ('找到断点后 walking 测试会终止，需要修复光纤后再次调用本 FB 确认恢复。', True),
    ],
    scenario='Lightbus 老线突然报通讯故障：调本 FB 定位断点 → 现场顺着光纤数到第 N 个模块（BOXNO 值）附近检查。',
    value='避免逐段拔光纤排查；一次测试定位到具体模块附近。',
    alt=(
        '- 人工逐段排查：耗时\n'
        '- 用专门光纤测试仪：要带工具到现场\n'
        '- **本 FB**：PLC 程序触发即可'
    ),
    related=['IOF_LB_ParityCheck', 'IOF_LB_ParityCheckWithReset', 'IOF_DeviceReset'],
    xml_scen='Lightbus 通讯故障：HMI 按钮触发断纤定位，BOXNO 显示断点位置帮助现场人员快速找到问题模块。',
    xml_val='把断纤定位做成 HMI 一键操作。',
    xml_verify='登录后 nLightbusDeviceId := 系统中 Lightbus 主站 DeviceId；写 bStartBreakTest := TRUE → bBreakTestBusy 短暂 TRUE → 回 FALSE 后 bBreakDetected 表示是否有断纤；正常时 nLastModuleNo 应等于工程配置的 Lightbus 模块总数。',
    xml_vars=[
        ('fbLightbusBreakTest', 'IOF_LB_BreakLocationTest', None, 'Lightbus 断纤定位 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nLightbusDeviceId', 'UDINT', '1', 'Lightbus 主站 Device Id'),
        ('bStartBreakTest', 'BOOL', 'FALSE', '上升沿触发测试'),
        ('tBreakTestTimeout', 'TIME', 'T#10S', 'ADS 超时（光纤环大时给足）'),
        ('bBreakTestBusy', 'BOOL', None, '工作中'),
        ('bBreakTestErr', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
        ('bBreakDetected', 'BOOL', None, '断纤标志'),
        ('nLastModuleNo', 'WORD', None, '模块号 / 总数'),
    ],
    xml_call=(
        'fbLightbusBreakTest(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nLightbusDeviceId,\n'
        '    START    := bStartBreakTest,\n'
        '    TMOUT    := tBreakTestTimeout,\n'
        '    BUSY     => bBreakTestBusy,\n'
        '    ERR      => bBreakTestErr,\n'
        '    ERRID    => nLastErrCode,\n'
        '    BREAK    => bBreakDetected,\n'
        '    BOXNO    => nLastModuleNo\n'
        ');\n'
    ),
)


REG['IOF_LB_ParityCheck'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        'Beckhoff Lightbus 读取所有模块的奇偶错误计数器（每模块一个 8 bit 计数器，无溢出）。'
        '**不复位** 计数（如要复位见 `IOF_LB_ParityCheckWithReset`）。最多 256 个计数（即最多 256 模块）。'
    ),
    behavior=(
        '调用前用户准备一个 `ARRAY[1..N] OF BYTE` 缓冲区（N = 要读的模块数）并把 `DESTADDR := ADR(buffer)`、`LEN := N`。'
        '`START` 上升沿触发一次读：`BUSY := TRUE`，FB 经 ADS 把 N 个奇偶计数器读到缓冲区。'
        '完成后 `BUSY := FALSE`，`buffer[k]` = 模块 k 的奇偶错误累积值。'
        '由于计数器不溢出，长时间运行的环可能某些模块累积到 255 后停在 255——这本身不是故障，只是已饱和。'
        '想看相对增长率，需要定期用 `IOF_LB_ParityCheckWithReset` 复位。'
    ),
    var_desc={
        'LEN': '要读的模块计数（字节数 = 计数器个数）。',
    },
    pitfalls=LB_PITFALLS + [
        ('计数器**不溢出**：到 255 后会停止累积；长时间不复位时数据失去时间分布信息。', True),
        ('PDF 中 `LEN` VAR 区写 `UDINT`、描述列写 "UINT"，以 VAR 区为准。', True),
    ],
    scenario='Lightbus 长期运行：周期（每天一次）读所有模块的奇偶错计数，趋势异常时报警。',
    value='把光纤层错误监控做成可程序化采集，写入历史库做趋势分析。',
    alt=(
        '- 直接读 Lightbus 主站寄存器：底层繁琐\n'
        '- **本 FB**：标准'
    ),
    related=['IOF_LB_ParityCheckWithReset', 'IOF_LB_BreakLocationTest'],
    xml_scen='Lightbus 长期运行下趋势监控：每天定时读 5 个模块的奇偶错计数到本地缓冲。',
    xml_val='让 SCADA 看光纤层的故障趋势。',
    xml_verify='登录后 nLightbusDeviceId 设为主站 ID；nParityCounterCount := 5；写 bStartReadParity := TRUE → bReadBusy 短暂 TRUE → 回 FALSE 后 aParityErrCounters[1..5] 显示 5 个模块的奇偶错累积值。',
    xml_vars=[
        ('fbLightbusParityRead', 'IOF_LB_ParityCheck', None, 'Lightbus 奇偶错读 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nLightbusDeviceId', 'UDINT', '1', '主站 Device Id'),
        ('aParityErrCounters', 'ARRAY[1..256] OF BYTE', None, '奇偶错计数缓冲'),
        ('nParityCounterCount', 'UDINT', '5', '要读的模块数（= 字节数）'),
        ('bStartReadParity', 'BOOL', 'FALSE', '上升沿触发'),
        ('tReadTimeout', 'TIME', 'T#5S', '超时'),
        ('bReadBusy', 'BOOL', None, '工作中'),
        ('bReadErr', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        '// LEN 是字节数 = 计数器个数；DESTADDR 用 ADR()\n'
        'fbLightbusParityRead(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nLightbusDeviceId,\n'
        '    LEN      := nParityCounterCount,\n'
        '    DESTADDR := ADR(aParityErrCounters),\n'
        '    START    := bStartReadParity,\n'
        '    TMOUT    := tReadTimeout,\n'
        '    BUSY     => bReadBusy,\n'
        '    ERR      => bReadErr,\n'
        '    ERRID    => nLastErrCode\n'
        ');\n'
    ),
)


REG['IOF_LB_ParityCheckWithReset'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '与 `IOF_LB_ParityCheck` 相同，**但读后立即把每个模块的奇偶错计数器清零**。'
        '用于做"过去 T 时间内的奇偶错增量"采样。'
    ),
    behavior=(
        '调用前用户准备 `ARRAY[1..N] OF BYTE` 缓冲区。'
        '`START` 上升沿触发：`BUSY := TRUE`，FB 经 ADS 把 N 个计数器读到缓冲区**并复位主站侧的计数到 0**。'
        '完成后 `buffer[k]` = 模块 k 从上次复位到现在的奇偶错次数。'
        '常见用法：每分钟调本 FB 采样一次 → 用差量做 1 分钟内的错误率统计 → SCADA 显示。'
    ),
    var_desc={
        'LEN': '要读的模块计数（字节数）。',
    },
    pitfalls=LB_PITFALLS + [
        ('调用之后主站侧计数器复位 0；想拿"自上次复位以来的累积"用本 FB；想看"长期累积"用不带 Reset 的版本。', False),
        ('两个版本不要混用 / 并发调用，会让两边的复位时机错乱。', True),
    ],
    scenario='Lightbus 实时错误率监控：每分钟调本 FB 一次 → 把结果直接当成"该分钟错误数"送 SCADA 画趋势图。',
    value='做实时错误率监控，比累积型计数更直观。',
    alt=(
        '- 不带 Reset + 自己减上次值：可行但容易出软件 bug（计数到 255 饱和时差量算错）\n'
        '- **本 FB**：硬件帮忙做差量'
    ),
    related=['IOF_LB_ParityCheck', 'IOF_LB_BreakLocationTest'],
    xml_scen='Lightbus 实时错误率：每分钟读 5 个模块奇偶错增量送 SCADA。',
    xml_val='做差量计数比软件自己减更可靠。',
    xml_verify='登录后第一次写 bStartReadResetParity := TRUE → 完成后 aParityIncrement[1..5] 显示自上次复位以来的奇偶错次数；间隔 1 分钟再触发一次 → 看 aParityIncrement 是否随通讯质量波动。',
    xml_vars=[
        ('fbLightbusParityReadReset', 'IOF_LB_ParityCheckWithReset', None, 'Lightbus 奇偶错读+复位 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nLightbusDeviceId', 'UDINT', '1', '主站 Device Id'),
        ('aParityIncrement', 'ARRAY[1..256] OF BYTE', None, '奇偶错增量缓冲'),
        ('nParityCounterCount', 'UDINT', '5', '要读的模块数'),
        ('bStartReadResetParity', 'BOOL', 'FALSE', '上升沿触发'),
        ('tReadTimeout', 'TIME', 'T#5S', '超时'),
        ('bReadBusy', 'BOOL', None, '工作中'),
        ('bReadErr', 'BOOL', None, '失败'),
        ('nLastErrCode', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        'fbLightbusParityReadReset(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nLightbusDeviceId,\n'
        '    LEN      := nParityCounterCount,\n'
        '    DESTADDR := ADR(aParityIncrement),\n'
        '    START    := bStartReadResetParity,\n'
        '    TMOUT    := tReadTimeout,\n'
        '    BUSY     => bReadBusy,\n'
        '    ERR      => bReadErr,\n'
        '    ERRID    => nLastErrCode\n'
        ');\n'
    ),
)


# ---------------- Beckhoff UPS (1 FB) ----------------

REG['FB_GetUPSStatus'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '读取 Beckhoff UPS（不间断电源）状态，从 PLC 程序就能拿到当前电源是否在用 UPS、电池剩余电量、是否处于断电倒计时等。'
        '本 FB 是 **电平触发**（不是边沿）：`bEnable = TRUE` 时周期读取（约每 4.5 秒一次），`bValid` 表示最新读到的数据是否有效。'
        '前提：已安装 Beckhoff UPS 软件组件（Windows 7+ 在 *Start → Programs → Beckhoff → UPS Software Components*）。'
    ),
    behavior=(
        '`bEnable = TRUE` 时 FB 每隔约 4.5 秒经 ADS 读一次 UPS 状态（间隔由 FB 内部控制，无需外部触发），结果填入 `stStatus`。'
        '`bValid` 反映最近一次读取是否成功：TRUE 表示 `stStatus` 数据可信；FALSE 表示当前读取在进行 / 出错。'
        '出错时 `bError := TRUE`、`nErrId` 给出 ADS 错误号；错误原因消失后下次循环会自动复位。'
        '本 FB 是 **电平**（level-triggered）模式：`bEnable = FALSE` 时停止读取，`bValid` 也会落到 FALSE。'
        '不同于其它 ADS FB 的"上升沿触发"，本 FB 一旦 enable 就持续工作直到 disable。'
        '`nPort = 0` 对应 Windows UPS Service / Windows Battery Driver；其它端口号保留为未来扩展。'
    ),
    var_desc={
        'sNetId': '本机用空串；远端填对端 AMS Net ID。',
        'nPort': 'ADS 端口号；目前固定 0（= Windows UPS Service / Windows Battery Driver）。',
        'bEnable': 'TRUE 电平使能周期读 UPS 状态；FALSE 停止。',
        'bValid': 'TRUE = 最新 `stStatus` 数据有效；FALSE = 数据未就绪 / 读取出错。',
        'bError': 'TRUE = 上次读取失败。',
        'nErrId': 'ADS 错误号。',
        'stStatus': 'UPS 状态结构（电池电量 / 在 AC 还是 battery / 是否倒计时关机等），详见 `ST_UPSStatus`。',
    },
    pitfalls=[
        ('**电平触发**，不是上升沿——业务侧直接给 `bEnable := TRUE` 即可，不需要发脉冲。', False),
        ('约 4.5 秒读一次，**不要期待秒级实时**。若需要立刻得到 UPS 状态，断电后 0-4.5 秒会出现陈旧数据。', True),
        ('需要事先安装 Beckhoff UPS 软件组件且正确配置；驱动未装时 ADS 调用会返回端口错误（`0x6`）。', True),
        ('远端读取（`sNetId` 非空）目前是预留能力——大部分 UPS 工作场景都是本机读本机 UPS（`sNetId := ""`）。', True),
    ],
    scenario='CX5020 工控机配 Beckhoff CB3011 UPS：PLC 程序周期读 UPS 状态，断电时立即把关键 retain 数据写盘并发报警。',
    value='掉电不丢数据：UPS 给约 2 秒延迟，本 FB 让 PLC 程序在掉电瞬间就知道断电了，并执行保护逻辑。',
    alt=(
        '- 不读 UPS 状态：断电瞬间 PLC 不知道，retain 不写盘\n'
        '- 用单独的 IO 给 UPS 报警继电器接 PLC DI：能做但要硬件接线\n'
        '- **本 FB**：纯软件方式读 UPS'
    ),
    related=['FB_S_UPS_CB3011 (Tc2_SUPS)', 'FB_S_UPS_BAPI (Tc2_SUPS)'],
    xml_scen='CX 工控机配 CB3011 UPS：周期读 UPS 状态；检测到 UPS 在用电池且剩余 < 30 秒 → 触发关键数据写盘 + 报警。',
    xml_val='掉电保护：让 PLC 程序提前 1-2 秒响应即将断电。',
    xml_verify='登录后 bEnableUpsMonitor := TRUE → 1-5 秒后 bUpsStatusValid 应为 TRUE，stUpsStatus 各字段（如 PowerStatus / BatteryFlag）有值；模拟断电（拔市电插头）→ 1-5 秒内 stUpsStatus 显示电池模式。',
    xml_vars=[
        ('fbReadUpsStatus', 'FB_GetUPSStatus', None, 'UPS 状态读 FB（电平触发）'),
        ('sUpsTargetNetId', 'T_AmsNetId', "''", '本机空串'),
        ('nUpsAdsPort', 'T_AmsPort', '0', '0 = Windows UPS Service'),
        ('bEnableUpsMonitor', 'BOOL', 'TRUE', '电平使能：TRUE 即开始监控'),
        ('bUpsStatusValid', 'BOOL', None, '数据是否有效'),
        ('bUpsReadError', 'BOOL', None, '读 UPS 出错'),
        ('nUpsReadErrId', 'UDINT', None, 'ADS 错误号'),
        ('stUpsStatus', 'ST_UPSStatus', None, 'UPS 状态结构'),
    ],
    xml_call=(
        '// 电平触发：bEnable = TRUE 即周期读，不需要上升沿\n'
        'fbReadUpsStatus(\n'
        '    sNetId   := sUpsTargetNetId,\n'
        '    nPort    := nUpsAdsPort,\n'
        '    bEnable  := bEnableUpsMonitor,\n'
        '    bValid   => bUpsStatusValid,\n'
        '    bError   => bUpsReadError,\n'
        '    nErrId   => nUpsReadErrId,\n'
        '    stStatus => stUpsStatus\n'
        ');\n'
    ),
)


# ---------------- Bus Terminal configuration (5 FBs) ----------------

KL_CONFIG_PITFALLS = [
    ('**写端子寄存器会改 EEPROM**，**不要循环周期调用 `bConfigurate`**——EEPROM 寿命 10 万次写入。上电时配置一次足够。', False),
    ('`stInData` / `stOutData` 必须 IN_OUT 链到 System Manager 中端子的过程数据区，否则 FB 与端子之间通讯不通。', True),
    ('PDF 指出"本 FB 不遵循 alternative output format"——意思是过程数据在标准 vs alternative 模式下偏移不同，FB 假定**标准模式**；若 System Manager 中端子设为 alternative 会出错。', True),
    ('`tTimeout` 默认未指定时建议给 ≥ 2 秒，K-bus 端子配置握手较慢。', True),
    ('错误号 `iErrorId` 见 PDF 5.6 节的 KL Config 错误码表（如端子型号不匹配 / 寄存器写失败）；具体表 PDF 在每个 FB 后会列。', True),
]

REG['FB_KL1501Config'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '配置 KL1501（1 通道计数器端子）：选择计数器类型（32 bit 上下计数 / 2×16 bit 上计数 / 32 bit 门控计数 (Low/High 禁用)）+ 选择反向计数。'
        '配置过程是把这些设置写到 KL1501 内部寄存器，并读回校验。'
    ),
    behavior=(
        '本 FB 有两种命令：'
        '`bConfigurate` 上升沿 = 写配置（先读端子通用数据 → 写配置寄存器 → 读回校验 → 输出到 FB 输出）；'
        '`bReadConfig` 上升沿 = 仅读配置（不写）。'
        '两者执行期间 `bBusy := TRUE`，期间不接受第二个命令。'
        '`iSetCounterType` 取值含义：0 = 32 bit 上下计数；1 = 2×16 bit 上计数；2 = 32 bit 门控计数（gate Low 禁用）；3 = 32 bit 门控计数（gate High 禁用）。'
        '`bSetBackwardCounting = TRUE` 反向计数。'
        '完成后输出端子的 `iTerminalType` (端子型号编码)、`iSpecialType` (特殊版本)、`iState` (状态)、`iDataIn0` / `iDataIn1` / `iDataIn` (当前计数值)。'
        '出错时 `bError := TRUE`、`iErrorId` 给出 KL Config 错误号。'
    ),
    var_desc={
        'bConfigurate': '上升沿启动写配置序列：先读端子通用信息 → 写配置寄存器 → 读回校验。',
        'bReadConfig': '上升沿启动只读序列：读端子通用信息 + 当前配置参数。',
        'iSetCounterType': '计数器类型：0=32bit 上下 1=2×16bit 上 2=32bit 门控(Low 禁用) 3=32bit 门控(High 禁用)。',
        'bSetBackwardCounting': 'TRUE = 反向计数。',
        'tTimeout': '端子配置 / 读取必须在此时长内完成。',
        'stInData': '端子输入过程映像，IN_OUT 链到 System Manager。',
        'stOutData': '端子输出过程映像，IN_OUT 链到 System Manager。',
        'iState': '端子状态字节。',
        'iDataIn0': '通道 0 当前计数值（用于 2×16bit 模式）。',
        'iDataIn1': '通道 1 当前计数值（同上）。',
        'iDataIn': '组合 32bit 计数值（32bit 模式）。',
        'iTerminalType': '端子型号编码（应为 KL1501 对应的值）。',
        'iSpecialType': '端子特殊版本。',
    },
    pitfalls=KL_CONFIG_PITFALLS + [
        ('计数器类型改变后端子计数值会清零；不要在运行中改类型。', True),
    ],
    scenario='印刷线 KL1501 计数器端子：上电时把端子配为 32 bit 上下计数（type 0）+ 不反向，配套编码器接到端子。',
    value='把端子配置代码化，避免现场用 KS2000 工具人工拨号。',
    alt=(
        '- KS2000 配置工具：要带工具到现场\n'
        '- 直接读写端子寄存器：底层繁琐\n'
        '- **本 FB**：上电一次完成配置'
    ),
    related=['FB_ReadCouplerRegs (Tc2_Coupler)', 'ReadWriteTerminalReg (Tc2_Coupler)'],
    xml_scen='上电时把 KL1501 配为 32 bit 上下计数器，不反向；运行后读端子计数值进行设备速度计算。',
    xml_val='端子配置纳入 PLC 程序版本控制。',
    xml_verify='登录确认 stKl1501InProcessImg / stKl1501OutProcessImg 已链到端子；在线写 bDoKl1501Configure := TRUE → fbKl1501.bBusy 短暂 TRUE → 回 FALSE 后 iLastKl1501Error = 0 表示成功；iCurrentCountValue 应反映编码器旋转。',
    xml_vars=[
        ('fbKl1501', 'FB_KL1501Config', None, 'KL1501 配置 FB'),
        ('stKl1501InProcessImg', 'ST_KL1501InData', None, 'KL1501 输入过程映像（链到 %I*）'),
        ('stKl1501OutProcessImg', 'ST_KL1501OutData', None, 'KL1501 输出过程映像（链到 %Q*）'),
        ('bDoKl1501Configure', 'BOOL', 'FALSE', '上升沿写配置'),
        ('bDoKl1501ReadConfig', 'BOOL', 'FALSE', '上升沿只读配置'),
        ('iCounterTypeSelected', 'INT', '0', '0=32 上下 1=2×16 上 2/3=门控'),
        ('bReverseCountDir', 'BOOL', 'FALSE', '反向计数'),
        ('tKl1501ConfigTimeout', 'TIME', 'T#5S', '配置超时'),
        ('bKl1501Busy', 'BOOL', None, '工作中'),
        ('bKl1501Error', 'BOOL', None, '出错'),
        ('iLastKl1501Error', 'UDINT', None, '错误号'),
        ('iKl1501State', 'USINT', None, '状态字节'),
        ('iCount0', 'UINT', None, '通道 0 计数'),
        ('iCount1', 'UINT', None, '通道 1 计数'),
        ('iCurrentCountValue', 'UDINT', None, '32 bit 组合计数值'),
        ('iKl1501TerminalCode', 'WORD', None, '端子型号编码'),
        ('iKl1501SpecialVer', 'WORD', None, '端子特殊版本'),
    ],
    xml_call=(
        'fbKl1501(\n'
        '    bConfigurate         := bDoKl1501Configure,\n'
        '    bReadConfig          := bDoKl1501ReadConfig,\n'
        '    iSetCounterType      := iCounterTypeSelected,\n'
        '    bSetBackwardCounting := bReverseCountDir,\n'
        '    tTimeout             := tKl1501ConfigTimeout,\n'
        '    stInData             := stKl1501InProcessImg,\n'
        '    stOutData            := stKl1501OutProcessImg,\n'
        '    bBusy                => bKl1501Busy,\n'
        '    bError               => bKl1501Error,\n'
        '    iErrorId             => iLastKl1501Error,\n'
        '    iState               => iKl1501State,\n'
        '    iDataIn0             => iCount0,\n'
        '    iDataIn1             => iCount1,\n'
        '    iDataIn              => iCurrentCountValue,\n'
        '    iTerminalType        => iKl1501TerminalCode,\n'
        '    iSpecialType         => iKl1501SpecialVer\n'
        ');\n'
    ),
)


REG['FB_KL27x1Config'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '配置 KL2751 / KL2761（1 通道调光器端子）：斜坡时间 / 调光模式 / 看门狗超时 / 短路后自动恢复 / 50Hz 或 60Hz 等。'
        '运行时不需要持续调，**上电配置一次** 即可。'
    ),
    behavior=(
        '`bConfigurate` 上升沿写配置；`bReadConfig` 上升沿只读。'
        '`iSetRampTime` 与 `bSetDimRampAbsolute` 配合定义斜坡时间：'
        '`bSetDimRampAbsolute = FALSE`（相对）→ 斜坡时间是整个数据区 0..32767 全程的时间；'
        '`= TRUE`（绝对）→ 每一调光步长都用相同的 ramp 时间。'
        '`iSetWatchdogTimeout`（单位 10 ms 倍数）：现场总线丢失通讯后多少 ms 触发 fail-safe。'
        '`iSetTimeoutOnValue` / `iSetTimeoutOffValue` 决定 fail-safe 时输出的亮度（取决于当前过程数据是 > 0 还是 = 0）。'
        '`bSetWatchdogDisable = TRUE` 关闭看门狗（不推荐生产线用）。'
        '`bSetOnAfterShortCircuit = TRUE` 短路恢复后自动点亮；FALSE 短路后保持灭。'
        '`bSetLineFrequency60Hz = TRUE` 表示 60 Hz 市电（北美），FALSE 表示 50 Hz（欧 / 亚）。'
    ),
    var_desc={
        'bConfigurate': '上升沿写配置。',
        'bReadConfig': '上升沿只读配置。',
        'bSetDimRampAbsolute': 'FALSE = 斜坡时间针对 0..32767 全程；TRUE = 每一步长固定时间。',
        'iSetRampTime': '斜坡时间设定（具体含义见 PDF 表）。',
        'bSetWatchdogDisable': 'TRUE = 关闭看门狗。',
        'iSetWatchdogTimeout': '看门狗超时（× 10 ms）。',
        'iSetTimeoutOnValue': 'fail-safe 模式下当前过程数据 > 0 时输出的亮度。',
        'iSetTimeoutOffValue': 'fail-safe 模式下当前过程数据 = 0 时输出的亮度。',
        'iSetDimmerMode': '调光模式（前沿 / 后沿等，见 PDF 表）。',
        'bSetOnAfterShortCircuit': 'TRUE = 短路恢复后自动开。',
        'bSetLineFrequency60Hz': 'TRUE = 60Hz, FALSE = 50Hz。',
        'tTimeout': '配置超时。',
    },
    pitfalls=KL_CONFIG_PITFALLS + [
        ('调光模式与负载类型必须匹配（电感 / 电容 / 阻性）；选错会损坏负载或端子。', False),
        ('60Hz / 50Hz 设置必须与市电匹配。', False),
    ],
    scenario='剧院 LED 调光：8 路 KL2751 端子上电时配置成"前沿调光 + 50 Hz + 短路恢复"。',
    value='把调光端子配置代码化，便于多台设备工程批量复制。',
    alt=(
        '- KS2000 工具：要带工具\n'
        '- **本 FB**：上电一次'
    ),
    related=['FB_KL320xConfig', 'FB_ReadCouplerRegs (Tc2_Coupler)'],
    xml_scen='剧院调光系统：上电时把 KL2751 配为绝对斜坡 100、50 Hz、短路恢复后亮、fail-safe = 0。',
    xml_val='端子配置纳入 PLC 程序版本控制；现场更换端子无需重新拨码。',
    xml_verify='登录确认 stKl27x1InProcessImg / OutProcessImg 已链；写 bDoConfigure := TRUE → fbKl27x1.bBusy 短暂 TRUE → 回 FALSE 后 iLastError = 0 表示成功。',
    xml_vars=[
        ('fbKl27x1', 'FB_KL27x1Config', None, 'KL2751/2761 配置 FB'),
        ('stKl27x1InProcessImg', 'ST_KL27x1InData', None, '输入过程映像'),
        ('stKl27x1OutProcessImg', 'ST_KL27x1OutData', None, '输出过程映像'),
        ('bDoConfigure', 'BOOL', 'FALSE', '上升沿写配置'),
        ('bDoReadConfig', 'BOOL', 'FALSE', '上升沿只读'),
        ('bUseAbsoluteRamp', 'BOOL', 'TRUE', 'TRUE = 每步固定时间'),
        ('iRampTimeSetting', 'INT', '100', '斜坡时间'),
        ('bDisableWatchdog', 'BOOL', 'FALSE', '关闭看门狗'),
        ('iWatchdogTimeoutMs10', 'UINT', '20', '看门狗超时 × 10 ms (= 200 ms)'),
        ('iFailSafeOnValue', 'UINT', '0', 'fail-safe 时数据>0 的亮度'),
        ('iFailSafeOffValue', 'UINT', '0', 'fail-safe 时数据=0 的亮度'),
        ('iDimMode', 'INT', '0', '调光模式（具体表见 PDF）'),
        ('bAutoOnAfterShortCircuit', 'BOOL', 'TRUE', '短路恢复后自动亮'),
        ('bUse60HzMains', 'BOOL', 'FALSE', '60Hz 还是 50Hz'),
        ('tKl27x1ConfigTimeout', 'TIME', 'T#5S', '超时'),
        ('bKl27x1Busy', 'BOOL', None, '工作中'),
        ('bKl27x1Error', 'BOOL', None, '出错'),
        ('iLastError', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        'fbKl27x1(\n'
        '    bConfigurate            := bDoConfigure,\n'
        '    bReadConfig             := bDoReadConfig,\n'
        '    bSetDimRampAbsolute     := bUseAbsoluteRamp,\n'
        '    iSetRampTime            := iRampTimeSetting,\n'
        '    bSetWatchdogDisable     := bDisableWatchdog,\n'
        '    iSetWatchdogTimeout     := iWatchdogTimeoutMs10,\n'
        '    iSetTimeoutOnValue      := iFailSafeOnValue,\n'
        '    iSetTimeoutOffValue     := iFailSafeOffValue,\n'
        '    iSetDimmerMode          := iDimMode,\n'
        '    bSetOnAfterShortCircuit := bAutoOnAfterShortCircuit,\n'
        '    bSetLineFrequency60Hz   := bUse60HzMains,\n'
        '    tTimeout                := tKl27x1ConfigTimeout,\n'
        '    bBusy                   => bKl27x1Busy,\n'
        '    bError                  => bKl27x1Error,\n'
        '    iErrorId                => iLastError\n'
        ');\n'
    ),
)


REG['FB_KL320xConfig'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '配置 KL3201 / KL3202 / KL3204（电阻传感器输入端子，RTD / PT100/PT1000 等）的单个通道传感器类型。'
        '多通道端子需要为每个通道单独实例化本 FB（混合配置允许）。'
    ),
    behavior=(
        '本 FB 只负责一个通道的配置。多通道端子需要按通道数实例化对应数量的 FB 实例（混合配置允许，例如通道 1 用 PT100、通道 2 用 PT1000）。'
        '`bConfigurate` 上升沿启动写配置序列：先读端子通用信息 → 写传感器类型寄存器 → 读回校验 → 输出端子型号 / 特殊版本 / 通道状态等。'
        '`bReadConfig` 上升沿启动只读序列：仅读取当前配置而不写入 EEPROM。'
        '执行期间 `bBusy := TRUE`，不接受第二个命令。'
        '`iSetSensorType` 选择传感器类型（PT100 / PT1000 / Ni100 / 0-3 kΩ 直接电阻 等），具体取值见 PDF KL3201/3202/3204 手册的传感器类型表。'
        '`tTimeout` 限制配置时长，默认建议 ≥ 2 秒以适应 K-bus 端子配置握手。'
        '完成后 `bBusy` 落回，`bError` / `iErrorId` 反映成功 / 失败。'
    ),
    var_desc={
        'iSetSensorType': '传感器类型编码（PT100 / PT1000 / Ni100 / 直接电阻 等；具体见 PDF KL3201 手册表）。',
    },
    pitfalls=KL_CONFIG_PITFALLS + [
        ('多通道端子须每通道一个 FB 实例；不要把一个 FB 实例切换通道使用。', True),
        ('传感器类型编码不同端子型号略有差异（KL3201 vs KL3202 vs KL3204），按当前接的端子手册选。', True),
    ],
    scenario='炉温监控：KL3204 多通道电阻输入端子，4 个通道接 4 个 PT100，上电时配 4 个 FB 实例把每通道配为 PT100。',
    value='端子配置代码化。',
    alt=(
        '- KS2000 工具：要带工具\n'
        '- **本 FB**：纯 PLC 程序'
    ),
    related=['FB_KL3208Config', 'FB_KL3228Config', 'FB_KL1501Config'],
    xml_scen='炉温监控：KL3204 端子 4 路接 PT100，上电时配 4 个通道全为 PT100。',
    xml_val='配置代码化，便于多炉子工程批量复制。',
    xml_verify='登录确认 stKl3204InProcessImg / OutProcessImg 已链；写 bDoConfigure := TRUE → fbKl320x.bBusy 短暂 TRUE → 回 FALSE 后 iLastError = 0 表示成功。',
    xml_vars=[
        ('fbKl320x', 'FB_KL320xConfig', None, 'KL3201/3202/3204 配置 FB（每通道一个实例）'),
        ('stKl3204InProcessImg', 'ST_KL320xInData', None, '过程映像 输入'),
        ('stKl3204OutProcessImg', 'ST_KL320xOutData', None, '过程映像 输出'),
        ('bDoConfigure', 'BOOL', 'FALSE', '上升沿写配置'),
        ('bDoReadConfig', 'BOOL', 'FALSE', '上升沿只读'),
        ('iSensorTypeCode', 'INT', '0', '传感器类型（具体表见 PDF）'),
        ('tConfigTimeout', 'TIME', 'T#5S', '超时'),
        ('bKl320xBusy', 'BOOL', None, '工作中'),
        ('bKl320xError', 'BOOL', None, '出错'),
        ('iLastError', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        'fbKl320x(\n'
        '    bConfigurate   := bDoConfigure,\n'
        '    bReadConfig    := bDoReadConfig,\n'
        '    iSetSensorType := iSensorTypeCode,\n'
        '    tTimeout       := tConfigTimeout,\n'
        '    stInData       := stKl3204InProcessImg,\n'
        '    stOutData      := stKl3204OutProcessImg,\n'
        '    bBusy          => bKl320xBusy,\n'
        '    bError         => bKl320xError,\n'
        '    iErrorId       => iLastError\n'
        ');\n'
    ),
)


REG['FB_KL3208Config'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '配置 KL3208-0010（8 通道电阻传感器输入端子）单个通道的传感器类型。'
        '8 个通道每个都用一个本 FB 实例（混合配置允许）。'
    ),
    behavior=(
        '与 `FB_KL320xConfig` 用法完全相同，只是面对的端子是 8 通道版本，需要 8 个 FB 实例分别配置。'
        '`bConfigurate` 上升沿启动写配置序列（读通用信息 → 写寄存器 → 读回校验）；'
        '`bReadConfig` 上升沿启动只读序列（不写入 EEPROM）。'
        '`iSetSensorType` 选传感器类型（具体编码见 PDF KL3208 手册表，与 KL3204 可能略有差异）。'
        '执行期间 `bBusy := TRUE`，结束后通过 `bError` / `iErrorId` 反映成功 / 失败。'
        '`tTimeout` 限制单通道配置时长；K-bus 握手较慢，建议 ≥ 2 秒。'
        '8 通道一次性配完时间约 4-8 秒（每通道一次握手），可串行调用。'
    ),
    var_desc={
        'iSetSensorType': '传感器类型编码（PT100 / PT1000 / Ni100 / 直接电阻 等；具体见 PDF KL3208 手册表）。',
    },
    pitfalls=KL_CONFIG_PITFALLS + [
        ('8 通道要 8 个 FB 实例，不要复用一个 FB 切通道访问。', True),
        ('KL3208 与 KL3204 的传感器类型编码可能不完全相同；按 KL3208 手册选。', True),
    ],
    scenario='机柜温度监控：KL3208 8 通道端子分别接 8 个 PT1000 监控不同设备温度。',
    value='8 通道配置代码化。',
    alt=(
        '- KS2000 工具：要带工具\n'
        '- **本 FB**：8 个实例搞定'
    ),
    related=['FB_KL320xConfig', 'FB_KL3228Config'],
    xml_scen='8 路 PT1000 上电批量配置；本 demo 只演示一个通道，实际要 8 个 FB 实例。',
    xml_val='代码化配置。',
    xml_verify='登录确认 stKl3208InProcessImg / OutProcessImg 已链；写 bDoConfigure := TRUE → fbKl3208.bBusy 短暂 TRUE → 回 FALSE 后 iLastError = 0。',
    xml_vars=[
        ('fbKl3208', 'FB_KL3208Config', None, 'KL3208-0010 配置 FB（每通道一个实例）'),
        ('stKl3208InProcessImg', 'ST_KL3208InData', None, '过程映像 输入'),
        ('stKl3208OutProcessImg', 'ST_KL3208OutData', None, '过程映像 输出'),
        ('bDoConfigure', 'BOOL', 'FALSE', '上升沿写配置'),
        ('bDoReadConfig', 'BOOL', 'FALSE', '上升沿只读'),
        ('iSensorTypeCode', 'INT', '1', 'PT1000 编码（具体表见 PDF）'),
        ('tConfigTimeout', 'TIME', 'T#5S', '超时'),
        ('bKl3208Busy', 'BOOL', None, '工作中'),
        ('bKl3208Error', 'BOOL', None, '出错'),
        ('iLastError', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        'fbKl3208(\n'
        '    bConfigurate   := bDoConfigure,\n'
        '    bReadConfig    := bDoReadConfig,\n'
        '    iSetSensorType := iSensorTypeCode,\n'
        '    tTimeout       := tConfigTimeout,\n'
        '    stInData       := stKl3208InProcessImg,\n'
        '    stOutData      := stKl3208OutProcessImg,\n'
        '    bBusy          => bKl3208Busy,\n'
        '    bError         => bKl3208Error,\n'
        '    iErrorId       => iLastError\n'
        ');\n'
    ),
)


REG['FB_KL3228Config'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '配置 KL3228（8 通道电阻传感器输入端子）单个通道的传感器类型。'
        '与 KL3208 类似但端子型号是 KL3228。'
    ),
    behavior=(
        '与 `FB_KL3208Config` 用法相同，本 FB 只负责一个通道的配置，8 通道端子需要 8 个 FB 实例。'
        '`bConfigurate` 上升沿启动写配置序列（读通用信息 → 写传感器类型寄存器 → 读回校验）。'
        '`bReadConfig` 上升沿启动只读序列（不写 EEPROM）。'
        '`iSetSensorType` 选传感器类型，编码按 KL3228 手册表（与 KL3208 可能略有差异，按当前接的端子手册选）。'
        '执行期间 `bBusy := TRUE`，结束后通过 `bError` / `iErrorId` 反映成功 / 失败。'
        '`tTimeout` 限制配置时长，默认建议 ≥ 2 秒以适应 K-bus 握手延迟。'
    ),
    var_desc={
        'iSetSensorType': '传感器类型编码（按 KL3228 手册表）。',
    },
    pitfalls=KL_CONFIG_PITFALLS + [
        ('KL3228 与 KL3208 编码可能不同，按 KL3228 手册选。', True),
    ],
    scenario='KL3228 8 通道温度采集，上电配置每个通道为对应传感器类型。',
    value='代码化批量配置。',
    alt=(
        '- KS2000 工具\n'
        '- **本 FB**：上电完成'
    ),
    related=['FB_KL3208Config', 'FB_KL320xConfig'],
    xml_scen='KL3228 端子 8 通道全部接 PT100 监控生产线 8 个工位温度。',
    xml_val='端子配置代码化。',
    xml_verify='登录确认 stKl3228InProcessImg / OutProcessImg 已链；写 bDoConfigure := TRUE → 回 FALSE 后 iLastError = 0。',
    xml_vars=[
        ('fbKl3228', 'FB_KL3228Config', None, 'KL3228 配置 FB'),
        ('stKl3228InProcessImg', 'ST_KL3228InData', None, '过程映像 输入'),
        ('stKl3228OutProcessImg', 'ST_KL3228OutData', None, '过程映像 输出'),
        ('bDoConfigure', 'BOOL', 'FALSE', '上升沿写配置'),
        ('bDoReadConfig', 'BOOL', 'FALSE', '上升沿只读'),
        ('iSensorTypeCode', 'INT', '0', 'PT100 编码（KL3228 手册）'),
        ('tConfigTimeout', 'TIME', 'T#5S', '超时'),
        ('bKl3228Busy', 'BOOL', None, '工作中'),
        ('bKl3228Error', 'BOOL', None, '出错'),
        ('iLastError', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        'fbKl3228(\n'
        '    bConfigurate   := bDoConfigure,\n'
        '    bReadConfig    := bDoReadConfig,\n'
        '    iSetSensorType := iSensorTypeCode,\n'
        '    tTimeout       := tConfigTimeout,\n'
        '    stInData       := stKl3228InProcessImg,\n'
        '    stOutData      := stKl3228OutProcessImg,\n'
        '    bBusy          => bKl3228Busy,\n'
        '    bError         => bKl3228Error,\n'
        '    iErrorId       => iLastError\n'
        ');\n'
    ),
)


# ---------------- CANopen (1 FB) ----------------

REG['IOF_CAN_Layer2Command'] = dict(
    ftype='FUNCTION_BLOCK',
    summary=(
        '向 CAN 主站发送一个 layer-2 命令（10 字节）。'
        '本 FB 是访问 CAN 层 2（原始 CAN 帧）的接口，绕过 CANopen 协议栈直接发原始 CAN 报文，用于诊断或与非 CANopen 设备通讯。'
        'PDF 明确："本功能 TwinCAT 3 目前不支持"（适配的硬件 HILSCHER CIF3xx 老 ISA 卡）。'
    ),
    behavior=(
        '`START` 上升沿触发一次发送：`BUSY := TRUE`，FB 把 `SRCADDR` 指向的 `LEN` 字节 layer-2 命令通过 ADS 发到 CAN 主站。'
        '完成后 `BUSY := FALSE`；出错 `ERR := TRUE`、`ERRID` 给出 ADS 错误号。'
        '触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再决定下一次是否重新触发。'
        '注意：本 FB 的 VAR_INPUT 在 PDF VAR 区只列了 NETID / DEVICEID / BOXADDR / START / TMOUT，'
        '但描述列还提到 `LEN` (UDINT) 和 `SRCADDR` (PVOID)；这两个字段实际存在但被 PDF VAR 区漏列。'
        '⚠️ 调用时按 PDF 描述列填，名称按 PDF 写法。'
    ),
    var_desc={
        'BOXADDR': 'CAN 设备地址（layer-2 命令的目标节点）。',
    },
    pitfalls=ADS_PITFALLS + [
        ('**TwinCAT 3 不支持本功能**（PDF 明确说明），HILSCHER CIF3xx 是早期 ISA 卡。', False),
        ('PDF VAR_INPUT 漏列 `LEN` 和 `SRCADDR`；实际接口含这两参数，按 PDF 描述列填。', True),
        ('layer-2 直发原始 CAN 报文需要懂 CAN 协议帧结构；用错可能干扰总线上其它节点。', True),
    ],
    scenario='维护老线：HILSCHER CIF30 ISA 卡接 CANopen 网络，用本 FB 发原始 CAN 报文做诊断（如发 NMT 复位命令）。',
    value='绕过 CANopen 栈访问底层 CAN 帧。',
    alt=(
        '- 在 TwinCAT 3 上跑：不支持\n'
        '- 用 Tc3_CANopen 库：标准做法\n'
        '- **本 FB**：仅维护早期工程'
    ),
    related=['IOF_DeviceReset'],
    xml_scen='HILSCHER CIF3xx ISA 卡 + CANopen 现场总线：发原始 CAN 帧做诊断（如手动触发 NMT 复位）。',
    xml_val='维护早期老工程的诊断能力。',
    xml_verify='⚠️ TwinCAT 3 不支持本功能；本例程仅作"代码兼容性参考"，运行时不会真正发出 CAN 报文。',
    xml_vars=[
        ('fbCanLayer2', 'IOF_CAN_Layer2Command', None, 'CAN layer-2 命令 FB'),
        ('sTargetNetId', 'T_AmsNetId', "''", '本机'),
        ('nCanDeviceId', 'UDINT', '1', 'CAN 主站 Device Id'),
        ('nCanNodeAddr', 'WORD', '0', '目标节点'),
        ('aCanLayer2Data', 'ARRAY[1..5] OF WORD', None, '10 字节 CAN layer-2 命令'),
        ('bStartCanCmd', 'BOOL', 'FALSE', '上升沿触发'),
        ('tCanCmdTimeout', 'TIME', 'T#5S', '超时'),
        ('bCanCmdBusy', 'BOOL', None, '工作中'),
        ('bCanCmdError', 'BOOL', None, '出错'),
        ('nLastCanErrCode', 'UDINT', None, '错误号'),
    ],
    xml_call=(
        '// 注：PDF VAR_INPUT 漏列 LEN/SRCADDR，但描述列说有；按描述列调用\n'
        'fbCanLayer2(\n'
        '    NETID    := sTargetNetId,\n'
        '    DEVICEID := nCanDeviceId,\n'
        '    BOXADDR  := nCanNodeAddr,\n'
        '    START    := bStartCanCmd,\n'
        '    TMOUT    := tCanCmdTimeout,\n'
        '    BUSY     => bCanCmdBusy,\n'
        '    ERR      => bCanCmdError,\n'
        '    ERRID    => nLastCanErrCode\n'
        ');\n'
    ),
)
