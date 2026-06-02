# FB_PcWatchdog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Watchdog function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30968459.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PcWatchdog.TcPOU`](../examples/P_Demo_FB_PcWatchdog.TcPOU) |

---

## 1. 功能简述

FB_PcWatchdog 启用 IPC 主板上的硬件看门狗（仅限特定主板：IP-4GVI63、CB1050、CB2050、CB3050、CB1051、CB2051、CB3051）。`bEnable = TRUE` 后必须以**短于** `tTimeOut` 的周期持续调用本 FB；一旦超时未喂狗，硬件强制重启整台 PC。用于在 PLC / Windows 死循环或卡死时自动恢复系统。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    tTimeOut : TIME;
    bEnable : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `tTimeOut` | `TIME` | 看门狗超时时长（1–255 秒）。范围外行为未定义。 |
| `bEnable` | `BOOL` | TRUE 启用看门狗；FALSE 禁用。每周期保持 TRUE 即每周期喂狗。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bEnabled : BOOL;
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnabled` | `BOOL` | 布尔标志：`bEnabled`。具体语义见 §3 行为说明。 |
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；`bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 ADS Return Codes。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：必须在循环任务里每个周期调用一次。`bEnable = TRUE` 且 `tTimeOut ≥ 1s` 时启用；后续每次调用相当于『喂狗』重置超时计数。

**超时窗口**：`tTimeOut` 范围 1–255 秒。一旦超过该时长无新的 FB 调用，硬件触发整机重启（**不是** PLC 重启，是整台 PC 立即冷启动）。

**禁用方式**：`bEnable = FALSE` 或 `tTimeOut = 0` 关闭看门狗。在断点调试、PLC Reset、TwinCAT Stop、切换 Config 模式、激活配置前**必须**显式禁用，否则在调试中超时将导致 PC 重启（PDF NOTICE 明确警告）。

**硬件依赖**：本 FB 直接读写主板看门狗芯片，只在 PDF 列出的主板型号上生效；其他主板调用无实际效果。

**用途**：典型用法是在 PLC MAIN 程序末尾调用一次，超时定为 5–10 秒。PLC 程序一旦卡死（死循环、外部 ADS 死锁），看门狗 5 秒后强制 PC 重启，配合开机自启动 TwinCAT 即可实现无人值守自动恢复。

## 4. 错误码 / 返回值

本 FB 通过 `bError` + `nErrId` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`（**ADS Return Codes**）。

常见错误号（看门狗 / IOCTL 相关）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）——RTime 子系统未启用或 NetID 错 |
| `0x07` | 目标机器未找到——AMS 路由不通 |
| `0x701` | 设备服务未就绪——RTime 看门狗子系统暂不可用 |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）——硬件或路由阻塞 |
| 其他 | 见 Beckhoff ADS Return Codes 在线表 |

**注意**：本 FB 不操作文件系统，所以**不会**返回 `0x70C / 0x70D / 0x1804` 等文件错误码——遇到那类码请检查是不是另一个文件 FB 输出被错挂到这里。PDF 也未列硬件家族特定的错误号；列表外的码请实测后回查官方 ADS Return Codes 表（⚠️）。

## 5. 使用注意 / 常见坑

- **调试时务必禁用**：断点停 PLC 立即触发超时重启 PC，会丢失整个调试现场。建议加 `IF NOT bDebugMode THEN bEnable := TRUE; END_IF;`。
- **`tTimeOut` 不能太短**：< 2 秒在 Windows 任务繁忙时容易误触发；建议 5–10 秒。（工程经验补充）
- **仅限指定主板**：列表外的主板调用本 FB 无效，系统仍可能卡死。要更广兼容性用 `FB_PcWatchDog_BAPI`。
- **不能停 PLC 不喂狗**：PLC Stop / Reset / 配置激活前必须显式禁用，否则停 PLC 后看门狗仍跑，超时即重启。
- **重启不可逆**：硬件复位等同断电，所有未持久化数据丢失；要保数据建议配 `FB_S_UPS_*`（Tc2_SUPS 库）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PcWatchdog.TcPOU`](../examples/P_Demo_FB_PcWatchdog.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：生产线 7×24 无人值守，PLC 主程序末尾启用 8 秒看门狗。一旦 PLC 任务卡死（外部 ADS 死锁或第三方 DLL 异常），8 秒后整机自动重启恢复。
- **价值**：替代外置硬件看门狗模块（需额外接线 + IO 资源），用主板内置芯片实现相同功能。不用本 FB 时只能依赖外部 watchdog timer 或人工巡检。
- **替代方案对比**：
  - 外置看门狗模块（接 DI/DO）：需额外接线，但兼容性广。
  - `FB_PcWatchDog_BAPI`：基于 BIOS-API，主板支持面更广，超时上限 15300 秒。
  - 软件看门狗（PLC 内部计时）：能检测部分卡死，但无法处理 PLC 自身崩溃。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30968459.html
- **相关 FB / FC**：`FB_PcWatchDog_BAPI`, `FB_S_UPS_CB3011`
