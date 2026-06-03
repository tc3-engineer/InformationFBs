# F_GetVersionTcDatabase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108004491.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcDatabase.TcPOU`](../examples/P_Demo_F_GetVersionTcDatabase.TcPOU) |

---

## 1. 功能简述

F_GetVersionTcDatabase 是 TC2 时代用于读取 Tc2_Database PLC 库自身版本信息的函数（major / minor / revision 三个版本号分量分别读取）。**注**：TC2 时代的"库版本查询函数"风格已在 TC3 中由全局常量 + Tc2_System.F_CmpLibVersion 替代；本函数仅保留在 TS6420 TC2 文档中，TC3（TF6420）InfoSys 已不再列出该入口——所以 `InfoSys-checked` 标 `⚠️ not-on-infosys`。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION F_GetVersionTcDatabase: UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nVersionElement` | `INT` | - | 要读取的版本号分量：`1` = major（主版本号）/ `2` = minor（次版本号）/ `3` = revision（修订号）。 |

### 返回值

| 类型 | 说明 |
|---|---|
| `UINT` | 对应 `nVersionElement` 分量的版本号数值。例如 v1.2 时调用 `F_GetVersionTcDatabase(1)` 返回 `1`、调 `F_GetVersionTcDatabase(2)` 返回 `2`、调 `F_GetVersionTcDatabase(3)` 返回 `0`（PDF 中未细化 revision 字段）。 |

## 3. 行为说明

**调用方式**：同步函数，立即返回。无 ADS 调用、无错误状态。

**典型用法**：PLC 启动时连续调用三次拿到 1/2/3 分量，组合成字串显示在 HMI"系统信息"页；或与业务硬编码的最低要求比较：`IF (F_GetVersionTcDatabase(1) < 1) OR ((F_GetVersionTcDatabase(1) = 1) AND (F_GetVersionTcDatabase(2) < 2)) THEN ... 报错 ... END_IF`——即要求库 ≥ 1.2。

**`nVersionElement` 越界**：传入 `0` / 负数 / `>3` 的值，PDF 没说返回什么。**保守做法是只用 1/2/3**——其它值视为不被支持。

**与 TC3 时代的 `stLibVersion_<Lib>` + `F_CmpLibVersion` 对比**：
- TC2（本函数）：仅返回单个 INT 值；要做版本比较 PLC 自己写 `IF` 逻辑。
- TC3：用 `ST_LibVersion` 结构体常量 + `F_CmpLibVersion(stLibVersion, iMajor, iMinor, iBuild, iRevision, nCmpType)` 标准化比较——更稳健、跨版本兼容性好。
- TC3 工程若想用旧风格：本函数仍然可调（向后兼容），但建议改用新风格。

**`UINT` 返回值范围 0-65535**：版本号实际不会超过这个上限。

## 4. 错误码 / 返回值

本函数无错误码——同步函数、立即返回、不涉及 ADS / DB。

返回值含义参见 §2 表格。`UINT` 返回值范围 0~65535；版本号实际不超过 100。

| nVersionElement | 含义 | Tc2_Database v1.2 返回值 |
|---|---|---|
| `1` | major | `1` |
| `2` | minor | `2` |
| `3` | revision | `0` |
| 其它 | PDF 未定义 | ⚠️ 不要依赖 |

## 5. 使用注意 / 常见坑

- **TC3 工程优先用新风格**：TC3 中很多 Beckhoff 库已不再提供 `F_GetVersion_<Lib>` 入口；统一走 `stLibVersion_<Lib>` 常量 + `F_CmpLibVersion`。
- **`nVersionElement` 限于 1/2/3**：传其它值 PDF 没规范返回值，避免依赖。
- **调用开销可忽略**：纯查表，PLC 周期内调几次都无影响。但版本号是编译期固定值，业务上调一次缓存即可。
- **`UINT` 上限 65535**：版本号不可能撞这个上限，但若 Beckhoff 改命名风格（极少见），最好留点余量。
- **本函数在 TF6420 TC3 InfoSys 已下架**：仅 TC2 时代的 `tcdbserver/html/` 旧 InfoSys 路径有页面，且现已 404。所以本文档 `InfoSys-checked` 标 `⚠️ not-on-infosys`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcDatabase.TcPOU`](../examples/P_Demo_F_GetVersionTcDatabase.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI"系统信息"页要展示当前装的 Tc2_Database 版本号；同时业务代码要求"库 ≥ 1.2"才能用部分新 FB（如 Stored Procedures 系列），不满足版本则跳错误提示。PLC 启动时调本函数三次拿到 major/minor/revision，拼成字串显示并做版本检查。
- **价值**：让客户运维方一眼看到库版本（不用进 TwinCAT XAE 项目检查 References）；让 OEM 代码在不满足最低版本时主动报错，避免运行时 FB 调用失败。
- **替代方案对比**：
  - **TC3 风格的 `stLibVersion_Tc2_Database` 常量 + `F_CmpLibVersion`**：标准化、可跨版本兼容；但 TC2 时代没有此常量。
  - **不查版本**：版本不够时业务功能调用失败，错误隐蔽。
  - **本函数**：TC2 时代的版本查询入口，向后兼容仍可用。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.2.1
- **InfoSys topic**：⚠️ 该函数在 TF6420 TC3 InfoSys 已下架；旧 TC2 路径 `https://infosys.beckhoff.com/content/1033/tcdbserver/html/TcDBServer_F_GetVersionTcDatabase.htm` 现 404。元信息中 `Source InfoSys` 字段指向 TF6420 Tc2_Database 库索引页 `https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108004491.html`（含 Tc2_Database 兼容章节，但不再单列本 FC）。
- **相关 FB / FC**：`Tc2_System.F_CmpLibVersion`（TC3 风格的版本比较）、`Tc2_System.stLibVersion_*`（库版本常量）
