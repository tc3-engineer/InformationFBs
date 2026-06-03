# FB_DBOdbcConnectionAdd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108012043.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBOdbcConnectionAdd.TcPOU`](../examples/P_Demo_FB_DBOdbcConnectionAdd.TcPOU) |

---

## 1. 功能简述

FB_DBOdbcConnectionAdd 在线向 XML 配置文件追加一条**ODBC 型数据库连接**条目（MySQL / PostgreSQL / Oracle / DB2 / InterBase / Firebird），返回 `hDBID`。本 FB 是 `FB_DBConnectionAdd` 的 ODBC 版本——区别在于走 ODBC 驱动而非 OLE DB，因此需要在目标机器上**预先安装对应的 ODBC 驱动**（例如 `MySQL ODBC 5.3 Driver`、`PostgreSQL Unicode ODBC Driver`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          :T_AmsNetId;
    eDBType         :E_DBTypes;
    eDBValueType    :E_DBValueType;
    sDBDriver       :T_MaxString;
    sDBServer       :T_MaxString;
    sDBDatabase     :T_MaxString;
    nDBPort         :UDINT;
    sDBProtocol     :T_MaxString;
    sDBUserId       :T_MaxString;
    sDBPassword     :T_MaxString;
    sDBScheme       :T_MaxString;
    sDBSequence     :T_MaxString;
    sDBClientDll    :T_MaxString;
    sDBTable        :T_MaxString;
    bExecute        :BOOL;
    tTimeout        :TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机用 `''`。 |
| `eDBType` | `E_DBTypes` | - | ODBC 数据库类型：`eDBType_ODBC_MySQL` / `eDBType_ODBC_PostgreSQL` / `eDBType_ODBC_Oracle` / `eDBType_ODBC_DB2` / `eDBType_ODBC_InterBase` / `eDBType_ODBC_Firebird`。 |
| `eDBValueType` | `E_DBValueType` | - | 值列格式：`eDBValue_Double`（LREAL）/ `eDBValue_Bytes`（结构体序列化）。 |
| `sDBDriver` | `T_MaxString` | - | ODBC 驱动名（必须与目标机上已安装的 ODBC 驱动注册名完全一致，例如 `'MySQL ODBC 5.3 ANSI Driver'`、`'PostgreSQL Unicode'`、`'Oracle in OraClient12Home1'`）。 |
| `sDBServer` | `T_MaxString` | - | 数据库服务器主机名或 IP。 |
| `sDBDatabase` | `T_MaxString` | - | 数据库名（schema 名）。 |
| `nDBPort` | `UDINT` | - | ODBC 端口号：MySQL 默认 3306、PostgreSQL 默认 5432、Oracle 默认 1521、DB2 默认 50000。 |
| `sDBProtocol` | `T_MaxString` | - | 协议名（通常 `'TCPIP'`）。 |
| `sDBUserId` | `T_MaxString` | - | 登录用户名。 |
| `sDBPassword` | `T_MaxString` | - | 登录密码（明文写入 XML）。 |
| `sDBScheme` | `T_MaxString` | - | Schema 名（多 schema 数据库需要，例如 PostgreSQL 的 `public`）。 |
| `sDBSequence` | `T_MaxString` | - | **仅 Oracle**：用于 autoID 的 sequence 名。 |
| `sDBClientDll` | `T_MaxString` | - | **仅 InterBase / Firebird**：`fbclient.dll` 的完整路径。 |
| `sDBTable` | `T_MaxString` | - | 默认表名。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次添加。 |
| `tTimeout` | `TIME` | - | ADS 超时，建议 `T#15S` 以上。 |

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
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示添加失败。 |
| `bErrID` | `UDINT` | **变量名 PDF 印为 `bErrID`（B 前缀，PDF/InfoSys 一致的 typo）**，含义是 ADS 错误码。 |
| `hDBID` | `UDINT` | 新建 ODBC 连接的 ID，传给后续 `FB_DBWrite` / `FB_DBRead` 等。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 把新条目写入 XML 配置文件并装载到运行时连接表，分配 `hDBID` 返回。

**驱动名要精确**：`sDBDriver` 必须与目标机上 ODBC Data Source Administrator（odbcad32.exe）"Drivers"标签页里看到的驱动名**完全一致**——包括大小写、空格、版本号。错一个字符就报 `IM002 / IM004` 类 ODBC 错误（在 `bErrID` 显示为 ADS 包装码）。

**端口与协议**：`sDBProtocol = 'TCPIP'` 是绝大多数 ODBC 场景的默认。`nDBPort` 必须与 DB 实际监听端口一致——MySQL `3306` / PostgreSQL `5432` / Oracle `1521` / DB2 `50000` / Firebird `3050`。

**Oracle 特殊字段**：`sDBSequence` 在 Oracle 中用于实现自增主键（Oracle 没有原生 autoID，需配 sequence + trigger 或新版的 IDENTITY 列）。`FB_DBRecordInsert_EX` 写入新行时会用这个 sequence 取下一个 ID。

**Firebird / InterBase 特殊字段**：`sDBClientDll` 必须指向 `fbclient.dll`（Firebird 客户端动态库）的绝对路径，因为它是 ISC 协议库非标准 ODBC。

**`hDBID` 用法**：与 `FB_DBConnectionAdd` 相同——后续所有 DB 操作 FB 都用这个 ID 区分连接。

**`bErrID` typo 说明**：与 `FB_DBConnectionAdd` 相同——PDF 与 InfoSys 都印 `bErrID`（B 前缀），调用代码必须用 `bErrID`。

## 4. 错误码 / 返回值

通过 `bError` + `bErrID` 输出：

| 错误号（典型） | 含义 | 排查建议 |
|---|---|---|
| `0x6` | DB Server 未启动 | 启动服务 |
| `0x70C` | XML 文件不存在 | 检查路径 |
| `0x70D` | XML 写入失败 | 检查权限 |
| `0x70F` | 连接已存在 | 用 `FB_GetDBXMLConfig` 查询后再 Add |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

ODBC 驱动级别错误（驱动找不到、连接串错、TCP 不通）通常包在 ADS 错误码里；具体的 SQL State / ODBC error 在 `FB_DBConnectionOpen` 调用时通过 `sSQLState : ST_DBSQLError` 输出。

## 5. 使用注意 / 常见坑

- **目标机必须装 ODBC 驱动**：远端 CX 工控机需要先装 `MySQL ODBC Connector`、`PostgreSQL ODBC` 等。Windows 32 位 PLC 走 32 位 ODBC（`%WinDir%\SysWOW64\odbcad32.exe`）；64 位 PLC 走 64 位（`%WinDir%\System32\odbcad32.exe`）。位宽不匹配会报"驱动未找到"。
- **`sDBDriver` 名字大小写敏感**：在 ODBC Administrator → Drivers 页签里复制驱动名，不要手敲。
- **MySQL 5.3 / 8.0 ANSI vs Unicode**：ANSI 驱动只支持 latin1 字符集；多语言 / 中文场景必须用 Unicode 驱动。
- **InterBase / Firebird 必须填 `sDBClientDll`**：常见路径 `C:\Program Files\Firebird\Firebird_2_5\bin\fbclient.dll`；找不到会报 ODBC 错误。
- **`sDBPassword` 明文存 XML**：与 `FB_DBConnectionAdd` 一样，运维需保护 XML 文件权限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBOdbcConnectionAdd.TcPOU`](../examples/P_Demo_FB_DBOdbcConnectionAdd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MES 集成项目中产线 PLC 需要把每件产品的工艺数据写到工厂车间的 MySQL 服务器（IP `192.168.10.20`、端口 3306、数据库 `mes_prod`）。CX 工控机预装 MySQL ODBC 驱动；PLC 启动时调本 FB 在线建立 ODBC 连接，从此 `FB_DBWrite` 写到 MES。
- **价值**：相比"用 OLE DB Provider 连 MySQL"——后者在 Windows 上没有官方 MySQL OLE DB（要装第三方），ODBC 驱动是官方原生支持，稳定性、跨版本兼容性更好。
- **替代方案对比**：
  - **`FB_DBConnectionAdd`**：MS SQL / Access / SQL Compact 等 OLE DB 型走那个。
  - **OPC UA / MQTT 中转**：PLC → 网关 → DB，灵活但多一层故障点；性能不如直连。
  - **本 FB**：MySQL / PostgreSQL / Oracle / DB2 等 ODBC 型 DB 的直连入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108012043.html
- **相关 FB / FC**：`FB_DBConnectionAdd`（OLE DB 型）、`FB_DBReloadConfig`、`FB_GetDBXMLConfig`、`FB_DBConnectionOpen` / `FB_DBConnectionClose`、`E_DBTypes`（枚举，列 ODBC 与 OLE DB 类型）
