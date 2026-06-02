# FB_DMXDiscUniqueBranch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DMX` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Discovery Messages` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55175691.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DMXDiscUniqueBranch.TcPOU`](../examples/P_Demo_FB_DMXDiscUniqueBranch.TcPOU) |

---

## 1. 功能简述

查询某个 UID 地址区间内是否存在 DMX 设备，是 RDM 二分发现协议的核心命令。给定 UID 下界和上界，所有 mute 未置位且 UID 落在区间内的设备都会响应；通过不断二分区间并 mute 已找到的设备，即可枚举出总线上的全部设备。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart                    : BOOL;
  byPortId                  : BYTE;
  wLowerBoundManufacturerId : WORD;
  dwLowerBoundDeviceId      : DWORD;
  wUpperBoundManufacturerId : WORD;
  dwUpperBoundDeviceId      : DWORD;
  dwOptions                 : DWORD := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。 |
| `byPortId` | `BYTE` | - | 被寻址 DMX 设备内的通道；子设备（sub-device）通过 Port Id 寻址，根设备的 Port Id 恒为 0。 |
| `wLowerBoundManufacturerId` | `WORD` | - | 搜索区间下界的厂商 ID 部分。 |
| `dwLowerBoundDeviceId` | `DWORD` | - | 搜索区间下界的设备 ID 部分。 |
| `wUpperBoundManufacturerId` | `WORD` | - | 搜索区间上界的厂商 ID 部分。 |
| `dwUpperBoundDeviceId` | `DWORD` | - | 搜索区间上界的设备 ID 部分。 |
| `dwOptions` | `DWORD` | `0` | 选项（当前未使用）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  udiErrorId              : UDINT;
  wReceivedManufacturerId : WORD;
  dwReceivedDeviceId      : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。 |
| `bError` | `BOOL` | 命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。 |
| `udiErrorId` | `UDINT` | 最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。 |
| `wReceivedManufacturerId` | `WORD` | 命令完成后，若区间内恰有单个设备无冲突响应，给出其厂商 ID。 |
| `dwReceivedDeviceId` | `DWORD` | 命令完成后，若区间内恰有单个设备无冲突响应，给出其设备 ID。 |

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

`bStart` 上升沿启动：`bBusy` 置 TRUE，功能块把 DISCOVERY UNIQUE_BRANCH 命令（携带由 `wLowerBoundManufacturerId` / `dwLowerBoundDeviceId` 与 `wUpperBoundManufacturerId` / `dwUpperBoundDeviceId` 构成的 UID 区间）排入 `stCommandBuffer` 发出，`byPortId` 指定通道。命令完成后 `bBusy` 落回 FALSE：若区间内仅一个设备响应（无冲突），其 UID 出现在 `wReceivedManufacturerId` / `dwReceivedDeviceId`；若多个设备同时响应会发生冲突，需把区间二分后分别再搜。配合 `FB_DMXDiscMute`（找到一个就 mute 掉）反复二分，即可遍历全部设备——这正是 `FB_DMXDiscovery` 内部所做的事。必须给 `bStart` 上升沿，活动期间后续上升沿被忽略；发送时配套通讯功能块须处于非 CycleMode（`bSetCycleMode := FALSE`）。

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

> 完整错误码表（含 `0x8007`–`0x801E` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。

## 5. 使用注意 / 常见坑

- **通常无需手动调用**：高层 `FB_DMXDiscovery` 已封装整套二分发现，仅在自写发现逻辑时才用本 FB。
- 区间内多设备会冲突：要自己实现区间二分逻辑，找到一个就用 `FB_DMXDiscMute` 排除再继续。
- 下界大于上界会返回 `0x8009`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DMXDiscUniqueBranch.TcPOU`](../examples/P_Demo_FB_DMXDiscUniqueBranch.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：实现一套带特殊约束的发现（例如只搜索某厂商 ID 段的灯具），需要手动控制每次搜索的 UID 区间。
- **价值**：把 RDM 二分发现的单步区间查询暴露出来，配合 Mute/UnMute 可实现任意自定义的设备枚举策略。
- **替代方案对比**：
  - 直接用 `FB_DMXDiscovery`：自动二分 + mute，覆盖绝大多数发现需求。
  - 用 `FB_DMXSendRDMCommand` 手发 DISCOVERY 命令：更底层、更繁琐。
  - **本 FB**：发现协议中区间查询步骤的专用封装。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf) §4.1.2.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx/55175691.html
- **相关 FB / FC**：`FB_DMXDiscMute` / `FB_DMXDiscUnMute`（mute 控制）、`FB_DMXDiscovery` / `FB_DMXDiscovery512`（高层自动发现）
