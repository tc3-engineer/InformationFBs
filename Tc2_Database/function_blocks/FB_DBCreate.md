# FB_DBCreate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108021259.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBCreate.TcPOU`](../examples/P_Demo_FB_DBCreate.TcPOU) |

---

## 1. 功能简述

FB_DBCreate 在线**物理创建一个新数据库文件**（MS SQL Compact `.sdf` / MS Access `.mdb` / XML / 或一个空 MS SQL 实例）。本 FB 仅创建本地文件型 DB 与 MS SQL 数据库；**不支持** DB2 / Oracle / MySQL / PostgreSQL / InterBase / Firebird（这些类型必须事先在 DB 服务器上由 DBA 创建）。本 FB 也**不会覆盖**同名已存在的文件，重复创建会报错。ASCII 文件不需要本 FB 创建，首次写入时自动建。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetID;
    sPathName   : T_MaxString;
    sDBName     : T_MaxString;
    eDBType     : E_DBTypes;
    sSystemDB   : T_MaxString;
    sUserId     : T_MaxString;
    sPassword   : T_MaxString;
    bExecute    : BOOL;
    tTimeout    : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | Database Server 所在目标 AMS Net ID。本机 = `''`。 |
| `sPathName` | `T_MaxString` | - | 新数据库的存放目录绝对路径（如 `'C:\TwinCAT\TcDatabaseSrv\Samples\'`）。 |
| `sDBName` | `T_MaxString` | - | 要创建的数据库文件名（含扩展名，如 `'NewLog.sdf'` / `'NewLog.mdb'`）。 |
| `eDBType` | `E_DBTypes` | - | 要创建的数据库类型枚举：`eDBType_Mobile_Server` / `eDBType_Access` / `eDBType_Sequal_Server` / `eDBType_XML`（不支持）。其它 ODBC 类型不可用本 FB 创建。 |
| `sSystemDB` | `T_MaxString` | - | 仅 Access 用：MDW（工作组安全文件）路径。其它类型填空串。 |
| `sUserId` | `T_MaxString` | - | 登录用户名（创建带认证的 DB 时用）。 |
| `sPassword` | `T_MaxString` | - | 登录密码。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次创建。 |
| `tTimeout` | `TIME` | - | ADS 超时。本地文件型 `T#15S`；MS SQL 远端建议 `T#60S`（CREATE DATABASE 可能慢）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示创建失败。 |
| `nErrID` | `UDINT` | ADS 错误码（PDF §9.1.1）。`0x70F` 文件已存在；`0x70C` 路径不存在；`0x701` Service 不支持（DB 类型不支持创建）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 触发底层 OLE DB Provider 或 SQL 命令执行物理创建。

**只创建文件，不注册到 XML 配置**：本 FB 创建完后数据库**还不在 Server 配置中**——必须再调一次 `FB_DBConnectionAdd` 把新文件加入 XML，才能用 `FB_DBWrite` / `FB_DBRead`。Beckhoff PDF 在本节末尾的 Note 明确指出："If the newly created databases are to be used by the TwinCAT Database Server, the connection data have to be written to the XML configuration file with the aid of the function block FB_DBConnectionAdd."

**完整流程**：
1. `FB_DBCreate`（物理创建文件）
2. `FB_DBConnectionAdd`（注册到 XML，拿 `hDBID`）
3. `FB_DBTableCreate`（在数据库里建表）
4. `FB_DBWrite` / `FB_DBRead`（业务读写）

**不支持的 DB 类型**：DB2 / Oracle / MySQL / PostgreSQL / InterBase / Firebird——这些必须事先由 DBA 在 DB 服务器上用 `CREATE DATABASE` SQL 命令创建好，PLC 只 Add 连接到 XML 即可。

**XML 数据库的特殊性**：`eDBType_XML` 在 PDF §7.3.7 的枚举里标 `(*not supported*)`，即本 FB 不应用于创建 XML 数据库。

**ASCII 文件**：不需要本 FB，第一次 `FB_DBWrite` 调用时 Server 会自动建文件。但条目仍要 `FB_DBConnectionAdd` 注册。

**`sPathName` 必须存在**：父目录需事先存在（PLC 不会自动 `mkdir`）。本机用 `C:\TwinCAT\TcDatabaseSrv\Samples\` 是 Beckhoff 推荐位置。

## 4. 错误码 / 返回值

通过 `bError` + `nErrID` 输出：

| 错误号 | 含义 | 排查 |
|---|---|---|
| `0x6` | Server 服务未启动 | 启动服务 |
| `0x70C` | 路径不存在 / 找不到 | 创建父目录 |
| `0x70F` | 文件已存在 | 删除老文件或换名 |
| `0x701` | Service 不支持（DB 类型本 FB 不支持） | DB2/Oracle/MySQL 等用 DBA 创建 |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **创建完不能立刻用**：还需 `FB_DBConnectionAdd` 注册到 XML、`FB_DBTableCreate` 建表才能用 `FB_DBWrite`。整个初始化流程比直接连已有 DB 复杂。
- **同名文件不会覆盖**：重复创建得 `0x70F`。OEM 设备每次启动都尝试创建是常见错误用法——应当先 `FB_GetDBXMLConfig` 查询，已注册就跳过 Create。
- **MS SQL Server 创建**：需 Server 上的 sysadmin 权限（`sUserId` 必须是 `sa` 或同等）。普通用户没有 `CREATE DATABASE` 权限。
- **`sPathName` 末尾要带分隔符**：路径 `'C:\TwinCAT\TcDatabaseSrv\Samples\'`（结尾的 `\`），不带可能被解释为文件名一部分。（工程经验补充）
- **SQL Compact `.sdf` 单文件限制**：默认最大 4 GB；高吞吐场景需用 MS SQL Server 而非 Compact。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBCreate.TcPOU`](../examples/P_Demo_FB_DBCreate.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：OEM 设备首次部署到客户车间——PLC 启动后自检发现本地没有日志数据库，自动调用本 FB 创建一个 `SiteLogs.sdf`（SQL Compact），再 Add + 建表 + 开始记录，整套流程对终端客户透明。
- **价值**：让 OEM 设备真正"开箱即用"，不需要 DBA 提前介入；只要客户接电、装好 TwinCAT，PLC 自己把 DB 环境搭起来。
- **替代方案对比**：
  - **手工预安装数据库 + XML**：靠谱但要 IT 介入；客户机房少 / 现场部署不灵活。
  - **GUI 配置工具引导**：要培训终端用户；OEM 设备目标是免培训。
  - **本 FB**：纯 PLC 代码自动建库；对 SQL Compact / Access / 本地 MS SQL 都适用。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108021259.html
- **相关 FB / FC**：`FB_DBConnectionAdd`（创建后注册）、`FB_DBTableCreate`（在 DB 里建表）、`E_DBTypes`（哪些类型可创建）
