# FB_AdsDeviceConnectionAdd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108013579.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AdsDeviceConnectionAdd.TcPOU`](../examples/P_Demo_FB_AdsDeviceConnectionAdd.TcPOU) |

---

## 1. 功能简述

FB_AdsDeviceConnectionAdd 在线向 XML 配置文件中**追加一条 ADS Device 条目**，让 TwinCAT Database Server 能访问该 ADS 设备的变量（用于 `FB_DBWrite` 的 cyclic logging 场景：Server 周期性从远端 ADS 设备读变量值并落库）。本 FB 返回一个 `hAdsId`，是后续 `FB_DBWrite` 入参 `hAdsID` 的值。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetID;
    sADSDevNetID    : T_AmsNetID;
    nADSDevPort     : UINT;
    tADSDevTimeout  : TIME;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | Database Server 所在目标的 AMS Net ID（本机 = `''`）。 |
| `sADSDevNetID` | `T_AmsNetID` | - | **被添加的 ADS 设备**的 AMS Net ID（PLC、CX、外部 ADS 服务器等）。 |
| `nADSDevPort` | `UINT` | - | 该 ADS 设备的端口号（PLC Runtime 1 = 801 / 851，NC = 500，IO = 300）。 |
| `tADSDevTimeout` | `TIME` | - | Database Server 访问该 ADS 设备时使用的超时（区别于本 FB 调用的 `tTimeout`）。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次添加。 |
| `tTimeout` | `TIME` | - | 本 FB 本身的 ADS 超时（写 XML + 装载条目的耗时），通常 `T#15S`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
    hAdsId      : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示添加失败。 |
| `nErrID` | `UDINT` | ADS 错误码（PDF §9.1.1）。 |
| `hAdsId` | `UDINT` | **输出**：新建 ADS 设备条目的 ID，用于 `FB_DBWrite` 的 `hAdsID` 入参。失败时为 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 把新 ADS 设备条目写入 XML 并分配 `hAdsId`。

**与 `FB_DBConnectionAdd` 的关系**：`FB_DBConnectionAdd` 加的是「数据库」，`FB_AdsDeviceConnectionAdd` 加的是「数据源」（被读取变量的 ADS 设备）。`FB_DBWrite` 需要两个 ID：`hDBID`（数据库连接）+ `hAdsID`（被读的 ADS 设备），数据流向是 ADS Device 的变量 → Database Server → DB。

**典型链路**：CX 主控 → 通过 ADS 路由读 PLC1（`sADSDevNetID = '1.1.1.1.1.1'`, `nADSDevPort = 851`）的变量值 → 落到 MS SQL。这条链路需要先调本 FB 把 PLC1 注册为 ADS Device，再调 `FB_DBConnectionAdd` 把 MS SQL 注册为数据库，最后用 `FB_DBWrite(hAdsID := <pcl1Id>, hDBID := <sqlId>, ...)`。

**`tADSDevTimeout` vs `tTimeout` 区分**：`tADSDevTimeout` 是 Server 在 cyclic logging 时去读 PLC1 变量的超时（建议 1~5 秒，避免 PLC1 死时拖死 Server）。`tTimeout` 是本 FB 调用本身的超时（写 XML 的时间，通常 15 秒够）。

**本机 ADS Device 的特殊场景**：要让 Server 读取本机 PLC 的变量，`sADSDevNetID` 填本机 NetID（不是空串），`nADSDevPort` 填 851（TC3）或 801（TC2）。

## 4. 错误码 / 返回值

通过 `bError` + `nErrID` 输出 ADS 错误码：

| 错误号 | 含义 | 排查建议 |
|---|---|---|
| `0x6` | DB Server 服务未启动 | 启动服务 |
| `0x7` | 目标机器未找到（Server 所在目标） | 检查 `sNetID` 路由 |
| `0x70D` | XML 写入错 | 检查权限 |
| `0x70F` | ADS Device 已存在 | 用 `FB_GetAdsDevXMLConfig` 查询 |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

ADS Device 本身是否在线（PLC1 是否启动）本 FB 不检查，要在 `FB_DBWrite` 调用时才看到。

## 5. 使用注意 / 常见坑

- **`sNetID` ≠ `sADSDevNetID`**：前者是 Database Server 在哪台机器，后者是数据源 PLC 在哪台。两者经常都填本机或远端，要按业务想清楚。
- **`nADSDevPort` 数字常量**：常用 `AMSPORT_R0_PLC_TC3 = 851`（TC3 PLC）、`AMSPORT_R0_PLC_RTS1 = 801`（TC2 PLC）。这些常量在 Tc2_System 库；如果未引用，直接写数字也可以。
- **`hAdsId` 不要硬编码**：与 `hDBID` 同样的道理，重启后可能重新分配，应在添加后保存。
- **`tADSDevTimeout` 不要太大**：cyclic logging 每周期都会用这个超时，太大（>10 秒）会让一个掉线的 PLC1 拖慢整个 Server。推荐 `T#1S`~`T#3S`。（工程经验补充）
- **ADS 路由必须先配好**：本 FB 只是把 NetID 写到 XML，并不会自动建 ADS 路由。运维必须先在 TwinCAT Routes 中加路由项；否则 Server 后续读不到变量。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AdsDeviceConnectionAdd.TcPOU`](../examples/P_Demo_FB_AdsDeviceConnectionAdd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：车间中央 CX 数据采集站要从 6 台分布式 CX-Slave（每台一台机床）上读取生产计数器变量落到 MS SQL。每台 Slave 调本 FB 一次注册为 ADS Device（`sADSDevNetID = '<slave AMS>'`、`nADSDevPort = 851`）→ 拿到 6 个 `hAdsId` → 配合一个 `hDBID` 就能用 6 个 `FB_DBCyclicRdWrt` 实例分别周期化记录。
- **价值**：相比每台 Slave 自己写 DB 直连——本 FB 把 DB 写入集中到 CX 数据采集站，Slave 只暴露 ADS 变量；网络拓扑简单（Slave 不需要 DB 网络访问）；Slave 死了不影响其它 Slave 和 DB。
- **替代方案对比**：
  - **`FB_DBWrite` 直接在 Slave 上调用**：每台 Slave 都要装 DB Server 客户端 + 自己处理重连；不集中。
  - **OPC UA Aggregator + DB Logger**：能用但要引入 OPC UA 服务，多一层；本方案纯 ADS 简单。
  - **本 FB**：Beckhoff 原生 ADS 数据落库的标准入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108013579.html
- **相关 FB / FC**：`FB_DBConnectionAdd`（加数据库）、`FB_DBWrite`（用 `hAdsID` + `hDBID`）、`FB_GetAdsDevXMLConfig`（查 ADS 设备列表）、`FB_DBCyclicRdWrt`（开关周期日志）
