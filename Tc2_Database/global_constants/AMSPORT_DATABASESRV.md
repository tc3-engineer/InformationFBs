# AMSPORT_DATABASESRV（含 Tc2_Database 全部 Global Constants）

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108063883.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_AMSPORT_DATABASESRV.TcPOU`](../examples/P_Demo_AMSPORT_DATABASESRV.TcPOU) |

---

## 1. 功能简述

Tc2_Database 库的全局常量集合（PDF §7.4.1 Global Variables）。覆盖三类：(1) `AMSPORT_DATABASESRV = 21372` ——Database Server 的 AMS 端口号；(2) 一组 `DBADS_IGR_*` ADS Index Group 常量——这些是 Database Server 内部分发各类操作的 ADS index group，少数高级场景下用户代码可能直接用 `ADSWRITE` / `ADSREAD` 绕过本库 FB 直访 Server；(3) 数组容量上限 `MAX_DB_TABLE_COLUMNS = 255` / `MAX_XML_DECLARATIONS = 255` / `MAX_STORED_PROCEDURES_PARAMETERS = 255`，被各种 FB 用作其输入数组的上界。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT 
    AMSPORT_DATABASESRV                             : UINT   := 21372;
    DBADS_IGR_RELOADXML                             : UDINT  :=16#100;
    DBADS_IGR_GETSTATE                              : UDINT  :=16#200;
    DBADS_IGR_DBCONNOPEN                            : UDINT  :=16#300;
    DBADS_IGR_DBCONNCLOSE                           : UDINT  :=16#301;
    DBADS_IGR_ADSDEVCONNOPEN                        : UDINT  :=16#302;
    DBADS_IGR_ADSDEVCONNCLOSE                       : UDINT  :=16#303;
    DBADS_IGR_DBSTOREDPROCEDURES                    : UDINT  :=16#400;
    DBADS_IGR_DBSTOREDPROCEDURES_RETURNRECORD       : UDINT  :=16#401;
    DBADS_IGR_DBSTOREDPROCEDURES_RETURNRECORDARRAY  : UDINT  :=16#402;
    DBADS_IGR_START                                 : UDINT  :=16#10000;
    DBADS_IGR_STOP                                  : UDINT  :=16#20000;
    DBADS_IGR_DBCONNADD                             : UDINT  :=16#30000;
    DBADS_IGR_ADSDEVCONNADD                         : UDINT  :=16#30001;
    DBADS_IGR_ODBC_DBCONNADD                        : UDINT  :=16#30010;
    DBADS_IGR_GETDBXMLCONFIG                        : UDINT  :=16#30101;
    DBADS_IGR_GETADSDEVXMLCONFIG                    : UDINT  :=16#30102;
    DBADS_IGR_DBWRITE                               : UDINT  :=16#40000;
    DBADS_IGR_DBREAD                                : UDINT  :=16#50000;
    DBADS_IGR_DBTABLECREATE                         : UDINT  :=16#60000;
    DBADS_IGR_DBCREATE                              : UDINT  :=16#70000;
    DBADS_IGR_DBRECORDSELECT                        : UDINT  :=16#80001;
    DBADS_IGR_DBRECORDINSERT                        : UDINT  :=16#80002;
    DBADS_IGR_DBRECORDDELETE                        : UDINT  :=16#80003;
    DBADS_IGR_DBAUTHENTIFICATIONADD                 : UDINT  :=16#90000;
    MAX_DB_TABLE_COLUMNS                            : UDINT  := 255;
    MAX_XML_DECLARATIONS                            : UDINT  := 255;
    MAX_STORED_PROCEDURES_PARAMETERS                : UDINT  := 255;
    
END_VAR
```

### 常量速查表

| 常量名 | 类型 | 值 | 用途 |
|---|---|---|---|
| `AMSPORT_DATABASESRV` | `UINT` | `21372` | Database Server 的 ADS 端口号——所有库内 FB 内部都用这个端口与 Server 通讯。 |
| `MAX_DB_TABLE_COLUMNS` | `UDINT` | `255` | `FB_DBTableCreate` 的 `pTableCfg` 数组容量上限——单表最多 255 列。 |
| `MAX_XML_DECLARATIONS` | `UDINT` | `255` | `FB_GetDBXMLConfig` / `FB_GetAdsDevXMLConfig` 的输出数组容量上限——单 Server 最多 255 个 DB / ADS Device 条目。 |
| `MAX_STORED_PROCEDURES_PARAMETERS` | `UDINT` | `255` | `FB_DBStoredProcedures*` 系列的参数列表数组上限——单存储过程最多 255 个参数。 |
| `DBADS_IGR_GETSTATE` | `UDINT` | `16#200` | `FB_GetStateTcDatabase` 内部用的 ADS Index Group。 |
| `DBADS_IGR_RELOADXML` | `UDINT` | `16#100` | `FB_DBReloadConfig` 内部用的 ADS Index Group。 |
| `DBADS_IGR_DBCONNOPEN` | `UDINT` | `16#300` | `FB_DBConnectionOpen` 内部 ADS IGR。 |
| `DBADS_IGR_DBCONNCLOSE` | `UDINT` | `16#301` | `FB_DBConnectionClose` 内部 ADS IGR。 |
| `DBADS_IGR_ADSDEVCONNOPEN` | `UDINT` | `16#302` | 内部用：打开 ADS Device 连接。 |
| `DBADS_IGR_ADSDEVCONNCLOSE` | `UDINT` | `16#303` | 内部用：关闭 ADS Device 连接。 |
| `DBADS_IGR_DBSTOREDPROCEDURES` | `UDINT` | `16#400` | `FB_DBStoredProcedures` 内部 ADS IGR。 |
| `DBADS_IGR_DBSTOREDPROCEDURES_RETURNRECORD` | `UDINT` | `16#401` | `FB_DBStoredProceduresRecordReturn` 内部 ADS IGR。 |
| `DBADS_IGR_DBSTOREDPROCEDURES_RETURNRECORDARRAY` | `UDINT` | `16#402` | `FB_DBStoredProceduresRecordArray` 内部 ADS IGR。 |
| `DBADS_IGR_START` | `UDINT` | `16#10000` | `FB_DBCyclicRdWrt` 启动周期读写的 ADS IGR。 |
| `DBADS_IGR_STOP` | `UDINT` | `16#20000` | `FB_DBCyclicRdWrt` 停止周期读写的 ADS IGR。 |
| `DBADS_IGR_DBCONNADD` | `UDINT` | `16#30000` | `FB_DBConnectionAdd` 内部 ADS IGR。 |
| `DBADS_IGR_ADSDEVCONNADD` | `UDINT` | `16#30001` | `FB_AdsDeviceConnectionAdd` 内部 ADS IGR。 |
| `DBADS_IGR_ODBC_DBCONNADD` | `UDINT` | `16#30010` | `FB_DBOdbcConnectionAdd` 内部 ADS IGR。 |
| `DBADS_IGR_GETDBXMLCONFIG` | `UDINT` | `16#30101` | `FB_GetDBXMLConfig` 内部 ADS IGR。 |
| `DBADS_IGR_GETADSDEVXMLCONFIG` | `UDINT` | `16#30102` | `FB_GetAdsDevXMLConfig` 内部 ADS IGR。 |
| `DBADS_IGR_DBWRITE` | `UDINT` | `16#40000` | `FB_DBWrite` 内部 ADS IGR。 |
| `DBADS_IGR_DBREAD` | `UDINT` | `16#50000` | `FB_DBRead` 内部 ADS IGR。 |
| `DBADS_IGR_DBTABLECREATE` | `UDINT` | `16#60000` | `FB_DBTableCreate` 内部 ADS IGR。 |
| `DBADS_IGR_DBCREATE` | `UDINT` | `16#70000` | `FB_DBCreate` 内部 ADS IGR。 |
| `DBADS_IGR_DBRECORDSELECT` | `UDINT` | `16#80001` | `FB_DBRecordSelect` / `_EX` 内部 ADS IGR。 |
| `DBADS_IGR_DBRECORDINSERT` | `UDINT` | `16#80002` | `FB_DBRecordInsert` / `_EX` 内部 ADS IGR。 |
| `DBADS_IGR_DBRECORDDELETE` | `UDINT` | `16#80003` | `FB_DBRecordDelete` 内部 ADS IGR。 |
| `DBADS_IGR_DBAUTHENTIFICATIONADD` | `UDINT` | `16#90000` | `FB_DBAuthentificationAdd` 内部 ADS IGR（obsolete）。 |

### VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT

不适用——本节是 `VAR_GLOBAL CONSTANT` 集合，无函数 / FB 接口。

## 3. 行为说明

**编译期常量**：所有声明都在 `VAR_GLOBAL CONSTANT` 块里——编译器把这些值固化到 PLC 代码中，运行时不可修改。

**`AMSPORT_DATABASESRV = 21372`**：用户代码极少需要直接引用这个端口；库内所有 FB 已封装好。如果业务想绕过库直接用 `ADSWRITE` / `ADSREAD` 直访 Server（不推荐），用本常量作为 `nPort` 入参。

**`MAX_*` 系列上限 = 255**：被库内函数块用于声明它们的输入 / 输出数组上界。用户代码声明对应数组时**必须用相同的上界**——否则会传错指针类型，编译期可能不报错但运行时按错偏移读写。例如：
```iecst
arrCfg : ARRAY[0..MAX_XML_DECLARATIONS] OF ST_DBXMLCfg;   (* 正确 *)
arrCfg : ARRAY[0..20] OF ST_DBXMLCfg;                      (* 错误：FB 内部按 255 偏移读 *)
```

**`DBADS_IGR_*` 一般用户不直访**：这些 ADS Index Group 是 Database Server 的内部分发标识。库内每个 FB 都对应一个 IGR：例如 `FB_DBWrite` 把它读出来的变量值写到 Server 的 `IndexGroup = 16#40000` 上，Server 识别后跑相应处理。直接用 `ADSWRITE` + 这些 IGR 绕过库 FB 是高级用法，不推荐——除非要做自动化测试 / 调试或库 FB 缺某种参数组合。

**值不可被赋值**：编译期 `CONSTANT` 保护；运行期 `arr[0] := 0` 之类会编译报错。

## 4. 错误码 / 返回值

不适用——本节是常量声明，无运行时行为、无错误码。

## 5. 使用注意 / 常见坑

- **数组上界用 `MAX_*` 常量符号而不是 `255`**：可读性更好；万一 Beckhoff 改了上限（未来 TC3 可能扩展），用符号常量自动兼容。
- **`AMSPORT_DATABASESRV` 通常不需要用户引用**：库内 FB 已封装；只有"绕过库直访 Server"才用。
- **`DBADS_IGR_*` 是内部细节**：除非要做协议级调试 / 拓展库；普通业务代码引用了反而暴露内部耦合。
- **常量值不可改**：`VAR_GLOBAL CONSTANT` 编译期定下；不要尝试赋值。
- **`MAX_*` 都是 255**：与 BYTE 范围（0-255）巧合，可能让人误以为是单字节限制；实际只是 Beckhoff 内部选的统一上限。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_AMSPORT_DATABASESRV.TcPOU`](../examples/P_Demo_AMSPORT_DATABASESRV.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上做了一个"ADS 直访调试"页面，技术运维选择"我要直接查 Server 状态"——PLC 用 `ADSREAD(nPort := AMSPORT_DATABASESRV, nIndexGroup := DBADS_IGR_GETSTATE, ...)` 直接读 Server 状态，绕过 `FB_GetStateTcDatabase`，用于排查库 FB 是否有 bug。
- **价值**：高级调试入口；普通业务不需要。数组上限常量则是日常每天都用。
- **替代方案对比**：
  - **硬编码数字**：能用但不可读，库版本升级时可能出错。
  - **本节常量**：标准化、可读、向前兼容。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108063883.html
- **相关 FB / FC**：每个 `DBADS_IGR_*` 对应一个库 FB（见上方速查表）；`MAX_DB_TABLE_COLUMNS` 用于 `FB_DBTableCreate`；`MAX_XML_DECLARATIONS` 用于 `FB_GetDBXMLConfig` / `FB_GetAdsDevXMLConfig`；`MAX_STORED_PROCEDURES_PARAMETERS` 用于 `FB_DBStoredProcedures*` 系列。
