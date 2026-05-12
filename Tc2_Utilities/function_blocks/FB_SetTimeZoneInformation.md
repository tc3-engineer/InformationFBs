# FB_SetTimeZoneInformation

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35022475.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SetTimeZoneInformation.xml`](../examples/P_Demo_FB_SetTimeZoneInformation.xml) |

---

## 1. 功能简述

FB_SetTimeZoneInformation 通过 ADS 写入目标 TwinCAT 系统的时区配置，改变其时区偏移与夏令时切换规则。批量部署时统一所有机器时区用得到。

成功调用后目标机器立刻应用新时区——Windows 系统时钟显示会跳变到新时区，所有时间戳逻辑也跟着变。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    tzInfo : ST_TimeZoneInformation;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `tzInfo` | `ST_TimeZoneInformation` | - | 要写入的时区结构。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrID` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿触发一次 ADS 写。要把 `tzInfo` 填好 `TIME_ZONE_INFORMATION` 结构再调。

**生效**：调用成功后目标机器立刻应用，影响所有依赖系统时区的程序（包括 Windows 服务、其他 TwinCAT 程序）。

**权限**：通常需要管理员权限（取决于 TwinCAT Engineering Mode 配置），非管理员调用会 `bErr = TRUE`。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` + `nErrId`（或 `bError` + `nErrorId`）输出报告错误：

- `bErr / bError = FALSE` 且 `nErrId / nErrorId = 0`：本次请求成功。
- `bErr / bError = TRUE`：本次请求失败，错误号在 `nErrId / nErrorId`。

常见错误号属于 **ADS Return Codes**（PDF 与 InfoSys 都引用此表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x07` | 目标机器未找到（ADSERR_DEVICE_INVALIDDATA） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| 其他 | PDF 未枚举，详见 Beckhoff 在线 ADS Return Codes 表 ⚠️ |

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **修改时区是系统级影响**——会让所有依赖系统时间的程序（日志、定时任务）瞬间产生时间跳变；生产环境务必走审批。
- `tzInfo` 结构里的切换日期字段是 Windows 的 `SYSTEMTIME` 表达法（wMonth + wDay 周次 + wDayOfWeek），不是直接的日期；细节见 Beckhoff InfoSys `TIME_ZONE_INFORMATION` 文档。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SetTimeZoneInformation.xml`](../examples/P_Demo_FB_SetTimeZoneInformation.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把出厂默认 UTC 时区的 PLC 批量改成『中国标准时间』并应用。
- **价值**：批量 commissioning 工具替代手工进每台机器控制面板改时区。
- **替代方案对比**：
  - 手动进每台机器改控制面板时区：人工成本高。
  - **本 FB**：PLC 程序批量统一。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.57
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35022475.html
- **相关 FB**：`FB_GetTimeZoneInformation`
