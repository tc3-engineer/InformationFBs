# FB_DBTableCreate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108022795.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBTableCreate.TcPOU`](../examples/P_Demo_FB_DBTableCreate.TcPOU) |

---

## 1. 功能简述

FB_DBTableCreate 在已注册的数据库（按 `hDBID` 索引）里**新建一张表**，列结构由调用方提供的 `ARRAY OF ST_DBColumnCfg` 描述。每列由列名、列属性、列类型（`E_DbColumnTypes`：BigInt/Integer/Float/DateTime/NVarChar 等）三要素组成。配合 `FB_DBCreate` 完成「建库 → 建表」的初始化流程。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetID;
    hDBID           : UDINT;
    sTableName      : T_MaxString;
    cbTableCfg      : UDINT;
    pTableCfg       : POINTER TO ARRAY[0..MAX_DB_TABLE_COLUMNS] OF ST_DBColumnCfg;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID（从 `FB_DBConnectionAdd` 或 `FB_GetDBXMLConfig` 取）。 |
| `sTableName` | `T_MaxString` | - | 新建表的表名（SQL 标识符）。 |
| `cbTableCfg` | `UDINT` | - | 列描述数组的字节大小（`SIZEOF(arr)`）。 |
| `pTableCfg` | `POINTER TO ARRAY[0..MAX_DB_TABLE_COLUMNS] OF ST_DBColumnCfg` | - | 列描述数组地址（`ADR(arr)`）。`MAX_DB_TABLE_COLUMNS = 255`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次建表。 |
| `tTimeout` | `TIME` | - | ADS 超时，`T#15S` 通常够。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
    sSQLState   : ST_DBSQLError;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示建表失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部错误码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码（数据库拒绝建表时填充，如表名冲突）。 |

### VAR_IN_OUT

无。

### 关联结构 `ST_DBColumnCfg`（PDF §7.3.1）

```iecst
TYPE ST_DBColumnCfg :
STRUCT
    sColumnName     : STRING(59);
    sColumnProperty : STRING(59);
    eColumnType     : E_DbColumnTypes;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `sColumnName` | `STRING(59)` | 列名。SQL 标识符限制（不能用关键字、不能含空格除非加引号）。 |
| `sColumnProperty` | `STRING(59)` | 列属性字串：`'PRIMARY KEY'` / `'NOT NULL'` / `'IDENTITY(1,1)'` / `'DEFAULT 0'` 等 SQL 列约束语法。可为空。 |
| `eColumnType` | `E_DbColumnTypes` | 列数据类型枚举（PDF §7.3.6）：`eDBColumn_BigInt`=0 / `_Integer`=1 / `_SmallInt`=2 / `_TinyInt`=3 / `_Bit`=4 / `_Money`=5 / `_Float`=6 / `_Real`=7 / `_DateTime`=8 / `_NText`=9 / `_NChar`=10 / `_Image`=11 / `_NVarChar`=12 / `_Binary`=13 / `_VarBinary`=14。 |

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 用调用方提供的列描述拼成 `CREATE TABLE <name> (<col1> <type1> <prop1>, <col2> <type2> <prop2>, …)` SQL 命令并执行。

**`pTableCfg` 数组准备**：调用方按列序填充：
```iecst
arr[0].sColumnName     := 'ID';
arr[0].sColumnProperty := 'IDENTITY(1,1) PRIMARY KEY';
arr[0].eColumnType     := eDBColumn_BigInt;

arr[1].sColumnName     := 'Timestamp';
arr[1].sColumnProperty := 'NOT NULL';
arr[1].eColumnType     := eDBColumn_DateTime;

arr[2].sColumnName     := 'Name';
arr[2].sColumnProperty := '';
arr[2].eColumnType     := eDBColumn_NVarChar;

arr[3].sColumnName     := 'Value';
arr[3].sColumnProperty := '';
arr[3].eColumnType     := eDBColumn_Float;
```
未填的位置由 `eColumnType` 是否为有效枚举判断（一般用前 N 项）。

**`cbTableCfg = SIZEOF(arr)` 不是已用大小**：传整个数组的字节大小，Server 内部按 `eColumnType` 非零作为有效列。

**典型表结构（Server 推荐）**：
- `ID` BigInt IDENTITY PRIMARY KEY（自增主键）
- `Timestamp` DateTime（数据点时间戳）
- `Name` NVarChar（变量名 / 标识）
- `Value` Float（数值）

这种 4 列结构是 `FB_DBWrite` 的最简模式。

**关于 `eColumnType` 长度**：`NVarChar` / `NChar` / `Binary` / `VarBinary` 的长度由 Server 内部按 DB 类型选默认值（SQL Compact 通常 80 字符、MS SQL 通常 max）。如需精确控制，要走 `FB_DBStoredProcedures` 或事先 DBA 建表。

**`SQLState` 用于排错**：建表失败时 `bError = TRUE` + `nErrID` 给宏观错误（ADS / Server 层），`sSQLState.sSQLState`（5 字符）给 SQL 标准错误码，`nSQLErrorCode` 给 DB 特有码。例如表名冲突 SQL Server 返回 `'42S01'` + nSQLErrorCode = 2714。

## 4. 错误码 / 返回值

| 错误号 | sSQLState 典型值 | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42S01` | 表已存在 | 用 `IF EXISTS DROP` 先删除（要用 `FB_DBStoredProcedures`） |
| `0x0` | `42000` | 语法错误（列名 / 列类型不对） | 检查 `sColumnName` 是否冲突关键字、`eColumnType` 是否有效 |
| `0x0` | `42501` | 权限不足 | DB 用户需 `CREATE TABLE` 权限 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **列名不可用 SQL 关键字**：`'Order'` / `'Group'` / `'User'` 等需要加引号（不同 DB 引号格式不同：MS SQL `[Order]` / MySQL `` `Order` ``）。最好避免用关键字。
- **`sColumnProperty` 语法因 DB 而异**：
  - MS SQL: `'IDENTITY(1,1) PRIMARY KEY'`
  - SQL Compact: `'PRIMARY KEY'`（Identity 不被 Compact 支持，用其它方法）
  - MySQL: `'AUTO_INCREMENT PRIMARY KEY'`
  - 写错会通过 `sSQLState` 反馈语法错。
- **`MAX_DB_TABLE_COLUMNS = 255`**：理论最大；实际 SQL Compact 限 320 列、MS SQL 1024 列、Access 255 列。
- **`eDBColumn_XML` 不在 v1.2 列表里**：要存 XML 数据走 `NVarChar(max)` 类型。
- **`FB_DBWrite` 的默认 4 列要求**：`Timestamp` / `Name` / `Value`。如果用本 FB 建表时少了任何一列，后续 `FB_DBWrite` 调用会得到 `42S22`（column not found）。（工程经验补充）
- **表创建后不会自动加索引**：高吞吐场景需要事先想好索引；DBA 后期加更稳妥。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBTableCreate.TcPOU`](../examples/P_Demo_FB_DBTableCreate.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：OEM 设备首次部署——本 FB 在新建的 SQL Compact 库里建一张 `tProcessLog` 表，列结构匹配 `FB_DBWrite` 的最简模式（ID/Timestamp/Name/Value）。之后客户机就具备完整日志能力。
- **价值**：让"建库 → 建表 → 开始写入"整套初始化由 PLC 代码闭环，不需要 DBA / 外部工具介入；OEM 设备可以全自动初始化。
- **替代方案对比**：
  - **DBA 预建表**：靠谱但需要人工；OEM 自动化部署受限。
  - **`FB_DBStoredProcedures` 执行 CREATE TABLE SQL**：能用，灵活度更高（支持复杂列约束、索引、视图），但要写 SQL。
  - **本 FB**：最简单——只为基础日志结构设计，复杂场景用 Stored Procedure。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108022795.html
- **相关 FB / FC / DUT**：`FB_DBCreate`（前置建库）、`FB_DBWrite`（后续写入）、`FB_DBStoredProcedures`（复杂建表用）、`ST_DBColumnCfg`、`E_DbColumnTypes`、`MAX_DB_TABLE_COLUMNS`（GVL=255）
