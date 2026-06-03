# FB_DBReloadConfig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108008971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBReloadConfig.TcPOU`](../examples/P_Demo_FB_DBReloadConfig.TcPOU) |

---

## 1. 功能简述

FB_DBReloadConfig 触发 TwinCAT Database Server 重新加载磁盘上的 XML 配置文件（默认 `C:\TwinCAT\TcDatabaseSrv\Config\TcDbSrv.xml`）。当通过外部工具（XML Configuration File Editor）或文本编辑器修改了 XML 之后，必须调一次本 FB 让 Server 把改动应用到运行时——否则 Server 仍按旧配置工作，新加的数据库 / 表 / 周期日志组都不会生效。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次重载请求；调用期间保持高电平直到 `bBusy` 落沿。 |
| `tTimeout` | `TIME` | - | ADS 调用超时时长。Beckhoff 例程多用 `T#15S`；XML 文件较大时建议加到 30 秒。 |

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
| `bBusy` | `BOOL` | TRUE 表示重载请求正在 Server 上处理；高电平期间不接受新触发。 |
| `bError` | `BOOL` | TRUE 表示重载失败，错误号在 `nErrID`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrID` | `UDINT` | 失败时返回 ADS 错误码（PDF §9.1.1）。常见 `0x6` 服务未启动、`0x745` 超时、`0x70D` XML 语法错误。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位为 FALSE。`bExecute` 上升沿后 `bBusy` 立刻置 TRUE 并发出 ADS 请求；Server 收到后会停止当前所有数据库连接、重新解析 XML、重建连接表，然后返回 `bBusy = FALSE`。整个过程对小配置文件通常 <100 ms，对包含 10+ 数据库的大配置可能需要 1~2 秒。

**何时必须重载**：
1. 用 XML Configuration File Editor 改了配置后保存（手动场景）
2. 用 `FB_DBConnectionAdd` / `FB_DBOdbcConnectionAdd` / `FB_AdsDeviceConnectionAdd` 等 FB 写入了新条目（PLC 在线场景）——这些 FB 内部会自动调本 FB 等价操作，但若 PLC 重启后想用最新配置而 Server 仍按缓存的老 XML 跑，就要手动调一次本 FB
3. PLC Boot 时如果不确定 Server 是否已用最新 XML 启动，可以显式调一次保险

**`bBusy` 期间数据库操作的影响**：本 FB 工作时会断开所有现有数据库连接。同周期里如果有 `FB_DBWrite` / `FB_DBRead` 等正在跑的实例，它们会收到 `bError`。业务侧重载期间应抑制其它 DB 操作。

**`nErrID` 区分**：`0x70D`（语法错误）说明 XML 文件被改坏了（标签未闭合 / 属性拼错），Server 拒绝加载；这时需用 XML Editor 重新打开纠正。`0x6` 说明 Server 服务根本没启动，重载请求无人响应。

## 4. 错误码 / 返回值

本 FB 通过 `bError` + `nErrID` 输出报告错误：

- `bError = FALSE` 且 `nErrID = 0`：重载成功，新 XML 已生效。
- `bError = TRUE`：重载失败，错误号在 `nErrID`（ADS Return Codes，PDF §9.1.1）。

常见错误号：

| 错误号（十六进制） | 含义 | 排查建议 |
|---|---|---|
| `0x6` | 目标端口未找到 | 启动 TwinCAT Database Server 服务 |
| `0x7` | 目标机器未找到 | 添加 AMS 路由 |
| `0x70D` | XML 语法错误 | 用 XML Editor 检查标签 / 属性是否闭合 |
| `0x745` | ADS 通讯超时 | 大 XML 文件加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **重载会断开所有连接**：所有用 `FB_DBConnectionOpen` 显式打开的 `hDBID` 会失效，重载后需要重新 Open。批量重载场景建议先关闭 cyclic logging（`FB_DBCyclicRdWrt` 落沿）。
- **`0x70D` 检查清单**：XML 字符编码（UTF-8 vs ANSI）、特殊字符没转义（`&` / `<` / `>`）、属性引号配对、结束标签拼写。Beckhoff 自带的 XML Editor 会自动校验；手工编辑 XML 出错率高。（工程经验补充）
- **远端目标的 XML 在远端**：`sNetID` 填远端时，Server 读的是远端机器上的 XML 文件，本机的 XML 改了不会影响远端。（工程经验补充）
- **PLC 不必周期调用本 FB**：每次 PLC 启动调一次就够，重载是"事件触发"而非"状态保持"。错误地周期触发会反复断开数据库连接。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBReloadConfig.TcPOU`](../examples/P_Demo_FB_DBReloadConfig.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上有"重新加载数据库配置"按钮，运维改完 XML 文件（加了一个新的 MS SQL 数据库连接）后点这个按钮——背后就是本 FB 触发一次 ADS 重载。
- **价值**：相比"重启 TwinCAT 系统"或"重启 Database Server 服务"——本 FB 是热重载，PLC 不掉电、其它非 DB 业务不受影响，只是 DB 连接重建一次。
- **替代方案对比**：
  - **重启 Database Server 服务**：粗暴但可靠；适合 XML 改动巨大（连接类型变了）的场景。
  - **重启 TwinCAT 系统**：更粗暴，PLC 全停。一般不该走到这里。
  - **`FB_DBConnectionAdd` 加新连接**：增量改动，不需要本 FB；改动是结构性的（删除 / 改连接串）则必须重载。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108008971.html
- **相关 FB / FC**：`FB_DBConnectionAdd`（新增 DB 连接到 XML）、`FB_DBOdbcConnectionAdd`（新增 ODBC 连接）、`FB_AdsDeviceConnectionAdd`（新增 ADS 设备）、`FB_GetStateTcDatabase`（重载完查一次状态确认 Server 在跑）
