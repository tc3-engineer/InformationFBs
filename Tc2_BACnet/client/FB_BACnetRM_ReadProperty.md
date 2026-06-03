# FB_BACnetRM_ReadProperty

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Acyclic Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_ReadProperty.TcPOU`](../examples/P_Demo_FB_BACnetRM_ReadProperty.TcPOU) |

---

## 1. 功能简述

非循环(acyclic)读远端 BACnet 对象的任意属性。与 `FB_BACnetRM_AI/AV/...` 的周期拉 Present_Value 不同,本 FB 适合按需读罕用属性(High_Limit / Description / Reliability 等)。通过 `iObject` 引用一个已经实例化的 RM 对象(用 ADR() 取地址)指定要读哪个对象。PDF §7.9 / §7.9.1 给完整示例。

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
| 触发 | `bExecute` | `BOOL` | 上升沿触发一次读(读完自动转 FALSE) |
| 目标对象 | `iObject` | `POINTER TO ...` | 用 `ADR(fbRmAi)` 等指向 RM 对象实例 |
| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要读的 BACnet 属性(`PropHighLimit` / `PropReliability` 等) |
| 接收缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | 用 `ADR(fOut)` + `SIZEOF(fOut)` 提供 |
| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化的 完成/忙/错 + 错误码 |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnetRM_ReadProperty` | — | 通过 iObject 指对象 |
| `FB_BACnetRM_ReadPropertyEx` | 增 `eObjType` + `nObjInst` | 直接给对象类型 + 实例号,不必先实例化 RM 对象 |

## 3. 行为说明

上升沿触发:`bExecute := TRUE` 触发一次 RP 请求,stack 发 ReadProperty 服务给 peer,等响应 → 把数据写到 `pData^`(长度 ≤ nData),完成后 `bDone := TRUE` 一个周期 + `bExecute` 自动复位 FALSE(典型的「忙/完成」两态机)。期间 `bBusy := TRUE`,出错时 `bError := TRUE` 且 `nErrorId` 给错误码。`iObject` 必须指向一个 RM 对象(因为 RM 对象自身存了 nObjectInstance 和对应类型),典型用 `fbRead.iObject := fbAI;`(stack 用类型转换自动取 ADR);PDF §7.9.1 示例 `fbRead.iObject := fbAI;` 直接赋值(IEC POINTER 隐式)。`FB_BACnetRM_ReadPropertyEx` 多了 `eObjType` + `nObjInst`,适合「读对端某个对象的属性但 PLC 端不想为该对象专门建一个 RM 实例」的场景(PDF §7.9.2 示例)。

## 4. 错误码 / 返回值

`bError := TRUE` 时 `nErrorId` 包含错误码;⚠️ 具体 BACnet error / abort / reject 码常量集中在 BACnet_Globals 章节,PDF 未在本节列。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`iObject` 不能为 NULL**:必须先实例化 RM 对象再赋给 iObject;PDF §7.9.1 强调「object referenced by iObject must be called cyclically」。
- **`pData` / `nData` 要匹配属性数据类型**:读 REAL 用 `pData := ADR(fOut); nData := SIZEOF(fOut);`;读字符串需要更大缓冲。
- **`bExecute` 是脉冲不是电平**:置 TRUE 触发一次,完成后 stack 自动清,不需要 PLC 复位。
- **大量按需读时考虑用 RPM**:RP 一次一个属性 + 一来回 RTT;RPM 一次多个属性合并请求,慢网段(MS/TP)节省大量时间(PDF §7.12)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_ReadProperty.TcPOU`](../examples/P_Demo_FB_BACnetRM_ReadProperty.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_ReadProperty
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteAI : FB_BACnetRM_AI := (Client := fbClient, nObjectInstance := 1);
    fbRead : FB_BACnetRM_ReadProperty := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    fHighLimit : REAL;
END_VAR

fbClient();
fbDevice();
fbRemoteAI();

fbRead.bExecute := bTrigger;
IF fbRead.bExecute THEN
    bTrigger := FALSE;
    fbRead.iObject := fbRemoteAI;
    fbRead.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbRead.pData   := ADR(fHighLimit);
    fbRead.nData   := SIZEOF(fHighLimit);
END_IF
fbRead();
```

## 7. 业务场景与实际价值

- **场景**:运维偶尔需要读对端设备某个对象的 High_Limit / Reliability / Description,但不想一直周期拉(浪费带宽)。
- **价值**:按需读,典型一次请求 < 1 秒;不污染 client 的周期请求。
- **替代方案对比**:把这些属性也走周期 RM 对象:浪费带宽 + 占 router memory;ReadProperty 按需触发。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.9(Acyclic read)、§7.9.1(完整 ReadProperty 示例)、§7.9.2(ReadPropertyEx 不需要 iObject 的示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnetRM_WriteProperty / WritePropertyEx`(对应的写)、`FB_BACnetRM_AI/AV/...`(被 iObject 引用的 RM 对象)
