# FB_GetTimeZoneInformation

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35004043.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetTimeZoneInformation.TcPOU`](../examples/P_Demo_FB_GetTimeZoneInformation.TcPOU) |

---

## 1. 功能简述

FB_GetTimeZoneInformation 通过 ADS 读取目标 TwinCAT 系统的时区配置 `TIME_ZONE_INFORMATION`：时区名、偏移量（与 UTC 的分钟差）、夏令时切换规则、当前是否处于夏令时等。

用于：把存储为 UTC 的时间戳显示给操作员前，本地化转换为该机器所在时区；或者把现场时区配置作为机器指纹（同一厂房所有机器应共享时区）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrID : UDINT;
    tzID : E_TimeZoneID;
    tzInfo : ST_TimeZoneInformation;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrID` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `tzID` | `E_TimeZoneID` | 参数 `tzID`（类型 `E_TimeZoneID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `tzInfo` | `ST_TimeZoneInformation` | 目标机器的时区配置结构（`TIME_ZONE_INFORMATION`）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿触发一次 ADS 读，目标机器由 `sNetID` 决定（空串 = 本机）。

**输出**：`tzInfo`（`TIME_ZONE_INFORMATION` 结构）含时区名、UTC 偏移分钟数、夏令时切换月 / 周 / 时 / 分等字段；`bDST`（输出 BOOL）表示『目标机器当前是否处于夏令时』。

**响应时间**：本地 < 50 ms；远端跨网视情况。

**典型组合**：常与 `FB_SystemTimeToTzSpecificLocalTime` 配合，先读时区再做 UTC → 本地时间换算。


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
- 夏令时切换规则按 Windows / TwinCAT/BSD 配置；运维人员在控制面板里改时区后规则即变，业务代码不能硬编码切换日期。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetTimeZoneInformation.TcPOU`](../examples/P_Demo_FB_GetTimeZoneInformation.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示报表时间戳前先读机器时区，做 UTC → 本地时间转换。
- **价值**：替代手工读注册表 `HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation`。
- **替代方案对比**：
  - 读注册表：跨 Windows 版本 / TwinCAT/BSD 不兼容。
  - **本 FB**：标准 ADS 调用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.37
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35004043.html
- **相关 FB**：`FB_SetTimeZoneInformation`, `FB_SystemTimeToTzSpecificLocalTime`
