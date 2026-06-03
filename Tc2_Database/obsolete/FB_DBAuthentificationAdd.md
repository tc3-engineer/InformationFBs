# FB_DBAuthentificationAdd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108038027.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBAuthentificationAdd.TcPOU`](../examples/P_Demo_FB_DBAuthentificationAdd.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃（Obsolete，PDF §7.1.20.1）**。FB_DBAuthentificationAdd 为已声明的数据库连接补充或修改认证信息（用户名 / 密码 / Access 库的 MDW 路径）。新工程应在 `FB_DBConnectionAdd` 创建连接时一并提供认证信息，不再需要后置补充。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetID;
    hDBID           : DINT;
    sDBSystemDB     : T_MaxString;
    sDBUserId       : T_MaxString;
    sDBPassword     : T_MaxString;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `DINT` | - | 已存在的连接 ID。 |
| `sDBSystemDB` | `T_MaxString` | - | 仅 Access 数据库：MDW（工作组安全文件）路径。 |
| `sDBUserId` | `T_MaxString` | - | 数据库登录用户名。 |
| `sDBPassword` | `T_MaxString` | - | 数据库登录密码。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次写入。 |
| `tTimeout` | `TIME` | - | ADS 超时。 |

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
| `bError` | `BOOL` | TRUE 表示失败。 |
| `nErrID` | `UDINT` | ADS 错误码。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃语义**：本 FB 历史上用于"先建连接（无密码），再补认证信息"的两步部署模式。现在 `FB_DBConnectionAdd` 已直接接收 `sDBUserId` / `sDBPassword` / `sDBSystemDB`，一次性建立带认证的连接，不再需要本 FB。

**保留原因**：兼容旧 PLC 代码——TC2 早期项目可能已大量使用本 FB；Beckhoff 在 v1.2 文档中将其列入 Obsolete 但仍保留运行能力，以便老工程升级时不必立刻重写。

**调用方式（兼容用）**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 在 `hDBID` 对应连接的 XML 条目中**覆盖** `sUserId` / `sPassword` / `sSystemDB` 三个字段——并不是追加，是修改。

**为什么应该迁移**：(1) 新代码两次 ADS 调用变一次，性能略好；(2) 减少"凭证后置"带来的"短暂裸连接"风险窗口（XML 中有连接但无密码时 Server 可能尝试无密码登录失败）；(3) 与 `FB_DBOdbcConnectionAdd` 保持接口风格一致。

**`hDBID` 是 `DINT`**：与 `FB_DBConnectionOpen` 同——需 `UDINT_TO_DINT()` 转换。

## 4. 错误码 / 返回值

| 错误号 | 含义 | 排查 |
|---|---|---|
| `0x6` | Server 未启动 | 启动服务 |
| `0x711` | 连接 ID 不存在 | 检查 `hDBID` 是否真实 |
| `0x70D` | XML 写入失败 | 检查权限 |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **新代码不要用本 FB**：用 `FB_DBConnectionAdd` 一步完成。
- **更改密码后所有现有 Open 连接会断**：内部 Server 会用新凭证重连——已 `FB_DBConnectionOpen` 的会话会失效，业务侧需感知并重连。
- **密码明文存 XML**：与 `FB_DBConnectionAdd` 同样的安全考虑。
- **Access MDW 路径**：仅 MS Access 数据库用 `sDBSystemDB`，其它 DB 类型应填空串 `''`，否则可能被误识别。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBAuthentificationAdd.TcPOU`](../examples/P_Demo_FB_DBAuthentificationAdd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护 2015 年部署的老 OEM 设备——该批 PLC 代码用了"先 ConnectionAdd 不带密码、运维上电后再用本 FB 在线补密码"的两步部署。改造时为不破坏既有部署流程，本 FB 仍然支持。新工程应直接用 `FB_DBConnectionAdd` 一步完成。
- **价值（历史）**：兼容老工程，降低升级成本。
- **替代方案对比**：
  - **`FB_DBConnectionAdd` 直接传认证**：✅ 推荐，新工程必走。
  - **本 FB**：仅兼容老工程使用。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.20.1（Obsolete）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108038027.html
- **相关 FB / FC**：`FB_DBConnectionAdd`（新工程推荐）、`FB_DBOdbcConnectionAdd`（ODBC 版）
