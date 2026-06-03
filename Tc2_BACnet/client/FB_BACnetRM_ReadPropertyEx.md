# FB_BACnetRM_ReadPropertyEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Acyclic Read (Ex)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_ReadPropertyEx.TcPOU`](../examples/P_Demo_FB_BACnetRM_ReadPropertyEx.TcPOU) |

---

## 1. 功能简述

非循环读远端 BACnet 对象的任意属性,扩展版 — 比 `FB_BACnetRM_ReadProperty` 多了 `eObjType` 与 `nObjInst`两个引脚,可以直接指定目标对象的类型 + 实例号,无需先在 PLC 端为该对象实例化一个 RM 对象。适合「只读对端某对象一两次,不值得专门建 RM 实例」的场景。PDF §7.9.2 + §7.12(RPM)给完整示例。

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
| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |
| 触发 | `bExecute` | `BOOL` | 上升沿触发一次读 |
| 目标对象类型 | `eObjType` | `E_BACnet_ObjectType` | `ObjAnalogInput` / `ObjBinaryValue` / `ObjMultistateOutput` 等(扩展版相对 ReadProperty 多的引脚) |
| 目标对象实例号 | `nObjInst` | `UDINT` | 远端对象实例号 |
| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要读的属性 |
| 接收缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(fOut)` + `SIZEOF(fOut)` |
| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 同 ReadProperty |

## 3. 行为说明

用法与 `FB_BACnetRM_ReadProperty` 几乎相同 — 上升沿触发,完成后 bDone 置位,bExecute 自动复位。区别仅在「指定目标对象的方式」:ReadProperty 需要先建 RM 对象 → iObject := RM对象;ReadPropertyEx 直接 `eObjType := ObjAnalogInput; nObjInst := 1;`。PDF §7.9.2 示例完整展示 — 读 device 42 的 AI:1 的 LowLimit,本 FB 一行指定 eObjType + nObjInst 即可,无需为 device 42 的 AI:1 建一个常驻 RM_AI 对象。PDF §7.12 示例进一步展示「多个 ReadPropertyEx 实例同时 bExecute,stack 自动合并成 RPM(ReadPropertyMultiple)请求」 — 这是大批量按需读最高效的方式。

## 4. 错误码 / 返回值

`bError := TRUE` 时 `nErrorId` 包含错误码,同 ReadProperty。⚠️ 具体 BACnet error 常量集中在 BACnet_Globals。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`ReadPropertyEx` vs `ReadProperty`**:前者不需要 RM 对象,适合一次性 / 多变目标;后者绑 RM 对象,适合稳定读同一目标的多个属性。
- **多个 ReadPropertyEx 同步触发 + 自动 RPM 合并**:PDF §7.12 示例 `fbReadEx1.bExecute := bRead; fbReadEx2.bExecute := bRead; fbReadEx3.bExecute := bRead;` 同 PLC 周期触发,stack 把三个请求合成一个 RPM 请求(节省 2 个 RTT)。
- **`nData` 必须够大**:读对象 Description / Object_Name 等字符串属性需要 ≥ 64 字节缓冲。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_ReadPropertyEx.TcPOU`](../examples/P_Demo_FB_BACnetRM_ReadPropertyEx.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_ReadPropertyEx
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbReadEx : FB_BACnetRM_ReadPropertyEx := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    fLowLimit : REAL;
END_VAR

fbClient();
fbDevice();

fbReadEx.bExecute := bTrigger;
IF fbReadEx.bExecute THEN
    bTrigger := FALSE;
    fbReadEx.eObjType := E_BACnet_ObjectType.ObjAnalogInput;
    fbReadEx.nObjInst := 1;
    fbReadEx.ePropID := E_BACnet_PropertyIdentifier.PropLowLimit;
    fbReadEx.pData   := ADR(fLowLimit);
    fbReadEx.nData   := SIZEOF(fLowLimit);
END_IF
fbReadEx();
```

## 7. 业务场景与实际价值

- **场景**:运维偶尔要读对端设备一组随机属性,不值得为每个对象建 RM 实例;或者大批量 RPM 高效读取。
- **价值**:比 ReadProperty 少了 RM 对象的实例化负担;多 ReadPropertyEx 同步触发 + 自动 RPM 合并性能极高(PDF §7.12 综合示例)。
- **替代方案对比**:写 SDK 直接发 BACnet 报文:工程师要懂 ASN.1 编码 + RP/RPM 协议格式;ReadPropertyEx 是高层封装,一行解决。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.9.2(ReadPropertyEx 单请求示例)、§7.12(多个 ReadPropertyEx 自动 RPM 合并)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnetRM_ReadProperty`(基础版,需 RM 对象)、`FB_BACnetRM_WriteProperty / WritePropertyEx`(写)
