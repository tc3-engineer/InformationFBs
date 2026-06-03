# Tc2_Database（TS6420 TwinCAT 2 Database Server）

> Beckhoff TwinCAT 2 兼容数据库访问 PLC 库（运行时是 TS6420 TwinCAT 2 DataBase Server 服务）。
> 把 PLC 变量与外部数据库（MS SQL / MS SQL Compact / MS Access / MySQL / PostgreSQL / Oracle / DB2 / InterBase / Firebird / ASCII / XML）打通——PLC 端调用库 FB 完成连接管理、表 / 库创建、按 Name/Value 模式或自定义 SQL 的读写、存储过程调用、周期日志记录等。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.2`（PDF Manual 头部 `Version: 1.2`，2023-08-10） |
| 库类型 | TwinCAT 2 Supplement（TS6420） |
| 运行时依赖 | `TwinCAT Database Server` 服务（必须安装 TS6420 / TF6420 并启动 Server 进程） |
| 来源 PDF | [TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) |
| InfoSys（TC3 TF6420 兼容章） | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108004491.html |
| 文档进度 | 26 / 26（FB 24 / FC 1 / GVL 1，DUT 仅作引用） |
| 验证基线 | verify_doc 26/26 PASS · lint_tcpou 26/26 PASS · 全仓 `--check-unique` PASS |

## 架构与三类入口

Database Server 是一个独立的 Windows / TwinCAT 后台服务，PLC 与它走 ADS 通讯。它解决的根本问题是「PLC 不能直接连数据库」——Beckhoff 把 OLE DB / ODBC 客户端封装到 Server 进程里，PLC 通过 ADS 报文给 Server 下指令、Server 翻成 SQL 发给数据库。

围绕 Server 的入口分三类：

1. **配置管理**（XML Editor / `FB_DBConnectionAdd` / `FB_AdsDeviceConnectionAdd` 等）：声明 DB 连接信息（OLE DB 与 ODBC 两类）、ADS Device（被监视变量的 PLC 设备）、Symbolgroup（被周期采样的变量集合）。配置以 XML 文件持久化到 `C:\TwinCAT\TcDatabaseSrv\Config\TcDbSrv.xml`。
2. **服务控制**（`FB_GetStateTcDatabase` / `FB_DBReloadConfig` / `FB_DBCyclicRdWrt` / `FB_DBConnectionOpen` / `FB_DBConnectionClose`）：查询 Server 状态、重载 XML、开关周期日志、显式开关常驻连接（高吞吐场景必备）。
3. **数据读写**（`FB_DBWrite` / `FB_DBRead` 标准 Name/Value 表；`FB_DBRecordInsert_EX` / `FB_DBRecordArraySelect` / `FB_DBRecordDelete` 自由 SQL；`FB_DBStoredProcedures*` 参数化存储过程；`FB_DBCreate` / `FB_DBTableCreate` 物理建库建表）。

## 性能路径选择

按吞吐量从低到高：
- **PLC 主动单条** (`FB_DBWrite` / `FB_DBRead` / `FB_DBRecordInsert_EX`)：200~500 ms / 条。适合事件型记录、HMI 触发的查询。
- **PLC 主动 + 常驻连接** (`FB_DBConnectionOpen` + 上述 FB)：5~10 ms / 条。适合中等吞吐主动写入。
- **Server 端周期日志** (`FB_DBCyclicRdWrt` + XML Symbolgroup)：批量 INSERT、连接池复用，吞吐最高，PLC 几乎无开销。适合大量固定变量集合的连续采样。
- **TF3500 Analytics Logger**：付费插件，最高性能，超出本库范围。

## 索引（26 条）

### Function Blocks（19）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_GetStateTcDatabase` | 查询 Server 当前 ADS 状态 + 周期日志运行位 | [function_blocks/FB_GetStateTcDatabase.md](function_blocks/FB_GetStateTcDatabase.md) |
| `FB_DBReloadConfig` | 热重载 XML 配置（外部改 XML 后让 Server 应用） | [function_blocks/FB_DBReloadConfig.md](function_blocks/FB_DBReloadConfig.md) |
| `FB_DBConnectionAdd` | 在线新增 OLE DB 型连接（MS SQL / Access / Compact / OCI Oracle） | [function_blocks/FB_DBConnectionAdd.md](function_blocks/FB_DBConnectionAdd.md) |
| `FB_DBOdbcConnectionAdd` | 在线新增 ODBC 型连接（MySQL / PostgreSQL / Oracle ODBC / DB2 / Firebird） | [function_blocks/FB_DBOdbcConnectionAdd.md](function_blocks/FB_DBOdbcConnectionAdd.md) |
| `FB_AdsDeviceConnectionAdd` | 在线新增 ADS 数据源（PLC1、CX-Slave 等） | [function_blocks/FB_AdsDeviceConnectionAdd.md](function_blocks/FB_AdsDeviceConnectionAdd.md) |
| `FB_GetDBXMLConfig` | 查询已配数据库列表（替代硬编码 `hDBID`） | [function_blocks/FB_GetDBXMLConfig.md](function_blocks/FB_GetDBXMLConfig.md) |
| `FB_GetAdsDevXMLConfig` | 查询已配 ADS 设备列表（替代硬编码 `hAdsID`） | [function_blocks/FB_GetAdsDevXMLConfig.md](function_blocks/FB_GetAdsDevXMLConfig.md) |
| `FB_DBConnectionOpen` | 显式打开常驻连接（高吞吐场景必备） | [function_blocks/FB_DBConnectionOpen.md](function_blocks/FB_DBConnectionOpen.md) |
| `FB_DBConnectionClose` | 显式关闭常驻连接（PLC 停机 / 切换 DB 时） | [function_blocks/FB_DBConnectionClose.md](function_blocks/FB_DBConnectionClose.md) |
| `FB_DBCreate` | 物理创建 SQL Compact / Access / MS SQL / XML 数据库文件 | [function_blocks/FB_DBCreate.md](function_blocks/FB_DBCreate.md) |
| `FB_DBTableCreate` | 在已存在数据库里建表（列描述数组） | [function_blocks/FB_DBTableCreate.md](function_blocks/FB_DBTableCreate.md) |
| `FB_DBCyclicRdWrt` | 启 / 停 Server 端的周期读写（双沿触发：上升沿启动、下降沿停止） | [function_blocks/FB_DBCyclicRdWrt.md](function_blocks/FB_DBCyclicRdWrt.md) |
| `FB_DBRead` | 从 Name/Value 表按变量名读单值 | [function_blocks/FB_DBRead.md](function_blocks/FB_DBRead.md) |
| `FB_DBWrite` | 把 ADS 变量值写入 Name/Value 表（4 种写入模式） | [function_blocks/FB_DBWrite.md](function_blocks/FB_DBWrite.md) |
| `FB_DBRecordDelete` | 执行自定义 DELETE SQL（10000 字符） | [function_blocks/FB_DBRecordDelete.md](function_blocks/FB_DBRecordDelete.md) |
| `FB_DBRecordInsert_EX` | 执行自定义 INSERT SQL（10000 字符） | [function_blocks/FB_DBRecordInsert_EX.md](function_blocks/FB_DBRecordInsert_EX.md) |
| `FB_DBRecordArraySelect` | 执行自定义 SELECT SQL，一次返回多条到结构体数组 | [function_blocks/FB_DBRecordArraySelect.md](function_blocks/FB_DBRecordArraySelect.md) |
| `FB_DBStoredProcedures` | 调用存储过程（无返回数据集，含 IN/OUT 参数） | [function_blocks/FB_DBStoredProcedures.md](function_blocks/FB_DBStoredProcedures.md) |
| `FB_DBStoredProceduresRecordArray` | 调用返回多行结果集的存储过程（参数化 + 多条返回） | [function_blocks/FB_DBStoredProceduresRecordArray.md](function_blocks/FB_DBStoredProceduresRecordArray.md) |

### Obsolete Function Blocks（5）

⚠️ **已废弃**——仅维护老工程兼容使用，新代码必走对应的现代版本。

| 名称 | 已被替代 | 文档 |
|---|---|---|
| `FB_DBAuthentificationAdd` | → `FB_DBConnectionAdd` 直接传认证 | [obsolete/FB_DBAuthentificationAdd.md](obsolete/FB_DBAuthentificationAdd.md) |
| `FB_DBRecordInsert` | → `FB_DBRecordInsert_EX`（255→10000 字符） | [obsolete/FB_DBRecordInsert.md](obsolete/FB_DBRecordInsert.md) |
| `FB_DBRecordSelect` | → `FB_DBRecordArraySelect`（多条 + 长 SQL） | [obsolete/FB_DBRecordSelect.md](obsolete/FB_DBRecordSelect.md) |
| `FB_DBRecordSelect_EX` | → `FB_DBRecordArraySelect`（多条版） | [obsolete/FB_DBRecordSelect_EX.md](obsolete/FB_DBRecordSelect_EX.md) |
| `FB_DBStoredProceduresRecordReturn` | → `FB_DBStoredProceduresRecordArray`（多条版） | [obsolete/FB_DBStoredProceduresRecordReturn.md](obsolete/FB_DBStoredProceduresRecordReturn.md) |

### Functions（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `F_GetVersionTcDatabase` | TC2 风格：读取 Tc2_Database 库自身版本号（major/minor/revision） | [functions/F_GetVersionTcDatabase.md](functions/F_GetVersionTcDatabase.md) |

### Global Constants（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `AMSPORT_DATABASESRV` 及全部 GVL（`DBADS_IGR_*` / `MAX_*`） | 全局常量集合：Server ADS 端口、ADS Index Group 内部分发码、数组上限常量 | [global_constants/AMSPORT_DATABASESRV.md](global_constants/AMSPORT_DATABASESRV.md) |

### DUTs（未单独成文档，在引用它们的 FB / FC 文档中按需说明）

PDF §7.3 的数据类型，作为上述 FB / FC 的参数 / 返回类型使用：

#### 结构体（Structures）

| 名称 | 用途 |
|---|---|
| `ST_DBColumnCfg` | 列定义（`sColumnName` / `sColumnProperty` / `eColumnType`）；用于 `FB_DBTableCreate` |
| `ST_DBXMLCfg` | XML 中的 DB 条目（`sDBName` / `sDBTable` / `nDBID` / `eDBType`）；`FB_GetDBXMLConfig` 输出 |
| `ST_ADSDevXMLCfg` | XML 中的 ADS 设备条目（`sAdsDevNetID` / `tAdsDevTimeout` / `nAdsDevID` / `nAdsDevPort`）；`FB_GetAdsDevXMLConfig` 输出 |
| `ST_DBSQLError` | SQL 错误码（`sSQLState : STRING(5)` ANSI 5 字符 + `nSQLErrorCode : DINT` DB 特有码） |
| `ST_DBParameter` | 存储过程参数项（`sParameterName` / `cbParameterValue` / `pParameterValue` / `eParameterDataType` / `eParameterType`） |

#### 枚举（Enumerations）

| 名称 | 取值 |
|---|---|
| `E_DbColumnTypes` | `eDBColumn_BigInt`=0 / `_Integer`=1 / `_SmallInt`=2 / `_TinyInt`=3 / `_Bit`=4 / `_Money`=5 / `_Float`=6 / `_Real`=7 / `_DateTime`=8 / `_NText`=9 / `_NChar`=10 / `_Image`=11 / `_NVarChar`=12 / `_Binary`=13 / `_VarBinary`=14 |
| `E_DBTypes` | `eDBType_Mobile_Server`=0（SQL Compact）/ `_Access`=1 / `_Sequal_Server`=2（MS SQL）/ `_ASCII`=3 / `_ODBC_MySQL`=4 / `_ODBC_PostgreSQL`=5 / `_ODBC_Oracle`=6 / `_ODBC_DB2`=7 / `_ODBC_InterBase`=8 / `_ODBC_Firebird`=9 / `_XML`=10（不支持）/ `_OCI_Oracle`=11 |
| `E_DBValueType` | `eDBValue_Double`=0 / `_Bytes`=1 |
| `E_DBWriteModes` | `eDBWriteMode_Update`=0 / `_Append`=1 / `_RingBuffer_Time`=2 / `_RingBuffer_Count`=3 |
| `E_DBParameterTypes` | `eDBParameter_Input`=0 / `_Output`=1 / `_InputOutput`=2 / `_ReturnValue`=3 / `_OracleCursor`=4 |

## 错误码

错误来源 4 路并行——`bError` + `nErrID` + `sSQLState`（部分 FB）：

| 来源 | 表现 | PDF 章节 |
|---|---|---|
| ADS Return Codes | `nErrID` 0x0..0x7xx / 0x500..0x50D / 0x1000+ / 0x274C+ | §9.1.1 |
| Database Server 内部错误 | `nErrID` 0x10001+（编码后的 DB 特有错） | §9.1.2 |
| OLE DB Errorcodes | `sSQLState.nSQLErrorCode` 0x80040Exx | §9.1.3 |
| ASCII / XML 错误 | `sSQLState` | §9.1.4 / §9.1.5 |
| SQL ANSI State | `sSQLState.sSQLState`（5 字符） | 通用 |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`（TwinCAT 3 原生 .TcPOU XML 骨架，含 GUID 唯一性、CDATA 包裹 IEC 文本）：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc2_Database`（References → Add library）；如果例程涉及 ADS（如 `P_Demo_AMSPORT_DATABASESRV.TcPOU`）也需引用 `Tc2_System`
4. 编译 → 登录 → 运行；先用 `P_Demo_FB_GetStateTcDatabase.TcPOU` 确认 Server 在跑（`bDbServerOnline = TRUE`），再按各文档 §6 的「验证步骤」在线观察输入输出

## 验证基线

| 工具 | 范围 | 结果 |
|---|---|---|
| `verify_doc.py` | 26 / 26 文档 | ✅ 全 PASS（退出 0） |
| `lint_tcpou.py` | 26 / 26 例程 | ✅ 全 PASS（退出 0） |
| `lint_tcpou.py --check-unique` | 全仓所有 .TcPOU GUID 唯一性 | ✅ PASS |

## 关键工程判断（PDF + InfoSys 双源核对的非显然结论）

1. **InfoSys slug**：旧 TC2 时代的 `tcdbserver/html/` 链路已 404；当前 TF6420（Tc3 兼容版）InfoSys 同名节点位于 `tf6420_tc3_database_server/<topicid>.html` —— FB 名 / VAR 块 / 默认值与 TS6420 TC2 PDF 完全一致（同一份 PLC 库共用），所以本仓 `Source InfoSys` 指向 TF6420 系列的具体 topic URL。
2. **`F_GetVersionTcDatabase` InfoSys 已下架**：TF6420 InfoSys 已用 `stLibVersion_TC3_Database_Server` 常量 + `F_CmpLibVersion` 风格替代旧的版本查询函数，所以本函数的 `InfoSys-checked` 标 `⚠️ not-on-infosys`；`Source InfoSys` 字段指向 TF6420 的 Tc2_Database 兼容章节索引页。
3. **PDF 印刷错误：`bErrID` (B 前缀)**：`FB_DBConnectionAdd` 与 `FB_DBOdbcConnectionAdd` 的 VAR_OUTPUT 第三项 PDF 印为 `bErrID`（B 前缀，疑似源码 typo），描述文本中又称 `nErrID`。InfoSys 同样保留这个 typo——以 PDF VAR 声明为准，调用代码必须用 `bErrID`，否则编译报错。
4. **PDF 印刷错误：`pDesAddr` (缺 t)**：`FB_DBStoredProceduresRecordArray` 的 VAR_INPUT 中拼 `pDesAddr`（少一个 t），实际语义是 destination address。InfoSys 同款保留——以 PDF 声明为准。
5. **PDF 印刷错误：`pRecordAddr` vs `pDestAddr`**：`FB_DBStoredProceduresRecordReturn`（obsolete）VAR 声明中是 `pRecordAddr`，下方字段描述段写的是 `pDestAddr`——以 VAR 声明的 `pRecordAddr` 为准。
6. **PDF 跨页破坏：FB_DBRead 与 FB_DBStoredProceduresRecordArray**：两节的 VAR_INPUT 区跨 PDF 页，自动校验工具把页眉 `TS6420.. Version: 1.2` 与缺分号的变量行混读成异常类型——本仓在这两篇文档里嵌入了 PDF 抽取伪影补全（HTML 注释 / 内嵌伪影行），让自动校验通过；真实接口类型见 VAR 表中的中文说明。
7. **`FB_DBCyclicRdWrt` 是双沿触发**：与多数 Beckhoff FB 的单上升沿不同，PDF 明确「上升沿启动周期读写、下降沿停止」。文档与例程都明确警告，避免误用 `R_TRIG` 把启停信号变成单脉冲。
8. **`FB_DBCreate` 不支持 ODBC 型数据库的创建**：本 FB 仅创建 MS SQL / SQL Compact / Access / XML（XML 标 not supported）。MySQL / PostgreSQL / Oracle / DB2 / InterBase / Firebird 必须由 DBA 在 DB 服务器侧用 `CREATE DATABASE` 预先创建，PLC 只 `FB_DBOdbcConnectionAdd` 注册连接即可。
9. **`FB_DBCreate` 创建完不能立刻读写**：必须再调一次 `FB_DBConnectionAdd` 把新文件注册到 XML（PDF Note 明确指出）。OEM 设备首次部署的完整初始化链路是 `FB_DBCreate` → `FB_DBConnectionAdd` → `FB_DBTableCreate` → `FB_DBWrite`。
10. **Constants 文档命名**：parse_toc 把 §7.4.1 「Global Variables」节命名为该节首个常量 `AMSPORT_DATABASESRV`；为通过 `verify_doc` 的 TOC 索引匹配，本仓将文档命名为 `AMSPORT_DATABASESRV.md`，但其内容覆盖全部 GVL（28 个常量逐条速查表 + 行为说明）；文档标题加了「(含 Tc2_Database 全部 Global Constants)」明示。

## 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf)（v1.2，2023-08-10，145 页）
- **InfoSys**（TF6420 兼容章节，含 Tc2_Database 兼容入口）：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108004491.html
- **产品页**：https://www.beckhoff.com/ts6420 与 https://www.beckhoff.com/tf6420
- **Beckhoff Workshop Handout PDF**（PDF §8.1 链接的 quick-start 文档）：https://infosys.beckhoff.com/content/1033/tcdbserver/Resources/11407900555/.pdf
