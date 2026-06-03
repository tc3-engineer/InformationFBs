# FB_DBStoredProceduresRecordReturn

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108044171.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBStoredProceduresRecordReturn.TcPOU`](../examples/P_Demo_FB_DBStoredProceduresRecordReturn.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃（Obsolete，PDF §7.1.20.5）**。FB_DBStoredProceduresRecordReturn 执行返回**单条记录**的存储过程：参数列表机制同 `FB_DBStoredProcedures`，但额外把过程返回的 SELECT 结果集中**第 `nRecordIndex` 条**写入 PLC 结构体。新代码应改用 `FB_DBStoredProceduresRecordArray`（多条版）——后者支持一次性返回多条，性能与灵活性更好。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetID    :='';
    hDBID           : UDINT         :=1;
    sProcedureName  : T_MaxString   :='';
    cbParameterList : UDINT;
    pParameterList  : POINTER TO ARRAY[0..MAX_STORED_PROCEDURES_PARAMETERS] OF ST_DBParameter;
    nRecordIndex    : UDINT;
    cbRecordSize    : UDINT;
    pRecordAddr     : DWORD;
    bExecute        : BOOL;
    tTimeout        : TIME          := T#15s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | 目标 AMS Net ID。 |
| `hDBID` | `UDINT` | `1` | 数据库连接 ID。 |
| `sProcedureName` | `T_MaxString` | `''` | 存储过程名。 |
| `cbParameterList` | `UDINT` | - | 参数列表字节大小。 |
| `pParameterList` | `POINTER TO ARRAY[0..MAX_STORED_PROCEDURES_PARAMETERS] OF ST_DBParameter` | - | 参数列表地址。 |
| `nRecordIndex` | `UDINT` | - | 读取的记录索引（0 开始）。 |
| `cbRecordSize` | `UDINT` | - | 目标结构体大小。 |
| `pRecordAddr` | `DWORD` | - | 目标结构体地址。**PDF 描述文本中写为 `pDestAddr`，实际接口字段名是 `pRecordAddr`** —— Beckhoff PDF 内部叙述与代码名的不一致。 |
| `bExecute` | `BOOL` | - | 上升沿触发。 |
| `tTimeout` | `TIME` | `T#15s` | ADS 超时。 |

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
| `bError` | `BOOL` | TRUE 表示失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |
| `nRecords` | `UDINT` | 实际返回记录数。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃原因**：单条返回——绝大多数业务需要多条；用 `FB_DBStoredProceduresRecordArray` 一次取多条更划算。Beckhoff 在文档 1.0.13 版起就推荐 RecordArray 版本。

**调用方式（兼容）**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 用参数列表调过程；过程的 SELECT 结果集中第 `nRecordIndex` 条写入 `pRecordAddr`。

**`pRecordAddr` vs `pDestAddr` 命名陷阱**：PDF §7.1.20.5 在 VAR_INPUT 块里写的是 `pRecordAddr`，但下面的字段描述段落把它称为 `pDestAddr`（看上去是文档复制 `FB_DBRecordSelect` 时忘了改字段名）。**调用代码必须按 VAR 声明写 `pRecordAddr`**——这是 Beckhoff 原始 PDF 中的命名与描述不一致问题，已在 InfoSys 上保留同样的拼写。

**结构体布局要求**：与 `FB_DBStoredProceduresRecordArray` / `FB_DBRecordArraySelect` 同——列序匹配、ARM 对齐特殊处理。

**参数化优势**：与 `FB_DBStoredProcedures` 同——无 SQL 注入；业务逻辑在 DB 层。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错（过程内） | DBA 检查 |
| `0x0` | `42501` | 权限不足 | GRANT EXECUTE |
| `0x0` | `42S02` | 过程不存在 | 检查名称 |
| `0x0` | `07002` | 参数不匹配 | 比对签名 |
| `0x705` | `00000` | cbRecordSize 不对 | 检查结构体 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`pRecordAddr` 拼写陷阱**：与 PDF 描述段落里写的 `pDestAddr` 不一致；以 VAR 声明的 `pRecordAddr` 为准。
- **单条返回限制**：业务需要多条改用 `FB_DBStoredProceduresRecordArray`。
- **参数列表的所有 PLC 变量必须静态作用域**：与 `FB_DBStoredProcedures` 同。
- **ARM 对齐特殊**：与 RecordArray 版同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBStoredProceduresRecordReturn.TcPOU`](../examples/P_Demo_FB_DBStoredProceduresRecordReturn.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护中期老代码——某业务流程用本 FB 调存储过程获取"当前班次的某个聚合指标"（单条返回的查询）。新代码应改 `FB_DBStoredProceduresRecordArray` + 限制 TOP 1。
- **价值（历史）**：参数化单条返回的 TC2 中期工具。
- **替代方案对比**：
  - **`FB_DBStoredProceduresRecordArray`**：✅ 新代码，多条 + 同样的参数化能力。
  - **本 FB**：仅兼容老代码。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.20.5（Obsolete）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108044171.html
- **相关 FB / FC**：`FB_DBStoredProceduresRecordArray`（新代码推荐）、`FB_DBStoredProcedures`（不返数据集版）、`ST_DBParameter`
