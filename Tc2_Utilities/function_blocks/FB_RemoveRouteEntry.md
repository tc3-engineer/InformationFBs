# FB_RemoveRouteEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35020939.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RemoveRouteEntry.TcPOU`](../examples/P_Demo_FB_RemoveRouteEntry.TcPOU) |

---

## 1. 功能简述

FB_RemoveRouteEntry 通过 ADS 从目标 TwinCAT 系统的路由表中删除指定的远端 AMS 路由条目。用于把测试期残留的 Temp / Static 路由清除，或在生产线设备搬迁时取消已不存在的路由。

调用一旦成功，目标路由表立即生效，被删的路由不能再用做 AMS 通讯。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetId;
    sName : String (MAX_ROUTE_NAME_LEN);
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `sName` | `String (MAX_ROUTE_NAME_LEN)` | - | 目标主机名 / 路由名（字符串）。 |
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

**协议**：`bExecute` 上升沿触发一次 ADS 删除请求。需要正确填 `sRemoteName` / `sRemoteRouteName`（即在路由表里显示的那个名字）才能唯一匹配。

**完成判定**：与 AddRoute 相同，`bBusy` → `bDone` 或 `bErr` + `nErrId`。

**注意**：成功删除属于持久化操作（除非删的是 Temp 路由）；后续 ADS 通讯走该路由会立刻失败。


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
- **误删后通讯立即断**：本机程序通过被删路由调用 ADS 会立刻 `nErrId = 6 (DEVICE_NOTFOUND)`，且无法再用本 FB 加回去（连接已断）。
- 路由名匹配区分大小写——`'AutoRoute-Line2'` 和 `'autoroute-line2'` 是两条不同路由。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RemoveRouteEntry.TcPOU`](../examples/P_Demo_FB_RemoveRouteEntry.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：生产线设备 retrofit 后，老 PLC 拆掉，路由表里残留的旧条目需要清掉。
- **价值**：替代手动 System Manager 操作，可纳入运维脚本。
- **替代方案对比**：
  - 手动 System Manager → Routes → Delete：标准方法。
  - **本 FB**：PLC 程序可一键清理批量历史路由。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.55
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35020939.html
- **相关 FB**：`FB_AddRouteEntry`, `FB_EnumRouteEntry`
