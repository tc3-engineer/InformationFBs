# FB_BACnet_Adapter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Server core` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319299211.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BACnet_Adapter.TcPOU`](../examples/P_Demo_FB_BACnet_Adapter.TcPOU) |

---

## 1. 功能简述

代表 TwinCAT System Manager 中 I/O 设备节点下的一个 BACnet 适配器（BACnet Adapter）。一个适配器对应一个物理通道：BACnet/IP 时连接到一块网卡，BACnet MS/TP 时连接到一只 EL6861 总线端子。为避免与 BACnet 协议层的「Device 对象」混淆，本库把硬件层的 BACnet 设备节点统一叫做「适配器」。FB 实例通过 `BACnet_AmsNetId` 引脚与 System Manager 中的同名 I/O 设备绑定，提供时间同步、网络扫描、诊断读取等运行时方法。库自带一个 `BACnet_Globals.DefaultAdapter` 全局实例，加入本库即自动生成，无需手工实例化即可使用单适配器场景。

## 2. 接口定义

> PDF §5.3.2 仅给出 FB 的功能说明与配套示例，未单独列出 `VAR_INPUT` / `VAR_OUTPUT` 区。下表整理 PDF 正文及示例代码中提到的引脚与方法（按 PDF §5.3.2 / §6.2.7 / §6.2.8 / §6.2.9）。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF 未在本 FB 节单独列 `VAR_INPUT`；运行时所有外部链接通过 `BACnet_AmsNetId` 引脚（用 `TcLinkTo` 属性绑定）完成，详见 §5。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_OUTPUT`；适配器的运行状态通过 `eDevState`、`bEthLink`、`bGateway` 等成员变量暴露（§7.7 客户端变量节中列出，原文按"Adapter:"列举）。

### VAR_IN_OUT

无。

### 关键属性 / 成员

| 名称 | 类型 | 说明 |
|---|---|---|
| `BACnet_AmsNetId` | `AMSNETID` | 与 System Manager 中 BACnet Adapter 设备的 `Inputs^AmsNetId` 绑定的引脚；通常用 `{attribute 'TcLinkTo' := '.BACnet_AmsNetId := TIID^Device N (BACnet ...)^Inputs^AmsNetId'}` 在变量声明上方一并写入 |
| `eDevState` | `E_BA_DevState` | 连接阶段状态机；正常完成后取 `eComplete` |
| `bEthLink` | `BOOL` | 物理链路已建立时为 `TRUE` |
| `bGateway` | `BOOL` | IP 地址设置含网关信息（跨 IT 路由器）时为 `TRUE` |
| `_bHasStarted` | `BOOL` | 状态机已启动 |
| `_nUpdateCount` | `UDINT` | 每周期自增一次的心跳计数 |

### 方法（按 PDF §6.2.7、§6.2.8、§6.2.9）

| 方法 | 用途 | 关键参数 |
|---|---|---|
| `TimeSync(pDateTime, bSendBroadcast)` | 以本适配器为时间主站发送 BACnet 本地时间同步报文 | `pDateTime : POINTER TO ST_BA_DateTime`；`bSendBroadcast : BOOL`（`TRUE` 广播）→ 返回 `BOOL` 成功标志 |
| `TimeSyncEx(...)` | 时间同步扩展版（携带 UTC / 时区信息，PDF §6.2.7 提及） | ⚠️ 详细签名 PDF 未列，使用前请对照 InfoSys 在线手册的 `TimeSyncEx` topic |
| `GetDiagnosis(pBuffer)` | 读出 System Manager 「Diagnosis」选项卡相同的诊断结构 | `pBuffer : POINTER TO ST_BACnet_Diagnosis` → 返回 `BOOL` 成功标志 |
| `StartScan()` | 发起一次 BACnet `Who-Is` 广播（不带过滤），等待若干秒后用 `GetScanResult` 读取结果 | 无参数 → 返回 `BOOL` 成功标志 |
| `StartScanEx(...)` | 带过滤参数的网络扫描扩展版 | ⚠️ 详细签名 PDF 未列 |
| `GetScanResult(pBuffer, nMaxResults)` | 读取上一次扫描发现的外部 BACnet 设备列表 | `pBuffer : POINTER TO ARRAY OF ST_BACnetRM_ScanResult`；`nMaxResults : UDINT` → 返回 `DINT`：>=0 实际找到数，-1 错误 |

## 3. 行为说明

FB 必须每个 PLC 循环调用一次（同库内所有 BACnet 对象 FB 一样，调用周期必须相同）。实例化方式有两种：（1）单适配器项目直接用 `BACnet_Globals.DefaultAdapter`，本 FB 已经在 GVL 中自动实例化并每周期被库内部循环调用；（2）多适配器项目（如同机同时跑 BACnet/IP + 多块 MS/TP 端子）每块外设各声明一个 `FB_BACnet_Adapter` 实例，并用 `{attribute 'TcLinkTo' := '.BACnet_AmsNetId := TIID^Device N (BACnet ...)^Inputs^AmsNetId'}` 绑定到 System Manager 中对应的 BACnet 设备节点，再每周期手工调用 `fbAdapter()`。`eDevState` 在握手完成后取 `eComplete`，此时 `bEthLink` 应为 `TRUE`；若网络断开 `eDevState` 退回上一阶段，`bEthLink` 变 `FALSE`。`TimeSync` / `TimeSyncEx` 是一次性方法，应在外部触发条件（HMI 按钮、NTP 周期定时器等）后调用一次，库不内置自动同步。`StartScan` + `GetScanResult` 是异步组合：发起后须等待若干秒（PDF 示例用 5 秒 TON）再调用 `GetScanResult` 才能拿到结果，过早调用返回 -1。多个 MS/TP 适配器的实例必须**额外**和它代表的远端设备 FB 一起被调用，参见 §7.6.6 的 `fbMstpDevice_3` 用法。

## 4. 错误码 / 返回值

`TimeSync` / `GetDiagnosis` / `StartScan` / `StartScanEx` 均返回 `BOOL`：`TRUE` 表示方法被成功接受（不代表网络收到 / 远端响应，仅代表本端调度成功），`FALSE` 表示本端拒绝（适配器尚未就绪、参数无效或 router memory 不足）。`GetScanResult` 返回 `DINT`：`>=0` 表示实际发现的设备数（即写入缓冲区的 `ST_BACnetRM_ScanResult` 条目数），`-1` 表示错误（最常见是扫描尚未结束或上一次 `StartScan` 失败）。

⚠️ PDF 与 InfoSys 均未在本 FB 节给出明细错误码表（BACnet 协议层错误集中在 `BACnet_Globals` 的 Error / Abort / Reject 码常量中，PDF §5.2.2 仅文字说明，未枚举），需在线对照官方手册 `BACnet_Globals` 章节。

## 5. 使用注意 / 常见坑

- **必须周期调用且周期一致**：所有 BACnet FB 都要每周期调用一次且使用同一周期任务（PDF §6.4.1 / §6.4.2，违反会导致 stack 启动时同步失败），适配器 FB 也不例外；多实例项目中每个 `fbAdapter` 都要在同一周期手动调用。
- **默认适配器不要手工再次调用**：`BACnet_Globals.DefaultAdapter` 已由库内部循环调用，POU 里再写一次 `BACnet_Globals.DefaultAdapter()` 会引起重复调度（工程经验补充）。
- **MS/TP 适配器要和它的 client FB 一起每周期调用**：PDF §7.6.6 的 sample 备注：使用 `FB_Code` 生成的客户端 FB 之外，还必须每周期单独调用 `fbMstpDevice_3 : FB_BACnet_Adapter`，否则该端子上挂的 BACnet 设备读不到值。
- **扫描结果数组大小要预留充足**：`GetScanResult` 的 `nMaxResults` 必须 >= 网段上实际设备数，否则只写入前 N 条；PDF 示例用 200 起步。
- **TimeSync 是 unconfirmed 服务**：发出后不会有响应，无法用返回值判断接收端是否真的同步成功；如要确认必须在接收端 PLC 用 `FB_BACnet_Device.GetTime` 之类读回校验（工程经验补充）。
- **库版本名是 `Tc3_BACnetRev14`**：本仓库目录沿用任务命名 `Tc2_BACnet` 作为别名，但实际 PLC 项目引用的库名是 `Tc3_BACnetRev14`（PDF 头页 "TF8020" / `Tc3_BACnetRev14`，旧的 `Tc2_BACnetRev12` 已停更，两者**不能共存**于同一项目）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BACnet_Adapter.TcPOU`](../examples/P_Demo_FB_BACnet_Adapter.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Adapter
VAR
    {attribute 'TcLinkTo' := '.BACnet_AmsNetId := TIID^Device 2 (BACnet IP)^Inputs^AmsNetId'}
    fbAdapter      : FB_BACnet_Adapter;
    stTimeMaster   : ST_BA_DateTime;
    bTriggerSync   : BOOL;
    bSyncOk        : BOOL;
    aScanResults   : ARRAY[0..199] OF ST_BACnetRM_ScanResult;
    fbScanTimer    : TON;
    bTriggerScan   : BOOL;
    bScanPending   : BOOL;
    nDevicesFound  : DINT;
END_VAR

fbAdapter();                                      // 多适配器项目下必须每周期手动调用
fbScanTimer(IN := bScanPending, PT := T#5S);

IF bTriggerSync THEN
    bTriggerSync := FALSE;
    bSyncOk := fbAdapter.TimeSync(pDateTime := ADR(stTimeMaster),
                                  bSendBroadcast := TRUE);
END_IF

IF bTriggerScan THEN
    bTriggerScan := FALSE;
    bScanPending := fbAdapter.StartScan();
END_IF
IF bScanPending AND fbScanTimer.Q THEN
    bScanPending := FALSE;
    nDevicesFound := fbAdapter.GetScanResult(pBuffer := ADR(aScanResults),
                                             nMaxResults := 200);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：楼宇自动化项目用 CX 控制器跑 BACnet 服务端，同时需要：（a）作为时间主站把控制器本地时间广播给楼层下其它 BACnet 控制器；（b）从 HMI 触发一次"扫描网段已有设备"用于自动建模；（c）周期读取 BACnet 协议栈诊断把内存占用、报文丢失数等送到 SCADA。
- **价值**：把 BACnet 协议的底层服务（`Who-Is` 广播、`Time-Synchronization` 服务、Stack 内部诊断）封装成 PLC 方法调用，工程师不必接触 BACnet ASN.1 报文层；且默认适配器 `BACnet_Globals.DefaultAdapter` 单一适配器场景下零配置可用。
- **替代方案对比**：
  - 直接调底层 BACnet C 库 API：可行但需第三方 SDK 且无 PLC 调用契约
  - 用 `Tc3_BACnetRev14` 之外的开源 BACnet 栈：与 TwinCAT 4024.11+ 内置 BACnet Supplement 不集成，会失去 System Manager 配置 GUI、EDE 文件导出等支持
  - **本 FB**：是 TwinCAT 3 上接入 BACnet/IP 与 MS/TP 的官方主入口，跟 System Manager 已经做好集成

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §5.3.2、§6.2.7（TimeSync）、§6.2.8（GetDiagnosis）、§6.2.9（StartScan / GetScanResult）、§7.6.6（多适配器示例）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319299211.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 FB / FC**：`FB_BACnet_Server`（自动调度，每库一个）、`FB_BACnet_Device`（运行时改本机设备对象属性）、`FB_BACnetRM_Device`（远端设备）、`FB_BACnet_DynObjectManager`（动态对象池）
