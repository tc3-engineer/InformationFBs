# FB_GetAdsDevXMLConfig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108016651.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetAdsDevXMLConfig.TcPOU`](../examples/P_Demo_FB_GetAdsDevXMLConfig.TcPOU) |

---

## 1. 功能简述

FB_GetAdsDevXMLConfig 从 TwinCAT Database Server 当前生效的 XML 配置文件中**读出所有已声明的 ADS Device 条目**（即被 Server 当作数据源去周期采样变量的 ADS 设备列表），填到调用方提供的 `ARRAY[0..MAX_XML_DECLARATIONS] OF ST_ADSDevXMLCfg` 缓冲。是 `FB_GetDBXMLConfig` 的 ADS-Device 版本——前者查"数据库"，本 FB 查"数据源"。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId;
    cbAdsDevCfg     : UDINT;
    pAdsDevCfg      : POINTER TO ARRAY [0.. MAX_XML_DECLARATIONS] OF ST_ADSDevXMLCfg
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机用 `''`。 |
| `cbAdsDevCfg` | `UDINT` | - | 缓冲区字节大小，用 `SIZEOF(arr)`。 |
| `pAdsDevCfg` | `POINTER TO ARRAY [0.. MAX_XML_DECLARATIONS] OF ST_ADSDevXMLCfg` | - | 缓冲区起始地址，用 `ADR(arr)`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次读取。 |
| `tTimeout` | `TIME` | - | ADS 超时，`T#15S` 通常够。 |

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

### 关联结构 `ST_ADSDevXMLCfg`（PDF §7.3.3）

```iecst
TYPE ST_ADSDevXMLCfg :
STRUCT
    sAdsDevNetID    : T_AmsNetID;
    tAdsDevTimeout  : TIME;
    nAdsDevID       : DINT;
    nAdsDevPort     : UINT;
END_STRUCT
END_TYPE
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `sAdsDevNetID` | `T_AmsNetID` | ADS 设备的 AMS Net ID。 |
| `tAdsDevTimeout` | `TIME` | Server 访问该设备的超时（与 `FB_AdsDeviceConnectionAdd` 的 `tADSDevTimeout` 一致）。 |
| `nAdsDevID` | `DINT` | ADS 设备的 ID，可作为 `hAdsID` 用于后续 `FB_DBWrite` 等。 |
| `nAdsDevPort` | `UINT` | ADS 设备端口（PLC=801/851，NC=500，…）。 |

## 3. 行为说明

**调用方式**：与 `FB_GetDBXMLConfig` 完全对称。`bExecute` 上升沿后 Server 把 ADS Device 列表写入 `pAdsDevCfg` 指向的数组，`bBusy` 复位即完成。

**与 `FB_GetDBXMLConfig` 配对使用**：典型 PLC 启动初始化流程：
1. 调本 FB → 拿到 ADS Device 列表 → 按 `sAdsDevNetID` 匹配业务关心的设备（例如某台机床 PLC）→ 取其 `nAdsDevID` 作为 `hAdsID`
2. 调 `FB_GetDBXMLConfig` → 拿到 DB 列表 → 按 `sDBName` 匹配业务目标库 → 取其 `nDBID` 作为 `hDBID`
3. 用 `hAdsID + hDBID` 启动 `FB_DBWrite` / `FB_DBCyclicRdWrt`

**未使用条目判断**：与 `FB_GetDBXMLConfig` 类似，`arr[i].nAdsDevID > 0` 或 `arr[i].sAdsDevNetID <> ''` 判断有效。

**典型用法**：
- HMI 显示"当前 Server 关联了几台 ADS 设备 + 每台的 NetID/Port/超时"
- 添加新设备前去重：`FB_AdsDeviceConnectionAdd` 之前先查
- 代码侧动态拿 `hAdsID` 替代硬编码

## 4. 错误码 / 返回值

通过 `bError` + `nErrID` 输出：

| 错误号 | 含义 | 排查建议 |
|---|---|---|
| `0x6` | DB Server 服务未启动 | 启动服务 |
| `0x70A` | 内存不足 | 检查 `cbAdsDevCfg` |
| `0x70C` | XML 不存在 | 检查路径 |
| `0x705` | 参数大小错 | 用 `SIZEOF(arr)` |
| `0x745` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`cbAdsDevCfg = SIZEOF(arr)`**：与 `FB_GetDBXMLConfig` 同。
- **`MAX_XML_DECLARATIONS = 255` 是上限**：单 Server 最多 255 个 ADS Device，实际使用极少超过 20。
- **再调用前清零**：与 `FB_GetDBXMLConfig` 同——若 XML 配置被改过、删除过条目，缓冲应先 MEMSET 清零再调，避免读到旧值。（工程经验补充）
- **`tAdsDevTimeout` 是 Server 端的超时**：与本 FB 调用的 `tTimeout` 区分。前者影响 Server 周期采样的稳定性，后者影响本次配置查询。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetAdsDevXMLConfig.TcPOU`](../examples/P_Demo_FB_GetAdsDevXMLConfig.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上"数据采集系统设置"页要显示一个表格——当前 Database Server 在跟哪些 ADS 设备通讯（每台 IP / 端口 / 超时）。本 FB 一次查询拿到全部，HMI Repeater 绑定到数组即可。
- **价值**：相比手工维护一份 PLC 内的"已配设备列表"——本 FB 直接读 Server 真实状态，永远与 XML 同步，不会因为 PLC 重启 / XML 改动而失效。
- **替代方案对比**：
  - **PLC 内自维护设备列表**：双份信息源，容易脱钩。
  - **HMI 直接读 XML 文件**：HMI 要装 XML 解析器；且 HMI 一般不该直接碰文件系统。
  - **本 FB**：单源、运行时、跨 ADS 路由通用。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108016651.html
- **相关 FB / FC / DUT**：`FB_GetDBXMLConfig`（同款查 DB 列表）、`ST_ADSDevXMLCfg`（数据结构）、`FB_AdsDeviceConnectionAdd`、`MAX_XML_DECLARATIONS`
