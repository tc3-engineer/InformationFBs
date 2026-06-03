# FB_BACnetRM_Device

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Remote Device` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_Device.TcPOU`](../examples/P_Demo_FB_BACnetRM_Device.TcPOU) |

---

## 1. 功能简述

代表远端 BACnet 设备的 Device 对象引用。每个 Client 必须实例化一个 FB_BACnetRM_Device 并每周期调用,用于监控连接状态(`eSysState` / `bOperational` / `nErrorCnt`),并把 client 的「远端设备发现 + 状态机维护」完成 — 没有这个 FB,client 不会发起 Who-Is,绑到本 client 的其它 RM 对象都跑不起来。PDF §7.11 详述监控用法。

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
| 系统状态(只读) | `eSysState` | `E_BACnet_SysState` | `eInit` / `eDiscovery` / `eOperational` / `eNoCommunication` |
| 可操作标志(只读) | `bOperational` | `BOOL` | TRUE 时已建立稳定通信,可发请求 |
| 错误计数(只读) | `nErrorCnt` | `UDINT` | 已尝试重连次数;超过阈值切到 eNoCommunication |

## 3. 行为说明

每周期调用一次,FB 内部驱动 client 状态机:`eInit` → `eDiscovery`(发 Who-Is 并等 I-Am)→ `eOperational`(可发请求)→ 出错时 `eNoCommunication`(超过 nErrorCnt 阈值)→ 自动重试回 eInit。PDF §7.11 解释:连接中断后 stack 自动重连,中断到检测出来通常需 30 秒左右(因为要等若干次 Who-Is 重试)。PLC 端可监视 `bOperational := TRUE` 作为可发 RM 请求的判据;`eSysState = eNoCommunication` 时所有发往 peer 的请求都会立刻失败,PLC 应停掉对应业务逻辑等连接恢复。

## 4. 错误码 / 返回值

无返回值;`eSysState` 是主要的诊断字段。⚠️ PDF + InfoSys 未列具体错误码常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **必须每周期 call**:不 call 的话 stack 不发 Who-Is,Client 永远停在 eInit。
- **`bOperational := FALSE` 时不要硬发 RM 请求**:会立刻失败 + 占带宽;PLC 应判 `IF fbDevice.bOperational THEN ... END_IF`。
- **MS/TP 网段连接成功时间偏长**:可能要 1..3 分钟才到 eOperational(MS/TP 令牌环要轮一圈才发现新设备),IP 通常 1..2 秒。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_Device.TcPOU`](../examples/P_Demo_FB_BACnetRM_Device.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_Device
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
END_VAR

fbClient();
fbDevice();
```

## 7. 业务场景与实际价值

- **场景**:多客户端项目中,每个 peer device 都要监控其在线状态;BMS 端看到 eSysState 字段实时刷新。
- **价值**:把「客户端 + 远端设备」两件事拆成两个 FB 后,monitor / discovery / fault detect 都自动化;PLC 端代码量从手写状态机的 200 行降到 1 行。
- **替代方案对比**:第三方 BACnet stack:需要自己实现状态机;本 FB 跟 client 配套,即插即用。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.11(连接监控完整说明 + 时序图)、§7.11.1 / §7.11.2(成功 / 中断示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Client`(必须绑)、`FB_BACnetRM_*`(其它远端对象,需要本 FB 把连接拉起来才能用)
