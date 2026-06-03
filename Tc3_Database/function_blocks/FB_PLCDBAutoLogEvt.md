# FB_PLCDBAutoLogEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674373259.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBAutoLogEvt.TcPOU`](../examples/P_Demo_FB_PLCDBAutoLogEvt.TcPOU) |

---

## 1. 功能简述

AutoLog（自动日志组）控制功能块。AutoLog 是 TwinCAT Database Server 提供的「服务端周期采样 + 批量入库」机制——一旦在配置器或 PLC 中定义好 AutoLog 组（属于哪个 `hDBID`、写哪张表、采样周期、要采集的 ADS 符号列表），Server 进程会以背景线程方式按周期拉取并写库，PLC 几乎无开销。本 FB 是该机制的 PLC 端遥控器：`Start` 启动定义好的全部 AutoLog 组，`Stop` 全部停，`RunOnce` 手动触发某一组立即采样一次（事件触发场景常用），`Status` 查询所有组当前是否在跑（注意 `Status` 有独立的 `bBusy_Status` 标志，可与其他三方法并行调用）。在 PDF 的 Configure mode（§6.1.1.1.2）与 PLC Expert mode（§6.1.1.2.2）两节同样出现——同一 FB 同一接口。

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
| `sNetID` | `T_AmsNetID` | `''` | 目标 Database Server 所在控制器 AMS Net ID；空 = 本机。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 调用超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResult: Tc3_EventLogger.I_TcMessage;
    bBusy_Status: BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | RunOnce / Start / Stop 任一方法执行中 TRUE；`Status` 方法不影响本位。 |
| `bError` | `BOOL` | 错误时 TRUE，配合 `ipTcResult` 取详细事件文本。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口；通过 `RequestEventText` 取本地化错误描述。 |
| `bBusy_Status` | `BOOL` | **专属 `Status` 方法**的忙位。`Status` 与 RunOnce / Start / Stop 可并行调用而互不阻塞——故而独立一个 busy。 |

### VAR_IN_OUT

无。

### Method: `RunOnce`

```iecst
METHOD RunOnce : BOOL
VAR_INPUT
    hAutoLogGrpID: UDINT;
    bAll: BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hAutoLogGrpID` | `UDINT` | 要触发执行一次的 AutoLog 组 ID。 |
| `bAll` | `BOOL` | TRUE = 忽略 `hAutoLogGrpID`，把所有 AutoLog 组各执行一次；FALSE = 只跑指定组。 |

### Method: `Start`

```iecst
METHOD Start : BOOL
```

无入参——启动所有已配置的 AutoLog 组（开始按各自周期循环采集）。

### Method: `Status`

```iecst
METHOD Status : BOOL
VAR_INPUT
    tCheckCycle: TIME;
    pError: POINTER TO BOOL;
    pAutoLogGrpStatus: POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_AutoLogGrpStatus;
    cbAutoLogGrpStatus: UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `tCheckCycle` | `TIME` | Server 内部刷新该状态数组的间隔（PDF 例 `T#30S`）。太短会增加 ADS 流量。 |
| `pError` | `POINTER TO BOOL` | Server 把「任一 AutoLog 组报错」聚合写到该地址（TRUE = 有组在错误状态）。 |
| `pAutoLogGrpStatus` | `POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_AutoLogGrpStatus` | 接收每组运行状态明细的数组地址；含运行标志、累计计数、最后一次错误等。 |
| `cbAutoLogGrpStatus` | `UDINT` | 该数组字节大小。 |

### Method: `Stop`

```iecst
METHOD Stop : BOOL
```

无入参——停止所有 AutoLog 组。

### Properties

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | Get / Set | 事件分级过滤（同 `FB_ConfigTcDBSrvEvt`）。 |

## 3. 行为说明

**AutoLog 的本质**：Server 端运行的「定时采集 + 批量插表」后台任务。一组 AutoLog 配置 = (`hDBID` + 目标表名 + 列定义 + 采样周期 + 要采集的 ADS 符号列表)。配置可在 TF6420 配置器图形界面下发，也可由 `FB_ConfigTcDBSrvEvt.Create` 加 `T_ConfigAutoLogGrp` 结构在 PLC 中动态生成。一旦 `Start` 调用，Server 后台按周期拉数并写库，PLC 程序无需参与每条记录；这是把高频日志采集 offload 到 Server 进程的标准做法。

**`Start` / `Stop` 是全局开关**：影响所有已配置的 AutoLog 组，不能选择性启动单组（PDF 明确）。需要精细控制要么靠「配置时 `bEnabled` 字段」要么靠 `RunOnce`（事件触发型采集）。

**`RunOnce` 的语义**：让指定（或所有）AutoLog 组「立刻执行一次完整采样并入库」。常用于事件型记录——比如急停时把所有过程值快照一次。注意 `RunOnce` 与持续运行的 `Start` 模式可叠加：在 Start 已运行的组上调 RunOnce，会插入一次额外采样，不影响后续周期。

**`Status` 与其他三方法并行**：FB 设计上 `Status` 是「读取状态快照」操作，与 `RunOnce` / `Start` / `Stop` 之间没有 ADS 流量竞争，所以有独立的 `bBusy_Status`。HMI 端可以以 1Hz 周期调 `Status` 不断刷状态显示，同时偶尔通过 `Start` / `RunOnce` 干预，互不阻塞。这点和典型 ADS FB 的「同一实例同时只能跑一个方法」不同。

**`ipTcResult` 的事件分级**：和 `FB_ConfigTcDBSrvEvt` 同理——Tc3 EventLogger 接口，`bError` 为 TRUE 时调 `RequestEventText` 取文本。`eTraceLevel` 设 `Information` 会把每次 Start/Stop 都记下（适合调试），生产期设 `Warning` 或更高。

**典型部署链路**：(1) 配置阶段：用 `FB_ConfigTcDBSrvEvt.Create` 同时建数据库连接和 AutoLog 组配置（或在配置器图形化做）；(2) PLC 启动后 `Start` 让所有 AutoLog 组按各自周期跑；(3) HMI 周期 `Status` 看每组运行情况；(4) 急停事件 `RunOnce(bAll := TRUE)` 强制一次全量快照；(5) PLC 停机或维护模式 `Stop`。

## 4. 错误码 / 返回值

每个方法返回 `BOOL`（TRUE = 方法体执行结束）；`bError` + `ipTcResult` 报实际成败。典型错误见 PDF §8.1.1：

| 现象 | 含义 | 处理 |
|---|---|---|
| `bError = TRUE`，事件文本含 `not found` | `hAutoLogGrpID` 不存在（仅 RunOnce） | 先用 `FB_ConfigTcDBSrvEvt.Read` 列出现有组 |
| `bError = TRUE`，事件含 `connection` | 关联的 `hDBID` 连接失败 | 检查 DB 服务器可达 + 用户名密码 |
| `bError = TRUE`，事件含 `timeout` | `tCheckCycle` / `tTimeout` 太小，或 DB 服务器卡 | 加大对应超时 |
| `pError^ = TRUE`（仅 Status） | 至少一组报错 | 遍历 `pAutoLogGrpStatus^[i]` 找具体组 |

完整错误码见 PDF §8.1.1（Tc3_Database error codes）。

## 5. 使用注意 / 常见坑

- **`Start` 不区分单组**：要让某组不跟随 Start 启动，必须在配置 (`T_ConfigAutoLogGrp`) 中把 `bEnabled` 设 FALSE。Start 后启用 / 禁用单组的官方做法是 `Delete` + `Create` 重建配置。
- **`Status` 的 `pAutoLogGrpStatus` 数组要全 255 槽**：即使只配了 3 组，也要分配 `ARRAY[1..MAX_CONFIGURATIONS]`；Server 不会按实际数量缩小写入范围。
- **`RunOnce(bAll := TRUE)` 在大量组场景代价高**：例如 100 组同时强制采样会让 DB 一瞬间收 100 条 INSERT。事件触发型批量快照前先评估 DB 吞吐。（工程经验补充）
- **`Status` 的 `tCheckCycle` 与 ADS 流量**：太短（如 `T#100MS`）会让 Server 每 100ms 刷新一次状态数组，叠加 HMI 周期读取，ADS 流量被该 FB 吃掉。生产建议 `T#1S` ~ `T#5S`。
- **`bBusy` 与 `bBusy_Status` 是独立的**：可同时 TRUE；监控面板要分别显示两位才不混乱。
- **`hAutoLogGrpID` 与 `hDBID` 不要混淆**：前者是 AutoLog 组 ID，后者是数据库连接 ID。两者各自从 1 编号、独立空间。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBAutoLogEvt.TcPOU`](../examples/P_Demo_FB_PLCDBAutoLogEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：能源监控柜需要把 96 个电表通道每 5 秒采样写入 InfluxDB 做长期趋势分析。如果用 PLC 主动 `FB_DBWrite` 每个通道一条记录，每个周期 96 次 ADS + 96 次 SQL，PLC 主循环吃掉相当时间且 DB 端连接抖动。改用 AutoLog：在配置器里把 96 个 ADS 符号划到 1 组，Server 后台每 5 秒一次性采集 + 批量 INSERT，PLC 端只负责开机调 `Start` 一次，急停时 `RunOnce(bAll := TRUE)` 多记一次快照。
- **价值**：把高频日志的 ADS / SQL 开销从 PLC 主循环 offload 到 Server 进程，PLC 周期时间稳定；批量 INSERT 比逐条快 5-20 倍；HMI 通过 `Status` 拿到组级运行情况，便于监控。
- **替代方案对比**：
  - **`FB_DBWrite` 主动逐条写**：实现简单但高频时 PLC 周期会拖长；每条 ADS + SQL 调用 5~10 ms。
  - **`FB_DBCyclicRdWrt`（Tc2_Database）**：上一代库的等价机制，TC2 项目可用；TC3 新项目优先用本 FB + `FB_ConfigTcDBSrvEvt`。
  - **TF3500 Analytics Logger**：付费插件，性能更高且带流处理，但成本高；普通日志记录用 AutoLog 足够。
  - **本 FB（Evt 版本）**：Server 后台采集的官方控制面板；带 EventLogger 事件诊断。obsolete 版 `FB_PLCDBAutoLog`（无 Evt）只通过 `nErrId : UDINT` 报错，调试不便，新项目应迁移到本 FB。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.1.2（Configure mode）、§6.1.1.2.2（PLC Expert mode）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674373259.html
- **相关 FB / FC / DUT**：`FB_ConfigTcDBSrvEvt`（创建 AutoLog 组）、`ST_AutoLogGrpStatus`（每组状态 §6.1.2.4.9）、`MAX_CONFIGURATIONS`、`Tc3_EventLogger.I_TcMessage`、obsolete `FB_PLCDBAutoLog`
