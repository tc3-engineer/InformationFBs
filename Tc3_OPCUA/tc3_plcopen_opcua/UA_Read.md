# UA_Read

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537643147.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_Read.TcPOU`](../examples/P_Demo_UA_Read.TcPOU) |

---

## 1. 功能简述

OPC UA 节点读功能块（PDF §5.2.3.14）。从已取句柄的节点读取数据到 PLC 本地缓冲区。`stNodeAddInfo` 可指定要读的属性（默认 `Value` 属性）和 IndexRange（数组节点用）。每次 `Execute` 上升沿触发一次读，完成后 `cbData_R` 给出实际接收字节数。**注意**：PLCopen 客户端**不支持** StructuredDataType（结构化类型），如需读结构化数据请改用 I/O Client（PDF §8.1 明示）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute           : BOOL;
    ConnectionHdl     : DWORD;
    NodeHdl           : DWORD;
    stNodeAddInfo     : ST_UANodeAdditionalInfo;
    pVariable         : PVOID;
    cbData            : UDINT;
    Timeout           : TIME := DEFAULT_ADS_TIMEOUT;    
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次读 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeHdl` | `DWORD` | — | 由 `UA_NodeGetHandle` 返回的节点句柄 |
| `stNodeAddInfo` | `ST_UANodeAdditionalInfo` | — | 附加信息：要读的 UA 属性（默认 `eUAAI_Value`）、IndexRange（数组节点） |
| `pVariable` | `PVOID` | — | 接收缓冲区首地址，用 `ADR()` 取地址；缓冲区必须足够大 |
| `cbData` | `UDINT` | — | 要读的最大字节数（缓冲区大小） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时（默认 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done        : BOOL;
    Busy        : BOOL;
    Error       : BOOL;
    ErrorID     : UDINT;
    cbData_R    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 成功完成时变 `TRUE` |
| `Busy` | `BOOL` | 命令执行中；`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `UDINT` | 命令特定 ADS 错误码 |
| `cbData_R` | `UDINT` | 实际读到的字节数 |

### VAR_IN_OUT

无。

#### ST_UANodeAdditionalInfo（PDF §5.2.2.20）

```iecst
TYPE ST_UANodeAdditionalInfo:
STRUCT
    eAttributeID     : E_UAAttributeID;
    nIndexRangeCount : UINT;
    nReserved        : ARRAY[1..2] OF BYTE; // fill bytes
    stIndexRange     : ARRAY[1..nMaxIndexRange] OF ST_UAIndexRange;
END_STRUCT
END_TYPE
```

| 字段 | 说明 |
|---|---|
| `eAttributeID` | 要读的 UA 属性（默认 `eUAAI_Value` = 13，即节点 Value 属性）；其他常见：`eUAAI_DataType`、`eUAAI_ValueRank`、`eUAAI_DisplayName` 等（详见 `E_UAAttributeID` PDF §5.2.2.1） |
| `nIndexRangeCount` | `stIndexRange` 数组中有效的元素数（0 = 不使用 IndexRange） |
| `nReserved` | 占位字节 |
| `stIndexRange` | 多维数组节点的索引范围 |

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次读：FB 通过 ADS 让 TF6100 客户端模块向 Server 发 OPC UA Read 请求；过程中 `Busy := TRUE`；收到应答（或 `Timeout` 到期）后 `Busy` 落 `FALSE`，成功则 `Done := TRUE` 一个周期 + 数据写入 `pVariable` 指向的缓冲区 + `cbData_R` 含实际字节数。

**缓冲区生命周期**：异步读期间（`Busy = TRUE`）系统会向 `pVariable` 指向的内存写入数据；该内存必须保活到 `Busy` 落沿，所以**不能**用栈上 / METHOD 局部变量做缓冲，必须用 PROGRAM / GVL / FB 实例成员。这是和 `ADSREAD` 类似的异步缓冲区约束。

**默认 Read 属性 = Value**：`stNodeAddInfo.eAttributeID` 缺省值 `eUAAI_Value`（13）即读节点的 Value 属性，这是 99% 业务场景所要的。如果是元数据查询场景（读节点的数据类型、显示名、AccessLevel 等）则设其他 attribute ID。

**`cbData_R` 用法**：对定长类型（`BOOL` / `INT` / `LREAL` 等）`cbData_R` 通常 = `SIZEOF(目标变量)`；对变长类型（`STRING` 内容、`ByteString`）`cbData_R` 是实际字节数，可能小于 `cbData`，业务侧用 `cbData_R` 截取有效数据。

**默认 `Value` 属性 vs `cbData`**：`cbData` 要足够大装下节点的最大可能值；定长类型给 `SIZEOF(变量)` 即可，变长类型按上限估算（PLC `STRING(80)` 上限是 81 字节含 NUL）。

**典型陷阱**：① `pVariable` 指向栈上变量 → 完成回调时缓冲已失效，数据写错地方甚至崩溃；② `cbData` 太小导致 Server 截断 → 拿到部分数据；③ 用本 FB 读 StructuredDataType（PLC `STRUCT` 类型直接映射出去的节点）→ PDF §8.1 明确不支持，必须改用 I/O Client；④ 用 NodeHdl = 0（没取过句柄就读）→ `UAC_E_INVAL_NODE_HDL`（`0xE4DD0116`）；⑤ 周期 Read 但忘了每周期都调（只在上升沿调一次）→ 内部状态机不推进，永远 `Busy = TRUE`。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 读取 `pVariable` 缓冲数据（按 `cbData_R` 截取） |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `cbData` 是否足够 |
| `0x706` | `DEVICE_INVALIDDATA` | 参数值无效 | 检查 NodeID、属性 ID、IndexRange |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0116` | `UAC_E_INVAL_NODE_HDL` | 节点句柄无效 | 重新 `UA_NodeGetHandle` |
| `0xE4DD0117` | `UAC_E_UAREADFAILED` | UA Read 失败（未知原因） | 查 Server 日志；检查节点权限 |
| `0xE4DD0125` | `UAC_E_NONVALIDTYPEINFO` | 节点类型信息不足 | 节点可能没有 Value 属性或 Server 返回的元数据不完整 |
| `0xE4DD0126` | `UAC_E_INVALIDATTRIBID` | 节点属性 ID 无效 | 检查 `stNodeAddInfo.eAttributeID` |

## 5. 使用注意 / 常见坑

- **StructuredDataType 不支持**：PDF §8.1 第一条「Behavior / Remedy」明确：PLCopen FB 读结构化类型会失败，请用 I/O Client。常见反例是想读 PLC 端用 `{attribute 'OPC.UA.DA' := '1'}` 暴露的 `STRUCT` 节点——必须改用 I/O Client + DTO 拆字段方式。
- **缓冲区放 PROGRAM / GVL / FB 实例成员**：异步读期间内存必须保活，栈上变量不行。
- **变长读用 `cbData_R` 截取**：`STRING` 内容、`ByteString` 等，业务侧按 `cbData_R` 取有效字节。
- **`stNodeAddInfo` 初始化**：`eAttributeID := eUAAI_Value` 是约定，`nIndexRangeCount := 0` 表示不切片；要读数组某段才填 IndexRange。
- **每 PLC 周期都要调本 FB**：上升沿启动后，内部 ADS 状态机靠周期调用推进；只调一次不会自己完成。
- **工程经验补充**：周期采集场景常用「TON 时钟 → R_TRIG → UA_Read」结构；上一次 Read 还没完（`Busy = TRUE`）时新触发会被 FB 忽略，业务侧应锁存 `Busy` 状态避免数据丢失。Read 失败时缓冲区数据是上一次成功的值（不会被覆盖），需要看 `Done` / `Error` 判断当前数据是否最新。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_Read.TcPOU`](../examples/P_Demo_UA_Read.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：从远端 OPC UA Server 周期采集生产数据。例如本地 PLC 每 5 秒从 MES 服务器读 `'MAIN.fTankLevel'`（水箱液位 `LREAL`）放进本地 HMI 显示，每秒读 `'GVL.iOrderQty'`（订单数量 `INT`）做工序触发。
- **价值**：把 OPC UA Read 服务的全部协议细节（SecureChannel framing、Encoding、StatusCode 处理、复用 NodeHdl 加速）封装为一次 FB 调用。PLC 工程师只需准备缓冲区、给 NodeHdl，业务代码与协议解耦。
- **替代方案对比**：① I/O Client 静态配置——适合编译期已知节点，运行期动态变量做不到；② 用 `Tc2_TcpIp` 自己实现 OPC UA Read 协议——理论可行但要写 BinaryEncoding 解码，无人这么做；③ 用 `Tc2_DataExchange` 走 ADS——仅 TwinCAT ↔ TwinCAT，连不到第三方 Server；④ **本 FB**——动态读 + 高吞吐（NodeHdl 缓存类型元数据）+ PLCopen Companion Spec 标准。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.14（UA_Read）、§5.2.2.20（ST_UANodeAdditionalInfo）、§5.2.2.1（E_UAAttributeID）、§5.2.2.16（ST_UAIndexRange）、§8.1（StructuredDataType 限制）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537643147.html
- **相关 FB**：`UA_NodeGetHandle`（前置取句柄）；`UA_ReadList`（批量读多个节点）；`UA_Write`（写）；`UA_HistoryUpdate`（写历史数据）；I/O Client（StructuredDataType 替代方案）
