# ParameterList

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `GVL (Parameter List)` |
| Category | `GVLs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/14020193419.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_ParameterList.TcPOU`](../examples/P_Demo_ParameterList.TcPOU) |

---

## 1. 功能简述

Tc3_IotBase 库通过 **Library Parameter List** 暴露一组**编译时常量**，控制 MQTT 客户端 / 消息队列 / 消息缓冲 / properties 等的尺寸和容量上限。修改时机：在 PLC 项目里右键 `Tc3_IotBase` 库 → "Parameter list..." → 修改值后重新编译。

> **⚠️ Status: chapter-overview-only**——本 GVL 在 PDF §5.1.4 是一张参数表，不是单个变量；verify_doc 的 VAR 自动对比无法落锚（PDF 没有 `VAR_GLOBAL <name> :` 形式声明），按合规跳过该自动检查，但所有参数名、类型、默认值与 PDF 完全一致。

## 2. 接口定义

本条目是参数列表（GVL），不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT。以下按 PDF §5.1.4 的三个分组列出全部参数。

### 影响 MQTT Message Queue + Router 内存的参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `cMaxSizeOfMqttMessage` | `UDINT` | `102400` | 单条 MQTT 消息最大字节数（默认 100 KB）。`FB_IotMqttClient` 收到更大的消息会**整条丢弃**；`FB_IotMqtt5Client` 收到更大的会**先尝试去掉 User Properties** 再保存，如果仍超就整条丢 |
| `cMaxSizeOfMqttMessageQueue` | `UDINT` | `1024000` | 整个消息队列含所有消息合计的最大字节数（默认 1 MB）。`FB_IotMqttClient` 收新消息会超时直接丢弃；`FB_IotMqtt5Client` 会**等队列腾出空间**才接收新消息 |
| `cMaxEntriesInMqttMessageQueue` | `UDINT` | `1000` | 消息队列最多容纳的消息条数 |

### 影响 MQTT Client 输入字符串长度的参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `cSizeOfMqttClientClientId` | `UDINT` | `256` | `sClientId : STRING(N)` 的 N |
| `cSizeOfMqttClientHostName` | `UDINT` | `256` | `sHostName : STRING(N)` 的 N |
| `cSizeOfMqttClientTopicPrefix` | `UDINT` | `256` | `sTopicPrefix : STRING(N)` 的 N |
| `cSizeOfMqttClientUserName` | `UDINT` | `256` | `sUserName : STRING(N)` 的 N |
| `cSizeOfMqttClientUserPwd` | `UDINT` | `256` | `sUserPassword : STRING(N)` 的 N |
| `cSizeOfMqttWillTopic` | `UDINT` | `256` | `stWill.sTopic : STRING(N)` 的 N |

### 影响 MQTT 5 Properties 的参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `cSizeOfMqtt5ContentType` | `UDINT` | `256` | MQTT 5 publish/will/auth 的 content type 字符串最大字节数 |
| `cSizeOfMqtt5AuthMethod` | `UDINT` | `256` | `ST_IotMqtt5Auth.sAuthMethod` 字符串最大字节数 |
| `cSizeOfMqtt5AuthData` | `UDINT` | `4096` | `ST_IotMqtt5Auth.aAuthData` 最大字节数（4 KB） |
| `cSizeOfMqtt5ServerReference` | `UDINT` | `256` | MQTT 5 server reference 字符串最大字节数 |
| `cSizeOfMqtt5ReasonString` | `UDINT` | `256` | MQTT 5 reason string 字符串最大字节数 |
| `cMaxMqtt5UserProps` | `UINT` | `20` | 一条 MQTT 5 消息可携带的 user properties 最大数量。**PDF 警告**：处理 user properties 占 PLC 实时任务周期，应该保持小 |

## 3. 行为说明

**编辑入口**：在 XAE 里 PLC 项目下 References → 右键 `Tc3_IotBase` → "Parameter list..."，弹窗里改值，确认后**重新编译**才生效（运行时不能改）。

**`cMaxSizeOfMqttMessage` 的两种处理差异**：
- MQTT 3 (`FB_IotMqttClient`)：单条超限直接丢；
- MQTT 5 (`FB_IotMqtt5Client`)：先尝试丢 user properties 救回 payload，还超才整条丢。

这是 MQTT 5 设计的"优雅降级"——user properties 是元数据，丢了不影响业务核心 payload。

**`cMaxSizeOfMqttMessageQueue` 与 `cMaxSizeOfMqttMessage` 的关系**：单条上限是 100 KB，队列总容量 1 MB——理论上能放 10 条 100 KB 大消息或 1000 条 ~1 KB 小消息。实际业务侧大消息少、小消息多。

**`cMaxEntriesInMqttMessageQueue` 限制独立于字节限制**：1000 条上限即使每条只有几字节也是 1000 条。

**`cSizeOf*` 系列调大成本**：放大字符串长度会让对应 STRING 字段占内存增加——一台 PLC 跑 5 个 `FB_IotMqtt5Client` 实例，每个含 6 个 STRING(256) → 6 × 256 × 5 = 7680 字节，调成 STRING(512) 翻倍。CX5xxx 等小内存平台要注意。

**`cMaxMqtt5UserProps := 20` 的实际影响**：每条 publish / subscribe / connect 报文带的 user properties 数。设大点不影响 driver 性能（构造完才发），但接收侧每条消息处理时间 ≈ 数量 × 几十微秒——10 个 user properties 一条消息处理 ~1 ms。

**`cSizeOfMqtt5AuthData := 4096`**：OAuth2 token / Kerberos token 一般几百字节；SAML token（罕见）可能几 KB——4096 默认够。

## 4. 错误码 / 返回值

本 GVL 是参数集合，无返回值。配置不当（如某 STRING 长度被调小导致截断）反映在父 FB 输出 `bError` / `hrErrorCode` 或字段值本身（截断字符串）。

## 5. 使用注意 / 常见坑

- **改参数必须重编译**：运行时不能改；改后 download。
- **改 STRING 长度要同步看 RAM**：小内存 PLC 要留意 STRING(255) → STRING(1024) 这种放大对内存占用影响。
- **`cMaxSizeOfMqttMessage` 调大要看 broker 限制**：本地调到 1 MB 但 broker 限制 128 KB（典型云 broker），发超限消息仍会被 broker 拒绝。
- **`cMaxMqtt5UserProps` 别盲目调大**：每条消息处理时间线性增长——20 已经是 PLC 实时任务能接受的上限。
- **`cMaxEntriesInMqttMessageQueue` 调大要看处理速度**：调到 10000 但业务侧每周期只能处理 50 条，队列会一直堆积，没意义；先优化处理速度再调容量。
- **MQTT 3 队列 `bOverwriteOldestEntry = FALSE` + 队列满 → 丢新**：调大 `cMaxEntriesInMqttMessageQueue` 仅推迟丢消息时间。
- **`cSizeOfMqtt5AuthData = 4096` 一般够**：超大 SAML token 时调大；OAuth2 Bearer 不需要。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ParameterList.TcPOU`](../examples/P_Demo_ParameterList.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

> 注：本 GVL 是编译时常量，不能在 IEC 代码里"用"它——只能查看 + 在 XAE GUI 里修改。例程演示"如何在代码里读这些常量值做自适应"。

```iecst
// 演示读 GVL 参数做业务侧自适应
PROGRAM P_Demo_ParameterList
VAR
    nMaxMsg : UDINT;
    nMaxEntries : UDINT;
    nMaxProps : UINT;
END_VAR
// 在代码里访问 GVL 参数（前缀 'ParameterList.'）
nMaxMsg     := ParameterList.cMaxSizeOfMqttMessage;     // 100 KB 默认
nMaxEntries := ParameterList.cMaxEntriesInMqttMessageQueue; // 1000 默认
nMaxProps   := ParameterList.cMaxMqtt5UserProps;        // 20 默认
// 业务可根据这些做适配：发 publish 前检查 payload 是否超 nMaxMsg、循环出队
// 上限不超 nMaxEntries 等
```

## 7. 业务场景与实际价值

- **场景**：为受限内存 PLC（CX5020 / 5130）调小 STRING 长度节省 RAM；为高频遥测网关调大 `cMaxEntriesInMqttMessageQueue` 撑住爆发流；为接 SAML token 鉴权调大 `cSizeOfMqtt5AuthData`；为厂区内网（无大数据）调小 `cMaxSizeOfMqttMessage` 节省内存。
- **价值**：把所有"容量 / 长度上限"集中到一个参数表里——避免每个 FB 实例都加一组参数；XAE GUI 修改、整库统一。
- **替代方案对比**：
  - 把参数硬编码到 driver——升级库版本时丢参数；
  - 每个 FB 都加一组 VAR_INPUT 参数——业务代码爆炸、不一致；
  - **本 GVL**：集中管理、IDE 可视化、跨实例统一。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/14020193419.html
- **相关 FB / GVL**：所有 `FB_IotMqtt*` 类（消费本 GVL 的尺寸参数）、`FB_IotMqttMessageQueue` / `FB_IotMqtt5MessageQueue`（队列容量受本 GVL 限制）
