# FB_BACnet_ReadProperty

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Server · Acyclic Read` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ infer-from-naming-convention` |
| Example | [`examples/P_Demo_FB_BACnet_ReadProperty.TcPOU`](../examples/P_Demo_FB_BACnet_ReadProperty.TcPOU) |

---

## 1. 功能简述

服务端非循环读自身对象的任意属性 — 用于让本机 PLC 程序读「自己」暴露的 BACnet 对象属性(如临时读自己 fbAv 的 EventState、读自己 fbBO 的 Priority_Array 等)。与 client 侧的 `FB_BACnetRM_ReadProperty` 对称,但操作目标是本机对象而非远端。Status: ⚠️ PDF 仅在 §6.1.1 注释 + 命名规则部分提及本 FB(命名与远端版一致但去掉 `RM_`),未给独立示例;本文档基于命名规则推导。

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
| 触发 | `bExecute` | `BOOL` | 上升沿触发一次读 |
| 目标对象 | `iObject` | `POINTER TO ...` | 指本机某个对象 FB 实例(用 ADR()) |
| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要读的属性 |
| 接收缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(val) + SIZEOF(val)` |
| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化完成 / 错状态 |

## 3. 行为说明

上升沿触发,stack 直接从 PLC 内本对象的 BACnet 属性表读出值(不经过网络),立即完成。适合 PLC 程序需要拿到「BACnet 标准的某个属性值」而该属性不是 FB 对象的直接成员的情况 — 例如Priority_Array 是 BACnet 标准属性但 FB_BACnet_AO 不把它作为 PLC 可读成员;用本 FB 读 PropPriorityArray 就能拿到 16 槽位的当前值快照。完成后 bDone 一个周期 + bExecute 自动复位。

## 4. 错误码 / 返回值

`bError := TRUE` 时 `nErrorId` 包含错误码(属性不存在 / 类型不匹配等);⚠️ PDF 未给独立示例,使用前请用 BACnet Explorer 验证目标属性 ID 与 buffer 大小。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **本 FB 操作本机对象,不发网络请求**:相比 RM 版几乎瞬时完成。
- **`iObject` 必须指本机 FB 对象实例**:用 `ADR(fbLocalAv)` 取地址。
- **typical use**:读 Priority_Array / Active_COV_Subscriptions / Status_Flags 等非直接成员的标准属性。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_ReadProperty.TcPOU`](../examples/P_Demo_FB_BACnet_ReadProperty.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_ReadProperty
VAR
    fbLocalAv : FB_BACnet_AV := (sObjectName := 'LocalAv');
    fbRead : FB_BACnet_ReadProperty;
    bTrigger : BOOL := FALSE;
    fLocalHighLimit : REAL;
END_VAR

fbLocalAv();
fbRead.bExecute := bTrigger;
IF fbRead.bExecute THEN
    bTrigger := FALSE;
    fbRead.iObject := fbLocalAv;
    fbRead.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbRead.pData   := ADR(fLocalHighLimit);
    fbRead.nData   := SIZEOF(fLocalHighLimit);
END_IF
fbRead();
```

## 7. 业务场景与实际价值

- **场景**:PLC 程序临时需要某本机对象的 BACnet 标准属性值(非 FB 直接成员),典型 Priority_Array、Active_COV_Subscriptions、Object_Identifier 等。
- **价值**:不必为每个标准属性都在 FB 中加 getter 成员;BACnet stack 已经维护这些属性,本 FB 一行读出。
- **替代方案对比**:用 RM 版读自己(client 连本机回环):工作但绕远;本 FB 直接读省网络。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1 命名规则(server-side 命名是 `FB_BACnet_<>` 去掉 `RM_`)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_WriteProperty`(对称的写)、`FB_BACnetRM_ReadProperty / ReadPropertyEx`(远端版)
