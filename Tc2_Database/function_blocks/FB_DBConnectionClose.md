# FB_DBConnectionClose

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108019723.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBConnectionClose.TcPOU`](../examples/P_Demo_FB_DBConnectionClose.TcPOU) |

---

## 1. 功能简述

FB_DBConnectionClose 关闭一个之前用 `FB_DBConnectionOpen` 显式打开的常驻数据库连接，释放 Database Server 与 DB 服务器之间的会话资源。建议每个 `FB_DBConnectionOpen` 都配一个 `FB_DBConnectionClose`——PLC 停机、定期重连维护、或切换数据库前都应调用本 FB。

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
| `hDBID` | `DINT` | - | 要关闭的连接 ID（与 `FB_DBConnectionOpen` 时一致）。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次关闭。 |
| `tTimeout` | `TIME` | - | ADS 超时，`T#15S` 通常够。 |

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
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示关闭失败。 |
| `nErrID` | `UDINT` | ADS 错误码（PDF §9.1.1）。`0x6` Server 未起。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 关闭与该 `hDBID` 对应的 DB 会话。

**与 `FB_DBConnectionOpen` 配对使用**：每个 Open 都应有对应的 Close。典型场景：
- PLC 启动 → Open
- PLC 主循环里频繁读写
- PLC 停机 / 切换 DB / 重新加载配置前 → Close
- PLC 重新启动 → Open

**关闭已关闭的连接**：本 FB 通常对未打开 / 已关闭的 `hDBID` 也是幂等的——不会报错，直接返回成功。但是 Server 不同版本行为可能微妙不同；保险起见调用前先用业务标志位记住"是否打开过"。

**关闭后 `hDBID` 仍可重新 Open**：连接关闭只是释放会话，`hDBID` 本身（在 XML 配置中的条目）仍然存在，可随时 Reopen。要彻底删除条目需要修改 XML + `FB_DBReloadConfig`。

**`FB_DBReloadConfig` 隐式关闭所有连接**：重载 XML 会强制断开所有 Open 的连接，下次访问需重 Open。

**`bExecute` 上升沿触发原则**：本 FB 不是状态保持型，是事件触发型。`bExecute := TRUE` 持续高电平不会反复关闭，只触发一次。

## 4. 错误码 / 返回值

通过 `bError` + `nErrID` 输出：

| 错误号 | 含义 | 排查 |
|---|---|---|
| `0x0` | 成功（连接已关） | - |
| `0x6` | Server 服务未启动 | 启动服务 |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

DB 服务器侧的关闭错误（罕见）会通过 ADS 错误码包装返回。

## 5. 使用注意 / 常见坑

- **PLC 停机前一定要 Close**：未关的常驻连接会一直占 DB 服务器侧的句柄；多个 PLC 启停循环后服务器可能因连接耗尽而拒绝新连接（特别是 SQL Express 限制 10 用户）。可放在 PLC 全局 OnStop 钩子或专门的状态机里。（工程经验补充）
- **Close 时不要还有进行中的 Read/Write**：等所有 DB 操作 FB 的 `bBusy = FALSE` 后再 Close。否则可能导致丢数据 / 错误状态。（工程经验补充）
- **关闭后业务侧的 `bConnReady` 必须翻 FALSE**：避免 `FB_DBWrite` 等仍以"连接开着"为前提调用，会得到错误。
- **不要在主循环里周期 Close**：本 FB 应当是事件触发（PLC 停机 / 切 DB），不要每周期触发——会反复 Close/Open 把性能彻底毁掉。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBConnectionClose.TcPOU`](../examples/P_Demo_FB_DBConnectionClose.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 控制器上 PLC 关闭时（操作员按 HMI"停机"按钮，触发 PLC 进入 SHUTDOWN 状态机）需要把常驻 DB 连接干净关闭，避免下次启动时 DB 服务器报"连接句柄超限"。
- **价值**：保护 DB 服务器资源；让多次启停循环可重复；满足 SQL Express 等连接受限的小型 DB 部署。
- **替代方案对比**：
  - **不显式 Close（让 OS 强制断开）**：能用，但 DB 服务器在 keepalive 超时（一般 30 秒~2 分钟）才察觉连接失效；连续启停容易超连接数限制。
  - **`FB_DBReloadConfig`**：会隐式关所有连接，但代价是要等 Server 重新解析 XML（100~500 ms），过重。
  - **本 FB**：精确关单个连接，开销小。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108019723.html
- **相关 FB / FC**：`FB_DBConnectionOpen`（配对开）、`FB_DBReloadConfig`（隐式关全部）、`FB_DBWrite` / `FB_DBRead`
