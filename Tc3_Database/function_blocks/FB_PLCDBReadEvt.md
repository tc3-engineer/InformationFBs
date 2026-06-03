# FB_PLCDBReadEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674377099.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBReadEvt.TcPOU`](../examples/P_Demo_FB_PLCDBReadEvt.TcPOU) |

---

## 1. 功能简述

从数据库表中读取记录的功能块（PDF §6.1.1.2.4，PLC Expert mode）。两个方法：`Read` 按 Beckhoff 标准表结构（4 列：ID / Timestamp / Name / Value，AutoLog 与 `FB_DBWriteEvt` 默认使用）读取，按 Name 过滤；`ReadStruct` 按任意自定义表结构读，列名通过 `pColumnNames` 数组传入。两者都支持排序（`eOrderBy` 或 `sOrderByColumn` + `eOrderType`）、分页（`nStartIndex` + `nRecordCount`）。

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
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。大结果集 / 远端 DB 需加大。 |

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
| `bError` | `BOOL` | 出错置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `nRecords` | `UDINT` | 输出根据 `sDBSymbolName` 过滤后可获得的最大记录数（实际行数，不是返回行数）。读前先看这个能知道总共有多少匹配行。 |
| `eTraceLevel` | `TcEventSeverity` | 事件分级。 |

### Method: `Read`（按 Beckhoff 标准表结构读）

```iecst
METHOD Read : BOOL
VAR_INPUT
    hDBID: UDINT;
    sTableName: T_MaxString;
    sDBSymbolName: T_MaxString;
    eOrderBy: E_OrderColumn := E_OrderColumn.eColumnID;
    eOrderType: E_OrderType := E_OrderType.eOrder_ASC;
    nStartIndex: UDINT;
    nRecordCount: UDINT;
    pData: POINTER TO ST_StandardRecord;
    cbData: UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `sTableName` | `T_MaxString` | - | 要读的表名（必须是 Beckhoff 标准 4 列结构）。 |
| `sDBSymbolName` | `T_MaxString` | - | 按 Name 列过滤的字符串；空 = 不过滤（取全部）。 |
| `eOrderBy` | `E_OrderColumn` | `eColumnID` | 排序列：`eColumnID` / `eColumn_Timestamp` / `eColumn_Name` / `eColumn_Value`。 |
| `eOrderType` | `E_OrderType` | `eOrder_ASC` | 排序方向：`eOrder_ASC` 升 / `eOrder_DESC` 降。 |
| `nStartIndex` | `UDINT` | - | 起始行索引（0 基）。 |
| `nRecordCount` | `UDINT` | - | 要读的行数；不超过 `pData^` 数组容量。 |
| `pData` | `POINTER TO ST_StandardRecord` | - | 接收行的数组地址（每元素 1 个标准记录）。 |
| `cbData` | `UDINT` | - | 该数组 `SIZEOF`。 |

### Method: `ReadStruct`（按自定义表结构读）

```iecst
METHOD ReadStruct : BOOL
VAR_INPUT
    hDBID: UDINT;
    sTableName: T_MaxString;
    pColumnNames: POINTER TO ARRAY [0..MAX_DBCOLUMNS] OF STRING(50);
    cbColumnNames: UDINT;
    sOrderByColumn: STRING(50);
    eOrderType: E_OrderType := E_OrderType.eOrder_ASC;
    nStartIndex: UDINT;
    nRecordCount: UDINT;
    pData: POINTER TO BYTE;
    cbData: UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hDBID` | `UDINT` | - | 数据库 ID。 |
| `sTableName` | `T_MaxString` | - | 表名。 |
| `pColumnNames` | `POINTER TO ARRAY [0..MAX_DBCOLUMNS] OF STRING(50)` | - | 列名数组地址；按列顺序填，Server 按此顺序读列。 |
| `cbColumnNames` | `UDINT` | - | 列名数组 SIZEOF。 |
| `sOrderByColumn` | `STRING(50)` | - | 排序列名（自由 SQL）。 |
| `eOrderType` | `E_OrderType` | `eOrder_ASC` | 排序方向。 |
| `nStartIndex` | `UDINT` | - | 起始行 0 基索引。 |
| `nRecordCount` | `UDINT` | - | 读取行数。 |
| `pData` | `POINTER TO BYTE` | - | 自定义结构体数组地址；列字段顺序须与 `pColumnNames^` 一致。 |
| `cbData` | `UDINT` | - | 数组 SIZEOF。 |

### 关联结构

`ST_StandardRecord`（PDF §6.1.2.4.12，4 列固定结构）：
```iecst
TYPE ST_StandardRecord :
STRUCT
    nID         : LINT;
    dtTimestamp : DATE_AND_TIME;
    sName       : STRING(80);
    nValue      : LREAL;
END_STRUCT
END_TYPE
```

## 3. 行为说明

**标准表 vs 自定义表**：Beckhoff 提供「标准 4 列结构」(ID / Timestamp / Name / Value) 作为 Name/Value 历史日志的通用模式，`FB_PLCDBWriteEvt.Write` 与 AutoLog 默认写入该结构。本 FB 的 `Read` 方法专门为此格式优化——配上 `sDBSymbolName` 按 Name 过滤就能取到指定信号的历史值；`ReadStruct` 方法用于任何用户自定义表（含 `FB_PLCDBWriteEvt.WriteStruct` 写出的结构表）。两者读出的 `pData^` 结构不同：`Read` 写入 `ST_StandardRecord` 数组；`ReadStruct` 写入用户结构数组（字段顺序按 `pColumnNames^` 顺序排）。

**`nRecords` 属性的作用**：调 `Read` 后 Server 会把「按 `sDBSymbolName` 过滤后的总匹配行数」写到 `nRecords` 属性。这是分页关键——若 `nRecords = 1000` 而本次只取了 `nRecordCount = 50`，调用方就知道还有 950 行要继续翻页。`ReadStruct` 不更新 `nRecords`（Beckhoff 文档未承诺）。

**排序与分页**：
- `Read`：`eOrderBy` 选枚举列；`nStartIndex` 是 0 基；`eOrderType.eOrder_DESC` 配 `nStartIndex := 0` 取最近 N 条。
- `ReadStruct`：`sOrderByColumn` 是字符串，直接拼到 ORDER BY；输入信任域同 `FB_PLCDBCmdEvt`，不要拼用户输入。

**读最新 N 条的标准用法**：`Read(eOrderBy := E_OrderColumn.eColumnID, eOrderType := E_OrderType.eOrder_DESC, nStartIndex := 0, nRecordCount := 10, ...)`——按 ID 降序取前 10 条 = 最近 10 条（前提：ID 是 IDENTITY 主键，新插入永远 ID 最大）。

**`pData^` 数组大小**：必须 ≥ `nRecordCount`（结构体大小 × 数量），否则 Server 越界写入会破坏其他变量。Server 通过 `cbData` 验证空间足够，不够会返回错误。

**调用语义**：`bExecute` 风格不存在——本 FB 用「调用方法即触发」语义，每周期调直到方法返回 TRUE。和 `FB_DBRead` 单输入 `bExecute` 边沿触发不同，调用要靠程序状态机控制（避免连续触发）。

**Tc3_EventLogger 错误**：失败时 `bError = TRUE`，`ipTcResult.RequestEventText` 取详细文本（如 `'Table not found'` / `'Column missing'` / `'Connection lost'`）。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）；`bError` + `ipTcResult` 表征实际成败。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| `bError`，事件含 `Table not found` | `sTableName` 拼写或不存在 | 检查 schema |
| `bError`，事件含 `Column missing` | `pColumnNames^[i]` 拼错或不在表内 | 用 SQL 客户端查表结构 |
| `bError`，事件含 `data too large` | `cbData` 小于实际所需 | 加大数组容量 |
| `nRecords = 0`（无 bError） | 过滤条件无匹配 | 改 `sDBSymbolName` 或检查表是否有数据 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **`Read` 只能读 Beckhoff 标准 4 列表**：自定义表结构必须用 `ReadStruct`；混用会返回错误（列对不上）。
- **`pData^` 数组要预先开够**：`ARRAY[0..99] OF ST_StandardRecord` 可读最多 100 行；调小 `nRecordCount` 不会让 Server 越界但能让 Server 提前返回。
- **`sDBSymbolName` 大小写敏感**：大多数 DB 默认列值大小写敏感。`'MyValue'` 与 `'myvalue'` 是两个 Name。
- **排序枚举可能跨库不一致**：MS SQL 的 NULL 排序在 `ASC` 时通常排前；MySQL 排后；SQLite 排前。如果数据有 NULL 字段需先用 SQL 客户端验证排序行为。（工程经验补充）
- **`ReadStruct` 的 `pColumnNames^` 与结构体字段顺序必须一一对应**：Server 把列数据按 `pColumnNames^` 顺序填到结构体起始偏移；如果结构体字段顺序不同 → 数据错位。
- **大结果集慎用 `Read(nRecordCount := nRecords)`**：一次取 10 万行会让 ADS 缓冲爆掉。生产建议分页 1000 行/次。
- **`nRecords` 属性是 `Read` 调用后才更新**：第一次没调 `Read` 前是默认 0，不要先看它再决定调不调。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBReadEvt.TcPOU`](../examples/P_Demo_FB_PLCDBReadEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上的「最近 10 次温度采样曲线」按钮。点击后 PLC 从 MS SQL 的 `tbl_TempHistory` 标准表里按 `sDBSymbolName := 'Reactor1_Temp'` 过滤、按 ID 降序取 10 行回填到 `ARRAY[0..9] OF ST_StandardRecord`，HMI 直接画曲线。
- **价值**：HMI 历史曲线无需第三方组件——PLC 直读 DB 后送数据；分页控制内存；`nRecords` 属性让分页页码可见。
- **替代方案对比**：
  - **`FB_DBRecordArraySelect`（Tc2_Database）**：等价但需要写完整 SELECT SQL；本 FB 更结构化。
  - **HMI 直连 DB（OPC UA + 第三方 SQL 客户端）**：依赖 HMI 端组件，许可成本；本 FB PLC 端搞定。
  - **本 FB**：TC3 现代版（带 EventLogger），首选；obsolete 版 `FB_PLCDBRead`（无 Evt）老项目兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674377099.html
- **相关 FB / FC / DUT**：`FB_PLCDBWriteEvt`（写入侧）、`ST_StandardRecord`（§6.1.2.4.12）、`E_OrderColumn` / `E_OrderType`（§6.1.2.4.4 / §6.1.2.4.5）、`MAX_DBCOLUMNS`、obsolete `FB_PLCDBRead`
