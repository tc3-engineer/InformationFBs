# FB_PcWatchDog_BAPI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Watchdog function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/2220165643.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PcWatchDog_BAPI.xml`](../examples/P_Demo_FB_PcWatchDog_BAPI.xml) |

---

## 1. 功能简述

FB_PcWatchDog_BAPI 通过 BIOS-API 启用 IPC 或 Embedded PC 的硬件看门狗，兼容所有支持 BIOS-API 的 Beckhoff 工控机。相比 `FB_PcWatchdog` 上限只能 255 秒，本 FB 的 `nWatchdogTimeS` 可达 15300 秒（255 分钟），适用于慢周期任务的恢复场景。通过 `bExecute` 上升沿启用，`nWatchdogTimeS ≥ 1` 才生效。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    nWatchdogTimeS : UDINT;
    bExecute : BOOL;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetID` | `T_AmsNetID` | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `nWatchdogTimeS` | `UDINT` | 看门狗超时时长，单位**秒**。范围 1–15300。 |
| `bExecute` | `BOOL` | TRUE 启用并喂狗；FALSE 禁用。 |
| `tTimeout` | `TIME` | ADS 调用超时（不同于看门狗超时），默认 `DEFAULT_ADS_TIMEOUT`。 |

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

**调用方式**：必须在循环任务里周期调用，调用周期需短于 `nWatchdogTimeS`。`bExecute = TRUE` 触发设置 + 喂狗动作。

**超时窗口**：`nWatchdogTimeS` 范围 1–15300 秒（约 4.25 小时）。超时后整机硬件复位。

**ADS 调用本质**：本 FB 通过 ADS 向 BIOS-API 设备发送写命令实现，所以有 `sNetID` / `tTimeout` 参数；本机用空 NetID。

**禁用方式**：`bExecute = FALSE` 或 `nWatchdogTimeS = 0`。在调试 / PLC Stop / 切换配置前同样**必须**显式禁用，否则会触发重启（PDF NOTICE 警告）。

**与 `FB_PcWatchdog` 区别**：本 FB 走 BIOS-API，主板支持更广；`FB_PcWatchdog` 直接读写芯片寄存器，只在特定主板生效。新工程优先选本 FB。

## 4. 错误码 / 返回值

本 FB 通过 `bError` + `nErrId` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`（**ADS Return Codes**）。

常见错误号（部分）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x70C` | 文件不存在 / 路径无效（ADSERR_DEVICE_NOTFOUND_FILE） |
| `0x70D` | 文件已存在（创建模式时） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| `0x1804` | 路径错误（FOPEN_MODEAPPEND 时常见，需路径已知） |
| 其他 | 见 Beckhoff ADS Return Codes 在线表 |

## 5. 使用注意 / 常见坑

- **调试务必禁用**：与 `FB_PcWatchdog` 一致——断点 / Reset 前 `bExecute := FALSE`。
- **`nWatchdogTimeS` 上限 15300 秒**：超出范围行为未定义，建议留 ≥ 10% 余量。
- **BIOS 不支持时静默失败**：老主板没有 BIOS-API 调用返回错误但不实际启用看门狗，需要在测试台先验证有效性。（工程经验补充）
- **调用周期必须短于超时**：每分钟一次的慢任务用 60 秒超时是边缘情况，建议至少 2 倍冗余（设 120 秒）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PcWatchDog_BAPI.xml`](../examples/P_Demo_FB_PcWatchDog_BAPI.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：慢工艺循环（如长达 10 分钟的烘干 / 热处理）的安全监护：超时 20 分钟，一旦工艺循环卡死自动重启。
- **价值**：比 `FB_PcWatchdog` 兼容主板更广 + 超时上限大 60 倍；现代工程的首选看门狗。
- **替代方案对比**：
  - `FB_PcWatchdog`：限定主板，超时 ≤ 255 秒。
  - 外置硬件看门狗：接线复杂但与 BIOS / OS 无关。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/2220165643.html
- **相关 FB / FC**：`FB_PcWatchdog`
