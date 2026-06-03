# FB_BACnet_Client

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Connection` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_Client.TcPOU`](../examples/P_Demo_FB_BACnet_Client.TcPOU) |

---

## 1. 功能简述

BACnet 客户端连接对象,代表 PLC 作为客户端连接到一个 BACnet 远端设备(peer device)。本 FB 维持与该 peer 的 BACnet 协议层会话(支持的服务、ReadMode、tReadCycleTime / tWriteCycleTime、最大并发请求数等),所有 `FB_BACnetRM_*` 远端对象引用都必须绑定一个 Client 实例。PDF §7.2 / §7.7 详述客户端变量与状态机。

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
| 链接 | `Adapter` | `FB_BACnet_Adapter` | 绑定的本地 BACnet 适配器(默认 `BACnet_Globals.DefaultAdapter`) |
| 远端设备 | `nDeviceInstance` | `UDINT` | Peer 设备的 BACnet device-id(用 Who-Is 解析为 IP / MS/TP 地址) |
| 读模式 | `eReadMode` | `E_BACnet_CommMode` | `eAutomatic` / `eCovU` / `eCovC` / `eCovP` / `eReadProperty` / `eReadPropertyMultiple`(PDF §7.2.1) |
| 周期 | `tReadCycleTime` / `tWriteCycleTime` | `TIME` | 读 / 写请求周期 |
| 并发 | `nMaxParallelRequests` | `UDINT` | 同时可在飞的请求数(MS/TP 通常 ≤ 20,IP 可到 50+) |
| 服务支持 | `bSuppRpm` / `bSuppCov` / `bSuppCovP` | `BOOL` | Peer 设备是否支持 RPM / COV / COV-P(eAutomatic 模式下 stack 自检测,手动模式下 PLC 配) |
| 自动恢复 | `bAutoResetObjError` | `BOOL` | TRUE 时连接中断后自动重置 client 状态机 |
| 状态(只读) | `bReady` / `bConnected` / `eState` | `BOOL` / `E_BACnet_ClientState` | FB 初始化完成 / 已连接 / 当前状态机阶段(PDF §7.7) |
| 诊断(只读) | `m_stDiag` | `ST_BACnet_ClientDiag` | 客户端连接的 roundtrip / 各请求类型计数(PDF §6.2.8) |

## 3. 行为说明

FB_BACnet_Client 每周期调用一次。上电后状态机从 eInit 开始,自动发 Who-Is 解析 nDeviceInstance,之后建立到 peer 的会话(eAutomatic 模式下扫描其支持的服务集);完成后 `bReady := TRUE` 且 `bConnected := TRUE`,后续 `FB_BACnetRM_*` 对象的读 / 写都通过本 client 走。`eReadMode := eAutomatic` 时 stack 根据 peer 支持的服务+ 待读属性总数自动选 RP / RPM / COV(PDF §7.2.1 阈值规则);手动模式下 PLC 设 `bSuppRpm / bSuppCov / bSuppCovP` 指定 stack 走哪种服务。`tReadCycleTime` / `tWriteCycleTime` 决定客户端轮询频率(典型 2..10 秒)。连接断开(网络故障或 peer 重启)时 `bConnected := FALSE` / `eState := eInit`,stack 自动重连;`bAutoResetObjError := TRUE` 时,绑定到本 client 的所有 RM 对象在 client 重连后会自动复位状态。

## 4. 错误码 / 返回值

无返回值;`bConnected` / `eState` / `m_stDiag` 暴露状态。⚠️ PDF + InfoSys 未列具体错误码,连接相关错误集中在 `BACnet_Globals.Error / Abort / Reject` 段以及 m_stDiag 子结构里(PDF §6.2.8)。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **MS/TP peer 必须先实例化对应的 FB_BACnet_Adapter**:`Client := (Adapter := fbMstpDevice_X, nDeviceInstance := ...)`,且 fbMstpDevice_X 也要每周期单独 call(PDF §7.6.6)。
- **大量 RM 对象时把 `nMaxParallelRequests` 调高**:默认 1 太保守,IP 设 50+,MS/TP 设 5..20。
- **`tReadCycleTime` 不要设太短**:< 1 秒会导致 MS/TP 网段被淹,建议 2..5 秒。
- **`bAutoResetObjError := TRUE` 适合不稳定网络**:网络偶断后所有 RM 对象自动从 init 重启;`:= FALSE` 时 PLC 要自己监测 bConnected 并 reset。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_Client.TcPOU`](../examples/P_Demo_FB_BACnet_Client.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Client
VAR
    fbClient : FB_BACnet_Client := (
        nDeviceInstance := 42,
        tReadCycleTime := T#5S,
        tWriteCycleTime := T#5S,
        nMaxParallelRequests := 20,
        eReadMode := E_BACnet_CommMode.eAutomatic);
END_VAR

fbClient();
```

## 7. 业务场景与实际价值

- **场景**:PLC 作为客户端连接其它楼控厂商的 BACnet 设备(西门子 PXC / 霍尼韦尔 Spyder 等),把对端的传感器读数 / 控制点同步到 BMS。
- **价值**:Client 是所有 RM 对象的前提;一个 Client 维护一条到 peer 的会话,自动选 RP/RPM/COV 取数据,无需 PLC 写 BACnet 协议栈。
- **替代方案对比**:用 BACnet stack 第三方库直连:成本高且与 System Manager 不集成;Tc3_BACnetRev14 client 让 BACnet 跨厂商通信变成几行 PLC 代码。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.2(Readmode 与自动选服务)、§7.7(客户端变量)、§7.11(连接监控)、§7.12(RPM 综合示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Adapter`(本地 BACnet 适配器)、所有 `FB_BACnetRM_*`(远端对象,必须绑本 client)
