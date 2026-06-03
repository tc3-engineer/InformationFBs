# FB_ConfigTcDBSrvEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674371339.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ConfigTcDBSrvEvt.TcPOU`](../examples/P_Demo_FB_ConfigTcDBSrvEvt.TcPOU) |

---

## 1. 功能简述

用 PLC 代码动态读写 TwinCAT Database Server XML 配置文件的功能块（带 Tc3_EventLogger 事件接口，文件名末尾 `Evt` 即「Event 版本」）。提供 `Create` / `Read` / `Delete` 三个方法，可在线增加 / 读取 / 删除数据库连接条目和 AutoLog 组条目，结果通过 `ipTcResult` 暴露 Tc3 EventLogger 消息接口，便于事件分级与日志可视化。在 PDF 的 Configure / PLC Expert / SQL Expert 三个模式章节中均出现同一份接口声明——三处 FB 完全相同，区别只在调用方传入 `pTcDBSrvConfig` 的实际结构体类型（`T_DBConfig_MsSQL` / `_MsCompactSQL` / `_MsAccess` / `_Odbc` / `_ASCII` / `_XML` 等，详见 §6.1.2.1.8）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID: T_AmsNetID := '';
    tTimeout: TIME := T#5S;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | 目标设备 AMS Net ID。空字符串 = 本机。远端 Database Server 填对应控制器 NetID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 调用超时。XML 写入有磁盘 IO，建议保留 5 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResult: Tc3_EventLogger.I_TcMessage;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 任一方法（Create/Read/Delete）执行中保持 TRUE。 |
| `bError` | `BOOL` | 方法执行出错置 TRUE；清错靠下一次成功调用或新方法触发覆盖。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口；`bError = TRUE` 时通过该接口的 `RequestEventText(nLangId, ...)` 取本地化错误文本，比裸 `nErrId` 更易诊断。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | Get / Set | 事件分级过滤阈值，只有严重度高于此值的事件才会进入 TwinCAT 事件系统。默认级别由 Tc3_EventLogger 决定，常用 `TcEventSeverity.Warning` 屏蔽 Verbose / Information。 |

### Method: `Create`

```iecst
METHOD Create : BOOL
VAR_INPUT
    pTcDBSrvConfig: POINTER TO BYTE;
    cbTcDBSrvConfig: UDINT;
    bTemporary: BOOL := TRUE;
    pConfigID: POINTER TO UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pTcDBSrvConfig` | `POINTER TO BYTE` | - | 配置结构体地址（如 `ADR(stMsSqlConfig)`），实际结构需为 `T_DBConfig_*` 之一。 |
| `cbTcDBSrvConfig` | `UDINT` | - | 该结构体字节长度（`SIZEOF(stMsSqlConfig)`）。 |
| `bTemporary` | `BOOL` | `TRUE` | TRUE = 仅放内存，TwinCAT 重启后丢失；FALSE = 写 XML 持久化。 |
| `pConfigID` | `POINTER TO UDINT` | - | 返回新生成的 `hDBID` 或 `hAutoLogGrpID`（写到指针指向的变量）。 |

### Method: `Read`

```iecst
METHOD Read : BOOL
VAR_INPUT
    pDBConfig: POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_ConfigDB;
    cbDBConfig: UDINT;
    pAutoLogGrpConfig: POINTER TO ARRAY[1..MAX_CONFIGURATIONS] OF ST_ConfigAutoLogGrp;
    cbAutoLogGrpConfig: UDINT;
    pDBCount: POINTER TO UDINT;
    pAutoLogGrpCount: POINTER TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDBConfig` | `POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_ConfigDB` | 接收数据库连接配置数组的地址。 |
| `cbDBConfig` | `UDINT` | 数据库配置数组字节大小。 |
| `pAutoLogGrpConfig` | `POINTER TO ARRAY[1..MAX_CONFIGURATIONS] OF ST_ConfigAutoLogGrp` | 接收 AutoLog 组配置数组的地址。 |
| `cbAutoLogGrpConfig` | `UDINT` | AutoLog 组数组字节大小。 |
| `pDBCount` | `POINTER TO UDINT` | 输出实际填入的数据库条目数。 |
| `pAutoLogGrpCount` | `POINTER TO UDINT` | 输出实际填入的 AutoLog 组条目数。 |

### Method: `Delete`

```iecst
METHOD Delete : BOOL
VAR_INPUT
    eTcDBSrvConfigType: E_TcDBSrvConfigType;
    hConfigID: UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eTcDBSrvConfigType` | `E_TcDBSrvConfigType` | 配置类型枚举：`Database`（删除数据库连接）/ `AutoLogGroup`（删除 AutoLog 组）。 |
| `hConfigID` | `UDINT` | 要删除的 `hDBID` 或 `hAutoLogGrpID`。 |

### 关联常量

`MAX_CONFIGURATIONS = 255`（PDF §6.1.3.1）——配置数组上限。

## 3. 行为说明

**调用流程**：声明 FB 实例（构造参数即 `sNetID` / `tTimeout`），上电后选择方法调用，每周期调用直到方法返回值变为 `TRUE`（表示方法体执行完毕）。然后检查 `bError`：FALSE = 成功，TRUE = 配合 `ipTcResult.RequestEventText(...)` 取错误描述。`bBusy` 用于面板灯：方法运行中始终亮，结束（成功或失败）灭。

**`Create` 的 `bTemporary` 参数含义**：TRUE = 配置只放在 Server 内存里，重启 TwinCAT 后丢失；FALSE = 写入 XML 文件 `C:\TwinCAT\Functions\TF6420-Database-Server\Win32\TcDbSrv.xml`，永久生效。OEM 设备首次部署用 FALSE；试验性配置 / 短期连接用 TRUE。

**配置结构体选择**：`pTcDBSrvConfig` 是裸 BYTE 指针，Server 通过 `cbTcDBSrvConfig` 长度判断结构类型。调用方必须传入与目标数据库类型匹配的结构（MS SQL → `T_DBConfig_MsSQL`，SQLite → `T_DBConfig_SQLite`，ASCII → `T_DBConfig_ASCII`，等等，全部在 §6.1.2.1.8）。SIZEOF 大小错配 → Server 把字节按错误模板解析，最终 XML 内出现乱字段。

**模式差异澄清**：PDF 在 §6.1.1.1 Configure mode、§6.1.1.2 PLC Expert mode、§6.1.1.3 SQL Expert mode 三处分别给出本 FB 的章节，但接口与方法签名 100% 一致。区别仅在于：Configure mode 通常配合配置器图形界面下发；PLC Expert mode 配合 `FB_PLCDB*Evt` 系列读写；SQL Expert mode 配合 `FB_SQLDatabaseEvt` 系列自由 SQL。同一 FB 实例可被三种模式混用——本质上就是 XML 配置管理 API，并不绑定到特定上层模式。

**Tc3_EventLogger 集成**：`ipTcResult` 不是传统的 `nErrId : UDINT`，而是 `I_TcMessage` 接口对象。可用 `RequestEventText(nLangId := 1031, ADR(sBuf), SIZEOF(sBuf))` 取德语文本，或 `1033` 取英语；亦可用 `EqualsToEventEntry(...)` 比较具体事件 ID 决定错误恢复策略。`eTraceLevel` 属性筛掉低严重度事件后，调试期的「冗余日志风暴」被自动压制。

**临时配置在线追加的典型时序**：(1) PLC 启动 → `Create` 传入 `bTemporary := TRUE` + `T_DBConfig_MsSQL`，等返回 TRUE；(2) 检查 `bError`，无错则记下 `pConfigID^` 作为 `hDBID`；(3) 后续 `FB_SQLDatabaseEvt.Connect(hDBID)` 即可用该临时配置。整条链路无需提前用配置器准备 XML，适合多车间 / 多设备 IP 动态变化的部署。

## 4. 错误码 / 返回值

每个方法返回 `BOOL`（TRUE = 方法体执行结束，无论成功失败）。错误细节经 `bError` + `ipTcResult` 暴露——`ipTcResult` 是 Tc3 EventLogger 接口，需调 `RequestEventText` 取本地化文本。

PDF §8.1.1（Tc3_Database 错误码）列出的常见事件：

| Event ID（典型） | 含义 | 处理建议 |
|---|---|---|
| `0x100` 段 ADS 错 | Database Server 服务未启动 | 检查 TwinCAT Functions 下 TF6420 服务运行状态 |
| `0x712` symbol not found | 传入的 `hDBID` / `hAutoLogGrpID` 不存在 | 先用 `Read` 列出现有配置 |
| `0x70xxxxx` Database 内部码 | XML 文件写入失败 / 路径无权限 | 检查 `C:\TwinCAT\Functions\TF6420-Database-Server\` 写权限 |
| `0x745` ADS timeout | XML 文件锁定 / 磁盘卡顿 | 加大 `tTimeout`、停用第三方扫描程序 |

完整错误码表见 PDF §8.1.1；用 `ipTcResult.RequestEventText(1033, ...)` 取英文描述比直接查表更省事。

## 5. 使用注意 / 常见坑

- **临时配置不持久化**：`bTemporary := TRUE` 创建的条目只活在 Server 内存里，TwinCAT 重启后丢失。OEM 设备的「真实」连接必须 `bTemporary := FALSE` 才能在断电恢复后还活着。
- **`pTcDBSrvConfig` 必须指向同作用域且持续有效的变量**：Server 异步消费这块内存。不能用临时栈变量。建议放在 PLC 程序的 VAR 区，至少在 `bBusy` 变 FALSE 之前不能被回收。（工程经验补充）
- **`cbTcDBSrvConfig` 必须等于实际结构 SIZEOF**：传入 `SIZEOF(stConfigDB)` 而不是固定数；不同 `T_DBConfig_*` 大小不同，写错会被错误解析。
- **`Read` 输出数组的大小**：`pDBConfig` 与 `pAutoLogGrpConfig` 都要预先分配 `ARRAY[1..MAX_CONFIGURATIONS]`（即 255 个槽），`pDBCount^` / `pAutoLogGrpCount^` 才告诉你实际填了几个。
- **`Delete` 删配置后**：已有的 `FB_SQLDatabaseEvt.Connect(hDBID)` 实例不会自动断开；先 `Disconnect` 再 `Delete` 才不会留 ghost 连接。（工程经验补充）
- **`eTraceLevel` 过低会刷屏**：开发阶段设 `TcEventSeverity.Verbose` 拿全量；生产阶段 `Warning` 或 `Error` 才不会把 Tc3 EventLogger 撑满。
- **`Create` 是覆盖语义还是追加？**：覆盖不存在的 ID 即追加；传入已存在 ID → Server 返回错误事件而非默默覆盖。要改配置须先 `Delete` 再 `Create`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ConfigTcDBSrvEvt.TcPOU`](../examples/P_Demo_FB_ConfigTcDBSrvEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机量产线每台机器需要把生产记录写到车间本地 MS SQL Express，而 SQL Server IP 在各车间不同。OEM 不希望每台机器都预装一份带具体 IP 的 XML 配置——开机后用 `FB_ConfigTcDBSrvEvt.Create(bTemporary := FALSE)` 把 HMI 上技师填的 IP / 用户名 / 密码动态写进 XML 配置，下次重启就自带这条连接。
- **价值**：替代「人工编辑 XML 后重启 TwinCAT」的手工部署模式；通过 Tc3 EventLogger 把错误事件直接送到 HMI 操作员可见的事件列表，比裸 `nErrId` 调试体验好得多；事件分级 (`eTraceLevel`) 让生产环境与调试环境共用一份代码而日志量不爆炸。
- **替代方案对比**：
  - **手工编辑 `TcDbSrv.xml`**：单台部署可行，量产 100 台时维护成本爆炸。
  - **配置器（Configurator）图形界面**：依赖 Engineering 工具，工艺工程师在车间没 XAE 也用不了。
  - **本 FB（Evt 版本）**：PLC 代码自管 + EventLogger 错误流水化，是 TF6420 现代版（TwinCAT 3.1 Build 4022.20 起）的官方推荐路径。
  - **旧的 `FB_ConfigTcDBSrv`（不带 Evt 后缀，§6.1.4）**：obsolete；只通过 `nErrId : UDINT` 报错，无法接 EventLogger 事件流。新项目不要再用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.1.1（Configure mode）、§6.1.1.2.1（PLC Expert mode）、§6.1.1.3.1（SQL Expert mode）——三节同一份接口
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674371339.html
- **相关 FB / FC / DUT**：`FB_PLCDBCreateEvt`（用相同 hDBID 做物理建库建表）、`FB_SQLDatabaseEvt.Connect(hDBID)`（消费配置的连接器）、`T_DBConfig_*`（§6.1.2.1.8 全部数据库类型结构体）、`Tc3_EventLogger.I_TcMessage`（消息接口）、`MAX_CONFIGURATIONS`（数组上限 255）、obsolete 版本 `FB_ConfigTcDBSrv`
