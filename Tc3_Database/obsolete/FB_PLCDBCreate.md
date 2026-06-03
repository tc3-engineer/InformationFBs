# FB_PLCDBCreate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183581835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBCreate.TcPOU`](../examples/P_Demo_FB_PLCDBCreate.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的物理建库 / 建表 FB（PDF §6.1.4.2.3）。两个方法：`Database` 创建数据库文件（仅文件型 DB），`Table` 在指定数据库里建表。行为与 `FB_PLCDBCreateEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_PLCDBCreateEvt`。

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

### Method: `Database`

```iecst
METHOD Database : BOOL
VAR_INPUT
    pDatabaseConfig: POINTER TO BYTE;
    cbDatabaseConfig: UDINT;
    bCreateXMLConfig: BOOL;
    pDBID: POINTER TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDatabaseConfig` | `POINTER TO BYTE` | 数据库配置结构体地址。 |
| `cbDatabaseConfig` | `UDINT` | 结构体 SIZEOF。 |
| `bCreateXMLConfig` | `BOOL` | TRUE = 同时注册到 XML。 |
| `pDBID` | `POINTER TO UDINT` | 返回的 hDBID。 |

### Method: `Table`

```iecst
METHOD Table : BOOL
VAR_INPUT
    hDBID : UDINT;
    sTableName : T_MaxString;
    pTableCfg : POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ColumnInfo;
    cbTableCfg : UDINT;
END_VAR
```

参数同 `FB_PLCDBCreateEvt.Table`。

## 3. 行为说明

与 `FB_PLCDBCreateEvt` 完全一致——`Database` 仅支持文件型 DB（SQL Compact / MS Access / MS SQL / XML），不支持 ODBC 远程；`Table` 用 `ST_ColumnInfo` 数组定义列。OEM 首次部署链路：`Database(bCreateXMLConfig := TRUE)` → 拿到 `hDBID` → `Table(hDBID, ...)` → `FB_PLCDBWrite.Write(...)`。

**与 Evt 版差别**：仅 `ipTcResultEvent : I_TcResultEvent` 接口名 / 类型不同。所有方法签名 / 参数 / 行为不变。新项目迁移只需把 FB 类型换为 Evt 版 + 改输出字段名。

**为何保留**：向后二进制兼容。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际成败。典型错误：文件已存在、路径无权限、表已存在、列类型不支持、hDBID 不存在。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_PLCDBCreateEvt`。
- **行为细节与 Evt 版完全一致**：可直接套用所有 §5 注意事项。
- **建表后必须用同一 hDBID 写入**：与 Evt 版同。
- **不能建 ODBC 远程数据库**：与 Evt 版同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBCreate.TcPOU`](../examples/P_Demo_FB_PLCDBCreate.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 项目用本 FB 装机自动建配方库 + 表。设备出货后保持二进制兼容性。
- **价值**：老工程二进制兼容；新项目应迁移到 `FB_PLCDBCreateEvt`。
- **替代方案对比**：
  - **`FB_PLCDBCreateEvt`**（推荐）：完全等价 + 现代 EventLogger。
  - **本 FB**：仅老工程兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183581835.html
- **相关 FB / FC / DUT**：`FB_PLCDBCreateEvt`（现代版）、`T_DBConfig_*`、`ST_ColumnInfo`、`E_ColumnType`、`MAX_DBCOLUMNS`、`I_TcResultEvent` vs `I_TcMessage`
