# FB_PLCDBCmd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183728395.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBCmd.TcPOU`](../examples/P_Demo_FB_PLCDBCmd.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的占位符 SQL 命令 FB（PDF §6.1.4.2.6）。两个方法 `Execute`（不返回数据）和 `ExecuteDataReturn`（返回数据集），与 `FB_PLCDBCmdEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_PLCDBCmdEvt`。

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
    ipTcResultEvent: Tc3_EventLogger.I_TcResultEvent;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式事件接口。 |

### VAR_IN_OUT

无。

### Method: `Execute`

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

参数同 `FB_PLCDBCmdEvt.Execute`——含占位符的 SQL + 参数描述数组 + 值结构。

### Method: `ExecuteDataReturn`

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

参数同 `FB_PLCDBCmdEvt.ExecuteDataReturn`。

## 3. 行为说明

与 `FB_PLCDBCmdEvt` 完全一致——支持 SQL 占位符 `{name}` 模式：调用方在 SQL 命令字符串里用 `{paraName}` 标位置，Server 根据 `pParameter^[i].sParaName` 在命令里找对应占位符并用 `pData^` 偏移读出实际值替换。`Execute` 用于 INSERT / UPDATE / DELETE / DDL 等不返回数据的场景；`ExecuteDataReturn` 用于 SELECT，结果写到 `pReturnData^` 自定义结构数组，`pRecords^` 输出实际读到的行数。连接每次自动开关。

**与 Evt 版差别**：仅输出接口字段名 / 类型不同。其他全部一样——参数化优势（防 SQL 注入、Server 类型转换、SQL 模板复用）、`E_ExpParameterType` 类型枚举、`pParameter^` 与 `pData^` 字段顺序要求。

**为何保留**：Beckhoff 向后二进制兼容；老 PLC 工程升级 TwinCAT Runtime 后本 FB 仍可用。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际结果。典型错误：Syntax error、Cannot convert、Placeholder not found、Buffer overflow。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_PLCDBCmdEvt`。
- **行为细节与 Evt 版完全一致**：套用所有 §5 注意事项。
- **占位符 `{name}` 不含大括号**：`sParaName` 填裸名。
- **`pData^` 字段顺序与参数描述顺序对应**：错位致错值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBCmd.TcPOU`](../examples/P_Demo_FB_PLCDBCmd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 工程的工艺记录 INSERT 模块用本 FB；新模块迁移到 `FB_PLCDBCmdEvt`。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_PLCDBCmdEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183728395.html
- **相关 FB / FC / DUT**：`FB_PLCDBCmdEvt`（现代版）、`ST_ExpParameter`、`E_ExpParameterType`、`MAX_DBCOLUMNS`
