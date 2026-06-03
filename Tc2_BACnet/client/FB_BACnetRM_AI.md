# FB_BACnetRM_AI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Remote Analog Input` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_AI.TcPOU`](../examples/P_Demo_FB_BACnetRM_AI.TcPOU) |

---

## 1. 功能简述

代表远端 BACnet 设备中一个「Analog Input」对象的引用。Client 端通过本 FB 周期读 / 写 peer 设备的对应对象,把远端 Present_Value 拉到 PLC 内变量(读)或把 PLC 内变量推到远端(写)。命名规则 `FB_BACnetRM_<shortcut>`(PDF §5.3.1 / §7.3)。

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
| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client(必填) |
| 远端对象 | `nObjectInstance` | `UDINT` | 远端对象的实例号 |
| 读模式覆盖 | `eReadMode` | `E_BACnet_CommMode` | 可单独覆盖 client 的全局 eReadMode(PDF §7.2.3 示例) |
| 当前值(只读) | `fPresVal` | `REAL` | Present_Value(stack 周期读后写入) |
| 状态(只读) | `stStatusFlags` | `ST_BACnet_StatusFlags` | Status_Flags(从远端读到的状态字 4 位) |
| 异步操作 | `bExecute` / `pData` / `nData` / `ePropID` | `BOOL` / `POINTER` / `UDINT` / `E_BACnet_PropertyIdentifier` | 配合非循环 ReadProperty / WriteProperty 使用(see FB_BACnetRM_ReadProperty 文档) |

## 3. 行为说明

FB_BACnetRM_Analog 每周期调用一次。stack 按 client 的 tReadCycleTime 周期发`ReadProperty(Present_Value)` 取远端值并写入 `fPresVal`(或在 eCOV / eCovP 模式下订阅 COV)。PLC 端只需读 `fPresVal` 就能拿到远端值。写远端用 `FB_BACnetRM_WriteProperty / WritePropertyEx`(独立 FB,见对应文档)。本 FB 也可以作为 ReadProperty / WriteProperty 的 `iObject` 参数(用 ADR() 取地址),让那两个非循环 FB 知道往哪个对象写。如果 client 的 bConnected = FALSE,stack 自动暂停周期请求,`stStatusFlags.bFault := TRUE`。

## 4. 错误码 / 返回值

无返回值;`stStatusFlags` 暴露远端值的状态(`bInAlarm` 等)。⚠️ PDF + InfoSys 未列具体错误码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **必须每周期 call**:不 call stack 不发周期请求,值不会刷新。
- **`eReadMode` 单独覆盖适合特殊对象**:PDF §7.2.3 示例「设备总体支持 COV 但某个对象不支持」,把该 RM 对象的 eReadMode 单独设回 eRead/eRpm。
- **大量 RM 对象时检查 nMaxParallelRequests**:每个 RM 都按 client 的 tReadCycleTime 发请求,几百个对象同时拉时间会成瓶颈。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_AI.TcPOU`](../examples/P_Demo_FB_BACnetRM_AI.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_AI
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemote : FB_BACnetRM_AI := (Client := fbClient, nObjectInstance := 1);
    val : REAL;
END_VAR
fbClient();
fbDevice();
fbRemote();
val := fbRemote.fPresVal;
```

## 7. 业务场景与实际价值

- **场景**:把远端 BACnet 设备(如西门子 RDG 房间控制器)的 analog input 拉到本机 PLC 用 — 例如把对端房间温度引到本机 PID 做综合控制。
- **价值**:周期拉值 + 状态监控全自动,PLC 端只读一个成员;BACnet 标准跨厂商通用。
- **替代方案对比**:用 ADS / Modbus 跨厂商不通用;BACnet RM 对象一行声明完成对接。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.3(Client POUs 命名规则)、§7.7(client 变量)、§7.9 / §7.10(非循环读 / 写,可指本 FB 作为 iObject)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_AI`(本机 AI)、`FB_BACnetRM_AV` / `BO` / `MI` / `MV`(其它 RM 变体)、`FB_BACnetRM_ReadProperty`(读其它属性)
