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
