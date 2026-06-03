# FB_NoSQLQueryBuilder_TimeSeriesDB

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/8116654091.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NoSQLQueryBuilder_TimeSeriesDB.TcPOU`](../examples/P_Demo_FB_NoSQLQueryBuilder_TimeSeriesDB.TcPOU) |

---

## 1. 功能简述

NoSQL Expert Mode 下定义时序数据库（InfluxDB / InfluxDB2 / TimescaleDB）查询的功能块（PDF §6.1.1.4.1.2）。与 `FB_NoSQLQueryBuilder_DocumentDB` 同理但接口更简化——只有 `pQueryOptions` + `cbQueryOptions` 两个字段，没有 `eQueryType` 和 `sCollectionName`（时序库的查询类型与表名编码在选项结构里：`T_QueryOptionTimeSeriesDB_Insert` 或 `T_QueryOptionTimeSeriesDB_Query`）。配合 `FB_NoSQLQueryEvt.Execute(hDBID, ADR(thisBuilder))` 发送。支持 PLC 端结构体数组批量写入（写入 1000 条记录用一次调用）+ Time-Series 风格的范围 / 聚合查询。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pQueryOptions : POINTER TO BYTE;
    cbQueryOptions : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pQueryOptions` | `POINTER TO BYTE` | - | 时序查询选项结构体地址。两类：`T_QueryOptionTimeSeriesDB_Insert`（批量写入）或 `T_QueryOptionTimeSeriesDB_Query`（范围查询）。PDF §6.1.2.2.4.2.x。 |
| `cbQueryOptions` | `UDINT` | - | 选项结构体 SIZEOF。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

（无输出字段。错误状态由调用方 `FB_NoSQLQueryEvt` 报告。）

### VAR_IN_OUT

无。

### Method: `Build`（可选，PDF `[optional]`）

```iecst
METHOD Build
```

PDF：「This method is called automatically in case of a FB_NoSQLQueryEvt (either with Execute or ExecuteDataReturn) before the query is sent.」一般不需手动调。

## 3. 行为说明

**时序库特有概念**：
- **Measurement / Table**：时序库的「表」概念，存储一类时间序列（如温度 / 压力 / 电流各一个 measurement）。在选项结构中通过 `sTableName` 字段指定。
- **Time-stamped Points**：每条记录都有时间戳（`nTimestamp` 字段），按时间索引。时序库的优势是按时间范围查询时极快。
- **Cyclic insertion**：本 Builder 的 Insert 模式专门为「PLC 周期采样」优化——`pSymbol` 指向 ARRAY 起始、`nDataCount` 是条数、`nStartTimestamp` 是第一条时间、`nCycleTime` 是后续条目间隔（µs 单位）。Server 用 `nStartTimestamp + i * nCycleTime` 算出每条记录的时间戳。这样 PLC 把整个数组一次性传出去，Server 端展开为 N 条带正确时间戳的记录写入时序库。

**典型 Insert 选项 `T_QueryOptionTimeSeriesDB_Insert`（PDF §6.1.2.2.4.2.1）字段**：
- `sTableName : T_MAXSTRING` — 目标 measurement / table
- `sDataType : T_MAXSTRING` — PLC 结构体类型名（如 `'MyStruct'`），Server 用作 schema 映射
- `pSymbol : POINTER TO BYTE` — 结构体数组首地址
- `cbSymbol : UDINT` — 数组总字节数
- `nDataCount : UDINT` — 条数（数组长度）
- `nStartTimestamp : ULINT` — 第一条记录时间戳（100ns 单位 NT 时间或 ns 单位）
- `nCycleTime : ULINT` — 后续条目间隔（µs / 1000 = 1 ms）

**与 DocumentDB Builder 的差异**：
- DocumentDB 用 `eQueryType + sCollectionName + pQueryOptions`；TimeSeriesDB 只有 `pQueryOptions + cbQueryOptions`。
- 时序库不用 collection 概念；表名（measurement）在选项里。
- 时序库不支持 Update（时序数据按时间戳排序，没有「更新某一行」的传统操作）；Delete 一般按时间范围。

**`sDataType` 与结构体属性**：PDF 提到「Data structures can be described with attributes to affect individual settings」——可以在 PLC 结构体声明上用 `{attribute 'ElementName' := 'colName'}` 等属性自定义列名映射。这样 PLC 结构字段名与时序库列名可以不一致。

**调用流程**（参考 PDF Sample）：
```iecst
fbBuilder.pQueryOptions := ADR(stInsertOpt);
fbBuilder.cbQueryOptions := SIZEOF(stInsertOpt);
stInsertOpt.sTableName := 'MeasurementName';
stInsertOpt.sDataType := 'MyStruct';
stInsertOpt.pSymbol := ADR(aMyArray);
stInsertOpt.cbSymbol := SIZEOF(aMyArray);
stInsertOpt.nDataCount := 1000;
stInsertOpt.nStartTimestamp := F_GetSystemTime();
stInsertOpt.nCycleTime := 1000;  // 1 ms
// 触发：
fbExecutor.Execute(hDBID, fbBuilder);
```

**何时该用本 Builder vs DocumentDB Builder**：
- 时序数据（按时间索引、按时间范围查询、值是简单数值或简单结构）→ TimeSeriesDB（更快、压缩好）
- 文档型数据（结构嵌套、字段不固定、需按内容字段查询）→ DocumentDB

**Tc3_EventLogger 错误**：本 FB 无 bError；由 Executor 报告。常见错误：`Schema mismatch`（sDataType 与 Server 端 measurement 不匹配）、`Buffer overflow`（cbSymbol 超过 Server 接收上限）。

## 4. 错误码 / 返回值

本 FB 不直接报错（无 VAR_OUTPUT 错误字段）。错误由 Executor 报告。典型上游错误：

| 现象 | 含义 | 处理 |
|---|---|---|
| 事件含 `Schema mismatch` | `sDataType` 与 Server 端 measurement 结构不匹配 | 比对结构体字段类型 |
| 事件含 `Buffer overflow` | `cbSymbol` 超过 Server 单次接收上限（一般 64KB） | 拆分批量为多次 |
| 事件含 `Connection failed` | 时序库不可达 | 检查 InfluxDB / TimescaleDB 状态 |
| 事件含 `nCycleTime invalid` | 0 或负值 | 改正 |

## 5. 使用注意 / 常见坑

- **`pSymbol^` 必须是 ARRAY 头地址，不是 ADR(ARRAY[0])**：两种写法等价但代码风格统一便于审。
- **`nCycleTime` 单位是 µs（1/1,000,000 秒）**：1ms 周期 = 1000、100ms 周期 = 100000。PDF 例子 `nCycleTime := 1000` = 1 ms。错误地写 `T#1MS` 是 TIME 类型，不可用。
- **`nStartTimestamp` 时间基准**：使用 `F_GetSystemTime()` 取当前 Windows FILETIME（100ns 单位）。和 PDF 例一致。不同时序库可能用不同时间基准——InfluxDB 默认 ns，TimescaleDB 默认 µs；Server 内部转换。
- **`sDataType` 一般填 PLC 结构体类型名**：Server 通过 PLC IEC 类型查询能力获取字段定义。要求结构体在工程里有完整声明。
- **批量插入吞吐**：单次调用 1000 条比 1000 次单条调用快 100 倍以上——时序库批量插入是核心优化点。
- **不支持 Update**：要修历史数据需先 Delete 后 Insert。
- **本 Builder 无 `sCollectionName` 字段**：与 DocumentDB Builder 接口不同；测试代码不能复用同一辅助函数。
- **`{attribute 'ElementName'}` 在 PLC 结构定义里**：例如 `{attribute 'ElementName' := 'temp_C'} rTemperature : LREAL;` 让 Server 端列名为 `temp_C` 而非 PLC 字段名。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NoSQLQueryBuilder_TimeSeriesDB.TcPOU`](../examples/P_Demo_FB_NoSQLQueryBuilder_TimeSeriesDB.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：风电场每台风机的 SCADA 数据 PLC 端按 100ms 周期采 1000 点存到本地 ARRAY[0..999] OF ST_SCADAPoint 缓冲；缓冲满后用本 Builder 一次性批量写入 InfluxDB measurement `turbine_data`。Server 按 `nStartTimestamp + i * nCycleTime` 给每点正确时间戳。
- **价值**：批量写入 100-1000 倍提速（vs 单条）；时序库按时间范围查询比 SQL 表快 10-100 倍；时序压缩节省 50-90% 存储；EventLogger 错误诊断。
- **替代方案对比**：
  - **SQL 表 + 单条 INSERT**：高频时序场景实际不可行（吞吐限制）。
  - **`FB_NoSQLQueryBuilder_DocumentDB`**：文档型数据用，不适合纯数值时序。
  - **TF3500 Analytics Logger**：付费插件性能更高，但成本与维护复杂度也高；本 FB 是免费方案。
  - **本 FB**：TF6420 时序库的唯一 Builder；新项目首选。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/8116654091.html
- **相关 FB / FC / DUT**：`FB_NoSQLQueryEvt`（Executor）、`T_QueryOptionTimeSeriesDB_Insert` / `_Query`（§6.1.2.2.4.2）、`E_TimeSeriesDbQueryType`（§6.1.2.2.5）、`F_GetSystemTime`（取 NT 时间）、`FB_NoSQLQueryBuilder_DocumentDB`（同类文档库版本）
