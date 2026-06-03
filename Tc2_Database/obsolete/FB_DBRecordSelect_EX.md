# FB_DBRecordSelect_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108042635.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRecordSelect_EX.TcPOU`](../examples/P_Demo_FB_DBRecordSelect_EX.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃（Obsolete，PDF §7.1.20.4）**。FB_DBRecordSelect_EX 是 `FB_DBRecordSelect` 的"长 SQL"扩展版（SQL 通过 `pCmdAddr + cbCmdSize` 指针方式传入，长度可达 10000 字符），但仍**只读取单条记录**。**不支持 ASCII 文件**。新代码应改用 `FB_DBRecordArraySelect`——后者同样支持 10000 字符 SQL 且能一次性返回多条。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetID;
    hDBID           : UDINT;
    cbCmdSize       : UDINT;
    pCmdAddr        : UDINT;
    nRecordIndex    : UDINT;
    cbRecordSize    : UDINT;
    pDestAddr       : DWORD;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `cbCmdSize` | `UDINT` | - | SQL 命令字节大小，`SIZEOF(sCmd)`。 |
| `pCmdAddr` | `UDINT` | - | SQL 命令缓冲地址，`ADR(sCmd)`。 |
| `nRecordIndex` | `UDINT` | - | 读取的记录索引（0 开始）。 |
| `cbRecordSize` | `UDINT` | - | 目标结构体大小，`SIZEOF(record)`。 |
| `pDestAddr` | `DWORD` | - | 目标结构体地址，`ADR(record)`。 |
| `bExecute` | `BOOL` | - | 上升沿触发。 |
| `tTimeout` | `TIME` | - | ADS 超时。 |

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
| `bError` | `BOOL` | TRUE 表示查询失败。 |
| `nErrID` | `UDINT` | ADS 错误码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |
| `nRecords` | `UDINT` | 实际返回记录数（0 或 1）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃原因**：单条返回 + 不支持 ASCII；功能完全被 `FB_DBRecordArraySelect`（多条 + 10000 SQL + 同样不支持 ASCII）覆盖。

**与 obsolete `FB_DBRecordSelect` 的差异**：本 EX 版扩展了 SQL 长度（10000 字符）。SQL 通过 `pCmdAddr` 而不是 `sSelectCmd`。

**调用方式（兼容）**：周期调用直到 `bBusy` 复位。结果集第 `nRecordIndex` 条按结构体二进制布局写到 `pDestAddr`。

**与 `FB_DBRecordArraySelect` 对比**：
- 都用 10000 SQL；
- 本 FB 只取 1 条，`FB_DBRecordArraySelect` 取多条；
- 本 FB 多了 `nRecordIndex` 单条索引，Array 版用 `nStartIndex + nRecordCount` 范围。

**结构体布局要求与 `FB_DBRecordArraySelect` 同**：列序、ARM 对齐特殊处理一致。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错 | 检查 SELECT |
| `0x0` | `42S02` | 表不存在 | 检查 FROM |
| `0x705` | `00000` | cbRecordSize 不匹配 | 检查结构体 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **新代码用 `FB_DBRecordArraySelect`**：多条批量取，性能更好。
- **`nRecordIndex` 不是 SQL OFFSET**：Server 拿完整结果集后取第 N 条；大结果集慢。要在 SQL 里用 ORDER BY + OFFSET/LIMIT 才高效。
- **不支持 ASCII**：与 obsolete `FB_DBRecordSelect` 同。
- **ARM 对齐**：与 `FB_DBRecordArraySelect` 同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRecordSelect_EX.TcPOU`](../examples/P_Demo_FB_DBRecordSelect_EX.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护中期老代码（2017-2019 年），用本 FB 跑长 SQL 单条查询。新代码改 `FB_DBRecordArraySelect` 直接拿多条。
- **价值（历史）**：长 SQL 单条查询的中期 TC2 工具。
- **替代方案对比**：
  - **`FB_DBRecordArraySelect`**：✅ 新代码必走，多条 + 长 SQL。
  - **本 FB**：仅兼容老代码。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.20.4（Obsolete）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108042635.html
- **相关 FB / FC**：`FB_DBRecordSelect`（更早期的 obsolete 短 SQL 版本）、`FB_DBRecordArraySelect`（新代码推荐）
