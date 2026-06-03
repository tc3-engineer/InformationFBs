# FB_BACnetRM_WriteProperty

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Acyclic Write` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_WriteProperty.TcPOU`](../examples/P_Demo_FB_BACnetRM_WriteProperty.TcPOU) |

---

## 1. 功能简述

非循环写远端 BACnet 对象的任意属性 — 把 PLC 端数据写到 peer 设备指定对象的指定属性。与 ReadProperty 对称,通过 `iObject` 引用 RM 对象指定写目标。PDF §7.10 / §7.10.1 详述。

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
| 目标对象 | `iObject` | `POINTER TO ...` | 用 `fbWrite.iObject := fbRmBo;` 指定 |
| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要写的属性 |
| 发送缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(val) + SIZEOF(val)` |
| 优先级 | `bPrio` | `BYTE` | 写命令型对象 Present_Value 时使用的 BACnet 优先级槽位(0..16,0 = 不指定,默认 16) |
| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化完成 / 错状态 |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnetRM_WriteProperty` | — | 通过 iObject 指对象 |
| `FB_BACnetRM_WritePropertyEx` | 增 `eObjType` + `nObjInst` | 直接给类型 + 实例号 |

## 3. 行为说明

上升沿触发 — `bExecute := TRUE` 触发一次 WriteProperty 服务,stack 把 `pData^` 中的数据按 ePropID 类型序列化后发给 peer,等响应 → `bDone := TRUE` 一个周期 + `bExecute` 自动复位 FALSE。PDF §7.10.1 示例展示写远端 BinaryOutput:0 的 Out_of_Service := TRUE/FALSE 的过程,只用 ePropID + pData + nData 三行。写命令型对象 Present_Value 时,`bPrio` 指定 BACnet 优先级槽位(BMS 通常用 8);本 FB 也提供 `WritePropertyNull` 方法 — 把指定 priority 槽位写成 NULL 释放该槽,PDF §9.6 reset priorities 示例展示这个用法。

## 4. 错误码 / 返回值

`bError := TRUE` 时 `nErrorId` 包含错误码(write_access_denied / value_out_of_range 等)。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **写命令型对象要指定 `bPrio`**:不指定时按 BACnet 默认 priority 16;BMS 写常用 priority 8(ManOperator)。
- **写 Read-Only 属性会被 reject**:对端 stack 返回 write_access_denied;PLC 端读 nErrorId 判断。
- **释放优先级用 `WritePropertyNull` 方法**:PDF §9.6 示例 `fbBV.WritePropertyNull(ePropertyId := PropPresentValue, bPrio := TO_BYTE(8));` 把 priority 8 槽位写 NULL。
- **同步写多个属性用 WPM**:本库不直接暴露 WriteProperty Multiple 但 RM 对象周期写自动批量,大批量更新时让 stack 合并请求。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_WriteProperty.TcPOU`](../examples/P_Demo_FB_BACnetRM_WriteProperty.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_WriteProperty
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteBO : FB_BACnetRM_BO := (Client := fbClient, nObjectInstance := 0);
    fbWrite : FB_BACnetRM_WriteProperty := (Client := fbClient);
    bTrigger : BOOL := FALSE;
    bOutOfService : BOOL := TRUE;
END_VAR

fbClient();
fbDevice();
fbRemoteBO();

fbWrite.bExecute := bTrigger;
IF fbWrite.bExecute THEN
    bTrigger := FALSE;
    fbWrite.iObject := fbRemoteBO;
    fbWrite.ePropID := E_BACnet_PropertyIdentifier.PropOutOfService;
    fbWrite.pData   := ADR(bOutOfService);
    fbWrite.nData   := SIZEOF(bOutOfService);
END_IF
fbWrite();
```

## 7. 业务场景与实际价值

- **场景**:运维想暂时把对端某个对象置成 Out_Of_Service(仿真模式)做对端调试,无需上对端登录。
- **价值**:跨厂商远程改属性,标准化无需懂对端品牌的协议细节。
- **替代方案对比**:登对端控制器改:费时;BACnet WriteProperty 一行触发。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.10(Acyclic write)、§7.10.1(完整 WriteProperty 写 Out_of_Service 示例)、§9.6(WritePropertyNull 释放 priority 槽位)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnetRM_ReadProperty / ReadPropertyEx`(对应的读)、`FB_BACnetRM_WritePropertyEx`(本 FB 的扩展版)
