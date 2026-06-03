# FB_PLCDBCmdEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674380939.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBCmdEvt.TcPOU`](../examples/P_Demo_FB_PLCDBCmdEvt.TcPOU) |

---

## 1. 功能简述

执行用户自定义 SQL 命令的功能块（PDF §6.1.1.2.6，PLC Expert mode）。两个方法：`Execute` 发送任意 SQL 命令到数据库（INSERT / UPDATE / DELETE / CREATE / 调用存储过程等），**不返回数据集**；`ExecuteDataReturn` 发送命令（一般 SELECT）并把返回行写到调用方提供的结构体数组。两个方法都支持 SQL 命令中的占位符——用 `{paraName}` 形式嵌入，Server 调用前按 `ST_ExpParameter` 数组里的参数描述与 `pData^` 里的 PLC 变量值替换。这是参数化 SQL 的标准做法，避免手工拼字符串带来的 SQL 注入和类型转换错误。

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
| `tTimeout` | `TIME` | `T#5S` | ADS 超时；复杂 SQL 加大。 |

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
| `bBusy` | `BOOL` | 任一方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |

### Method: `Execute`（不返回数据）

```iecst
METHOD Execute : BOOL
VAR_INPUT
    hDBID: UDINT;
    pExpression: POINTER TO BYTE;
    cbExpression: UDINT;
    pData: POINTER TO BYTE;
    cbData: UDINT;
    pParameter: POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ExpParameter;
    cbParameter: UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hDBID` | `UDINT` | 数据库 ID。 |
| `pExpression` | `POINTER TO BYTE` | SQL 命令字符串地址（如 `ADR(sCmd)`）。 |
| `cbExpression` | `UDINT` | 字符串字节大小（`SIZEOF`）。 |
| `pData` | `POINTER TO BYTE` | 含参数实际值的结构体地址。 |
| `cbData` | `UDINT` | 数据结构 `SIZEOF`。 |
| `pParameter` | `POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ExpParameter` | 参数描述数组地址（每元素描述一个占位符的名 / 类型 / 大小）。 |
| `cbParameter` | `UDINT` | 参数描述数组 `SIZEOF`。 |

### Method: `ExecuteDataReturn`（返回数据集）

```iecst
METHOD ExecuteDataReturn : BOOL
VAR_INPUT
    hDBID: UDINT;
    pExpression: POINTER TO BYTE;
    cbExpression: UDINT;
    pData: POINTER TO BYTE;
    cbData: UDINT;
    pParameter: POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ExpParameter;
    cbParameter: UDINT;
    nStartIndex : UDINT ;
    nRecordCount : UDINT ;
    pReturnData: POINTER TO BYTE;
    cbReturnData : UDINT ;
    pRecords: POINTER TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hDBID` | `UDINT` | 数据库 ID。 |
| `pExpression` | `POINTER TO BYTE` | SQL 命令地址（一般 SELECT）。 |
| `cbExpression` | `UDINT` | SQL 字节大小。 |
| `pData` | `POINTER TO BYTE` | 含参数实际值的结构体地址（占位符替换源）。 |
| `cbData` | `UDINT` | 数据结构 SIZEOF。 |
| `pParameter` | `POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ExpParameter` | 参数描述数组地址。 |
| `cbParameter` | `UDINT` | 参数描述数组 SIZEOF。 |
| `nStartIndex` | `UDINT` | 起始行 0 基索引。 |
| `nRecordCount` | `UDINT` | 要读的行数。 |
| `pReturnData` | `POINTER TO BYTE` | 接收返回行的自定义结构体数组地址。 |
| `cbReturnData` | `UDINT` | 接收数组 SIZEOF。 |
| `pRecords` | `POINTER TO UDINT` | Server 写回「实际读出的行数」。 |

### 关联结构 `ST_ExpParameter`（PDF §6.1.2.4.11）

| 字段 | 类型 | 说明 |
|---|---|---|
| `sParaName` | `STRING(50)` | 占位符名（不含 `{` `}`，例 `'colInteger'` 对应 SQL 里 `{colInteger}`）。 |
| `eParaType` | `E_ExpParameterType` | 参数类型枚举（`Int32` / `Int64` / `Float32` / `Double64` / `Boolean` / `Byte_` / `STRING_` / `ByteArray` / `DateTime` 等，§6.1.2.4.3）。 |
| `nParaSize` | `UDINT` | 参数值字节大小。 |

## 3. 行为说明

**占位符 SQL 模式**：与拼字符串 SQL 不同，本 FB 用 `{name}` 形式在 SQL 中标占位，Server 拿到命令后按 `pParameter^[i].sParaName` 在命令里找 `{<name>}` 并用 `pData^` 偏移 `i` 处的值（按 `eParaType` + `nParaSize` 解释）替换。例如：
```sql
INSERT INTO MyTable (colInt, colName) VALUES ({colInt}, {colName})
```
配合 `pParameter^[0] = (sParaName='colInt', eParaType=Int32, nParaSize=4)`、`pParameter^[1] = (sParaName='colName', eParaType=STRING_, nParaSize=50)`，`pData^` 是结构体 `STRUCT colInt:DINT; colName:STRING(50); END_STRUCT`——Server 读取这个结构按声明顺序映射到占位符。

**为什么用占位符**：(1) 防 SQL 注入——值不是字符串拼接而是绑定参数；(2) 不用 PLC 端做 DT/REAL/INT 转字符串再拼字符串再让 DB 转回去；(3) 同一条 SQL 反复执行只改 `pData^` 内容即可，Server 可重用预编译计划。

**`Execute` vs `ExecuteDataReturn`**：`Execute` 用于「执行但不返回结果集」——INSERT / UPDATE / DELETE / DDL 等。`ExecuteDataReturn` 用于 SELECT 类查询——除了输入参数描述还要预先准备「接收结果集的结构体数组」与「每次读多少行」。

**连接是每次自动开关**：PDF 明确说「The database connection is opened with each call and then closed again.」——和 Tc2_Database 的 `FB_DBConnectionOpen` 模式不同，本 FB 每次方法调用都新连接，不持续占用 DB 句柄。高吞吐场景考虑配合 `FB_SQLDatabaseEvt.Connect` 持久连接模式。

**`pParameter^` 数组大小**：上限 `MAX_DBCOLUMNS = 255`；实际通常 < 20。数组顺序必须与 `pData^` 结构字段顺序一致。

**`ExecuteDataReturn` 返回行数**：调 Server 后 `pRecords^` 写入「实际读到的行数」（≤ `nRecordCount`）。调用方据此遍历 `pReturnData^[0..pRecords^-1]`。

**Tc3_EventLogger 错误**：失败时 `ipTcResult.RequestEventText` 取详细文本，常见 `'Syntax error'` / `'Cannot convert'` / `'Connection lost'` / `'Type mismatch'`。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）；`bError` + `ipTcResult` 报实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| `bError`，事件含 `Syntax error` | SQL 语法错（占位符没写大括号等） | 在 SQL 客户端先跑通 SQL |
| `bError`，事件含 `Cannot convert` | `eParaType` 与 DB 列类型不匹配 | 比对 PLC 类型 ↔ DB 类型映射 |
| `bError`，事件含 `Placeholder not found` | SQL 里有 `{x}` 但 `pParameter^` 找不到 `x` | 检查 sParaName 拼写 |
| `bError`，事件含 `Buffer overflow` | `cbReturnData` 不够装 `nRecordCount` 行 | 加大接收数组 |
| `pRecords^ < nRecordCount`（无 bError） | DB 实际只有这么多匹配行 | 正常 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **`pExpression` 必须是 STRING 而非 STRING 数组**：传入要用 `ADR(sCmd)`，`sCmd : STRING(10000)`。最大 STRING 长度限制了 SQL 命令长度。
- **占位符 `{name}` 不可与 SQL 的字面 `{` 冲突**：MySQL / MS SQL 通常不在 SQL 里用 `{`，但 PostgreSQL 的 JSON 操作符可能用。极少数情况要转义。
- **`pParameter^[i].sParaName` 必须不带 `{}` 大括号**：传 `'colName'` 而不是 `'{colName}'`。
- **`pData^` 结构必须与参数描述顺序对应**：Server 按 `pParameter^[i].nParaSize` 累积偏移读 `pData^`。多出 padding 或字段顺序乱 → 读到错值。建议结构体字段紧贴参数顺序，类型大小精确匹配。（工程经验补充）
- **`ExecuteDataReturn` 的 `pReturnData^` 结构与 SELECT 返回列的对应**：按列序排列字段，与 `FB_PLCDBReadEvt.ReadStruct` 同理。
- **连接每次开关 = 性能瓶颈**：每次 Execute 都有 100-500ms TCP/OLE DB 建连延迟。高吞吐场景用 `FB_SQLDatabaseEvt`。
- **不能用 SELECT 配 Execute**：Execute 不取结果；用 ExecuteDataReturn 即可。
- **Server 端预编译**：同一条 SQL 反复 Execute 时 Server 可能复用预编译——但参数大小变化时（如 STRING 实际长度不同）可能重新编译。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBCmdEvt.TcPOU`](../examples/P_Demo_FB_PLCDBCmdEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MES 客户端要从 PLC 端 INSERT 一条工艺记录到 `tbl_BatchResult(batchId, productType, startTime, endTime, totalGood, totalBad)`——6 字段，3 数值 / 2 时间 / 1 字符串。手工拼 SQL 字符串既要处理引号转义又要处理时间格式，还要防注入。用 `Execute` 配占位符：SQL 文本固定一次写好，每次只把当前批数据塞进 `pData^` 结构再调一次方法。
- **价值**：参数化避免 SQL 注入；类型由 Server 转换不用 PLC 端拼 DateTime 字符串；同一 SQL 模板可执行多次只改数据；EventLogger 错误诊断让生产环境调试快。
- **替代方案对比**：
  - **拼字符串 SQL + `FB_DBRecordInsert_EX`（Tc2 风格）**：直观但易出错且有注入风险。
  - **`FB_PLCDBWriteEvt.WriteStruct`**：用列名数组写自定义表更结构化但不支持 UPDATE/DELETE/调用存储过程。
  - **`FB_SQLCommandEvt`（SQL Expert mode）**：配合 `FB_SQLDatabaseEvt` 长连接，更适合高吞吐主动写。
  - **本 FB**：PLC Expert mode 的自由 SQL 通用入口；占位符 + 自动连接管理；事件驱动型写入首选；obsolete `FB_PLCDBCmd` 仅老项目兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674380939.html
- **相关 FB / FC / DUT**：`ST_ExpParameter`（§6.1.2.4.11）、`E_ExpParameterType`（§6.1.2.4.3）、`MAX_DBCOLUMNS`、`FB_SQLCommandEvt`（带 SQL Expert 长连接的等价 FB）、obsolete `FB_PLCDBCmd`
