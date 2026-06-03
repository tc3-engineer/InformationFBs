# FB_DBRecordSelect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108041099.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRecordSelect.TcPOU`](../examples/P_Demo_FB_DBRecordSelect.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃（Obsolete，PDF §7.1.20.3）**。FB_DBRecordSelect 是 SELECT 单条记录的早期版本——`sSelectCmd` 用 `T_MaxString`（≤255 字符），读到的单行记录写入指定结构体地址。**不支持 ASCII 文件**。新代码应改用 `FB_DBRecordArraySelect`（多行 + 10000 字符 SQL）或 `FB_DBStoredProceduresRecordArray`（参数化）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetID;
    hDBID           : UDINT;
    sSelectCmd      : T_MaxString;
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
| `sSelectCmd` | `T_MaxString` | - | SELECT SQL 命令（≤255 字符）。 |
| `nRecordIndex` | `UDINT` | - | 要读取的记录索引（0 开始）。从 SELECT 结果集里第几条。 |
| `cbRecordSize` | `UDINT` | - | 记录结构体大小，`SIZEOF(record)`。 |
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
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |
| `nRecords` | `UDINT` | 实际返回的记录数（本 FB 总是 0 或 1）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃原因**：
1. SQL 长度限 255——多列结构 + ORDER BY + WHERE 容易超。
2. 单条返回——业务通常需要多条，循环调本 FB 效率低。
3. 已被 `FB_DBRecordSelect_EX`（也是 obsolete §7.1.20.4，SQL 长 10000）和 `FB_DBRecordArraySelect`（多行 + 10000）覆盖。

**调用方式（兼容）**：周期调用直到 `bBusy` 复位。SELECT 结果集中第 `nRecordIndex` 条按 PLC 端结构体二进制布局写到 `pDestAddr`。

**PLC 端结构体匹配 SELECT 列序**：与 `FB_DBRecordArraySelect` 同要求。

**ARM 处理器需 dummy 字段**：与 `FB_DBRecordArraySelect` 同——PDF §7.1.20.3 给的例子里 ARM 版结构体把 Value 放到 Name 前面 + 加 Dummy:BYTE。

**`T_ULARGE_INTEGER` 来自 TcUtilities.lib**：PDF 明确——用于映射 SQL 的 BIGINT；TC3 改用 `ULINT`。

**`pDestAddr` 是 `DWORD`**：32 位指针；64 位 TC3 需手动用 `ADR()` 得到正确地址值。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错 / 被截断 | 用 EX 版 |
| `0x0` | `42S02` | 表不存在 | 检查 FROM |
| `0x705` | `00000` | cbRecordSize 不匹配 | 检查结构体 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **255 字符 SQL 限制**：与 `FB_DBRecordInsert` 同样的根本问题。
- **`nRecordIndex` 越界返回空**：`nRecords = 0` 表示该索引位置无数据。
- **不支持 ASCII**：PDF 明确说明。
- **新代码不要用本 FB**：用 `FB_DBRecordArraySelect`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRecordSelect.TcPOU`](../examples/P_Demo_FB_DBRecordSelect.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护老代码——某 OEM 用本 FB 循环读取 10 条历史日志，每次改 `nRecordIndex` 跑一次。改造时为不破坏既有逻辑保留。
- **价值（历史）**：早期 TC2 时代唯一的 SELECT 入口。
- **替代方案对比**：
  - **`FB_DBRecordArraySelect`**：✅ 新代码，多条 + 长 SQL。
  - **`FB_DBStoredProceduresRecordArray`**：参数化 + 多条。
  - **本 FB**：仅维护老代码。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.20.3（Obsolete）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108041099.html
- **相关 FB / FC**：`FB_DBRecordSelect_EX`（obsolete 也是 EX 长 SQL 单行版）、`FB_DBRecordArraySelect`（新代码推荐多行版）
