# UA_NodeGetHandle

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537641099.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_NodeGetHandle.TcPOU`](../examples/P_Demo_UA_NodeGetHandle.TcPOU) |

---

## 1. 功能简述

OPC UA 节点句柄获取功能块（PDF §5.2.3.10）。把一个 `ST_UANodeID`（namespace index + identifier）解析为节点句柄 `NodeHdl`（`DWORD`），后续 `UA_Read` / `UA_Write` / `UA_HistoryUpdate` 都按此句柄寻址。NodeID 由 `UA_GetNamespaceIndex` 解析出的 namespace index + 用户指定的 identifier（字符串如 `'Symbol.fTemperature'`、数字、GUID、Opaque）构成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute       : BOOL;
    ConnectionHdl : DWORD;
    NodeID        : ST_UANodeID;
    Timeout       : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次句柄申请 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeID` | `ST_UANodeID` | — | 目标节点：包含 namespace index、identifier 字符串、identifier 类型（String / Numeric / GUID / Opaque）。namespace index 由 `UA_GetNamespaceIndex` 解析 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    NodeHdl     : DWORD;
    Done        : BOOL;
    Busy        : BOOL;
    Error       : BOOL;
    ErrorID     : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `NodeHdl` | `DWORD` | 解析出的节点句柄。后续 `UA_Read` / `UA_Write` / `UA_HistoryUpdate` 等以此寻址 |
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中。`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `DWORD` | 命令特定错误码 |

### VAR_IN_OUT

无。

#### ST_UANodeID（PDF §5.2.2.19）

```iecst
TYPE ST_UANodeID:
STRUCT
    nNamespaceIndex  : UINT;
    nReserved        : ARRAY [1..2] OF BYTE; //fill bytes
    sIdentifier      : STRING(MAX_STRING_LENGTH);
    eIdentifierType  : E_UAIdentifierType;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `nNamespaceIndex` | `UINT` | namespace 索引（由 `UA_GetNamespaceIndex` 解析得到） |
| `nReserved` | `ARRAY[1..2] OF BYTE` | 占位字节 |
| `sIdentifier` | `STRING(MAX_STRING_LENGTH)` | 节点 identifier；UA namespace 里 `Identifier` 属性显示的那个字符串 |
| `eIdentifierType` | `E_UAIdentifierType` | identifier 类型：`eUAIdentifierType_String` / `eUAIdentifierType_Numeric` / `eUAIdentifierType_GUID` / `eUAIdentifierType_Opaque` |

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次节点解析：FB 向 Server 发 OPC UA `TranslateBrowsePathsToNodeIds` 或直接 NodeID 验证请求，匹配后返回内部句柄。整个动作异步推进，必须每 PLC 周期调用让内部状态机推进。`Busy = TRUE` 期间不接受新命令；`Done = TRUE` 一个周期标志成功完成，此后 `NodeHdl` 可用。

**为什么需要句柄而不能直接拿 NodeID 读写**：OPC UA Read / Write 协议本身确实可以用 NodeID 直接读，但 PLCopen Companion Spec 引入了句柄抽象——客户端模块用句柄做内部缓存（数据类型、长度、订阅状态等），同一节点反复 Read 时不需要每次都跟 Server 重新协商类型信息。代价是要管理句柄生命周期（取 → 用 → 释放），收益是吞吐量。

**句柄寿命**：拿到的 `NodeHdl` 在会话 `ConnectionHdl` 存活期间有效。会话断开后所有 `NodeHdl` 自动失效。不再需要时用 `UA_NodeReleaseHandle` 释放，否则会占用 Server 端的节点句柄表条目（虽然不会很快耗尽，但长期累积有影响）。

**典型用法**：① 启动期：`UA_Connect → UA_GetNamespaceIndex → UA_NodeGetHandle`（对每个要读写的节点都调一次，或用 `UA_NodeGetHandleList` 批量）；② 业务期：拿着 `NodeHdl` 周期 `UA_Read` / `UA_Write`；③ 停机：`UA_NodeReleaseHandle` 释放 → `UA_Disconnect`。

**典型陷阱**：① `NodeID` 拼错（`sIdentifier` 大小写、namespace index 错） → `UAC_E_INVALIDNODEID`（`0xE4DD0113`）；② `eIdentifierType` 设错（节点其实是字符串 identifier，填了 Numeric） → `UAC_E_INVAL_IDENTIFIER_TYPE`（`0xE4DD0114`）；③ namespace index 用了硬编码、Server 重启后顺序变了 → 找不到节点；④ 在 `ConnectionHdl` 还没拿到时调本 FB → `UAC_E_INVALIDHDL`；⑤ 频繁 GetHandle / ReleaseHandle 同一个节点 → 浪费往返开销，应该取一次复用整个会话。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 用 `NodeHdl` 做后续读写 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`；检查 Server 状态 |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0113` | `UAC_E_INVALIDNODEID` | UA NodeID 未知 | 检查 namespace index 和 identifier 拼写 |
| `0xE4DD0114` | `UAC_E_INVAL_IDENTIFIER_TYPE` | identifier 类型无效 | 检查 `eIdentifierType` 是否匹配节点真实类型 |
| `0xE4DD0115` | `UAC_E_IDENTIFIER_NOTSUPP` | identifier 类型不支持 | TwinCAT 客户端不支持的 identifier 类型 |

## 5. 使用注意 / 常见坑

- **TwinCAT OPC UA Server 的常见 identifier 形式**：默认 PLC namespace 里 identifier 是字符串形如 `'MAIN.fTemperature'`（程序变量）或 `'GVL.bMotorRun'`（GVL 变量）；`eIdentifierType := eUAIdentifierType_String`。第三方 Server 可能用 Numeric（整数）或 GUID。
- **identifier 大小写敏感**：OPC UA 是大小写敏感协议，`'MAIN.x'` 和 `'main.x'` 是不同节点。
- **NodeID 用 UaExpert 等工具验证**：构造 NodeID 时先用 UaExpert 浏览 Server 找到目标节点的「NodeId」属性，复制其 namespace index 和 identifier 字符串到 PLC 代码里。
- **句柄长期复用，不要循环取**：会话存活期间一次取够；业务变更要切换节点时才考虑 Release 旧的取新的。
- **批量取用 `UA_NodeGetHandleList`**：要取超过 5-10 个节点句柄时，用 List 版本一次 OPC UA 往返完成，比串行 N 次本 FB 快得多。
- **工程经验补充**：把所有要用的 NodeHdl 集中到一个 FB 实例的 VAR_INSTANCE（或一个 GVL）里，配合「连接状态机」在 Connected 状态下自动取齐、Disconnect 时自动 Release——业务层只看「就绪 / 未就绪」一个布尔。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_NodeGetHandle.TcPOU`](../examples/P_Demo_UA_NodeGetHandle.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：从远端 TwinCAT OPC UA Server 周期采集 PLC 业务变量（如 `'MAIN.fTankLevel'`）。会话建立 + namespace 解析后，对每个要读取的变量都需要先取节点句柄，再周期 `UA_Read`。
- **价值**：把 OPC UA 协议里的「NodeID → NodeHdl」步骤封装为一次 FB 调用；客户端模块缓存节点的数据类型 / 长度信息，后续 Read 不需要重复协商。
- **替代方案对比**：① 不用句柄，直接每次 Read 都传 NodeID——OPC UA 协议本身允许，但 PLCopen Companion Spec 没设计这样的 FB，且每次都要带完整 NodeID 字符串造成流量浪费；② 用 I/O Client 静态配置——只能用于编译期已知的变量，运行期动态变量必须用本 FB；③ 用 `UA_NodeGetHandleList`——批量版本，少量节点时本 FB 更直接；④ **本 FB**——动态单节点访问的标准入口。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.10（UA_NodeGetHandle）、§5.2.2.19（ST_UANodeID）、§5.2.2.6（E_UAIdentifierType）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537641099.html
- **相关 FB**：`UA_Connect` / `UA_GetNamespaceIndex`（前置）；`UA_NodeGetHandleList`（批量版本，> 5 个节点用它）；`UA_NodeReleaseHandle`（必须配对释放）；`UA_Read` / `UA_Write` / `UA_HistoryUpdate`（用 NodeHdl 寻址）
