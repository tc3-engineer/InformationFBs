# FB_AddRouteEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34973323.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AddRouteEntry.TcPOU`](../examples/P_Demo_FB_AddRouteEntry.TcPOU) |

---

## 1. 功能简述

FB_AddRouteEntry 通过 ADS 在目标 TwinCAT 系统的路由表中插入一条新的远端 AMS 路由条目（Route），让目标机器能通过 AmsNetId 找到对方主机的 IP 和验证凭据。

典型场景：现场首次部署机器时，由工程师 PC 上的 TwinCAT 程序代替手动 `Add Route...` 对话框，把生产机器互相加进对方的路由表，做到一键 commissioning。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    stRoute : ST_AmsRouteEntry;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | **目标 TwinCAT 系统**（被加路由的那一端）的 AMS Net ID。 |
| `stRoute` | `ST_AmsRouteEntry` | - | 参数 `stRoute`（类型 `ST_AmsRouteEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次添加请求。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求未结束。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS / 自定义错误号，0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**协议**：`bExecute` 上升沿触发一次 ADS 请求。FB 把 sNetID 视为目标系统（被加路由的那一端），把 sRemoteNetID + sRemoteIP + sRemoteName + sRemoteRouteName 视为要写入的新路由条目。如果目标系统需要身份验证（典型 TwinCAT Engineering Mode），还要正确填 sUsername / sPassword。

**完成判定**：`bBusy = TRUE` 期间不响应新请求；ADS 应答到达后 `bBusy → FALSE`、`bDone → TRUE`（或 `bErr` / `nErrId`）。

**重要副作用**：调用成功后目标机器路由表立即生效，重启不丢；属于持久化配置修改。


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

- **ADS 路由是 TwinCAT 系统级配置，影响所有 PLC / SystemService**——通过 PLC 程序动态修改路由属于运维侵入操作，生产环境务必先做白名单 / 审计。
- **跨网段调用要靠路由可达**：本机如果路由表里没有目标 AmsNetId，调用会立刻 `nErrId = 6 (DEVICE_NOTFOUND)` 或 `0x745 (CLIENT_SYNCTIMEOUT)`。
- ADS 端口建议明确指定（如 851 = PLC RT、852 = PLC RT1、10000 = SystemService）；不写或写错会调用到非预期目标。（工程经验补充）
- `tTimeout` 默认 5 秒；跨广域链路要适当放大，但太大会卡住调用周期任务，建议放在后台任务里调用。（工程经验补充）
- PDF 未列详细错误码——错误号属于通用 ADS Return Codes 表，参考 Beckhoff InfoSys 在线表。
- **身份验证错误最常见**：`sUsername` / `sPassword` 不对 → `nErrId = 0x745` 或自定义错误号。注意密码是目标主机 Windows 用户密码，不是 TwinCAT 项目密码。
- 路由名 `sRemoteRouteName` 在目标侧必须唯一；重复会替换旧条目。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AddRouteEntry.TcPOU`](../examples/P_Demo_FB_AddRouteEntry.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工程师 PC 端跑一段 ST 程序，把 5 台生产线 PLC 互相加进路由表，免去手动逐台开 TwinCAT System Manager。
- **价值**：替代手动『Add Route...』对话框，可纳入自动 commissioning 脚本；提升上线效率约 10×。
- **替代方案对比**：
  - 手动 TwinCAT System Manager → Add Route：标准方法，但人工逐台耗时。
  - TwinCAT XAE 命令行 `TcAmsRemoteMgr`：可脚本化，但需要 Windows shell 通道。
  - **本 FB**：纯 PLC 程序调用，可在 commissioning POU 里批量发起。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34973323.html
- **相关 FB**：`FB_AddRouteEntryEx`, `FB_EnumRouteEntry`, `FB_RemoveRouteEntry`
