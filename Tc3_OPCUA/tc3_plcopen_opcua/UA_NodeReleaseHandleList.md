# UA_NodeReleaseHandleList

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/3171647883.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_NodeReleaseHandleList.TcPOU`](../examples/P_Demo_UA_NodeReleaseHandleList.TcPOU) |

---

## 1. 功能简述

OPC UA 节点句柄批量释放功能块（PDF §5.2.3.13）。一次性释放多个由 `UA_NodeGetHandleList`（或 `UA_NodeGetHandle`）申请到的节点句柄；用作 `UA_NodeReleaseHandle` 的批量版本。和 List 版本的 Get 配对使用，一次往返代替 N 次单独释放。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute          : BOOL;
    ConnectionHdl    : DWORD;
    NodeHdlCount     : UINT;
    NodeHdls         : ARRAY[1..nMaxNodeIDsInList] OF DWORD;
    Timeout          : TIME := DEFAULT_ADS_TIMEOUT;    
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次批量释放 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeHdlCount` | `UINT` | — | 要释放的句柄数量 |
| `NodeHdls` | `ARRAY[1..nMaxNodeIDsInList] OF DWORD` | — | 要释放的节点句柄数组；前 `NodeHdlCount` 个生效 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    NodeErrorIDs : ARRAY[1..nMaxNodeIDsInList] OF DWORD;
    Done         : BOOL;
    Busy         : BOOL;
    Error        : BOOL;
    ErrorID      : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `NodeErrorIDs` | `ARRAY[1..nMaxNodeIDsInList] OF DWORD` | 每个节点的释放错误码；成功为 0 |
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 至少一个失败时变 `TRUE`（具体到哪个看 `NodeErrorIDs`） |
| `ErrorID` | `DWORD` | 汇总错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次批量释放：FB 把 `NodeHdls[1..NodeHdlCount]` 一次性提交给 Server；Server 释放每个节点句柄。每节点独立处理：成功则 `NodeErrorIDs[i] = 0`；失败（句柄已失效 / 不存在 / 不属于该会话）则填错误码，整体 `Error := TRUE`。

**部分失败处理**：和 Get List 类似——业务侧应遍历 `NodeErrorIDs[1..NodeHdlCount]`，对失败的句柄通常视作已清理（句柄可能本来就无效），不需要重试。整批 `Error` 视作「至少一个失败」预警，但不阻塞后续 Disconnect 流程。

**释放后 PLC 端句柄变量清零**：和单节点版同理，释放成功后业务侧应循环把 `NodeHdls` 数组所有元素清 0，避免后续误用陈旧值。

**典型用法**：停机流程末尾——`业务停 → 调本 FB 释放全部节点句柄 → UA_MethodReleaseHandle 循环释放方法句柄 → UA_Disconnect 关会话`。

**典型陷阱**：① `NodeHdlCount` > 数组长度 → 越界；② 释放后忘清零 PLC 端句柄数组 → 后续误用；③ 多次重复释放 → 第二次报错（视作已清理忽略）；④ 在会话已断后释放 → 可能拿 `UAC_E_INVALIDHDL`，忽略此错误继续走 Disconnect。

## 4. 错误码 / 返回值

`ErrorID` 是汇总错误码；`NodeErrorIDs[i]` 是单节点错误码。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 全部成功 | 清零 PLC 端句柄数组 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `NodeHdlCount` 不超过数组长度 |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 会话已断；忽略此错误继续 Disconnect |

单节点 `NodeErrorIDs[i]` 常见：

| 单节点码 (Hex) | 含义 |
|---|---|
| `0` | 该句柄成功释放 |
| `0xE4DD0116` | 节点句柄已无效（视作已清理） |

## 5. 使用注意 / 常见坑

- **和 Get List 配对**：批量取 + 批量释放对称使用，效率最优。
- **`NodeHdlCount` 必须正确**：超过数组长度会越界，PLC 崩。
- **部分失败视作清理完成**：单节点 `UAC_E_INVAL_NODE_HDL` 通常意味着句柄已经失效（可能 Server 端兜底清理过），不需要重试。
- **释放后立即清零数组**：避免后续代码误用陈旧句柄。
- **工程经验补充**：「数据采集层」架构里，连接状态机的 Disconnect 流程：① 调本 FB 释放 `gNodeHdls`、② 循环 `UA_MethodReleaseHandle` 释放所有方法句柄、③ `UA_Disconnect`、④ 清零所有句柄存储。一气呵成最清晰。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_NodeReleaseHandleList.TcPOU`](../examples/P_Demo_UA_NodeReleaseHandleList.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：业务停机时清理批量取得的节点句柄。生产代码典型用法是连接状态机的 Disconnect 流程中调一次本 FB 释放所有数据采集节点句柄。
- **价值**：从 N 次串行 `UA_NodeReleaseHandle` 压缩到 1 次往返；停机时间从数秒缩到一两次往返时间；代码简化（不用循环 + 状态管理）。
- **替代方案对比**：① 串行 N 次 `UA_NodeReleaseHandle`——简单但慢；② 不释放，等 `UA_Disconnect` 兜底——PLC 端 NodeHdl 数组无人清；③ **本 FB**——批量释放标准入口。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.13（UA_NodeReleaseHandleList）、§5.2.4（nMaxNodeIDsInList 库参数）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/3171647883.html
- **相关 FB**：`UA_NodeGetHandleList`（必须配对）；`UA_NodeReleaseHandle`（单节点版本，少于 5 个用它）；`UA_Disconnect`（最终兜底）
