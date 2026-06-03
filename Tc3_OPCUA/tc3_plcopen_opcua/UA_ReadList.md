# UA_ReadList

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
| Example | [`examples/P_Demo_UA_ReadList.TcPOU`](../examples/P_Demo_UA_ReadList.TcPOU) |

---

## 1. 功能简述

OPC UA 节点批量读功能块（PDF §5.2.3.15）。一次性从多个节点读数据到一个连续缓冲区；按 `UA_Read` 的协议但批量化。`UA_Read` 单节点读一次往返；`UA_ReadList` 读 N 个节点也只一次往返，大幅降低 OPC UA 流量。配合 `UA_NodeGetHandleList` 取齐句柄后用作主力周期采集 FB。

⚠️ 该 FB 的 InfoSys 当前版本未给出独立 per-topic 页面，元信息 `InfoSys-checked` 标 `⚠️ not-on-infosys`；事实核对仅基于 PDF §5.2.3.15。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute          : BOOL;
    ConnectionHdl    : DWORD;
    NodeHdlCount     : UINT;
    NodeHdls         : ARRAY[1..nMaxNodeIDsInList] OF DWORD;
    stNodeAddInfo    : ARRAY[1..nMaxNodeIDsInList] OF ST_UANodeAdditionalInfo;
    pVariable        : PVOID;
    cbData           : ARRAY[1..nMaxNodeIDsInList] UDINT;
    cbDataTotal      : UDINT;
    Timeout          : TIME := DEFAULT_ADS_TIMEOUT;    
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次批量读 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeHdlCount` | `UINT` | — | 要读的节点数 |
| `NodeHdls` | `ARRAY[1..nMaxNodeIDsInList] OF DWORD` | — | 节点句柄数组（来自 `UA_NodeGetHandleList` 或 `UA_NodeGetHandle`） |
| `stNodeAddInfo` | `ARRAY[1..nMaxNodeIDsInList] OF ST_UANodeAdditionalInfo` | — | 每节点的附加信息（属性 ID、IndexRange） |
| `pVariable` | `PVOID` | — | 接收缓冲区首地址；所有节点数据按 `NodeHdls` 顺序连续写入 |
| `cbData` | `ARRAY[1..nMaxNodeIDsInList] OF UDINT` | — | 每节点数据大小（字节） |
| `cbDataTotal` | `UDINT` | — | 总缓冲区大小 = SUM(`cbData[1..NodeHdlCount]`) |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done      : BOOL;
    Busy      : BOOL;
    Error     : BOOL;
    ErrorID   : UDINT;
    cbData_R  : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `UDINT` | 命令特定 ADS 错误码 |
| `cbData_R` | `UDINT` | 实际接收的总字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次批量读：FB 把 `NodeHdls[1..NodeHdlCount]` 一次性提交给 Server，按每节点的 `stNodeAddInfo[i]`（属性 ID、IndexRange）读取，Server 把所有节点的值并发取出并按顺序拼接成响应；FB 把响应解码到 `pVariable` 指向的连续缓冲区，按 `cbData[i]` 的偏移依次摆放第 1, 2, ..., N 个节点的数据。`cbData_R` 给出总字节数。

**连续缓冲区布局**：例如 3 个节点 `LREAL` + `INT` + `BOOL`，业务侧需声明 `ARRAY[1..11] OF BYTE`（= 8 + 2 + 1）或者一个 PACK 结构 `STRUCT fVal:LREAL; nVal:INT; bVal:BOOL; END_STRUCT`（注意是否需要 `{attribute 'pack_mode' := '0'}` 取消对齐填充）。`cbData[1] = 8`, `cbData[2] = 2`, `cbData[3] = 1`, `cbDataTotal = 11`。

**`stNodeAddInfo` 每节点独立配置**：每个节点可以读不同属性（节点 1 读 Value、节点 2 读 DisplayName），常见 99% 场景全是 Value 属性。

**典型陷阱**：① `cbDataTotal` 与 `cbData` 数组累加不一致 → 缓冲偏移错乱 → 数据写错位置；② `pVariable` 缓冲太小（< `cbDataTotal`）→ 越界覆盖其他变量；③ `pVariable` 指向栈上变量 → 异步期间地址失效；④ `nMaxNodeIDsInList` 库参数没调高就传超过 10 的 `NodeHdlCount`；⑤ 把本 FB 当 1-2 节点的小读用——开销大于直接调多个 `UA_Read`，4+ 节点才有明显收益。

**部分节点失败**：PDF 没明确单节点错误码输出。整批 `Error` 表示至少一个失败，但不像 `UA_NodeGetHandleList` 那样有 per-node `NodeErrorIDs`。失败诊断只能基于 `cbData_R` 与 `cbDataTotal` 比对 + 缓冲区数据合理性检查；要精细化诊断只能改用单 `UA_Read` 逐个读。这是本 FB 相比 List Get 在诊断粒度上的弱点。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 全部成功 | 按 `cbData` 偏移解析 `pVariable` 缓冲 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `cbDataTotal` = SUM(`cbData[1..N]`) |
| `0x706` | `DEVICE_INVALIDDATA` | 参数值无效 | 检查 `stNodeAddInfo` / `NodeHdls` |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0116` | `UAC_E_INVAL_NODE_HDL` | 某节点句柄无效 | 重新 `UA_NodeGetHandle(List)`；本 FB 不区分到具体哪个节点 |
| `0xE4DD0117` | `UAC_E_UAREADFAILED` | UA Read 失败 | 看 Server 日志 |

## 5. 使用注意 / 常见坑

- **从 4 个节点起本 FB 收益明显**：1-3 个节点 `UA_Read` 串行更简单；4+ 节点开始批量收益线性提升。
- **`cbDataTotal` 严格 = SUM(`cbData[1..N]`)**：错就缓冲偏移错位，所有节点数据写到错误位置。
- **缓冲区放 GVL / PROGRAM / FB 实例成员**：异步保活。
- **结构体打包模式**：用 STRUCT 接收缓冲时注意默认有对齐填充（4 字节 / 8 字节）；要严格按字节连续摆放需 `{attribute 'pack_mode' := '0'}` 取消填充。
- **本 FB 失败诊断粒度差**：整体 Error 时无法精确到具体哪个节点失败。生产代码可在初始化期单独跑一次 `UA_Read` 验证每个节点，运行期才上 List。
- **StructuredDataType 不支持**：和 `UA_Read` 一样 PLCopen Client 硬限制。
- **InfoSys 没单页**：本 FB 在 InfoSys 上没有独立 per-topic URL，元信息 `InfoSys-checked` 标 `⚠️ not-on-infosys`；权威信息仅 PDF §5.2.3.15。
- **工程经验补充**：把要读的节点定义在一个 GVL 数据结构，封装一个 helper FB（`FB_McpReadAllMesData`）内部组装 `NodeHdls` / `cbData` / `stNodeAddInfo`，业务层只调一次 helper 就拿到所有数据，本 FB 复杂度被封装。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_ReadList.TcPOU`](../examples/P_Demo_UA_ReadList.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：从远端 MES Server 周期读 5 个生产数据节点（液位、压力、温度、流量、订单号）。配合 `UA_NodeGetHandleList` 取齐句柄后，每周期单次 `UA_ReadList` 一并采集，替代 5 次 `UA_Read` 的 5 次往返。
- **价值**：从 N 次往返压缩到 1 次；周期任务执行时间从数百毫秒缩到几十毫秒；OPC UA 网络流量降 N 倍。这是「数据采集层」的工业标准做法。
- **替代方案对比**：① 串行 N 次 `UA_Read`——简单但慢；② 用 OPC UA Subscription（PLCopen Client 不直接支持）——理想方案但 PLCopen 库没实现；③ 用 I/O Client 配置静态映射——静态节点首选但运行期动态做不到；④ **本 FB**——动态批量周期读的标准入口。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.15（UA_ReadList）、§5.2.2.20（ST_UANodeAdditionalInfo）、§5.2.4（nMaxNodeIDsInList）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/（库根，本 FB 在 InfoSys 没单独页）
- **相关 FB**：`UA_NodeGetHandleList`（前置批量取句柄）；`UA_Read`（单节点版本）；`UA_NodeReleaseHandleList`（停机释放）；`UA_Write`（写）
