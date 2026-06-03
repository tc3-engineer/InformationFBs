# -*- coding: utf-8 -*-
"""Per-FB authored Chinese content for Tc2_DMX doc/TcPOU generation.
Imported by _tc2_dmx_gen.py. Every fact (VAR names/types/defaults) is pulled
verbatim from the PDF by the generator; this file only supplies Chinese prose
(descriptions, behavior, scenario) translated from the PDF+InfoSys text.
"""
from _tc2_dmx_gen import (
    add, D_bStart, D_wDest, D_dwDest, D_byPort, D_dwOpt, D_buf,
    D_bBusy, D_bError, D_udiErr,
)

# Common input/inout description set shared by the addressed-RDM FBs.
def base_in(extra=None):
    d = {"bStart": D_bStart, "wDestinationManufacturerId": D_wDest,
         "dwDestinationDeviceId": D_dwDest, "byPortId": D_byPort,
         "dwOptions": D_dwOpt, "stCommandBuffer": D_buf,
         "bBusy": D_bBusy, "bError": D_bError, "udiErrorId": D_udiErr}
    if extra:
        d.update(extra)
    return d

# Standard scenario/value/verify for read-one-RDM-parameter FBs.
def std_decl(fbtype, instname, extra_decl):
    return (
        f"    {instname:<18}: {fbtype};\n"
        "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
        "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID（示例：Beckhoff）\n"
        "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
        "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
        "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
        "    bBusy             : BOOL;                         // 命令进行中\n"
        "    bError            : BOOL;                         // 命令出错\n"
        "    udiErrId          : UDINT;                        // 错误码\n"
        f"{extra_decl}"
    )

ADDR_CALL_HEAD = (
    "// 单次上升沿触发；需每周期调用并等 bBusy 落回 FALSE 后再读结果。\n"
    "// 配套通讯 FB 必须处于非 CycleMode（bSetCycleMode := FALSE），否则错误码 0x800A。\n"
)

# ===========================================================================
# High Level
# ===========================================================================
add("FB_DMXDiscovery512", section="4.1.1.2", cat="high_level", cat_label="High Level",
    guid="{56ed35eb-105c-5834-8632-6c2094e24208}",
    summary="高层（High Level）设备搜索功能块，与 `FB_DMXDiscovery` 同源但搜索范围扩大到最多 512 个 DMX 设备，并可选地自动连续分配 DMX512 起始地址。它把底层 RDM 二分发现协议封装为一次触发即完成的批量发现，适合设备数量超过 50 的大型剧场 / 演艺中心总线。",
    vardesc=base_in({
        "dwOptions": "选项位（见下表），多个常量用 OR 按位或起来。",
        "uliLowerBoundSearchUID": "搜索过程中当前发送的搜索地址下界。",
        "uliUpperBoundSearchUID": "搜索过程中当前发送的搜索地址上界。",
        "arrDMXDeviceInfoList": "找到的 DMX 设备的关键信息数组（最多 512 个）。",
        "uiNextDMX512StartAddress": "若激活 `DMX_OPTION_SET_START_ADDRESS`，此处显示将分配给下一个设备的起始地址。",
        "iFoundDevices": "搜索过程中此处给出当前已找到的设备数量。",
    }),
    opt_table=[("DMX_OPTION_COMPLETE_NEW_DISCOVERY", "把所有 DMX 设备都纳入搜索（完全重新发现）。"),
               ("DMX_OPTION_SET_START_ADDRESS", "为找到的所有 DMX 设备设置起始地址，从 1 开始连续分配。"),
               ("DMX_OPTION_OPTICAL_FEEDBACK", "找到某设备时调用 `IDENTIFY_DEVICE` 让其闪烁 2 秒做光学反馈。")],
    behavior="`bStart` 上升沿触发一次搜索：`bBusy` 置 TRUE，功能块通过 `stCommandBuffer` 排入一连串 RDM 发现命令（基于 Mute/UnMute + UniqueBranch 的二分式 UID 搜索），由共享的 `FB_EL6851CommunicationEx` 实例实际发出。与 `FB_DMXDiscovery` 的唯一区别是结果数组上界为 512 而非 50。搜索是异步过程，可能持续多个 PLC 周期；其间 `uliLowerBoundSearchUID` / `uliUpperBoundSearchUID` 反映当前二分查找区间，`iFoundDevices` 实时累加。完成后 `bBusy` 落回 FALSE，`arrDMXDeviceInfoList[1..iFoundDevices]` 填好各设备信息。`dwOptions` 控制自动编址、光学反馈、完全重搜。必须给 `bStart` 上升沿，持续高电平不会重复触发；发现期间配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。",
    errnote="搜索若一直 `0x800A`，说明通讯功能块还停在 CycleMode；`0x8009` 表示搜索地址下界大于上界。",
    notes=["**必须配合一个通讯功能块实例**且共用同一个 `stCommandBuffer`；发现期间通讯功能块要处于非 CycleMode。",
           "**最多搜索 512 个设备**：超过部分不会被记录；设备数 ≤ 50 时用 `FB_DMXDiscovery` 数组更小。",
           "搜索是异步的，要每周期调用并等 `bBusy` 落回 FALSE 后再读结果。（工程经验补充）",
           "`DMX_OPTION_OPTICAL_FEEDBACK` 让每个设备闪 2 秒，设备越多搜索总时长越长。（工程经验补充）"],
    scenario="大型演艺中心 DMX 总线挂了上百台调光 / 染色灯，首次调试要一次性扫出全部设备并自动从 1 起连续编排起始地址。",
    value="一次触发即完成全总线扫描（最多 512 台）、收集设备信息并自动编址，底层二分发现协议全部隐藏，且不像 `FB_DMXDiscovery` 受 50 台上限约束。",
    alt=["用 `FB_DMXDiscovery`：实现相同但最多 50 台，设备多时不够用。",
         "自己用底层 `FB_DMXDiscMute`/`FB_DMXDiscUniqueBranch`/`FB_DMXDiscUnMute` 二分搜索：可行但要自写整套 UID 区间逻辑，易错。",
         "**本功能块**：大规模总线一键发现 + 自动编址。"],
    related="`FB_DMXDiscovery`（≤50 台版本）、`FB_DMXDiscMute` / `FB_DMXDiscUniqueBranch` / `FB_DMXDiscUnMute`（底层发现命令）、`FB_EL6851CommunicationEx`（通讯核心）",
    decl="""    fbDmxDiscovery512  : FB_DMXDiscovery512;               // 高层设备搜索（最多 512 台）
    stDmxCmdBuffer     : ST_DMXCommandBuffer;              // 与通讯 FB 共用的命令缓冲区
    bStartDiscovery    : BOOL := FALSE;                    // 在线给一次上升沿触发搜索
    dwDiscoveryOptions : DWORD;                            // 搜索选项（OR 组合）
    bDiscoveryBusy     : BOOL;                             // 搜索进行中
    bDiscoveryError    : BOOL;                             // 搜索出错
    udiDiscoveryErrId  : UDINT;                            // 错误码
    arrFoundDevices    : ARRAY [1..512] OF ST_DMXDeviceInfo;  // 找到的设备清单
    iFoundDeviceCount  : INT;                              // 已找到设备数
    uiNextStartAddr    : UINT;                             // 下一个待分配的起始地址""",
    scen_c="演艺中心 DMX 总线挂了上百台灯，首次上电要扫出全部设备并自动从 1 连续编址。",
    val_c="一次触发完成全总线（最多 512 台）扫描 + 收集信息 + 自动编址，不受 FB_DMXDiscovery 的 50 台上限约束。",
    ver_c="给 bStartDiscovery 一次上升沿 -> bDiscoveryBusy 变 TRUE，iFoundDeviceCount 递增；bDiscoveryBusy 回 FALSE 后 arrFoundDevices[1..N] 填入设备信息。",
    call="""dwDiscoveryOptions := DMX_OPTION_COMPLETE_NEW_DISCOVERY OR DMX_OPTION_SET_START_ADDRESS;

fbDmxDiscovery512(
    bStart                   := bStartDiscovery,
    dwOptions                := dwDiscoveryOptions,
    stCommandBuffer          := stDmxCmdBuffer,
    bBusy                    => bDiscoveryBusy,
    bError                   => bDiscoveryError,
    udiErrorId               => udiDiscoveryErrId,
    arrDMXDeviceInfoList     => arrFoundDevices,
    uiNextDMX512StartAddress => uiNextStartAddr,
    iFoundDevices            => iFoundDeviceCount
);""")

# ===========================================================================
# Base
# ===========================================================================
add("FB_DMXSendRDMCommand", section="4.1.2.1.1", cat="base", cat_label="Base",
    guid="{bc0a4ef2-08cc-5028-bb1e-33ca19b0fcb1}",
    summary="通用 RDM 命令发送功能块：由命令号（Command Class + Parameter Id）和可选的传输参数自由组装并发送任意一条 RDM 命令。当某个具体功能（如读传感器、设地址）没有现成的专用 FB，或需要发厂商自定义 PID 时，用它直接构造原始 RDM 报文。",
    vardesc=base_in({
        "wSubDevice": "子设备号。带重复模块的设备（如调光柜）用子设备寻址，使参数命令可发给设备内某个具体模块以读 / 设其属性。",
        "eCommandClass": "命令类别（CC），指示报文动作（见 `E_DMXCommandClass`）。",
        "eParameterId": "参数 Id，16 位数字，标识某种参数数据的类型（见 `E_DMXParameterId`）。",
        "byParameterDataLength": "参数数据长度（PDL），即参数数据区中后续的字节数；为 `0x00` 时表示无参数数据。",
        "arrParameterData": "可变长度的参数数据，内容格式取决于 PID。",
        "byResponseMessageCount": "指示 DMX 从设备还有更多消息；用 RDM 命令 Get: QUEUED_MESSAGE 读取这些消息。",
        "byResponseDataLength": "RDM 命令返回的字节数。",
        "arrResponseData": "RDM 命令应答数据，长度可变，格式取决于具体 RDM 命令。",
    }),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块按 `wDestinationManufacturerId` / `dwDestinationDeviceId` / `byPortId` / `wSubDevice` 寻址目标（子设备），按 `eCommandClass`（GET/SET/DISCOVERY 等）+ `eParameterId`（PID）+ `byParameterDataLength` + `arrParameterData` 组装一条完整 RDM 报文，排入 `stCommandBuffer` 由通讯功能块发出。完成后 `bBusy` 落回 FALSE，应答数据在 `arrResponseData[0..byResponseDataLength-1]`，`byResponseMessageCount` 提示设备是否还有排队消息。这是所有专用 RDM FB 的底层基础——专用 FB 本质上就是预设好 CC/PID 后对它的封装。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时通讯功能块须处于非 CycleMode。",
    errnote="`0x800F`–`0x8019` 是各类 RDM 应答错误（命令未实现、参数越界、子设备未知等），含义取决于所发 PID。",
    notes=["**这是最底层的通用 RDM 接口**：要自己查 RDM/ESTA E1.20 标准确定 CC、PID、参数数据格式，比专用 FB 难用但最灵活。",
           "应答可能超长（`0x801C`）：参数数据过长时必须用 `FB_EL6851CommunicationEx` 做通讯核心，旧版 `FB_EL6851Communication` 收不全。",
           "`byResponseMessageCount > 0` 表示设备还有排队消息，需再用 Get: QUEUED_MESSAGE 取出。（工程经验补充）",
           "优先用专用 FB（如 `FB_DMXGetSensorValue`）：它们已经把 CC/PID 设好，不易出错。仅在没有专用 FB 时才用本 FB。（工程经验补充）"],
    scenario="某品牌灯具支持一个非标准的厂商自定义 PID（例如读取灯具内部温度曲线），Tc2_DMX 没有对应的专用 FB。",
    value="无需等 Beckhoff 出专用 FB，直接按 RDM 标准填 CC/PID/参数即可发任意命令并取回原始应答，覆盖全部 RDM 能力。",
    alt=["等 / 找专用 FB：覆盖不到厂商自定义 PID。",
         "外接 RDM 控台发命令：进不了 PLC 逻辑。",
         "**本 FB**：PLC 内构造任意 RDM 报文，最灵活。"],
    related="`FB_EL6851CommunicationEx`（通讯核心）、各专用 RDM FB（`FB_DMXGet*` / `FB_DMXSet*`，都是本 FB 的封装）、`E_DMXCommandClass` / `E_DMXParameterId`（枚举）",
    decl="""    fbSendRdm         : FB_DMXSendRDMCommand;         // 通用 RDM 命令发送
    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用
    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID
    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID
    byTargetPort      : BYTE := 0;                    // 根设备通道 0
    wTargetSubDevice  : WORD := 0;                    // 0 = 根设备
    eCmdClass         : E_DMXCommandClass;            // GET / SET ...
    eParamId          : E_DMXParameterId;             // 目标 PID
    byParamLen        : BYTE := 0;                    // 参数数据长度
    arrParamData      : ARRAY [0..255] OF BYTE;       // 参数数据
    bDoSend           : BOOL := FALSE;                // 在线给一次上升沿触发
    bBusy             : BOOL;
    bError            : BOOL;
    udiErrId          : UDINT;
    byRespMsgCount    : BYTE;                         // 设备排队消息数
    byRespLen         : BYTE;                         // 应答字节数
    arrRespData       : ARRAY [0..255] OF BYTE;       // 应答数据""",
    scen_c="某灯具支持厂商自定义 PID，库里没有专用 FB，需手工构造 RDM 命令读取。",
    val_c="按 RDM 标准填 CC/PID/参数即可发任意命令取回原始应答，覆盖全部 RDM 能力，无需等专用 FB。",
    ver_c="设好 eCmdClass / eParamId / arrParamData 后给 bDoSend 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 arrRespData[0..byRespLen-1] 是应答；用 GET 一个标准 PID（如 DEVICE_INFO）先验证链路。",
    call="""eCmdClass := eDMXCommandClassGetCommand;     // 示例：GET 命令
eParamId  := eDMXParameterIdDeviceInfo;      // 示例：读 DEVICE_INFO（标准 PID）
byParamLen := 0;                             // GET DEVICE_INFO 无参数数据

fbSendRdm(
    bStart                     := bDoSend,
    wDestinationManufacturerId := wTargetManufId,
    dwDestinationDeviceId      := dwTargetDeviceId,
    byPortId                   := byTargetPort,
    wSubDevice                 := wTargetSubDevice,
    eCommandClass              := eCmdClass,
    eParameterId               := eParamId,
    byParameterDataLength      := byParamLen,
    arrParameterData           := arrParamData,
    dwOptions                  := 0,
    stCommandBuffer            := stDmxCmdBuffer,
    bBusy                      => bBusy,
    bError                     => bError,
    udiErrorId                 => udiErrId,
    byResponseMessageCount     => byRespMsgCount,
    byResponseDataLength       => byRespLen,
    arrResponseData            => arrRespData
);""")

# ===========================================================================
# Device Control Parameter Message
# ===========================================================================
add("FB_DMXGetIdentifyDevice", section="4.1.2.2.1", cat="device_control", cat_label="Device Control Parameter Message",
    guid="{85a698f3-0eb3-56ae-b8de-91e4a5ca41cc}",
    summary="查询某个 DMX 设备的识别（identify）状态是否处于激活。识别激活时设备通常会闪烁或以其它可见方式提示自己，便于在一排灯里找到具体哪一台。",
    vardesc=base_in({"bIdentifyActive": "命令完成（`bBusy` 为 FALSE）后，给出该设备的识别状态：TRUE = 识别激活，FALSE = 未激活。"}),
    behavior="`bStart` 上升沿启动一次查询：`bBusy` 置 TRUE，功能块把 GET IDENTIFY_DEVICE 命令排入 `stCommandBuffer` 由通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令完成后 `bBusy` 落回 FALSE，`bIdentifyActive` 反映设备当前识别状态，`bError` / `udiErrorId` 可读。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则错误码 `0x800A`。",
    notes=["与 `FB_DMXSetIdentifyDevice` 配对：本 FB 只读状态，置位 / 复位识别用 Set 版。",
           "识别一般表现为灯具闪烁，但具体可见行为由设备厂商实现，不保证一致。（工程经验补充）"],
    scenario="一排外观相同的灯具中要确认 PLC 里某个 UID 到底对应现场哪一盏：先用 Set 让它进入识别（闪烁），用本 FB 回读确认识别已生效。",
    value="把识别状态做成可读接口，可在 HMI 上显示哪台设备正在识别，避免现场凭记忆判断。",
    alt=["不读状态、只发 Set：无法确认设备是否真的进入识别。",
         "现场人工目视：能看但进不了 PLC / HMI。",
         "**本 FB**：识别状态可编程读取。"],
    related="`FB_DMXSetIdentifyDevice`（置位 / 复位识别）、`FB_DMXGetDeviceInfo`（设备综合信息）",
    decl="    fbGetIdentify     : FB_DMXGetIdentifyDevice;      // 读识别状态\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    bIsIdentifying    : BOOL;                         // 设备识别是否激活",
    scen_c="一排相同灯具中确认某 UID 对应现场哪盏：回读识别状态确认其是否在闪。",
    val_c="把识别状态做成可读接口，HMI 上可显示哪台设备在识别，无需现场凭记忆判断。",
    ver_c="先用 FB_DMXSetIdentifyDevice 让目标灯进入识别，再给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 bIsIdentifying 应为 TRUE。",
    call="fbGetIdentify(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    bIdentifyActive            => bIsIdentifying\n);")

add("FB_DMXSetIdentifyDevice", section="4.1.2.2.2", cat="device_control", cat_label="Device Control Parameter Message",
    guid="{099c3999-926b-53e2-8084-072d029b61cb}",
    summary="激活或关闭某个 DMX 设备的识别（identify）。激活后设备会以可见方式（通常闪烁）标识自己，方便在现场一排灯中定位到 PLC 里的某个 UID。",
    vardesc=base_in({"bIdentify": "要设置的识别状态：TRUE = 激活识别，FALSE = 关闭识别。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET IDENTIFY_DEVICE 命令（携带 `bIdentify` 的目标状态）排入 `stCommandBuffer` 发出。`wDestinationManufacturerId` / `dwDestinationDeviceId` / `byPortId` 寻址目标设备及通道。命令完成后 `bBusy` 落回 FALSE，`bError` / `udiErrorId` 可读。`bIdentify` 默认 FALSE，因此不显式置位时本 FB 会关闭识别。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则错误码 `0x800A`。",
    notes=["与 `FB_DMXGetIdentifyDevice` 配对：本 FB 写状态，回读用 Get 版确认。",
           "`bIdentify` 默认 FALSE：忘记置位会把设备识别关掉，调试定位前记得设 TRUE。（工程经验补充）"],
    scenario="维护时要在几十台灯里找到 PLC 报警指向的那一台：对该 UID 发 `bIdentify := TRUE`，现场对应灯具开始闪烁，定位完再发 FALSE 关闭。",
    value="把让某台灯自报家门这一动作做成一次 PLC 调用，免去现场逐台拔插或对照地址表。",
    alt=["靠地址表 + 人工数通道：易错、慢。",
         "现场逐台断电观察：影响演出 / 运行。",
         "**本 FB**：点一下就让目标灯闪起来。"],
    related="`FB_DMXGetIdentifyDevice`（读识别状态）、`FB_DMXSetResetDevice`（复位设备）",
    decl="    fbSetIdentify     : FB_DMXSetIdentifyDevice;      // 置 / 复位识别\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bIdentifyOn       : BOOL := TRUE;                 // TRUE=进入识别(闪烁)\n"
         "    bDoSet            : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="维护时在几十台灯里找到 PLC 报警指向的那台：对该 UID 发识别(闪烁)，定位完再关。",
    val_c="把让某台灯自报家门做成一次 PLC 调用，免去现场逐台拔插或对照地址表。",
    ver_c="给 bDoSet 一次上升沿（bIdentifyOn=TRUE）-> bBusy 短暂 TRUE -> 回 FALSE 后现场目标灯应开始闪烁；改 bIdentifyOn=FALSE 再触发可关闭闪烁。",
    call="fbSetIdentify(\n"
         "    bStart                     := bDoSet,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    bIdentify                  := bIdentifyOn,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);")

add("FB_DMXSetResetDevice", section="4.1.2.2.3", cat="device_control", cat_label="Device Control Parameter Message",
    guid="{127ce2d4-32fe-50fb-bdb5-ca0bd71a858f}",
    summary="触发某个 DMX 设备执行复位（reset）。复位类型可选热复位（warm，默认）或冷复位（cold），用于让设备从异常状态恢复，相当于对单台灯具远程重启。",
    vardesc=base_in({"eResetDeviceType": "复位类型（见 `E_DMXResetDeviceType`），默认 `eDMXResetDeviceTypeWarm`（热复位）。"}),
    behavior="`bStart` 上升沿启动一次复位：`bBusy` 置 TRUE，功能块把 SET RESET_DEVICE 命令（携带 `eResetDeviceType` 指定的复位类型）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效。`eResetDeviceType` 取值超出有效范围会返回错误码 `0x8007`；热复位保留较多运行状态，冷复位更彻底。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略，持续高电平不会重复触发；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    errnote="`0x8007` 表示 `eResetDeviceType` 参数超出有效范围。",
    notes=["热复位（warm）保留更多运行状态，冷复位（cold）更彻底，相当于断电重启。按设备手册选择。",
           "复位会让设备短时离线，不要在演出 / 关键运行时段对在用灯具发复位。（工程经验补充）"],
    scenario="某盏灯通讯进入异常但物理可达，希望不用人去现场断电，直接从 PLC 远程复位让其恢复。",
    value="把远程重启单台设备这一操作做成一次调用，省去派人到现场或整段总线断电。",
    alt=["现场断电重启：要派人、且常常只能整组断电。",
         "整条 DMX 总线断电：影响所有灯。",
         "**本 FB**：精确复位单台设备。"],
    related="`FB_DMXSetIdentifyDevice`（识别）、`E_DMXResetDeviceType`（复位类型枚举）",
    decl="    fbResetDevice     : FB_DMXSetResetDevice;         // 远程复位单台设备\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    eResetKind        : E_DMXResetDeviceType := eDMXResetDeviceTypeWarm;  // 热复位\n"
         "    bDoReset          : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="某盏灯通讯异常但物理可达，不派人现场断电，直接从 PLC 远程复位恢复。",
    val_c="把远程重启单台设备做成一次调用，省去派人到现场或整段总线断电。",
    ver_c="给 bDoReset 一次上升沿（eResetKind=eDMXResetDeviceTypeWarm）-> bBusy 短暂 TRUE -> 回 FALSE 后目标设备应短时离线再恢复；若 bError 且 udiErrId=0x8007 说明复位类型越界。",
    call="fbResetDevice(\n"
         "    bStart                     := bDoReset,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    eResetDeviceType           := eResetKind,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);")

# ===========================================================================
# Discovery Messages
# ===========================================================================
add("FB_DMXDiscMute", section="4.1.2.3.1", cat="discovery", cat_label="Discovery Messages",
    guid="{854c123b-7889-5727-b841-be37d4fe319f}",
    summary="设置某个 DMX 设备的 mute（静音）标志。mute 标志决定该设备是否响应 `FB_DMXDiscUniqueBranch()` 命令：mute 未置位时响应，置位后不再响应。它是 RDM 二分发现协议的关键步骤——已找到的设备被 mute 掉，后续二分搜索就能聚焦到尚未发现的设备。",
    vardesc=base_in({"wControlField": "命令完成（`bBusy` 为 FALSE）后给出设备返回的控制字段（control field），其各位含义见 PDF 中的位定义表。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 DISCOVERY MUTE 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令完成后 `bBusy` 落回 FALSE，`wControlField` 给出设备的控制字段，`bError` / `udiErrorId` 可读。设备被 mute 后将不再响应 UniqueBranch 搜索，这正是二分发现得以收敛的机制。通常不直接调用本 FB，而是用高层 `FB_DMXDiscovery` / `FB_DMXDiscovery512` 自动完成整套 Mute/UnMute/UniqueBranch 流程。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。",
    notes=["**通常无需手动调用**：高层 `FB_DMXDiscovery` 已封装整套 Mute/UnMute/UniqueBranch 二分发现，仅在自写发现逻辑时才用本 FB。",
           "与 `FB_DMXDiscUnMute` 配对：本 FB 置位 mute，复位用 UnMute 版。",
           "`wControlField` 的各位（如 Managed Proxy / Sub-Device / Boot-Loader / Proxied Device 标志）见 PDF 位定义表。（工程经验补充）"],
    scenario="自行实现一套定制的 DMX 设备发现流程（例如只在某个 UID 子区间内搜索）时，需要手动 mute 已确认的设备以缩小搜索范围。",
    value="把 RDM 发现协议中的 mute 步骤暴露为单独 FB，给需要自定义发现策略的高级用户精细控制权。",
    alt=["直接用 `FB_DMXDiscovery`：自动完成全流程，绝大多数场景的首选。",
         "自己拼 `FB_DMXSendRDMCommand` 发 DISCOVERY MUTE：可行但要手填 CC/PID。",
         "**本 FB**：发现协议中 mute 步骤的专用封装。"],
    related="`FB_DMXDiscUnMute`（复位 mute）、`FB_DMXDiscUniqueBranch`（区间搜索）、`FB_DMXDiscovery`（高层自动发现）",
    decl="    fbDiscMute        : FB_DMXDiscMute;               // 置位设备 mute 标志\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoMute           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    wCtrlField        : WORD;                         // 设备返回的控制字段",
    scen_c="自写定制发现流程（如只在某 UID 子区间搜索）时，手动 mute 已确认设备以缩小搜索范围。",
    val_c="把 RDM 发现协议中的 mute 步骤暴露为单独 FB，给需要自定义发现策略的用户精细控制权。",
    ver_c="给 bDoMute 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 wCtrlField 有值；之后对同一设备发 FB_DMXDiscUniqueBranch 应不再得到响应（已被 mute）。",
    call="fbDiscMute(\n"
         "    bStart                     := bDoMute,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    wControlField              => wCtrlField\n);")

add("FB_DMXDiscUnMute", section="4.1.2.3.3", cat="discovery", cat_label="Discovery Messages",
    guid="{37766f8d-32c0-534f-82a0-c987cb4ecf80}",
    summary="复位某个 DMX 设备的 mute（静音）标志。mute 标志决定该设备是否响应 `FB_DMXDiscUniqueBranch()` 命令：mute 未置位时响应，置位后不响应。本 FB 把标志清掉，使设备重新参与二分发现搜索。",
    vardesc=base_in({"wControlField": "命令完成（`bBusy` 为 FALSE）后给出设备返回的控制字段（control field），其各位含义见 PDF 中的位定义表。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 DISCOVERY UN-MUTE 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令完成后 `bBusy` 落回 FALSE，`wControlField` 给出设备控制字段，`bError` / `udiErrorId` 可读。复位 mute 后设备重新响应 UniqueBranch 搜索，常用于开始一轮全新发现前把所有设备恢复到可被发现状态。通常由高层 `FB_DMXDiscovery` 自动调用。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。",
    notes=["**通常无需手动调用**：高层 `FB_DMXDiscovery` 已封装整套发现流程，仅在自写发现逻辑时才用本 FB。",
           "与 `FB_DMXDiscMute` 配对：本 FB 复位 mute，置位用 Mute 版。",
           "开始全新一轮发现前，对广播地址 UnMute 可让所有设备重新可被发现。（工程经验补充）"],
    scenario="自定义发现流程结束后，要把先前 mute 掉的设备全部恢复，以便下一轮搜索或让其它控制器也能发现它们。",
    value="把 RDM 发现协议中的 un-mute 步骤暴露为单独 FB，配合 Mute / UniqueBranch 实现完全自定义的发现策略。",
    alt=["直接用 `FB_DMXDiscovery`：自动管理 mute / un-mute，多数场景首选。",
         "自己拼 `FB_DMXSendRDMCommand` 发 DISCOVERY UN-MUTE：可行但要手填 CC/PID。",
         "**本 FB**：发现协议中 un-mute 步骤的专用封装。"],
    related="`FB_DMXDiscMute`（置位 mute）、`FB_DMXDiscUniqueBranch`（区间搜索）、`FB_DMXDiscovery`（高层自动发现）",
    decl="    fbDiscUnMute      : FB_DMXDiscUnMute;             // 复位设备 mute 标志\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoUnMute         : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    wCtrlField        : WORD;                         // 设备返回的控制字段",
    scen_c="自定义发现流程结束后，把先前 mute 掉的设备全部恢复，以便下一轮搜索或让其它控制器也能发现。",
    val_c="把 RDM 发现协议中的 un-mute 步骤暴露为单独 FB，配合 Mute / UniqueBranch 实现完全自定义的发现策略。",
    ver_c="先用 FB_DMXDiscMute 把目标设备 mute，再给 bDoUnMute 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后对该设备发 UniqueBranch 应又能得到响应。",
    call="fbDiscUnMute(\n"
         "    bStart                     := bDoUnMute,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    wControlField              => wCtrlField\n);")

add("FB_DMXDiscUniqueBranch", section="4.1.2.3.2", cat="discovery", cat_label="Discovery Messages",
    guid="{357ec525-39b9-5d78-b051-4faf5797c3dc}",
    summary="查询某个 UID 地址区间内是否存在 DMX 设备，是 RDM 二分发现协议的核心命令。给定 UID 下界和上界，所有 mute 未置位且 UID 落在区间内的设备都会响应；通过不断二分区间并 mute 已找到的设备，即可枚举出总线上的全部设备。",
    vardesc={"bStart": D_bStart, "byPortId": D_byPort, "dwOptions": D_dwOpt, "stCommandBuffer": D_buf,
             "bBusy": D_bBusy, "bError": D_bError, "udiErrorId": D_udiErr,
             "wLowerBoundManufacturerId": "搜索区间下界的厂商 ID 部分。",
             "dwLowerBoundDeviceId": "搜索区间下界的设备 ID 部分。",
             "wUpperBoundManufacturerId": "搜索区间上界的厂商 ID 部分。",
             "dwUpperBoundDeviceId": "搜索区间上界的设备 ID 部分。",
             "wReceivedManufacturerId": "命令完成后，若区间内恰有单个设备无冲突响应，给出其厂商 ID。",
             "dwReceivedDeviceId": "命令完成后，若区间内恰有单个设备无冲突响应，给出其设备 ID。"},
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 DISCOVERY UNIQUE_BRANCH 命令（携带由 `wLowerBoundManufacturerId` / `dwLowerBoundDeviceId` 与 `wUpperBoundManufacturerId` / `dwUpperBoundDeviceId` 构成的 UID 区间）排入 `stCommandBuffer` 发出，`byPortId` 指定通道。命令完成后 `bBusy` 落回 FALSE：若区间内仅一个设备响应（无冲突），其 UID 出现在 `wReceivedManufacturerId` / `dwReceivedDeviceId`；若多个设备同时响应会发生冲突，需把区间二分后分别再搜。配合 `FB_DMXDiscMute`（找到一个就 mute 掉）反复二分，即可遍历全部设备——这正是 `FB_DMXDiscovery` 内部所做的事。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。",
    notes=["**通常无需手动调用**：高层 `FB_DMXDiscovery` 已封装整套二分发现，仅在自写发现逻辑时才用本 FB。",
           "区间内多设备会冲突：要自己实现区间二分逻辑，找到一个就用 `FB_DMXDiscMute` 排除再继续。",
           "下界大于上界会返回 `0x8009`。（工程经验补充）"],
    scenario="实现一套带特殊约束的发现（例如只搜索某厂商 ID 段的灯具），需要手动控制每次搜索的 UID 区间。",
    value="把 RDM 二分发现的单步区间查询暴露出来，配合 Mute/UnMute 可实现任意自定义的设备枚举策略。",
    alt=["直接用 `FB_DMXDiscovery`：自动二分 + mute，覆盖绝大多数发现需求。",
         "用 `FB_DMXSendRDMCommand` 手发 DISCOVERY 命令：更底层、更繁琐。",
         "**本 FB**：发现协议中区间查询步骤的专用封装。"],
    related="`FB_DMXDiscMute` / `FB_DMXDiscUnMute`（mute 控制）、`FB_DMXDiscovery` / `FB_DMXDiscovery512`（高层自动发现）",
    decl="    fbUniqueBranch    : FB_DMXDiscUniqueBranch;       // UID 区间查询\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    wLowManuf         : WORD := 0;                    // 区间下界厂商 ID\n"
         "    dwLowDevice       : DWORD := 0;                   // 区间下界设备 ID\n"
         "    wUpManuf          : WORD := 16#FFFF;              // 区间上界厂商 ID（全范围）\n"
         "    dwUpDevice        : DWORD := 16#FFFFFFFF;         // 区间上界设备 ID（全范围）\n"
         "    bDoSearch         : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    wRecvManuf        : WORD;                         // 响应设备厂商 ID\n"
         "    dwRecvDevice      : DWORD;                        // 响应设备设备 ID",
    scen_c="实现带特殊约束的发现（如只搜某厂商 ID 段灯具），手动控制每次搜索的 UID 区间。",
    val_c="把 RDM 二分发现的单步区间查询暴露出来，配合 Mute/UnMute 可实现任意自定义的设备枚举策略。",
    ver_c="设好全范围区间（wLowManuf=0..dwUpDevice=16#FFFFFFFF），给 bDoSearch 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后若总线只一台未 mute 设备，wRecvManuf/dwRecvDevice 即其 UID；多台时会冲突需二分。",
    call="fbUniqueBranch(\n"
         "    bStart                    := bDoSearch,\n"
         "    byPortId                  := byTargetPort,\n"
         "    wLowerBoundManufacturerId := wLowManuf,\n"
         "    dwLowerBoundDeviceId      := dwLowDevice,\n"
         "    wUpperBoundManufacturerId := wUpManuf,\n"
         "    dwUpperBoundDeviceId      := dwUpDevice,\n"
         "    dwOptions                 := 0,\n"
         "    stCommandBuffer           := stDmxCmdBuffer,\n"
         "    bBusy                     => bBusy,\n"
         "    bError                    => bError,\n"
         "    udiErrorId                => udiErrId,\n"
         "    wReceivedManufacturerId   => wRecvManuf,\n"
         "    dwReceivedDeviceId        => dwRecvDevice\n);")

# ===========================================================================
# Power and Lamp Setting Parameter Messages
# ===========================================================================
add("FB_DMXGetLampHours", section="4.1.2.4.1", cat="power_lamp", cat_label="Power and Lamp Setting Parameter Messages",
    guid="{0b5a4f5e-d26d-57a6-b424-43a2a602ea10}",
    summary="读取某个 DMX 设备的灯泡（lamp）已点亮小时数。该计数器可用 `FB_DMXSetLampHours()` 编辑。常用于灯泡寿命管理——按累计点亮时长提示更换灯泡。",
    vardesc=base_in({"udiLampHours": "灯泡已点亮的小时数。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET LAMP_HOURS 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `udiLampHours` 给出灯泡累计点亮小时数，`bError` 与 `udiErrorId` 才有效。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略，持续高电平不会重复触发；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXSetLampHours` 配对：本 FB 只读，写 / 清零计数器用 Set 版。",
           "并非所有灯具都支持 LAMP_HOURS 参数；不支持时会返回 RDM 应答错误（`0x8010`）。（工程经验补充）"],
    scenario="剧场灯泡寿命管理：定期读取每盏灯的累计点亮时长，接近额定寿命时在 HMI 上提示运维更换，避免演出中途坏灯。",
    value="把灯泡寿命数据接入 PLC / HMI，实现预测性维护，无需人工逐台记录开灯时间。",
    alt=["人工记录每盏灯的使用时间：繁琐且易漏。",
         "等灯泡坏了再换：可能在演出关键时刻失效。",
         "**本 FB**：从灯具直接读累计小时数，自动化寿命管理。"],
    related="`FB_DMXSetLampHours`（写计数器）、`FB_DMXGetLampOnMode`（开灯行为）、`FB_DMXGetDeviceInfo`（设备综合信息）",
    decl="    fbGetLampHours    : FB_DMXGetLampHours;           // 读灯泡点亮小时数\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    udiHours          : UDINT;                        // 灯泡累计点亮小时数",
    scen_c="剧场灯泡寿命管理：定期读每盏灯累计点亮时长，接近寿命时 HMI 提示更换。",
    val_c="把灯泡寿命数据接入 PLC/HMI 实现预测性维护，无需人工逐台记录开灯时间。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 udiHours 即灯泡累计小时数；不支持该参数的灯会 bError 且 udiErrId=0x8010。",
    call="fbGetLampHours(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    udiLampHours               => udiHours\n);")

add("FB_DMXSetLampHours", section="4.1.2.4.3", cat="power_lamp", cat_label="Power and Lamp Setting Parameter Messages",
    guid="{4198e345-c2f5-588d-9020-8d8a8a76b07a}",
    summary="设置某个 DMX 设备的灯泡（lamp）已点亮小时数计数器。该计数器可用 `FB_DMXGetLampHours()` 读取。常用于换灯后把计数器清零，重新开始寿命统计。",
    vardesc=base_in({"udiLampHours": "要写入的灯泡点亮小时数，默认 0（换灯后清零）。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET LAMP_HOURS 命令（携带 `udiLampHours` 目标值）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效。`udiLampHours` 默认 0，因此不显式赋值时本 FB 会把计数器清零。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXGetLampHours` 配对：本 FB 写，读取用 Get 版。",
           "默认 `udiLampHours := 0`：换灯清零最常用；要回填历史时长则显式赋值。（工程经验补充）",
           "并非所有灯具支持写 LAMP_HOURS；不支持时返回 RDM 应答错误（`0x8015` / `0x8010`）。（工程经验补充）"],
    scenario="灯泡更换作业：换上新灯泡后把该灯具的点亮小时计数器清零，使后续寿命统计从 0 重新开始。",
    value="把换灯后的计数器复位做成一次 PLC 调用，保证寿命管理数据与实际灯泡同步。",
    alt=["不清零：寿命统计累计错误，提示更换的时机失真。",
         "靠外部台账手工记录换灯：与设备内计数器脱节。",
         "**本 FB**：直接写设备内计数器，数据一致。"],
    related="`FB_DMXGetLampHours`（读计数器）、`FB_DMXSetLampOnMode`（开灯行为）",
    decl="    fbSetLampHours    : FB_DMXSetLampHours;           // 写灯泡点亮小时数\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    udiNewHours       : UDINT := 0;                   // 换灯后清零\n"
         "    bDoSet            : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="灯泡更换作业：换新灯后把该灯具点亮小时计数器清零，寿命统计从 0 重新开始。",
    val_c="把换灯后的计数器复位做成一次 PLC 调用，保证寿命管理数据与实际灯泡同步。",
    ver_c="设 udiNewHours:=0，给 bDoSet 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后用 FB_DMXGetLampHours 回读应为 0。",
    call="fbSetLampHours(\n"
         "    bStart                     := bDoSet,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    udiLampHours               := udiNewHours,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);")

add("FB_DMXGetLampOnMode", section="4.1.2.4.2", cat="power_lamp", cat_label="Power and Lamp Setting Parameter Messages",
    guid="{74320089-d185-57d6-ad91-3a0caf6c4810}",
    summary="读取定义某个 DMX 设备开灯（switch-on）行为的参数。该值可用 `FB_DMXSetLampOnMode()` 编辑。开灯模式决定设备上电 / 收到 DMX 数据后灯泡如何点亮（如立即亮、收到数据才亮等）。",
    vardesc=base_in({"eLampOnMode": "设备当前的开灯模式（见 `E_DMXLampOnMode`）。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET LAMP_ON_MODE 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `eLampOnMode` 给出设备开灯模式枚举值，`bError` 与 `udiErrorId` 才有效。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略，持续高电平不会重复触发；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXSetLampOnMode` 配对：本 FB 只读，修改开灯模式用 Set 版。",
           "并非所有灯具支持 LAMP_ON_MODE 参数；不支持时返回 RDM 应答错误。（工程经验补充）"],
    scenario="调试灯具上电行为：核对每盏灯当前的开灯模式是否符合现场要求（例如要求收到 DMX 数据后才点亮，避免上电瞬间满亮刺眼）。",
    value="把开灯行为参数读进 PLC，便于在 HMI 上集中核对 / 显示，无需逐台进设备菜单查看。",
    alt=["进每台设备的本地菜单查看：逐台操作、慢。",
         "假定出厂默认：实际可能被改过，不可靠。",
         "**本 FB**：从设备直接读开灯模式。"],
    related="`FB_DMXSetLampOnMode`（写开灯模式）、`FB_DMXGetLampHours`（灯泡小时数）、`E_DMXLampOnMode`（枚举）",
    decl="    fbGetLampOnMode   : FB_DMXGetLampOnMode;          // 读开灯模式\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    eOnMode           : E_DMXLampOnMode;              // 当前开灯模式",
    scen_c="调试灯具上电行为：核对每盏灯当前开灯模式是否符合现场要求（如收到 DMX 数据后才亮）。",
    val_c="把开灯行为参数读进 PLC，便于在 HMI 集中核对/显示，无需逐台进设备菜单查看。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 eOnMode 即设备当前开灯模式枚举值。",
    call="fbGetLampOnMode(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    eLampOnMode                => eOnMode\n);")

add("FB_DMXSetLampOnMode", section="4.1.2.4.4", cat="power_lamp", cat_label="Power and Lamp Setting Parameter Messages",
    guid="{c062a242-20ca-54e0-ac2e-6ec36fe4332f}",
    summary="设置某个 DMX 设备的开灯（switch-on）行为。该值可用 `FB_DMXGetLampOnMode()` 读取。通过它可统一配置一批灯具上电 / 收到数据后的点亮策略。",
    vardesc=base_in({"eLampOnMode": "要设置的开灯模式（见 `E_DMXLampOnMode`），默认 `eDMXLampOnModeOff`。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET LAMP_ON_MODE 命令（携带 `eLampOnMode` 目标值）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效。`eLampOnMode` 默认 `eDMXLampOnModeOff`。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXGetLampOnMode` 配对：本 FB 写，回读用 Get 版确认。",
           "并非所有灯具支持写 LAMP_ON_MODE；不支持时返回 RDM 应答错误。（工程经验补充）"],
    scenario="批量配置一批新装灯具的上电行为，统一设为收到 DMX 数据后才点亮，避免上电瞬间所有灯满亮造成观众席刺眼或电网冲击。",
    value="把开灯策略下发做成 PLC 调用，可对全场灯具批量统一配置，无需逐台进本地菜单。",
    alt=["逐台进设备菜单设置：几十台灯耗时且易漏。",
         "接受出厂默认：可能不满足现场上电要求。",
         "**本 FB**：从 PLC 批量下发开灯模式。"],
    related="`FB_DMXGetLampOnMode`（读开灯模式）、`FB_DMXSetLampHours`（灯泡小时数）、`E_DMXLampOnMode`（枚举）",
    decl="    fbSetLampOnMode   : FB_DMXSetLampOnMode;          // 写开灯模式\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    eNewOnMode        : E_DMXLampOnMode := eDMXLampOnModeDMX;  // 仅收到 DMX 数据时点亮\n"
         "    bDoSet            : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="批量配置新装灯具上电行为，统一设为收到 DMX 数据后才点亮，避免上电满亮刺眼。",
    val_c="把开灯策略下发做成 PLC 调用，可对全场灯具批量统一配置，无需逐台进本地菜单。",
    ver_c="设 eNewOnMode，给 bDoSet 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后用 FB_DMXGetLampOnMode 回读应等于所设值。",
    call="fbSetLampOnMode(\n"
         "    bStart                     := bDoSet,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    eLampOnMode                := eNewOnMode,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);")

# ===========================================================================
# Queued and Status Messages
# ===========================================================================
add("FB_DMXGetStatusMessages", section="4.1.2.6.3", cat="status", cat_label="Queued and Status Messages",
    guid="{1f6969a5-4458-5004-a2cc-d3ced27274ab}",
    summary="收集某个 DMX 设备的状态或错误信息。设备内部把告警 / 警告 / 错误等事件以状态消息形式排队，本 FB 按 `eStatusType` 指定的级别一次性读出最多 25 条，填入状态消息数组，供 PLC 做集中故障诊断。",
    vardesc=base_in({
        "eStatusType": "要读取的状态消息级别（见 `E_DMXStatusType`），默认 `eDMXStatusTypeNone`。",
        "arrStatusMessages": "读到的状态消息数组（最多 25 条，索引 0..24）。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET STATUS_MESSAGES 命令（携带 `eStatusType` 过滤级别）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `arrStatusMessages[0..24]` 填入设备当前排队的状态消息（每条含状态 ID、子设备号等字段），`bError` 与 `udiErrorId` 才有效。`eStatusType` 可按 Advisory / Warning / Error 等级别过滤，只取关心的消息。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["**最多一次读 25 条**：消息更多时需多次读取或先处理再清。",
           "状态消息只给出状态 ID；可用 `FB_DMXGetStatusIdDescription` 把 ID 翻成可读文本。",
           "读完用 `FB_DMXClearStatusId` 清掉已处理消息，避免重复读到旧消息。（工程经验补充）"],
    scenario="灯光系统集中故障诊断：周期性轮询每盏灯的错误级状态消息，把灯泡故障、过温等事件汇总到中控 HMI 报警列表。",
    value="把分散在各灯具里的状态 / 错误信息统一收进 PLC，实现集中式故障监控，不必到每台设备本地查看。",
    alt=["逐台到设备本地面板看状态：现场分散、无法集中。",
         "只靠灯不亮的现象判断：被动且定位慢。",
         "**本 FB**：主动轮询设备状态消息，集中报警。"],
    related="`FB_DMXGetStatusIdDescription`（状态 ID 转文本）、`FB_DMXClearStatusId`（清消息）、`E_DMXStatusType` / `ST_DMXStatusMessage`",
    decl="    fbGetStatusMsgs   : FB_DMXGetStatusMessages;      // 读设备状态消息\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    eWantStatusType   : E_DMXStatusType := eDMXStatusTypeError;  // 只读错误级\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    arrStatusMsgs     : ARRAY [0..24] OF ST_DMXStatusMessage;  // 状态消息数组",
    scen_c="灯光系统集中故障诊断：周期轮询每盏灯的错误级状态消息，汇总到中控 HMI 报警列表。",
    val_c="把分散在各灯具的状态/错误信息统一收进 PLC，集中式故障监控，不必逐台本地查看。",
    ver_c="设 eWantStatusType:=eDMXStatusTypeError，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 arrStatusMsgs[0..] 含设备当前错误消息（无错误时为空）。",
    call="fbGetStatusMsgs(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    eStatusType                := eWantStatusType,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    arrStatusMessages          => arrStatusMsgs\n);")

add("FB_DMXGetStatusIdDescription", section="4.1.2.6.2", cat="status", cat_label="Queued and Status Messages",
    guid="{bc650127-fb21-5450-8445-6237d68276a8}",
    summary="读取某个状态 ID 在指定 DMX 设备中对应的文本描述。RDM 定义了一些标准状态消息，每条有唯一的状态 ID；本 FB 把该 ID 翻译成设备给出的可读文本，便于在 HMI 上显示人能看懂的故障说明。",
    vardesc=base_in({
        "uiStatusMessageId": "要查询的状态消息 ID，默认 1。",
        "sStatusMessage": "该状态 ID 对应的文本描述。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET STATUS_ID_DESCRIPTION 命令（携带 `uiStatusMessageId`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `sStatusMessage` 给出该状态 ID 的文本描述，`bError` 与 `udiErrorId` 才有效。它通常与 `FB_DMXGetStatusMessages` 配合：先读出状态消息列表得到一串状态 ID，再逐个用本 FB 翻成文本。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXGetStatusMessages` 配合：状态消息只含数字 ID，本 FB 负责翻成可读文本。",
           "`uiStatusMessageId` 默认 1；要查特定 ID 须显式赋值为 `FB_DMXGetStatusMessages` 读回的 ID。（工程经验补充）"],
    scenario="HMI 故障显示：把从设备读到的状态 ID（如某个告警码）转换成设备厂商提供的文本说明，直接显示给运维人员，无需查表。",
    value="把数字状态 ID 自动翻成人类可读文本，HMI 报警条目自解释，省去人工维护 ID-文本对照表。",
    alt=["自己维护 ID→文本对照表：厂商不同表不同，维护量大且易过时。",
         "只显示数字 ID：运维看不懂，要翻手册。",
         "**本 FB**：直接从设备取文本说明。"],
    related="`FB_DMXGetStatusMessages`（读状态消息 ID 列表）、`FB_DMXClearStatusId`（清消息）",
    decl="    fbGetStatusDesc   : FB_DMXGetStatusIdDescription; // 状态 ID 转文本\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    uiQueryStatusId   : UINT := 1;                    // 要查询的状态 ID\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    sStatusText       : STRING;                       // 状态 ID 对应文本",
    scen_c="HMI 故障显示：把从设备读到的状态 ID 转成厂商提供的文本说明直接显示给运维，无需查表。",
    val_c="把数字状态 ID 自动翻成人类可读文本，HMI 报警条目自解释，省去人工维护对照表。",
    ver_c="设 uiQueryStatusId 为 FB_DMXGetStatusMessages 读回的某个 ID，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 sStatusText 即该 ID 的文本描述。",
    call="fbGetStatusDesc(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    uiStatusMessageId          := uiQueryStatusId,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    sStatusMessage             => sStatusText\n);")

add("FB_DMXClearStatusId", section="4.1.2.6.1", cat="status", cat_label="Queued and Status Messages",
    guid="{64386ca4-84b2-5199-825c-1d1f4eefe324}",
    summary="清空某个 DMX 设备内部的消息缓冲区。设备会把告警 / 错误等事件排进状态消息缓冲区；处理完这些消息后用本 FB 清掉，避免下次读取时又读到已处理的旧消息。",
    vardesc=base_in(),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET CLEAR_STATUS_ID 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效，设备消息缓冲区被清空。它在故障处理闭环中扮演确认角色：读 → 处理 → 清，确保下一轮 `FB_DMXGetStatusMessages` 只拿到新发生的消息。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["**在故障处理闭环末尾调用**：读状态消息 → 上报 / 处理 → 用本 FB 清缓冲，否则旧消息会被反复读到。",
           "清的是设备端缓冲区，不影响 PLC 侧已读取的数据副本。（工程经验补充）"],
    scenario="故障处理闭环：PLC 读出某灯的状态消息并上报报警后，确认处理完毕时清掉该灯的消息缓冲，使后续轮询只反映新故障。",
    value="把设备消息缓冲的清除做成 PLC 调用，实现「读取—处理—清除」的标准故障闭环，避免重复报警。",
    alt=["不清缓冲：每轮都读到同样的旧消息，HMI 反复报同一故障。",
         "重启设备清状态：代价大且影响运行。",
         "**本 FB**：精确清掉已处理消息，闭环干净。"],
    related="`FB_DMXGetStatusMessages`（读状态消息）、`FB_DMXGetStatusIdDescription`（ID 转文本）",
    decl="    fbClearStatus     : FB_DMXClearStatusId;          // 清设备消息缓冲\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoClear          : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="故障处理闭环：PLC 读出某灯状态消息并上报后，确认处理完毕清掉该灯消息缓冲。",
    val_c="把设备消息缓冲清除做成 PLC 调用，实现读-处理-清的标准故障闭环，避免重复报警。",
    ver_c="先用 FB_DMXGetStatusMessages 确认有消息，给 bDoClear 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后再读 FB_DMXGetStatusMessages 应不再返回已清消息。",
    call="fbClearStatus(\n"
         "    bStart                     := bDoClear,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);")

# ===========================================================================
# Product Information Messages
# ===========================================================================
add("FB_DMXGetDeviceInfo", section="4.1.2.5.1", cat="product_info", cat_label="Product Information Messages",
    guid="{c76cb709-b81f-5755-9ef4-ef57ebe11bc8}",
    summary="查询某个 DMX 设备的全部关键信息，一次性返回一个 `ST_DMXDeviceInfo` 结构（含 RDM 协议版本、设备型号、产品类别、软件版本、DMX512 占用槽数、起始地址、子设备数、传感器数等）。是了解一台陌生设备能力的总入口。",
    vardesc=base_in({"stDMXDeviceInfo": "命令完成后返回的设备综合信息结构（见 `ST_DMXDeviceInfo`）。"}),
    behavior="`bStart` 上升沿启动一次查询：`bBusy` 置 TRUE，功能块把 GET DEVICE_INFO 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stDMXDeviceInfo` 填入设备综合信息，`bError` 与 `udiErrorId` 才有效。DEVICE_INFO 是 RDM 标准强制实现的核心 PID，几乎所有合规设备都支持，因此它是探测一台新设备能力的首选命令。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略，持续高电平不会重复触发；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["DEVICE_INFO 是 RDM 必备 PID，可作为探测设备是否在线、是否合规的基础命令。",
           "返回结构里的子设备数 / 传感器数告诉你后续可用哪些专用 FB（如有传感器才用 `FB_DMXGetSensorValue`）。（工程经验补充）"],
    scenario="接入一台不熟悉的第三方灯具时，先读 DEVICE_INFO 摸清它的型号、协议版本、占用多少 DMX 通道、有没有子设备和传感器，据此决定后续如何配置。",
    value="一次调用拿到设备全貌，免去逐个 PID 试探，是设备接入 / 自检流程的起点。",
    alt=["逐个发各类 GET 命令拼凑信息：调用多、慢。",
         "查设备纸质手册：信息可能与实际固件不符。",
         "**本 FB**：从设备直接读权威综合信息。"],
    related="`ST_DMXDeviceInfo`（返回结构）、`FB_DMXGetDeviceModelDescription` / `FB_DMXGetManufacturerLabel`（型号 / 厂商文本）、`FB_DMXGetSupportedParameters`（支持的 PID 列表）",
    decl="    fbGetDeviceInfo   : FB_DMXGetDeviceInfo;          // 读设备综合信息\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    stDeviceInfo      : ST_DMXDeviceInfo;             // 设备综合信息",
    scen_c="接入陌生第三方灯具时先读 DEVICE_INFO 摸清型号、协议版本、占用通道数、子设备/传感器情况。",
    val_c="一次调用拿到设备全貌，免去逐个 PID 试探，是设备接入/自检流程的起点。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 stDeviceInfo 各字段（如 DMX512 占用槽数、子设备数）有值；设备不在线则 bError 且 udiErrId=0x8002。",
    call="fbGetDeviceInfo(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    stDMXDeviceInfo            => stDeviceInfo\n);")

add("FB_DMXGetDeviceLabel", section="4.1.2.5.2", cat="product_info", cat_label="Product Information Messages",
    guid="{8e76b4c8-7f63-58e9-a7f2-386a57af3d1d}",
    summary="读取某个 DMX 设备中保存的设备标签文本（device label）——一段对设备更具体的人工描述，可用 `FB_DMXSetDeviceLabel()` 编辑。常用于给灯具起便于辨识的名字（如「舞台左侧 Par 灯 3」）。",
    vardesc=base_in({"sDeviceLabel": "从设备读到的设备标签文本。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET DEVICE_LABEL 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `sDeviceLabel` 给出设备里保存的标签文本，`bError` 与 `udiErrorId` 才有效。设备标签是写在设备非易失存储里的自定义名字，便于现场和 HMI 上辨识具体哪一台。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXSetDeviceLabel` 配对：本 FB 只读，命名用 Set 版。",
           "标签长度受设备实现限制，过长会被截断；具体上限见设备手册。（工程经验补充）"],
    scenario="HMI 设备列表显示：把每盏灯在设备里存的自定义标签读出来显示，让运维一眼看出「这是舞台左侧第 3 盏」而非只有一串 UID。",
    value="把人为可读的设备名读进 HMI，提升运维可读性，命名信息随设备走（换 PLC 也不丢）。",
    alt=["在 PLC 里维护 UID→名字映射表：换设备 / 改线就要同步维护。",
         "只显示 UID：运维记不住、辨识难。",
         "**本 FB**：名字存在设备里，读出即用。"],
    related="`FB_DMXSetDeviceLabel`（写标签）、`FB_DMXGetManufacturerLabel` / `FB_DMXGetDeviceModelDescription`（厂商 / 型号文本）",
    decl="    fbGetDeviceLabel  : FB_DMXGetDeviceLabel;         // 读设备标签\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    sLabel            : STRING;                       // 设备标签文本",
    scen_c="HMI 设备列表显示：把每盏灯在设备里存的自定义标签读出显示，让运维一眼辨识具体哪台。",
    val_c="把人为可读的设备名读进 HMI，提升运维可读性，命名信息随设备走（换 PLC 也不丢）。",
    ver_c="先用 FB_DMXSetDeviceLabel 写一个标签，再给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 sLabel 应等于所写文本。",
    call="fbGetDeviceLabel(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    sDeviceLabel               => sLabel\n);")

add("FB_DMXSetDeviceLabel", section="4.1.2.5.7", cat="product_info", cat_label="Product Information Messages",
    guid="{30f0139f-3cf4-5157-b611-714c896eac39}",
    summary="把一段描述文本写入某个 DMX 设备的设备标签（device label）。该文本可用 `FB_DMXGetDeviceLabel()` 读取。用于给灯具命名，名字存在设备非易失存储里，便于现场辨识。",
    vardesc=base_in({"sDeviceLabel": "要写入的设备标签文本，默认空串 `''`。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET DEVICE_LABEL 命令（携带 `sDeviceLabel` 文本）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效，文本被写入设备非易失存储。`sDeviceLabel` 默认空串，因此不显式赋值时会把标签清空。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXGetDeviceLabel` 配对：本 FB 写，回读用 Get 版确认。",
           "默认 `sDeviceLabel := ''`：忘记赋值会清空标签。（工程经验补充）",
           "文本过长会被设备截断；命名前查设备手册的标签长度上限。（工程经验补充）"],
    scenario="新装灯具调试时，按布局给每盏灯写入可读名字（如「舞台左侧 Par 灯 3」），写进设备本身，使后续任何控制器读到的都是统一名字。",
    value="把命名信息固化到设备里，实现一次命名、处处可读，比在各上位机里各自维护映射表更可靠。",
    alt=["在每个上位机 / PLC 里各自维护名字表：多处不一致。",
         "贴物理标签：人能看但程序读不到。",
         "**本 FB**：名字写进设备，随设备走、谁都能读。"],
    related="`FB_DMXGetDeviceLabel`（读标签）、`FB_DMXGetDeviceInfo`（设备综合信息）",
    decl="    fbSetDeviceLabel  : FB_DMXSetDeviceLabel;         // 写设备标签\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    sNewLabel         : STRING := 'Stage-Left-Par-3'; // 要写入的设备名\n"
         "    bDoSet            : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="新装灯具调试时按布局给每盏灯写可读名字（如 Stage-Left-Par-3），写进设备本身。",
    val_c="把命名信息固化到设备里，实现一次命名处处可读，比在各上位机各自维护映射表更可靠。",
    ver_c="设 sNewLabel，给 bDoSet 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后用 FB_DMXGetDeviceLabel 回读应等于所写文本。",
    call="fbSetDeviceLabel(\n"
         "    bStart                     := bDoSet,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    sDeviceLabel               := sNewLabel,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);")

add("FB_DMXGetDeviceModelDescription", section="4.1.2.5.3", cat="product_info", cat_label="Product Information Messages",
    guid="{7f24ba09-e867-5b58-a8f0-697599ef1c7a}",
    summary="查询某个 DMX 设备的设备型号描述文本（device model description）——厂商给出的型号说明字符串，只读、不可改。用于在 HMI 上显示设备的具体型号名称。",
    vardesc=base_in({"sDeviceModelDescription": "设备型号描述文本。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET DEVICE_MODEL_DESCRIPTION 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `sDeviceModelDescription` 给出厂商定义的型号描述文本，`bError` 与 `udiErrorId` 才有效。该文本由厂商固化、不能通过 RDM 修改，可作为资产盘点时识别设备型号的依据。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["只读：型号描述由厂商固化，无对应 Set FB。",
           "并非所有设备实现该 PID；不支持时返回 RDM 应答错误（`0x8010`）。（工程经验补充）"],
    scenario="资产盘点 / 备件管理：批量读出总线上每盏灯的型号描述，自动生成设备清单，便于采购对应备件。",
    value="把型号信息从设备直接读出，资产清单与现场实物一致，免去人工抄录。",
    alt=["人工拆灯看铭牌：费时且影响运行。",
         "凭安装记录：可能与实际换型号后不符。",
         "**本 FB**：从设备读权威型号描述。"],
    related="`FB_DMXGetManufacturerLabel`（厂商文本）、`FB_DMXGetDeviceInfo`（设备综合信息）、`FB_DMXGetSoftwareVersionLabel`（软件版本）",
    decl="    fbGetModelDesc    : FB_DMXGetDeviceModelDescription; // 读型号描述\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    sModelDesc        : STRING;                       // 型号描述文本",
    scen_c="资产盘点/备件管理：批量读出总线每盏灯的型号描述，自动生成设备清单便于采购备件。",
    val_c="把型号信息从设备直接读出，资产清单与现场实物一致，免去人工抄录。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 sModelDesc 即厂商型号描述文本；不支持该 PID 的设备 bError 且 udiErrId=0x8010。",
    call="fbGetModelDesc(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    sDeviceModelDescription    => sModelDesc\n);")

add("FB_DMXGetManufacturerLabel", section="4.1.2.5.4", cat="product_info", cat_label="Product Information Messages",
    guid="{3b9f0471-5e3a-5820-912c-a9591c2548a0}",
    summary="查询某个 DMX 设备的厂商描述文本（manufacturer label）——设备制造商名称字符串，只读。用于在 HMI / 资产清单中显示设备厂商。",
    vardesc=base_in({"sManufacturerLabel": "设备厂商描述文本。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET MANUFACTURER_LABEL 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `sManufacturerLabel` 给出厂商名称文本，`bError` 与 `udiErrorId` 才有效。它与设备 UID 高 16 位的厂商 ID 相对应，但返回的是人类可读的厂商名而非数字 ID，便于直接显示。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["只读：厂商名由制造商固化，无对应 Set FB。",
           "厂商 ID（UID 高 16 位）由 ESTA 分配，本 FB 返回的是其对应的可读名称。（工程经验补充）"],
    scenario="多品牌混装的灯光系统资产盘点：读出每盏灯的厂商名，配合型号描述生成完整的「厂商 + 型号」设备台账。",
    value="把厂商信息以可读文本读出，免去用数字厂商 ID 反查 ESTA 列表。",
    alt=["用厂商 ID 数字查 ESTA 在线表：要联网查表、繁琐。",
         "凭外观判断品牌：不可靠。",
         "**本 FB**：从设备直接读厂商名文本。"],
    related="`FB_DMXGetDeviceModelDescription`（型号文本）、`FB_DMXGetDeviceInfo`（设备综合信息）",
    decl="    fbGetManufLabel   : FB_DMXGetManufacturerLabel;   // 读厂商描述\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    sManufLabel       : STRING;                       // 厂商描述文本",
    scen_c="多品牌混装灯光系统资产盘点：读出每盏灯厂商名，配合型号描述生成完整厂商+型号台账。",
    val_c="把厂商信息以可读文本读出，免去用数字厂商 ID 反查 ESTA 列表。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 sManufLabel 即厂商名称文本。",
    call="fbGetManufLabel(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    sManufacturerLabel         => sManufLabel\n);")

add("FB_DMXGetSoftwareVersionLabel", section="4.1.2.5.6", cat="product_info", cat_label="Product Information Messages",
    guid="{88aeeff4-c3d5-5477-a798-ea2ab8319528}",
    summary="查询某个 DMX 设备的软件版本描述文本（software version label）——设备固件版本字符串，只读。用于核对设备固件版本，便于批量升级管理。",
    vardesc=base_in({"sSoftwareVersionLabel": "设备软件版本描述文本。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SOFTWARE_VERSION_LABEL 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `sSoftwareVersionLabel` 给出固件版本文本，`bError` 与 `udiErrorId` 才有效。该文本是厂商定义的可读版本说明，比 DEVICE_INFO 里的数字软件版本号更直观，可用于现场快速核对哪些设备需要升级。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["只读：固件版本由设备给出，无对应 Set FB。",
           "返回的是可读版本字符串；数字版本号在 `FB_DMXGetDeviceInfo` 的结构里。（工程经验补充）"],
    scenario="固件批量升级前的版本核对：读出总线上每盏灯的固件版本文本，筛出版本过旧、需要升级的设备。",
    value="把固件版本从设备直接读出，升级前能精确定位待升级设备，避免漏升或重复升。",
    alt=["逐台进设备菜单看版本：现场分散、慢。",
         "假定批次一致：实际可能混有不同固件。",
         "**本 FB**：从设备读权威固件版本文本。"],
    related="`FB_DMXGetDeviceInfo`（含数字软件版本号）、`FB_DMXGetDeviceModelDescription`（型号文本）",
    decl="    fbGetSwVersion    : FB_DMXGetSoftwareVersionLabel; // 读软件版本\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    sSwVersion        : STRING;                       // 软件版本文本",
    scen_c="固件批量升级前版本核对：读出总线每盏灯固件版本文本，筛出版本过旧需升级的设备。",
    val_c="把固件版本从设备直接读出，升级前能精确定位待升级设备，避免漏升或重复升。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 sSwVersion 即固件版本文本。",
    call="fbGetSwVersion(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    sSoftwareVersionLabel      => sSwVersion\n);")

add("FB_DMXGetProductDetailIdList", section="4.1.2.5.5", cat="product_info", cat_label="Product Information Messages",
    guid="{232f9d65-72c6-5942-b7ac-43748510f2a8}",
    summary="查询某个 DMX 设备所属的产品类别。RDM 定义了多种设备类别，每台设备最多可归入 6 个类别，类别由厂商指定、不能通过 RDM 修改。返回一个最多 6 元素的类别枚举数组。",
    vardesc=base_in({"arrProductDetails": "设备所属的产品类别数组（最多 6 个，见 `E_DMXProductDetail`）。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET PRODUCT_DETAIL_ID_LIST 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `arrProductDetails[1..6]` 填入设备所属的产品类别枚举（如调光器、换色器、烟机等），未用到的元素为默认值，`bError` 与 `udiErrorId` 才有效。这些类别由厂商固化、不可改，可用于按功能类型对设备分组。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["**最多 6 个类别**：数组上界 6，少于 6 类时多余元素为默认值。",
           "类别只读、厂商指定；并非所有设备实现该 PID。（工程经验补充）"],
    scenario="按功能给灯具自动分组：读出每台设备的产品类别，把调光器、染色灯、烟机等分别归类，供 HMI 分组显示或分组控制。",
    value="把设备功能类别从设备直接读出，可实现自动化的设备分类，免去人工按型号归类。",
    alt=["人工按型号归类：型号多时工作量大、易错。",
         "不分类、平铺显示：大型系统难管理。",
         "**本 FB**：从设备读功能类别自动分组。"],
    related="`E_DMXProductDetail`（类别枚举）、`FB_DMXGetDeviceInfo`（设备综合信息含产品类别字段）",
    decl="    fbGetProdDetails  : FB_DMXGetProductDetailIdList; // 读产品类别列表\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    arrProdDetails    : ARRAY [1..6] OF E_DMXProductDetail;  // 产品类别（最多 6）",
    scen_c="按功能给灯具自动分组：读出每台设备产品类别，把调光器/染色灯/烟机等分别归类供分组控制。",
    val_c="把设备功能类别从设备直接读出，可实现自动化设备分类，免去人工按型号归类。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 arrProdDetails[1..6] 含设备产品类别枚举值。",
    call="fbGetProdDetails(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    arrProductDetails          => arrProdDetails\n);")

# ===========================================================================
# RDM Information Messages
# ===========================================================================
add("FB_DMXGetParameterDescription", section="4.1.2.7.1", cat="rdm_info", cat_label="RDM Information Messages",
    guid="{564351a6-0ee8-50d9-a6cb-35db4e1e65d9}",
    summary="查询某个厂商自定义 PID（参数 ID）的定义。RDM 允许厂商定义标准之外的私有参数，本 FB 读回该 PID 的描述信息（数据类型、取值范围、单位、可读可写性、文本名称等），填入 `ST_DMXParameterDescription` 结构，使控制器无需厂商手册即可理解私有参数。",
    vardesc=base_in({
        "eParameterId": "要查询定义的参数 Id（见 `E_DMXParameterId`）。",
        "stParameterDescription": "返回的参数定义结构（见 `ST_DMXParameterDescription`）。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET PARAMETER_DESCRIPTION 命令（携带 `eParameterId`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stParameterDescription` 填入该 PID 的元信息（数据类型、命令类、PDL、取值上下限、单位、前缀、文本标签等），`bError` 与 `udiErrorId` 才有效。它只对厂商自定义 PID 有意义——标准 PID 的定义已固定在 RDM 规范里。配合 `FB_DMXGetSupportedParameters` 先列出设备支持哪些自定义 PID，再逐个用本 FB 取定义。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["**仅对厂商自定义 PID 有意义**：标准 PID 的定义由 RDM 规范固定，不需查询。",
           "配合 `FB_DMXGetSupportedParameters`：先拿到自定义 PID 列表，再逐个查定义。",
           "查询不被支持的 PID 会返回 RDM 应答错误。（工程经验补充）"],
    scenario="开发一个能适配任意品牌灯具的通用上位机：对每个厂商自定义 PID 先查定义，动态构建可读可写的参数编辑界面，无需为每个品牌单独写代码。",
    value="把厂商私有参数的元信息从设备读出，实现自描述式参数访问，做到一套程序适配多品牌设备。",
    alt=["为每个品牌硬编码 PID 含义：维护成本高，新设备就得改代码。",
         "只支持标准 PID：用不了厂商扩展功能。",
         "**本 FB**：运行时读 PID 定义，自适应任意设备。"],
    related="`FB_DMXGetSupportedParameters`（支持的 PID 列表）、`ST_DMXParameterDescription`（返回结构）、`FB_DMXSendRDMCommand`（按定义发自定义命令）",
    decl="    fbGetParamDesc    : FB_DMXGetParameterDescription; // 读 PID 定义\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    eQueryPid         : E_DMXParameterId;             // 要查定义的 PID\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    stParamDesc       : ST_DMXParameterDescription;   // PID 定义结构",
    scen_c="开发适配任意品牌的通用上位机：对每个厂商自定义 PID 先查定义，动态构建参数编辑界面。",
    val_c="把厂商私有参数元信息从设备读出，实现自描述式参数访问，一套程序适配多品牌设备。",
    ver_c="先用 FB_DMXGetSupportedParameters 取得一个自定义 PID 赋给 eQueryPid，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 stParamDesc 含该 PID 的类型/范围/文本等定义。",
    call="fbGetParamDesc(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    eParameterId               := eQueryPid,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    stParameterDescription     => stParamDesc\n);")

add("FB_DMXGetSupportedParameters", section="4.1.2.7.2", cat="rdm_info", cat_label="RDM Information Messages",
    guid="{55d8c689-efa0-53ac-ae09-4a158a618985}",
    summary="查询某个 DMX 设备支持的全部参数（PID）。返回一个最多 115 元素的 PID 枚举数组，列出该设备实现了哪些可选 / 厂商自定义参数，使控制器在访问参数前先确认其可用性。",
    vardesc=base_in({"arrParameters": "设备支持的参数 ID 数组（最多 115 个，索引 0..114，见 `E_DMXParameterId`）。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SUPPORTED_PARAMETERS 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `arrParameters[0..114]` 填入设备支持的 PID 枚举（不含 RDM 强制的核心 PID），`bError` 与 `udiErrorId` 才有效。它是动态适配设备的第一步：先拿到支持列表，再决定调用哪些专用 FB 或对哪些自定义 PID 调 `FB_DMXGetParameterDescription` 取定义。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["**最多 115 个 PID**：数组上界 114；列表不含 RDM 强制核心 PID（那些默认都支持）。",
           "用它做能力探测：访问可选参数前先确认设备支持，避免对不支持的 PID 发命令而报错。（工程经验补充）"],
    scenario="通用上位机适配设备：先读支持的 PID 列表，据此动态启用 / 隐藏功能按钮（如设备不支持传感器 PID，就不显示传感器读数界面）。",
    value="把设备能力清单从设备直接读出，实现按能力裁剪的自适应界面与控制逻辑，避免盲发命令报错。",
    alt=["不探测、对所有 PID 都试：大量命令失败、刷错误。",
         "按型号查手册定制：新设备就要改程序。",
         "**本 FB**：运行时读能力清单，自适应。"],
    related="`FB_DMXGetParameterDescription`（取自定义 PID 定义）、`FB_DMXGetDeviceInfo`（设备综合信息）、`E_DMXParameterId`（枚举）",
    decl="    fbGetSupported    : FB_DMXGetSupportedParameters; // 读支持的 PID 列表\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    arrSupportedPids  : ARRAY [0..114] OF E_DMXParameterId;  // 支持的 PID 列表",
    scen_c="通用上位机适配设备：先读支持的 PID 列表，据此动态启用/隐藏功能按钮。",
    val_c="把设备能力清单从设备直接读出，实现按能力裁剪的自适应界面与控制逻辑，避免盲发命令报错。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 arrSupportedPids 列出设备支持的可选 PID（数组前若干元素有效）。",
    call="fbGetSupported(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    arrParameters              => arrSupportedPids\n);")

# ===========================================================================
# Sensor Parameter Messages
# ===========================================================================
add("FB_DMXGetSensorDefinition", section="4.1.2.8.1", cat="sensor", cat_label="Sensor Parameter Messages",
    guid="{a25fa889-0331-5afa-90d2-530feeaf3da9}",
    summary="查询某个 DMX 设备内指定传感器的定义。一台设备可带多个传感器（温度、电压、风扇转速等），本 FB 按传感器编号读回该传感器的定义（类型、单位、量程上下限、是否支持记录最值等），填入 `ST_DMXSensorDefinition`，使控制器知道如何解释传感器读数。",
    vardesc=base_in({
        "bySensorNumber": "要查询的传感器编号，默认 0。",
        "stSensorDefinition": "返回的传感器定义结构（见 `ST_DMXSensorDefinition`）。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SENSOR_DEFINITION 命令（携带 `bySensorNumber`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stSensorDefinition` 填入该传感器的元信息（类型、单位、单位前缀、量程上下限、归一值、文本描述等），`bError` 与 `udiErrorId` 才有效。它是解释传感器读数的前提：先读定义知道单位和量程，再用 `FB_DMXGetSensorValue` 读实际值。设备的传感器数量可从 `FB_DMXGetDeviceInfo` 得知。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["`bySensorNumber` 默认 0（第一个传感器）；超出设备实际传感器数会返回错误码 `0x801B`。",
           "与 `FB_DMXGetSensorValue` 配合：先读定义拿单位 / 量程，再读值才能正确换算与显示。",
           "设备传感器数量见 `FB_DMXGetDeviceInfo` 返回结构。（工程经验补充）"],
    scenario="把灯具内置温度传感器接入监控：先读传感器定义拿到单位（摄氏度）和量程，HMI 才能把原始读数正确显示成带单位的温度。",
    value="把传感器的单位与量程从设备读出，使读数自带物理含义，免去为每个型号硬编码换算系数。",
    alt=["硬编码每个传感器的单位 / 量程：换设备就要改、易错。",
         "只显示原始数值：运维不知道是多少度 / 多少伏。",
         "**本 FB**：从设备读权威传感器定义。"],
    related="`FB_DMXGetSensorValue`（读传感器实时值）、`ST_DMXSensorDefinition`（返回结构）、`FB_DMXGetDeviceInfo`（传感器数量）",
    decl="    fbGetSensorDef    : FB_DMXGetSensorDefinition;    // 读传感器定义\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bySensorIndex     : BYTE := 0;                    // 第一个传感器\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    stSensorDef       : ST_DMXSensorDefinition;       // 传感器定义结构",
    scen_c="把灯具内置温度传感器接入监控：先读传感器定义拿单位(摄氏度)和量程，HMI 才能正确显示。",
    val_c="把传感器单位与量程从设备读出，使读数自带物理含义，免去为每个型号硬编码换算系数。",
    ver_c="设 bySensorIndex:=0，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 stSensorDef 含该传感器类型/单位/量程；编号越界则 bError 且 udiErrId=0x801B。",
    call="fbGetSensorDef(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    bySensorNumber             := bySensorIndex,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    stSensorDefinition         => stSensorDef\n);")

add("FB_DMXGetSensorValue", section="4.1.2.8.2", cat="sensor", cat_label="Sensor Parameter Messages",
    guid="{1fdfda82-6135-508a-9cf4-8613ba8490f1}",
    summary="读取某个 DMX 设备内指定传感器的当前值。按传感器编号返回 `ST_DMXSensorValue` 结构（含当前值及该传感器记录的最低 / 最高值）。配合 `FB_DMXGetSensorDefinition` 的单位 / 量程即可换算成带物理含义的读数。",
    vardesc=base_in({
        "bySensorNumber": "要读取的传感器编号，默认 0。",
        "stDMXSensorValue": "返回的传感器值结构（当前值 / 最低值 / 最高值，见 `ST_DMXSensorValue`）。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SENSOR_VALUE 命令（携带 `bySensorNumber`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stDMXSensorValue` 给出该传感器的当前值及记录的最低 / 最高值，`bError` 与 `udiErrorId` 才有效。返回的是原始整数值，需结合 `FB_DMXGetSensorDefinition` 的单位与量程换算成实际物理量。可周期触发以监控传感器趋势。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["`bySensorNumber` 默认 0；超出设备传感器数会返回错误码 `0x801B`。",
           "返回原始值：要配合 `FB_DMXGetSensorDefinition` 的单位 / 前缀换算成实际物理量。",
           "结构里含最低 / 最高值，可用于判断传感器是否曾越限。（工程经验补充）"],
    scenario="灯具过温保护监控：周期读取每盏灯的温度传感器当前值，超过阈值时在 PLC 里降功率或报警，防止灯具过热损坏。",
    value="把灯具内部传感器（温度 / 电压 / 风扇等）实时值接入 PLC，实现基于真实物理量的保护与预测性维护。",
    alt=["不监控传感器：过温 / 风扇故障只能等灯坏了才发现。",
         "外接独立温度探头：要额外硬件接线。",
         "**本 FB**：直接读灯具自带传感器值。"],
    related="`FB_DMXGetSensorDefinition`（传感器定义 / 单位 / 量程）、`ST_DMXSensorValue`（返回结构）、`FB_DMXGetStatusMessages`（设备状态 / 错误）",
    decl="    fbGetSensorVal    : FB_DMXGetSensorValue;         // 读传感器当前值\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bySensorIndex     : BYTE := 0;                    // 第一个传感器（如温度）\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    stSensorVal       : ST_DMXSensorValue;            // 传感器值结构",
    scen_c="灯具过温保护监控：周期读每盏灯温度传感器当前值，超阈值时 PLC 降功率或报警防过热。",
    val_c="把灯具内部传感器实时值接入 PLC，实现基于真实物理量的保护与预测性维护。",
    ver_c="设 bySensorIndex:=0，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 stSensorVal 含当前值/最低值/最高值；配合 FB_DMXGetSensorDefinition 的单位换算成实际温度。",
    call="fbGetSensorVal(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    bySensorNumber             := bySensorIndex,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    stDMXSensorValue           => stSensorVal\n);")

# ===========================================================================
# Setup Messages
# ===========================================================================
add("FB_DMXGetDMX512StartAddress", section="4.1.2.9.2", cat="setup", cat_label="Setup Messages",
    guid="{1fbe10b6-576b-5ab1-96b4-339b8e0b760c}",
    summary="查询某个 DMX 设备的 DMX512 起始地址。起始地址在 1–512 范围内；若设备不占用任何 DMX 槽，则返回 `0xFFFF`（65535）。每个子设备和根设备各占用不同的起始地址。",
    vardesc=base_in({"iDMX512StartAddress": "设备的 DMX512 起始地址（1–512）；不占用 DMX 槽时为 `0xFFFF`（65535）。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET DMX_START_ADDRESS 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `iDMX512StartAddress` 给出该设备占用的 DMX512 起始地址，`bError` 与 `udiErrorId` 才有效。起始地址决定设备从 DMX512 帧的哪个通道开始取数据；不占槽的纯 RDM 设备返回 `0xFFFF`。它与 `FB_DMXSetDMX512StartAddress` 配对，用于核对当前地址规划。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["与 `FB_DMXSetDMX512StartAddress` 配对：本 FB 只读，设地址用 Set 版。",
           "返回 `0xFFFF`（65535）表示设备不占 DMX 槽（纯 RDM 设备）。",
           "子设备与根设备地址不同，用 `byPortId` 区分。（工程经验补充）"],
    scenario="地址规划核对：上电后批量读出每盏灯的 DMX512 起始地址，与设计图纸比对，发现地址冲突或漂移及时纠正。",
    value="把现场实际起始地址读进 PLC 与设计值自动比对，避免因地址冲突导致多盏灯同动作。",
    alt=["逐台进设备菜单看地址：分散、慢。",
         "凭图纸假定：现场可能被人改过。",
         "**本 FB**：从设备读实际地址，自动核对。"],
    related="`FB_DMXSetDMX512StartAddress`（设起始地址）、`FB_DMXGetSlotInfo`（槽功能信息）、`FB_DMXGetDeviceInfo`（设备综合信息）",
    decl="    fbGetStartAddr    : FB_DMXGetDMX512StartAddress;  // 读起始地址\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    iStartAddr        : INT;                          // DMX512 起始地址(1-512;0xFFFF=不占槽)",
    scen_c="地址规划核对：上电后批量读出每盏灯 DMX512 起始地址，与设计图纸比对，发现冲突及时纠正。",
    val_c="把现场实际起始地址读进 PLC 与设计值自动比对，避免因地址冲突导致多盏灯同动作。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 iStartAddr 即设备起始地址(1-512)；纯 RDM 不占槽设备返回 0xFFFF(=-1 按 INT 显示或 65535)。",
    call="fbGetStartAddr(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    iDMX512StartAddress        => iStartAddr\n);")

add("FB_DMXSetDMX512StartAddress", section="4.1.2.9.5", cat="setup", cat_label="Setup Messages",
    guid="{c6c78fe4-8cb6-526e-83a0-bf1ca43ade48}",
    summary="设置某个 DMX 设备的 DMX512 起始地址，范围 1–512。每个子设备和根设备各占用不同的起始地址。它是把灯具编入 DMX 帧的关键——决定该设备从帧的哪个通道开始取自己的控制数据。",
    vardesc=base_in({"iDMX512Startadresse": "要设置的 DMX512 起始地址（1–512）。⚠️ 该形参名在 PDF 与库中拼作 `iDMX512Startadresse`（德式拼写，非 `iDMX512StartAddress`），调用时须按此拼写。"}),
    behavior="`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 SET DMX_START_ADDRESS 命令（携带目标起始地址）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `bError` 与 `udiErrorId` 才有效，设备起始地址被改写。起始地址必须落在 1–512，越界会返回错误码 `0x800B`，设置失败会返回 `0x800C`。本 FB 的目标地址形参在 PDF 与库中拼作 `iDMX512Startadresse`（德式拼写）。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    errnote="`0x800B` 表示地址超出 1–512；`0x800C` 表示设置 DMX512 起始地址失败。",
    notes=["**形参名是德式拼写 `iDMX512Startadresse`**（不是 `iDMX512StartAddress`）——这是 PDF 与库里的实际命名，写代码要照抄。",
           "与 `FB_DMXGetDMX512StartAddress` 配对：设完用 Get 版回读确认。",
           "地址范围 1–512，越界 `0x800B`；批量自动编址可改用高层 `FB_DMXDiscovery` 的 `SET_START_ADDRESS` 选项。（工程经验补充）"],
    scenario="新装或更换灯具后手动编址：按图纸给某盏灯设定它在 DMX 帧里的起始通道（如第 45 通道），使调光台对该地址段的控制落到这盏灯上。",
    value="把单台设备的 DMX512 编址做成一次 PLC 调用，配合回读实现可验证的地址配置，免去进设备菜单手拨。",
    alt=["进设备本地菜单手设地址：逐台操作、易设错。",
         "用高层 `FB_DMXDiscovery` 自动连续编址：适合批量，但不适合给单台设指定地址。",
         "**本 FB**：精确给指定设备设指定地址。"],
    related="`FB_DMXGetDMX512StartAddress`（读起始地址）、`FB_DMXDiscovery`（批量自动编址）、`FB_DMXGetSlotInfo`（槽功能）",
    decl="    fbSetStartAddr    : FB_DMXSetDMX512StartAddress;  // 设起始地址\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    iNewStartAddr     : INT := 45;                    // 目标起始地址(图纸指定第 45 通道)\n"
         "    bDoSet            : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;",
    scen_c="新装/更换灯具后手动编址：按图纸给某盏灯设定 DMX 帧起始通道(如第 45 通道)。",
    val_c="把单台设备 DMX512 编址做成一次 PLC 调用，配合回读实现可验证的地址配置，免去进菜单手拨。",
    ver_c="设 iNewStartAddr:=45（须在 1-512），给 bDoSet 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后用 FB_DMXGetDMX512StartAddress 回读应为 45；越界则 bError 且 udiErrId=0x800B。",
    call="// 注意：目标地址形参为德式拼写 iDMX512Startadresse（PDF/库中实际命名）\n"
         "fbSetStartAddr(\n"
         "    bStart                     := bDoSet,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    iDMX512Startadresse        := iNewStartAddr,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId\n);",
    warn=["`FB_DMXSetDMX512StartAddress` 的起始地址形参在 PDF 与库中拼作 `iDMX512Startadresse`（德式拼写），而对应的读取 FB `FB_DMXGetDMX512StartAddress` 输出却拼作 `iDMX512StartAddress`（英式）。两者拼写不一致是 Beckhoff 命名遗留，本文档按 PDF 原文逐字保留。"])

add("FB_DMXGetDMX512PersonalityDescription", section="4.1.2.9.1", cat="setup", cat_label="Setup Messages",
    guid="{9c94715c-aba1-5d02-b4b9-caa6da933c02}",
    summary="读取某个 DMX 设备某个 personality（个性 / 工作模式）的详细信息。部分 DMX 设备支持多个 personality，切换 personality 会改变设备占用的 DMX 通道数及部分 RDM 参数。本 FB 按 personality 编号返回其描述（占用槽数、文本说明），填入 `ST_DMX512PersonalityDescription`。",
    vardesc=base_in({
        "byPersonality": "要查询的 personality 编号，默认 0。",
        "stDMX512PersonalityDescription": "返回的 personality 描述结构（见 `ST_DMX512PersonalityDescription`）。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET DMX_PERSONALITY_DESCRIPTION 命令（携带 `byPersonality`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `stDMX512PersonalityDescription` 填入该 personality 占用的 DMX512 槽数与文本描述，`bError` 与 `udiErrorId` 才有效。personality 相当于设备的工作模式：不同模式占用的通道数不同（如 3 通道 RGB 模式 vs 8 通道扩展模式）。选定 personality 前可逐个读描述比较。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["personality 即设备工作模式：切换会改变占用的 DMX 通道数，进而影响地址规划。",
           "`byPersonality` 默认 0；遍历各 personality 描述可帮助选定合适的工作模式。（工程经验补充）",
           "并非所有设备支持多 personality；不支持时返回 RDM 应答错误。（工程经验补充）"],
    scenario="为支持多模式的灯具选工作模式：调试时遍历各 personality 的描述（看每种占多少通道、功能如何），据现场通道预算选定合适的一种。",
    value="把各工作模式的占用通道数与说明读出来集中比较，避免凭手册猜测、选错模式导致通道冲突。",
    alt=["查设备手册逐个对照 personality：手册可能与固件不符。",
         "盲选一个模式：可能与现场通道规划冲突。",
         "**本 FB**：从设备读各模式真实描述再选。"],
    related="`FB_DMXGetSlotInfo` / `FB_DMXGetSlotDescription`（槽功能 / 文本）、`ST_DMX512PersonalityDescription`（返回结构）、`FB_DMXGetDeviceInfo`（当前 personality）",
    decl="    fbGetPersDesc     : FB_DMXGetDMX512PersonalityDescription; // 读 personality 描述\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    byWantPersonality : BYTE := 1;                    // 查询 personality 1\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    stPersDesc        : ST_DMX512PersonalityDescription;  // personality 描述",
    scen_c="为多模式灯具选工作模式：遍历各 personality 描述(看占多少通道/功能)，据现场通道预算选定。",
    val_c="把各工作模式占用通道数与说明读出集中比较，避免凭手册猜测、选错模式导致通道冲突。",
    ver_c="设 byWantPersonality:=1，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 stPersDesc 含该 personality 占用槽数与文本说明。",
    call="fbGetPersDesc(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    byPersonality              := byWantPersonality,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    stDMX512PersonalityDescription => stPersDesc\n);")

add("FB_DMXGetSlotDescription", section="4.1.2.9.3", cat="setup", cat_label="Setup Messages",
    guid="{833da19f-a32f-5fc7-b622-67e51a2a961f}",
    summary="读取某个 DMX 设备某个槽（slot）偏移的文本描述。DMX 设备占用的每个 DMX512 槽对应一个功能（如 Red、Green、Dimmer、Pan 等），本 FB 按槽偏移返回该槽的人工可读名称，便于在 HMI 上把通道标注成具体功能。",
    vardesc=base_in({
        "iDMX512SlotOffset": "要查询的槽偏移，默认 0（范围 0–511）。",
        "sSlotDescription": "该槽偏移对应的功能文本描述。",
    }),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SLOT_DESCRIPTION 命令（携带 `iDMX512SlotOffset`）排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `sSlotDescription` 给出该槽偏移的功能文本（如 `Red`、`Dimmer`），`bError` 与 `udiErrorId` 才有效。槽偏移从设备起始地址算起：偏移 0 即设备占用的第一个通道。它与 `FB_DMXGetSlotInfo`（给出每槽的功能类型枚举）互补，本 FB 给的是可读文本。偏移越界返回错误码 `0x801A`。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    errnote="`0x801A` 表示 `iDMX512SlotOffset` 超出有效范围（0–511）。",
    notes=["`iDMX512SlotOffset` 默认 0（第一个槽），范围 0–511；越界返回 `0x801A`。",
           "与 `FB_DMXGetSlotInfo` 互补：Info 给功能类型枚举，本 FB 给可读文本名。",
           "槽偏移从设备起始地址算起，不是 DMX 帧绝对通道号。（工程经验补充）"],
    scenario="为操作员标注通道功能：读出某灯各槽的功能文本（Red/Green/Blue/Dimmer…），在 HMI 通道表里显示功能名而非裸通道号，降低误操作。",
    value="把每个 DMX 通道的功能名从设备读出，HMI 通道标注自动且准确，免去人工查手册填功能名。",
    alt=["人工查手册给每通道填功能名：型号多时工作量大且易错。",
         "只显示通道号：操作员不知道每通道控什么。",
         "**本 FB**：从设备读通道功能文本。"],
    related="`FB_DMXGetSlotInfo`（槽功能类型枚举）、`FB_DMXGetDMX512PersonalityDescription`（工作模式）、`E_DMXSlotType` / `E_DMXSlotDefinition`",
    decl="    fbGetSlotDesc     : FB_DMXGetSlotDescription;     // 读槽功能文本\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    iSlotOffset       : INT := 0;                     // 第一个槽(偏移 0)\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    sSlotText         : STRING;                       // 槽功能文本描述",
    scen_c="为操作员标注通道功能：读出某灯各槽功能文本(Red/Green/Dimmer…)，HMI 显示功能名而非裸通道号。",
    val_c="把每个 DMX 通道功能名从设备读出，HMI 通道标注自动且准确，免去人工查手册填功能名。",
    ver_c="设 iSlotOffset:=0，给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 sSlotText 即该槽功能文本；偏移越界则 bError 且 udiErrId=0x801A。",
    call="fbGetSlotDesc(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    iDMX512SlotOffset          := iSlotOffset,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    sSlotDescription           => sSlotText\n);")

add("FB_DMXGetSlotInfo", section="4.1.2.9.4", cat="setup", cat_label="Setup Messages",
    guid="{00d4dc3f-7161-5190-af99-b79a14c2194c}",
    summary="查询某个 DMX 设备各 DMX512 槽（slot）的基本功能信息。一次性返回一个最多 46 元素的 `ST_DMXSlotInfo` 数组，描述设备占用的每个槽的功能类型（如颜色、强度、位置等），使控制器了解每个 DMX 通道控制什么。",
    vardesc=base_in({"arrSlotInfos": "设备各 DMX512 槽的功能信息数组（最多 46 个，索引 0..45，见 `ST_DMXSlotInfo`）。"}),
    behavior="`bStart` 上升沿启动一次读取：`bBusy` 置 TRUE，功能块把 GET SLOT_INFO 命令排入 `stCommandBuffer`，由共享的通讯功能块发出。`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标设备，`byPortId` 指定设备内通道（根设备为 0）。命令执行完成后 `bBusy` 落回 FALSE，此时 `arrSlotInfos[0..45]` 填入设备各槽的功能信息（每项含槽类型、槽定义等），`bError` 与 `udiErrorId` 才有效。它一次给出全部槽的功能类型枚举，是把 DMX 帧通道映射到具体功能的基础；要拿可读文本名则配合 `FB_DMXGetSlotDescription`。必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）后续上升沿被忽略；发送 RDM 命令时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。",
    notes=["**最多 46 个槽**：数组上界 45；占用槽更多的设备需结合 personality 信息分析。",
           "给的是功能类型枚举；可读文本名用 `FB_DMXGetSlotDescription` 逐槽读取。",
           "与 personality 相关：切换 personality 后槽功能可能变化。（工程经验补充）"],
    scenario="自动构建通道映射表：一次读出某灯所有槽的功能类型，PLC 据此自动把各 DMX 通道关联到颜色 / 强度 / 位置等控制变量，无需人工逐通道配置。",
    value="一次调用拿到全部槽功能，自动化通道映射，比逐槽 `FB_DMXGetSlotDescription` 更快地建立通道—功能对应关系。",
    alt=["逐槽用 `FB_DMXGetSlotDescription`：要发多条命令、慢。",
         "人工查手册配通道映射：型号多时工作量大。",
         "**本 FB**：一次读全部槽功能类型。"],
    related="`FB_DMXGetSlotDescription`（单槽可读文本）、`FB_DMXGetDMX512PersonalityDescription`（工作模式）、`ST_DMXSlotInfo`（返回结构）",
    decl="    fbGetSlotInfo     : FB_DMXGetSlotInfo;            // 读各槽功能信息\n"
         "    stDmxCmdBuffer    : ST_DMXCommandBuffer;          // 与通讯 FB 共用\n"
         "    wTargetManufId    : WORD := 16#4241;              // 目标灯具厂商 ID\n"
         "    dwTargetDeviceId  : DWORD := 16#12131415;         // 目标灯具设备 ID\n"
         "    byTargetPort      : BYTE := 0;                    // 根设备通道 0\n"
         "    bDoRead           : BOOL := FALSE;                // 在线给一次上升沿触发\n"
         "    bBusy             : BOOL;\n    bError            : BOOL;\n    udiErrId          : UDINT;\n"
         "    arrSlotInfo       : ARRAY [0..45] OF ST_DMXSlotInfo;  // 各槽功能信息(最多 46)",
    scen_c="自动构建通道映射表：一次读出某灯所有槽功能类型，PLC 据此自动关联各 DMX 通道到控制变量。",
    val_c="一次调用拿到全部槽功能，自动化通道映射，比逐槽 FB_DMXGetSlotDescription 更快建立对应关系。",
    ver_c="给 bDoRead 一次上升沿 -> bBusy 短暂 TRUE -> 回 FALSE 后 arrSlotInfo[0..] 含设备各槽功能类型（占用 N 个槽则前 N 项有效）。",
    call="fbGetSlotInfo(\n"
         "    bStart                     := bDoRead,\n"
         "    wDestinationManufacturerId := wTargetManufId,\n"
         "    dwDestinationDeviceId      := dwTargetDeviceId,\n"
         "    byPortId                   := byTargetPort,\n"
         "    dwOptions                  := 0,\n"
         "    stCommandBuffer            := stDmxCmdBuffer,\n"
         "    bBusy                      => bBusy,\n"
         "    bError                     => bError,\n"
         "    udiErrorId                 => udiErrId,\n"
         "    arrSlotInfos               => arrSlotInfo\n);")
