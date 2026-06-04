# FB_OpcUAServerGetStatus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc2_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_server/7633284619.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_OpcUAServerGetStatus.TcPOU`](../examples/P_Demo_FB_OpcUAServerGetStatus.TcPOU) |

---

## 1. 功能简述

TwinCAT OPC UA Server 心跳探活功能块（legacy 库 `Tc2_OpcUa`，TF6100 PDF §5.1.2.2）。仅通过 ADS 接口探测 Server 进程是否仍可达，返回 `eOPCUAServerStatus_Alive` 或 `eOPCUAServerStatus_NotResponding`。和 `FB_OpcUAServer` 不同，本 FB **不**走 OPC UA 协议，只看 ADS 端口；因此即使 OPC UA 接口已经被 Shutdown，只要 TcOpcUaServer 进程没退出，这里仍报 Alive——ADS 接口只在 Server 进程被 kill 才会消失。这是 PDF §5.1.2.2 专门强调的差异。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId             : T_AmsNetId;
    bGetStatus         : BOOL;
    tTimeout           : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | 运行 TwinCAT OPC UA Server 的设备 AMS Net ID。本机用空串 `''` |
| `bGetStatus` | `BOOL` | — | 上升沿触发一次状态查询 |
| `tTimeout` | `TIME` | — | ADS 超时时长 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    eOPCUAServerStatus : E_OPCUAServerStatus;
    bDone              : BOOL;
    bBusy              : BOOL;
    bError             : BOOL;
    nErrorId           : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eOPCUAServerStatus` | `E_OPCUAServerStatus` | Server 状态：`eOPCUAServerStatus_Alive`（ADS 可达）/ `eOPCUAServerStatus_NotResponding`（ADS 不可达）/ `eOPCUAServerStatus_None`（初始值） |
| `bDone` | `BOOL` | 功能块完成（无错误）一个周期内置 `TRUE` |
| `bBusy` | `BOOL` | 正在查询；置 `FALSE` 后才允许下一次上升沿 |
| `bError` | `BOOL` | 查询失败（ADS 端口/路由错等） |
| `nErrorId` | `UDINT` | 错误码（ADS 错误码） |

### VAR_IN_OUT

无。

#### E_OpcUAServerStatus（PDF §5.1.1.3）

```iecst
TYPE E_OpcUAServerStatus
(
    eOPCUAServerStatus_None,
    eOPCUAServerStatus_Alive,
    eOPCUAServerStatus_NotResponding
);
END_TYPE
```

| 枚举值 | 说明 |
|---|---|
| `eOPCUAServerStatus_None` | 枚举的初始值（尚未查询过） |
| `eOPCUAServerStatus_Alive` | TwinCAT OPC UA Server 的 ADS 接口可访问 |
| `eOPCUAServerStatus_NotResponding` | ADS 接口不可访问（Server 进程没启动 / 已被 kill） |

## 3. 行为说明

本 FB 走 ADS 探活，**不发起 OPC UA 协议会话**：只查询目标设备上 TcOpcUaServer 进程暴露的 ADS 端口是否还能响应一个最低限度的 ping 类请求。`bGetStatus` 由 `FALSE → TRUE` 上升沿触发一次查询：FB 通过 ADS 把请求发到 `sNetId` 指定的设备，过程中 `bBusy := TRUE`；收到应答（或 `tTimeout` 到期）后 `bBusy` 落 `FALSE`，成功则 `bDone := TRUE` 一个周期 + `eOPCUAServerStatus` 含 Alive/NotResponding，失败（ADS 路由不通等更底层错误）则 `bError := TRUE` 且 `nErrorId` 含错误码。

「Alive」和「OPC UA 服务可用」是两件事：①如果 `FB_OpcUAServer` 用 `eOPCUAServerOption_Shutdown` 关停了 OPC UA 接口但 Server 进程还在跑，本 FB 仍报 Alive——因为 ADS 没断；②只有 Server 进程被操作系统 kill 或被 TwinCAT 整个停掉，本 FB 才会报 NotResponding。要确认 OPC UA 协议层真的能服务客户端，需另用 OPC UA 客户端 ping 一下 endpoint，或用 `FB_OpcUAServer` 的 ServerInfo 模式（那是经 OPC UA 通道查的）。

**典型用法**：HMI 上「OPC UA 心跳」灯——周期 1-2 秒触发一次本 FB，把 `eOPCUAServerStatus = eOPCUAServerStatus_Alive` 翻译成绿灯，其他翻译成红灯+提示「需检查 TcOpcUaServer 进程」。Cyclic 触发需要外面接一个 `R_TRIG`（或一个 0.5 Hz 的方波到 `bGetStatus`），FB 内部只看上升沿。

**典型陷阱**：① 误以为 Alive 等于「客户端能正常订阅」——只有 ADS 是活的，OPC UA 接口可能仍被 Shutdown；② `bGetStatus` 接死循环常 `TRUE` 不会反复查，必须有边沿；③ `tTimeout` 太短在控制器启动阶段会假报错（启动几秒内 ADS 路由可能未就绪）；④ `bDone` 仅维持一个 PLC 周期，要锁存结果需外部 R_TRIG + 状态变量。

## 4. 错误码 / 返回值

`nErrorId` 是 ADS 错误码（高字 `0x0000`）。常见取值（PDF §8.2.1）：

| `nErrorId` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 看 `eOPCUAServerStatus` 判断结果 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | ADS 目标端口未找到（OPC UA Server 进程没启动 / 没装 TF6100） | 在目标机查 TcOpcUaServer 进程；检查 TF6100 license 与 Runtime |
| `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标机不可达（AMS 路由不通） | 检查 `sNetId`、Static Routes、网卡/网线 |
| `0x745` (1861) | ADS Timeout | 查询未在 `tTimeout` 内完成 | 加大 `tTimeout`；检查链路 |

注意：`eOPCUAServerStatus_NotResponding` 是「业务层」答案（Server 不在），不是 `bError`——`bError` 表示 ADS 调用本身失败（路由错），`eOPCUAServerStatus_NotResponding` 表示调用成功但 Server 进程在指定地址不应答。

## 5. 使用注意 / 常见坑

- **Alive 不等于「OPC UA 接口可用」**：本 FB 只查 ADS。要查 OPC UA 接口本身可达性，用 `FB_OpcUAServer` 的 ServerInfo 模式（那个走 OPC UA 通道）或用 `Tc3_PLCopen_OpcUa.UA_Connect` 真正握手一次。
- **本 FB 是非破坏性的**：每周期问一下不会给 Server 增加可察觉的负载，可以做高频探活灯。`FB_OpcUAServer` 的 ServerInfo 模式则会消耗一次 OPC UA 会话资源，频率不宜过高。
- **`bDone` 是单周期脉冲**：HMI 要看「上次查询成功 vs 失败」需要外部锁存。
- **本 FB 属 legacy `Tc2_OpcUa` 库**：新工程的客户端连接用 `Tc3_PLCopen_OpcUa.UA_ConnectGetStatus`（在 `tc3_plcopen_opcua/` 目录），那个查的是已建立的 OPC UA 会话状态，是另一回事。
- **工程经验补充**：搭一对「心跳灯 + 重启按钮」面板时，心跳灯走本 FB（每 2 秒），重启按钮走 `FB_OpcUAServer(eOPCUAServerOption_Restart)`。心跳灯红的时候按重启没用（重启走 OPC UA 通道，Server 进程已死），此时需要 Windows 管理员介入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_OpcUAServerGetStatus.TcPOU`](../examples/P_Demo_FB_OpcUAServerGetStatus.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：CX 控制器同时承担 PLC 业务 + OPC UA Server 角色给 SCADA 提供实时数据。运维需要在 HMI 上有一个「OPC UA 心跳灯」反映 Server 是否还活着；一旦红灯亮触发声光报警提示 IT 人员上线处理。这是工业场景里最常见的轻量探活需求。
- **价值**：单 FB + 一个周期定时器即可实现「2 秒粒度的 OPC UA 服务可用性监测」。无需写 ADS 通信代码、无需了解 ADS 索引组私有约定，PLC 工程师一键集成。
- **替代方案对比**：① 用 `FB_OpcUAServer` 的 ServerInfo 模式做探活——能确认 OPC UA 协议层真活着，但消耗 Server 一次会话资源，不适合高频；② 用 `Tc3_PLCopen_OpcUa.UA_Connect` + `UA_Disconnect`——能验证完整握手，但每次查询要建立完整会话开销大；③ 自己写 ADS `ADSREAD` 调 Server 私有索引——本 FB 已经封装好；④ 完全不监控——出问题只能等客户端报警，响应延迟分钟级。本 FB 是「最轻量、最快、最早期」的预警手段；与方案 ① / ② 配合可以做分层监控（本 FB 周期 2 秒、方案 ① 每分钟、方案 ② 每小时）。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.1.2.2（FB_OpcUAServerGetStatus）、§5.1.1.3（E_OpcUAServerStatus）、§8.2.1 ADS 状态码
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_server/7633284619.html
- **相关 FB**：`FB_OpcUAServer`（同 PLC 库，管理动作 / ServerInfo 查询）；`Tc3_PLCopen_OpcUa.UA_ConnectGetStatus`（查已建立的客户端 OPC UA 会话状态，逻辑层完全不同）
