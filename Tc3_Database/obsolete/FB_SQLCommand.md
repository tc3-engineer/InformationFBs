# FB_SQLCommand

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/9007205438842123.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLCommand.TcPOU`](../examples/P_Demo_FB_SQLCommand.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 SQL Expert mode SQL 命令 FB（PDF §6.1.4.3.3）。使用前必须先由 `FB_SQLDatabase.CreateCmd` 绑连接。提供 `Execute`（不返回数据）和 `ExecuteDataReturn`（返回数据集到 `FB_SQLResult`）两个方法。行为与 `FB_SQLCommandEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新），以及 `ExecuteDataReturn` 的 `pSQLDBResult` 类型指向 `FB_SQLResult`（obsolete）而非 `FB_SQLResultEvt`。新项目用 `FB_SQLCommandEvt`。

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
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID（与配套 `FB_SQLDatabase` 同）。 |
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
| `bBusy` | `BOOL` | 任一方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式事件接口。 |

### VAR_IN_OUT

无。

### Method: `Execute`

```iecst
METHOD Execute : BOOL
VAR_INPUT
    pSQLCmd: POINTER TO BYTE;
    cbSQLCmd: UDINT;
END_VAR
```

参数同 `FB_SQLCommandEvt.Execute`——执行任意 SQL 命令字符串。

### Method: `ExecuteDataReturn`

```iecst
METHOD ExecuteDataReturn : BOOL
VAR_INPUT
    pSQLCmd: POINTER TO BYTE;
    cbSQLCmd: UDINT;
    pSQLDBResult: POINTER TO FB_SQLResult;
END_VAR
```

注意：`pSQLDBResult` 类型指向 obsolete `FB_SQLResult`，与 Evt 版的 `FB_SQLResultEvt` 不同。

## 3. 行为说明

与 `FB_SQLCommandEvt` 完全一致的行为语义——必须先由 `FB_SQLDatabase.CreateCmd(ADR(thisFb))` 绑定连接才能用；`Execute` 用于 INSERT / UPDATE / DELETE / DDL 不返回结果集的场景；`ExecuteDataReturn` 用于 SELECT，结果由 Server 缓存到 obsolete 版的 `FB_SQLResult` 实例供后续读取。本 FB 不支持 SQL 占位符——调用方拼好完整 SQL 字符串。同一 `FB_SQLCommand` 实例可反复 Execute 不同 SQL 复用同一连接，无需重新 CreateCmd。

**与 Evt 版差别**：(1) 输出接口字段名 / 类型 `ipTcResultEvent : I_TcResultEvent`（vs 新版 `I_TcMessage`）；(2) `ExecuteDataReturn` 的 `pSQLDBResult` 指向 `FB_SQLResult`（obsolete）而非 `FB_SQLResultEvt`，两套互不兼容。新项目迁移除替换 FB 类型外还要把 Result FB 类型同步换。

**为何保留**：Beckhoff 向后二进制兼容承诺。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际成败。典型错误：not initialized（忘 CreateCmd）、Syntax error、Connection lost、Permission denied。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_SQLCommandEvt`。
- **必须先 `FB_SQLDatabase.CreateCmd` 绑连接**：否则 Execute 报「未初始化」。
- **`ExecuteDataReturn` 的 Result 实例必须是 obsolete `FB_SQLResult`**：不能传 Evt 版。
- **行为细节与 Evt 版完全一致**：套用所有 §5 注意事项。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLCommand.TcPOU`](../examples/P_Demo_FB_SQLCommand.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 高吞吐 SQL 写入模块用本 FB 配 `FB_SQLDatabase` 长连接。新模块迁移到 Evt 版。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_SQLCommandEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/9007205438842123.html
- **相关 FB / FC / DUT**：`FB_SQLCommandEvt`（现代版）、`FB_SQLDatabase`（必须先 CreateCmd）、`FB_SQLResult`（obsolete 接收结果）
