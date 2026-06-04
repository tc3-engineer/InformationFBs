# UA_GetNamespaceIndex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537637003.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_GetNamespaceIndex.TcPOU`](../examples/P_Demo_UA_GetNamespaceIndex.TcPOU) |

---

## 1. 功能简述

OPC UA 命名空间索引解析功能块（PDF §5.2.3.5）。把 namespace URI（字符串，如 `'urn:BeckhoffAutomation:Ua:PLC1'`）解析为 namespace 索引（`UINT`，例如 4）。索引在后续 `UA_NodeGetHandle` / `UA_MethodGetHandle` 构造 `ST_UANodeID` 时作为 `nNamespaceIndex` 字段使用——因为 namespace index 是 Server 端动态分配的（每次 Server 启动可能变），不能硬编码，必须运行时解析。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute       : BOOL;
    ConnectionHdl : DWORD;
    NamespaceUri  : STRING(MAX_STRING_LENGTH);
    Timeout       : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次解析请求 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NamespaceUri` | `STRING(MAX_STRING_LENGTH)` | — | 要解析的 namespace URI。TwinCAT OPC UA Server 第一个 PLC runtime 用 `'urn:BeckhoffAutomation:Ua:PLC1'` |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    NamespaceIndex : UINT;
    Done           : BOOL;
    Busy           : BOOL;
    Error          : BOOL;
    ErrorID        : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `NamespaceIndex` | `UINT` | 解析得到的 namespace index。给后续 FB（如 `UA_NodeGetHandle` / `UA_MethodGetHandle`）的 `ST_UANodeID.nNamespaceIndex` 使用 |
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中，监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `DWORD` | 命令特定错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次 namespace 解析：FB 向 Server 发 OPC UA `ReadValueIDs` 服务读 NamespaceArray（OPC UA 标准节点 `Server_NamespaceArray`，包含该 Server 上所有 namespace URI 的有序数组），匹配输入 URI 后返回索引。整个动作异步推进，必须每 PLC 周期调用让内部状态机推进。`Busy = TRUE` 期间不接受新命令；`Done = TRUE` 一个周期标志成功完成，此后 `NamespaceIndex` 可用。

为什么需要这一步：① OPC UA 协议里每个 NodeID 必须包含 namespace index（命名空间在该 Server 上的排序号）；② Server 启动时按配置加载 namespace 列表，0 永远是 `OPC UA` 标准 namespace，1 永远是 Server 自身 namespace，**业务 namespace 索引（如用户 PLC namespace）则取决于配置顺序**，下次 Server 启动可能不一样；③ 因此 PLC 客户端不能硬编码 namespace index，必须每次会话建立后用本 FB 解析。

**典型用法**：会话状态机里——`UA_Connect → Done` → 触发本 FB（输入「业务 namespace URI」）→ 拿到 `NamespaceIndex` 写入一个 GVL 变量 → 后续构造所有 `ST_UANodeID` 都从该 GVL 取 index。这样若 Server 重启 namespace 重排，重连流程跑一遍本 FB 后业务自动适配。

**典型陷阱**：① `NamespaceUri` 拼错（漏前缀 `urn:`、URI 大小写错、末尾多空格） → `UAC_E_NSNAME_NOTFOUND`（`0xE4DD0109`）；② 在 `ConnectionHdl` 还没拿到（`UA_Connect` 没成功）时调本 FB → 句柄无效报错；③ 把本 FB 当一次性调用，没存返回值 → 每次构造 NodeID 都重复解析，浪费流量（PLC 程序通常存到 GVL 复用）；④ 把 `NamespaceIndex` 当全局常量长期使用，Server 重启后不重新解析 → 拿陈旧 index，所有 `UA_NodeGetHandle` 失败。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 存 `NamespaceIndex` 给后续用 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`；检查 Server |
| `0xE4DD0109` | `UAC_E_NSNAME_NOTFOUND` | 找不到该 URI 对应的 namespace | 用 UaExpert 等工具查 Server 的 NamespaceArray，核对 URI 拼写 |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0111` | `UAC_E_TIMEOUT` | Server 不响应 | 加大 `Timeout` 或检查 Server 状态 |

## 5. 使用注意 / 常见坑

- **会话建立后必跑一次**：把 `UA_Connect → UA_GetNamespaceIndex` 当一对：建会话后立刻解析所有要用的 namespace URI（如果业务横跨多个 namespace，多次调用本 FB 即可）。
- **URI 拼写必须严格匹配**：URI 是 OPC UA Server 自报的字符串，没有「智能匹配」；大小写、空格、`urn:` 前缀必须 1:1。
- **Server 端通过 `Server_NamespaceArray` 节点暴露 namespace 列表**：可以用 UaExpert / UaModeler 等工具浏览该节点确认 URI 列表。
- **TwinCAT OPC UA Server 的默认 URI**：第一个 PLC runtime = `urn:BeckhoffAutomation:Ua:PLC1`、第二个 = `urn:BeckhoffAutomation:Ua:PLC2`，依此类推（PDF §5.2.3.5 明确）。
- **工程经验补充**：把 namespace index 存到一个全局结构 `gOpcUaNs : ST_OpcUaNamespaces;`（字段 `nNsPlc1`、`nNsCustom1` 等），业务代码全程用 `gOpcUaNs.nNsPlc1` 避免散落硬编码。重连时重新填一次即可。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_GetNamespaceIndex.TcPOU`](../examples/P_Demo_UA_GetNamespaceIndex.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：跨设备 OPC UA 数据集成。例如 CX 控制器要从远端 TwinCAT OPC UA Server 读「PLC1 runtime 的某变量」+ 从同一 Server 读「Custom Companion Spec namespace 下的某节点」——两边 namespace 不同，业务运行前必须分别解析得到 index。
- **价值**：把 namespace 索引解析这个 OPC UA 协议必经步骤包装为一次 FB 调用；屏蔽 NamespaceArray 节点的协议细节；可在客户端启动 / 重连时自动适配 Server 配置变更。
- **替代方案对比**：① 硬编码 namespace index（例如 `nNamespaceIndex := 4`）——Server 重启 namespace 顺序变化就崩；② 自己用 `UA_Read` 读 `Server_NamespaceArray` 解析——可行但要写 NodeID 4-tuple、用 `UA_NodeGetHandle` 取句柄，等于把本 FB 手工实现一遍；③ 用 Configurator 在 I/O Client 侧静态配置——只适合静态变量映射，不能用于动态 NodeID 构造；④ **本 FB**——PLCopen 标准接口，一次调用搞定，PLC 工程师无需了解 OPC UA 协议细节。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.5（UA_GetNamespaceIndex）、§5.2.2.19（ST_UANodeID 中 `nNamespaceIndex` 字段）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537637003.html
- **相关 FB**：`UA_Connect`（前置）；`UA_NodeGetHandle` / `UA_NodeGetHandleList`（用本 FB 的输出构造 NodeID）；`UA_MethodGetHandle`（同样用 NamespaceIndex）
