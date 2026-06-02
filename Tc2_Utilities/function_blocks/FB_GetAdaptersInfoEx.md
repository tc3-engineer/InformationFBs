# FB_GetAdaptersInfoEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682552715.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetAdaptersInfoEx.TcPOU`](../examples/P_Demo_FB_GetAdaptersInfoEx.TcPOU) |

---

## 1. 功能简述

FB_GetAdaptersInfoEx 是 FB_GetAdaptersInfo 的增强版：返回的 `ST_AdapterInfoEx` 比 `ST_AdapterInfo` 多了 IPv6 地址、适配器类型（Ethernet / WiFi / Loopback）、DNS Server 列表等字段。

新项目建议直接用 Ex 版本，可向后兼容 IPv6 环境。

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
    nErrorID : UDINT;
    nAdapters : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrorID` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `nAdapters` | `UINT` | 无符号整数输出：`nAdapters`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：与 FB_GetAdaptersInfo 完全一致——`bExecute` 上升沿，一次性填充 `aAdapters` 数组。

**输出结构**：`ST_AdapterInfoEx` 包含 IPv4 + IPv6 + 适配器类型 + DNS 服务器列表，比原版字段多。


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

- **Windows 系统调用，跨网段 ADS 时长比本地慢**——本地调用 < 50 ms，跨网段可能 500 ms+。（工程经验补充）
- **返回字符串编码**：主机名 / 域名通常 ASCII，跨语言系统（中文 Windows）可能带本地编码字节，处理 UI 显示前要确认编码。（工程经验补充）
- `bExecute` 上升沿触发，不要持续高电平当作连续读——会被忽略。
- PDF 未列错误码——按通用 ADS Return Codes 对照（参考 Beckhoff 在线表）。
- 调用前 `bDone` / `bErr` 输出保留上一次结果，业务代码不要在 `bExecute` 还没触发就读输出。（工程经验补充）
- IPv6 地址字符串可能长达 39 字符（不含前缀），缓冲区要 `STRING(45)` 起步。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetAdaptersInfoEx.TcPOU`](../examples/P_Demo_FB_GetAdaptersInfoEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：混合 IPv4 / IPv6 部署的客户机房，需要列举所有 IP 地址做白名单。
- **价值**：比原版多 IPv6 / DNS 等字段。
- **替代方案对比**：
  - FB_GetAdaptersInfo：仅 IPv4。
  - **本 FB**：IPv4 + IPv6。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.25
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682552715.html
- **相关 FB**：`FB_GetAdaptersInfo`
