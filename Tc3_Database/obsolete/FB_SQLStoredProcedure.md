# FB_SQLStoredProcedure

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6184484619.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLStoredProcedure.TcPOU`](../examples/P_Demo_FB_SQLStoredProcedure.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 SQL Expert mode 存储过程执行 FB（PDF §6.1.4.3.5）。使用前必须先由 `FB_SQLDatabase.CreateSP` 绑连接 + 参数描述。提供 `Execute` / `ExecuteDataReturn` / `Release` 三个方法。行为与 `FB_SQLStoredProcedureEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新），以及 `ExecuteDataReturn` 的 `pSQLDBResult` 类型指向 `FB_SQLDBResult`（obsolete 配套）而非 Evt 版的 `FB_SQLDBResultEvt`。新项目用 `FB_SQLStoredProcedureEvt`。

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

### Method: `Execute`

```iecst
METHOD Execute : BOOL
VAR_INPUT
    pParameterStrc: POINTER TO BYTE;
    cbParameterStrc: UDINT;
END_VAR
```

参数同 `FB_SQLStoredProcedureEvt.Execute`——传入参数结构体地址，IN 参数已填，调用后 OUT 参数回填到该结构体。

### Method: `ExecuteDataReturn`

```iecst
METHOD ExecuteDataReturn : BOOL
VAR_INPUT
    pParameterStrc: POINTER TO BYTE;
    cbParameterStrc: UDINT;
    pSQLDBResult: POINTER TO FB_SQLDBResult;
END_VAR
```

注意：`pSQLDBResult` 指向 obsolete 配套的 `FB_SQLDBResult`（专为存储过程结果设计），而非通用 `FB_SQLResult`。Evt 版同理指向 `FB_SQLDBResultEvt`。

### Method: `Release`

`METHOD Release : BOOL` —— 无入参，释放 `CreateSP` 初始化时传入的参数描述。

## 3. 行为说明

与 `FB_SQLStoredProcedureEvt` 完全一致的行为语义——必须先由 obsolete 配套的 `FB_SQLDatabase.CreateSP(sProcName, ADR(aParams), SIZEOF(aParams), ADR(thisFb))` 绑定（CreateSP 可能跨多周期完成）。然后 `pParameterStrc^` 按 `CreateSP` 传入的参数信息数组顺序填字段，调 `Execute` 执行；OUT 参数在 Execute 完成后回填到结构体；要返回结果集用 `ExecuteDataReturn` 配 `FB_SQLDBResult` 实例接收。`Release` 释放参数描述（停用前必做避免 Server 累积内存）。

**与 Evt 版差别**：(1) 输出接口字段名 / 类型 `ipTcResultEvent : I_TcResultEvent`（vs 新版 `I_TcMessage`）；(2) `ExecuteDataReturn` 的 `pSQLDBResult` 指向 `FB_SQLDBResult`（obsolete）而非 `FB_SQLDBResultEvt`。新旧两套独立工作不混用。

**为何保留**：Beckhoff 向后二进制兼容承诺。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际结果。典型错误：not initialized（忘 CreateSP）、Parameter mismatch、Permission denied、Procedure not found。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_SQLStoredProcedureEvt`。
- **必须先 `FB_SQLDatabase.CreateSP` 绑参数描述**：否则报「未初始化」。
- **`pParameterStrc^` 字段顺序与 CreateSP 参数信息顺序严格一致**。
- **`Release` 不调泄漏 Server 描述**：停用前务必调。
- **行为细节与 Evt 版完全一致**：套用所有 §5 注意事项。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLStoredProcedure.TcPOU`](../examples/P_Demo_FB_SQLStoredProcedure.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 工程班次汇总存储过程模块用本 FB；新模块迁移到 Evt 版。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_SQLStoredProcedureEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6184484619.html
- **相关 FB / FC / DUT**：`FB_SQLStoredProcedureEvt`（现代版）、`FB_SQLDatabase`（必须先 CreateSP）、`FB_SQLDBResult`（obsolete 配套）、`ST_SQLSPParameter`
