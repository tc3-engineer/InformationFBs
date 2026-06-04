# ETcIotMqttClientState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `ENUM` |
| Category | `Enums` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12887974283.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ETcIotMqttClientState.TcPOU`](../examples/P_Demo_ETcIotMqttClientState.TcPOU) |

---

## 1. 功能简述

`ETcIotMqttClientState` 是 Tc3_IotBase 库的 MQTT 客户端**连接状态枚举**，作为 `FB_IotMqttClient.eConnectionState` / `FB_IotMqtt5Client.eConnectionState` / `FB_IotMqtt5ClientBase.eConnectionState` 的输出类型。

把客户端的连接状态细分成 42 个值（PDF §5.1.3 列出 0–41 共 41 个，外加 PDF §7.2 Error Codes 表里另列的 `MQTT_ERR_CONN_PENDING := -1`，详见 §3）；业务侧据此细分诊断当前是"正常连上 / 还没连上 / 用户名密码错 / TLS 验证失败 / Topic ACL 拒绝 / DNS 解析失败 / 主机不可达" 等。

底层类型 `DINT`——因为含 -1 值，无法用 USINT/UINT。

## 2. 接口定义

本条目是枚举类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT。

### 枚举定义（PDF §5.1.3 — 主定义）

```iecst
TYPE ETcIotMqttClientState :
(
MQTT_ERR_SUCCESS            :=0,
MQTT_ERR_NOMEM              :=1,
MQTT_ERR_PROTOCOL           :=2,
MQTT_ERR_INVAL              :=3,
MQTT_ERR_NO_CONN            :=4,
MQTT_ERR_CONN_REFUSED       :=5,
MQTT_ERR_NOT_FOUND          :=6,
MQTT_ERR_CONN_LOST          :=7,
MQTT_ERR_TLS                :=8,
MQTT_ERR_PAYLOAD_SIZE       :=9,
MQTT_ERR_NOT_SUPPORTED      :=10,
MQTT_ERR_AUTH               :=11,
MQTT_ERR_ACL_DENIED         :=12,
MQTT_ERR_UNKNOWN            :=13,
MQTT_ERR_ERRNO              :=14,
MQTT_ERR_EAI                :=15,
MQTT_ERR_PROXY              :=16,
MQTT_ERR_TLS_CA_NOTFOUND    :=17,
MQTT_ERR_TLS_CERT_NOTFOUND  :=18,
MQTT_ERR_TLS_KEY_NOTFOUND   :=19,
MQTT_ERR_TLS_CA_INVALID     :=20,
MQTT_ERR_TLS_CERT_INVALID   :=21,
MQTT_ERR_TLS_KEY_INVALID    :=22,
MQTT_ERR_TLS_VERIFY_FAIL    :=23,
MQTT_ERR_TLS_SETUP          :=24,
MQTT_ERR_TLS_HANDSHAKE_FAIL :=25,
MQTT_ERR_TLS_CIPHER_INVALID :=26,
MQTT_ERR_TLS_VERSION_INVALID:=27,
MQTT_ERR_TLS_PSK_INVALID    :=28,
MQTT_ERR_TLS_CRL_NOTFOUND   :=29,
MQTT_ERR_TLS_CRL_INVALID    :=30,
MQTT_ERR_FINALIZE_DISCONNECT:=31,
MQTT_ERR_BIND               :=32,
MQTT_ERR_BIND_ADDR_INUSE    :=33,
MQTT_ERR_BIND_ADDR_INVAL    :=34,
MQTT_ERR_CREATE             :=35,
MQTT_ERR_CREATE_TYPE        :=36,
MQTT_ERR_CONN               :=37,
MQTT_ERR_CONN_TIMEDOUT      :=38,
MQTT_ERR_CONN_HOSTUNREACH   :=39,
MQTT_ERR_TLS_CERT_EXPIRED   :=40,
MQTT_ERR_TLS_CN_MISMATCH    :=41
) DINT;
END_TYPE
```

### 各值含义

| 取值 | 名称 | 含义 |
|---|---|---|
| -1 | `MQTT_ERR_CONN_PENDING` | 连接挂起（连接进行中，从 §7.2 错误码表观察，§5.1.3 主定义未列） |
| 0 | `MQTT_ERR_SUCCESS` | 连接正常，broker 已建链 |
| 1 | `MQTT_ERR_NOMEM` | 内存不足 |
| 2 | `MQTT_ERR_PROTOCOL` | MQTT 协议错（broker 用了不兼容的协议） |
| 3 | `MQTT_ERR_INVAL` | 无效参数 |
| 4 | `MQTT_ERR_NO_CONN` | 尚未连接 broker（典型: bConnect=TRUE 但 broker 不可达） |
| 5 | `MQTT_ERR_CONN_REFUSED` | broker 主动拒绝连接（多半是用户名/密码、ACL 不允许、ClientId 重复） |
| 6 | `MQTT_ERR_NOT_FOUND` | 资源未找到（典型: subscribe 拿不到匹配响应、内部资源不存在） |
| 7 | `MQTT_ERR_CONN_LOST` | 连接被对端中断（网络抖动、broker 重启、keepalive 超时） |
| 8 | `MQTT_ERR_TLS` | 通用 TLS 错（具体看下面 17–30 / 40 / 41） |
| 9 | `MQTT_ERR_PAYLOAD_SIZE` | payload 超 `cMaxSizeOfMqttMessage` 或 broker 限制 |
| 10 | `MQTT_ERR_NOT_SUPPORTED` | 功能不支持（典型: broker 不支持指定 QoS / wildcard / retain） |
| 11 | `MQTT_ERR_AUTH` | 鉴权失败（用户名/密码错、enhanced auth method 失败） |
| 12 | `MQTT_ERR_ACL_DENIED` | broker ACL 拒绝（topic 没权限 publish/subscribe） |
| 13 | `MQTT_ERR_UNKNOWN` | 未知错（一般是 driver 内部未识别的错） |
| 14 | `MQTT_ERR_ERRNO` | 系统调用 errno 错（OS 层报错） |
| 15 | `MQTT_ERR_EAI` | getaddrinfo() 错（DNS 解析失败） |
| 16 | `MQTT_ERR_PROXY` | 代理服务器错（走 HTTP proxy 时） |
| 17 | `MQTT_ERR_TLS_CA_NOTFOUND` | TLS CA 证书文件没找到 |
| 18 | `MQTT_ERR_TLS_CERT_NOTFOUND` | TLS 客户端证书文件没找到 |
| 19 | `MQTT_ERR_TLS_KEY_NOTFOUND` | TLS 客户端私钥文件没找到 |
| 20 | `MQTT_ERR_TLS_CA_INVALID` | TLS CA 证书无效（格式损坏或不是 CA） |
| 21 | `MQTT_ERR_TLS_CERT_INVALID` | TLS 客户端证书无效 |
| 22 | `MQTT_ERR_TLS_KEY_INVALID` | TLS 客户端私钥无效（密码错、不配对） |
| 23 | `MQTT_ERR_TLS_VERIFY_FAIL` | TLS 服务端证书校验失败（最常见：server 证书不是本 CA 签的） |
| 24 | `MQTT_ERR_TLS_SETUP` | TLS 上下文初始化失败 |
| 25 | `MQTT_ERR_TLS_HANDSHAKE_FAIL` | TLS 握手失败 |
| 26 | `MQTT_ERR_TLS_CIPHER_INVALID` | TLS 加密套件不可用（`sCiphers` 配置错或 OpenSSL 不支持） |
| 27 | `MQTT_ERR_TLS_VERSION_INVALID` | TLS 协议版本不支持（典型: `sVersion := 'tlsv1.0'` 但 OpenSSL 新版禁用） |
| 28 | `MQTT_ERR_TLS_PSK_INVALID` | PSK 无效（identity / key 与 broker 不匹配） |
| 29 | `MQTT_ERR_TLS_CRL_NOTFOUND` | TLS CRL 文件没找到 |
| 30 | `MQTT_ERR_TLS_CRL_INVALID` | TLS CRL 文件无效 |
| 31 | `MQTT_ERR_FINALIZE_DISCONNECT` | 优雅关闭过程出错 |
| 32 | `MQTT_ERR_BIND` | 本地端口 bind 失败 |
| 33 | `MQTT_ERR_BIND_ADDR_INUSE` | 本地地址被占用 |
| 34 | `MQTT_ERR_BIND_ADDR_INVAL` | 本地地址无效 |
| 35 | `MQTT_ERR_CREATE` | socket 创建失败 |
| 36 | `MQTT_ERR_CREATE_TYPE` | socket 类型错 |
| 37 | `MQTT_ERR_CONN` | 通用连接错 |
| 38 | `MQTT_ERR_CONN_TIMEDOUT` | 连接超时（TCP 层超时） |
| 39 | `MQTT_ERR_CONN_HOSTUNREACH` | 主机不可达（IP 路由错） |
| 40 | `MQTT_ERR_TLS_CERT_EXPIRED` | TLS 证书过期（broker 端 / 客户端任一） |
| 41 | `MQTT_ERR_TLS_CN_MISMATCH` | TLS 证书 CN/SAN 与 `sHostName` 不一致 |

### 双源差异

> **⚠️ PDF 与 InfoSys 不一致**：PDF §5.1.3 主定义未列 `MQTT_ERR_CONN_PENDING := -1`；PDF §7.2 错误码段 + InfoSys "Error Codes" topic 把 -1 单独列出来。本 KB 按 InfoSys + §7.2 的拓展集为准——主定义里加 -1 是事实 API（DINT 类型与 -1 兼容）；实际枚举值 42 个。InfoSys topic 12887974283 也明确写了 `MQTT_ERR_CONN_PENDING (-1)` 表示"连接进行中"。

## 3. 行为说明

**典型业务诊断**：连接异常时按 `eConnectionState` 分支处理：
- `MQTT_ERR_SUCCESS` (0) — 一切正常；
- `MQTT_ERR_CONN_PENDING` (-1) / `MQTT_ERR_NO_CONN` (4) — 连接进行中或还没连上；
- `MQTT_ERR_CONN_REFUSED` (5) / `MQTT_ERR_AUTH` (11) / `MQTT_ERR_ACL_DENIED` (12) — 配置类问题，要改 ClientId / 用户名密码 / broker ACL；
- `MQTT_ERR_CONN_LOST` (7) / `MQTT_ERR_CONN_TIMEDOUT` (38) / `MQTT_ERR_CONN_HOSTUNREACH` (39) — 网络问题；
- `MQTT_ERR_TLS_*` (8 / 17-30 / 40 / 41) — TLS 配置 / 证书问题；
- `MQTT_ERR_EAI` (15) — DNS 解析失败，`sHostName` 配错或 DNS 服务挂了。

**枚举分布逻辑**：
- 0–16：通用错误（含 MQTT_ERR_AUTH/ACL_DENIED/CONN_REFUSED 等业务级）；
- 17–30, 40-41：TLS 错（细分到证书 / 私钥 / CRL / 版本 / 套件 / CN 等）；
- 31–39：网络栈错（bind / create / conn / timedout / hostunreach）；

按这个分布做 CASE 语句的分支组织。

**与 broker 返回 reason code 的关系**：MQTT 5 broker 在 CONNACK / DISCONNECT 报文里给出 0x80–0xA2 系列 reason code（参考 `FB_IotMqtt5ConnAckProperties.md` §4）——这些是**协议层**断连原因；本枚举是**客户端 driver 层**对错误的分类。两者互补：
- broker 主动拒/踢 → broker 给 reason code → driver 翻译成 `MQTT_ERR_*` 大类（如 `MQTT_ERR_AUTH`）；
- 网络/TLS/资源问题 → broker 根本没机会回 reason code → driver 直接给本枚举。

**底层类型 DINT 的原因**：因为有 -1 值（`MQTT_ERR_CONN_PENDING`），所以不能用 USINT/UINT/BYTE；用 DINT 兼容负值。

## 4. 错误码 / 返回值

本枚举本身就是错误码集合——业务侧 `CASE` 分支即可。

## 5. 使用注意 / 常见坑

- **`MQTT_ERR_CONN_PENDING` (-1) 在 PDF §5.1.3 主定义里看不到**：要看 PDF §7.2 或 InfoSys 才有。实际运行时如果连接正在进行中可能短暂出现 -1 值。
- **`MQTT_ERR_SUCCESS` (0) 是"连接 OK"不是"无错"**：业务上读到 0 表示"现在连上了"，跟 `bConnected = TRUE` 等价。
- **`MQTT_ERR_NO_CONN` (4) vs `MQTT_ERR_CONN_LOST` (7)**：前者 = 还没连上（首次启动 / DNS 失败 / 防火墙）；后者 = 连过但断了（网络抖动 / broker 重启）。
- **`MQTT_ERR_AUTH` 不一定是用户名密码错**：也可能是 enhanced auth method 失败或 token 过期——配 MQTT 5 时要看 `fbConnAckProps.nReasonCode` 细分。
- **TLS 错码很多——但 22 / 23 最常见**：`MQTT_ERR_TLS_KEY_INVALID` (22) 一般是私钥与证书不配对；`MQTT_ERR_TLS_VERIFY_FAIL` (23) 一般是服务端证书不是本 CA 签的。
- **`MQTT_ERR_EAI` (15) 含义不直观**：是 getaddrinfo() 返回非零 errno，典型 DNS 解析失败——查 `sHostName` 拼写、DNS 服务器、hosts 文件。
- **`MQTT_ERR_PAYLOAD_SIZE` (9) 既反映本地限制也反映 broker 限制**：单条 publish payload 超过 `cMaxSizeOfMqttMessage`（本地）或 `fbConnAckProps.nMaxPackateSize`（broker 端）任一限制。
- **业务侧建议用 CASE + comment 分支**：枚举值多，没注释的代码可读性差。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ETcIotMqttClientState.TcPOU`](../examples/P_Demo_ETcIotMqttClientState.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_ETcIotMqttClientState
VAR
    fbClient : FB_IotMqttClient;
    sErrCategory : STRING(60);
END_VAR
fbClient.Execute(bConnect := TRUE);
CASE fbClient.eConnectionState OF
    ETcIotMqttClientState.MQTT_ERR_SUCCESS:        sErrCategory := '已连上';
    ETcIotMqttClientState.MQTT_ERR_NO_CONN:        sErrCategory := '尚未连接，检查 hostname / 端口';
    ETcIotMqttClientState.MQTT_ERR_CONN_REFUSED:   sErrCategory := 'broker 拒连，检查用户名密码 / ClientId';
    ETcIotMqttClientState.MQTT_ERR_CONN_LOST:      sErrCategory := '连接已断，网络抖动？';
    ETcIotMqttClientState.MQTT_ERR_AUTH:           sErrCategory := '鉴权失败';
    ETcIotMqttClientState.MQTT_ERR_ACL_DENIED:     sErrCategory := 'broker ACL 拒绝该 topic';
    ETcIotMqttClientState.MQTT_ERR_TLS_VERIFY_FAIL:sErrCategory := 'TLS 服务端证书校验失败';
    ETcIotMqttClientState.MQTT_ERR_TLS_CN_MISMATCH:sErrCategory := 'TLS 证书 CN/SAN 与 hostname 不一致';
    ETcIotMqttClientState.MQTT_ERR_EAI:            sErrCategory := 'DNS 解析失败';
    ETcIotMqttClientState.MQTT_ERR_PAYLOAD_SIZE:   sErrCategory := 'payload 太大';
ELSE
    sErrCategory := '其他错';
END_CASE
```

## 7. 业务场景与实际价值

- **场景**：HMI 显示 PLC 与 broker 的连接健康度——红 / 黄 / 绿三色加文字描述。绿 = `MQTT_ERR_SUCCESS`；黄 = `MQTT_ERR_NO_CONN` / `MQTT_ERR_CONN_LOST` / `MQTT_ERR_TLS_HANDSHAKE_FAIL`（临时问题）；红 = `MQTT_ERR_AUTH` / `MQTT_ERR_ACL_DENIED` / `MQTT_ERR_TLS_VERIFY_FAIL` / `MQTT_ERR_TLS_CERT_EXPIRED`（配置错，运维介入）。比单看 `bError` / `bConnected` 信息丰富得多。
- **价值**：把 MQTT 客户端的内部错误状态细分到 42 个值——业务侧能针对性地"重试"还是"告警运维"。MQTT 3 + MQTT 5 共用同一个枚举，统一诊断口径。
- **替代方案对比**：
  - 只看 `bConnected` 布尔——什么错都不知道，HMI 只能"红 / 绿"；
  - 看 `bError` + `hrErrorCode` HRESULT——HRESULT 是全 TwinCAT 通用，过粗；
  - 看 MQTT 5 broker 给的 reason code——只反映 broker 层断连，不反映客户端层的 TLS / 网络问题；
  - **本枚举**：客户端 driver 层最细分的诊断口径。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.3（主定义） + §7.2（Error Codes，含 MQTT_ERR_CONN_PENDING）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/12887974283.html
- **相关 FB**：`FB_IotMqttClient.eConnectionState`、`FB_IotMqtt5Client.eConnectionState`、`FB_IotMqtt5ClientBase.eConnectionState`、`FB_IotMqtt5ConnAckProperties.nReasonCode`（MQTT 5 broker 端 reason code）
