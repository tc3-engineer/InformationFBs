# FB_BACnet_WriteProperty

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Server · Acyclic Write` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ infer-from-naming-convention` |
| Example | [`examples/P_Demo_FB_BACnet_WriteProperty.TcPOU`](../examples/P_Demo_FB_BACnet_WriteProperty.TcPOU) |

---

## 1. 功能简述

服务端非循环写自身对象的任意属性 — 用于让本机 PLC 程序写「自己」暴露的 BACnet 对象属性。与 client 侧的 `FB_BACnetRM_WriteProperty` 对称,但目标是本机对象而非远端。Status: ⚠️ PDF 仅在 §6.1.1 注释 + 命名规则部分提及本 FB,未给独立示例;本文档基于命名规则推导。

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
| 触发 | `bExecute` | `BOOL` | 上升沿触发一次写 |
| 目标对象 | `iObject` | `POINTER TO ...` | 指本机某个对象 FB 实例 |
| 属性 ID | `ePropID` | `E_BACnet_PropertyIdentifier` | 要写的属性 |
| 发送缓冲 | `pData` / `nData` | `POINTER TO BYTE` / `UDINT` | `ADR(val) + SIZEOF(val)` |
| 优先级 | `bPrio` | `BYTE` | 写命令型对象 Present_Value 时使用的 BACnet 优先级槽位 |
| 完成(只读) | `bDone` / `bBusy` / `bError` / `nErrorId` | `BOOL` / `UDINT` | 标准化完成 / 错状态 |

## 3. 行为说明

上升沿触发,stack 直接在本机 BACnet 属性表上写值(不经网络)。本 FB 与 PLC 直接修改 FB 成员的差别:PLC 直接 `fbAv.fValPgm := 22.0` 是把 PLC 端缓冲改了等下次 stack 循环;而本 FB 模拟外部 BACnet 客户端 WriteProperty 服务,触发 stack 内的全套属性变更钩子 — 包括写到优先级槽位、触发 COV 通知、updateCounter 自增等。也可通过 PLC 端用本 FB 复位某优先级槽位:`bPrio := 8` + 数据带 BACnet NULL 编码就可释放槽位 (等同于 RM 版的 WritePropertyNull,但目标是本机)。

## 4. 错误码 / 返回值

`bError := TRUE` 时 `nErrorId` 包含错误码(写保护属性 / 越界等);⚠️ PDF 未给独立示例。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **本 FB 与直接写 FB 成员的差别**:直接写 PLC 端缓冲(简单);本 FB 模拟外部写,触发完整 BACnet 钩子(COV 通知等)。
- **`iObject` 必须指本机 FB 对象**:用 `ADR(fbLocalAv)`。
- **释放优先级槽位**:用本 FB + 特殊 NULL 编码,或直接调本机对象的 `WritePropertyNull` 方法(PDF §9.6)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_WriteProperty.TcPOU`](../examples/P_Demo_FB_BACnet_WriteProperty.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_WriteProperty
VAR
    fbLocalAv : FB_BACnet_AV := (sObjectName := 'LocalAv');
    fbWrite : FB_BACnet_WriteProperty;
    bTrigger : BOOL := FALSE;
    fNewHighLimit : REAL := 90.0;
END_VAR

fbLocalAv();
fbWrite.bExecute := bTrigger;
IF fbWrite.bExecute THEN
    bTrigger := FALSE;
    fbWrite.iObject := fbLocalAv;
    fbWrite.ePropID := E_BACnet_PropertyIdentifier.PropHighLimit;
    fbWrite.pData   := ADR(fNewHighLimit);
    fbWrite.nData   := SIZEOF(fNewHighLimit);
END_IF
fbWrite();
```

## 7. 业务场景与实际价值

- **场景**:PLC 程序需要模拟「外部 BACnet 客户端」修改本机某属性,触发完整 stack 钩子(COV 通知 / updateCounter 等);或释放某优先级槽位。
- **价值**:直接 PLC 写 FB 成员可能漏掉 stack 钩子;用本 FB 保证 BACnet 标准行为一致性。
- **替代方案对比**:直接写 FB 成员:简单但漏钩子;本 FB 完整。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1 命名规则、§9.6(WritePropertyNull 释放优先级,本 FB 配 NULL 编码可等效)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_ReadProperty`(对称的读)、`FB_BACnetRM_WriteProperty / WritePropertyEx`(远端版)
