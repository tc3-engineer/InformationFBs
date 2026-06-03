# FB_BACnet_Server

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Server core` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319293451.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BACnet_Server.TcPOU`](../examples/P_Demo_FB_BACnet_Server.TcPOU) |

---

## 1. 功能简述

代表 PLC 中的一个 BACnet 服务器实例。除了暴露内存占用、内部状态等信息外，还提供报警确认（acknowledge）、持久化数据写入、复位服务器错误状态、遍历对象数据库等运行时方法。库会自动实例化一个 `BACnet_Globals.DefaultServer`，绝大多数项目无需在 PLC 程序里再 `fbServer()` 一次。要在多服务器场景中使用，则必须把 `FB_BACnet_Server` 与 `FB_BACnet_Adapter` 配对显式声明并每周期手动调用。

## 2. 接口定义

> PDF §6.7 仅给出 FB 用途说明 + 持久化、初始化方向相关变量描述，未单独列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表整理 PDF 正文及 §9.16 示例代码中确认存在的引脚与方法。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF 未单独列出 `VAR_INPUT`；运行时配置通过结构体成员引脚完成（见下表"关键属性 / 成员"）。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_OUTPUT`；内存与诊断信息通过成员变量暴露。

### VAR_IN_OUT

无。

### 关键属性 / 成员（按 PDF §6.7 / §6.10 / §6.11 / §9.16 综合）

| 名称 | 类型 | 说明 |
|---|---|---|
| `Adapter` | `FB_BACnet_Adapter` | 关联的适配器；多 server 项目里在变量初始化时绑定 `Server := FB_BACnet_Server := (Adapter := fbAdapter)`（PDF §9.16 示例） |
| `bWritePersistent` | `BOOL` | 触发一次持久化写入；用法是 PLC 程序里写 `TRUE`，库写盘完成后再由用户代码写 `FALSE` 复位（PDF §6.11） |
| `eInitMode` | `E_BACnet_InitMode` | 启动同步方向：`eInitReset`（Reset to Origin 后由库置位 → 数据库清空 → 自动转 `eInitToPlc`）、`eInitToPlc`（默认，BACnet 持久化数据→PLC）、`eInitForceFromPlc`（强制 PLC 值→BACnet）|

### 方法（按 PDF §6.11）

| 方法 | 用途 | 返回 |
|---|---|---|
| `SavePersistentStackData()` | 主动触发一次持久化写盘（与 `bWritePersistent := TRUE` 等效但同步返回成功标志） | `BOOL`：`TRUE` 写盘成功 |

⚠️ PDF §6.7 文字提到还有「报警确认」「复位服务器错误」「遍历对象数据库」等方法，但未给出具体方法名与签名。需要时请对照 InfoSys 在线手册 `FB_BACnet_Server` 主题页面。

## 3. 行为说明

`FB_BACnet_Server` 是 BACnet 协议栈在 PLC 侧的总入口；启动期会与 BACnet supplement 同步对象数据库（PDF §6.4.1 强调所有 BACnet FB 必须每周期调用一次并且用同一周期）。`eInitMode` 决定首次启动时数据同步方向：默认 `eInitToPlc` 把 supplement 保存的持久化值搬到 PLC 端（这是建筑被运维后的常态）；交付前调试还在改 P/I/D 参数时希望以 PLC 端代码值为准，可暂时设 `eInitForceFromPlc`，建筑投产前再切回 `eInitToPlc`。持久化（PDF §6.11）默认按时间间隔自动写盘（默认 30 分钟，少于此会加速 flash 寿命损耗），写盘文件叫 `BACnetOnline_<DeviceInstance>.bootdata` 放在 TwinCAT boot 目录；带 UPS 的项目可关闭定时持久化、改在断电检测 FB（如 `Tc2_SUPS`）回调里主动调用 `SavePersistentStackData()` 或写 `bWritePersistent := TRUE`，从而把"断电时把最新值落盘"和 BACnet 持久化解耦。`bWritePersistent` 是电平触发：程序里设 `TRUE`，库写盘完成后用户代码需主动写回 `FALSE`，否则下一周期还会被识别为重写请求。

## 4. 错误码 / 返回值

`SavePersistentStackData()` 返回 `BOOL`：`TRUE` 写盘成功，`FALSE` 失败（最常见原因：flash 不可写、目录权限、router memory 不足）。PDF §6.11 未在本 FB 节列具体错误码常量；BACnet 协议层（Error / Abort / Reject Code）的常量集中在 `BACnet_Globals` 中，需对照在线手册 `BACnet_Globals` 章节。

⚠️ PDF + InfoSys 均未在本 FB 节列具体错误码表，⚠️ 待人工对照 BACnet_Globals 章节补全。

## 5. 使用注意 / 常见坑

- **默认服务器不要手工再调用**：`BACnet_Globals.DefaultServer` 已由库内部循环调用，POU 中再 `BACnet_Globals.DefaultServer()` 一次会引起重复调度。
- **持久化间隔不能短于 30 分钟**：PDF §6.11 警示，少于 30 分钟会显著缩短 flash 介质寿命；带 UPS 的项目把自动持久化关掉，改 SUPS 库回调里手工触发是首选实践。
- **持久化写盘是阻塞 IO**：`SavePersistentStackData()` 同步等盘 IO 完成，长写盘期间本任务被 hold 住，不能放在毫秒级控制回路里。
- **`bWritePersistent` 需要手动清零**：PDF 明示"variable must also be reset from the PLC program"；忘清会被识别为持续重写请求。
- **`eInitMode = eInitForceFromPlc` 仅作交付前调试**：建筑投产后这个模式会让 BMS 管理员的属性写入被 PLC 启动时覆盖，造成"现场改值不生效"。
- **router memory 默认 32 MB 不够大项目**：本 FB 与所有 BACnet 对象 FB 共享 router memory，按 PDF §6.5 估算「每对象 ≈ 20 KB + Trendlog 缓冲」，当达到 60% 占用时库会拒绝新建对象（这条监控集中在本 FB 上，需读其内存字段判断）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BACnet_Server.TcPOU`](../examples/P_Demo_FB_BACnet_Server.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Server
VAR
    {attribute 'TcLinkTo' := '.BACnet_AmsNetId := TIID^Device 2 (BACnet IP)^Inputs^AmsNetId'}
    fbBACnetAdapter : FB_BACnet_Adapter;
    fbBACnetServer  : FB_BACnet_Server := (Adapter := fbBACnetAdapter);
    bTriggerSave    : BOOL;
    bSaveOk         : BOOL;
END_VAR

fbBACnetAdapter();
fbBACnetServer();

IF bTriggerSave THEN
    bTriggerSave := FALSE;
    bSaveOk := fbBACnetServer.SavePersistentStackData();
END_IF
```

## 7. 业务场景与实际价值

- **场景**：一台工业 PC 同时承担两个独立 BACnet 服务（如左侧楼栋 BACnet/IP + 右侧 MS/TP），每台 server 跑独立的对象数据库 + 独立的持久化文件；又或者把 BACnet 持久化和 `Tc2_SUPS` 的"掉电存盘"流程绑定，断电时由 UPS FB 回调里主动调 `SavePersistentStackData()`。
- **价值**：用 `BACnet_Globals.DefaultServer` 单实例零配置就能上线 1 个 server；需要 N 个 server 时各显式实例化即可，不必接触 BACnet C SDK 层。
- **替代方案对比**：
  - 写死 `BACnet_Globals.DefaultServer`：只支持单 server 场景，多楼栋拆 server 时不可用
  - 直接持有 BACnet stack handle 调写盘 API：能做但需第三方 SDK，并失去与 TwinCAT XAE 的诊断整合

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.7、§6.10（推荐工作流）、§6.11（持久化）、§9.16（多 server 数组初始化示例）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319293451.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 FB / FC**：`FB_BACnet_Adapter`（必须配对）、`FB_BACnet_Device`（运行时改本机设备对象属性）、`FB_BACnet_DynObjectManager`、`FB_S_UPS_*`（断电检测，配合手动持久化触发）
