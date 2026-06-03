# FB_DBConnectionOpen

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108018187.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBConnectionOpen.TcPOU`](../examples/P_Demo_FB_DBConnectionOpen.TcPOU) |

---

## 1. 功能简述

FB_DBConnectionOpen 显式打开一个已声明的数据库连接（按 `hDBID` 索引）。打开后该连接会**常驻**，后续 `FB_DBWrite` / `FB_DBRead` / `FB_DBRecordInsert*` / `FB_DBRecordSelect*` 调用不需要每次重新连，提升吞吐量。常驻连接用完后需用 `FB_DBConnectionClose` 关闭释放资源。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetId;
    hDBID       : DINT;
    bExecute    : BOOL;
    tTimeout    : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID（Database Server 所在）。本机用 `''`。 |
| `hDBID` | `DINT` | - | 要打开的连接 ID。**注意类型是 `DINT`**（带符号 32 位），与其它 FB 多用的 `UDINT` 不同。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次打开。 |
| `tTimeout` | `TIME` | - | ADS 超时。SQL Server 远端建议 `T#30S`（含 TCP 建连）。 |

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
| `bError` | `BOOL` | TRUE 表示打开失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部错误码混合（PDF §9.1.1 + §9.1.2）。常见 `0x6` Server 未起、`0x6 + 0x70xxxx` DB 拒绝连接。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构体：`sSQLState : STRING(5)` 5 字符 SQL ANSI 状态码 + `nSQLErrorCode : DINT` 数据库特有错误码。成功时 `sSQLState = '00000'`、`nSQLErrorCode = 0`。 |

### VAR_IN_OUT

无。

### 关联结构 `ST_DBSQLError`（PDF §7.3.4）

```iecst
TYPE ST_DBSQLError :
STRUCT
    sSQLState       : STRING(5);
    nSQLErrorCode   : DINT;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `sSQLState` | `STRING(5)` | 5 字符 SQL ANSI 标准状态码（如 `'08001'` connection failure）。成功 = `'00000'`。 |
| `nSQLErrorCode` | `DINT` | 数据库特有错误码（MS SQL = 4060 / MySQL = 2003 / …）。 |

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。本 FB 是**可选优化**——不调本 FB 直接用 `FB_DBWrite` 也能跑（Server 会每次写时自动连开），但每次连开都有 100~500 ms 的 TCP / OLE DB / ODBC 建连延迟，高吞吐场景累计起来非常慢。本 FB 显式建一个常驻连接，后续读写几乎只剩协议层延迟（个位数 ms）。

**`hDBID` 类型为 `DINT`**：与其它多数 FB 的 `UDINT` 不同。从 `FB_DBConnectionAdd` 拿到的 `hDBID : UDINT` 传入时需要 `UDINT_TO_DINT` 转换（值在合法范围内不会丢失，连接 ID 永远 ≥ 1）。

**何时打开 / 何时关闭**：
- 推荐：PLC init 阶段开 → PLC 主循环里频繁读写 → PLC stop 阶段关
- 反模式：每次 FB_DBWrite 之前开 + 写完关——这样反而比不调本 FB 慢（额外多了 Open/Close 两次 ADS 调用）
- 长时间不用的连接建议关闭，避免 DB 服务器侧的连接资源浪费

**SQL Error vs ADS Error**：`nErrID` 是 ADS 层（连接 ADS Server 拒绝）；`sSQLState` 是 SQL 层（DB 服务器拒绝认证 / 锁定 / 网络断开）。两者要分开看：
- `nErrID = 0x6` → DB Server 服务没启动（ADS 层错）
- `nErrID = 0x745` → ADS 超时
- `nErrID = 0` 但 `sSQLState = '28000'` → SQL 认证失败（用户名 / 密码错）
- `nErrID = 0` 但 `sSQLState = '08001'` → 网络连不通（防火墙、服务器宕机）

**多次 Open 同一连接**：第二次 Open 已开过的连接是合法的，Server 会忽略（或返回成功）。Close 同样幂等。

## 4. 错误码 / 返回值

通过 `bError` + `nErrID` + `sSQLState` 三重输出：

| nErrID（典型） | sSQLState（典型） | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 服务未启动 | 启动 TcDbServer |
| `0x70xxxxx` | （根据 DB） | DB 拒绝连接 | 看 sSQLState 详细 |
| `0` | `08001` | 网络连不通 | 检查服务器 IP / 防火墙 |
| `0` | `28000` | 认证失败 | 检查用户名 / 密码 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

PDF §9.1.3（OleDB Errorcodes）、§9.1.4（ASCII）、§9.1.5（XML）有详细 SQL Error 列表。

## 5. 使用注意 / 常见坑

- **常驻连接占资源**：长时间运行的连接会占 DB 服务器上的连接句柄；SQL Server 默认连接数上限 32767，但实际成本是每连接 1~2 MB 内存。建议每 24 小时 Close + Reopen 一次清理。（工程经验补充）
- **`hDBID` 类型转换**：`UDINT_TO_DINT(udintHDBID)`；UDINT 上限远超 DINT 上限，但实际 ID 永远 ≤ 255。
- **DB 服务器侧的空闲超时**：很多 DB 服务器（如 MySQL `wait_timeout = 28800`、8 小时）会主动关闭长时间空闲连接。空闲超时后下次 Read/Write 会得到错误 → 必须重新 Open。建议加 keep-alive 机制。
- **`sSQLState` 不要用 `=` 比较**：用 `LEFT(sSQLState, 5) = '00000'` 因为有时 Server 会在尾部填空格。（工程经验补充）
- **本 FB 不验证连接配置**：如果 XML 中的 `hDBID` 不存在，错误会以 `0x711`（symbol not found）或类似形式返回。先用 `FB_GetDBXMLConfig` 确认 ID 是否真实存在。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBConnectionOpen.TcPOU`](../examples/P_Demo_FB_DBConnectionOpen.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 控制器每秒钟向 MS SQL 写 100 条工艺参数。若每次 `FB_DBWrite` 都自动连开，每次 ~200 ms 的建连延迟会让吞吐量降到 5 条/秒；用本 FB 在启动时开一次常驻连接，后续每条写入只剩 5~10 ms 协议延迟，吞吐 100 条/秒以上。
- **价值**：高吞吐场景下 10~50 倍性能提升；同时降低 DB 服务器侧的连接建立开销。
- **替代方案对比**：
  - **不用本 FB（每次 Write 自动连）**：低吞吐场景可以，每秒 1 条以下；高吞吐死活做不到。
  - **`FB_DBCyclicRdWrt`**：Server 端周期采样，性能最高但配置受限于 XML 预定义。本 FB 适合 PLC 主动写、变量 / 表灵活的场景。
  - **本 FB**：手动管理常驻连接的最简方案。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108018187.html
- **相关 FB / FC / DUT**：`FB_DBConnectionClose`（配对关闭）、`FB_DBWrite` / `FB_DBRead`（受益方）、`ST_DBSQLError`（错误结构）、`FB_DBConnectionAdd`（创建条目）
