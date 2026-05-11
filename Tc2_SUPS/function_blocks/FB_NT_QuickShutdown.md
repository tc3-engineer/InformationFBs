# FB_NT_QuickShutdown

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/9007199285238027.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NT_QuickShutdown.xml`](../examples/P_Demo_FB_NT_QuickShutdown.xml) |

---

## 1. 功能简述

`FB_NT_QuickShutdown` 是 Tc2_SUPS 的**内部使用 FB**：它的职责是「不停 TwinCAT、不走 Windows 关机流程，直接让控制器立即重启」——也就是 1-second UPS 路径上断电应急的最后一步。`FB_S_UPS_*` 系列在 retain 写完后调用本 FB 完成实际的重启动作。

**PDF 与 InfoSys 均明确警告：本 FB 不可被业务代码独立调用**。原因是业务代码独立调本 FB 不会先调用 `SPDM_2PASS` 持久化，等于强制重启时 retain 还没刷盘 → 数据丢失。**只有 `FB_S_UPS_*` 系列内部使用本 FB 才是安全的**——它们已经把"写 retain → 等待写完 → 触发本 FB"的正确顺序写好。

本文档存在的意义是：**让工程师知道这是内部 FB、避免误用**，同时记录其接口供 Beckhoff 内部维护参考。如果你的需求是"软关机"或"软重启"，请用 Tc2_System 库的 `NT_Shutdown` / `NT_Reboot` 走标准 Windows 流程。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | — | 控制器 AmsNetID（空串表示本机）。Quick shutdown 通常只对本机有意义 |
| `START` | `BOOL` | — | 上升沿触发一次立即重启。**触发时 retain 未保证已落盘**——本 FB 不做任何"先存盘"的工作 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时；触发 quick shutdown 的 ADS 调用等待回执的时间窗 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY  : BOOL;
    ERR   : BOOL;
    ERRID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | quick shutdown 触发命令仍在执行（ADS 回执未回 / 系统未真正重启）时为 `TRUE` |
| `ERR` | `BOOL` | 出错时为 `TRUE`（与 IEC 61131 命名习惯一致；与 `FB_S_UPS_BAPI` 的 `bError` 字段不同，这里没有 PDF 笔误） |
| `ERRID` | `UDINT` | 错误号（仅当 `ERR = TRUE` 时有意义）。具体取值表 PDF 与 InfoSys 均未列出 ⚠️ |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发方式**：`START` 上升沿。`BUSY` 立刻置 `TRUE`，FB 通过内部 ADS 向 TwinCAT 系统服务发送 quick shutdown 命令；命令送达后系统在毫秒级内重启（TwinCAT 不走 Windows 关机流程，等同于硬复位但有序释放硬件状态）。

**与 Windows 关机的差异**：
- `NT_Shutdown`（Tc2_System 库）：调 Windows API，停服务、关进程、关文件句柄、然后断电。耗时 30 秒到几分钟。**不适合 1-second UPS 路径**（电容根本撑不到 Windows 关服务结束）。
- `FB_NT_QuickShutdown`（本 FB）：跳过 Windows，TwinCAT 直接触发硬件重启路径，毫秒级完成。**只在「retain 已经存好、系统状态可以从 retain 恢复」的前提下才安全**。

**为什么 PDF 警告「会导致数据丢失」**：本 FB 不调用任何 `SPDM_*` 持久化模式；它仅触发重启信号。所以独立调用 = 强制硬复位 = 当时所有未刷盘的变量丢失（包括所有非 RETAIN 变量、以及虽是 RETAIN 但当前周期还没被持久化的部分）。`FB_S_UPS_*` 系列已经处理了"先 `SPDM_2PASS` 把 retain 写完，确认完成后再触发本 FB"的顺序，所以由它们调用是安全的。

**典型时序**（在 `FB_S_UPS_*` 内部）：
1. `FB_S_UPS_*` 检测掉电 → 触发 `SPDM_2PASS` 写 retain
2. 等到 `SPDM_2PASS` 完成（FB 内部观察 ADS 回执）
3. 设置内部状态 `eState := eSUPS_QuickShutdown`
4. 给本 `FB_NT_QuickShutdown` 实例的 `START` 上升沿
5. 本 FB 触发系统重启；`BUSY = TRUE`
6. 几个周期后系统重启；PLC 进程结束

## 4. 错误码 / 返回值

`ERR` / `ERRID` 输出对的语义：

| `ERR` | 含义 |
|---|---|
| `FALSE` | 命令已下发、`BUSY` 表示是否还在执行 |
| `TRUE` | 触发 quick shutdown 失败，`ERRID` 给出错误号 |

⚠️ PDF §4.6 与 InfoSys topic 9007199285238027 均未列出具体 `ERRID` 取值表。常见可能错误（基于 ADS 通用错误号推测）：
- `0x745` (1861)：ADS timeout（TMOUT 太短或系统服务无响应）
- `0x7`：未知 AMS port（NETID 错或控制器未运行 TwinCAT）

具体故障建议联系 Beckhoff 支持并提供 `ERRID` 数值，本 FB 是内部组件，公开错误表 Beckhoff 未发布。

## 5. 使用注意 / 常见坑

- **不要在业务代码里独立调用本 FB**：PDF 明确警告会导致数据丢失。**所有断电应急场景都应通过 `FB_S_UPS_*` 系列**（它会在 retain 刷完后自动调本 FB）。
- **不要把本 FB 当"软重启"用**：软重启请用 Tc2_System 的 `NT_Reboot`（走 Windows 关机流程，干净）；本 FB 是「半硬复位」级别。
- **如果误调用本 FB 导致 retain 丢失**：恢复手段只有从最近的备份回填 + 人工对单。Beckhoff 不能恢复内存里未持久化的数据。
- **`TMOUT` 一般保持默认**：本 FB 仅在 1-second UPS 紧急路径上被调用，那种场景下 ADS 系统服务通常仍然能立即响应，默认 `DEFAULT_ADS_TIMEOUT`（约 5s）够用。
- **`BUSY` 看到 TRUE 之后系统会很快重启**（工程经验补充）：所以业务代码看到 `BUSY = TRUE` 也来不及做"通知 HMI"之类的事——真要做就要在更早的 `eState := eSUPS_WritePersistentData` 阶段做。
- **本 FB 没有 `bExecute` 配对的 `bDone`**（工程经验补充）：因为成功的"完成态"就是系统重启，PLC 进程已经不在了，没有运行时机回报 `bDone`。
- **`NETID` 跨机重启在工业现场几乎用不上**（工程经验补充）：tested 多次但运营上极少出现"远程让另一台 PLC 紧急重启"的需求；几乎所有使用都是本机 `NETID := ''`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NT_QuickShutdown.xml`](../examples/P_Demo_FB_NT_QuickShutdown.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)
>
> **⚠️ 警告**：本例程仅用于演示接口结构。**实际工程中不要这样直接调用本 FB**——会导致 retain 数据丢失。请改用 `FB_S_UPS_*` 系列。

```iecst
// 场景：本例程用于"读懂接口"，演示 FB_NT_QuickShutdown 的输入输出。
//       在线测试时不要真的给 bTriggerEmergencyReboot 置 TRUE——系统会立即
//       重启而 retain 没存。看完接口结构请改用 FB_S_UPS_* 系列。
//
// 价值：让工程师知道这个 FB 存在、知道它危险、知道它的接口长什么样、不至于
//       在 Tc2_SUPS 库列表里看到时不知道是什么。
//
// 验证：登录运行 → 在线把 bTriggerEmergencyReboot 置 TRUE 一次（仅在台架
//       且 retain 不重要时） → 系统在 100-500 ms 内重启。注意：实际工程
//       不要这么做，使用 FB_S_UPS_* 自动管理。
PROGRAM P_Demo_FB_NT_QuickShutdown
VAR
    fbQuickShutdown            : FB_NT_QuickShutdown;
    sLocalNetIDForReboot       : T_AmsNetId := '';     // 本机
    bTriggerEmergencyReboot    : BOOL := FALSE;        // ⚠️ 上升沿即重启
    tShutdownAdsTimeout        : TIME := DEFAULT_ADS_TIMEOUT;
    bQuickShutdownBusy         : BOOL;
    bQuickShutdownError        : BOOL;
    nQuickShutdownErrID        : UDINT;
END_VAR
fbQuickShutdown(
    NETID := sLocalNetIDForReboot,
    START := bTriggerEmergencyReboot,
    TMOUT := tShutdownAdsTimeout,
    BUSY  => bQuickShutdownBusy,
    ERR   => bQuickShutdownError,
    ERRID => nQuickShutdownErrID
);
```

## 7. 业务场景与实际价值

- **场景**：本 FB **不是给业务工程师用的**——它是 Tc2_SUPS 内部组件，由 `FB_S_UPS_*` 系列在断电应急路径上自动调用。本文档列出它的接口是为了「文档完整性 + 避免误用」。
- **价值**：理解 1-second UPS 应急路径的最后一环。当读者看到 `FB_S_UPS_*` 的 `eState = eSUPS_QuickShutdown` 时，知道这是本 FB 在内部跑。调试时若发现"retain 写完了但系统没重启"，可以推测 `FB_NT_QuickShutdown` 出错（`ERR/ERRID`）——但实际上 `FB_S_UPS_*` 不暴露这些，需要 Beckhoff 现场支持。
- **替代方案对比**：
  - **业务直接用本 FB**：❌ 错误用法，PDF 明确禁止
  - **业务用 `FB_S_UPS_*`**：✅ 正确，retain → quick shutdown 顺序被保证
  - **业务用 `NT_Reboot` / `NT_Shutdown`（Tc2_System）**：✅ 用于非紧急的软重启 / 软关机，走 Windows 流程
- **若工程"必须"用本 FB**：唯一合法场景是 Beckhoff 自己在 Tc2_SUPS 库内部维护。第三方代码不应触及。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §4.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/9007199285238027.html
- **相关 FB**：所有 `FB_S_UPS_*`（本 FB 的合法调用方）、`NT_Reboot` / `NT_Shutdown`（Tc2_System，软重启替代）
