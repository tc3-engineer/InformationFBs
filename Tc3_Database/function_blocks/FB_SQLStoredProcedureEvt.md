# FB_SQLStoredProcedureEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/18014401183870603.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLStoredProcedureEvt.TcPOU`](../examples/P_Demo_FB_SQLStoredProcedureEvt.TcPOU) |

---

## 1. 功能简述

SQL Expert mode 下执行存储过程的功能块（PDF §6.1.1.3.5）。使用前必须由 `FB_SQLDatabaseEvt.CreateSP` 把连接 + 存储过程名 + 参数信息绑定到本 FB 实例。提供 `Execute`（不返回结果集，常用于 UPDATE / INSERT 类过程或仅取 OUTPUT 参数）、`ExecuteDataReturn`（带结果集，需配 `FB_SQLDBResultEvt` 接收）、`Release`（释放绑定时传入的参数描述）三个方法。与 `FB_PLCDBCmdEvt` 用占位符模拟「参数化」不同——本 FB 直接调用 DB 端 stored procedure，业务逻辑可以集中在 DB 层（DBA 维护），PLC 端只是触发器。

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

### Method: `Execute`（不返回结果集）

```iecst
METHOD Execute : BOOL
VAR_INPUT
    pParameterStrc: POINTER TO BYTE;
    cbParameterStrc: UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pParameterStrc` | `POINTER TO BYTE` | 参数结构体地址；包含传入存储过程的 IN 参数值，调用后 OUT 参数值回填到该结构体（按 CreateSP 时声明的字段顺序）。 |
| `cbParameterStrc` | `UDINT` | 参数结构体 SIZEOF。 |

### Method: `ExecuteDataReturn`（返回结果集）

```iecst
METHOD ExecuteDataReturn : BOOL
VAR_INPUT
    pParameterStrc: POINTER TO BYTE;
    cbParameterStrc: UDINT;
    pSQLDBResult: POINTER TO FB_SQLDBResultEvt;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pParameterStrc` | `POINTER TO BYTE` | 参数结构体地址（同上）。 |
| `cbParameterStrc` | `UDINT` | 参数结构体 SIZEOF。 |
| `pSQLDBResult` | `POINTER TO FB_SQLDBResultEvt` | `FB_SQLDBResultEvt` 实例地址；返回行将缓存到 Server 内由该实例读取。 |

### Method: `Release`

```iecst
METHOD Release : BOOL
```

无入参——释放 `CreateSP` 初始化时传入的参数描述信息（PDF 第 6.1.1.3.5.3 节）。停用本 FB 实例前应调用。

## 3. 行为说明

**典型生命周期**：
1. 调 `FB_SQLDatabaseEvt.Connect(hDBID)` 建连接。
2. 准备参数描述数组 `aSPParams : ARRAY[0..N] OF ST_SQLSPParameter`（每元素一个参数：name / type / data type / size）。
3. 调 `FB_SQLDatabaseEvt.CreateSP(sProcName, ADR(aSPParams), SIZEOF(aSPParams), ADR(fbSP))` 把连接 + 参数描述绑到本 FB 实例；该方法可能跨多周期完成。
4. 准备值结构 `stParaValues`（字段顺序对应 `aSPParams^[i].sParameterName`），填入 IN 参数实际值。
5. 调 `fbSP.Execute(ADR(stParaValues), SIZEOF(stParaValues))` 或 `ExecuteDataReturn(...)` 调用存储过程。
6. 完成后从 `stParaValues` 读 OUTPUT 参数；若有结果集从 `fbResult` 读。
7. 停用前调 `fbSP.Release()` 释放参数描述。

**`pParameterStrc^` 字段排列**：按 `CreateSP` 时传入的 `pParameterInfo^[i]` 顺序。例如参数信息数组是 `(name='@Cust', dir=Input, type=BigInt, size=8)`、`(name='@Count', dir=Output, type=Int32, size=4)`，那 `pParameterStrc` 指向的结构应是 `STRUCT Cust : LINT; Count : DINT; END_STRUCT`。Execute 前调用方写 Cust 值；执行后 Server 把过程的 @Count OUTPUT 值回填到 Count 字段。

**`Execute` vs `ExecuteDataReturn`**：当存储过程仅做事不返回结果集（UPDATE / 触发归档 / 计算并 OUTPUT 单值），用 `Execute`；返回 SELECT 类结果集时用 `ExecuteDataReturn` 配 `FB_SQLDBResultEvt`。注意 PDF 此处用 `FB_SQLDBResultEvt`（而非 `FB_SQLResultEvt`），是一个专门的存储过程结果接收 FB——细节同 `FB_SQLResultEvt`。

**与 PLC Expert 占位符模式对比**：`FB_PLCDBCmdEvt` 占位符是 Server 端字符串替换 + 参数化，PLC 端只感知数据结构；本 FB 是真正调用 DB 端 stored procedure（DB 引擎层面），过程内部可以有复杂逻辑（事务、循环、临时表），且过程定义可由 DBA 维护，PLC 不需要改代码。

**参数化 + Server 缓存的优势**：(1) 防 SQL 注入——值是绑定参数不是字符串拼接；(2) Server 端 stored procedure 可预编译执行计划，多次调用快；(3) 业务逻辑集中在 DB 层易维护。

**Tc3_EventLogger 错误**：失败时 `ipTcResult.RequestEventText` 取详细文本，常见 `'Procedure not initialized'`（忘记 CreateSP）、`'Parameter mismatch'`（结构与描述不符）、`'Procedure not found'`、`'Permission denied'`。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 报实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| 事件含 `not initialized` | 忘记 `FB_SQLDatabaseEvt.CreateSP` | 加初始化 |
| 事件含 `Parameter mismatch` | `pParameterStrc^` 结构与 CreateSP 时的描述不符 | 比对字段顺序 / 大小 |
| 事件含 `Permission denied` | 用户无 EXECUTE 权限 | DBA `GRANT EXECUTE` |
| 事件含 `Procedure not found` | 过程不存在或 scheme 错（缺少 `dbo.`） | 检查名 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **`pParameterStrc^` 字段顺序与 `CreateSP` 时的 `pParameterInfo^` 顺序必须严格一致**：Server 按累积偏移读 / 写；错位会得到错值。建议字段命名一致便于交叉对照。（工程经验补充）
- **OUTPUT 参数对应字段必须事先分配**：例如 OUTPUT NVARCHAR(200) 对应 `STRING(200)` 字段，调用前内容随便填，调用后会被 Server 回写。
- **`ReturnValue` 参数**：MS SQL 的 `RETURN code` 通过 `eParameterType := E_SPParameterType.ReturnValue` 在 CreateSP 时声明；通常放在参数列表第一个或最后一个，按结构字段顺序对应。
- **`Release` 不调会泄漏 Server 端描述**：长时间运行后参数描述累积；下次重启 PLC 才清理。建议每次停用本 FB 之前都 Release。
- **多次 Execute 同一 FB 实例**：可行，每次重新填 `pParameterStrc^` 的 IN 字段即可，无需重 CreateSP。
- **连接断后失效**：`FB_SQLDatabaseEvt.Disconnect` 后本 FB 实例所有方法失效；必须 Disconnect → Connect → CreateSP 重建。
- **存储过程内部错误**：DB 端 `RAISERROR` / `THROW` 会被 Server 转成 `bError = TRUE` + 事件文本；过程内部 `TRY...CATCH` 可吃掉错误让 Server 端看不到。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLStoredProcedureEvt.TcPOU`](../examples/P_Demo_FB_SQLStoredProcedureEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：班次结束时 PLC 调 DBA 写好的存储过程 `dbo.SP_CloseShift(@batchId IN, @shiftStart IN, @shiftEnd IN, @totalCount OUT, @qualityIndex OUT)`——过程内部把当班次数据归档、计算质量指标、更新统计表，最后 OUTPUT 归档行数与质量指数。PLC 通过本 FB 调用 + 取 OUT 参数显示在 HMI。
- **价值**：业务逻辑集中在 DB 层，DBA 改归档规则不需要 PLC 改代码 + 升级；参数化无 SQL 注入；OUTPUT 参数让 PLC 不必再发 SELECT 拿结果。
- **替代方案对比**：
  - **PLC 端拼多条 SQL（`FB_SQLCommandEvt.Execute`）**：耦合紧，逻辑分散在 PLC + DB 两边。
  - **`FB_DBStoredProcedures`（Tc2_Database）**：等价但 nErrId 报错。
  - **`FB_PLCDBCmdEvt`（PLC Expert mode）**：用占位符 SQL 间接调用，但不能直接拿到 OUT 参数。
  - **本 FB**：TC3 SQL Expert mode 调用存储过程的最优解；obsolete `FB_SQLStoredProcedure` 仅老项目兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/18014401183870603.html
- **相关 FB / FC / DUT**：`FB_SQLDatabaseEvt`（必须先 CreateSP 绑参数描述）、`ST_SQLSPParameter` / `E_SPParameterType`、`FB_SQLDBResultEvt`（接收结果集）、`MAX_SPPARAMETER`、obsolete `FB_SQLStoredProcedure`
