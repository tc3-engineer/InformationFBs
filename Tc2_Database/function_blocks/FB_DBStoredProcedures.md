# FB_DBStoredProcedures

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108033547.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBStoredProcedures.TcPOU`](../examples/P_Demo_FB_DBStoredProcedures.TcPOU) |

---

## 1. 功能简述

FB_DBStoredProcedures 执行数据库的**存储过程**（Stored Procedure），通过 `ST_DBParameter` 数组传入 / 取出 INPUT / OUTPUT / INOUT 参数。本 FB **不返回数据集**——只用于"调用过程做服务端逻辑"场景（如更新统计表、触发归档、计算业务指标）。如果要返回结果集，用 `FB_DBStoredProceduresRecordArray`（多行）或 `FB_DBStoredProceduresRecordReturn`（单行，obsolete）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID              : T_AmsNetID    :='';
    hDBID               : UDINT         :=1;
    sProcedureName      : T_MaxString   :='';
    cbParameterList     : UDINT;
    pParameterList      : POINTER TO ARRAY[0..MAX_STORED_PROCEDURES_PARAMETERS] OF ST_DBParameter;
    bExecute            : BOOL;
    tTimeout            : TIME          := T#15s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | 目标 AMS Net ID。本机 = `''`（默认值即空串）。 |
| `hDBID` | `UDINT` | `1` | 数据库连接 ID。默认值 `1`（第一个连接）。 |
| `sProcedureName` | `T_MaxString` | `''` | 存储过程名（DB 端已创建好的过程名）。 |
| `cbParameterList` | `UDINT` | - | 参数列表字节大小，`SIZEOF(arrParams)`。 |
| `pParameterList` | `POINTER TO ARRAY[0..MAX_STORED_PROCEDURES_PARAMETERS] OF ST_DBParameter` | - | 参数列表地址，`ADR(arrParams)`。`MAX_STORED_PROCEDURES_PARAMETERS = 255`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次调用。 |
| `tTimeout` | `TIME` | `T#15s` | ADS 超时。复杂存储过程建议加大。 |

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
| `bError` | `BOOL` | TRUE 表示调用失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |

### VAR_IN_OUT

无。

### 关联结构 `ST_DBParameter`（PDF §7.3.5）

```iecst
TYPE ST_DBParameter :
STRUCT
    sParameterName      : STRING(59);
    cbParameterValue    : UDINT;
    pParameterValue     : UDINT;
    eParameterDataType  : E_DBColumnTypes;
    eParameterType      : E_DBParameterTypes;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `sParameterName` | `STRING(59)` | 参数名（与存储过程定义中的 `@paramName` 对应）。 |
| `cbParameterValue` | `UDINT` | 参数值缓冲大小，用 `SIZEOF(value)`。 |
| `pParameterValue` | `UDINT` | 参数值缓冲地址，用 `ADR(value)`。 |
| `eParameterDataType` | `E_DBColumnTypes` | 参数数据类型枚举（与列类型同枚举）。 |
| `eParameterType` | `E_DBParameterTypes` | 参数方向：`eDBParameter_Input` / `eDBParameter_Output` / `eDBParameter_InputOutput` / `eDBParameter_ReturnValue` / `eDBParameter_OracleCursor`。 |

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 用调用方提供的参数数组调用对应存储过程；OUTPUT / INOUT 参数的值会回填到调用方 PLC 变量。

**参数列表准备**：每个参数一个 `ST_DBParameter` 项。PDF §7.3.5 给的示范：
```iecst
paraList[0].sParameterName     := 'p1';
paraList[0].eParameterDataType := eDBColumn_Integer;
paraList[0].eParameterType     := eDBParameter_Input;
paraList[0].cbParameterValue   := SIZEOF(p1);
paraList[0].pParameterValue    := ADR(p1);
```
PLC 端的实际变量（`p1 : DINT`）跟参数项是分开的——参数项里的 `pParameterValue` 是变量地址，Server 在调用前从该地址读 INPUT 值，调用后向 OUTPUT 地址写回值。

**5 种参数方向**（`E_DBParameterTypes`）：
- `eDBParameter_Input` (0)：仅传入；调用前 PLC 写值。
- `eDBParameter_Output` (1)：仅传出；调用后 Server 写值到 PLC 变量。
- `eDBParameter_InputOutput` (2)：双向；调用前后都用。
- `eDBParameter_ReturnValue` (3)：存储过程的 `RETURN` 值（MS SQL 的 `RETURN code`）。
- `eDBParameter_OracleCursor` (4)：仅 Oracle 用——返回游标。

**参数化优势**：相比 PLC 端拼 SQL（`FB_DBRecordInsert_EX`）——本 FB 走存储过程是参数化的，避免 SQL 注入；并且业务逻辑可以集中在 DB 层（DBA 维护），PLC 端只是触发器。

**调用不返回数据集**：本 FB 适合"做事不取结果"的过程（更新某统计表、触发归档作业、写审计日志）。需要返回的用 RecordReturn / RecordArray 系列。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错（过程内部） | DBA 检查过程定义 |
| `0x0` | `42501` | 过程权限不足 | 给用户 GRANT EXECUTE |
| `0x0` | `42S02` | 过程不存在 | 检查 `sProcedureName` 拼写、scheme |
| `0x0` | `07002` | 参数数 / 类型不匹配 | 比对参数列表与过程签名 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **参数顺序一般要匹配过程签名**：虽然 ST_DBParameter 给了 `sParameterName`，但部分 OLE DB Provider 仍按位置传参。安全做法是按过程参数顺序填 paraList。
- **`pParameterValue` 必须指向同一作用域且持续有效的变量**：不能用临时栈变量；Server 调用是异步的，本 FB 返回时若 PLC 变量已失效会读写错误地址。
- **OUTPUT 参数的 PLC 变量要够大**：例如过程返回 `NVARCHAR(200)` OUTPUT，PLC 变量要 `STRING(200)` 否则被截断或越界。
- **MS SQL 与 Oracle 参数命名风格不同**：MS SQL `@p1`，Oracle 直接 `p1`。`sParameterName` 一般填裸名（`'p1'`），Server 内部加前缀。
- **`MAX_STORED_PROCEDURES_PARAMETERS = 255`**：理论上限；实际过程参数通常 < 10。
- **DBA 不一定愿意给 GRANT**：生产 DB 走存储过程是好做法但需要 DBA 配合定义并 GRANT EXECUTE。OEM 设备初次部署要规划好。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBStoredProcedures.TcPOU`](../examples/P_Demo_FB_DBStoredProcedures.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：每个班次结束 PLC 调用 DBA 写好的存储过程 `sp_CloseShift(@batchId, @shiftStart, @shiftEnd, @totalCount OUT)`——过程内部把当班次数据归档到 `tArchive`、计算质量指标、更新统计表，最后输出归档行数；PLC 通过 OUT 参数拿到行数显示在 HMI。
- **价值**：相比 PLC 端写 5~10 条 SQL 调用——业务逻辑集中在 DB，PLC 端解耦；DBA 改归档逻辑不需要 PLC 改代码 + 升级；参数化无 SQL 注入风险。
- **替代方案对比**：
  - **PLC 端拼多条 SQL（`FB_DBRecordInsert_EX` 等）**：耦合紧，业务逻辑分散在 PLC + DB 两边。
  - **`FB_DBStoredProceduresRecordReturn`（obsolete 单行返回）/ `FB_DBStoredProceduresRecordArray`（多行返回）**：需要返回结果集时用。
  - **本 FB**：纯调用、不返回数据集场景的最优解。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108033547.html
- **相关 FB / FC / DUT**：`FB_DBStoredProceduresRecordArray`（返回多行）、`FB_DBStoredProceduresRecordReturn`（obsolete，单行）、`ST_DBParameter`、`E_DBParameterTypes`、`E_DBColumnTypes`、`MAX_STORED_PROCEDURES_PARAMETERS`
