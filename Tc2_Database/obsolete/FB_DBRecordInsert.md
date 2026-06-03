# FB_DBRecordInsert

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108039563.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRecordInsert.TcPOU`](../examples/P_Demo_FB_DBRecordInsert.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃（Obsolete，PDF §7.1.20.2）**。FB_DBRecordInsert 是 INSERT SQL 命令执行 FB 的早期版本——SQL 命令通过 `T_MaxString`（最大 255 字符）的 `sInsertCmd` 参数传入。新工程应改用 `FB_DBRecordInsert_EX`，后者支持 10000 字符的 SQL（通过指针 + 长度方式传入）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetId;
    hDBID       : UDINT;
    sInsertCmd  : T_MaxString;
    bExecute    : BOOL;
    tTimeout    : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `sInsertCmd` | `T_MaxString` | - | INSERT SQL 命令。`T_MaxString` 限 255 字符（TwinCAT 内部约定）；超长 SQL 会被截断。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次插入。 |
| `tTimeout` | `TIME` | - | ADS 超时。 |

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
| `bError` | `BOOL` | TRUE 表示插入失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃原因**：
1. `T_MaxString` 限 255 字符——多列 INSERT、批量 INSERT、含子查询的复杂 INSERT 都装不下。
2. `FB_DBRecordInsert_EX`（PDF §7.1.16）支持 10000 字符，通过 `pCmdAddr` + `cbCmdSize` 指针方式传入；功能完全覆盖本 FB 且无截断限制。

**调用方式（兼容）**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 在 `hDBID` 对应连接执行 `sInsertCmd` 字串。

**典型场景（兼容用）**：旧 OEM 设备的简单单行 INSERT，SQL 拼起来不长（如 `INSERT INTO tLog VALUES (GETDATE(), 'p1', 1.0)`）。

**为什么新代码必须迁移**：新工程或新业务表（如带 NVARCHAR(1000) 长字段）很容易超过 255 字符；用本 FB 写入会截断后变成语法错。

**`sInsertCmd` 长度限制 ≤ 255**：超过会被 IEC `T_MaxString` 截断；Server 收到不完整 SQL 报语法错。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错 / SQL 被截断 | 改用 EX 版 |
| `0x0` | `23000` | 违反约束 | 检查冲突 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **255 字符上限**：业务字段长一点就装不下；新代码必须用 `FB_DBRecordInsert_EX`。
- **PLC 端拼 SQL 仍要转义单引号**：与 EX 版同。
- **不要再写新代码用本 FB**：维护成本高、隐蔽截断 bug。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRecordInsert.TcPOU`](../examples/P_Demo_FB_DBRecordInsert.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护 2014 年部署的老 OEM 设备代码——SQL 都很短（< 200 字符），用本 FB 已稳定运行十年。
- **价值（历史）**：早期 TC2 时代没有 EX 版本时的唯一 INSERT 入口。
- **替代方案对比**：
  - **`FB_DBRecordInsert_EX`**：✅ 新代码必走，支持 10000 字符。
  - **本 FB**：仅维护老代码。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.20.2（Obsolete）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108039563.html
- **相关 FB / FC**：`FB_DBRecordInsert_EX`（推荐替代）、`FB_DBRecordDelete`（DELETE 同款 EX 风格）
