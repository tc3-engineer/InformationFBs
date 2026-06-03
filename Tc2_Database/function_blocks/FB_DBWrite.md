# FB_DBWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108027403.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBWrite.TcPOU`](../examples/P_Demo_FB_DBWrite.TcPOU) |

---

## 1. 功能简述

FB_DBWrite 把指定 ADS 变量的当前值写入数据库的"`Timestamp`/`Name`/`Value`"模式表。值由 Database Server 后台从被监视的 ADS 设备（`hAdsID` 索引）按变量名读取，再按 `eDBWriteMode` 写入数据库（`hDBID` 索引）的目标表。支持 4 种写入模式：Append（追加）、Update（更新）、RingBuffer_Time（环形按时间截断）、RingBuffer_Count（环形按条数截断）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID              : T_AmsNetID;
    hDBID               : UDINT;
    hAdsID              : UDINT;
    sVarName            : T_MaxString;
    nIGroup             : UDINT;
    nIOffset            : UDINT;
    nVarSize            : UDINT;
    sVarType            : T_MaxString;
    sDBVarName          : T_MaxString;
    eDBWriteMode        : E_DBWriteModes;
    tRingBufferTime     : TIME;
    nRingBufferCount    : UDINT;
    bExecute            : BOOL;
    tTimeout            : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标 AMS Net ID（Database Server 所在）。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `hAdsID` | `UDINT` | - | ADS 设备 ID（来源变量所在）。 |
| `sVarName` | `T_MaxString` | - | 要读取的 ADS 变量名（如 `'MAIN.fProductionCount'`）。 |
| `nIGroup` | `UDINT` | - | **仅 BC9000 用**：变量的 ADS Index Group。普通 PLC 填 0。 |
| `nIOffset` | `UDINT` | - | **仅 BC9000 用**：变量的 ADS Index Offset。普通 PLC 填 0。 |
| `nVarSize` | `UDINT` | - | **仅 BC9000 用**：变量字节数。普通 PLC 填 0。 |
| `sVarType` | `T_MaxString` | - | **仅 BC9000 用**：变量类型字串，可选 `'BOOL'` / `'LREAL'` / `'REAL'` / `'INT16'` / `'DINT'` / `'USINT'` / `'BYTE'` / `'UDINT'` / `'DWORD'` / `'UINT16'` / `'WORD'` / `'SINT'`。普通 PLC 填 `''`。 |
| `sDBVarName` | `T_MaxString` | - | 写入数据库时 `Name` 列的值（用于后续按变量名查 / 多变量同表）。 |
| `eDBWriteMode` | `E_DBWriteModes` | - | 写入模式：`eDBWriteMode_Update` / `eDBWriteMode_Append` / `eDBWriteMode_RingBuffer_Time` / `eDBWriteMode_RingBuffer_Count`。 |
| `tRingBufferTime` | `TIME` | - | 仅 RingBuffer_Time 模式：表中数据保留的最大时长，超过则删旧。 |
| `nRingBufferCount` | `UDINT` | - | 仅 RingBuffer_Count 模式：表中数据保留的最大条数，超过则删旧。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次写入。 |
| `tTimeout` | `TIME` | - | ADS 超时，`T#15S` 通常够。 |

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
| `bError` | `BOOL` | TRUE 表示写入失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 做三步：(1) 从 `hAdsID` 对应的 ADS 设备按 `sVarName` 读取变量当前值；(2) 把读到的值按 `eDBWriteMode` 写入 `hDBID` 对应数据库的目标表（XML Symbolgroup 配置中预定义的表名）；(3) 返回 `bBusy = FALSE` + 错误码。

**4 种写入模式（`E_DBWriteModes`）**：
- **`eDBWriteMode_Update` (0)**：UPDATE 已存在的 `Name = sDBVarName` 行的 `Value` 与 `Timestamp`；不存在则 INSERT。"最新值"语义——只看当前值，无历史。
- **`eDBWriteMode_Append` (1)**：INSERT 新行，保留所有历史；表会无限增长。
- **`eDBWriteMode_RingBuffer_Time` (2)**：INSERT 新行；同时删除 `Timestamp < (NOW - tRingBufferTime)` 的旧行——限制数据年龄。
- **`eDBWriteMode_RingBuffer_Count` (3)**：INSERT 新行；同时按 `Name` 维度限制保留 `nRingBufferCount` 条最近记录——限制每变量的条数。

**BC9000 兼容字段**：`nIGroup` / `nIOffset` / `nVarSize` / `sVarType` 是给老式 BC9000（无符号表）控制器用的——这种控制器没有变量名解析能力，需要 PLC 端手填 ADS 三元组（group / offset / size）和数据类型字串。普通 PLC 全填 0 / `''` 让 Server 通过符号查询解析。

**Timestamp 列由 Server 填**：Server 写入时自动在 `Timestamp` 列填**当前 Server 时间**——不是 PLC 时间也不是变量被读取的时间。在跨时区或时钟不同步的环境下要注意。

**`sDBVarName` 不必与 `sVarName` 相同**：PLC 端变量 `MAIN.fProductionCount` 可以用更友好的 `'production_count'` 存数据库。

**性能上限**：单 FB_DBWrite 调用 PLC 端 200~500 ms（含 ADS 来回 + DB 写入）。高吞吐场景建议用 `FB_DBCyclicRdWrt` + XML Symbolgroup 替代。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42S22` | DB 表中没有 Name / Value / Timestamp 列 | 用 `FB_DBTableCreate` 重建表 |
| `0x0` | `42501` | DB 用户无 INSERT / UPDATE 权限 | 给用户 GRANT |
| `0x710` | - | ADS 变量未找到 | 检查 `sVarName` 拼写 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |
| `0x70xxx` | DB 特有 | DB 服务器错误 | 看 sSQLState 详细 |

## 5. 使用注意 / 常见坑

- **表结构必须含 `Timestamp / Name / Value` 三列**：少任一列得 `42S22`。`FB_DBTableCreate` 默认建出来的就符合。
- **Timestamp 是 Server 时间**：跨时区 / NTP 不同步会导致看似数据时间错乱。建议 Server 与 PLC 都用 NTP 同步。
- **`eDBWriteMode_Update` 不保留历史**：选错模式后再切回 Append 也补不回历史。OEM 设备首次部署时多次确认模式。
- **RingBuffer 模式删旧靠 SQL DELETE**：高频写入下 DELETE 频次也高，DB 性能会下降；MS SQL 建议在 Timestamp 列建索引。（工程经验补充）
- **`hAdsID` 必须先用 `FB_AdsDeviceConnectionAdd` 注册**：直接写远端 PLC 而 `hAdsID` 未注册会得到 `0x710`。
- **`sVarName` 大小写**：TwinCAT PLC 通常 case-insensitive；引用结构体字段 `MAIN.stData.fValue` 要按声明大小写写。
- **不要在 PLC 循环里高频触发**：本 FB 单次 200~500 ms；要做高频日志用 `FB_DBCyclicRdWrt`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBWrite.TcPOU`](../examples/P_Demo_FB_DBWrite.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：每批次生产结束时把"班次累计产量"写入本地 SQL Compact——`eDBWriteMode_Update` 模式（一个变量名只对应一条记录，更新最新值），下次开机用 `FB_DBRead` 按 Name 读回作为新班次起点。
- **价值**：相比 PLC retain 变量——DB 数据可异机房备份、可在 HMI 历史报表显示、可被外部 BI 工具查询。
- **替代方案对比**：
  - **PLC retain 变量**：不持久（SD 卡坏 / 重装丢）；不支持历史趋势；HMI 也得自己写。
  - **`FB_DBRecordInsert_EX` SQL 直写**：灵活但要写完整 INSERT 语句；本 FB 简单很多。
  - **`FB_DBCyclicRdWrt` + Symbolgroup**：高频日志场景；事件型场景用本 FB 更简单。
  - **本 FB**：事件型 / 中低频日志的最佳入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108027403.html
- **相关 FB / FC**：`FB_DBRead`（对偶读）、`FB_DBCyclicRdWrt`（高频版）、`FB_AdsDeviceConnectionAdd`（注册 hAdsID）、`E_DBWriteModes`（写入模式枚举）、`FB_DBTableCreate`（建标准表）
