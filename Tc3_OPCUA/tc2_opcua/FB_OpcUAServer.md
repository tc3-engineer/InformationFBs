# FB_OpcUAServer

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc2_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_server/7633282699.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_OpcUAServer.TcPOU`](../examples/P_Demo_FB_OpcUAServer.TcPOU) |

---

## 1. 功能简述

TwinCAT OPC UA Server 控制功能块（属 legacy 库 `Tc2_OpcUa`，TF6100 PDF §5.1.2.1）。通过 ADS 命令向本机或远端的 TwinCAT OPC UA Server 发送一条管理动作：重启 OPC UA 接口、停掉 OPC UA 接口、重读配置文件、读取会话/订阅统计信息。`bExecute` 上升沿触发一次操作，操作类型由 `eOpcUAServerOption` 决定，结果写到 `stOpcUAServerInfo`（仅 ServerInfo 模式有意义）。本 FB 操作的是 OPC UA Server 的 OPC UA 接口（即客户端连进来用的那一面），不是它的 ADS 接口；ADS 接口只有 Server 进程被 kill 才会消失。

> 同一份 PDF 还描述 `Tc3_PLCopen_OpcUa`（§5.2），即新工程主用的 PLCopen OPC UA Client 库；两者是不同 PLC 库，本仓库的「Library」字段沿用 `Tc3_OPCUA` 作为 PDF 标识，但每篇文档在元信息「Category」行写明所属 PLC 库。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId             : T_AmsNetId;
    bExecute           : BOOL;
    eOpcUAServerOption : E_OpcUAServerOption;
    tTimeout           : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | 运行 TwinCAT OPC UA Server 的设备 AMS Net ID。本机用空串 `''` |
| `bExecute` | `BOOL` | — | 上升沿触发一次功能块执行 |
| `eOpcUAServerOption` | `E_OpcUAServerOption` | — | 要执行的操作。可选 `eOPCUAServerOption_Restart`（重启 OPC UA 接口）、`eOPCUAServerOption_Shutdown`（关停 OPC UA 接口）、`eOPCUAServerOption_RefreshCfg`（当前版本无作用）、`eOPCUAServerOption_ServerInfo`（查询会话/订阅统计信息，写入 `stOpcUAServerInfo`）、`eOPCUAServerOption_None`（初始枚举值） |
| `tTimeout` | `TIME` | — | ADS 超时时长 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stOpcUAServerInfo : ST_OpcUAServerInfo;
    bBusy             : BOOL;
    bError            : BOOL;
    nErrorId          : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stOpcUAServerInfo` | `ST_OpcUAServerInfo` | 仅当 `eOpcUAServerOption := eOPCUAServerOption_ServerInfo` 时填入：累计/当前会话数、被拒会话数、安全拒绝会话数、超时会话数、当前订阅数、被拒请求数、安全拒绝请求数 |
| `bBusy` | `BOOL` | 功能块正在处理；置 `FALSE` 后才允许下一次上升沿 |
| `bError` | `BOOL` | 发生错误时变 `TRUE`，错误码在 `nErrorId` |
| `nErrorId` | `UDINT` | 错误码（ADS 错误码或客户端自定义 `0xE4DDxxxx` 范围） |

### VAR_IN_OUT

无。

#### ST_OpcUAServerInfo（PDF §5.1.1.1）

```iecst
TYPE ST_OpcUAServerInfo :
STRUCT
    nReserved                     : UDINT;
    nCummulatedSessionCount       : UDINT;
    nCurrentSessionCount          : UDINT;
    nRejectedSessionCount         : UDINT;
    nSecurityRejectedSessionCount : UDINT;
    nSessionTimeoutCount          : UDINT;
    nCurrentSubscriptionCount     : UDINT;
    nRejectedRequestCount         : UDINT;
    nSecurityRejectedRequestCount : UDINT;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `nReserved` | `UDINT` | 占位字段 |
| `nCummulatedSessionCount` | `UDINT` | OPC UA Server 启动以来累计的客户端会话数 |
| `nCurrentSessionCount` | `UDINT` | 当前活跃客户端会话数 |
| `nRejectedSessionCount` | `UDINT` | 被 Server 拒绝的会话总数 |
| `nSecurityRejectedSessionCount` | `UDINT` | 出于安全原因（用户名密码错等）被拒会话数 |
| `nSessionTimeoutCount` | `UDINT` | 因超时被关闭的会话数 |
| `nCurrentSubscriptionCount` | `UDINT` | 当前订阅总数 |
| `nRejectedRequestCount` | `UDINT` | 失败请求总数 |
| `nSecurityRejectedRequestCount` | `UDINT` | 安全原因失败请求总数 |

#### E_OpcUAServerOption（PDF §5.1.1.2）

```iecst
TYPE E_OpcUAServerOption
(
    eOPCUAServerOption_None,
    eOPCUAServerOption_Restart,
    eOPCUAServerOption_Shutdown,
    eOPCUAServerOption_RefreshCfg,
    eOPCUAServerOption_ServerInfo
);
END_TYPE
```

| 枚举值 | 说明 |
|---|---|
| `eOPCUAServerOption_None` | 枚举的初始值 |
| `eOPCUAServerOption_Restart` | 重启 OPC UA Server 的 OPC UA 接口 |
| `eOPCUAServerOption_Shutdown` | 关停 OPC UA 接口；因为 Restart 经由 OPC UA 实施，关停后必须重启 Server 进程才能恢复 |
| `eOPCUAServerOption_RefreshCfg` | 当前版本此选项无功能（PDF 原话） |
| `eOPCUAServerOption_ServerInfo` | 查询 Server 的统计信息，结果在 `ST_OpcUAServerInfo` |

## 3. 行为说明

本 FB 用 ADS 调用 TwinCAT OPC UA Server 暴露的管理服务，因此运行需要 Server 进程正在 `sNetId` 指定的设备上运行，并且 ADS 路由已经通到那台设备。`bExecute` 由 `FALSE → TRUE` 上升沿触发一次操作：FB 把 `eOpcUAServerOption` 选定的命令打包发给 Server，过程中 `bBusy := TRUE`；Server 返回应答（或 `tTimeout` 到期）后 `bBusy` 落 `FALSE`，成功则 `bError := FALSE`、`stOpcUAServerInfo` 含返回数据（仅 ServerInfo 模式）；失败则 `bError := TRUE`、`nErrorId` 含错误码。

ServerInfo 模式给出的统计是「自 Server 启动以来累计 + 当前快照」的混合：`nCummulated…` / `nRejected…` / `nSessionTimeoutCount` / `nRejectedRequestCount` 是累计自增计数，`nCurrentSessionCount` / `nCurrentSubscriptionCount` 是即时快照。如果要监控趋势（例如「最近 10 分钟内有多少会话被安全拒绝」），需要外部按周期采样，FB 自身不提供差分。

Restart 操作通过 OPC UA 通道发给 Server 自己，所以**一旦先用 Shutdown 关停了 OPC UA 接口，就无法再用本 FB 把它启回来**——只能重启整个 Server 进程（停 TcOpcUaServer.exe / TwinCAT 服务，或者重启控制器）。这是 PDF 明确警告的不可逆动作。RefreshCfg 在当前 TF6100 版本里是空操作，调用不报错但不做任何事；想热加载新配置实际仍要 Restart。

**典型用法**：管理上位机界面上做一个「重启 OPC UA 接口」按钮，按下走 Restart；做一个「会话监控面板」周期 2 秒触发一次 ServerInfo，把当前会话数 / 累计被拒数 / 当前订阅数推到 HMI；做一个「停用 OPC UA」高权限操作走 Shutdown（界面要清楚提示「之后必须重启 Server 进程才能恢复」）。

**典型陷阱**：① `bExecute` 拉成电平 `TRUE` 不会反复触发——一个上升沿一次操作，要再触发必须先回落；② 在 ServerInfo 模式以外的模式去读 `stOpcUAServerInfo` 字段是无意义的，那时该结构没被写；③ `tTimeout` 设得过短（< 1 秒）在远端 OPC UA Server 启动初期或网络抖动时容易报超时 1861；④ 本 FB 走 ADS，需要目标机器装好 TF6100 Runtime 并已启动 Server 进程，否则 `nErrorId = 6` 或 `7`。

## 4. 错误码 / 返回值

`nErrorId` 是 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx` 范围。常见取值（PDF §8.2.1 / §8.2.3）：

| `nErrorId` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 读取 `stOpcUAServerInfo` 或确认操作生效 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到（OPC UA Server 进程没启动 / 没装 TF6100） | 在目标机上确认 TcOpcUaServer 进程运行；检查 TF6100 license |
| `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标机不可达（AMS 路由不通） | 检查 `sNetId`、Static Routes 配置 |
| `0x745` (1861) | ADS Timeout | 操作未在 `tTimeout` 内完成 | 加大 `tTimeout`；检查目标 Server 是否正卡顿 |
| `0xE4DD0001` | `UAC_E_FAIL` | OPC UA 服务调用失败 | 查 Server 日志（`TcOpcUaServer.log`） |
| `0xE4DD0107` | `UAC_E_SUSPENDED` | 设备繁忙 | 稍后重试 |

完整 ADS 错误码表见 PDF §8.2.1，客户端自定义码表见 §8.2.3。

## 5. 使用注意 / 常见坑

- **Restart 不能救活已 Shutdown 的接口**：Shutdown 走 OPC UA 通道下发，关停后该通道也死了，本 FB 无路径再发 Restart。要恢复只能重启 Server 进程或控制器。
- **RefreshCfg 不要当热加载用**：PDF 明文说本版本无功能；要让 Server 加载新配置必须 Restart。
- **`sNetId` 用空串等价于「本机 OPC UA Server」**：和其他 Tc2/Tc3 ADS FB 一致，远端机器需在 Static Routes 里配好并指向那台机器的 AMS Net ID。
- **ServerInfo 统计是累计 + 即时混合**：要做趋势分析需自己存历史值做差分。
- **本 FB 是 legacy `Tc2_OpcUa` 库**：新工程做客户端连别的 OPC UA Server 应使用 `Tc3_PLCopen_OpcUa`（同 PDF §5.2，本仓库 `tc3_plcopen_opcua/` 子目录）。本 FB 是用来管 TwinCAT OPC UA **Server** 本身的，不是连别人的 Server。
- **工程经验补充**：在 SCADA 端做一个「OPC UA 心跳监控」面板时，建议每 5-10 秒查一次 ServerInfo，把 `nCurrentSessionCount = 0` 持续超过 N 周期视为 Server 失活预警。如果只想知道 Server 是否还在响应，用配套 `FB_OpcUAServerGetStatus` 更轻，那个 FB 只查 ADS 心跳不查 OPC UA 接口。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_OpcUAServer.TcPOU`](../examples/P_Demo_FB_OpcUAServer.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：生产线上的 CX 控制器同时运行 TF6100 OPC UA Server 给 MES / SCADA 提供 PLC 数据。运维人员希望在不停 PLC 程序的前提下，远程重启 OPC UA 接口（升级证书后、修改 namespace 映射后）、监控当前并发会话数（防止某客户端订阅泄漏导致 Server 资源耗尽）、紧急关停 OPC UA 接口（安全事件期间锁外网访问）。
- **价值**：把这些管理操作封装为一个 ADS FB 调用——无需远程登录控制器、无需手工 kill/start Server 进程。和 HMI 联动后，运维可以一键操作。配合 `FB_OpcUAServerGetStatus`（轻量探活）可构建完整的「OPC UA 健康监控 + 控制面板」。
- **替代方案对比**：① 远程登录 Windows 桌面手工重启 TcOpcUaServer 服务——延迟大、需登录权限、无审计；② 自己写 ADS 命令调 Server 管理接口——和本 FB 实质相同但要查私有索引组；③ 用 OPC UA 标准客户端工具（UaExpert）调 `Method` 实现重启——只能在 Server 还可达时做。本 FB 优势在于 PLC 程序内部即可发起，可与业务逻辑联动（例如「检测到第三方客户端连续 10 次安全拒绝就自动 Shutdown 等待人工介入」）。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.1.2.1（FB_OpcUAServer）、§5.1.1.1（ST_OpcUAServerInfo）、§5.1.1.2（E_OpcUAServerOption）、§8.2 状态码
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_server/7633282699.html
- **相关 FB**：`FB_OpcUAServerGetStatus`（仅查 ADS 心跳的轻量探活）；`Tc3_PLCopen_OpcUa.UA_Connect`（新工程客户端连远端 OPC UA Server 用）
