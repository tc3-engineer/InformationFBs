# FB_SQLDatabaseEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674382859.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLDatabaseEvt.TcPOU`](../examples/P_Demo_FB_SQLDatabaseEvt.TcPOU) |

---

## 1. 功能简述

SQL Expert mode 的数据库连接管理功能块（PDF §6.1.1.3.2）。提供 `Connect` 打开常驻数据库连接、`Disconnect` 关闭；以及 `CreateCmd` / `CreateSP` 两个工厂方法——它们把当前已打开的连接句柄绑定到一个新的 `FB_SQLCommandEvt`（执行任意 SQL）或 `FB_SQLStoredProcedureEvt`（执行存储过程）实例上，让那些实例「借用」本 FB 的常驻连接，避免每次执行 SQL 都重连。这是 SQL Expert mode 的入口——区别于 PLC Expert mode 的 `FB_PLCDB*Evt` 系列（每次自动开关连接），本 FB 用「显式打开 → 反复使用 → 显式关闭」模式，高吞吐场景必备。

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
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。远端 SQL Server 建连建议加大到 `T#30S` 含 TCP 建连时间。 |

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
| `bBusy` | `BOOL` | 任一方法（Connect/Disconnect/CreateCmd/CreateSP）运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |

### Method: `Connect`

```iecst
METHOD Connect : BOOL
VAR_INPUT
    hDBID: UDINT := 1;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hDBID` | `UDINT` | `1` | 已在 XML 配置中注册的数据库连接 ID。默认 1 是第一个连接。 |

### Method: `CreateCmd`

```iecst
METHOD CreateCmd : BOOL
VAR_INPUT
    pSQLCommand: POINTER TO FB_SQLCommandEvt;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSQLCommand` | `POINTER TO FB_SQLCommandEvt` | 调用方提供的 `FB_SQLCommandEvt` 实例地址；本 FB 把当前连接绑定到该实例。 |

### Method: `CreateSP`

```iecst
METHOD CreateSP : BOOL
VAR_INPUT
    sProcedureName: T_MaxString;
    pParameterInfo: POINTER TO ARRAY [0..MAX_SPPARAMETER] OF ST_SQLSPParameter;
    cbParameterInfo: UDINT;
    pSQLProcedure: POINTER TO FB_SQLStoredProcedureEvt;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sProcedureName` | `T_MaxString` | DB 中已存在的存储过程名（如 `'dbo.SP_GetCustomerPositions'`）。 |
| `pParameterInfo` | `POINTER TO ARRAY [0..MAX_SPPARAMETER] OF ST_SQLSPParameter` | 存储过程参数描述数组地址（每元素描述一个 IN/OUT 参数）。 |
| `cbParameterInfo` | `UDINT` | 参数描述数组 SIZEOF。 |
| `pSQLProcedure` | `POINTER TO FB_SQLStoredProcedureEvt` | 调用方提供的 `FB_SQLStoredProcedureEvt` 实例地址；本 FB 把连接 + 参数信息绑定到该实例。 |

### Method: `Disconnect`

```iecst
METHOD Disconnect : BOOL
```

无入参——关闭本 FB 实例打开的连接。

### 关联结构 `ST_SQLSPParameter`（PDF §6.1.2.3.4）

| 字段 | 类型 | 说明 |
|---|---|---|
| `sParameterName` | `STRING(50)` | 参数名（如 `'@Customer_ID'`，与 DB 端存储过程定义对应）。 |
| `eParameterType` | `E_SPParameterType` | 参数方向：`Input` / `Output` / `InputOutput` / `ReturnValue` / `OracleCursor`。 |
| `eParameterDataType` | `E_ColumnType` | 数据类型枚举。 |
| `nParameterSize` | `UDINT` | 参数值字节大小。 |

## 3. 行为说明

**SQL Expert mode 的设计**：PLC Expert mode（`FB_PLCDB*Evt`）封装了「建表 / 读 / 写 / 命令」的高层语义但每次操作都自动开关连接；SQL Expert mode（本 FB + `FB_SQLCommandEvt` / `FB_SQLResultEvt` / `FB_SQLStoredProcedureEvt`）暴露底层「建连 + 反复执行 + 断连」模式，让用户精细控制连接生命周期。两种 mode 可在同一程序里混用，不冲突。

**典型生命周期**：
1. PLC 启动后调 `Connect(hDBID := 1)` 建一次常驻连接（阻塞调用直到方法返回 TRUE，且 `bError = FALSE`）。
2. 调 `CreateCmd(ADR(fbCmd))` 把连接绑到 `fbCmd : FB_SQLCommandEvt` 实例上；后续用 `fbCmd.Execute(ADR(sSql), SIZEOF(sSql))` 执行 SQL，复用同一连接。
3. 需要执行存储过程时调 `CreateSP(sProcName, ADR(aParaInfo), SIZEOF(aParaInfo), ADR(fbSP))` 绑到存储过程实例。
4. PLC 停机前调 `Disconnect()` 释放连接。

**`CreateCmd` 与 `CreateSP` 的区别**：`CreateCmd` 一次返回，本周期完成（PDF 明确「The initialization of the function block FB_SQLCommand is completed in the same cycle」）；`CreateSP` 可能跨多周期（需要预编译存储过程参数描述），调用方必须周期检查方法返回值。

**连接生命周期与 FB 实例的绑定**：每个 `FB_SQLDatabaseEvt` 实例管理一个连接句柄；通过 `CreateCmd` / `CreateSP` 把这个句柄借给其他 FB。同一个 `FB_SQLDatabaseEvt.Connect` 后可以 `CreateCmd` 多次建立多个 `FB_SQLCommandEvt` 实例都用同一连接。

**`Disconnect` 后**：所有借了该连接的 `FB_SQLCommandEvt` / `FB_SQLStoredProcedureEvt` 实例都失效，再调它们的方法会报错。建议先停业务，再 Disconnect。

**何时该 Disconnect / Reconnect**：长时间空闲的连接会被 DB 端（如 MySQL `wait_timeout = 28800` 秒）主动断；建议每 24 小时 Disconnect + Connect 一次清理，或在检测到错误时执行重连。（工程经验补充）

**Tc3_EventLogger 错误**：`bError` 时 `ipTcResult.RequestEventText` 取详细文本，常见 `'Connection failed'`、`'Authentication failed'`、`'Procedure not found'`（CreateSP 时）。

## 4. 错误码 / 返回值

每方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 报实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| Connect 错，事件含 `Connection failed` | DB 服务器不可达 / 认证失败 | 检查 IP/端口/用户名/密码 |
| Connect 错，事件含 `hDBID not found` | XML 没注册该 ID | 用 `FB_ConfigTcDBSrvEvt.Read` 列出现有连接 |
| CreateSP 错，事件含 `Procedure not found` | 存储过程名拼写错或不存在 | DBA 确认过程已建并 GRANT EXECUTE |
| CreateSP 错，事件含 `Parameter mismatch` | `ST_SQLSPParameter` 描述与 DB 过程签名不匹配 | 比对过程定义 |
| Disconnect 错 | 连接已被对端关 | 一般 ignore；下次 Connect 重建即可 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **`hDBID` 必须事先在 XML 注册**：通过 TF6420 配置器或 `FB_ConfigTcDBSrvEvt.Create` 创建后才能用。
- **`pSQLCommand` / `pSQLProcedure` 必须指向同作用域且持续有效的 FB 实例**：不能临时建栈实例传址；Server 异步操作期间该实例不能被销毁。
- **CreateSP 的 `pParameterInfo^` 数组同样要持续有效**：直到 Release / Disconnect 之前不能修改。
- **重连后的 `FB_SQLCommandEvt` 实例不能直接复用**：必须重新 `CreateCmd` 绑定。
- **`tTimeout` 太小**：远端 SQL Server 首次连接可能要数秒（TLS 握手 + 认证）；默认 5 秒在某些 LAN 环境刚好够，VPN / 跨网络要加大到 30S。
- **多实例并发**：可同时建多个 `FB_SQLDatabaseEvt` 连不同 `hDBID`；DB 连接数受限于 Server 端 `MAX_DBCONNECTIONS = 255`。
- **不能给 `FB_PLCDB*Evt` 系列用本 FB 的连接**：那些 FB 用自动连接管理，与本 FB 的连接不兼容。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLDatabaseEvt.TcPOU`](../examples/P_Demo_FB_SQLDatabaseEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 控制器每秒向 MS SQL 写 100 条工艺参数（高吞吐采集）+ 偶尔调存储过程做日终汇总。如果用 PLC Expert mode 的 `FB_PLCDBCmdEvt`，每次 Execute 都自动开关连接 → 每条 200-500 ms 建连延迟 → 实际吞吐降到 5 条/秒。改用 SQL Expert mode：PLC 启动后 `Connect` 一次拿到常驻连接，`CreateCmd` 绑到 `FB_SQLCommandEvt`，后续每条 SQL 只有协议层延迟 5-10 ms，吞吐 100+ 条/秒；同时 `CreateSP` 绑存储过程实例做日终汇总。
- **价值**：高吞吐 10-50 倍提升；连接生命周期可视化；存储过程参数描述一次建立反复用；EventLogger 错误诊断。
- **替代方案对比**：
  - **PLC Expert `FB_PLCDBCmdEvt`**：自动连接管理简单，但高频写不能用。
  - **Tc2_Database `FB_DBConnectionOpen` + `FB_DBRecordInsert_EX`**：TC2 等价但 nErrId 报错。
  - **AutoLog（`FB_PLCDBAutoLogEvt`）**：Server 端周期日志最高效，但需固定变量集 + 配置器。
  - **本 FB + `FB_SQLCommandEvt`**：TC3 高吞吐 + 自由 SQL 首选；obsolete `FB_SQLDatabase`（无 Evt）仅老项目兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674382859.html
- **相关 FB / FC / DUT**：`FB_SQLCommandEvt`（被 CreateCmd 绑定）、`FB_SQLStoredProcedureEvt`（被 CreateSP 绑定）、`FB_SQLResultEvt`（读结果）、`ST_SQLSPParameter` / `E_SPParameterType` / `E_ColumnType`、`MAX_SPPARAMETER`、`MAX_DBCONNECTIONS`、obsolete `FB_SQLDatabase`
