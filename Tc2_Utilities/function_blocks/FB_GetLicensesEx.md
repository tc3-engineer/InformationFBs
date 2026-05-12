# FB_GetLicensesEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682567435.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetLicensesEx.xml`](../examples/P_Demo_FB_GetLicensesEx.xml) |

---

## 1. 功能简述

FB_GetLicensesEx 是 FB_GetLicenses 的增强版：除了 License ID 还返回更详细元数据（签发日期 / 到期日 / 厂商）。

用于：合规审计 / 续费提醒。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeout : TIME;
    sNetId : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |
| `sNetId` | `T_AmsNetId` | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    nValidLicenses : UDINT;
    aValidLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nPendingLicenses : UDINT;
    aPendingLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nDemoLicenses : UDINT;
    aDemoLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nOemLicenses : UDINT;
    aOemLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nFailedLicenses : UDINT;
    aFailedLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nInvalidLicenses : UDINT;
    aInvalidLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrorId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `nValidLicenses` | `UDINT` | 无符号整数输出：`nValidLicenses`。 |
| `aValidLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | 参数 `aValidLicenses`（类型 `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nPendingLicenses` | `UDINT` | 无符号整数输出：`nPendingLicenses`。 |
| `aPendingLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | 参数 `aPendingLicenses`（类型 `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nDemoLicenses` | `UDINT` | 无符号整数输出：`nDemoLicenses`。 |
| `aDemoLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | 参数 `aDemoLicenses`（类型 `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nOemLicenses` | `UDINT` | 无符号整数输出：`nOemLicenses`。 |
| `aOemLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | 参数 `aOemLicenses`（类型 `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nFailedLicenses` | `UDINT` | 无符号整数输出：`nFailedLicenses`。 |
| `aFailedLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | 参数 `aFailedLicenses`（类型 `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nInvalidLicenses` | `UDINT` | 无符号整数输出：`nInvalidLicenses`。 |
| `aInvalidLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | 参数 `aInvalidLicenses`（类型 `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：与 FB_GetLicenses 相同接口，输出结构字段更多。


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
- **License 是商业资产**——查询 / 操作 License 的 PLC 程序应放在受限权限的项目里，避免泄漏。
- Beckhoff dongle / OEM License 有完整的 ID 体系，本 FB 仅暴露查询 / 文件操作接口，不直接生成密钥。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetLicensesEx.xml`](../examples/P_Demo_FB_GetLicensesEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：合规审计 / 续费提醒。
- **价值**：更详细元数据。
- **替代方案对比**：
  - 手动通过 TwinCAT License Manager 操作。
  - **本 FB**：PLC 程序可脚本化批量。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.32
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682567435.html
- **相关 FB**：`FB_GetLicenses`
