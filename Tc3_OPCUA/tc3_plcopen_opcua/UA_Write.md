# UA_Write

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537644171.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_Write.TcPOU`](../examples/P_Demo_UA_Write.TcPOU) |

---

## 1. 功能简述

OPC UA 节点写功能块（PDF §5.2.3.16）。把 PLC 本地数据写到远端 OPC UA Server 的指定节点。`stNodeAddInfo` 可指定目标属性（默认 `Value`）和 IndexRange（数组节点）。每次 `Execute` 上升沿触发一次写。**注意**：和 `UA_Read` 一样，PLCopen 客户端**不支持** StructuredDataType 节点的写——需要用 I/O Client 替代（PDF §8.1 明示）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute        : BOOL;
    ConnectionHdl  : DWORD;
    NodeHdl        : DWORD;
    stNodeAddInfo  : ST_UANodeAdditionalInfo; 
    pVariable      : PVOID;
    cbData         : UDINT;     
    Timeout        : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次写 |
| `ConnectionHdl` | `DWORD` | — | 由 `UA_Connect` 返回的会话句柄 |
| `NodeHdl` | `DWORD` | — | 由 `UA_NodeGetHandle` 返回的节点句柄 |
| `stNodeAddInfo` | `ST_UANodeAdditionalInfo` | — | 附加信息：目标 UA 属性（默认 `eUAAI_Value`）、IndexRange |
| `pVariable` | `PVOID` | — | 数据源地址，用 `ADR()` 取地址 |
| `cbData` | `UDINT` | — | 要写的字节数 |
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
| `Error` | `BOOL` | 失败时变 `TRUE` |
| `ErrorID` | `DWORD` | 命令特定 ADS 错误码 |

### VAR_IN_OUT

无。

`ST_UANodeAdditionalInfo` 同 `UA_Read`，写时常用 `eAttributeID := eUAAI_Value` 即写 Value 属性。

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次写：FB 通过 ADS 让 TF6100 客户端模块向 Server 发 OPC UA Write 请求，把 `pVariable` 指向的 `cbData` 字节作为新值。过程中 `Busy := TRUE`；收到应答（或 `Timeout` 到期）后 `Busy` 落 `FALSE`，成功则 `Done := TRUE` 一个周期。

**`cbData` 必须精确**：对定长类型用 `SIZEOF(变量)`；对 `STRING` 用 `LEN(变量) + 1`（含 NUL）；对 `ByteString` 用实际字节数。多写或少写会导致 Server 端解码错误。

**写权限**：节点 `AccessLevel` 必须包含 `CurrentWrite` 位；TwinCAT OPC UA Server 端 PLC 程序变量默认带 `OPC.UA.DA` 属性时有读权限，要写还需 `'OPC.UA.DA' := '1'` 配置中允许 Write，或 PLC 端没有 `{attribute 'OPC.UA.DA.Access' := '1'}` 限制成只读。

**数据源缓冲生命周期**：和 Read 类似，`pVariable` 指向的内存必须在 `Busy = TRUE` 期间保活（不能是栈上变量）。

**典型用法**：HMI 上一个「设定值」滑块，业务程序检测到本地变量变化后触发一次 `UA_Write` 把新设定值推到远端 Server，远端 PLC 收到后调整执行机构。

**典型陷阱**：① `cbData` 错（多写 / 少写）→ Server 端报数据格式错；② 写不可写节点（`AccessLevel` 不含 `CurrentWrite`）→ `UAC_E_UAWRITEFAILED`（`0xE4DD0118`）或 `0x706` `DEVICE_INVALIDDATA`；③ 类型不匹配（节点是 `INT` 但传 `LREAL` 数据）→ `UAC_E_CONVERSION`（`0xE4DD0106`）；④ 写 StructuredDataType → 失败，用 I/O Client；⑤ `pVariable` 指向栈上变量 → 异步期间被覆盖造成数据错乱。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。常见取值：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 写入完成 |
| `0x705` | `DEVICE_INVALIDSIZE` | 参数 size 不正确 | 检查 `cbData` 是否匹配节点类型大小 |
| `0x706` | `DEVICE_INVALIDDATA` | 参数值无效 | 检查目标节点是否可写、值是否合法 |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout` |
| `0xE4DD0106` | `UAC_E_CONVERSION` | 数据类型不能转换 | 检查 PLC 类型是否与节点类型匹配 |
| `0xE4DD0112` | `UAC_E_INVALIDHDL` | 会话句柄无效 | 重新 `UA_Connect` |
| `0xE4DD0116` | `UAC_E_INVAL_NODE_HDL` | 节点句柄无效 | 重新 `UA_NodeGetHandle` |
| `0xE4DD0118` | `UAC_E_UAWRITEFAILED` | UA Write 失败（未知原因） | 看 Server 日志；检查节点 AccessLevel |
| `0xE4DD0126` | `UAC_E_INVALIDATTRIBID` | 节点属性 ID 无效 | 检查 `stNodeAddInfo.eAttributeID` |

## 5. 使用注意 / 常见坑

- **类型必须严格匹配**：写一个 `INT` 节点必须传 16-bit 整数 + `cbData = 2`；写 `LREAL` 节点必须传 64-bit float + `cbData = 8`。错配 → `UAC_E_CONVERSION`。
- **`STRING` 写法**：`pVariable := ADR(sValue); cbData := LEN(sValue) + 1;`（+1 for NUL）。注意 PLC `STRING(80)` 写到 OPC UA 时还原成 NUL 截断的可读字符串。
- **写不可写节点**：Server 端 `Server_AccessLevel` 标识；UaExpert 可以查。某些标准节点（如 `Server_NamespaceArray`）永远只读。
- **StructuredDataType 不支持**：要写复合结构必须用 I/O Client。常见反例是把 PLC 端 `STRUCT` 用 `'OPC.UA.DA'` 暴露后想用本 FB 写——必须按字段拆开逐个 `UA_Write`，或用 I/O Client 整体映射。
- **数据源保活**：`pVariable` 指向 PROGRAM / GVL / FB 实例成员，不要用栈上变量。
- **工程经验补充**：设定值类「写一次」场景常用「业务逻辑检测到本地变量变化（R_TRIG）→ 触发 Execute → 等 Done → 复位变化检测」的状态机；不要每周期无脑触发 `Execute`——会浪费 OPC UA 带宽。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_Write.TcPOU`](../examples/P_Demo_UA_Write.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：HMI 操作员调整生产配方参数：本地 PLC 接收 HMI 触摸屏的数值滑块输入，业务确认后通过 OPC UA 写到远端 MES Server 的「当前配方」节点（如 `'GVL.fSetpointFlow'`）。或者：本地工艺循环结束后把统计结果（产量、合格率）回写到 MES 数据节点。
- **价值**：把 OPC UA Write 服务的全套协议细节封装为一次 FB 调用，PLC 工程师只关心数据源 / 字节数 / 节点句柄。比自己实现 OPC UA 协议解码省数千行代码。
- **替代方案对比**：① I/O Client + Write Enable——适合静态映射，运行期动态写不灵活；② 在 Server 端开 RPC Method 让客户端通过 `UA_MethodCall` 推数据——能附带业务校验逻辑但开发复杂；③ 用 `Tc2_DataExchange`走 ADS——仅 TwinCAT ↔ TwinCAT；④ **本 FB**——动态写、PLCopen 标准、跨厂家 Server 通用。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.16（UA_Write）、§5.2.2.20（ST_UANodeAdditionalInfo）、§8.1（StructuredDataType 限制 + I/O Client Write Enable 提醒）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537644171.html
- **相关 FB**：`UA_NodeGetHandle`（前置取句柄）；`UA_Read`（读）；`UA_MethodCall`（有业务校验的写选项，调 Server 端方法）；`UA_HistoryUpdate`（写历史数据）
