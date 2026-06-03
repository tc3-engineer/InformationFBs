# UA_MethodReleaseHandle

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537640075.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_MethodReleaseHandle.TcPOU`](../examples/P_Demo_UA_MethodReleaseHandle.TcPOU) |

---

## 1. 功能简述

OPC UA 方法句柄释放功能块（PDF §5.2.3.9）。释放由 `UA_MethodGetHandle` 申请的方法句柄，对应客户端模块内部「Object + Method 关联表」中的条目回收。和 `UA_NodeReleaseHandle` 同理，会话关闭时 Server 端会兜底清理，但显式释放是规范流程。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute           : BOOL;
    ConnectionHdl     : DWORD;
    MethodHdl         : DWORD;
    Timeout           : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次释放 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `MethodHdl` | `DWORD` | — | 要释放的方法句柄（来自 `UA_MethodGetHandle`） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done     : BOOL;
    Busy     : BOOL;
    Error    : BOOL;
    ErrorID  : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `UDINT` | 命令特定 ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次释放：FB 通过 ADS 通知客户端模块解绑方法句柄；过程中 `Busy := TRUE`，完成后 `Busy` 落 `FALSE`，成功则 `Done := TRUE` 一个周期。整个动作异步推进，必须每 PLC 周期调用让内部状态机推进。

**何时调用**：① 业务停机：所有 `UA_MethodCall` 都不再发起后，释放方法句柄；② 业务变更：要换调不同的方法时，释放旧句柄取新的；③ `UA_MethodCall` 持续报 `UAC_E_INVAL_NODEMETHOD_HDL`（`0xE4DD0119`）→ 清理无效句柄重取。

**是否非要释放**：`UA_Disconnect` 关会话时 Server 端会自动清理。**但和节点句柄一样**，规范流程要求显式释放，原因是：① PLC 端 `MethodHdl` 变量值未清零，下次启动复用陈旧值会拿到错误码；② 业务方法集动态变化场景下不能等 Disconnect。

**典型陷阱**：① 释放成功后忘清零 PLC 端 `MethodHdl` 变量 → 后续误用；② 多次重复释放同一句柄 → 第二次报错；③ 在已断的会话上释放 → 句柄相关错误，但通常忽略此错误继续走清理流程。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 把 PLC 端 `MethodHdl` 变量清 0 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 会话已断，方法句柄已失效；忽略此错误 |
| `0xE4DD0119` | `UAC_E_INVAL_NODEMETHOD_HDL` | 方法句柄无效 | 句柄已释放或未存在；视为已清理 |

## 5. 使用注意 / 常见坑

- **成功后立即清零 PLC 端句柄变量**：避免后续误用陈旧值。
- **Disconnect 是兜底**：规范是先释放方法句柄再 Disconnect 会话；只 Disconnect 的话 PLC 端句柄变量没人清。
- **本 FB 无 List 批量版**：要释放 5 个方法句柄就调 5 次。
- **工程经验补充**：把所有方法句柄集中到 GVL 全局结构，配合连接状态机自动管理。停机流程：`UA_NodeReleaseHandleList → 循环 UA_MethodReleaseHandle → UA_Disconnect`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_MethodReleaseHandle.TcPOU`](../examples/P_Demo_UA_MethodReleaseHandle.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：业务停机或方法集变更时清理资源。例如「批次切换」：上一批工艺用的远端方法集（StartA、StopA、ResetA）不再调，要释放给新批次方法集（StartB、StopB）腾资源。
- **价值**：显式释放方法句柄、明确生命周期、避免 PLC 端句柄变量残留。配合 `UA_Disconnect` 构成「优雅关闭」流程。
- **替代方案对比**：① 不释放，等 Disconnect 兜底——PLC 端 MethodHdl 变量无人清；② 强制重启 PLC——副作用大；③ **本 FB**——精确释放单方法句柄的标准入口。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.9（UA_MethodReleaseHandle）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537640075.html
- **相关 FB**：`UA_MethodGetHandle`（必须配对）；`UA_MethodCall`（业务期使用）；`UA_Disconnect`（最终兜底）
