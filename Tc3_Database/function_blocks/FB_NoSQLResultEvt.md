# FB_NoSQLResultEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5875270411.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NoSQLResultEvt.TcPOU`](../examples/P_Demo_FB_NoSQLResultEvt.TcPOU) |

---

## 1. 功能简述

NoSQL Expert Mode 下读取 Server 缓存的 NoSQL 查询结果的功能块（PDF §6.1.1.4.3）。配合 `FB_NoSQLQueryEvt.ExecuteDataReturn` 使用——查询结果先被 Server 缓存到本 FB 实例对应的内存区。然后通过 `ReadAsString`（JSON 字符串数组）或 `ReadAsStruct`（PLC 结构数组，可选验证）读出。`Release` 释放缓存。注意：本 FB 的内部声明在 PDF 中写为 `FUNCTION BLOCK FB_SQLResultEvt`（少了 NoSQL 前缀）—— PDF 印刷 typo，实际工程中的 FB 名是 `FB_NoSQLResultEvt`，从 InfoSys topic ID 与 `FB_NoSQLQueryEvt` 的 `pNoSQLResult: POINTER TO FB_NoSQLResultEvt` 引用都可确认。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID: T_AmsNetID := '';
    tTimeout: TIME := T#5S;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResult: Tc3_EventLogger.I_TcMessage;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |
| `nDataCount` | `UDINT` | 上次 `FB_NoSQLQueryEvt.ExecuteDataReturn` 后返回的可读总行数。 |

### Method: `ReadAsString`（读为 JSON 字符串数组）

```iecst
METHOD ReadAsString : BOOL
VAR_INPUT
    nStartIndex: UDINT := 0;
    nRecordCount: UDINT := 1;
    pData: POINTER TO BYTE;
    cbData: UDINT;
    nMaxDocumentSize : UDINT;
    bDataRelease: BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nStartIndex` | `UDINT` | `0` | 起始行 0 基索引。 |
| `nRecordCount` | `UDINT` | `1` | 要读的文档数。 |
| `pData` | `POINTER TO BYTE` | - | 接收数组地址（`ARRAY[0..N] OF STRING(M)`）。 |
| `cbData` | `UDINT` | - | 接收数组 SIZEOF。 |
| `nMaxDocumentSize` | `UDINT` | - | 单文档最大 STRING 字节数。 |
| `bDataRelease` | `BOOL` | `TRUE` | TRUE = 读完自动释放 Server 缓存；FALSE = 保留供分页继续读。 |

### Method: `ReadAsStruct`（读到 PLC 结构数组）

```iecst
METHOD ReadAsStruct: BOOL
VAR_INPUT
    nStartIndex: UDINT := 0;
    nRecordCount: UDINT := 1;
    pData: POINTER TO BYTE;
    cbData: UDINT;
    bValidate: BOOL := FALSE;
    pNoSQLValidation : POINTER TO FB_NoSQLValidationEvt;
    bDataRelease: BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nStartIndex` | `UDINT` | `0` | 起始行索引。 |
| `nRecordCount` | `UDINT` | `1` | 行数。 |
| `pData` | `POINTER TO BYTE` | - | 自定义 PLC 结构体数组地址。Server 按 JSON 字段名匹配结构体字段名做映射；不一致字段可用 `{attribute 'ElementName' := '...'}` 自定义。 |
| `cbData` | `UDINT` | - | 数组 SIZEOF。 |
| `bValidate` | `BOOL` | `FALSE` | TRUE = Server 比对 PLC 结构与返回数据 schema，结果通过 `pNoSQLValidation^` 暴露。 |
| `pNoSQLValidation` | `POINTER TO FB_NoSQLValidationEvt` | - | 验证结果接收 FB 地址；`bValidate := TRUE` 时必填。 |
| `bDataRelease` | `BOOL` | `TRUE` | 同上。 |

### Method: `Release`

```iecst
METHOD Release : BOOL
```

无入参——显式释放 Server 端缓存。

## 3. 行为说明

**两种读取风格**：
- `ReadAsString`：把每条文档原样作为 JSON 字符串读出，适合「不想做结构映射，直接给 HMI 显示原文」或「字段不确定要先看一眼」场景。
- `ReadAsStruct`：把 JSON 自动映射到 PLC 结构体；字段名匹配按结构字段名（或 `{attribute 'ElementName'}`）查找 JSON key。结构清晰能直接计算的场景首选。

**`ReadAsStruct` 的 schema 映射**：Server 通过 PLC IEC 类型查询能力获取结构定义；JSON 字段按名匹配。字段名不一致 → 那字段不填（默认值）；多余 JSON 字段被忽略（`bValidate := TRUE` 时可通过 ValidationEvt 拿到「未映射字段列表」）。

**`bValidate` 与 `FB_NoSQLValidationEvt`**：当 PLC 结构与 JSON 文档不完全匹配（字段名差异、缺字段、多字段），开 `bValidate := TRUE` 让 Server 把差异详情写到 `pNoSQLValidation^` 指向的 FB 实例的内部缓存。然后用 `fbValidation.GetIssues(...)`（取问题列表）/ `GetRemainingData(...)`（取未映射的原 JSON）。便于调试 schema mismatch。

**`bDataRelease` 与分页**：与 SQL 同理——分页读 FALSE，全读完 TRUE。漏 Release 会让 Server 累积内存。

**`nDataCount` 属性**：在调用 `FB_NoSQLQueryEvt.ExecuteDataReturn` 后被 Server 填——告诉调用方一共多少条文档。读前看此值决定分多少页。

**PDF 印刷 typo 说明**：PDF 6.1.1.4.3 节定义中写 `FUNCTION BLOCK FB_SQLResultEvt` —— 漏了「No」前缀。InfoSys 同保留。从 `FB_NoSQLQueryEvt.ExecuteDataReturn` 的入参 `pNoSQLResult: POINTER TO FB_NoSQLResultEvt` 可确认实际 FB 名是 `FB_NoSQLResultEvt`，调用代码必须用完整名。本仓元信息字段中的 Library 与 Source 也用正确名。

**Tc3_EventLogger 错误**：`bError` 时 `ipTcResult.RequestEventText` 取详细文本，常见 `'Cache empty'`、`'Index out of range'`、`'Schema mismatch'`、`'Buffer too small'`（cbData 小于实际所需）。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 表征实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| `bError`，事件含 `Cache empty` | 缓存已释放后再读 | 重发查询 |
| `bError`，事件含 `Index out of range` | nStartIndex + nRecordCount > nDataCount | 减小 |
| `bError`，事件含 `Buffer too small` | cbData < 实际所需 | 加大数组 |
| `bError`，事件含 `Schema mismatch` (ReadAsStruct, bValidate=FALSE) | 字段名 / 类型不匹配 | 开 bValidate=TRUE 看具体差异 |

完整 PDF §8.1.1 + NoSQL 错误码（PDF Appendix）。

## 5. 使用注意 / 常见坑

- **必须先 `FB_NoSQLQueryEvt.ExecuteDataReturn` 绑定缓存**：否则 Read 找不到缓存。
- **`pData^` 容量必须 ≥ `nRecordCount * SIZEOF(item)`**：否则报 buffer too small。
- **`ReadAsString` 的单文档大小用 `nMaxDocumentSize`**：超长 JSON 会被截断。
- **`ReadAsStruct` schema 映射对 `STRING` 长度敏感**：JSON 字段长度超 PLC `STRING(N)` 会被截断（视 bValidate 模式不同：FALSE 静默；TRUE 报 issue）。
- **分页读 `bDataRelease := FALSE`**：所有中间 Read 用 FALSE，最后一次或显式 Release。
- **`pNoSQLValidation^` 必须独立的 `FB_NoSQLValidationEvt` 实例**：不能用临时栈对象。
- **同一 Result 实例不能并发读**：单线程语义。
- **PDF FB 名 typo `FB_SQLResultEvt`**：代码实际用 `FB_NoSQLResultEvt`；IEC 编译器按 InfoSys 定义。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NoSQLResultEvt.TcPOU`](../examples/P_Demo_FB_NoSQLResultEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：能源管理 HMI 触发「查最近 1 小时所有电表读数」→ PLC 用 `FB_NoSQLQueryEvt.ExecuteDataReturn` 查 InfluxDB 拿到 720 条（5 秒间隔），缓存在本 FB 关联实例。HMI 分页展示——每页 100 条，PLC 分 8 次 `ReadAsStruct` 各取 100 行到 `ARRAY[0..99] OF ST_EnergyPoint`，HMI 边收边画。读完 `Release` 缓存。同时另一线索：开 `bValidate := TRUE` + `FB_NoSQLValidationEvt` 验证 InfluxDB 返回字段是否符合预期 schema（防 measurement 结构改了不知道）。
- **价值**：大结果集分页 + schema 验证一站式；JSON 字符串 / PLC 结构两种格式；EventLogger 错误诊断。
- **替代方案对比**：
  - **SQL 的 `FB_SQLResultEvt`**：仅适合 SQL；NoSQL 数据无法处理（JSON 嵌套、字段不固定）。
  - **PLC 端解析 JSON 字符串（用 Tc3_JsonXml）**：可行但 PLC CPU 开销大，500+ 条文档可能让周期超时。
  - **本 FB**：TC3 NoSQL Expert mode 结果集读取唯一选项。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5875270411.html
- **相关 FB / FC / DUT**：`FB_NoSQLQueryEvt`（必须先 ExecuteDataReturn）、`FB_NoSQLValidationEvt`（schema 验证）、`{attribute 'ElementName'}`（字段名映射）、`Tc3_JsonXml`（PLC 端备选 JSON 解析）
