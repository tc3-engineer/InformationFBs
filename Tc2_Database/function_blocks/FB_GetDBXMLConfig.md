# FB_GetDBXMLConfig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108015115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetDBXMLConfig.TcPOU`](../examples/P_Demo_FB_GetDBXMLConfig.TcPOU) |

---

## 1. 功能简述

FB_GetDBXMLConfig 从 TwinCAT Database Server 当前生效的 XML 配置文件中**读出所有已声明的数据库连接条目**，填到调用方提供的 `ARRAY[0..MAX_XML_DECLARATIONS] OF ST_DBXMLCfg` 缓冲里。每条记录含数据库名、表名、`nDBID`（连接 ID）、`eDBType`（类型枚举）。常用于：PLC 启动时获取 `hDBID` 替代硬编码、HMI 显示当前 DB 列表、`FB_DBConnectionAdd` 前去重检查。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId;
    cbDBCfg         : UDINT;
    pDBCfg          : POINTER TO ARRAY [0.. MAX_XML_DECLARATIONS] OF ST_DBXMLCfg
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机用 `''`。 |
| `cbDBCfg` | `UDINT` | - | 缓冲区字节大小，调用方用 `SIZEOF(arr)` 给出。Server 实际写回不会超过这个大小。 |
| `pDBCfg` | `POINTER TO ARRAY [0.. MAX_XML_DECLARATIONS] OF ST_DBXMLCfg` | - | 缓冲区起始地址，调用方用 `ADR(arr)` 给。`MAX_XML_DECLARATIONS = 255`（GVL 常量）。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次读取。 |
| `tTimeout` | `TIME` | - | ADS 超时，`T#15S` 通常足够。 |

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
| `bError` | `BOOL` | TRUE 表示读取失败。 |
| `nErrID` | `UDINT` | ADS 错误码（PDF §9.1.1）。 |

### VAR_IN_OUT

无。

### 关联结构 `ST_DBXMLCfg`（PDF §7.3.2）

```iecst
TYPE ST_DBXMLCfg :
STRUCT
    sDBName     : STRING;
    sDBTable    : STRING;
    nDBID       : DINT;
    eDBType     : E_DBTypes;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `sDBName` | `STRING` | 数据库名（XML 中 `<Database name="...">`）。 |
| `sDBTable` | `STRING` | 默认表名（XML 中 `<Symbolgroup table="...">`）。 |
| `nDBID` | `DINT` | 连接 ID，可作为 `hDBID` 用于后续 `FB_DBRead` / `FB_DBWrite`。 |
| `eDBType` | `E_DBTypes` | 数据库类型枚举。 |

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 解析 XML 并写入缓冲区。注意输出不通过 `bBusy / bError / nErrID` 之外的引脚返回——结果**已经写在调用方提供的 `pDBCfg` 指向的数组里**了。

**缓冲区责任**：`pDBCfg` 的内存必须由调用方提供，且至少能容纳 `MAX_XML_DECLARATIONS = 255` 个 `ST_DBXMLCfg`。建议直接声明 `arr : ARRAY[0..255] OF ST_DBXMLCfg;` + `cbDBCfg := SIZEOF(arr)` + `pDBCfg := ADR(arr)`。

**未使用条目的判断**：Server 只填实际声明的条目，剩余位置保持原值（如果是首次调用就是 0）。判断"该位置有效"的标准方法：`arr[i].nDBID > 0` 或 `arr[i].sDBName <> ''`。

**典型用法**：
1. PLC 启动 → 调本 FB → 遍历数组找到 `sDBName = 'mes_prod'` 的条目 → 取其 `nDBID` 作为后续 `FB_DBWrite` 的 `hDBID` → 避免硬编码 `hDBID = 1`。
2. HMI 上需要"当前已配数据库列表" → 把数组绑定到 HMI Repeater 控件展示。
3. 重复添加防护：调本 FB 后 → 遍历检查 `FB_DBConnectionAdd` 想加的连接是否已存在。

**与 `FB_DBReloadConfig` 配合**：如果刚用 `FB_DBConnectionAdd` 加了新连接想立刻能查到，最好先调一次本 FB——Server 内部已更新，但若一些工具流程导致 XML 与 runtime 不一致，可用 `FB_DBReloadConfig` 强制刷新。

## 4. 错误码 / 返回值

通过 `bError` + `nErrID` 输出：

| 错误号 | 含义 | 排查建议 |
|---|---|---|
| `0x6` | DB Server 服务未启动 | 启动服务 |
| `0x70A` | 内存不足 | 检查 `cbDBCfg` 是否合理 |
| `0x70C` | XML 文件不存在 | 检查 Server 配置路径 |
| `0x705` | 参数大小不正确 | `cbDBCfg` 必须等于实际数组的 `SIZEOF` |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`cbDBCfg` 必须等于 `SIZEOF(arr)`**：填错值会被 Server 拒绝（`0x705`）。**不要**手算字节数，永远用 `SIZEOF`。
- **`MAX_XML_DECLARATIONS = 255`**：单台 DB Server 最多支持 255 个连接。绝大多数项目用不到 10 个；分配 255 大小的数组是 Beckhoff 推荐做法（约 65 KB）。
- **数组未填部分残留旧值**：第二次调用前如果改了 XML 配置（删除了某些条目），调用方应在调本 FB 前 `MEMSET(ADR(arr), 0, SIZEOF(arr))` 清零，避免读到上次的残留。（工程经验补充）
- **`sDBName` / `sDBTable` 字符串截断**：`ST_DBXMLCfg` 用裸 `STRING`（默认 80 字符）。XML 中超长的名字会被截断。
- **本 FB 只查 OLE DB / OCI 类的数据库**：ODBC 数据库可能不显示在 `ST_DBXMLCfg` 里——根据 PDF §6 描述，ODBC 配置存于 XML 的 ODBC 节，但本 FB 同样返回。具体格式以 XML Configuration File Editor 显示为准。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetDBXMLConfig.TcPOU`](../examples/P_Demo_FB_GetDBXMLConfig.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 控制器代码维护时不希望硬编码 `hDBID := 1`——XML 配置可能被重排导致 ID 漂移。启动时调本 FB 查一次，按 `sDBName` 匹配业务数据库（例如 `'mes_prod'`），动态得到正确的 `nDBID`，后续所有 DB 操作都用这个动态值。
- **价值**：相比硬编码——本方案对 XML 改动免疫；HMI 上也能展示当前实际配的 DB 列表，运维直观。
- **替代方案对比**：
  - **硬编码 `hDBID`**：简单粗暴但脆弱；XML 重排 / 中间被删过条目就会指错连接。
  - **`FB_DBConnectionAdd` 每次启动重添**：能用但每次启动都会写 XML，加速文件磨损；且重复添加报 `0x70F`。
  - **本 FB**：只读查询，正确解耦"业务代码"与"配置 ID"。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108015115.html
- **相关 FB / FC / DUT**：`FB_GetAdsDevXMLConfig`（同款查 ADS 设备列表）、`ST_DBXMLCfg`（数据结构）、`E_DBTypes`（枚举）、`FB_DBConnectionAdd`、`FB_DBReloadConfig`、`MAX_XML_DECLARATIONS`（GVL 常量 = 255）
