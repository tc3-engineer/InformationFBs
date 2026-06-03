# FB_DBRead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108025867.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRead.TcPOU`](../examples/P_Demo_FB_DBRead.TcPOU) |

---

## 1. 功能简述

FB_DBRead 从数据库的"`Name`/`Value`"模式表中按变量名 `sDBVarName` 读出对应的 `Value` 值，写入调用方提供的目标缓冲。本 FB 是 `FB_DBWrite` 的对偶——后者按变量名写值，本 FB 按变量名读值。如果同名变量在表中有多行，**只返回第一条**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId;
    hDBID           : DINT;
    sDBVarName      : STRING(80);
    cbReadLen       : UDINT;
    pDestAddr       : DWORD;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `DINT` | - | 数据库连接 ID（`DINT` 类型，需 `UDINT_TO_DINT` 转换 `FB_DBConnectionAdd` 返回的 `UDINT`）。 |
| `sDBVarName` | `STRING(80)` | - | 数据库表 `Name` 列中要查找的变量名。 |
| `cbReadLen` | `UDINT` | - | 目标缓冲大小（字节），`SIZEOF(target)`。 |
| `pDestAddr` | `DWORD` | - | 目标缓冲地址，`ADR(target)`。PDF 用 `DWORD` 但语义是指针。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次读取。 |
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
| `bError` | `BOOL` | TRUE 表示读取失败（含变量未找到）。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 在该连接的目标表里执行 `SELECT TOP 1 Value FROM <table> WHERE Name = <sDBVarName>`（或等效），把 `Value` 列内容序列化后写到 `pDestAddr` 指向的缓冲。

**表结构假设**：本 FB 假定数据库的目标表是"Name/Value"模式——至少含 `Name`（变量名列）和 `Value`（值列，按 `eDBValueType` 是 Double 或 Bytes 序列化）。如果表不是这种模式（如多列业务表），本 FB 不适用，应用 `FB_DBRecordSelect_EX` 或 `FB_DBRecordArraySelect`。

**值类型与缓冲匹配**：调用方必须知道存的是 `BOOL` / `INT` / `LREAL` / 结构体 等，传入大小匹配的缓冲。本 FB 不做类型检查，按 `cbReadLen` 字节复制——错了缓冲会写错相邻变量。

**多条同名记录**：返回第一条。如果业务有同名多版本（不同时间戳），本 FB 不适合——要用 SQL `ORDER BY Timestamp DESC LIMIT 1`，得走 `FB_DBRecordSelect_EX`。

**`hDBID` 是 `DINT`**：与 `FB_DBConnectionOpen` 同——`UDINT_TO_DINT()` 转换。

**`pDestAddr` 是 `DWORD` 但语义是指针**：32 位 TwinCAT 2/3 上 `DWORD` 与 `POINTER` 大小一致。64 位 TwinCAT 3 上要小心——PDF 是 TS6420（TwinCAT 2），描述基于 32 位假设。新 TC3 工程建议改用 `PVOID` 包装；但本 FB 接口签名固定为 `DWORD`，调用方用 `ADR(buf)` 显式拿地址给到。

**`sDBVarName` 长度限制 80**：PDF 明确 `STRING(80)`，超长截断。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42S22` | 变量未找到 / 列不存在 | 检查表是否有 Name 列 / sDBVarName 是否存在 |
| `0x0` | `42S02` | 表不存在 | 检查目标表 |
| `0x0` | `42501` | 权限不足 | DB 用户需 SELECT 权限 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |
| `0x705` | `00000` | cbReadLen 不匹配 Value 字段大小 | 检查 SIZEOF(target) |

## 5. 使用注意 / 常见坑

- **目标缓冲大小必须匹配**：`cbReadLen := SIZEOF(target)` 不要手填常量。
- **多条同名只返回第一条**：业务上同名多版本要用 `FB_DBRecordSelect_EX` 加 `ORDER BY`。
- **`eDBValueType = Double` vs `Bytes`**：连接 Add 时选 `Double` 的库只能存数值（Bool/Int/Real/LReal），Bytes 才能存结构体 / 字符串。读时类型必须匹配。
- **`hDBID` 类型转换易忘**：编译时不会警告 `UDINT → DINT` 隐式转换的潜在丢精度（值永远小，实际不丢）。
- **`sDBVarName` 大小写敏感**：取决于 DB 排序规则（Collation）。SQL Server 默认 case-insensitive；MySQL utf8_general_ci 是 ci；PostgreSQL 默认 case-sensitive。跨 DB 项目用统一命名风格。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRead.TcPOU`](../examples/P_Demo_FB_DBRead.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：PLC 启动时要从本地 SQL Compact 库里读"上次班次的最终累计产量"作为当前班次的起点——这条数据是上次班次结束时 `FB_DBWrite` 写入的 `Name = 'shift_total'` / `Value = 1234.0` 一条。本 FB 调一次按变量名读到 LREAL 变量。
- **价值**：替代"PLC 自己用 retain 变量保存"——retain 在 PLC 重装 / SD 卡换新时会丢；DB 是持久化的，更稳。同时所有班次数据可在 DB 里查历史。
- **替代方案对比**：
  - **PLC retain 变量**：简单，但不持久化（SD 卡损坏 / 重装 PLC 丢失）。
  - **`FB_FileRead` + 文本配置文件**：通用，但要自己解析；变量名 / 值结构都得手写代码。
  - **`FB_DBRecordSelect_EX`**：多列结构化数据要用这个；本 FB 只适合 Name/Value 简单模式。
  - **本 FB**：Name/Value 模式下的最简读取入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108025867.html
- **相关 FB / FC**：`FB_DBWrite`（对偶写入）、`FB_DBRecordSelect_EX`（多列查询）、`FB_DBRecordArraySelect`（批量查询）、`ST_DBSQLError`
