# Constants

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108063883.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_Constants.TcPOU`](../examples/P_Demo_Constants.TcPOU) |

---

## 1. 功能简述

Tc3_Database 库的全部全局常量（PDF §6.1.3.1 节，`VAR_GLOBAL CONSTANT GVL`）。包含 1 个 ADS 端口常量（`AMSPORT_DBSRV` = 21372，TwinCAT Database Server 的 ADS 端口号）+ 5 个数组上限常量（`MAX_DBCONNECTIONS` / `MAX_DBCOLUMNS` / `MAX_SPPARAMETER` / `MAX_CONFIGURATIONS` / `MAX_RECORDS` 均为 255）。这些常量在库内 FB 的方法签名里被广泛引用——例如 `FB_PLCDBReadEvt.ReadStruct` 的 `pColumnNames : POINTER TO ARRAY [0..MAX_DBCOLUMNS] OF STRING(50)`、`FB_ConfigTcDBSrvEvt.Read` 的 `pDBConfig : POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_ConfigDB` 等。PLC 端声明数组时直接用这些常量保证与 Server 端接收上限一致。

## 2. 接口定义

### VAR_GLOBAL CONSTANT GVL

```iecst
VAR_GLOBAL CONSTANT GVL
AMSPORT_DBSRV : UINT := 21372;
MAX_DBCONNECTIONS : UDINT := 255;
MAX_DBCOLUMNS : UDINT := 255;
MAX_SPPARAMETER : UDINT := 255;
MAX_CONFIGURATIONS : UDINT := 255;
MAX_RECORDS : UDINT := 255;
END_VAR
```

| 名称 | 类型 | 值 | 说明 |
|---|---|---|---|
| `AMSPORT_DBSRV` | `UINT` | `21372` | TwinCAT Database Server ADS 端口号（十进制 21372，十六进制 0x537C）。用作 ADS 调用的目标 Port。 |
| `MAX_DBCONNECTIONS` | `UDINT` | `255` | 数据库连接配置数组上限。系统最多支持 255 个并发数据库连接。 |
| `MAX_DBCOLUMNS` | `UDINT` | `255` | 表列定义 / 列名数组上限。建表 / 读 / 写时列数组最多 255 列。 |
| `MAX_SPPARAMETER` | `UDINT` | `255` | 存储过程参数数组上限。单个存储过程最多 255 个参数（实际通常 < 10）。 |
| `MAX_CONFIGURATIONS` | `UDINT` | `255` | 配置条目数组上限。`FB_ConfigTcDBSrvEvt.Read` 等返回的数据库配置 / AutoLog 组配置数组容量。 |
| `MAX_RECORDS` | `UDINT` | `255` | 单次读 / 写记录数上限（影响 `FB_PLCDB*Evt` 和 `FB_SQL*Evt` 的某些操作）。 |

### VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT

GVL 没有这些字段——全局常量声明。

## 3. 行为说明

**作为数组维度声明的标准做法**：本库所有需要数组的 FB 方法都用这些常量做维度，例如：
- `FB_PLCDBReadEvt.ReadStruct` 的 `pColumnNames : POINTER TO ARRAY [0..MAX_DBCOLUMNS] OF STRING(50)`
- `FB_ConfigTcDBSrvEvt.Read` 的 `pDBConfig : POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_ConfigDB`
- `FB_PLCDBCmdEvt.Execute` 的 `pParameter : POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ExpParameter`
- `FB_SQLDatabaseEvt.CreateSP` 的 `pParameterInfo : POINTER TO ARRAY [0..MAX_SPPARAMETER] OF ST_SQLSPParameter`
- `FB_PLCDBAutoLogEvt.Status` 的 `pAutoLogGrpStatus : POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_AutoLogGrpStatus`

PLC 端声明匹配数组时用这些常量保证与 Server 端接收上限一致——例如 `aColumns : ARRAY[0..MAX_DBCOLUMNS] OF STRING(50);`。如果用别的常量（如 `[0..50]`）虽然能编译但与 Server 接收上限不对齐，导致空槽 / 越界风险。

**`AMSPORT_DBSRV` 的使用**：本库内 FB 都通过 `sNetID + tTimeout` 抽象访问 Server，不直接暴露端口号。但当用户写自定义 ADS 调用（`ADSREADREQ` / `ADSWRITEREQ` 等底层 FB）跟 Database Server 通讯时，目标 Port 必须填本常量。这是 Beckhoff 官方为 TwinCAT Database Server 注册的固定端口号。

**为何全部上限是 255**：与 BYTE 范围一致（255 = 8 位无符号最大），是 PLC 与 Server 端通讯协议的字段宽度限制。如要更大数组，必须批量分批 — 例如要写 1000 列必须分 4 次写每次 ≤ 255 列（实际生产场景不会出现这种需求）。

**版本稳定性**：这些常量值自 TF6420 v1.0 起保持不变到 1.14.1；Beckhoff 公开承诺二进制兼容，不会改值。

## 4. 错误码 / 返回值

常量本身无返回值 / 错误码。引用错误（数组维度对不齐 / 端口号写错）是 PLC 编译期错误。

## 5. 使用注意 / 常见坑

- **优先用常量声明数组**：`ARRAY[0..MAX_DBCOLUMNS] OF ...` 而非 `ARRAY[0..254] OF ...`。前者随库升级自动跟进（虽然概率极低 Beckhoff 也不会改），后者硬编码不直观。
- **`AMSPORT_DBSRV` 在配置工具中可见**：TwinCAT XAE 路由表里 TwinCAT Database Server 列在端口 21372。验证 Server 是否在运行可以用 `netstat -an | findstr 21372`。（工程经验补充）
- **`MAX_RECORDS` 影响 nRecordCount 上限**：单次 Read / Write 上限 255 行；超出需分页。
- **常量类型不要篡改**：所有上限是 `UDINT`，但 `AMSPORT_DBSRV` 是 `UINT`（与端口号 16 位范围一致）。
- **GVL 名 `GVL`**：PDF 声明里 `VAR_GLOBAL CONSTANT GVL` 的 `GVL` 是命名空间名。引用时一般直接用常量名（库引用后自动可见），无需 `GVL.AMSPORT_DBSRV` 这种限定路径。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Constants.TcPOU`](../examples/P_Demo_Constants.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：OEM 设备的数据库子系统初始化代码：用 `MAX_CONFIGURATIONS` 声明配置数组、`MAX_DBCOLUMNS` 声明列定义数组、`MAX_SPPARAMETER` 声明存储过程参数数组。同时若要写直接 ADS 通讯（如旁路本库做特定优化），目标 Port 用 `AMSPORT_DBSRV`。
- **价值**：常量名表达意图（"max database columns" 比 "255" 清楚）；与 Server 端约定一致避免空槽 / 越界；端口号集中维护避免 magic number。
- **替代方案对比**：
  - **硬编码数字**：可行但意图不清晰；Beckhoff 改值（极不可能）后旧代码不跟进。
  - **本 GVL（推荐）**：库内规范用法；最佳工程实践。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108063883.html
- **相关 FB / FC / DUT**：所有 `FB_PLCDB*Evt` / `FB_SQL*Evt` / `FB_NoSQL*Evt` 都引用这些常量、`stLibVersion_TC3_Database_Server`（库版本常量，等价 Tc2 的 `F_GetVersionTcDatabase`）
