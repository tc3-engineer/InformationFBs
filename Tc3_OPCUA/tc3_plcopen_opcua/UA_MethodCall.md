# UA_MethodCall

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537638027.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_MethodCall.TcPOU`](../examples/P_Demo_UA_MethodCall.TcPOU) |

---

## 1. 功能简述

OPC UA 方法调用功能块（PDF §5.2.3.7）。在远端 OPC UA Server 上调用一个 Method，传入参数、收取返回参数。这是本库里输入数量最多的 FB（15 个 VAR_INPUT），原因是 OPC UA Method 调用需要分别描述输入参数信息（`ST_UAMethodArgInfo` 数组）、输入数据（定长 / 变长两个 buffer）、输出参数信息（meta）以及输出数据 buffer——所有这些都需要客户端事先准备好缓冲区指针和大小。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute                     : BOOL;
    ConnectionHdl               : DWORD;
    MethodHdl                   : DWORD;
    nNumberOfInputArguments     : UDINT;
    pInputArgInfo               : POINTER TO ST_UAMethodArgInfo;
    cbInputArgInfo              : UDINT;
    pInputArgData               : PVOID;
    cbInputArgData              : UDINT;
    pInputWriteData             : PVOID;
    cbInputWriteData            : UDINT;
    nNumberOfOutputArguments    : UDINT;
    pOutputArgInfo              : POINTER TO ST_UAMethodArgInfo;
    cbOutputArgInfo             : UDINT; 
    pOutputArgInfoAndData       : PVOID;
    cbOutputArgInfoAndData      : UDINT; 
    Timeout                     : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次方法调用 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `MethodHdl` | `DWORD` | — | 由 `UA_MethodGetHandle` 返回的方法句柄 |
| `nNumberOfInputArguments` | `UDINT` | — | 输入参数数量 |
| `pInputArgInfo` | `POINTER TO ST_UAMethodArgInfo` | — | 输入参数信息数组的地址（`ARRAY[1..n] OF ST_UAMethodArgInfo` 配 `ADR()`） |
| `cbInputArgInfo` | `UDINT` | — | 输入参数信息数组的总字节数 |
| `pInputArgData` | `PVOID` | — | 定长输入参数（如 `DINT` / `LREAL`）的缓冲区地址 |
| `cbInputArgData` | `UDINT` | — | 定长输入缓冲区字节数 |
| `pInputWriteData` | `PVOID` | — | 变长输入参数（如 `STRING` / `ByteString`）的缓冲区地址 |
| `cbInputWriteData` | `UDINT` | — | 变长输入缓冲区字节数 |
| `nNumberOfOutputArguments` | `UDINT` | — | 输出参数数量 |
| `pOutputArgInfo` | `POINTER TO ST_UAMethodArgInfo` | — | 输出参数信息数组地址（业务可填 `nLenData` 指定输出缓冲；其他字段可不填以「不做类型校验」） |
| `cbOutputArgInfo` | `UDINT` | — | 输出参数信息数组字节数 |
| `pOutputArgInfoAndData` | `PVOID` | — | 输出参数总缓冲区地址（包含输出数量 `DINT` + 4 字节保留 + 输出 `ST_UAMethodArgInfo` 数组 + 纯数据，**1-byte alignment 紧凑布局**） |
| `cbOutputArgInfoAndData` | `UDINT` | — | 输出参数总缓冲区字节数 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    cbRead_R     : UDINT;
    Done         : BOOL;
    Busy         : BOOL;
    Error        : BOOL;
    ErrorID      : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `cbRead_R` | `UDINT` | 实际接收的字节数总和 |
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `UDINT` | 命令特定 ADS 错误码 |

### VAR_IN_OUT

无。

#### ST_UAMethodArgInfo（PDF §5.2.2.18）

```iecst
TYPE ST_UAMethodArgInfo:
STRUCT
    DataType        : E_UADataType := -1;
    ValueRank       : DINT := 2147483647;
    ArrayDimensions : ARRAY[1..3] OF UDINT := [0,0,0];
    nLenData        : DINT;
END_STRUCT
END_TYPE
```

| 字段 | 默认值 | 说明 |
|---|---|---|
| `DataType` | `-1` (Undefined) | 参数 UA 数据类型（如 `eUAType_Int32`、`eUAType_Double`、`eUAType_String`） |
| `ValueRank` | `2147483647` | 参数维度：`-1` 标量 / 0+ 数组 |
| `ArrayDimensions` | `[0,0,0]` | 数组维度长度（最多 3 维） |
| `nLenData` | — | 参数长度；**输出参数的 STRUCT 必填，用于确定输出目标内存大小** |

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次方法调用：FB 把 `pInputArgInfo` + `pInputArgData` + `pInputWriteData` 描述的所有输入参数打包成 OPC UA Method Call 请求发给 Server；过程中 `Busy := TRUE`；Server 执行 Method 后返回输出参数，FB 把它们解码到 `pOutputArgInfoAndData` 指向的缓冲区，`cbRead_R` 给出总字节数。`Done := TRUE` 一个周期标志完成。

**输入参数三个缓冲区**：① `pInputArgInfo` 是 `ARRAY[1..nInput] OF ST_UAMethodArgInfo`，描述每个参数的类型、长度、维度；② `pInputArgData` 包含定长参数的实际值（`DINT` / `BOOL` / `LREAL` 等紧凑排列）；③ `pInputWriteData` 包含变长参数的实际值（`STRING` 内容、`ByteString` 字节流）。简单的方法可能只用 ArgInfo + ArgData 两个缓冲，不用 WriteData。

**输出参数缓冲区布局**：PDF §5.2.3.7 指明 `pOutputArgInfoAndData` 缓冲区有特殊布局：「输出参数数量（`DINT`）+ 4 字节保留 + ARRAY OF `ST_UAMethodArgInfo`（每参数一个）+ 纯数据」全部 1-byte alignment 紧凑排列。业务侧解析时按这个布局逐字段抽取。

**`pOutputArgInfo`**：业务可填 `nLenData` 告知 FB 每个输出参数预留多少字节；其他字段（`DataType` / `ValueRank` / `ArrayDimensions`）可设默认值不做类型校验，由 FB 接受 Server 返回的实际类型。

**典型用法**：① `UA_Connect → UA_MethodGetHandle` 取方法句柄；② 业务事件触发：业务侧准备 `aInputArgInfos`、定长数据 `nInputDint`、变长 `sInputString`；③ 调本 FB；④ 解析 `aOutputBuffer` 拿到输出参数。

**典型陷阱**：① `pOutputArgInfo` 的 `nLenData` 没填 → 输出缓冲区分配 0 字节，Server 返回数据被截断；② 缓冲区大小估算不足 → `cbRead_R` 可能仍 < 实际需求，需要按错误重试用更大缓冲；③ 输入 `nNumberOfInputArguments` 与实际数组长度不符 → Server 端解码错；④ Method 输出超过 3 维 → PDF 明确 `UAC_E_TOOMUCHDIM`（`0xE4DD011F`）；⑤ 类型错配（PLC 给 `INT` 但 Method 要 `STRING`） → `UAC_E_CALL_FAILED_TYPEMISMATCH`（`0xE4DD0121`）；⑥ 方法句柄无效（会话断开后未重连 → 用陈旧句柄） → `UAC_E_INVAL_NODEMETHOD_HDL`（`0xE4DD0119`）。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 按布局解析 `pOutputArgInfoAndData` 缓冲 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 | 在 I/O 区配 OPC UA Virtual Device |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`；远端方法可能耗时长 |
| `0xE4DD0119` | `UAC_E_INVAL_NODEMETHOD_HDL` | 方法句柄无效 | 重新 `UA_MethodGetHandle` |
| `0xE4DD011A` | `UAC_E_CALL_FAILED` | 方法调用失败，原因未知 | 查 Server 日志 |
| `0xE4DD011B` | `UAC_E_CALLDECODE_FAILED` | 调用成功但返回值解码失败 | 检查输出缓冲布局 / 大小 |
| `0xE4DD011D` | `UAC_E_CALL_FAILED_BADINTERNAL` | UA_BadInternal | Server 内部错；查 Server |
| `0xE4DD011E` | `UAC_E_METHODIDINVALID` | MethodID 未知 | 句柄过期 / Server 重启重新取 |
| `0xE4DD011F` | `UAC_E_TOOMUCHDIM` | 方法输出含 > 3 维参数 | 协议层限制，需 Server 端方法重新设计 |
| `0xE4DD0120` | `UAC_E_CALL_FAILED_INVALIDARG` | UA_BadInvalidArgument | 检查输入参数值合法性 |
| `0xE4DD0121` | `UAC_E_CALL_FAILED_TYPEMISMATCH` | 输入参数类型不匹配 | 检查 `aInputArgInfos[i].DataType` 与实际数据 |
| `0xE4DD0122` | `UAC_E_CALL_FAILED_OUTOFRANGE` | UA_BadOutOfRange | 检查参数取值范围 |
| `0xE4DD0123` | `UAC_E_CALL_FAILED_BADSTRUCTURE` | OpcUa_BadStructureMissing | 输入参数结构缺失 |
| `0xE4DD0124` | `UAC_E_CALL_TYPEMISMATCH_OUTPARAM` | 调用成功但输出参数类型不匹配 | 检查 `aOutputArgInfos` 与 Method 实际输出 |

## 5. 使用注意 / 常见坑

- **本 FB 是全库最复杂的 FB**：15 个输入需要业务侧严格准备好所有缓冲区指针 + 大小，没有任何「便利方法」简化。但一旦封装好，可调任意 OPC UA Method 包括 Server 端 PLC FB METHOD、第三方设备 RPC 接口等。
- **输出缓冲布局必须严格按 PDF §5.2.3.7 规范解析**：「输出数量 DINT + 4 字节保留 + ArgInfo 数组 + 纯数据，1-byte alignment」；解析代码常用 `MEMCPY` 按偏移量抽取。
- **`pOutputArgInfo.nLenData` 必填**：告诉 FB 每个输出参数预留多少字节，否则 Server 数据被截断。
- **STRUCT 结构作为方法参数不支持**：和 Read / Write 一样，StructuredDataType 是 PLCopen Client 硬限制（PDF §8.1）。
- **慢方法用大 `Timeout`**：Server 端 Method 可能涉及数据库查询、外部 API、计算等慢操作；按业务最坏耗时 × 2 设 `Timeout`。
- **工程经验补充**：把每个常用方法封装成自己的辅助 FB（例如 `FB_CallStartOrder` 内部组装好 `aInputArgInfos` / `aInputData` / 输出解析），业务层只看「输入业务字段 → 等 Done → 取输出业务字段」三段式；这样业务代码读起来就像本地函数调用，本 FB 的复杂度被封装在内。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_MethodCall.TcPOU`](../examples/P_Demo_UA_MethodCall.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：调远端 OPC UA Server 上的业务方法。例如调 MES 的 `StartOrder(DINT, STRING) : BOOL`、SCADA 报警的 `AcknowledgeAlarm(DINT)`、第三方机器人控制 RPC `MoveToPose(LREAL[6]) : INT`。覆盖工业 RPC、远程控制、复杂业务交互场景。
- **价值**：把 OPC UA Method Call 服务的协议细节（参数编码、Method 寻址、调用结果解码）封装成一次 FB 调用。比自己用 ADS + 私有 socket 实现 RPC 节省数月开发量。比把方法换成 `UA_Write` + 服务端订阅触发器优雅得多（无需 Server 端额外开发）。
- **替代方案对比**：① `UA_Write` 写一个触发节点 + Server 端订阅触发器执行业务——能用但参数 / 返回值传递麻烦、需 Server 端额外开发；② REST API——非 OPC UA 场景；③ 自己实现 OPC UA Call 协议——可行但要写数百行 Binary Encoding；④ **本 FB**——PLCopen 标准 RPC 入口，跨厂家 Server 通用。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.7（UA_MethodCall）、§5.2.2.18（ST_UAMethodArgInfo）、§5.2.2.5（E_UADataType）、§8.2.3（错误码 `0xE4DD0119`–`0xE4DD0124`）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537638027.html
- **示例代码**：Beckhoff 提供的 `TF6100_OpcUa_Client_Sample` PLC 工程（PDF §6 / GitHub `Beckhoff/TF6100_Samples`）
- **相关 FB**：`UA_MethodGetHandle`（前置取句柄）；`UA_MethodReleaseHandle`（停机释放）；`UA_NodeGetHandle` + `UA_Read` / `UA_Write`（数据节点访问，不是方法）
