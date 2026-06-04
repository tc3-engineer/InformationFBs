# UA_HistoryUpdate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/5745233931.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_HistoryUpdate.TcPOU`](../examples/P_Demo_UA_HistoryUpdate.TcPOU) |

---

## 1. 功能简述

OPC UA 历史数据写入功能块（PDF §5.2.3.6，要求 TwinCAT 3.1 ≥ 4024.1 + `Tc3_PLCopen_OpcUa >= v3.1.9.0`）。把一批带时间戳的历史数据一次性写入支持 HistoryUpdate 功能的 OPC UA Server（如 TwinCAT OPC UA Server 的 Historical Access 模块）。每个数据用 `UAHADataValue` 对象表示（含 Value 指针、StatusCode、SourceTimeStamp、ServerTimeStamp），单次最多 1000 个值。常用于补传某时段的历史业务数据（机器状态归档、报表回填等）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute        : BOOL;
    ConnectionHdl  : DWORD;
    NodeHdl        : DWORD;
    PerformInsert  : BOOL; 
    PerformReplace : BOOL;
    DataValueCount : UINT; 
    Timeout        : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次历史写入 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeHdl` | `DWORD` | — | 目标历史节点的句柄（来自 `UA_NodeGetHandle`） |
| `PerformInsert` | `BOOL` | — | PDF 默认 `TRUE`（即新值插入历史） |
| `PerformReplace` | `BOOL` | — | PDF 默认 `FALSE`。若已有同时间戳值要替换则设 `TRUE`，**目前仅 SQL adapter 支持**，其他 adapter 忽略 |
| `DataValueCount` | `UINT` | — | 本次传送的值数量（最多 1000） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done      : BOOL;
    Busy      : BOOL;
    Error     : BOOL;
    ErrorID   : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 至少一个值写失败（具体到哪个看 `ValueErrorIDs`） |
| `ErrorID` | `DWORD` | 命令特定 ADS 错误码 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    DataValues       : ARRAY[*] OF UAHADataValue;
    ValueErrorIDs    : ARRAY[*] OF DWORD;    
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DataValues` (read-only) | `ARRAY OF UAHADataValue` | 历史值数组；长度可任意但必须 ≥ `DataValueCount`。每个 `UAHADataValue` 对象封装 Value 指针 + StatusCode + 时间戳。FB 只读 |
| `ValueErrorIDs` (write-only) | `ARRAY OF DWORD` | 每值的错误码数组；长度 ≥ `DataValueCount`。FB 写入：单值写失败时填 `0x80000000` 类码，业务侧据此重试 |

#### UAHADataValue（PDF §5.2.2.23）

```iecst
aDataValues : ARRAY [1..50] OF UAHADataValue(ValueSize:=SIZEOF(LREAL));
```

| Property | 类型 | Access | 初始值 | 说明 |
|---|---|---|---|---|
| `Value` | `PVOID` | Set | - | 数据源地址（用 `ADR()`）；FB 复制数据到对象内部 |
| `StatusCode` | `UAHAUpdateStatusCode` | Get/Set | `HistorianRaw` | 历史数据状态码：`HistorianRaw`（原始）/ `HistorianCalculated` / `HistorianInterpolated` / `HistorianPartial` / `HistorianExtraData` / `HistorianMultiValue` |
| `SourceTimeStamp` | `ULINT` | Get/Set | 0 | UTC 源时间戳（用 `F_GetSystemTime()` 取） |
| `ServerTimeStamp` | `ULINT` | Get/Set | 0 | UTC Server 时间戳（PDF 注「此功能当前不支持」） |

实例化时 `ValueSize := SIZEOF(LREAL)`（或其他目标类型）决定每个对象内部缓冲区大小。

#### UAHAUpdateStatusCode（PDF §5.2.2.24）

```iecst
TYPE UAHAUpdateStatusCode :
(
    HistorianRaw          := 0,
    HistorianCalculated   := 1,
    HistorianInterpolated := 2,
    Reserved              := 3,
    HistorianPartial      := 4,
    HistorianExtraData    := 8,
    HistorianMultiValue   := 16
) UDINT;
END_TYPE
```

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次批量历史写入：FB 把 `DataValues[1..DataValueCount]` 全部值发给 Server，等 Server 处理完返回；过程中 `Busy := TRUE`。每个值独立处理：成功则该位置 `ValueErrorIDs[i] = 0`；失败则填错误码，整体 `Error := TRUE`、`ErrorID` 给出汇总错误码。

**PDF 提醒「数据量越大 PLC 执行越久」**：1000 个值的极限会占用较大 ADS / OPC UA 协议处理时间，PLC 周期任务里要预估超时并把 `Timeout` 加大（建议 ≥ T#30S）。批量越大单值开销越小，但极限附近会触碰路由内存。

**典型用法**：① 离线机器报表回填：业务程序周期采集，缓存在 PLC 本地 `ARRAY[1..50] OF UAHADataValue`，每分钟一次 `UA_HistoryUpdate` 批量推到 Server 的 SQL adapter；② 设备状态归档：状态变更时记一条带时间戳的 `Value + StatusCode = HistorianRaw`，本地累积后批量推送；③ 计算结果回填：本地算出的 KPI（含 `HistorianCalculated` 状态码标识其性质）补写历史。

**和 Server 端 Historical Access 周期采样的区别**（PDF 明确）：如果数据本来就是周期采集，让 Server 端的 Historical Access 模块自己采更高效——只需在配置工具里选监控节点设采样率。本 FB 适合「非周期性、特定时段、需要补写」的场景。

**典型陷阱**：① 数据类型大小不匹配 `UAHADataValue(ValueSize := ...)`：实例化时指定的 `ValueSize` 必须与实际写的 PLC 变量类型大小一致，错配 → `UAC_E_INVALID_DATASIZE`（`0xE4DE0101`）；② 整个 `DataValues` 数组里混合不同数据类型 → `UAC_E_INVALID_DATASIZE`，所有 `UAHADataValue` 必须同类型；③ `DataValueCount` 超出 `DataValues` 实际长度 → 读越界，PLC 崩；④ 目标 Server 不支持 HistoryUpdate（很多第三方 Server 没实现） → `UAC_E_NOTSUPPORTED`（`0xE4DD0128`）；⑤ 用 `PerformReplace := TRUE` 但 Server 不是 SQL adapter → PDF 明确这些 adapter 忽略 Replace，不会报错但行为是「插入新值不替换旧值」造成时间戳重复。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码或客户端自定义码。`ValueErrorIDs[i]` 是单值错误码（成功为 0）。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 全部成功 | 清缓冲准备下一批 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `DataValues` / `ValueErrorIDs` 数组长度 ≥ `DataValueCount` |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`（大批量推荐 ≥ T#30S） |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0116` | `UAC_E_INVAL_NODE_HDL` | 节点句柄无效 | 重新 `UA_NodeGetHandle` |
| `0xE4DD0128` | `UAC_E_NOTSUPPORTED` | Server 不支持 HistoryUpdate | 换用支持的 Server 或改其他写入方式 |
| `0xE4DE0100` | `UAC_E_INVALID_ARRAY_LENGTH` | `DataValueCount` 与传入数组不匹配 | 检查 `DataValueCount` 和数组长度 |
| `0xE4DE0101` | `UAC_E_INVALID_DATASIZE` | 数据值大小无效 | 检查 `UAHADataValue.ValueSize` 与实际类型一致 |
| `0xE4DE0102` | `UAC_E_SUBERROR` | 至少一个值失败 | 遍历 `ValueErrorIDs` 找具体失败项 |
| 单值 `0x80000000` | — | 单值写入失败（PDF §5.2.3.6） | 业务侧重试该值 |

## 5. 使用注意 / 常见坑

- **所有 `UAHADataValue` 必须同类型**：实例化时 `ValueSize` 固定，同一数组里不能混 `LREAL` 和 `INT`。
- **`PerformReplace` 仅 SQL adapter 用**：其他 adapter 不会报错但忽略此选项，可能造成时间戳重复。生产代码应检查 Server adapter 类型。
- **极限 1000 值 + 大 `Timeout`**：单次推 1000 个值在路由内存压力下需要 T#30S+ 才稳；推得太大可能触发 ADS router memory 不足（PDF §8.1 第二条提到此现象）。
- **时间戳必须递增**：业务侧保证 `aDataValues[1].SourceTimeStamp < aDataValues[2].SourceTimeStamp < ...`；多数 Server 实现按时间戳建索引，乱序会 Server 端排序但增加开销。
- **Server 端要开 HistoryUpdate**：TwinCAT OPC UA Server 默认不启用 Historical Access；要在配置工具里把目标节点标记为「记录历史」并选 adapter（File / SQL）。
- **本 FB 是 PLCopen-based Client 的硬限制**：StructuredDataType 不能历史写（PDF §8.1 第一条扩展到 HistoryUpdate）；要写复合结构必须按字段拆开各调一次本 FB。
- **工程经验补充**：补传场景常用「本地缓冲 50 条 → 触发一次推送 → 等 Done → 检查 ValueErrorIDs → 失败项保留下次重试 → 全成功才清缓冲」的状态机。不要用 `DataValueCount := 1` 单值推（每次都要一次往返开销，浪费）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_HistoryUpdate.TcPOU`](../examples/P_Demo_UA_HistoryUpdate.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：① 网络抖动导致 SCADA 没收到某段实时数据，PLC 本地缓存的备份现需补传到 MES 历史库；② 工厂离线设备每周一次接入 Server 把整周采集的历史数据一次性推送；③ 离线计算（如班次能耗汇总）结果回填到历史数据库，业务报表能查到。
- **价值**：单次 FB 调用推 1000 条历史值；屏蔽 OPC UA HistoryUpdate Service 的全部协议细节（PerformInsertReplace、UpdateHistoryData、ValueErrorIDs 解码）。不依赖 SCADA 数据库直连或 SQL 写法，跨 Server 适配。
- **替代方案对比**：① 让 Server 端 Historical Access 自动周期采集——适合实时不间断采集，不适合补传 / 离线场景；② 写 SQL 直接插数据库——绕过 OPC UA Server 的数据治理 / 权限 / 类型校验，不推荐；③ 单值 `UA_Write` 写 N 次——每条独立往返，开销 N 倍于本 FB；④ **本 FB**——批量 + 协议标准 + 含状态码 + 时间戳精确控制，是历史数据补传 / 离线推送的标准方案。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.6（UA_HistoryUpdate）、§5.2.2.23（UAHADataValue）、§5.2.2.24（UAHAUpdateStatusCode）、§8.2.3（错误码含 0xE4DE0100/0101/0102）、§8.1（ADS router 内存提示）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/5745233931.html
- **示例代码**：Beckhoff 提供的 `TF6100_OPCUA_HASample` PLC 工程（PDF §6 / GitHub `Beckhoff/TF6100_Samples`）
- **相关 FB**：`UA_Connect` / `UA_NodeGetHandle`（前置）；`UA_Read` / `UA_Write`（实时单值读写，不带时间戳）；服务器端 Historical Access 配置（用于周期采集场景）
