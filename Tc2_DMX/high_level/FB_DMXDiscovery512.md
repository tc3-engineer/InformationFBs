# FB_DMXDiscovery512

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `High Level` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/498705035.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXDiscovery512.TcPOU`](../examples/P_Demo_FB_DMXDiscovery512.TcPOU) |

---

## 1. 功能简述

高层（High Level）设备搜索功能块，与 `FB_DMXDiscovery` 同源但搜索范围扩大到最多 512 个 DMX 设备，并可选地自动连续分配 DMX512 起始地址。它把底层 RDM 二分发现协议封装为一次触发即完成的批量发现，适合设备数量超过 50 的大型剧场 / 演艺中心总线。

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
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。 |
| `dwOptions` | `DWORD` | - | 选项位（见下表），多个常量用 OR 按位或起来。 |

`dwOptions` 可用常量：

| 常量 | 含义 |
|---|---|
| `DMX_OPTION_COMPLETE_NEW_DISCOVERY` | 把所有 DMX 设备都纳入搜索（完全重新发现）。 |
| `DMX_OPTION_SET_START_ADDRESS` | 为找到的所有 DMX 设备设置起始地址，从 1 开始连续分配。 |
| `DMX_OPTION_OPTICAL_FEEDBACK` | 找到某设备时调用 `IDENTIFY_DEVICE` 让其闪烁 2 秒做光学反馈。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                    : BOOL;
  bError                   : BOOL;
  udiErrorId               : UDINT;
  uliLowerBoundSearchUID   : T_ULARGE_INTEGER;
  uliUpperBoundSearchUID   : T_ULARGE_INTEGER;
  arrDMXDeviceInfoList     : ARRAY [1..512] OF ST_DMXDeviceInfo;
  uiNextDMX512StartAddress : UINT;
  iFoundDevices            : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `uliLowerBoundSearchUID` | `T_ULARGE_INTEGER` | 搜索过程中当前发送的搜索地址下界。 |
| `uliUpperBoundSearchUID` | `T_ULARGE_INTEGER` | 搜索过程中当前发送的搜索地址上界。 |
| `arrDMXDeviceInfoList` | `ARRAY [1..512] OF ST_DMXDeviceInfo` | 找到的 DMX 设备的关键信息数组（最多 512 个）。 |
| `uiNextDMX512StartAddress` | `UINT` | 若激活 `DMX_OPTION_SET_START_ADDRESS`，此处显示将分配给下一个设备的起始地址。 |
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

`bStart` 上升沿触发一次搜索：`bBusy` 置 TRUE，功能块通过 `stCommandBuffer` 排入一连串 RDM 发现命令（基于 Mute/UnMute + UniqueBranch 的二分式 UID 搜索），由共享的 `FB_EL6851CommunicationEx` 实例实际发出。与 `FB_DMXDiscovery` 的唯一区别是结果数组上界为 512 而非 50。搜索是异步过程，可能持续多个 PLC 周期；其间 `uliLowerBoundSearchUID` / `uliUpperBoundSearchUID` 反映当前二分查找区间，`iFoundDevices` 实时累加。完成后 `bBusy` 落回 FALSE，`arrDMXDeviceInfoList[1..iFoundDevices]` 填好各设备信息。`dwOptions` 控制自动编址、光学反馈、完全重搜。必须给 `bStart` 上升沿，持续高电平不会重复触发；发现期间配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。

## 4. 错误码 / 返回值

本功能块通过 `bError` + `udiErrorId` 报告错误。`udiErrorId = 0` 表示无错。Tc2_DMX 全库共用同一张命令专用错误码表（PDF §4.1.3 Error codes），常见值：

| 错误码（hex） | 十进制 | 含义 |
|---|---|---|
| `0x0000` | 0 | 无错误。 |
| `0x8001` | 32769 | DMX 端子无应答。 |
| `0x8002` | 32770 | DMX 设备无应答。 |
| `0x8003` | 32771 | 通讯缓冲区溢出。 |
| `0x8004` | 32772 | 通讯功能块无应答。 |
| `0x8005` | 32773 | `byPortId` 参数超出有效范围。 |
| `0x8006` | 32774 | 校验和错误。 |
| `0x8008` | 32776 | 超时。 |
| `0x800A` | 32778 | 端子处于 CycleMode，无法发送 RDM 命令。 |
| `0x800F` | 32783 | RDM 应答：RDM 报文应答无效。 |
| `0x8010` | 32784 | RDM 应答：设备未实现该命令，无法响应。 |
| `0x8016` | 32790 | RDM 应答：给定参数的值超范围或不支持。 |
| `0x801C` | 32796 | RDM 应答：参数数据（PD）过长，无法收全，需改用 `FB_EL6851CommunicationEx()`。 |

> 完整错误码表（含 `0x8007`–`0x801E` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。搜索若一直 `0x800A`，说明通讯功能块还停在 CycleMode；`0x8009` 表示搜索地址下界大于上界。

## 5. 使用注意 / 常见坑

- **必须配合一个通讯功能块实例**且共用同一个 `stCommandBuffer`；发现期间通讯功能块要处于非 CycleMode。
- **最多搜索 512 个设备**：超过部分不会被记录；设备数 ≤ 50 时用 `FB_DMXDiscovery` 数组更小。
- 搜索是异步的，要每周期调用并等 `bBusy` 落回 FALSE 后再读结果。（工程经验补充）
- `DMX_OPTION_OPTICAL_FEEDBACK` 让每个设备闪 2 秒，设备越多搜索总时长越长。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXDiscovery512.TcPOU`](../examples/P_Demo_FB_DMXDiscovery512.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：大型演艺中心 DMX 总线挂了上百台调光 / 染色灯，首次调试要一次性扫出全部设备并自动从 1 起连续编排起始地址。
- **价值**：一次触发即完成全总线扫描（最多 512 台）、收集设备信息并自动编址，底层二分发现协议全部隐藏，且不像 `FB_DMXDiscovery` 受 50 台上限约束。
- **替代方案对比**：
  - 用 `FB_DMXDiscovery`：实现相同但最多 50 台，设备多时不够用。
  - 自己用底层 `FB_DMXDiscMute`/`FB_DMXDiscUniqueBranch`/`FB_DMXDiscUnMute` 二分搜索：可行但要自写整套 UID 区间逻辑，易错。
  - **本功能块**：大规模总线一键发现 + 自动编址。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/498705035.html
- **相关 FB / FC**：`FB_DMXDiscovery`（≤50 台版本）、`FB_DMXDiscMute` / `FB_DMXDiscUniqueBranch` / `FB_DMXDiscUnMute`（底层发现命令）、`FB_EL6851CommunicationEx`（通讯核心）
