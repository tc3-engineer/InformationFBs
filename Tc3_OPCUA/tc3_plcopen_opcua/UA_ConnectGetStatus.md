# UA_ConnectGetStatus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/12554588939.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_ConnectGetStatus.TcPOU`](../examples/P_Demo_UA_ConnectGetStatus.TcPOU) |

---

## 1. 功能简述

OPC UA 会话状态查询功能块（PDF §5.2.3.3，要求 `Tc3_PLCopen_OpcUa >= 3.2.11.0`）。查询由 `UA_Connect` 建立的某条会话的健康状态——根据内部会话信息或 OPC UA 心跳判定，**不会**产生额外的读写流量。可选通过 `GetServiceLevel := TRUE` 让 FB 顺便在后台发一次 Read 取 Server 的 ServiceLevel 节点（OPC UA 标准节点，表示 Server 自评的服务质量 0–255）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute            : BOOL;
    ConnectionHdl      : DWORD;
    GetServiceLevel    : BOOL;     
    Timeout            : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次状态查询 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `GetServiceLevel` | `BOOL` | — | `TRUE` 时附带读 Server ServiceLevel 节点（多一次 Read 开销） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时；和 `UA_Connect` 同样建议 ADS Timeout > 2 × `ST_UASessionConnectInfo.tConnectTimeout` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done             : BOOL;
    Busy             : BOOL;
    Error            : BOOL;
    ErrorID          : DWORD;
    ConnectionStatus : E_UAConnectionStatus;
    ServerState      : E_UAServerState;
    ServiceLevel     : BYTE; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中，监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 调用本身失败（ADS 错或客户端模块错） |
| `ErrorID` | `DWORD` | 命令特定错误码 |
| `ConnectionStatus` | `E_UAConnectionStatus` | 业务层连接状态：`Connected` / `ConnectionError` / `Shutdown` |
| `ServerState` | `E_UAServerState` | OPC UA 标准 Server 状态：`Running` / `Failed` / `NoConfiguration` / `Suspended` / `Shutdown` / `Test` / `CommunicationFault` / `Unknown` |
| `ServiceLevel` | `BYTE` | Server ServiceLevel 节点值（0–255，仅 `GetServiceLevel = TRUE` 时有效） |

### VAR_IN_OUT

无。

#### E_UAConnectionStatus（PDF §5.2.2.4，要求 `Tc3_PLCopen_OpcUa >= 3.2.11.0`）

```iecst
TYPE E_UAConnectionStatus:
(
    Connected       := 0
    ConnectionError := 1,
    Shutdown        := 2
)DINT;
END_TYPE
```

| 值 | 说明 |
|---|---|
| `Connected` (0) | 会话已建立 |
| `ConnectionError` (1) | 建立会话时发生错误 |
| `Shutdown` (2) | 会话已断开 |

#### E_UAServerState（PDF §5.2.2.10，要求 `Tc3_PLCopen_OpcUa >= 3.2.11.0`）

```iecst
TYPE E_UAServerState:
(
    Running            := 0
    Failed             := 1,
    NoConfiguration    := 2,
    Suspended          := 3,
    Shutdown           := 4,
    Test               := 5,
    CommunicationFault := 6,
    Unknown            := 7
)DINT;
END_TYPE
```

| 值 | 说明 |
|---|---|
| `Running` (0) | Server 运行中 |
| `Failed` (1) | Server 失效 |
| `NoConfiguration` (2) | 未配置 |
| `Suspended` (3) | 暂停 |
| `Shutdown` (4) | 已关停 |
| `Test` (5) | 测试模式 |
| `CommunicationFault` (6) | 通讯故障 |
| `Unknown` (7) | 未知 |

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次状态查询：FB 内部检查 PLCopen 客户端模块保存的会话快照（最后一次心跳时间、SecureChannel 状态等）并向上报告 `ConnectionStatus`、`ServerState`。**默认不会**向 Server 发实际 OPC UA 请求——是「内部 cache 查询」级开销，因此可以高频调用（每 PLC 周期一次都可以）。当 `GetServiceLevel := TRUE` 时 FB 额外在后台发一次 Read 取 ServiceLevel 节点（OPC UA Server 标准节点 `Server_ServiceLevel`），这次 Read 的开销与一次 `UA_Read` 相当，建议不要每周期都开。

`ConnectionStatus` vs `ServerState` 的区别：① `ConnectionStatus` 是 PLC 客户端模块对会话本身的判定（连得通否、被断了否），用于触发本地重连状态机；② `ServerState` 是从 Server 自报的状态读出来的，反映远端 Server 进程的工作状态——例如 Server 进入 `Suspended`（运维下发暂停命令）时 `ConnectionStatus` 仍可能是 `Connected` 但 `ServerState` 是 `Suspended`，这时本地业务应该停掉读写避免拿到陈旧数据。

**典型用法**：连接状态机里每 1-2 秒触发一次本 FB；判断 `ConnectionStatus`：`Connected` → 业务继续；`ConnectionError` → 触发「Disconnect → 等 5 秒 → Connect」重连流程；`Shutdown` → Server 已主动关闭，重连意义不大，写报警等人工干预。`ServerState` 用作业务侧软中断：`Running` 时允许写；非 `Running` 时只读，避免错误操作。

**典型陷阱**：① 把本 FB 当 ping 用反复 `Execute` 但忘了边沿——电平 `TRUE` 持续期间只触发一次；② `GetServiceLevel := TRUE` 每周期都开 → 不必要的 OPC UA 流量；③ 仅看 `ConnectionStatus` 不看 `ServerState` → Server 处于 `Suspended` / `Test` 时业务侧无感知拿到测试值；④ 在会话尚未建立（`UA_Connect` 还没成功）时调本 FB → 句柄无效报错。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 看 `ConnectionStatus` / `ServerState` |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`；检查 Server 状态 |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 句柄过期或从未建立；重新 `UA_Connect` |
| `0xE4DD0111` | `UAC_E_TIMEOUT` | Server 不响应（仅 `GetServiceLevel = TRUE` 时可能出现） | 加大 `Timeout` 或暂时关掉 `GetServiceLevel` |

## 5. 使用注意 / 常见坑

- **`Connected` ≠ Server 数据可读**：`ServerState` 必须看一眼；`Suspended` / `Test` / `CommunicationFault` 时业务侧建议只读不写。
- **`GetServiceLevel` 不要常开**：那是真正的 OPC UA Read，每次几十字节流量、毫秒级延迟。低频运维监控（每分钟一次）足够。
- **版本要求**：`Tc3_PLCopen_OpcUa >= 3.2.11.0` 才有本 FB；旧版库工程升级后才能用，PDF §5.2.3.3 明确给出此版本要求。
- **作为「软探活」**：本 FB 比让 `UA_Read` 一个无关节点然后看错误码优雅得多——这是专门设计的状态查询接口。
- **工程经验补充**：连接状态机推荐结构：每 1 秒触发本 FB（仅 `ConnectionStatus`，不开 `GetServiceLevel`）；每 30 秒额外开一次 `GetServiceLevel := TRUE` 做带服务质量的深度检查。检测到 ServiceLevel < 200 表示 Server 处于「降级运行」，应触发预警。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_ConnectGetStatus.TcPOU`](../examples/P_Demo_UA_ConnectGetStatus.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：长寿命 OPC UA 客户端会话健康监控。控制器周期连 MES Server 拉订单、推工单状态；网络波动 / Server 重启 / 防火墙重置 / NAT 会话表过期都可能导致会话「假活」（句柄看上去还在，实际已废）。需要主动检测尽早重连。
- **价值**：用最小代价（不发额外 OPC UA 流量）持续监控会话健康；触发本地自动重连状态机，不再依赖业务读写失败回滚。同时通过 `ServerState` 感知远端 Server 主动状态变更（Suspended / Test 模式），业务侧可联动停写避免误操作。
- **替代方案对比**：① 用 `UA_Read` 读一个 dummy 节点看错误码——浪费流量、且语义不直接（错误可能是节点权限问题不是会话问题）；② 不监控，业务读写失败时再处理——会有数秒到数十秒的「假活窗口」造成数据错乱；③ 用 `FB_OpcUAServerGetStatus`（Tc2_OpcUa）——那是查 ADS 接口探活，与 OPC UA 会话健康不是一回事；④ **本 FB**——OPC UA Companion Spec 标准查询接口，语义清晰、开销最低。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.3（UA_ConnectGetStatus）、§5.2.2.4（E_UAConnectionStatus）、§5.2.2.10（E_UAServerState）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/12554588939.html
- **相关 FB**：`UA_Connect`（前置）；`UA_Disconnect`（重连前清理）；`FB_OpcUAServerGetStatus`（Tc2_OpcUa；查 ADS 接口探活，不同层次）
