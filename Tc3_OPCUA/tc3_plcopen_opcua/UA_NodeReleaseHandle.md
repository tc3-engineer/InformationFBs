# UA_NodeReleaseHandle

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537642123.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_NodeReleaseHandle.TcPOU`](../examples/P_Demo_UA_NodeReleaseHandle.TcPOU) |

---

## 1. 功能简述

OPC UA 节点句柄释放功能块（PDF §5.2.3.12）。释放由 `UA_NodeGetHandle` 申请的单个节点句柄；释放后该 `NodeHdl` 在 Server 端的内部句柄表对应槽位被回收，PLC 端不可再用该句柄做 Read / Write 操作。`UA_NodeReleaseHandleList` 是批量版本。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute       : BOOL;
    ConnectionHdl : DWORD;
    NodeHdl       : DWORD;
    Timeout       : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次释放 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeHdl` | `DWORD` | — | 要释放的节点句柄（来自 `UA_NodeGetHandle`） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done       : BOOL;
    Busy       : BOOL;
    Error      : BOOL;
    ErrorID    : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `DWORD` | 命令特定 ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次释放：FB 通过 ADS 通知 TF6100 客户端模块向 Server 释放该 `NodeHdl`。整个动作异步推进，必须每 PLC 周期调用让内部状态机推进。`Busy = TRUE` 期间不接受新命令；`Done = TRUE` 一个周期标志释放成功。

**何时调用**：① 业务停机：所有 Read / Write 都结束后，逐个释放 NodeHdl 再 `UA_Disconnect`；② 节点列表变化：业务需要的节点集合改变时，释放不再用的句柄取新的；③ 错误恢复：拿到 `UAC_E_INVAL_NODE_HDL`（`0xE4DD0116`）后清理无效句柄重新取。

**是否非要释放**：严格意义上 `UA_Disconnect` 关会话时 Server 端会自动清理所有附属节点句柄。**所以「会话关闭」是兜底**。但规范流程要求显式释放，原因是：① PLC 端 `NodeHdl` 变量值未清零，下一次启动复用旧值会拿到错误码（PLC 程序自己以为有效，操作时才报错）；② 业务节点动态变化场景下不能等 Disconnect。

**典型陷阱**：① 释放成功后忘了把 PLC 端 `NodeHdl` 变量清 0 → 后续误用陈旧句柄 → `UAC_E_INVAL_NODE_HDL`；② 多次重复释放同一 NodeHdl → 第二次 Error；③ 在 `ConnectionHdl` 已断的会话上释放 → 句柄相关错误；④ 单节点释放频率太高（每周期 GetHandle / ReleaseHandle）→ 极大浪费 OPC UA 流量，应该会话期间长持有。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 把 PLC 端 `NodeHdl` 变量清 0 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 会话已断，节点句柄也已自动失效，无需再释放 |
| `0xE4DD0116` | `UAC_E_INVAL_NODE_HDL` | 节点句柄无效 | 句柄已释放或从未存在；视为已清理 |

## 5. 使用注意 / 常见坑

- **释放成功后立即清零 PLC 端句柄变量**：避免代码后续误用陈旧值。
- **Disconnect 是兜底但不是替代**：规范流程「先 Release 句柄再 Disconnect 会话」更稳；只 Disconnect 的话 PLC 端句柄变量没人清，重启复用时会出错。
- **批量释放用 `UA_NodeReleaseHandleList`**：节点超过 5-10 个时批量版本远比串行调本 FB 高效。
- **不要在每个 PLC 周期都释放**：句柄是长寿命资源，会话级别复用；动态变化才需要释放重取。
- **工程经验补充**：把所有 NodeHdl 集中到 GVL 全局结构，配合「连接状态机」在 Disconnect 流程里循环释放并清零；业务层不直接调本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_NodeReleaseHandle.TcPOU`](../examples/P_Demo_UA_NodeReleaseHandle.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：OPC UA 客户端业务停机或节点集合动态变化时清理资源。例如「批次切换」场景：上一批工件用的节点不再读，需要释放给新批次的节点腾资源。
- **价值**：显式释放节点句柄、明确生命周期边界、避免 PLC 端节点句柄变量残留陈旧值。配合 `UA_Disconnect` 构成完整的「优雅关闭」流程。
- **替代方案对比**：① 不释放，等 `UA_Disconnect` 兜底——简单但 PLC 端句柄变量无人清；② 强制重启 PLC 程序——副作用太大；③ 用 `UA_NodeReleaseHandleList` 批量释放——节点多时首选；④ **本 FB**——单节点释放的标准入口，少量节点场景更直接。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.12（UA_NodeReleaseHandle）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537642123.html
- **相关 FB**：`UA_NodeGetHandle`（必须配对）；`UA_NodeReleaseHandleList`（批量版）；`UA_Disconnect`（最终兜底）
