# BACnet_Globals

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `GVL` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319275659.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_BACnet_Globals.TcPOU`](../examples/P_Demo_BACnet_Globals.TcPOU) |

---

## 1. 功能简述

库级全局变量集合，集中了三类内容：（1）默认适配器与服务器实例 `DefaultAdapter` / `DefaultServer`，单适配器项目零配置可用；（2）BACnet 协议层共用的支持对象类型枚举、Error / Abort / Reject Code 常量；（3）库工具常量如 `nBACnetInstId_Auto`（在动态对象创建时让库自动分配实例号）。整个 BACnet 项目里所有对实例号、协议错误码常量、默认适配器/服务器的引用都从这里走。

## 2. 接口定义

> PDF §5.2.2 仅给出 GVL 的用途说明，未列具体字段。下表整理 PDF 正文及示例代码中确认存在的字段。

### VAR_GLOBAL

```iecst
VAR_GLOBAL
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_GLOBAL` 区；下表整理 PDF 正文（§5.2.2、§5.3.2.1 默认适配器、§8.3 默认实例号常量）以及 §6.2.7、§6.2.8、§6.2.9、§6.11、§8.4 示例代码中确认存在的字段。

### 关键字段

| 名称 | 类型（按 PDF 上下文推断） | 说明 |
|---|---|---|
| `DefaultAdapter` | `FB_BACnet_Adapter` | 默认适配器实例；加入本库即自动生成并循环调用；单适配器项目无需自行声明（PDF §5.3.2.1） |
| `DefaultServer` | `FB_BACnet_Server` | 默认服务器实例；与 `DefaultAdapter` 配对，库内部已自动循环调用 |
| `nBACnetInstId_Auto` | `UDINT` | 实例号"自动分配"哨兵值；`FB_BACnet_DynObjectManager.CreateObject` 调用时传入此值让库自动选一个未占用实例号（PDF §8.4 示例） |

### 协议常量集（位于本 GVL）

PDF §5.2.2 描述本 GVL "specifies global settings like the Default Adapter, BACnet-specific values like supported object types and Error-, Abort- and Reject-Codes"。即：

- 支持对象类型枚举（BACnet 协议标准定义的 25 + 类对象，本库支持哪些在这里声明）
- Error Code 常量（BACnet error class / error code 列表）
- Abort Code 常量（BACnet APDU abort reasons）
- Reject Code 常量（BACnet APDU reject reasons）

⚠️ PDF §5.2.2 / InfoSys 均未在文本中枚举所有具体常量值。需要使用具体协议错误码常量时请在 XAE 中导航 `Tc3_BACnetRev14 / GVLs / BACnet_Globals` 查看完整声明。

## 3. 行为说明

GVL 在库加载时由 TwinCAT 自动初始化。`DefaultAdapter` 与 `DefaultServer` 的"内部自动循环调用"语义意味着：在单适配器项目中，PLC 程序里**不要再写 `BACnet_Globals.DefaultAdapter();`**——重复调度会被 BACnet supplement 视为多重对象访问。要触发默认适配器的运行时方法（`TimeSync` / `StartScan` / `GetDiagnosis`）直接 `BACnet_Globals.DefaultAdapter.TimeSync(...)` 即可，方法本身是一次性事件，不会和内部循环调用冲突。`nBACnetInstId_Auto` 在动态对象创建时**总是首选**：它把"实例号唯一性"责任从用户代码转移给库内部，避免与 System Manager 中静态配置的实例号冲突。要做"协议错误对照"时，把外部读到的错误码与本 GVL 中的命名常量比较（如某条 Abort Code 是否等于 BACnet_Globals 里某个命名常量），不要把数字硬编码进 PLC 程序。

## 4. 错误码 / 返回值

GVL 自身无错误码。其内含的错误码常量是给"BACnet 协议层返回错误时对照用"的。

⚠️ PDF + InfoSys 未在 §5.2.2 列具体的 Error / Abort / Reject Code 常量名表，需在 XAE 中导航查看。

## 5. 使用注意 / 常见坑

- **绝不要再次调用 `DefaultAdapter` / `DefaultServer`**：库内部已周期循环调度，外部再调一次会被 supplement 检测为重复访问错误。
- **多适配器项目需自行声明额外的 `FB_BACnet_Adapter` 实例**：默认适配器只有一个；要接第二、第三块 BACnet 设备（如 MS/TP EL6861 端子）必须自己在 POU 里 `fbExtraAdapter : FB_BACnet_Adapter;` 并每周期手动调用。
- **`nBACnetInstId_Auto` 不能用于静态对象**：本常量只在 `FB_BACnet_DynObjectManager.CreateObject` 时有意义；静态变量区声明 `fbAv : FB_BACnet_AV := (nObjectInstance := BACnet_Globals.nBACnetInstId_Auto)` 的语义未定义（工程经验补充：静态对象的实例号必须固定，否则 BMS 端订阅不稳定）。
- **协议错误码常量名跨版本可能变化**：升级库时如果手工硬编码了 Abort Code 等常量名，重编译可能失败；建议给"项目本地化常量包"做封装层降低耦合（工程经验补充）。
- **GVL 名是 `Tc3_BACnetRev14.BACnet_Globals`**：跨多个 namespace 调用时（如同时引用了 `Tc3_BACnetRev14` 与 `Tc3_BA2_Common`）要带 namespace 前缀，避免符号冲突。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BACnet_Globals.TcPOU`](../examples/P_Demo_BACnet_Globals.TcPOU)

```iecst
PROGRAM P_Demo_BACnet_Globals
VAR
    bTriggerOnce      : BOOL;
    bTimeSyncOk       : BOOL;
    stMasterTime      : ST_BA_DateTime;
    bSavePersist      : BOOL;
    bSaveOk           : BOOL;
END_VAR

IF bTriggerOnce THEN
    bTriggerOnce := FALSE;
    bTimeSyncOk := BACnet_Globals.DefaultAdapter.TimeSync(
                       pDateTime      := ADR(stMasterTime),
                       bSendBroadcast := TRUE);
END_IF

IF bSavePersist THEN
    bSavePersist := FALSE;
    bSaveOk := BACnet_Globals.DefaultServer.SavePersistentStackData();
END_IF
```

## 7. 业务场景与实际价值

- **场景**：单适配器楼控项目中所有运行时 BACnet 方法调用都从 `BACnet_Globals.Default*` 走（PDF §6.2.7、§6.11 示例采用的就是这个写法），不显式声明任何 `FB_BACnet_Adapter` / `FB_BACnet_Server` 实例。
- **价值**：零配置即可用单 BACnet 适配器 + 单 BACnet 服务器，大幅降低简单项目的样板代码；同时为动态对象创建提供 `nBACnetInstId_Auto` 让"实例号唯一性"自动解决。
- **替代方案对比**：
  - 自行实例化 `FB_BACnet_Adapter` / `FB_BACnet_Server`：可行但单适配器项目里增加了两条样板声明 + 两条样板调用
  - 自行选静态实例号：可行但跨项目复用要做编号管理，多人协作容易撞号
  - **本 GVL**：官方默认方式，跨版本兼容

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §5.2.2、§5.3.2.1（默认适配器）、§8.3（实例号自动分配）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319275659.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 GVL**：`BACnet_Param`（项目级参数）、`Version`（库版本声明）
