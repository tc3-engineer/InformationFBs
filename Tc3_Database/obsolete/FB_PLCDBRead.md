# FB_PLCDBRead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183259275.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBRead.TcPOU`](../examples/P_Demo_FB_PLCDBRead.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 PLC Expert mode 数据读取 FB（PDF §6.1.4.2.4）。提供 `Read`（标准 4 列表）和 `ReadStruct`（自定义表）两个方法，行为与 `FB_PLCDBReadEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_PLCDBReadEvt`。

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

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `nRecords` | `UDINT` | 输出按过滤条件可获得的最大记录数。 |
| `eTraceLevel` | `TcEventSeverity` | 事件分级。 |

### Method: `Read`

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

参数同 `FB_PLCDBReadEvt.Read`——读 Beckhoff 标准 4 列结构。

### Method: `ReadStruct`

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

参数同 `FB_PLCDBReadEvt.ReadStruct`——读自定义结构表。

## 3. 行为说明

与 `FB_PLCDBReadEvt` 完全一致的行为语义——本 FB 提供两种读取风格：`Read` 方法专为 Beckhoff 标准 4 列日志表（ID / Timestamp / Name / Value）设计，结合 `sDBSymbolName` 按 Name 列做过滤；`ReadStruct` 用于任意自定义表，列名通过 `pColumnNames` 数组传入，PLC 结构体字段顺序须与列名顺序一致。两个方法都支持排序（`eOrderBy` / `eOrderType` 或 `sOrderByColumn`）、分页（`nStartIndex` / `nRecordCount`），以及通过 `nRecords` 属性获知过滤后的总匹配行数（用于 HMI 分页页码计算）。调用方周期调直到方法返回 TRUE，然后检查 `bError` 与 `ipTcResultEvent`。

**与 Evt 版差别**：仅输出接口名 `ipTcResultEvent`（类型 `I_TcResultEvent`）vs `ipTcResult`（类型 `I_TcMessage`）；方法签名 / 参数 / 状态机 / 错误码 / 排序枚举完全一致。新项目迁移只需改字段名 + 接口类型断言。

**为何保留**：Beckhoff 向后二进制兼容承诺——老 PLC 工程升级 TwinCAT Runtime 但不重新编译时本 FB 仍可用。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际成败。典型错误：表不存在、列不存在、cbData 不够、索引越界。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_PLCDBReadEvt`。
- **行为细节与 Evt 版完全一致**：可直接套用所有 §5 注意事项。
- **`pData` 数组必须够装**：`ARRAY[0..N] OF ST_StandardRecord` 须 ≥ nRecordCount。
- **分页用 nStartIndex + nRecordCount + nRecords**：与 Evt 版同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBRead.TcPOU`](../examples/P_Demo_FB_PLCDBRead.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 工程历史曲线模块用本 FB；新模块迁移到 `FB_PLCDBReadEvt`。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_PLCDBReadEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183259275.html
- **相关 FB / FC / DUT**：`FB_PLCDBReadEvt`（现代版）、`ST_StandardRecord`、`E_OrderColumn` / `E_OrderType`、`MAX_DBCOLUMNS`
