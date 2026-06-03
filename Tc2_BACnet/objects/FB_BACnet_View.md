# FB_BACnet_View

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Structured View` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_View.TcPOU`](../examples/P_Demo_FB_BACnet_View.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Structured View」对象类型(BACnet Object_Type = 29 / Structured View)。本对象类型不存任何 Present_Value,它的作用是构建 BACnet 对象的层级视图 / 数据点寻址(DPAD),把 Building → Floor → Zone → Sensor 这种树结构暴露给 BMS,运维端能像浏览文件树一样浏览楼控对象。其它对象通过 `iParent` 引用 View 节点接入树。结合 `\/` 操作符可在 Object_Name / Description / EventMessageTextsConfig 三个字符串属性上做父节点字符串拼接。PDF §6.2.10 / §9.15 详细说明。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;以下表把 PDF/InfoSys 在 §6.1.1 / §6.1.2 / §9.x 提及的成员按 BACnet 标准属性分类整理。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;运行状态以 FB 成员形式暴露,见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | 上一级 View(顶层为空)+ 名称(`\/` 触发拼接) |
| 节点类型 | `eNodeType` | `E_BACnet_NodeType` | Node_Type(`eArea` / `eOrganizational` / `eNetwork` / `eDevice` / `eCollection` 等,决定 BMS 端图标) |

## 3. 行为说明

FB_BACnet_View 每周期调用一次。它本身没有数据语义,只是定义 BACnet 标准的 Structured View 节点。其它对象(包括 View)用 `iParent := fbParentView` 把自己挂到该节点下,形成 BACnet 标准的 DPAD(Data Point Address Description)。`\/` 操作符在 `sObjectName` / `sDescription` / `aEventMessageTextsConfig` 三个字符串属性的首字符出现时,触发父节点对应字符串 + 分隔符 + 本节点字符串的拼接 — PDF §9.15 示例 `fbCabinet := (... sObjectName := '\/Controllers')` 在 Verl/Eiserstr/Floor 2 父链下最终展示为 `Germany.Verl.Eiserstr.Floor 2.Controllers`。System Manager 的树形显示按 `eSymbolName` / `eObjectName` / `eDescription` 三种模式(在 BACnet_Globals 配)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`\/` 拼接只对三个字符串属性生效**:Object_Name / Description / EventMessageTextsConfig;其它字符串属性(如 Device_Type)不参与拼接。
- **顶层 View 不要写 `iParent`**:留空表示根节点(PDF §9.15 `fbGermany` / `fbSwitzerland` / `fbSpain` 示例)。
- **`eNodeType` 不影响数据,只影响 BMS 图标**:`eDevice` 显示设备图标,`eArea` 显示区域图标等。
- **DPAD 的层级深度无硬限,但建议 ≤ 5**:太深会让 BMS 树性能下降。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_View.TcPOU`](../examples/P_Demo_FB_BACnet_View.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_View
VAR
    fbBuilding : FB_BACnet_View := (
        eNodeType := E_BACnet_NodeType.eOrganizational,
        sObjectName := 'BuildingA');
    fbFloor3 : FB_BACnet_View := (
        iParent := fbBuilding,
        eNodeType := E_BACnet_NodeType.eArea,
        sObjectName := '\/Floor3');
    fbAi : FB_BACnet_AI := (
        iParent := fbFloor3,
        sObjectName := '\/Temp',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius);
END_VAR
fbBuilding();
fbFloor3();
fbAi();
```

## 7. 业务场景与实际价值

- **场景**:楼控项目有 2000+ BACnet 对象,运维在 BMS 上要按楼宇 → 楼层 → 区域 → 房间 → 传感器层级浏览,而不是看 2000 行扁平列表。
- **价值**:Structured View 是 BACnet 标准,跨 BMS 通用;一行 `iParent := fbParent` 就建好层级,无需手动配置 BMS 树。
- **替代方案对比**:在 BMS 端手配树:换 BMS 厂商要重做;DPAD 在 PLC 端定义,树结构跟着对象库走。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(View = Structured View)、§6.2.10(DPAD 详解 + `\/` 拼接)、§9.15(完整层级示例)、§9.16(数组初始化下挂 View)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:所有对象 FB 都可通过 `iParent` 挂到 View 下;`FB_BACnet_DynObjectManager`(动态对象 + View 一起管理)
