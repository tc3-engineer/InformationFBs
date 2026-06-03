# UA_Disconnect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537635979.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_Disconnect.TcPOU`](../examples/P_Demo_UA_Disconnect.TcPOU) |

---

## 1. 功能简述

OPC UA 客户端断会话功能块（PDF §5.2.3.4）。`Execute` 上升沿向 `ConnectionHdl` 指向的会话发 CloseSession，完成后 Server 端释放该会话占用的资源（订阅、节点句柄等）。**特殊行为**：传 `ConnectionHdl := 0` 会**断开本客户端持有的所有 OPC UA 会话**（包括 I/O Client 配置建立的连接），PDF 文档把这个用法明确推荐作 PLC 启动期的「幽灵会话清理」步骤。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute           : BOOL;
    ConnectionHdl     : DWORD;     
    Timeout           : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次断会话 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄；传 `0` 则断开本 client 的全部会话 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认全局常量 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done        : BOOL;
    Busy        : BOOL;
    Error       : BOOL;
    ErrorID     : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE`，错误码在 `ErrorID` |
| `ErrorID` | `DWORD` | 命令特定错误码（ADS 错误码或客户端自定义 `0xE4DDxxxx` 范围） |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次断会话动作：FB 通过 ADS 通知 TF6100 客户端模块对指定 `ConnectionHdl` 发 CloseSession；过程中 `Busy := TRUE`，完成后 `Busy` 落 `FALSE`，成功则 `Done := TRUE` 一个周期。整个动作异步推进，必须每 PLC 周期调用本 FB 让内部状态机推进。

特殊用法 `ConnectionHdl := 0`：PDF §5.2.3.4 的「Disconnect all connections」专题段落明确：传 0 时 OPC UA 客户端会断开本 client 上所有现存连接，**包括通过 OPC UA I/O Client 配置建立的连接**。这是工程上做「PLC 启动期清理」的标准做法——因为 PLC 程序 Reset / Re-download 后旧会话句柄在 PLC 这边失忆但 Server 端可能仍持有，启动时一发广播断开即可清空所有遗留。

**典型用法**：① 业务结束前的优雅关闭：`UA_NodeReleaseHandle(List)` → `UA_Disconnect(具体句柄)`；② 启动期清理：上电后立刻调一次 `UA_Disconnect(0)`，等 `Done = TRUE` 再开始正常 Connect 流程。

**典型陷阱**：① 在 `Busy = TRUE` 期间又触发 `Execute` 不会有效——必须等 Busy 落沿；② 业务还有未释放的 `NodeHdl` / `MethodHdl` 时直接 Disconnect → Server 端被动清理，节点句柄相关错误码可能写到下一次操作；推荐先 Release 再 Disconnect；③ 误传一个已经断开的句柄 → 通常 Server 报「会话不存在」类错误（`UAC_E_INVALIDHDL` `0xE4DD0112`），但生产程序通常忽略此错误继续走清理流程。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 继续后续清理 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 句柄可能已被断开，忽略此错误继续 |
| `0xE4DD0107` | `UAC_E_SUSPENDED` | 设备繁忙 | 稍后重试 |

## 5. 使用注意 / 常见坑

- **`ConnectionHdl := 0` 是广播清理**：PDF §5.2.3.4 明确，会断开所有会话包括 I/O Client；如果项目里同时用 I/O Client 配置和 PLCopen FB 做混合访问，启动期清理会把 I/O Client 连接也断了——通常 I/O Client 状态机会自动重连，但建议在生产前评估。
- **顺序：先 Release 句柄再 Disconnect**：理论上 Disconnect 会触发 Server 端清理所有从属资源（节点句柄、订阅），但 PLC 端的 `NodeHdl` 变量没人清理，下一次启动复用旧值会拿到错误码。规范做法是 `UA_NodeReleaseHandleList → UA_MethodReleaseHandle → UA_Disconnect`。
- **优雅 vs 强制关闭**：本 FB 是优雅断开（发 CloseSession）。如果 Server 已经不响应，本 FB 会等到 Timeout 后报 `Error`，但 PLC 端 `ConnectionHdl` 仍可视为「已废弃」——业务可继续。
- **工程经验补充**：连接状态机里把 `UA_ConnectGetStatus` 检测到 `ConnectionError` / `Shutdown` 时自动调 `UA_Disconnect(具体句柄)`、等 Done、再 `UA_Connect` 重连。不要省略 Disconnect 直接 Connect——某些 Server 实现下会拒绝同一 PLC 来源的第二个会话直到旧的超时。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_Disconnect.TcPOU`](../examples/P_Demo_UA_Disconnect.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：① 设备停机：PLC 业务程序在收到停机指令后必须释放 OPC UA 客户端资源，给 Server 端腾空间；② 重连：连接状态机检测到 `ConnectionError` 时先 Disconnect 旧句柄再 Connect 新句柄；③ PLC 上电启动期：自动调 `UA_Disconnect(0)` 清掉上一轮 PLC 程序留下的所有幽灵会话，避免长期累积导致 Server 资源耗尽。
- **价值**：单 FB 调用即可完成 OPC UA CloseSession 协议交互（包括 SecureChannel 关闭、Token invalidation）。`ConnectionHdl := 0` 广播清理避免了「PLC 重启 → 旧句柄留在 Server → 一段时间后会话超时积压」的常见运维痛点。
- **替代方案对比**：① 不调 Disconnect 让会话自然超时——会留下「孤立会话」占 Server 资源直到 `tSessionTimeout` 到期（通常 60-600 秒），高频重启场景会累积；② 强制 kill Server 进程——破坏性，所有客户端断开；③ 重启 PLC 控制器——破坏性更高；④ **本 FB**——优雅、可重试、可针对单会话或广播清理。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.4（UA_Disconnect 含「Disconnect all connections」专题段）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537635979.html
- **相关 FB**：`UA_Connect`（必须配对）；`UA_ConnectGetStatus`（监控会话健康，触发重连）；`UA_NodeReleaseHandle(List)` / `UA_MethodReleaseHandle`（关会话前先释放节点 / 方法句柄）
