# FB_BACnet_Prog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Program` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ infer-from-naming-convention` |
| Example | [`examples/P_Demo_FB_BACnet_Prog.TcPOU`](../examples/P_Demo_FB_BACnet_Prog.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Program」对象类型(BACnet Object_Type = 16 / Program),用于把 PLC 内的应用程序状态(Run / Halted / Idle / Unloaded / Waiting / Loading 等)暴露给 BMS。BMS 可以通过 `Program_Change` 属性向 PLC 发送启动 / 停止 / 重启 / 卸载请求,PLC 接到请求后由本 FB 在 `Program_State` 输出当前应用程序的实际状态。本对象类型在本库中仅基础类,无后缀变体。Status: ⚠️ PDF 仅在 §6.1.1 表中列出 Prog 一行,未给独立示例;本文档基于 BACnet 标准 Program 对象语义 + 本库命名规则推导。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |
| 程序状态 | `eState` | `E_BACnet_ProgramState` | Program_State(`eIdle` / `eRunning` / `eHalted` / `eUnloading` / `eLoading` / `eWaiting`) |
| 控制请求 | `eChange` | `E_BACnet_ProgramRequest` | Program_Change(BMS 写入触发状态切换:`eReady` / `eLoad` / `eRun` / `eHalt` / `eRestart` / `eUnload`) |
| 出错原因 | `eReason` | `E_BACnet_ProgramError` | Reason_For_Halt(Halted 状态下说明原因) |
| 描述 | `sDescriptionOfHalt` | `STRING(*)` | Description_Of_Halt(自由文本说明) |

## 3. 行为说明

FB_BACnet_Prog 每周期调用一次,PLC 把当前应用程序状态写到 `eState`(典型用法:启动时写 eLoading,进入正常循环写 eRunning,被运维 Halt 后写 eHalted,等等)。BMS 通过 `WriteProperty(Program_Change, eRun)` 发请求,PLC 在本 FB 的 `eChange` 引脚上读到 BMS 的请求,然后由 PLC 自定义代码决定是否接受请求并切换 eState。本 FB 本身不强制状态机,只是把状态字段标准化暴露 — BMS 看到的是 BACnet 标准的 ProgramState 枚举,不论 PLC 内部实际怎么实现状态切换。Reason_For_Halt 在 eState=eHalted 时由 PLC 填写,BMS 读到后可显示具体错误码。PDF 未给独立示例,典型用法参照 BACnet 标准定义。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码;本对象类型也未在 §9 给出示例。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **PLC 端要响应 `eChange`**:本 FB 只是把 BMS 写入的 Program_Change 暴露到 `eChange`,PLC 还需要自己读这个值并决定是否接受请求(典型:`IF fbProg.eChange = eHalt THEN ...PLC_Halt_Logic...; fbProg.eState := eHalted; END_IF`)。
- **eChange 写入后建议清零**:接受请求并切换状态后,把 `eChange := eReady` 让 BMS 知道请求已处理(工程经验补充)。
- **状态切换要原子化**:不要在不同周期里写 eState 不同值,会让 BMS 看到中间态闪烁(用上升沿触发 + 状态机集中管理)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_Prog.TcPOU`](../examples/P_Demo_FB_BACnet_Prog.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Prog
VAR
    fbAppStatus : FB_BACnet_Prog := (
        sObjectName := 'MainApp_Status',
        sDescription := 'Floor 3 East zone control app',
        eState := E_BACnet_ProgramState.eLoading);  // 上电初始
    bAppReady : BOOL := FALSE;
END_VAR

IF bAppReady AND fbAppStatus.eState = E_BACnet_ProgramState.eLoading THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eRunning;
END_IF
// BMS 请求 Halt
IF fbAppStatus.eChange = E_BACnet_ProgramRequest.eHalt THEN
    fbAppStatus.eState := E_BACnet_ProgramState.eHalted;
    fbAppStatus.eReason := E_BACnet_ProgramError.eOther;
    fbAppStatus.sDescriptionOfHalt := 'Halted by BMS request';
    fbAppStatus.eChange := E_BACnet_ProgramRequest.eReady;  // 清零
END_IF
fbAppStatus();
```

## 7. 业务场景与实际价值

- **场景**:大型楼控项目希望在 BMS 上看到每个 PLC 应用程序的运行状态;运维可以远程 Halt 某个程序(如冬季关停喷淋系统的控制程序),无需远程登录 PLC。
- **价值**:Program 是 BACnet 标准的运行时管理对象,BMS 直接显示状态 / 发请求,代替「自己写 Modbus 寄存器 + 协议解码」的脏方案。
- **替代方案对比**:用 MV 暴露状态:能显示但 BMS 端没有「Program_Change」语义,无法标准化「控制请求」。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(Prog = Program)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Device`(本机设备对象)、`FB_BACnet_MV`(虚拟多态值)
