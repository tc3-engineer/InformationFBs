# FB_NoSQLObjectId_MongoDB

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5989983371.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NoSQLObjectId_MongoDB.TcPOU`](../examples/P_Demo_FB_NoSQLObjectId_MongoDB.TcPOU) |

---

## 1. 功能简述

NoSQL Expert Mode 下解析 MongoDB ObjectId 的辅助功能块（PDF §6.1.1.4.5.1，归类于 Helper 子节）。MongoDB 给每个文档自动分配 12 字节 ObjectId 作为主键 `_id`；PLC 里通过 `T_ObjectId_MongoDB` 12 字节结构体描述。本 FB 把该 12 字节解析成可读字段（`nId` / `nMachineId` / `nProcessId` / `tTimestamp`）+ 两个字符串转换方法（`ToString` 返回带 `'ObjectId("...")'` 包装的字符串；`ValueOf` 返回纯 24 字符 hex 字符串）。常用于 PLC 端把 MongoDB 返回的 ObjectId 转给 HMI 显示，或解析创建时间用于业务逻辑（ObjectId 头 4 字节是 Unix 时间戳）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ObjectId : T_ObjectId_MongoDB;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ObjectId` | `T_ObjectId_MongoDB` | 12 字节 MongoDB ObjectId 数据类型（PDF §6.1.2.2.3）。 |

### VAR_OUTPUT

无显式 VAR_OUTPUT；本 FB 的输出走属性。

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级。 |
| `nId` | `UDINT` | Non-unique, sequential number ——ObjectId 内嵌的递增序号（不同进程内可能重复，配合 nProcessId 唯一）。 |
| `nMachineId` | `UDINT` | Identification of the machine ——ObjectId 内嵌的写入主机标识（3 字节）。 |
| `nProcessId` | `UINT` | Identification of the writing process ——ObjectId 内嵌的进程 ID（2 字节）。 |
| `tTimestamp` | `DATE_AND_TIME` | Time stamp of the record ——ObjectId 头 4 字节解码后的时间戳。 |

### Method: `ToString`

`METHOD ToString : STRING(36)` —— 返回带类型包装的字符串，如 `'ObjectId("5be15c11afa6ec72b107dafaf")'`（36 字符即包含包装 `ObjectId("..")` 的 10 字符 + 24 字符 hex + 引号）。

### Method: `ValueOf`

`METHOD ValueOf : STRING(24)` —— 返回纯 24 字符 hex 字符串，如 `'5be15c11afa6ec72b107dafaf'`。

### 关联类型 `T_ObjectId_MongoDB`（PDF §6.1.2.2.3）

12 字节描述结构。在 PLC 里作为字节数组或对应结构体使用。从 MongoDB 文档读出后传给本 FB 实例即可解析。

## 3. 行为说明

**MongoDB ObjectId 内部结构**（标准定义）：
- 字节 0-3：Unix 时间戳（big-endian 32 位）→ 本 FB 解码为 `tTimestamp`
- 字节 4-6：机器标识（3 字节）→ `nMachineId`
- 字节 7-8：进程 ID（2 字节）→ `nProcessId`
- 字节 9-11：递增计数（3 字节）→ `nId`

本 FB 把这些字段以属性形式暴露，PLC 读 `fbId.tTimestamp` 即可拿到时间戳，无需自己拆字节。

**两种字符串方法的差异**：
- `ToString` 返回 36 字符——MongoDB shell 显示风格 `ObjectId("5be...faf")`，适合作为日志 / HMI 显示文本。
- `ValueOf` 返回 24 字符——纯 hex，适合作为 KEY 拼接到 URL / SQL 字符串、或与外部 MongoDB 客户端的输出对比。

**实例化方式**：本 FB 是参数化的 FB（PDF 写 `FUNCTION_BLOCK FB_NoSQLObjectId_MongoDB`，构造参数即 `ObjectId`）。声明：`fbId : FB_NoSQLObjectId_MongoDB(ObjectId := stReadObjectId);`。声明后即可访问属性。

**典型用法**：
```iecst
// 从 MongoDB Find 结果拿到 ObjectId
stReadObjectId : T_ObjectId_MongoDB := stReadData._id;
fbId : FB_NoSQLObjectId_MongoDB(ObjectId := stReadObjectId);
sId24Hex := fbId.ValueOf();                   // 24-char hex
dtCreated := fbId.tTimestamp;                 // 文档创建时间
```

**MongoDB 文档创建时间**：因为 ObjectId 头 4 字节是时间戳，本 FB 让 PLC 端不用查 DB 也能知道每条 MongoDB 文档的创建时间——比业务上额外加 `createdAt` 字段省事。

**Tc3_EventLogger**：本 FB 无显式 `bError` / `ipTcResult` 输出 —— 解析操作是同步的，不涉及 ADS 调用。`eTraceLevel` 在 PDF 提到但实际用途有限（解析失败的情况极少）。

## 4. 错误码 / 返回值

本 FB 主要通过属性输出。方法 `ToString` / `ValueOf` 返回 STRING。无 `bError` 形式的错误输出。如果 `ObjectId` 字节数据无效（如全零或非法格式），属性可能输出错误值但无显式报错。调用方应在使用前确认 ObjectId 来源可信（如来自 MongoDB Find 结果）。

## 5. 使用注意 / 常见坑

- **`ObjectId` 必须是合法的 12 字节 MongoDB ObjectId**：随机字节会解析出无意义的时间戳 / 机器 ID，但不会报错。
- **`tTimestamp` 时区**：MongoDB ObjectId 头时间戳是 UTC Unix 时间；本 FB 解码后是 PLC 本地时区还是 UTC？PDF 未明确——建议用前先测试 + 必要时用 `TIMEZONE` 转换。（工程经验补充）
- **`ToString` 36 字符容纳上限**：`ObjectId("...")` 是 36 字符正好，如返回类型 `STRING(36)` 表示有效字符数 36，包含尾部 0 实际占 37。注意 IEC `STRING(36)` 内部能存 36 字符 + 1 字节 null terminator，赋值时不会被截断。
- **`ValueOf` 24 字符就是 ObjectId 的 hex 字符串**：MongoDB 标准格式。可直接用于 `db.collection.findOne({_id: ObjectId("...")})` 风格的查询字符串。
- **跨 MongoDB 实例的 ObjectId 唯一性**：MongoDB 设计上跨实例也唯一（机器 ID + 进程 ID + 计数器），但跨地理分布的多写场景（多个 MongoDB 主节点）有极低概率冲突。一般不用担心。
- **`FB_NoSQLObjectId_MongoDB` 实例无 ADS 通讯**：属于 PLC 本地计算 FB，性能极高（< 1 µs）。
- **PDF 拼写「FB_NoSQLObjecId_MongoDB」**：PDF 6.1.1.4.5.1 节定义里有时拼为 `FB_NoSQLObjecId_MongoDB`（少一个 `t`，可能是 typo），InfoSys 用完整 `FB_NoSQLObjectId_MongoDB`。本仓按 InfoSys 标准命名。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NoSQLObjectId_MongoDB.TcPOU`](../examples/P_Demo_FB_NoSQLObjectId_MongoDB.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MongoDB 存生产工单文档，每条自动有 `_id : ObjectId`。PLC 端从某文档读出 ObjectId 后用本 FB 实例：(1) 通过 `tTimestamp` 属性立即知道这条工单是何时创建（无需在文档里额外存 `createdAt` 字段）；(2) 通过 `ValueOf()` 拿 24-char hex 字符串拼到 HMI URL（如 `http://hmi/order?id=5be...faf`）供操作员点击查详细。
- **价值**：MongoDB 文档创建时间「免费」（不占字段）；与 mongoshell 显示风格一致让运维好对照；纯 PLC 本地计算无 ADS 开销。
- **替代方案对比**：
  - **业务上加 createdAt 字段**：可行但增加文档大小；与 MongoDB 自动机制重复。
  - **PLC 端手工拆 ObjectId 字节**：可行但需对 ObjectId 结构有领域知识；本 FB 一行调用就完成。
  - **本 FB**：TC3 MongoDB ObjectId 解析唯一 FB；NoSQL Expert mode 必备 Helper。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.4.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5989983371.html
- **相关 FB / FC / DUT**：`T_ObjectId_MongoDB`（§6.1.2.2.3，12 字节描述类型）、`FB_NoSQLResultEvt.ReadAsStruct`（如何拿到 ObjectId）、MongoDB ObjectId 标准定义
