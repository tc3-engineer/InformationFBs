# Tc3_OPCUA（TF6100 OPC UA Client）

> Beckhoff TwinCAT 3 OPC UA 客户端 PLC API。
> 本仓库的 `Tc3_OPCUA` 实际对应同一份 PDF（`TF6100_TC3_OPC_UA_Client_EN.pdf`）描述的两个 PLC 库：
> 1. **`Tc2_OpcUa`**（legacy 服务器内置库）：管理本机或远端的 TwinCAT OPC UA Server 进程，2 个 FB
> 2. **`Tc3_PLCopen_OpcUa`**（主用客户端库）：基于 PLCopen「OPC UA Client Companion Spec」实现 16 个标准客户端 FB
>
> 新工程对接第三方 OPC UA Server 使用 `Tc3_PLCopen_OpcUa`；管理本机 TwinCAT OPC UA Server 仍用 `Tc2_OpcUa`。运行 OPC UA 客户端功能需要 TF6100 license 和在 TwinCAT I/O 区配置一个「OPC UA Virtual Device」（产品版本 2.x 起强制要求）。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.3.0` |
| 来源 PDF | [TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/ |
| 文档进度 | 18 / 18 FB（含 DUT/枚举随父 FB 完整引用） |

## 典型部署模板

### 客户端最小流程（PLCopen FB 链）

`UA_Disconnect(0)` 启动清理 → `UA_Connect` 建会话 → `UA_GetNamespaceIndex` 解析 namespace → `UA_NodeGetHandleList`（或 `UA_NodeGetHandle`）取节点句柄 → 周期 `UA_ReadList` / `UA_Read` 读 + 业务事件触发 `UA_Write` 写 → 停机 `UA_NodeReleaseHandleList` → `UA_Disconnect`

### 客户端调远端方法（RPC 风格）

`UA_Connect` → `UA_GetNamespaceIndex` → `UA_MethodGetHandle`（取方法句柄）→ 业务事件触发 `UA_MethodCall`（带输入参数、收输出参数）→ 停机 `UA_MethodReleaseHandle` → `UA_Disconnect`

### 客户端浏览 Server namespace（调试 / 配置发现）

`UA_Connect` → `UA_Browse`（从 ObjectRoot 出发 + ContinuationPoint 处理大 Server 分批数据）→ 解析 `ST_UAReferenceDescription` 数组 → `UA_Disconnect`

### 历史数据补传

`UA_Connect` → `UA_NodeGetHandle`（目标历史节点）→ 本地缓冲 N 个 `UAHADataValue`（每对象含 Value 指针 + 时间戳 + StatusCode）→ `UA_HistoryUpdate` 批量推送 → 检查 `ValueErrorIDs` 单值失败重试 → 停机

### 管理 TwinCAT OPC UA Server 进程（Tc2_OpcUa）

`FB_OpcUAServerGetStatus`（轻量探活，秒级粒度）+ `FB_OpcUAServer`（管理动作：重启 OPC UA 接口 / 关停 / 查统计信息）。两者并行使用做完整 Server 健康 + 控制面板。

## 文档索引

### Tc2_OpcUa / Function blocks（2，管理 TwinCAT OPC UA Server）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_OpcUAServer` | 重启 / 关停 OPC UA Server 接口、查会话/订阅统计 | [tc2_opcua/FB_OpcUAServer.md](tc2_opcua/FB_OpcUAServer.md) |
| `FB_OpcUAServerGetStatus` | 通过 ADS 探活 Server（Alive / NotResponding） | [tc2_opcua/FB_OpcUAServerGetStatus.md](tc2_opcua/FB_OpcUAServerGetStatus.md) |

### Tc3_PLCopen_OpcUa / Function blocks（16，PLCopen OPC UA Client）

#### 会话管理（4）

| 名称 | 用途 | 文档 |
|---|---|---|
| `UA_Connect` | 建 OPC UA 会话，获取 ConnectionHdl | [tc3_plcopen_opcua/UA_Connect.md](tc3_plcopen_opcua/UA_Connect.md) |
| `UA_Disconnect` | 关会话；`ConnectionHdl := 0` 用作启动期幽灵会话清理 | [tc3_plcopen_opcua/UA_Disconnect.md](tc3_plcopen_opcua/UA_Disconnect.md) |
| `UA_ConnectGetStatus` | 查会话健康（ConnectionStatus + ServerState + ServiceLevel），驱动重连状态机 | [tc3_plcopen_opcua/UA_ConnectGetStatus.md](tc3_plcopen_opcua/UA_ConnectGetStatus.md) |
| `UA_GetNamespaceIndex` | namespace URI → namespace index（用于构造 NodeID） | [tc3_plcopen_opcua/UA_GetNamespaceIndex.md](tc3_plcopen_opcua/UA_GetNamespaceIndex.md) |

#### 节点句柄管理（4）

| 名称 | 用途 | 文档 |
|---|---|---|
| `UA_NodeGetHandle` | 单节点 NodeID → NodeHdl | [tc3_plcopen_opcua/UA_NodeGetHandle.md](tc3_plcopen_opcua/UA_NodeGetHandle.md) |
| `UA_NodeGetHandleList` | 批量 NodeID → NodeHdl（4+ 节点用批量版） | [tc3_plcopen_opcua/UA_NodeGetHandleList.md](tc3_plcopen_opcua/UA_NodeGetHandleList.md) |
| `UA_NodeReleaseHandle` | 单节点释放 NodeHdl | [tc3_plcopen_opcua/UA_NodeReleaseHandle.md](tc3_plcopen_opcua/UA_NodeReleaseHandle.md) |
| `UA_NodeReleaseHandleList` | 批量释放 NodeHdl | [tc3_plcopen_opcua/UA_NodeReleaseHandleList.md](tc3_plcopen_opcua/UA_NodeReleaseHandleList.md) |

#### 读 / 写 / 浏览（4）

| 名称 | 用途 | 文档 |
|---|---|---|
| `UA_Read` | 单节点读 Value（或其他属性） | [tc3_plcopen_opcua/UA_Read.md](tc3_plcopen_opcua/UA_Read.md) |
| `UA_ReadList` | 批量读到连续缓冲区（数据采集层主力） | [tc3_plcopen_opcua/UA_ReadList.md](tc3_plcopen_opcua/UA_ReadList.md) |
| `UA_Write` | 单节点写 Value | [tc3_plcopen_opcua/UA_Write.md](tc3_plcopen_opcua/UA_Write.md) |
| `UA_Browse` | namespace 浏览，含 ContinuationPoint 分批拉取 | [tc3_plcopen_opcua/UA_Browse.md](tc3_plcopen_opcua/UA_Browse.md) |

#### 方法调用（3）

| 名称 | 用途 | 文档 |
|---|---|---|
| `UA_MethodGetHandle` | 方法句柄申请（Object NodeID + Method NodeID → MethodHdl） | [tc3_plcopen_opcua/UA_MethodGetHandle.md](tc3_plcopen_opcua/UA_MethodGetHandle.md) |
| `UA_MethodCall` | 调远端 Method（15 个输入，最复杂） | [tc3_plcopen_opcua/UA_MethodCall.md](tc3_plcopen_opcua/UA_MethodCall.md) |
| `UA_MethodReleaseHandle` | 方法句柄释放 | [tc3_plcopen_opcua/UA_MethodReleaseHandle.md](tc3_plcopen_opcua/UA_MethodReleaseHandle.md) |

#### 历史数据（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `UA_HistoryUpdate` | 批量写带时间戳历史值（最多 1000 条/批） | [tc3_plcopen_opcua/UA_HistoryUpdate.md](tc3_plcopen_opcua/UA_HistoryUpdate.md) |

## DUTs / 枚举（未单独成文档）

以下数据类型在 §5.1.1 / §5.2.2 出现，作为上述 FB 的参数 / 返回类型使用；按本仓 CLAUDE.md 流程它们随父 FB 在其文档内完整收录（含 STRUCT 字段表、ENUM 枚举值表），不另外单独成篇：

| 名称 | 类型 | 主要使用方 |
|---|---|---|
| `ST_OpcUAServerInfo` | STRUCT | `FB_OpcUAServer`（统计输出） |
| `E_OpcUAServerOption` | ENUM | `FB_OpcUAServer`（动作选项） |
| `E_OpcUAServerStatus` | ENUM | `FB_OpcUAServerGetStatus` |
| `E_UAAttributeID` | ENUM | `UA_Read` / `UA_Write` 的 `stNodeAddInfo.eAttributeID` |
| `E_UABrowseDirection` | ENUM | `UA_Browse` |
| `E_UABrowseResultMask` | ENUM | `UA_Browse` |
| `E_UAConnectionStatus` | ENUM | `UA_ConnectGetStatus` |
| `E_UADataType` | ENUM | `UA_MethodCall.ST_UAMethodArgInfo.DataType` |
| `E_UAIdentifierType` | ENUM | `ST_UANodeID.eIdentifierType` |
| `E_UANodeClassMask` | ENUM | `UA_Browse` / `ST_UAReferenceDescription` |
| `E_UASecurityMsgMode` | ENUM | `ST_UASessionConnectInfo.eSecurityMode` |
| `E_UASecurityPolicy` | ENUM | `ST_UASessionConnectInfo.eSecurityPolicyUri` |
| `E_UAServerState` | ENUM | `UA_ConnectGetStatus.ServerState` |
| `E_UATransportProfile` | ENUM | `ST_UASessionConnectInfo.eTransportProfileUri` |
| `E_UAUserIdentityTokenType` | ENUM | `ST_UAUserIdentityTokenType.eUserIdentTokenType` |
| `ST_UABrowseDescription` | STRUCT | `UA_Browse` |
| `ST_UAExpandedNodeID` | STRUCT | `ST_UAReferenceDescription` |
| `ST_UAIndexRange` | STRUCT | `ST_UANodeAdditionalInfo.stIndexRange` |
| `ST_UALocalizedText` | STRUCT | `ST_UAReferenceDescription.stDisplayName` |
| `ST_UAMethodArgInfo` | STRUCT | `UA_MethodCall` |
| `ST_UANodeAdditionalInfo` | STRUCT | `UA_Read` / `UA_Write` / `UA_ReadList` |
| `ST_UANodeID` | STRUCT | 所有节点 / 方法相关 FB |
| `ST_UAReferenceDescription` | STRUCT | `UA_Browse` 输出数组元素 |
| `ST_UASessionConnectInfo` | STRUCT | `UA_Connect` |
| `ST_UAUserIdentityTokenType` | STRUCT | `ST_UASessionConnectInfo.stUserIdentTokenType` |
| `UAHADataValue` | 数据对象 FB | `UA_HistoryUpdate` |
| `UAHAUpdateStatusCode` | ENUM | `UAHADataValue.StatusCode` |

## 库参数（PDF §5.2.4）

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nMaxNodeIDsInList` | `UINT` | `10` | 决定 `UA_NodeGetHandleList` / `UA_NodeReleaseHandleList` / `UA_ReadList` 等批量 FB 的数组上限；超过 10 节点的项目调高此参数后重新编译 |
| `sNetId` | `T_AmsNetId` | `127.0.0.1.1.1` | 运行 TwinCAT OPC UA Client 模块的设备 AMS Net ID。**TF6100 v2.x 起必须在 I/O 区配 OPC UA Virtual Device 并把它的 AMS Net ID 写到此参数**，否则 `UA_Connect` 直接报 ADS 错误 6 |

## 错误码概览

`ErrorID` / `nErrorId` 是 ADS 错误码（高字 `0x0000`）+ 客户端自定义错误码（高字 `0xE4DDxxxx` / `0xE4DExxxx`）。完整码表见 PDF §8.2.1（ADS 全局错误码）+ §8.2.3（客户端自定义码）。最常见的几个：

| 范围 | 来源 | 典型码 |
|---|---|---|
| `0x0000-0x0FFF` | ADS 系统码 | `6` 目标端口未找到、`7` 目标机不可达、`705` size 错、`706` data 错、`70A` 内存不足、`745` (1861) Timeout |
| `0xE4DD0001-0xE4DD0128` | OPC UA Client 自定义 | `0001` UA 调用失败、`0100` 已连接、`0101` 连接失败、`0102` 安全协商失败、`0107` 设备繁忙、`0109` namespace 未找到、`0110` 主机不可达、`0111` 主机不应答、`0112` 会话句柄无效、`0113` NodeID 未知、`0114/0115` identifier 类型问题、`0116` 节点句柄无效、`0117` Read 失败、`0118` Write 失败、`0119` 方法句柄无效、`011A-0124` Method 调用失败子分类、`0125` 节点类型信息不足、`0126` 属性 ID 无效、`0128` Server 不支持（如 HistoryUpdate） |
| `0xE4DE0100-0xE4DE0102` | HistoryUpdate 专用 | `0100` 数组长度错、`0101` 数据大小错、`0102` 至少一个值失败 |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc3_PLCopen_OpcUa`（References → Add library）；legacy FB 还需引用 `Tc2_OpcUa`
4. **TF6100 v2.x 起：在 I/O 区配置「OPC UA Virtual Device」并把 AMS Net ID 写入 `Tc3_PLCopen_OpcUa` 库参数列表的 `sNetId`**——这是 PDF §5.2.1 强制要求，否则 `UA_Connect` 直接报错
5. 编译 → 登录 → 运行
6. 按各文档 §6 / §7 中的「验证步骤」在线观察输入输出

所有例程都给出业务化的「场景 / 价值 / 验证步骤」三件套注释；导入后按注释操作即可观察 FB 真实行为。多 FB 联动的例程（如 UA_Read 需要前置 UA_Connect / UA_NodeGetHandle）在注释里明确给出「先跑哪个 demo 拿什么句柄抄到本程序」的依赖说明。

## 验证基线（2026-06-03）

- 18 / 18 文档：`verify_doc.py` 全 PASS
- 18 / 18 例程：`lint_tcpou.py` 全 PASS
- 全仓 `lint_tcpou.py --check-unique`：PASS（GUID 全局唯一）
- ⚠️ `InfoSys-checked: ⚠️ not-on-infosys` 的 FB：`UA_Browse` / `UA_ReadList`（InfoSys 当前版本未发布独立 per-topic 页面；事实仅基于 PDF §5.2.3.1 / §5.2.3.15）

## 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf)（v1.3.0，2026-04-08）
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/
- **Beckhoff 官方示例代码**：https://github.com/Beckhoff/TF6100_Samples（含 `TF6100_OpcUa_Client_Sample` 完整 PLC 工程 + `TF6100_OPCUA_HASample` 历史数据示例）
- **OPC UA PLCopen Companion Spec**：本库实现该规范的 16 个标准客户端 FB（Spec 全称「PLC Client Function Blocks based on IEC 61131-3」）
