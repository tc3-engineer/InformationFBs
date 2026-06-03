# FB_SQLDatabase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183828619.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLDatabase.TcPOU`](../examples/P_Demo_FB_SQLDatabase.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 SQL Expert mode 连接管理 FB（PDF §6.1.4.3.2）。提供 `Connect` / `Disconnect` 连接管理 + `CreateCmd` / `CreateSP` 把连接绑给 obsolete 版的 `FB_SQLCommand` 与 `FB_SQLStoredProcedure`。行为与 `FB_SQLDatabaseEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_SQLDatabaseEvt`。

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
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。远端 SQL 建议加大到 `T#30S`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResultEvent: Tc3_EventLogger.I_TcResultEvent;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 任一方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式事件接口。 |

### VAR_IN_OUT

无。

### Method: `Connect`

```iecst
METHOD Connect : BOOL
VAR_INPUT
    hDBID: UDINT := 1;
END_VAR
```

参数同 `FB_SQLDatabaseEvt.Connect`——打开指定 hDBID 的常驻连接。

### Method: `CreateCmd`

```iecst
METHOD CreateCmd : BOOL
VAR_INPUT
    pSQLCommand: POINTER TO FB_SQLCommand;
END_VAR
```

注意：参数类型是 `POINTER TO FB_SQLCommand`（obsolete 版的 Command FB），与 Evt 版的 `POINTER TO FB_SQLCommandEvt` 不同。两套不能混用。

### Method: `CreateSP`

```iecst
METHOD CreateSP : BOOL
VAR_INPUT
    sProcedureName: T_MaxString;
    pParameterInfo: POINTER TO ARRAY [0..MAX_SPPARAMETER] OF ST_SQLSPParameter;
    cbParameterInfo: UDINT;
    pSQLProcedure: POINTER TO FB_SQLStoredProcedure;
END_VAR
```

注意：参数类型是 `POINTER TO FB_SQLStoredProcedure`（obsolete 版的 SP FB），与 Evt 版的 `POINTER TO FB_SQLStoredProcedureEvt` 不同。

### Method: `Disconnect`

`METHOD Disconnect : BOOL` —— 无入参，关连接。

## 3. 行为说明

与 `FB_SQLDatabaseEvt` 完全一致的行为语义——SQL Expert mode 的入口；`Connect` 建一次常驻连接，`CreateCmd` / `CreateSP` 把该连接绑给其他 FB 实例（注意：必须是 obsolete 版的 `FB_SQLCommand` / `FB_SQLStoredProcedure`，不能跨绑给 Evt 版），后续多次执行 SQL / 存储过程共用该连接，最后 `Disconnect` 释放。同一个 `FB_SQLDatabase` 实例可 CreateCmd 多次创建多个 Command 实例都用同一连接。`CreateCmd` 同周期完成；`CreateSP` 可能跨多周期完成（需周期检查方法返回值）。

**与 Evt 版差别**：(1) 输出接口字段名 `ipTcResultEvent` 与类型 `I_TcResultEvent`（vs 新版 `ipTcResult` + `I_TcMessage`）；(2) `CreateCmd` / `CreateSP` 的目标 FB 类型是 obsolete 版（`FB_SQLCommand` / `FB_SQLStoredProcedure`），**不能跨绑 Evt 版**。新旧两套各自独立工作不混用。

**为何保留**：Beckhoff 向后二进制兼容；老 PLC 工程升级 Runtime 后本 FB 仍可用。

## 4. 错误码 / 返回值

每方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际成败。典型错误：Connection failed、hDBID not found、Procedure not found（CreateSP）。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_SQLDatabaseEvt`。
- **不能与 Evt 版混用**：`CreateCmd` 绑给 `FB_SQLCommand`（obsolete）而非 `FB_SQLCommandEvt`。
- **`tTimeout` 太小**：远端 SQL 建议 `T#30S`。
- **行为细节与 Evt 版完全一致**：套用所有 §5 注意事项。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLDatabase.TcPOU`](../examples/P_Demo_FB_SQLDatabase.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 工程的 SQL 长连接模块用本 FB 系列；新模块迁移到 Evt 版。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_SQLDatabaseEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183828619.html
- **相关 FB / FC / DUT**：`FB_SQLDatabaseEvt`（现代版）、`FB_SQLCommand` / `FB_SQLStoredProcedure`（obsolete 配套）、`ST_SQLSPParameter`、`E_SPParameterType`、`MAX_SPPARAMETER`
