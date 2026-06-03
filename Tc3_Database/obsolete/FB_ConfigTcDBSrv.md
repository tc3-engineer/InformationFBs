# FB_ConfigTcDBSrv

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6184886539.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ConfigTcDBSrv.TcPOU`](../examples/P_Demo_FB_ConfigTcDBSrv.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 TwinCAT Database Server 配置管理 FB（PDF §6.1.4.1.1 / §6.1.4.2.1 / §6.1.4.3.1，三模式同接口）。提供 `Create` / `Read` / `Delete` 三个方法，用法与 `FB_ConfigTcDBSrvEvt` 相同；唯一区别：输出接口用 `ipTcResultEvent : Tc3_EventLogger.I_TcResultEvent`（旧式接口），而现代版用 `ipTcResult : I_TcMessage`。新项目应直接用 `FB_ConfigTcDBSrvEvt`；本 FB 仅维护对早期工程的兼容。

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
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式 Tc3 EventLogger 接口；提供事件详情。注：现代 FB_ConfigTcDBSrvEvt 用 `I_TcMessage`。 |

### VAR_IN_OUT

无。

### Method: `Create`

```iecst
METHOD Create : BOOL
VAR_INPUT
    pTcDBSrvConfig: POINTER TO BYTE;
    cbTcDBSrvConfig: UDINT;
    bTemporary: BOOL := TRUE;
    pConfigID: POINTER TO UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pTcDBSrvConfig` | `POINTER TO BYTE` | - | 配置结构体地址（`T_DBConfig_*`）。 |
| `cbTcDBSrvConfig` | `UDINT` | - | 结构体 SIZEOF。 |
| `bTemporary` | `BOOL` | `TRUE` | TRUE = 仅内存；FALSE = 写 XML。 |
| `pConfigID` | `POINTER TO UDINT` | - | 返回的 hDBID / hAutoLogGrpID。 |

### Method: `Read`

```iecst
METHOD Read : BOOL
VAR_INPUT
    pDBConfig: POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_ConfigDB;
    cbDBConfig: UDINT;
    pAutoLogGrpConfig: POINTER TO ARRAY[1..MAX_CONFIGURATIONS] OF ST_ConfigAutoLogGrp;
    cbAutoLogGrpConfig: UDINT;
    pDBCount: POINTER TO UDINT;
    pAutoLogGrpCount: POINTER TO UDINT;
END_VAR
```

参数同 `FB_ConfigTcDBSrvEvt.Read`。

### Method: `Delete`

```iecst
METHOD Delete : BOOL
VAR_INPUT
    eTcDBSrvConfigType: E_TcDBSrvConfigType;
    hConfigID: UDINT;
END_VAR
```

参数同 `FB_ConfigTcDBSrvEvt.Delete`。

## 3. 行为说明

**与 `FB_ConfigTcDBSrvEvt` 的差异**：方法签名 / 行为 / 状态机 100% 一致；唯一差别是错误诊断接口的类型：本 FB 用 `I_TcResultEvent`（旧接口），Evt 版用 `I_TcMessage`（新接口）。两个接口大致提供相同能力（`RequestEventText` / 事件分类）但方法集略有不同。

**为何 deprecated**：Beckhoff 在 TF6420 1.13+ 版本统一了 EventLogger 接口语义，把所有 FB 改为 `I_TcMessage` 输出。旧 `I_TcResultEvent` 仍可用但已停止增强，新功能（如某些 Severity 分级、跨语言事件文本）只在新接口上更新。

**调用流程**：与 Evt 版完全一致——周期调用方法直到返回 TRUE，检查 `bError`，配合 `ipTcResultEvent.RequestEventText(nLangId, ...)` 取事件文本。

**新项目迁移**：把 `FB_ConfigTcDBSrv` 替换为 `FB_ConfigTcDBSrvEvt`，把 `ipTcResultEvent` 字段换为 `ipTcResult`，类型从 `I_TcResultEvent` 改为 `I_TcMessage`。其他代码不需改动。

**为何还保留在 PDF / 库里**：Beckhoff 保证向后兼容，老 PLC 工程不重新编译也能跑；删 FB 会破坏老工程。

## 4. 错误码 / 返回值

每方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResultEvent` 报实际结果。错误码集合与 Evt 版一致——典型 ADS 错（`0x6` 服务未启 / `0x745` 超时 / `0x712` symbol 不存在）以及 Database Server 内部码（`0x10001+` 编码后的 DB 特有错），完整列表见 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_ConfigTcDBSrvEvt`。
- **`I_TcResultEvent` 接口可能在未来版本失效**：虽然现在还能用，但不保证持续。
- **行为与 Evt 版完全一致**：可以直接套用 Evt 版的所有 §5 注意事项。
- **不能与 Evt 版混用同一连接**：每个 FB 实例独立管理；混用会让某些事件丢失。
- **运行时识别废弃**：本 FB 编译运行无警告（IEC 编译器无 deprecated 标记）；只能靠代码 review 发现。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ConfigTcDBSrv.TcPOU`](../examples/P_Demo_FB_ConfigTcDBSrv.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 项目 2018 年用 TF6420 v1.8 写的 PLC 代码用 `FB_ConfigTcDBSrv` 管 XML 配置。设备出货后 5 年不重新编译就要能在新版 TwinCAT 上跑——这是 Beckhoff 保留 obsolete FB 的目的。本 FB 在新版 TF6420 1.14.1 上仍能正常工作，但功能不再增强。
- **价值**：对老工程的二进制兼容；新项目应迁移到 `FB_ConfigTcDBSrvEvt`。
- **替代方案对比**：
  - **`FB_ConfigTcDBSrvEvt`**（现代版，推荐）：完全等价的接口 + 更新的 EventLogger。
  - **本 FB**：仅老工程兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.1.1 / §6.1.4.2.1 / §6.1.4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6184886539.html
- **相关 FB / FC / DUT**：`FB_ConfigTcDBSrvEvt`（现代版）、`I_TcResultEvent` 与 `I_TcMessage`（新旧接口差异）、`T_DBConfig_*`、`E_TcDBSrvConfigType`、`MAX_CONFIGURATIONS`
