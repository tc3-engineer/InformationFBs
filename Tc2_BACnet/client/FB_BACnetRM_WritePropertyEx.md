# FB_BACnetRM_WritePropertyEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Acyclic Write (Ex)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_WritePropertyEx.TcPOU`](../examples/P_Demo_FB_BACnetRM_WritePropertyEx.TcPOU) |

---

## 1. 功能简述

非循环写远端 BACnet 对象的任意属性,扩展版 — 比 `FB_BACnetRM_WriteProperty` 多 `eObjType` + `nObjInst`,可以直接指定目标对象的类型 + 实例号,无需在 PLC 端为该对象先实例化 RM 对象。PDF §7.10.2 给完整示例。

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
| 触发 | `bExecute` | `BOOL` | 上升沿触发一次写 |
| 目标对象类型 | `eObjType` | `E_BACnet_ObjectType` | `ObjBinaryOutput` 等 |
| 目标对象实例号 | `nObjInst` | `UDINT` | 远端对象实例号 |
| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要写的属性 |
| 发送缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | 数据 |
| 优先级 | `bPrio` | `BYTE` | BACnet 优先级槽位(同 WriteProperty) |
| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化 |

## 3. 行为说明

用法与 `FB_BACnetRM_WriteProperty` 几乎相同 — 区别在指定目标对象的方式:Ex 版不需要 RM 对象,直接通过 `eObjType + nObjInst` 两个引脚表达对端的对象类型和实例号。PDF §7.10.2 完整示例:写远端 BinaryOutput:1 的 Out_of_Service,只在 ePropID / pData / nData / eObjType / nObjInst 五个引脚配好即可。上升沿触发后 stack 把 pData^ 中的数据按 ePropID 类型序列化发给 peer,等响应后 bDone 置位 + bExecute 自动复位。适合「只写一次某对象、不想专门建 RM 实例」的场景;多个 WritePropertyEx 同步触发理论上可被 stack 合并为 WPM(WritePropertyMultiple)请求。

## 4. 错误码 / 返回值

`bError := TRUE` 时 `nErrorId` 包含错误码,同 WriteProperty。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **WritePropertyEx vs WriteProperty**:前者不需要 RM 对象,适合一次性 / 多变目标;后者绑 RM 对象,稳定写同一目标多个属性时方便。
- **多个 WritePropertyEx 同步触发**:与 ReadPropertyEx 类似,stack 可能合并成 WPM(WritePropertyMultiple);不过本 PDF 未给 WPM 综合示例。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_WritePropertyEx.TcPOU`](../examples/P_Demo_FB_BACnetRM_WritePropertyEx.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_WritePropertyEx
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbWriteEx : FB_BACnetRM_WritePropertyEx := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    bOutOfService : BOOL := TRUE;
END_VAR

fbClient();
fbDevice();

fbWriteEx.bExecute := bTrigger;
IF fbWriteEx.bExecute THEN
    bTrigger := FALSE;
    fbWriteEx.eObjType := E_BACnet_ObjectType.ObjBinaryOutput;
    fbWriteEx.nObjInst := 1;
    fbWriteEx.ePropID := E_BACnet_PropertyIdentifier.PropOutOfService;
    fbWriteEx.pData := ADR(bOutOfService);
    fbWriteEx.nData := SIZEOF(bOutOfService);
END_IF
fbWriteEx();
```

## 7. 业务场景与实际价值

- **场景**:一次性写远端某对象的某个属性,不想为该对象专门建 RM 实例(节省 PLC 内存)。
- **价值**:比 WriteProperty 更轻量;适合大量「一次性」写命令。
- **替代方案对比**:同 WriteProperty,只是省了 RM 对象实例化。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.10.2(WritePropertyEx 完整示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnetRM_WriteProperty`(基础版,需 RM 对象)、`FB_BACnetRM_ReadProperty / ReadPropertyEx`(读)
