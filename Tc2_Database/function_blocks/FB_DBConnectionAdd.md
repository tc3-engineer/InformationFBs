# FB_DBConnectionAdd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108010507.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBConnectionAdd.TcPOU`](../examples/P_Demo_FB_DBConnectionAdd.TcPOU) |

---

## 1. 功能简述

FB_DBConnectionAdd 在线向 TwinCAT Database Server 的 XML 配置文件中**追加一条新的数据库连接条目**，并立即返回该连接的 `hDBID`。新条目按 `eDBType`（MS SQL / MS Access / SQL Compact / ASCII / XML / OCI-Oracle 等本机型类，详见 `E_DBTypes`）与 `eDBValueType`（值表存储格式：`eDBValue_Double` 数值列 / `eDBValue_Bytes` 字节缓冲列）区分。本 FB 适合 PLC 在线添加数据库（OEM 设备自助配置场景）；ODBC 型数据库（MySQL / PostgreSQL / DB2 等）请用 `FB_DBOdbcConnectionAdd`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          :T_AmsNetId;
    eDBType         :E_DBTypes;
    eDBValueType    :E_DBValueType;
    sDBServer       :T_MaxString;
    sDBProvider     :T_MaxString;
    sDBUrl          :T_MaxString;
    sDBSystemDB     :T_MaxString;
    sDBUserId       :T_MaxString;
    sDBPassword     :T_MaxString;
    sDBTable        :T_MaxString;
    bExecute        :BOOL;
    tTimeout        :TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机用空串 `''`。 |
| `eDBType` | `E_DBTypes` | - | 数据库类型枚举。本 FB 适用于：`eDBType_Mobile_Server`（SQL Compact）/ `eDBType_Access` / `eDBType_Sequal_Server`（MS SQL）/ `eDBType_ASCII` / `eDBType_XML`（不支持，PDF 标注）/ `eDBType_OCI_Oracle`。ODBC 型走 `FB_DBOdbcConnectionAdd`。 |
| `eDBValueType` | `E_DBValueType` | - | 值列存储格式：`eDBValue_Double`（数值统一按 LREAL 存）/ `eDBValue_Bytes`（按字节序列化，支持结构体、字符串）。 |
| `sDBServer` | `T_MaxString` | - | 服务器名（远端 SQL Server / Oracle 实例名）。Access / ASCII / SQL Compact 等本地文件型可填空串。 |
| `sDBProvider` | `T_MaxString` | - | OLE DB Provider 名（如 MS SQL 用 `SQLOLEDB`、Access 用 `Microsoft.Jet.OLEDB.4.0` / `Microsoft.ACE.OLEDB.12.0`）。可填空串走默认。 |
| `sDBUrl` | `T_MaxString` | - | 数据库路径：本地文件型填 MDB / SDF / TXT / XML 文件的绝对路径；远端 SQL Server 填数据库名。 |
| `sDBSystemDB` | `T_MaxString` | - | 仅 Access 数据库使用：MDW（工作组安全文件）路径。其它类型填空串。 |
| `sDBUserId` | `T_MaxString` | - | 数据库登录用户名。SQL Compact / ASCII 等无认证类型填空串。 |
| `sDBPassword` | `T_MaxString` | - | 数据库登录密码。注意：明文存到 XML，敏感场景需配 Impersonate 或加密。 |
| `sDBTable` | `T_MaxString` | - | 默认表名（后续 `FB_DBWrite` / `FB_DBRead` 操作的目标表）。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次写 XML + 建连接。 |
| `tTimeout` | `TIME` | - | ADS 超时，Beckhoff 例程多用 `T#15S`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    bErrID      : UDINT;
    hDBID       : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中；高电平期间不接受新触发。 |
| `bError` | `BOOL` | TRUE 表示新增失败，错误号在 `bErrID`。 |
| `bErrID` | `UDINT` | **变量名 PDF 印刷为 `bErrID`（B 前缀，PDF 写错了但 InfoSys 也保留这个名字），含义仍是 ADS 错误码**。常见 `0x6` 服务未启动、`0x70D` XML 写入失败、`0x70F` 连接已存在。 |
| `hDBID` | `UDINT` | **输出**：新建连接的 ID，传给后续 `FB_DBWrite` / `FB_DBRead` 等。失败时为 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 会做三件事：写 XML、把新连接装载到运行时表、分配 `hDBID` 返回。整个流程对本地文件型 DB（SQL Compact / ASCII）通常 50~200 ms；对远端 SQL Server 需要先 TCP 建连，可能 1 秒以上。

**`eDBType` + `eDBValueType` 组合矩阵**：
- `eDBType_Sequal_Server` + `eDBValue_Double` = MS SQL，数值表，表结构需含 `Timestamp / Name / Value(float)` 三列（最简模式）
- `eDBType_Mobile_Server` + `eDBValue_Bytes` = SQL Compact (.sdf)，字节表，可存结构体
- `eDBType_ASCII` + `eDBValue_Double` = ASCII 文件，每行一条 `Timestamp,Name,Value` 记录
- `eDBType_Access` + `eDBValue_Bytes` = MS Access (.mdb)，字节表
- `eDBType_OCI_Oracle` = Oracle，需 OCI 客户端

具体每种 DB 类型的字段语义见 PDF §6.5.x（每个 DB 类型一节）。

**`hDBID` 的用法**：后续所有数据库操作 FB（`FB_DBWrite` / `FB_DBRead` / `FB_DBRecordInsert_EX` / `FB_DBRecordDelete` 等）的 `hDBID` 入参必须填本 FB 返回的 ID。多个连接并存时，按 `hDBID` 区分。重启 Database Server 后 `hDBID` **可能**重新分配（按 XML 顺序），所以业务侧不要硬编码 `hDBID = 1`，而是用 `FB_GetDBXMLConfig` 查询。

**重复添加**：同一组 `sDBUrl + sDBTable` 重复 Add 会得到 `0x70F`（已存在）。先用 `FB_GetDBXMLConfig` 查一遍是否已存在。

**`bErrID` 命名说明**：PDF + InfoSys 都把这个输出印为 `bErrID`（B 前缀，疑似源码 typo），但 PDF 正文说明里写的是 `nErrID`（N 前缀）。**调用代码必须用 PDF 声明里的 `bErrID`**，否则编译报错。

## 4. 错误码 / 返回值

通过 `bError` + `bErrID` 输出：

| 错误号 | 含义 | 排查建议 |
|---|---|---|
| `0x6` | DB Server 服务未启动 | 启动 TwinCAT Database Server |
| `0x70C` | XML 文件不存在 / 路径错 | 检查 `C:\TwinCAT\TcDatabaseSrv\Config\TcDbSrv.xml` |
| `0x70D` | XML 写入失败 / 语法错 | 检查文件读写权限 |
| `0x70F` | 连接已存在（同名重复 Add） | 用 `FB_GetDBXMLConfig` 查一遍后再 Add |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

数据库连接失败（如 SQL Server 网络不通）通常不在本 FB 报错，而是延后到 `FB_DBConnectionOpen` / `FB_DBWrite` 阶段。

## 5. 使用注意 / 常见坑

- **密码明文写入 XML**：`sDBPassword` 不会加密，运维需保护 `C:\TwinCAT\TcDatabaseSrv\Config\TcDbSrv.xml` 权限或启用 Impersonate（PDF §6.6.1）。
- **`hDBID` 不要硬编码**：第一次添加的连接 ID 可能是 1，但删了再加可能变成 2 或更大。OEM 设备代码应在添加完后保存 `hDBID` 到 retain 变量。
- **ODBC 型数据库不要用本 FB**：MySQL / PostgreSQL / DB2 / Firebird / InterBase 走 `FB_DBOdbcConnectionAdd`，本 FB 会用 OLE DB Provider 试连接失败。
- **`sDBTable` 字段含义**：是"该连接默认的表"，后续 `FB_DBWrite` 的 sDBVarName 隐含写入这个表的 Value 列。如果一个数据库要写多张表，建议每张表单独 Add 一个连接。（工程经验补充）
- **添加后 `bErrID` = 0 ≠ 连接成功**：本 FB 只是把条目写入 XML 并分配 `hDBID`；真正的 DB 连接打开发生在 `FB_DBConnectionOpen` 或第一次 Read/Write 时。要确认 DB 通就再调一次 `FB_DBConnectionOpen`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBConnectionAdd.TcPOU`](../examples/P_Demo_FB_DBConnectionAdd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：OEM 设备厂出货前不知道客户最终用哪种数据库；上电后 HMI 弹窗让用户选择 MS SQL / SQL Compact / Access，填好服务器和密码 → PLC 调本 FB 一次性把连接写到 XML，从此就可以日志参数到该 DB。
- **价值**：相比"提前在 XML Editor 手工配好"，本 FB 让 PLC 程序可以**在运行时根据用户选择动态添加**，OEM 设备同一份固件适配多家客户。
- **替代方案对比**：
  - **手工 XML Editor 配置**：适合一次性部署、参数固定的场景；OEM 多客户场景不灵活。
  - **`FB_DBOdbcConnectionAdd`**：ODBC 型 DB（MySQL / PostgreSQL）必须用这个 FB。
  - **本 FB**：OLE DB 型（MS SQL / Access / SQL Compact / OCI Oracle / ASCII / XML）专用，最常见。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108010507.html
- **相关 FB / FC**：`FB_DBOdbcConnectionAdd`（ODBC 型）、`FB_AdsDeviceConnectionAdd`（ADS 设备）、`FB_DBReloadConfig`（重载 XML）、`FB_GetDBXMLConfig`（查询已配连接）、`FB_DBConnectionOpen` / `FB_DBConnectionClose`、`E_DBTypes` / `E_DBValueType`（枚举）
