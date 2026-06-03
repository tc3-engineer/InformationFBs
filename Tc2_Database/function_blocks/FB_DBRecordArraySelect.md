# FB_DBRecordArraySelect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108032011.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRecordArraySelect.TcPOU`](../examples/P_Demo_FB_DBRecordArraySelect.TcPOU) |

---

## 1. 功能简述

FB_DBRecordArraySelect 执行 `SELECT` SQL 命令一次性读出**多条结构化记录**到调用方提供的结构体数组。SQL 命令长度上限 10000 字符。从 `nStartIndex` 起最多读 `nRecordCount` 条；每条对应 PLC 端一个结构体实例。是 `FB_DBRecordSelect` / `FB_DBRecordSelect_EX`（单条版，§7.1.20.3 / 7.1.20.4 obsolete）的现代批量版本。**不支持 ASCII 文件**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID             : T_AmsNetID;
    hDBID              : UDINT;
    cbCmdSize          : UDINT;
    pCmdAddr           : UDINT;
    nStartIndex        : UDINT;
    nRecordCount       : UDINT;
    cbRecordArraySize  : UDINT;
    pDestAddr          : DWORD;
    bExecute           : BOOL;
    tTimeout           : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `cbCmdSize` | `UDINT` | - | SQL 命令字节长度，用 `SIZEOF(sCmd)`。 |
| `pCmdAddr` | `UDINT` | - | SQL 命令缓冲地址，`ADR(sCmd)`。 |
| `nStartIndex` | `UDINT` | - | 起始记录索引（0 开始）；用于分页。 |
| `nRecordCount` | `UDINT` | - | 最多读取的记录数（数组容量）。 |
| `cbRecordArraySize` | `UDINT` | - | 结果数组字节大小，`SIZEOF(arrRecords)`。 |
| `pDestAddr` | `DWORD` | - | 结果数组地址，`ADR(arrRecords)`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次查询。 |
| `tTimeout` | `TIME` | - | ADS 超时，大查询建议 `T#60S`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
    sSQLState   : ST_DBSQLError;
    nRecords    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示查询失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |
| `nRecords` | `UDINT` | **输出**：实际返回的记录数。`< nRecordCount` 表示已到结果末尾或匹配不足。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 执行 SELECT，把结果按 PLC 端结构体二进制布局写入 `pDestAddr`。

**PLC 端结构体必须匹配 DB 列顺序**：PDF §7.1.17 给的例子：
```iecst
TYPE ST_Record :
STRUCT
    ID         : T_ULARGE_INTEGER;
    Timestamp  : DT;
    Name       : STRING(80);
    VALUE      : LREAL;
END_STRUCT
END_TYPE
```
对应表 `tMyTable(ID bigint, Timestamp datetime, Name nvarchar(80), Value float)`。**字段顺序必须与 SELECT 输出列顺序严格一致**——`SELECT * FROM tMyTable` 时按表定义顺序；自定义 SELECT 时按列指定顺序。

**ARM 处理器的对齐特殊性**：PDF 明确指出："For ARM - processors the order of the data types is different and you have to add a 'Dummy-BYTE' to the struct because of the different byte alignment"。ARM 上要按"对齐顺序"排列字段并加 dummy padding：
```iecst
TYPE ST_Record :    (* ARM 版 *)
STRUCT
    ID        : T_ULARGE_INTEGER;
    Timestamp : DT;
    Value     : LREAL;
    Name      : STRING(80);
    Dummy     : BYTE;
END_STRUCT
END_TYPE
```

**`T_ULARGE_INTEGER` 来自 TcUtilities.lib**：PDF 提示需引用 `TcUtilities.lib`（TC2 时代的工具库）才能用 `T_ULARGE_INTEGER`（64 位无符号整型）映射 SQL 的 `bigint`。TC3 工程可用 `ULINT`（64 位无符号）替代。

**`nStartIndex` + `nRecordCount` 分页语义**：本 FB 内部似乎不是真分页（不会下推到 SQL 的 OFFSET/LIMIT），而是 Server 拿到完整结果后从 `nStartIndex` 开始取 `nRecordCount` 条。大结果集分页建议在 SQL 里就写 `OFFSET nStartIndex ROWS FETCH NEXT nRecordCount ROWS ONLY`（MS SQL 2012+）。

**`nRecords` 输出**：实际返回多少条。`nRecords < nRecordCount` 说明结果不足或已到末尾，业务侧可判断"还有数据吗"。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错 | 检查 SELECT |
| `0x0` | `42S02` | 表不存在 | 检查 FROM |
| `0x705` | `00000` | 缓冲大小不匹配（结构体大小与列布局对不上） | 检查结构体字段顺序 / 大小 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **PLC 结构体 = SELECT 列序**：列名匹配靠**顺序**不是按名匹配。`SELECT Name, Value` 与 `SELECT Value, Name` 拿到的内容完全不同。
- **NVARCHAR / NTEXT 在 PLC 端用 `STRING(N)`**：注意宽字符与字节的换算。SQL Server 的 `NVARCHAR(80)` 是 80 字符（160 字节），PLC `STRING(80)` 是 80 字节。匹配方式见 PDF §6.5.2 之后的章节。
- **ARM 平台对齐**：CX9 系列等 ARM CX 必须改结构体布局，否则会读到错位数据——是非常隐蔽的 bug。（工程经验补充）
- **`pDestAddr := ADR(arr)` 而非 `ADR(arr[0])`**：本 FB 写整段数组，地址传整体的起始；前一种和后一种值相同但前一种语义清晰。
- **大结果集慢**：单 ADS 报文上限约 1 MB，单次最多容纳的记录数 = 1 MB / SIZEOF(struct)。超过用分页或循环。
- **ASCII 文件型 DB 不支持**：PDF 明确指出 "not compatible with ASCII files"——ASCII 是顺序文件，没有 SELECT 语义。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRecordArraySelect.TcPOU`](../examples/P_Demo_FB_DBRecordArraySelect.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上"班次报表"页要展示最近 20 条工艺日志记录——本 FB 一次性把 20 条读到 PLC 端 `ARRAY[0..19] OF ST_Record`，HMI 再绑定数组到 Repeater 控件展示。
- **价值**：相比循环调 `FB_DBRecordSelect`（已废弃，每次只读一条）——批量调用节省 19 次 ADS 来回，性能高 10 倍以上。
- **替代方案对比**：
  - **`FB_DBRecordSelect`（obsolete）**：单条版本，已废弃，新代码不该用。
  - **`FB_DBStoredProceduresRecordArray`**：参数化 + 多条返回，更安全，复杂业务推荐。
  - **本 FB**：纯 SQL 多条查询的主力工具。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108032011.html
- **相关 FB / FC / DUT**：`FB_DBRecordSelect` / `FB_DBRecordSelect_EX`（obsolete 单条版本）、`FB_DBStoredProceduresRecordArray`（参数化）、`T_ULARGE_INTEGER`（TcUtilities）
