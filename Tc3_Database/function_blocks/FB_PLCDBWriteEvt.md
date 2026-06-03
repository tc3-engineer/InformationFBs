# FB_PLCDBWriteEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674379019.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBWriteEvt.TcPOU`](../examples/P_Demo_FB_PLCDBWriteEvt.TcPOU) |

---

## 1. 功能简述

把 PLC 变量值写入数据库表的功能块（PDF §6.1.1.2.5，PLC Expert mode）。三个方法：`Write` 把单个数值（地址 + 长度）按 Beckhoff 标准 4 列结构（ID / Timestamp / Name / Value）写入；`WriteBySymbol` 让 Server 从指定 ADS 设备读符号值再写库（支持跨设备）；`WriteStruct` 把任意自定义结构按 `pColumnNames` 列名数组写入自定义表。`Write` 与 `WriteBySymbol` 都支持 4 种 `E_WriteMode`：append（追加）、update（更新同 Name 行）、ring buffer by time（按时间窗滚动覆盖）、ring buffer by count（按行数滚动覆盖），让 PLC 端能直接控制日志保留策略。

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
| `bBusy` | `BOOL` | 任一方法运行中。 |
| `bError` | `BOOL` | 出错置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |

### Method: `Write`（标准 4 列表）

```iecst
METHOD Write : BOOL
VAR_INPUT
    hDBID: UDINT;
    sTableName: T_MaxString;
    pValue: POINTER TO BYTE;
    cbValue: UDINT;
    sDBSymbolName: T_MaxString;
    eDBWriteMode: E_WriteMode := E_WriteMode.eADS_TO_DB_Append;
    nRingBuffParameter: UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hDBID` | `UDINT` | - | 数据库 ID。 |
| `sTableName` | `T_MaxString` | - | 目标表名（标准 4 列）。 |
| `pValue` | `POINTER TO BYTE` | - | PLC 变量地址（`ADR(myValue)`），其值写到 Value 列。 |
| `cbValue` | `UDINT` | - | 变量字节大小（`SIZEOF(myValue)`）。 |
| `sDBSymbolName` | `T_MaxString` | - | 写入的 Name 列字符串。 |
| `eDBWriteMode` | `E_WriteMode` | `eADS_TO_DB_Append` | 写入模式（4 种，详见行为说明）。 |
| `nRingBuffParameter` | `UDINT` | - | RingBuffer 模式的参数：by time 时是秒数、by count 时是行数。 |

### Method: `WriteBySymbol`（Server 跨设备读符号再写）

签名：`METHOD WriteBySymbol : BOOL`，参数与说明：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| hDBID | UDINT | - | 数据库 ID。 |
| sTableName | T_MaxString | - | 目标表名（标准 4 列）。 |
| stADSDevice | ST_ADSDevice | - | 源 ADS 设备：NetID + Port + 读模式 + 超时。 |
| stSymbol | ST_Symbol | - | 源符号：DataType + Symbol Name + 长度。 |
| eDBWriteMode | E_WriteMode | `eADS_TO_DB_Append` | 同 `Write`。 |
| nRingBuffParameter | UDINT | - | 同 `Write`。 |

### Method: `WriteStruct`（自定义表结构）

签名：`METHOD WriteStruct : BOOL`，参数与说明：

| 参数 | 类型 | 说明 |
|---|---|---|
| hDBID | UDINT | 数据库 ID。 |
| sTableName | T_MaxString | 自定义表名。 |
| pRecord | POINTER TO BYTE | 自定义结构体地址；字段顺序须与 pColumnNames^ 顺序对应。 |
| cbRecord | UDINT | 结构体 SIZEOF。 |
| pColumnNames | POINTER TO ARRAY [0..MAX_DBCOLUMNS] OF STRING(50) | 列名数组地址，按列顺序填。 |
| cbColumnNames | UDINT | 列名数组 SIZEOF。 |

## 3. 行为说明

**Beckhoff 标准 4 列结构**：ID（LINT 主键自增）、Timestamp（DATE_AND_TIME 入库时由 Server 填）、Name（STRING(80)）、Value（LREAL 或按 `cbValue` 大小转换）。`Write` / `WriteBySymbol` 都写入此结构；表必须先用 `FB_PLCDBCreateEvt.Table` 按这 4 列建好（或用 AutoLog 默认表模板）。

**`E_WriteMode` 4 种模式**：
- `eADS_TO_DB_Append`（默认）：每次调用追加新行，DB 行数随时间无限增长；适合事件型日志且有外部清理任务。
- `eADS_TO_DB_Update`：按 Name 列查找已有行，存在则覆盖 Value + 更新 Timestamp，不存在则插新行；适合「最新值表」（一个信号只有一行最新值）。
- `eADS_TO_DB_RingBuff_Time`：按 `nRingBuffParameter` 秒数滚动——比该秒数早的同 Name 行被删除；适合「保留最近 N 秒」。
- `eADS_TO_DB_RingBuff_Count`：按 `nRingBuffParameter` 行数滚动——保留同 Name 的最近 N 行，更早的删；适合「保留最近 N 次」。

**`Write` vs `WriteBySymbol`**：`Write` 写本地 PLC 变量值；`WriteBySymbol` 让 Database Server 主动通过 ADS 去 `stADSDevice` 描述的设备（可能是别的 PLC、CX-Slave）读取 `stSymbol` 对应符号再写库。后者用于「Database Server 跨 PLC 收集数据」——一台 Server 服务整个生产线。

**`WriteStruct` 字段对齐**：`pRecord^` 的字段排布顺序必须与 `pColumnNames^[i]` 顺序一一对应。Server 按列名读 `pRecord` 起始 + 累积偏移的字段。如果 PLC 结构体里多了 padding 或字段顺序与列名不一致 → DB 收到错位数据。建议结构体定义紧贴列名顺序，且类型大小匹配（PLC `LREAL` ↔ DB `FLOAT(53)`）。

**`bExecute` 风格**：本 FB 用方法触发即执行，不是边沿。每个写入要由调用方代码确保只触发一次（用状态机或 R_TRIG），否则同一周期内多次调会得到多条重复行。

**Server 行为细节**：
- `RingBuff_Time/Count` 删除老行是在每次 `Write` 调用时同步做（不是后台任务），所以高频写入时会有额外的 DELETE 开销。
- `Update` 模式要求 Name 列建立索引才高效（否则全表扫描），OEM 部署建表时应加 `'INDEX IX_Name (sName)'` 之类索引。

**Tc3_EventLogger 错误**：`bError = TRUE` 时 `ipTcResult.RequestEventText` 取详细文本，常见：`'Cannot insert NULL'`、`'String too long'`、`'Constraint violation'`、`'Connection lost'`。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 表征实际成败。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| `bError`，事件含 `String too long` | `sDBSymbolName` 超过 Name 列长度（标准 80） | 缩短名字 |
| `bError`，事件含 `Cannot convert` | `cbValue` 与 Value 列类型不匹配 | 改 cbValue 或 Value 列类型 |
| `bError`，事件含 `Connection lost` | DB 连接断开 | 检查网络 / 重连 |
| `bError`，事件含 `Constraint violation` | 主键 / 唯一约束冲突 | Update 模式 / 改业务逻辑 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **`Write` 的 `cbValue` 必须等于 `SIZEOF(myValue)`**：Server 按字节数与 Value 列类型对照转换；不匹配会写入零或错值。
- **`sDBSymbolName` 超长被截断**：标准表 Name 列默认 `STRING(80)`，超出会被 Server 静默截断（部分 DB 会报错）；命名规范严格控制在 80 内。
- **`WriteBySymbol` 的 `stADSDevice` 必须可达**：Server 进程会通过 ADS 路由去读符号，失败会报超时。预先确认对方 NetID 在 AMS Router 列表里。
- **`WriteStruct` 的列名顺序与结构字段顺序**：必须一一对应；多个工程师协作时极易出错——建议在结构体字段注释里写「列号」备注。（工程经验补充）
- **Update 模式要 Name 列有索引**：否则每写一次全表扫描；100 万行表会让单次写入秒级。
- **RingBuffer 模式高频写入开销大**：每次 Write 都做删除；如果场景是每秒 100 次写，RingBuff_Count = 100，每次都 DELETE 旧行 → DB CPU 飙升。考虑改 Append + 后台清理任务。
- **`pValue` / `pRecord` 必须指向同作用域且持续有效的变量**：Server 异步读取，临时栈变量会随作用域消失。
- **WriteStruct 不支持 RingBuffer / Update 模式**：只能 Append；如需更新策略要自己在 Server 上做存储过程或 trigger。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBWriteEvt.TcPOU`](../examples/P_Demo_FB_PLCDBWriteEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机每个生产周期把 5 个关键工艺参数（温度 / 压力 / 周期时间 / 注射时间 / 保压时间）作为一条自定义结构记录写入 `tbl_CycleHistory`，OEE 仪表盘按 ID 倒序读最新 100 条做趋势曲线。同时把单条「机器健康度」实时值用 `Write(eMode := Update)` 写入「最新值表」让 SCADA 实时拉取。
- **价值**：周期日志记录 + 最新值缓存全在一个 FB 完成；3 种模式（Append / Update / RingBuffer）覆盖了 90% 工业日志场景；Tc3 EventLogger 错误诊断让生产环境出问题能直接定位。
- **替代方案对比**：
  - **`FB_DBWrite`（Tc2_Database）**：TC2 版本等价，仅 nErrId 报错。
  - **AutoLog（`FB_PLCDBAutoLogEvt`）**：高频周期采样首选；本 FB 适合事件型 / 业务驱动型写入。
  - **`FB_PLCDBCmdEvt`**：自由 SQL INSERT，灵活但要拼 SQL 字符串。本 FB 用方法签名约束安全。
  - **本 FB**：TC3 现代版（带 EventLogger），新项目首选；obsolete `FB_PLCDBWrite` 仅老项目兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674379019.html
- **相关 FB / FC / DUT**：`ST_StandardRecord`（§6.1.2.4.12）、`ST_ADSDevice` / `ST_Symbol`（§6.1.2.4.8 / §6.1.2.4.14）、`E_WriteMode`（§6.1.2.4.7）、`E_ADSRdWrtMode` / `E_PLCDataType`、`FB_PLCDBReadEvt`（读侧）、`FB_PLCDBCreateEvt`（建表）、obsolete `FB_PLCDBWrite`
