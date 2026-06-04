# UA_Connect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_OPCUA` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Tc3_PLCopen_OpcUa / Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537634955.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_UA_Connect.TcPOU`](../examples/P_Demo_UA_Connect.TcPOU) |

---

## 1. 功能简述

OPC UA 客户端建会话功能块，对应 PLCopen「OPC UA Client Companion Spec」标准 FB（TF6100 PDF §5.2.3.2）。`Execute` 上升沿向 `ServerUrl` 指向的远端 OPC UA Server 发起一次完整会话握手（包含选 endpoint、协商 SecurityPolicy / MessageMode、用户身份验证、CreateSession），握手成功后输出会话句柄 `ConnectionHdl`，后续所有 `UA_Browse` / `UA_NodeGetHandle` / `UA_Read` / `UA_Write` / `UA_MethodCall` 等都靠这个句柄寻址。运行时需要 TF6100 license 并在 I/O 区配置好一个 OPC UA Virtual Device（产品版本 2.x 起的硬要求，PDF §5.2.1 给出强制说明）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute            : BOOL;
    ServerUrl          : STRING(MAX_STRING_LENGTH);
    SessionConnectInfo : ST_UASessionConnectInfo;     
    Timeout            : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次建会话请求 |
| `ServerUrl` | `STRING(MAX_STRING_LENGTH)` | — | 目标 OPC UA Server 的 endpoint URL，如 `'opc.tcp://172.16.3.207:4840'` 或 `'opc.tcp://CX_0193BF:4840'` |
| `SessionConnectInfo` | `ST_UASessionConnectInfo` | — | 会话配置结构：应用名、SecurityMessageMode、SecurityPolicy、TransportProfile、用户身份令牌、会话超时、连接超时（字段定义见本文下方接口章节 `ST_UASessionConnectInfo` 子表） |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 端超时（全局常量默认 5 秒）。**经验法则：`Timeout > 2 × ST_UASessionConnectInfo.tConnectTimeout`** |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    ConnectionHdl : DWORD;
    Done          : BOOL;
    Busy          : BOOL;
    Error         : BOOL;
    ErrorID       : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ConnectionHdl` | `DWORD` | OPC UA 会话句柄。仅当 `Done = TRUE` 且 `Error = FALSE` 时有效；后续所有 PLCopen FB 都以此作为 `ConnectionHdl` 输入 |
| `Done` | `BOOL` | 成功完成时变 `TRUE`（与 `Busy` 互斥） |
| `Busy` | `BOOL` | 命令执行中。`Busy = TRUE` 期间不接受新命令；监控的是「应答到达时间」而非 TCP/IP 连接时间 |
| `Error` | `BOOL` | 失败时变 `TRUE`，错误码在 `ErrorID` |
| `ErrorID` | `DWORD` | 命令特定错误码（ADS 系统码 + 客户端自定义 `0xE4DDxxxx` 范围） |

### VAR_IN_OUT

无。

#### ST_UASessionConnectInfo（PDF §5.2.2.15）

```iecst
TYPE ST_UASessionConnectInfo:
STRUCT
    sApplicationName     : STRING(MAX_STRING_LENGTH);
    eSecurityMode        : E_UASecurityMsgMode;
    eSecurityPolicyUri   : E_UASecurityPolicy;
    eTransportProfileUri : E_UATransportProfile;
    stUserIdentTokenType : ST_UAUserIdentityTokenType;
    tSessionTimeout      : TIME;
    tConnectTimeout      : TIME;
END_STRUCT
END_TYPE
```

| 字段 | 说明 |
|---|---|
| `sApplicationName` | 客户端应用名，最长 255 字符 |
| `eSecurityMode` | 消息安全模式（None / Sign / Sign+Encrypt / BestAvailable）；详见 `E_UASecurityMsgMode`（PDF §5.2.2.8） |
| `eSecurityPolicyUri` | 安全策略（Basic128 / Basic128Rsa15 / Basic256 / None / BestAvailable）；详见 `E_UASecurityPolicy`（PDF §5.2.2.9） |
| `eTransportProfileUri` | 传输协议（`UATcp` / `WSHttpBinary` / `WSHttpXmlOrBinary` / `WSHttpXml`）；详见 `E_UATransportProfile`（PDF §5.2.2.11） |
| `stUserIdentTokenType` | 用户身份令牌结构：Anonymous / Username / x509 / IssuedToken；详见 `ST_UAUserIdentityTokenType`（PDF §5.2.2.22） |
| `tSessionTimeout` | OPC UA 会话超时 |
| `tConnectTimeout` | TCP/握手层连接超时（**要与 ADS Timeout 联动：ADS Timeout > 2 × ConnectTimeout**） |

（旧版本里还有一个 `sApplicationUri` 字段，PDF 注明自 TcUAClient 2.0.0.14 起改由证书自动指定，新库版本已不再使用。）

## 3. 行为说明

`Execute` 由 `FALSE → TRUE` 上升沿触发一次握手：FB 通过 ADS 向虚拟 OPC UA Device（I/O 区下挂的 TF6100 客户端模块）下发 Connect 命令，模块再走 OPC UA 协议向远端 Server 完成「OpenSecureChannel → CreateSession → ActivateSession」三段式握手。整个过程异步推进，必须每个 PLC 周期调用本 FB 让内部状态机推进（与所有 PLCopen 风格 FB 一致）。`Busy = TRUE` 期间不能再给新命令；`Done = TRUE` 一个周期标志成功完成，此后 `ConnectionHdl` 可用；`Error = TRUE` 则 `ErrorID` 标识失败原因。

握手内部细节：SecurityPolicy / MessageMode 不为 None 时 PLC 端必须先把证书装好（参考 PDF §4.14 安全章节）；用户身份是 Username/x509 时令牌字段必填（`ST_UAUserIdentityTokenType.sTokenParam1` 为用户名 / 证书路径，`sTokenParam2` 为密码 / 私钥密码）。`Timeout`（ADS 层）一定要比 `SessionConnectInfo.tConnectTimeout`（OPC UA 层）大至少一倍——否则在握手最后阶段 ADS 先超时，PLC 这边以 `1861` 错误终止，OPC UA 通道实际仍可能成功，造成 Server 端有一个「幽灵会话」直到自然超时。

会话寿命：成功拿到 `ConnectionHdl` 后只要不调 `UA_Disconnect` 且 Server 端不超时，会话会一直保持。但 PLC 程序 Reset / Re-download 后旧句柄在 PLC 这边失忆，Server 端却仍持有；通常做法是在 PLC 启动逻辑里先调一次 `UA_Disconnect(ConnectionHdl := 0)`——PDF §5.2.3.4 明确说传 0 句柄会断开本 client 持有的全部连接，用作启动清理。

**典型用法**：阶段 1 启动时调一次 `UA_Disconnect(0)`；阶段 2 用 `UA_Connect` 建会话；阶段 3 用 `UA_GetNamespaceIndex` 取目标 namespace；阶段 4 用 `UA_NodeGetHandle(List)` 取要读写的节点句柄；阶段 5 周期 `UA_Read` / `UA_Write` / `UA_MethodCall`；阶段 6 停机前 `UA_NodeReleaseHandle(List)` + `UA_Disconnect`。

**典型陷阱**：① 没在 I/O 区配 OPC UA Virtual Device → 在 TF6100 v2.x 上 `UA_Connect` 直接报 ADS 错误 6（参考 PDF §8.1 错误诊断）；② `ServerUrl` 拼错（漏 `opc.tcp://` 前缀或端口）→ `UAC_E_CONNECT_NOTFOUND`（`0xE4DD0110`）；③ `Timeout` 设得比 `tConnectTimeout` 还短 → 假超时 + Server 端遗留半成品会话；④ Security 配错（PLC 没证书但要求 Sign+Encrypt） → `UAC_E_UASECURITY`（`0xE4DD0102`）；⑤ 用户名 / 密码字段空着但 `eUserIdentTokenType = eUAUITT_Username` → Server 拒绝。

## 4. 错误码 / 返回值

`ErrorID` 为 ADS 错误码（高字 `0x0000`）或客户端自定义 `0xE4DDxxxx`。完整码表见 PDF §8.2.3，建会话最常碰到的：

| `ErrorID` (Hex) | 名称 | 含义 | 处理建议 |
|---|---|---|---|
| `0x0` | `ERR_NOERROR` | 成功 | 用 `ConnectionHdl` 做后续操作 |
| `0x6` | `ERR_TARGETPORTNOTFOUND` | TF6100 客户端模块未启动 / 未配 Virtual Device | 参考 PDF §8.1：在 I/O 区配 OPC UA Virtual Device，把 AMS Net ID 填到 `sNetId` 参数 |
| `0x745` (1861) | ADS Timeout | `Timeout` 到期 | 加大 `Timeout`（必须 > 2× `tConnectTimeout`）；检查网络 |
| `0xE4DD0001` | `UAC_E_FAIL` | OPC UA 服务调用失败 | 看 OPC UA Server 日志 |
| `0xE4DD0100` | `UAC_E_CONNECTED` | Server 已经连接（同一 `sNetId` 重复 Connect） | 复用现有句柄或先 Disconnect |
| `0xE4DD0101` | `UAC_E_CONNECT` | 建会话失败 | 检查 `ServerUrl` 拼写、Server 是否在线、防火墙 4840 端口 |
| `0xE4DD0102` | `UAC_E_UASECURITY` | UA 安全设置失败 | 检查证书互信、SecurityPolicy 配置 |
| `0xE4DD0107` | `UAC_E_SUSPENDED` | 设备繁忙 | 稍后重试 |
| `0xE4DD0110` | `UAC_E_CONNECT_NOTFOUND` | 目标主机不可达 | 检查 IP / DNS / 网络 |
| `0xE4DD0111` | `UAC_E_TIMEOUT` | 目标主机不应答 | 检查 Server 状态；加大 `tConnectTimeout` |

## 5. 使用注意 / 常见坑

- **TF6100 v2.x 必须先在 I/O 区配 OPC UA Virtual Device** 并把它的 AMS Net ID 写到 PLC 库的参数 `sNetId`（参数列表见 PDF §5.2.4）；否则 `UA_Connect` 直接报 ADS 错误 6（PDF §8.1 明确给出此场景）。
- **ADS Timeout 与 OPC UA tConnectTimeout 必须联动**：`Timeout ≥ 2 × tConnectTimeout`。例：业务允许的最长握手时间 = 5 秒 → `tConnectTimeout := T#5S`、`Timeout := T#12S`。
- **Server 端会留「半成品会话」**：握手中途 ADS 超时但 OPC UA 实际成功的场景下，Server 端有一个孤立会话直到 `tSessionTimeout` 自然过期。生产环境定期 `UA_Disconnect(0)` + 重连一次可避免长期累积。
- **Username 模式凭证存储**：`stUserIdentTokenType.sTokenParam2`（密码）存在 PLC 内存里以明文形式，**严禁把工程师/PLC 调试登录密码硬编码**；用一个专门的 OPC UA 客户端账户、最小权限。
- **重复 Connect 不会自动复用**：再来一次 `Execute` 上升沿 PDF/InfoSys 没明确，工程经验是会**报 `UAC_E_CONNECTED`（`0xE4DD0100`）拒绝**。要重连必须先 Disconnect 再 Connect。
- **工程经验补充**：生产代码里 `UA_Connect` 通常包在一个状态机里，自动监控 `UA_ConnectGetStatus`，断了就走「Disconnect → 等几秒 → Connect」重连流程；不要让业务层裸调 `UA_Connect`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UA_Connect.TcPOU`](../examples/P_Demo_UA_Connect.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 .TcPOU 文件中场景 / 价值 / 验证步骤三件套注释。

## 7. 业务场景与实际价值

- **场景**：本地 CX 控制器要从远端的 Siemens / Rockwell / 第三方 OPC UA Server 拉数据进 PLC，或反过来从 PLC 主动调远端 Server 上的 Method（如 RPC 控制远端 robot 启动）。`UA_Connect` 是这条客户端链路的入口；没有它后面所有 `UA_Read` / `UA_Write` / `UA_MethodCall` 都无从谈起。
- **价值**：PLCopen 标准接口屏蔽了底层 OPC UA 协议的全部复杂度（SecureChannel、Session、Activate、Heartbeat 等），PLC 工程师只需配会话参数和 endpoint，就能与任何符合 OPC UA 规范的 Server 互通。比自己用 ADS + 私有 socket 实现节省数月开发量。
- **替代方案对比**：① TF6100 Configurator 配「I/O Client」（变量直接映射到 IEC 变量）—适合静态周期采样，不适合动态 Method 调用；② 用 `Tc2_TcpIp` 自己实现 OPC UA 协议——可行但要写数千行解码代码，无人这么做；③ 跨 PLC 通讯用 ADS（`Tc2_DataExchange`）——仅 TwinCAT ↔ TwinCAT，不能连第三方 Server；④ **本 FB**——动态客户端场景的标准选择，覆盖 PLCopen Companion Spec 全部 16 个 FB。

## 8. 参考资料

- **PDF**：[TF6100_TC3_OPC_UA_Client_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6100_TC3_OPC_UA_Client_EN.pdf) §5.2.3.2（UA_Connect）、§5.2.2.15（ST_UASessionConnectInfo）、§5.2.4（参数列表）、§8.2.3（错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6100_tc3_opcua_client/537634955.html
- **相关 FB**：`UA_Disconnect`（必须配对，包括启动清理 `UA_Disconnect(0)`）；`UA_ConnectGetStatus`（监控已建会话状态）；`UA_GetNamespaceIndex`（建会话后必跑一次）；`UA_NodeGetHandle`（按 NodeID 取节点句柄）；`UA_Read` / `UA_Write` / `UA_MethodCall`（业务读写 / 调方法）
