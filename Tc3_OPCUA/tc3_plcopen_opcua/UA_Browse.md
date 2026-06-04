# UA_Browse

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/ |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_Browse.TcPOU`](../examples/P_Demo_UA_Browse.TcPOU) |

---

## 1. 功能简述

OPC UA namespace 浏览功能块（PDF §5.2.3.1）。从指定起始节点出发，按 `BrowseDescription` 配置的方向 / 引用类型 / NodeClass 过滤，读出该节点的全部引用并以 `ReferenceDescriptions` 数组形式返回。结果可用于进一步深入 namespace（递归 Browse）或自动发现节点。Server 数据大时支持 `ContinuationPoint` 分批拉取。

⚠️ 该 FB 的 InfoSys 当前版本未给出独立 per-topic 页面，元信息 `InfoSys-checked` 标 `⚠️ not-on-infosys`；事实核对仅基于 PDF §5.2.3.1。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute             : BOOL;
    ConnectionHdl       : DWORD;
    BrowseDescription   : ST_UABrowseDescription;
    ContinuationPointIn : DWORD;
    Timeout             : TIME; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次 Browse |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `BrowseDescription` | `ST_UABrowseDescription` | — | Browse 配置：起始节点 NodeID、方向（Forward / Inverse / Both）、引用类型 NodeID、是否包含子类型、NodeClass 过滤、结果掩码 |
| `ContinuationPointIn` | `DWORD` | — | 上一次 Browse 返回的 `ContinuationPointOut`；首次调用传 `0` |
| `Timeout` | `TIME` | — | ADS 超时（无默认；调用方必须显式给值） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done                 : BOOL;
    Busy                 : BOOL;
    Error                : BOOL;
    ErrorID              : DWORD;
    ContinuationPointOut : DWORD;
    cbBrowseResultCnt    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `DWORD` | 命令特定错误码 |
| `ContinuationPointOut` | `DWORD` | Server 分批返回时给出，非零表示还有更多数据可拉，下次调用作为 `ContinuationPointIn` 传入；零表示已读完 |
| `cbBrowseResultCnt` | `UDINT` | 本次返回的 `ReferenceDescription` 数量 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    ReferenceDescriptions : POINTER TO ST_UAReferenceDescriptions;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ReferenceDescriptions` | `POINTER TO ST_UAReferenceDescriptions` | 输出引用描述数组的缓冲区。PLC 程序声明一个 `ARRAY OF ST_UAReferenceDescription` 然后传 `ADR()` |

#### ST_UABrowseDescription（PDF §5.2.2.13）

```iecst
TYPE ST_UABrowseDescription:
STRUCT
    stStartingNodeId  : ST_UANodeId;
    eDirection        : E_UABrowseDirection;
    stReferenceTypeId : ST_UANodeId;
    bIncludeSubtypes  : BOOL;
    eNodeClass        : E_UANodeClassMask;
    eResultMask       : E_UABrowseResultMask;
END_STRUCT
END_TYPE
```

PDF 给出的默认建议（Values 列）：
| 字段 | PDF 建议默认 |
|---|---|
| `stStartingNodeId` | ObjectRoot（OPC UA 标准根节点 i=84） |
| `eDirection` | `eUABD_Forward`（正向） |
| `stReferenceTypeId` | Hierarchical（i=33） |
| `bIncludeSubtypes` | `TRUE` |
| `eNodeClass` | `eUANCM_All`（255，所有 NodeClass） |
| `eResultMask` | `eUABRM_All`（63，全部字段） |

#### ST_UAReferenceDescription（PDF §5.2.2.21）

```iecst
TYPE ST_UAReferenceDescription:
STRUCT
    stReferenceTypeId : ST_UANodeId;
    bIsForward        : BOOL;
    stNodeId          : ST_UAExpandedNodeId;
    stBrowseName      : STRING(MAX_STRING_LENGTH);
    stDisplayName     : ST_UALocalizedText;
    eNodeClass        : E_UANodeClassMask;
    stTypeDefinition  : ST_UAExpandedNodeId;
END_STRUCT
END_TYPE
```

| 字段 | 说明 |
|---|---|
| `stReferenceTypeId` | 引用类型 NodeID（如 Organizes、HasChild、HasTypeDefinition） |
| `bIsForward` | 该引用方向是否为正向 |
| `stNodeId` | 目标节点（Expanded NodeID，含 namespace URI） |
| `stBrowseName` | 目标节点 BrowseName |
| `stDisplayName` | 目标节点本地化显示名 |
| `eNodeClass` | 目标节点的 NodeClass |
| `stTypeDefinition` | TypeDefinition 引用 |

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次 Browse：FB 把 `BrowseDescription` 提交给 Server，Server 返回所有匹配的引用描述（依方向 + 引用类型 + NodeClass 过滤），结果按 `eResultMask` 包含或省略某些字段写入 `ReferenceDescriptions` 数组指向的缓冲区，`cbBrowseResultCnt` 给出本次条目数。

**分批拉取（ContinuationPoint）**：当 Server 端节点引用数量超过单次返回上限时，本次只返回前 N 条 + 一个非零 `ContinuationPointOut`；业务侧应继续触发 Browse 时把这个值传到 `ContinuationPointIn`，Server 返回下一批，直到 `ContinuationPointOut = 0`。这是 OPC UA 协议标准做法。

**典型用法**：① 工具类应用——客户端启动时自动发现 Server 提供哪些节点（按 ObjectRoot → Folder → Variable 递归 Browse）；② 自动配置——根据 Server 当前 namespace 内容动态生成监控点；③ 调试——人工查节点路径。**业务采集场景一般不用 Browse**，因为节点路径在工程设计阶段就确定，运行时直接用 NodeID + `UA_NodeGetHandle` 即可。

**`BrowseDescription` 配置例子**：
- 从 ObjectRoot 出发列出所有 Object：`stStartingNodeId` = ObjectRoot、`eDirection` = Forward、`eNodeClass` = `eUANCM_Object`
- 列某 Object 下所有变量节点：`stStartingNodeId` = 上面找到的 Object NodeID、`eNodeClass` = `eUANCM_Variable`
- 查某变量的类型定义：`stStartingNodeId` = 变量 NodeID、`stReferenceTypeId` = HasTypeDefinition

**典型陷阱**：① `ReferenceDescriptions` 缓冲数组太小 → Server 返回数据截断，需要查 `cbBrowseResultCnt`；② 忽略 `ContinuationPointOut`，以为一次读完 → 大 Server 上拉到一半就停了；③ `BrowseDescription` 配置不全（如忘了设 `eResultMask`） → 拿到的字段不完整；④ 把 Browse 当周期采集用 → 极大浪费 OPC UA 流量。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 处理 `ReferenceDescriptions[1..cbBrowseResultCnt]`；若 `ContinuationPointOut ≠ 0` 继续触发拉下一批 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `ReferenceDescriptions` 缓冲大小 |
| `0x706` | `DEVICE_INVALIDDATA` | 参数值无效 | 检查 `BrowseDescription` 字段 |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`；大型 Server Browse 慢可设 30 秒 |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0113` | `UAC_E_INVALIDNODEID` | UA NodeID 未知 | 检查 `BrowseDescription.stStartingNodeId` |

## 5. 使用注意 / 常见坑

- **Browse 是「发现工具」不是「业务读取手段」**：业务采集应直接 NodeID + `UA_NodeGetHandle`；Browse 仅用于动态发现、调试、配置生成等低频场景。
- **`ContinuationPoint` 必须处理**：大 Server 一次 Browse 可能返回 100+ 条；务必循环触发到 `ContinuationPointOut = 0`。
- **缓冲数组够大**：`ARRAY[1..nMaxRefs] OF ST_UAReferenceDescription` 中 `nMaxRefs` 至少 50；不够则配合 ContinuationPoint 多次拉取。
- **PDF 没给 `Timeout` 默认值**：所有其他 PLCopen FB 默认 `DEFAULT_ADS_TIMEOUT` (5 秒)，但本 FB 的 `Timeout` PDF 写法是裸 `TIME;`，调用方必须显式给值（建议 T#10S 起步，大 Server 给 T#30S）。
- **InfoSys 没单页**：本 FB 在 InfoSys 上没有独立 per-topic URL，元信息 `InfoSys-checked` 标 `⚠️ not-on-infosys`；权威信息仅 PDF §5.2.3.1。
- **工程经验补充**：递归 Browse 常用「深度限制 + 队列广度优先」结构，避免循环引用导致死循环（OPC UA namespace 允许出现 cycle，Browse 不自动去环）。生产代码里写 Browse 工具时务必加深度上限 + visited NodeID 哈希。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_Browse.TcPOU`](../examples/P_Demo_UA_Browse.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：工厂部署多台 TwinCAT 控制器，每台暴露的 OPC UA namespace 节点构成不一样（不同生产工艺、不同变量定义）。配置工具上电后用本 FB 从 ObjectRoot 递归 Browse 出每台 Server 的全部 Variable 节点，自动生成监控点列表给 SCADA，免人工编辑。或者：调试期间用 Browse 找节点 NodeID（替代手工开 UaExpert）。
- **价值**：把 OPC UA 协议里 Browse 服务（含 BrowseDescription 编码、ReferenceDescription 解码、ContinuationPoint 流控）封装为 7 输入 6 输出的 FB 调用；PLC 工程师不需要了解 OPC UA Binary Encoding 的复杂规则。
- **替代方案对比**：① UaExpert / UaModeler 手工浏览——一次性的；动态场景做不到；② 自己用 `Tc2_TcpIp` 实现 Browse 协议——可行但要写 ASN.1 风格的 Binary Encoding 解码，数百行代码；③ 不浏览，硬编码 NodeID——简单但不适应 Server 变化；④ **本 FB**——动态、PLCopen 标准、跨 Server 通用。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.1（UA_Browse）、§5.2.2.13（ST_UABrowseDescription）、§5.2.2.21（ST_UAReferenceDescription）、§5.2.2.2（E_UABrowseDirection）、§5.2.2.3（E_UABrowseResultMask）、§5.2.2.7（E_UANodeClassMask）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/（库根，本 FB 在 InfoSys 没单独页）
- **相关 FB**：`UA_Connect`（前置）；`UA_GetNamespaceIndex`（用于构造 Starting NodeID）；`UA_NodeGetHandle`（业务采集流程后续步骤）；`UA_Read`（拿到节点 NodeID 后读值）
