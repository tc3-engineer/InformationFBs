# FB_DBCyclicRdWrt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108024331.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBCyclicRdWrt.TcPOU`](../examples/P_Demo_FB_DBCyclicRdWrt.TcPOU) |

---

## 1. 功能简述

FB_DBCyclicRdWrt **启动 / 停止** Database Server 的"周期读写"功能——Server 后台按 XML 中预配置的 `Symbolgroup`（变量组、采样周期、目标表）周期性地从 ADS 设备读取变量并落库。本 FB 是这个后台引擎的开关：**`bExecute` 上升沿启动周期读写，下降沿停止**（注意这是 PDF 明确指出的双沿语义，与多数 FB 的单上升沿语义不同）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetId;
    bExecute    : BOOL;
    tTimeout    : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID（Database Server 所在）。本机 = `''`。 |
| `bExecute` | `BOOL` | - | **上升沿启动、下降沿停止周期读写**（PDF 原文：a rising edge starts the read/write cycle, while a falling edge stops it）。 |
| `tTimeout` | `TIME` | - | ADS 超时（针对启动 / 停止命令本身，不影响周期采样的超时）。 |

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
| `bError` | `BOOL` | TRUE 表示启动 / 停止失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部错误码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码（DB 拒绝时填充）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**双沿触发语义**：与多数 Beckhoff FB 的"单上升沿触发"不同，本 FB 是开关型：
- `bExecute` 上升沿（FALSE → TRUE）：发送"启动周期读写"命令给 Server
- `bExecute` 下降沿（TRUE → FALSE）：发送"停止周期读写"命令给 Server

业务侧的常见用法是用 `bExecute := bWantLogging;` 直接赋"是否记录"的业务标志位——这样标志位翻转时自动启停。

**周期读写本身在 Server 内运行**：本 FB 只是开关，真正的周期采样、写入、缓冲管理都在 Database Server 后台进程里。本 FB 调完后 PLC 不需要关心采样细节——下一次轮到的变量由 XML 的 Symbolgroup 配置决定（在 XML Configuration File Editor 里设置）。

**`FB_GetStateTcDatabase` 的 `nDevState` Bit1**：检查周期读写是否在跑，用 `nDevState AND 2 = 2`。

**`FB_DBWrite` vs 本 FB**：
- `FB_DBWrite`：PLC 主动触发的单次写入，每次调用写一条；变量名 / 表名灵活；适合不固定的事件型日志
- 本 FB + XML 预配 Symbolgroup：Server 自动周期采样落库，PLC 只开关；性能最高；变量列表固定

**`bBusy` 期间**：启动 / 停止命令本身的处理通常很快（< 50 ms）。

**XML 预配置必须完成**：本 FB 启动时 Server 会读 XML 的 Symbolgroup 配置——如果没配过任何 Symbolgroup（即没指定要采集哪些变量），启动后就什么也不写。运维需事先用 XML Configuration File Editor 配好 Symbol、变量名、AdsID、DBID、写入模式。

**写入模式与 XML 的 LogMode 联动**：XML 中每个变量可配 `ADS_to_DB_APPEND` / `_UPDATE` / `_RINGBUFFER` / `DB_to_ADS`（PDF §6.3）。本 FB 启动后所有变量按各自 LogMode 工作。

## 4. 错误码 / 返回值

| 错误号 | 含义 | 排查 |
|---|---|---|
| `0x6` | Server 未启动 | 启动服务 |
| `0x707` | 设备未就绪（例如 XML 未配 Symbolgroup） | 用 XML Editor 配 Symbolgroup |
| `0x745` | ADS 超时 | 加大 `tTimeout` |
| `0` + `sSQLState` 非 0 | DB 拒绝写入 | 看 sSQLState 详细 |

## 5. 使用注意 / 常见坑

- **双沿触发是关键差异**：不要按 `R_TRIG` 单脉冲触发！直接用业务侧的"是否记录"BOOL 接 `bExecute`：`bExecute := bLoggingEnabled;`。
- **启动后不要每周期触发**：电平保持即可；电平翻转才触发启 / 停。
- **必须先有 XML Symbolgroup 配置**：本 FB 不会自动配，需要 GUI 工具或第三方 XML 工具配好。
- **停止后缓冲不一定立刻 flush**：Server 可能仍有未写完的缓存数据；停止后等 1~2 秒再做"`hDBID` 改配"等破坏性操作。（工程经验补充）
- **`FB_GetStateTcDatabase` 的 Bit1 确认运行**：调本 FB 后建议查一次 `nDevState`，看 Bit1 是否真的置 1；没置 1 说明 XML 配置有问题。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBCyclicRdWrt.TcPOU`](../examples/P_Demo_FB_DBCyclicRdWrt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MES 集成项目——生产线运行时连续记录 50 个工艺参数到 SQL Server，每 100 ms 采样一次。运维用 XML Editor 把 50 个变量配成一个 Symbolgroup，PLC 启动后调本 FB 一次让 Server 跑起来；停止时业务侧把 `bLoggingEnabled` 翻 FALSE 就停。
- **价值**：性能远高于 PLC 主动 `FB_DBWrite`——Server 内部做批量 INSERT、连接复用、缓冲；PLC 几乎无开销。
- **替代方案对比**：
  - **PLC 主动 `FB_DBWrite` 周期触发**：灵活，但每条 ADS round-trip，吞吐量受限；CPU 开销高。
  - **TF3500 Analytics Logger**：付费的高端日志工具，性能更高但代价大。
  - **本 FB + XML Symbolgroup**：性能比 `FB_DBWrite` 高 5~10 倍；适合固定变量集的中等吞吐场景。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.12 / §6.3（Write Direction Mode）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108024331.html
- **相关 FB / FC**：`FB_DBWrite`（PLC 主动版本）、`FB_GetStateTcDatabase`（查 `nDevState` Bit1）、`E_DBWriteModes`（XML 的 LogMode 对应枚举）
