# UA_NodeGetHandleList

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/2346494731.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_NodeGetHandleList.TcPOU`](../examples/P_Demo_UA_NodeGetHandleList.TcPOU) |

---

## 1. 功能简述

OPC UA 节点句柄批量获取功能块（PDF §5.2.3.11）。一次性向 Server 申请多个节点的句柄；用于业务有多个数据节点要采集时替代多次 `UA_NodeGetHandle`。单次 List 调用比串行 N 次 `UA_NodeGetHandle` 节省 N-1 次 OPC UA 往返开销；列表上限由库参数 `nMaxNodeIDsInList` 决定（默认 10）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute          : BOOL;
    ConnectionHdl    : DWORD;
    NodeIDCount      : UINT;
    NodeIDs          : ARRAY[1..nMaxNodeIDsInList] OF ST_UANodeID;
    Timeout          : TIME := DEFAULT_ADS_TIMEOUT;    
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次批量句柄申请 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeIDCount` | `UINT` | — | 要申请句柄的节点数量 |
| `NodeIDs` | `ARRAY[1..nMaxNodeIDsInList] OF ST_UANodeID` | — | NodeID 数组；用前 `NodeIDCount` 个元素 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    NodeHdls     : ARRAY[1..nMaxNodeIDsInList] OF DWORD;
    NodeErrorIDs : ARRAY[1..nMaxNodeIDsInList] OF DWORD;
    cbData_R     : UDINT;
    Done         : BOOL;
    Busy         : BOOL;
    Error        : BOOL;
    ErrorID      : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `NodeHdls` | `ARRAY[1..nMaxNodeIDsInList] OF DWORD` | 申请到的节点句柄数组；按 `NodeIDs` 顺序对应 |
| `NodeErrorIDs` | `ARRAY[1..nMaxNodeIDsInList] OF DWORD` | 每节点错误码；成功为 0，失败为具体错误码（业务侧据此重试单节点） |
| `cbData_R` | `UDINT` | 实际读到的数据字节数 |
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 至少一个节点失败时变 `TRUE`（具体到哪个看 `NodeErrorIDs`） |
| `ErrorID` | `DWORD` | 汇总错误码 |

### VAR_IN_OUT

无。

#### nMaxNodeIDsInList（PDF §5.2.4 参数列表）

```
默认值 10。要支持更多节点需在库参数列表里调高（PDF 明确 nMaxNodeIDsInList 是 UINT）。
```

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次批量解析：FB 把 `NodeIDs[1..NodeIDCount]` 一次性提交给 Server；Server 并行解析每个 NodeID，返回每节点对应的句柄到 `NodeHdls`。每节点独立处理：成功则 `NodeHdls[i]` 含句柄、`NodeErrorIDs[i] = 0`；失败则 `NodeHdls[i]` 无效、`NodeErrorIDs[i]` 含错误码，整体 `Error := TRUE`。

**部分失败处理**：本 FB 不是「全部成功 / 全部失败」二态——单批次允许部分节点成功部分失败（典型场景：5 个节点里 1 个 NodeID 拼错），业务侧应遍历 `NodeErrorIDs[1..NodeIDCount]`：① 成功的节点照常用 `NodeHdls[i]`；② 失败的节点找出原因（NodeID 拼错 / namespace index 过期 / 节点不存在）修正后单独重试。

**`nMaxNodeIDsInList` 库参数**：默认 10。要批量取 50 个节点：在工程的库参数列表里把 `nMaxNodeIDsInList` 改成 50 + 重新编译。这会改变 `NodeIDs` / `NodeHdls` / `NodeErrorIDs` 数组长度。注意：参数太大会让 ADS 路由内存占用上升。

**典型用法**：启动期一次取齐——`UA_Connect → UA_GetNamespaceIndex → 准备 N 个 NodeID → UA_NodeGetHandleList(NodeIDCount := N)`；如果业务节点超过 `nMaxNodeIDsInList` 上限，分多批调本 FB。

**典型陷阱**：① `NodeIDCount` > `NodeIDs` 数组有效长度 → 越界，PLC 崩；② 库参数 `nMaxNodeIDsInList` 没调高就传超过 10 的 NodeIDCount → 越界；③ 节点数 = 1 时用本 FB → 没好处，单 `UA_NodeGetHandle` 更直接；④ 部分失败误以为整批失败 → 应遍历 `NodeErrorIDs` 单独处理。

## 4. 错误码 / 返回值

`ErrorID` 是汇总错误码；`NodeErrorIDs[i]` 是单节点错误码。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 全部成功 | 用 `NodeHdls[1..NodeIDCount]` 做后续读写 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `NodeIDCount` 不超过数组长度 |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |

单节点错误码 `NodeErrorIDs[i]` 常见：

| 单节点码 (Hex) | 含义 |
|---|---|
| `0` | 该节点成功 |
| `0xE4DD0113` | NodeID 未知 |
| `0xE4DD0114` | identifier 类型无效 |
| `0xE4DD0125` | 节点类型信息不足 |

## 5. 使用注意 / 常见坑

- **批量收益从 5 个节点起明显**：1-4 个节点用本 FB 没什么好处，5+ 个开始单往返收益线性提升。
- **`nMaxNodeIDsInList` 是库级参数**：所有用本 FB 和 `UA_ReadList` / `UA_NodeReleaseHandleList` 的实例共享同一上限。生产工程评估好真实需要 + 一定 margin（如 50）。
- **部分失败是常态**：业务侧必须遍历 `NodeErrorIDs`，不能只看汇总 `Error`。
- **配 `UA_NodeReleaseHandleList` 释放**：批量取 + 批量释放对称使用，效率最优。
- **工程经验补充**：把所有要采集的节点定义在一个 GVL 全局数组（`gNodeRequests : ARRAY[1..50] OF ST_UANodeID;`）+ 一个对应的句柄数组（`gNodeHdls : ARRAY[1..50] OF DWORD;`），连接状态机里建会话后调一次本 FB 取齐；这是「数据采集层」的典型架构。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_NodeGetHandleList.TcPOU`](../examples/P_Demo_UA_NodeGetHandleList.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：CX 控制器要从远端 MES Server 采集多个生产数据（液位、压力、温度、流量、订单号等 5+ 个 LREAL / INT 节点）。启动期一次取齐全部节点句柄供后续周期 `UA_ReadList` 批量读用。
- **价值**：从「N 次往返」变「1 次往返」，启动期时间从数秒缩到一两次往返时间；ADS / 网络流量大幅减少；业务代码可以集中处理「就绪 / 未就绪」一个状态。
- **替代方案对比**：① 串行 N 次 `UA_NodeGetHandle`——简单但慢，5 个节点要 5 次往返；② 用一个状态机管 N 次调用——代码复杂；③ I/O Client 静态配置——只适合编译期已知节点；④ **本 FB**——批量场景标准入口。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.11（UA_NodeGetHandleList）、§5.2.4（nMaxNodeIDsInList 库参数）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/2346494731.html
- **相关 FB**：`UA_Connect` / `UA_GetNamespaceIndex`（前置）；`UA_NodeGetHandle`（单节点版本，少于 5 个用它）；`UA_NodeReleaseHandleList`（必须配对释放）；`UA_ReadList`（批量读，配合本 FB）
