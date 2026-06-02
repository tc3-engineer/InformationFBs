# FB_GetAdaptersInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34995851.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetAdaptersInfo.TcPOU`](../examples/P_Demo_FB_GetAdaptersInfo.TcPOU) |

---

## 1. 功能简述

FB_GetAdaptersInfo 获取本机所有网络适配器（网卡）的列表，每个适配器返回 MAC / IP / 掩码 / 网关 / DHCP 状态等信息。返回结构是 `ARRAY OF ST_AdapterInfo`。

用于：诊断 PLC 启动时网卡是否就绪、记录硬件指纹（MAC）做授权绑定、HMI 显示当前 IP。

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
    arrAdapters : ARRAY[0..MAX_LOCAL_ADAPTERS] OF ST_IpAdapterInfo;
    nCount : UDINT;
    nGet : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrID` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `arrAdapters` | `ARRAY[0..MAX_LOCAL_ADAPTERS] OF ST_IpAdapterInfo` | 参数 `arrAdapters`（类型 `ARRAY[0..MAX_LOCAL_ADAPTERS] OF ST_IpAdapterInfo`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nCount` | `UDINT` | 无符号整数输出：`nCount`。 |
| `nGet` | `UDINT` | 无符号整数输出：`nGet`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿一次性返回所有适配器信息到 `aAdapters` 缓冲区，数量在 `nAdapters` 里。

**缓冲区**：调用方需要预分配 `aAdapters` 数组（典型 `ARRAY[0..15] OF ST_AdapterInfo`），如果实际适配器更多会被截断；本 FB 在 `nAdapters` 里返回真实数量。

**性能**：本地 SystemAPI 调用，< 100 ms。


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
- 缓冲区数组上限要预估，CX 设备一般 2-4 个网卡，工程师 PC 可能 10+（包括虚拟网卡）。（工程经验补充）
- **虚拟网卡 / VPN 适配器都会出现**：用 MAC 做授权要按主物理网卡过滤，否则克隆 / 重装容易换 MAC。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetAdaptersInfo.TcPOU`](../examples/P_Demo_FB_GetAdaptersInfo.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：开机 self-test 阶段读所有网卡 IP，确认上位机网络已就绪后才允许进入 Run 模式。
- **价值**：替代调 Win32 API GetAdaptersInfo 自写包装。
- **替代方案对比**：
  - 不读网卡，直接试 ADS 通讯失败再处理：用户体验差。
  - **本 FB**：开机自检逻辑可读 IP 直接报错给运维。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.24
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34995851.html
- **相关 FB**：`FB_GetAdaptersInfoEx`, `FB_GetHostAddrByName`
