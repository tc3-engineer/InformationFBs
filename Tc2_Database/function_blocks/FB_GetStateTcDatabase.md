# FB_GetStateTcDatabase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108007435.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetStateTcDatabase.TcPOU`](../examples/P_Demo_FB_GetStateTcDatabase.TcPOU) |

---

## 1. 功能简述

FB_GetStateTcDatabase 通过 ADS 异步查询本机或远端 TwinCAT Database Server 的当前状态，返回 ADS 状态码（`nAdsState`，对应 `ADSSTATE_*` 系列）与 Server 设备状态码（`nDevState`，标识"DB Server 是否启动"和"周期读写是否在跑"）。本 FB 必须周期调用直到 `bBusy` 复位，是 HMI 上"DB 服务在线/离线"指示灯、以及做任何数据库操作前的健康检查的标准入口。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetID;
    bExecute    : BOOL;
    tTimeout    : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标系统的 AMS Net ID 字符串。本机用空串 `''`；远端填对端 AMS Net ID。Database Server 服务必须运行在该目标上。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 状态查询；调用期间保持高电平直到 `bBusy` 落沿。 |
| `tTimeout` | `TIME` | - | ADS 调用超时时长。Beckhoff 例程多用 `T#15S`，跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
    nAdsState   : UINT;
    nDevState   : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示 ADS 请求正在传输中；同周期 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrID`。`bBusy` 复位为 FALSE 后该值才可信。 |
| `nErrID` | `UDINT` | 失败时返回 ADS 错误码（参见 ADS Return Codes，PDF §9.1.1）。 |
| `nAdsState` | `UINT` | ADS 标准状态码：`ADSSTATE_INVALID`=0 / `ADSSTATE_IDLE`=1 / `ADSSTATE_RESET`=2 / `ADSSTATE_INIT`=3 / `ADSSTATE_START`=4 / `ADSSTATE_RUN`=5 / `ADSSTATE_STOP`=6 / `ADSSTATE_SAVECFG`=7 / `ADSSTATE_LOADCFG`=8 / `ADSSTATE_POWERFAILURE`=9 / `ADSSTATE_POWERGOOD`=10 / `ADSSTATE_ERROR`=11。正常运行时为 5（RUN）。 |
| `nDevState` | `UINT` | Database Server 专有状态位掩码：Bit0 (=1) 表示 TwinCAT Database Server 已启动；Bit1 (=2) 表示周期读写功能（`FB_DBCyclicRdWrt`）正在运行。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：本 FB 是异步 ADS 调用包装，必须每个 PLC 周期调用一次直到 `bBusy` 复位为 FALSE。`bExecute` 上升沿后 `bBusy` 立刻置 TRUE 并发出一次 ADS 查询；Database Server 应答返回后 `bBusy` 复位、`bError` 与 `nErrID` 给出结果、`nAdsState` 与 `nDevState` 装载当前状态值。

**`nAdsState` 与 `nDevState` 的语义区分**：`nAdsState` 是所有 ADS 设备都遵循的通用状态机（INVALID / IDLE / INIT / RUN / STOP …），值 5（RUN）说明 ADS 通讯通；`nDevState` 是 Database Server 自定义的位掩码——Bit0=1 表 Server 进程已起、Bit1=1 表周期读写（`FB_DBCyclicRdWrt` 启动后置 1）在跑。两者必须同时为"已启动"状态，业务侧的数据库读写才会成功，否则即使 ADS 通讯通也会得到错误。

**典型调用时机**：PLC 启动 init 阶段、HMI 上"DB 服务状态"指示灯每 1~5 秒轮询一次、或者在批量调用 `FB_DBRead` / `FB_DBWrite` 前做一次预检。`bExecute` 上升沿后通常 1~2 个 PLC 周期内 `bBusy` 复位，本机查询几乎 < 10 ms。

**`bBusy` 期间忽略新触发**：`bBusy = TRUE` 时再次抬高 `bExecute` 不会触发新查询；必须等 `bBusy` 落沿后才能下一次。如果业务需要"持续轮询"，标准模式是 `bExecute := NOT bBusy AND tPoll.Q;`（带定时器节流）而不是周期性硬置高。

**`bError` 复位时机**：调用成功时 `bError = FALSE / nErrID = 0`。失败后下次成功调用 `bError` 自动复位为 FALSE，不需要手动清除。

## 4. 错误码 / 返回值

本 FB 通过 `bError` + `nErrID` 输出报告错误：

- `bError = FALSE` 且 `nErrID = 0`：调用成功，`nAdsState` 与 `nDevState` 可读。
- `bError = TRUE`：调用失败，错误号在 `nErrID`（**ADS Return Codes**，参见 PDF §9.1.1 或本仓库的 ADS 错误码表）。

常见错误号：

| 错误号（十六进制） | 含义 | 排查建议 |
|---|---|---|
| `0x6` | 目标端口未找到（ADS Server 未启动） | 检查 TwinCAT Database Server 服务是否运行 |
| `0x7` | 目标机器未找到（缺 ADS 路由） | 添加 AMS Net ID 路由 |
| `0x745` | ADS 通讯超时 | 检查 sNetID、网络连接、防火墙、`tTimeout` 是否太短 |
| `0x748` | ADS 端口未打开 | 重启 TwinCAT 系统 |

## 5. 使用注意 / 常见坑

- **DB 服务未起时 `nErrID = 0x6`**：第一次调用就拿到 `0x6` 通常是 Database Server 服务未启动（或 AMSPORT_DATABASESRV = 21372 端口被防火墙拦）。先用 Beckhoff 提供的 `TcDbServer.exe` GUI 工具确认服务运行状态。
- **远端目标必须先配 ADS 路由**：`sNetID` 填远端时本机 TwinCAT 路由表里必须有对应条目，否则报 `0x7`。在 TwinCAT System Manager → Routes 里添加。
- **`nDevState` 是位掩码，不是状态机**：判断"周期读写在跑"用 `(nDevState AND 2) <> 0`，不要用 `nDevState = 2`——Bit0 也可能同时为 1。（工程经验补充）
- **不要在 IO 任务里调本 FB**：ADS 调用的延迟可能超过 1 ms，应放在普通 PLC 任务里。（工程经验补充）
- **多实例并发查询同一目标**：多个 `FB_GetStateTcDatabase` 实例同时跑没有问题，但会浪费 ADS 队列槽位；HMI 显示一份状态就够，不需要每个调用点都查。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetStateTcDatabase.TcPOU`](../examples/P_Demo_FB_GetStateTcDatabase.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 工控机上 PLC 启动后，业务代码要把 100 个工艺参数写入 MS SQL；如果 Database Server 服务没起、或者周期读写已经独占了 DB 连接，盲目调 `FB_DBWrite` 会得到一堆错误。先用本 FB 查一次 `nAdsState` 是否 = 5（RUN）+ `nDevState` Bit0 是否 = 1，确认才进入正式写入流程。
- **价值**：替代"先调 FB_DBWrite 看返回错误码再处理"的反应式模式，改为"先 check 再做"的主动式。避免在 HMI 上看到一堆 `0x6` 报警；也避免在网络抖动时把业务流程卡死。
- **替代方案对比**：
  - **不检查直接调 FB_DBWrite**：能用但每个写入操作都要带错误处理；状态查询集中一处更清晰。
  - **用 OS 层 ping / netstat 检查端口**：需要 IT 层权限，PLC 自身不易做到。
  - **本 FB**：唯一 PLC 内可调的、跨本机/远端通用的 DB Server 健康检查入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108007435.html
- **相关 FB / FC**：`FB_DBReloadConfig`（重载 XML 配置）、`FB_DBCyclicRdWrt`（开关周期读写——其状态体现在本 FB 的 `nDevState` Bit1）、`FB_DBConnectionOpen` / `FB_DBConnectionClose`（连接管理）
