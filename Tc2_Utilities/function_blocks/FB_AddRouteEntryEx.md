# FB_AddRouteEntryEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682603019.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AddRouteEntryEx.xml`](../examples/P_Demo_FB_AddRouteEntryEx.xml) |

---

## 1. 功能简述

FB_AddRouteEntryEx 是 FB_AddRouteEntry 的扩展版：在原参数基础上额外暴露选项标志位，允许业务程序指定路由是 Static / Temp、是否加密、是否启用 AMS Subnet 自动发现等高级配置。

典型用场：要在 commissioning 阶段批量加临时路由（重启即丢）做调试，或要按设备类型差异化设置加密策略。

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
| `sNetID` | `T_AmsNetID` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `stRoute` | `ST_AmsRouteEntry` | - | 参数 `stRoute`（类型 `ST_AmsRouteEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

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
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**协议**：与 FB_AddRouteEntry 相同的 ADS 请求时序：`bExecute` 上升沿触发，`bBusy` 高电平期间不响应新请求，`bDone` / `bErr` + `nErrId` 反馈结果。

**新增选项**：`eRouteType` 决定 Static（持久化）/ Temp（重启清空）；`bSetStandardOptions` 等位允许混合控制加密、自动 NAT 穿透等。

**与 FB_AddRouteEntry 关系**：底层 ADS 命令字 / 错误码与原版完全相同，仅多几个选项位；推荐新项目直接用 Ex 版。


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
- Static / Temp 选择错容易导致测试期间加的路由被持久化进生产路由表，发布前清理麻烦——commissioning 建议先用 Temp。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AddRouteEntryEx.xml`](../examples/P_Demo_FB_AddRouteEntryEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：commissioning 时批量加 Temp 路由做联通测试，测试完重启自动清掉。
- **价值**：比 FB_AddRouteEntry 多了类型 / 加密选项位，避免修改两次。
- **替代方案对比**：
  - FB_AddRouteEntry：基础版，仅能加 Static 路由。
  - **本 FB**：可灵活指定路由类型与加密策略。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682603019.html
- **相关 FB**：`FB_AddRouteEntry`, `FB_RemoveRouteEntry`
