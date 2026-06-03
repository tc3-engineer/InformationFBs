# FB_DMXDiscovery

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `High Level` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55169803.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXDiscovery.TcPOU`](../examples/P_Demo_FB_DMXDiscovery.TcPOU) |

---

## 1. 功能简述

高层（High Level）设备搜索功能块：在 DMX/RDM 总线上自动搜索最多 50 个 DMX 设备，并可选地自动为它们分配 DMX512 起始地址。搜索到的每个设备的关键信息（UID、厂商、起始地址等）填入一个 `ST_DMXDeviceInfo` 数组。它把底层的 RDM 发现命令（Mute / UniqueBranch / UnMute 二分查找）封装成一次"按一下就找全"的操作，是上电自检和总线巡检的首选入口。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart    : BOOL;
  dwOptions : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次搜索）。 |
| `dwOptions` | `DWORD` | - | 选项位（见下表），多个常量需用 OR 运算符按位或起来。 |

`dwOptions` 可用常量：

| 常量 | 含义 |
|---|---|
| `DMX_OPTION_COMPLETE_NEW_DISCOVERY` | 把所有 DMX 设备都纳入搜索（完全重新发现）。 |
| `DMX_OPTION_SET_START_ADDRESS` | 为找到的所有 DMX 设备设置起始地址，从 1 开始连续分配。 |
| `DMX_OPTION_OPTICAL_FEEDBACK` | 找到某设备时，调用 `IDENTIFY_DEVICE` 让其闪烁 2 秒做光学反馈。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                    : BOOL;
  bError                   : BOOL;
  udiErrorId               : UDINT;
  uliLowerBoundSearchUID   : T_ULARGE_INTEGER;
  uliUpperBoundSearchUID   : T_ULARGE_INTEGER;
  arrDMXDeviceInfoList     : ARRAY [1..50] OF ST_DMXDeviceInfo;
  uiNextDMX512StartAddress : UINT;
  iFoundDevices            : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `uliLowerBoundSearchUID` | `T_ULARGE_INTEGER` | 搜索过程中，当前发送的搜索地址下界。 |
| `uliUpperBoundSearchUID` | `T_ULARGE_INTEGER` | 搜索过程中，当前发送的搜索地址上界。 |
| `arrDMXDeviceInfoList` | `ARRAY [1..50] OF ST_DMXDeviceInfo` | 找到的 DMX 设备的关键信息数组。 |
| `uiNextDMX512StartAddress` | `UINT` | 若激活了 `DMX_OPTION_SET_START_ADDRESS`，此处显示将分配给下一个设备的起始地址。 |
| `iFoundDevices` | `INT` | 搜索过程中此处给出当前已找到的设备数量。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  stCommandBuffer : ST_DMXCommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCommandBuffer` | `ST_DMXCommandBuffer` | 与通讯功能块 `FB_EL6851Communication()` / `FB_EL6851CommunicationEx()` 交换命令的缓冲区结构引用。 |

## 3. 行为说明

`bStart` 上升沿触发一次搜索：`bBusy` 置 TRUE，功能块通过 `stCommandBuffer` 排入一连串 RDM 发现命令（基于 Mute/UnMute + UniqueBranch 的二分式 UID 搜索），由共享的 `FB_EL6851CommunicationEx` 实例实际发出。搜索是异步过程，可能持续多个 PLC 周期；其间 `uliLowerBoundSearchUID` / `uliUpperBoundSearchUID` 反映当前二分查找的地址区间，`iFoundDevices` 实时累加。完成后 `bBusy` 落回 FALSE，`arrDMXDeviceInfoList[1..iFoundDevices]` 填好各设备信息。`dwOptions` 控制行为：置 `DMX_OPTION_SET_START_ADDRESS` 时，找到的设备会被从 1 起连续编排 DMX512 起始地址，`uiNextDMX512StartAddress` 指示下一个待分配地址；置 `DMX_OPTION_OPTICAL_FEEDBACK` 时每找到一个设备就让它闪 2 秒便于现场目视核对；置 `DMX_OPTION_COMPLETE_NEW_DISCOVERY` 则忽略已有 Mute 状态做彻底重搜。**触发语义**：必须给 `bStart` 上升沿，持续高电平不会重复触发。出错时 `bError := TRUE`、`udiErrorId` 给出错误码（仅 `bBusy = FALSE` 时有效）。

## 4. 错误码 / 返回值

本功能块通过 `bError` + `udiErrorId` 报告错误。`udiErrorId = 0` 表示无错。Tc2_DMX 全库共用同一张命令专用错误码表（PDF §4.1.3 Error codes），与搜索相关的常见值：

| 错误码（hex） | 十进制 | 含义 |
|---|---|---|
| `0x0000` | 0 | 无错误。 |
| `0x8001` | 32769 | DMX 端子无应答。 |
| `0x8002` | 32770 | DMX 设备无应答。 |
| `0x8003` | 32771 | 通讯缓冲区溢出。 |
| `0x8004` | 32772 | 通讯功能块无应答。 |
| `0x8008` | 32776 | 超时。 |
| `0x8009` | 32777 | `uliLowerBoundUID` 参数大于 `uliUpperBoundUID` 参数。 |
| `0x800A` | 32778 | 端子处于 CycleMode，无法发送 RDM 命令。 |

> 完整错误码表（含 `0x8005`–`0x801E` 等校验和、参数越界、RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。搜索若一直 `0x800A`，说明通讯功能块还停在 CycleMode，需先退出 CycleMode 再发现。

## 5. 使用注意 / 常见坑

- **必须配合一个 `FB_EL6851CommunicationEx`（或旧版 `FB_EL6851Communication`）实例**，且二者共用同一个 `stCommandBuffer`；发现期间通讯功能块要处于非 CycleMode（`bSetCycleMode := FALSE`），否则得 `0x800A`。
- **最多搜索 50 个设备**：`arrDMXDeviceInfoList` 上界为 50，超过部分不会被记录。若总线设备更多需分段或改用底层发现 FB 自行管理。
- **搜索是异步的**：要每周期调用本功能块并等 `bBusy` 落回 FALSE 后再读 `arrDMXDeviceInfoList`，不能给一次 `bStart` 就立刻读结果。（工程经验补充）
- 用 `DMX_OPTION_SET_START_ADDRESS` 自动编址会改写现场设备的 DMX512 起始地址，调试期方便，但**生产环境慎用**——会覆盖人工设定的地址规划。（工程经验补充）
- `DMX_OPTION_OPTICAL_FEEDBACK` 让灯逐个闪 2 秒，会显著拉长搜索总时长（设备越多越久）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXDiscovery.TcPOU`](../examples/P_Demo_FB_DMXDiscovery.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：剧场布线完成后首次上电调试：工程师想知道 DMX 总线上到底接了哪些设备、各自的 UID 和起始地址，并希望系统自动把起始地址从 1 连续排好，省去逐台手设。
- **价值**：一次 `bStart` 就完成"扫描全总线 + 收集设备清单 + 自动编址 + 可选闪灯定位"，把底层繁琐的 RDM 二分发现协议（Mute/UnMute/UniqueBranch 反复二分）完全隐藏。
- **替代方案对比**：
  - 自己用 `FB_DMXDiscMute` / `FB_DMXDiscUniqueBranch` / `FB_DMXDiscUnMute` 实现二分搜索：可行但要自己写整套 UID 区间二分逻辑，易错。
  - 用专用 DMX/RDM 控台 / 手持设备扫描：能扫但结果进不了 PLC，无法自动化。
  - **本功能块**：PLC 内一键发现 + 自动编址，最省事。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55169803.html
- **相关 FB / FC**：`FB_DMXDiscovery512`（512 地址范围的发现）、`FB_DMXDiscMute` / `FB_DMXDiscUniqueBranch` / `FB_DMXDiscUnMute`（底层发现命令）、`FB_EL6851CommunicationEx`（通讯核心）
