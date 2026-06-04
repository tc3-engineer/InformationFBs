# UA_MethodGetHandle

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537639051.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_MethodGetHandle.TcPOU`](../examples/P_Demo_UA_MethodGetHandle.TcPOU) |

---

## 1. 功能简述

OPC UA 方法句柄获取功能块（PDF §5.2.3.8）。把「Object NodeID + Method NodeID」组合解析为方法句柄 `MethodHdl`，后续 `UA_MethodCall` 用此句柄调远端 Server 上的方法。OPC UA 中 Method 必须挂在 Object 节点下（Object 是接收者，Method 是动作）；本 FB 在客户端模块内部建立两者关联并返回句柄。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute          : BOOL;
    ConnectionHdl    : DWORD;
    ObjectNodeID     : ST_UANodeID;
    MethodNodeID     : ST_UANodeID;
    Timeout          : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次句柄申请 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `ObjectNodeID` | `ST_UANodeID` | — | 方法宿主 Object 的 NodeID |
| `MethodNodeID` | `ST_UANodeID` | — | 方法本身的 NodeID（对应 UA namespace 里 Method 节点的 Identifier 属性） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    MethodHdl   : DWORD;
    Done        : BOOL;
    Busy        : BOOL;
    Error       : BOOL;
    ErrorID     : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `MethodHdl` | `DWORD` | 方法句柄；后续 `UA_MethodCall` 以此寻址 |
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `UDINT` | 命令特定 ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次方法解析：FB 在 Server 上验证 Object 节点存在 + Method 节点存在 + Method 是 Object 的有效 `HasComponent` 引用，匹配后客户端模块内部建立映射返回 `MethodHdl`。整个动作异步推进，必须每 PLC 周期调用让内部状态机推进。

**和 `UA_NodeGetHandle` 的区别**：节点句柄是「数据节点」（Variable），方法句柄是「Object + Method 关联」（含两个 NodeID）。OPC UA 协议层 Method 调用必须显式传 Object NodeID 因为同一 Method 定义（如 `Reset()`）可能在多个 Object 下作为不同方法实例存在；客户端模块在句柄解析阶段把这两个 NodeID 绑成一个不透明 ID 加速后续 Call。

**句柄寿命**：会话存活期间有效；会话断开自动失效。停机时用 `UA_MethodReleaseHandle` 释放。

**典型用法**：① 启动期：`UA_Connect → UA_GetNamespaceIndex → UA_NodeGetHandle` 取数据节点 + `UA_MethodGetHandle` 取方法句柄；② 业务期：按业务事件触发 `UA_MethodCall(MethodHdl, 输入参数, 输出参数)`；③ 停机：`UA_MethodReleaseHandle` 释放 + `UA_Disconnect`。

**典型陷阱**：① `ObjectNodeID` 或 `MethodNodeID` 拼错 → `UAC_E_INVALIDNODEID`（`0xE4DD0113`）；② Method 不属于该 Object（其他 Object 下的同名方法）→ Server 端验证失败；③ Method 节点 AccessLevel 不允许调用 → 后续 Call 时报；④ namespace index 用了硬编码、Server 重启后变化 → 找不到节点。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 用 `MethodHdl` 做后续 `UA_MethodCall` |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0113` | `UAC_E_INVALIDNODEID` | NodeID 未知 | 检查 Object / Method NodeID 拼写 |
| `0xE4DD0119` | `UAC_E_INVAL_NODEMETHOD_HDL` | 方法句柄无效（罕见，通常在后续 Call 时报） | 重新申请 |
| `0xE4DD011E` | `UAC_E_METHODIDINVALID` | MethodID 未知（Call 时报） | 检查 `MethodNodeID` |

## 5. 使用注意 / 常见坑

- **Object + Method 两个 NodeID 必须同时给对**：两个都要存在且 Method 必须挂在 Object 下；只给 Method NodeID 不行（OPC UA 协议本身要求 Object 上下文）。
- **TwinCAT OPC UA Server 中 PLC FB 的 Method 表达**：Server 把 PLC 程序里的 Function Block 实例当 Object，FB 的 METHOD 当 Method；例如 PLC 里有 `fbWriter : FB_MesWriter;` 且 `FB_MesWriter` 有 `METHOD WriteRecord`，则 Object NodeID 是 `'GVL.fbWriter'` 类形式，Method NodeID 是 `'GVL.fbWriter.WriteRecord'` 类形式（具体依 namespace + PLC 暴露规则）。
- **句柄长期复用，不要循环取**：会话期一次取够，业务变更才 Release 重取。
- **多 Method 用串行 GetHandle**：本 FB 没有 List 版本（不像 `UA_NodeGetHandleList`）；要为 5 个方法各取句柄就要调 5 次本 FB。
- **工程经验补充**：把所有方法句柄集中到 GVL 全局结构（`gMethodHdls.hReset / hStart / hStop`），配合连接状态机自动管理。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_MethodGetHandle.TcPOU`](../examples/P_Demo_UA_MethodGetHandle.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：远端 OPC UA Server 暴露业务方法（如 MES 的 `'GVL.fbOrderMgr.StartOrder(nOrderId, sRecipe)'` 启动订单、`'fbReportGen.SubmitReport(...)'` 提交日报）。PLC 客户端业务事件触发时需通过 `UA_MethodCall` 调用这些方法；调用前必须先用本 FB 取方法句柄。
- **价值**：把方法解析从 OPC UA 协议层抽象出来；客户端模块缓存方法元信息（参数类型、参数数量），后续 Call 不必每次都跟 Server 重新协商。
- **替代方案对比**：① 把方法换成 `UA_Write` 触发 + Server 端订阅触发器实现——能用但 Server 端要写代码、参数返回值传递麻烦；② 跨厂家用 REST API——OPC UA 场景下不通用；③ **本 FB**——PLCopen 标准、与 `UA_MethodCall` 配套，RPC 风格调用的入口。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.8（UA_MethodGetHandle）、§5.2.2.19（ST_UANodeID）、§5.2.2.18（ST_UAMethodArgInfo）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537639051.html
- **相关 FB**：`UA_Connect` / `UA_GetNamespaceIndex`（前置）；`UA_MethodCall`（用 MethodHdl 调方法）；`UA_MethodReleaseHandle`（必须配对释放）
