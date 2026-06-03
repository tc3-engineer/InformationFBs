# FB_SQLResult

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6184299403.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLResult.TcPOU`](../examples/P_Demo_FB_SQLResult.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 SQL Expert mode 结果集读取 FB（PDF §6.1.4.3.4）。配合 obsolete 版的 `FB_SQLCommand.ExecuteDataReturn` 或 `FB_SQLStoredProcedure.ExecuteDataReturn` 使用——Server 把 SELECT 结果缓存到本 FB 实例对应内存，由 `Read` 方法分页读取，`Release` 释放缓存。行为与 `FB_SQLResultEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_SQLResultEvt`。

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
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResultEvent: Tc3_EventLogger.I_TcResultEvent;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式事件接口。 |

### VAR_IN_OUT

无。

### Method: `Read`

```iecst
METHOD Read : BOOL
VAR_INPUT
    nStartIndex: UDINT := 0;
    nRecordCount: UDINT := 1;
    pData: POINTER TO BYTE;
    cbData: UDINT;
    bWithVerifying: BOOL := FALSE;
    bDataRelease: BOOL := TRUE;
END_VAR
```

参数同 `FB_SQLResultEvt.Read`——支持分页 + 类型验证 + 自动 / 手动释放缓存。

### Method: `Release`

`METHOD Release : BOOL` —— 无入参，显式释放 Server 端缓存。

## 3. 行为说明

与 `FB_SQLResultEvt` 完全一致的行为语义——本 FB 实例对应 Server 内的一块结果集缓存（由配套 obsolete `FB_SQLCommand.ExecuteDataReturn` 或 `FB_SQLStoredProcedure.ExecuteDataReturn` 创建）。`Read` 方法按 `nStartIndex` + `nRecordCount` 取一段数据写到 `pData^` 自定义结构数组；`bWithVerifying := TRUE` 让 Server 验证列类型与 PLC 结构匹配并自适应调整（防类型错配时静默写错值）；`bDataRelease := TRUE` 让读完自动释放缓存（一次性读完场景），FALSE 保留供后续分页 Read。`Release` 方法显式释放缓存。

**与 Evt 版差别**：仅输出接口字段名 / 类型不同。其他全部一样——分页模式、类型验证、Release 语义。新项目迁移除替换 FB 类型外，还要把 `ExecuteDataReturn` 的 `pSQLDBResult` 类型同步换为 `FB_SQLResultEvt`。

**为何保留**：Beckhoff 向后二进制兼容。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际结果。典型错误：Cache empty（缓存已释放）、Index out of range、Buffer too small、Type mismatch（关 verifying 时类型不符）。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_SQLResultEvt`。
- **必须先由配套 obsolete FB `ExecuteDataReturn` 绑缓存**：否则 Read 找不到。
- **分页用 bDataRelease := FALSE**：中间 Read 用 FALSE，最后或显式 Release。
- **bWithVerifying := TRUE 防静默错值**：性能损失 < 10%。
- **行为细节与 Evt 版完全一致**：套用所有 §5 注意事项。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLResult.TcPOU`](../examples/P_Demo_FB_SQLResult.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 工程 SQL 查询模块用本 FB 接收结果；新模块迁移到 `FB_SQLResultEvt`。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_SQLResultEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6184299403.html
- **相关 FB / FC / DUT**：`FB_SQLResultEvt`（现代版）、`FB_SQLCommand` / `FB_SQLStoredProcedure`（obsolete 产生方）、`ST_StandardRecord`
