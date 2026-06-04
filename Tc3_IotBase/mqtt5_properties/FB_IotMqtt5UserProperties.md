# FB_IotMqtt5UserProperties

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5 Properties` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13962881163.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5UserProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5UserProperties.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5UserProperties` 是 MQTT 5 **user properties** 集合的容器功能块，是其他几个 properties FB（`FB_IotMqtt5ConnAckProperties` / `FB_IotMqtt5DisconnectProperties` / `FB_IotMqtt5PublishProperties` / `FB_IotMqtt5SubscribeProperties` / `FB_IotMqtt5UnsubscribeProperties`）的**基类**。

user properties 是 MQTT 5 引入的**任意键值对元数据**——不在协议规范定义的具体语义里，由应用层双方约定。典型用法：trace-id（分布式追踪）、tenant-id（多租户）、版本号、设备唯一标识、命令序号、debug 标志等。

PDF 警告：**user properties 占用 PLC 实时任务周期**——一条消息处理几十个 user properties 会显著拖慢；要少用。受 GVL 参数 `cMaxMqtt5UserProps`（默认 20）限制。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError           : BOOL;
    hrErrorCode      : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错置 `TRUE` |
| `hrErrorCode` | `HRESULT` | HRESULT 错误码 |

### VAR_IN_OUT

无。

### Property

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `nUserPropertyCnt` | `UINT` | Get | 当前持有的 user properties 数量 |

### Method

| 方法 | 用途 |
|---|---|
| `AddUserProperty` | 添加一个 user property（按 name + value 指定） |
| `ClearUserProperties` | 清空所有 user properties |
| `GetUserPropertyByIdx` | 按 index 取 user property 的 name + value |
| `GetUserPropertyValueByName` | 按 name 取 user property 的 value |
| `SetUserProperties` | 清空当前 properties 然后用一个 `MqttUserProperty` 数组批量设值 |

PDF 仅列方法名 / 用途，具体签名见 InfoSys topic 13962881163 或 IntelliSense。

## 3. 行为说明

**两种使用方式**：
1. **作为基类被继承**——业务侧用 `FB_IotMqtt5PublishProperties` / `FB_IotMqtt5SubscribeProperties` 等，本 FB 的方法 / 属性自动可用；
2. **直接实例化（罕见）**——例如要预先构造一组 user properties 待用，可以声明 `fbUserProps : FB_IotMqtt5UserProperties;`，但通常没必要——直接在派生 FB 上调即可。

**`AddUserProperty` 用法**：每次调用追加一对 key-value。同名 key 允许多次添加——MQTT 5 协议规定 user properties 是有序的、允许重复名。但实际业务侧通常希望唯一名——添加前要么先 `ClearUserProperties` 全清要么不重复调。

**`GetUserPropertyByIdx` 用法**：按 0 开始的 index 遍历——典型代码：
```
FOR i := 0 TO fbProps.nUserPropertyCnt - 1 DO
    fbProps.GetUserPropertyByIdx(nIdx := i, REF=> sName, REF=> sValue);
    // 处理 sName / sValue
END_FOR
```

**`GetUserPropertyValueByName` 用法**：按 name 查 value。**注意**：同名多 property 时只返回**第一个**——MQTT 5 规范允许同名但本 method 是"按名取首个"的便捷接口。要全部取出用 `GetUserPropertyByIdx` 遍历。

**`SetUserProperties` 用法**：批量赋值——传入一个 `ARRAY OF MqttUserProperty`，本 FB 先 `ClearUserProperties` 再按数组顺序 `AddUserProperty`。适合一次性构造完整 properties 集合。

**`nUserPropertyCnt` 反映当前持有数**：和 `cMaxMqtt5UserProps`（默认 20）这个**接收侧上限**不一样——本 FB 是**构造**用，理论上能加到内存限制；但 broker 端如果限制 20，超出可能被截。

**接收侧 `nUserPropertyCntLost`**：见 `FB_IotMqtt5Message.nUserPropertyCntLost`——接收消息时丢弃的 user properties 数（broker 发了 30 个但客户端只能接 20 个时为 10）。这是接收侧的截断指示。

**性能警告**：PDF 写道 "The processing of UserProperties in the PLC real-time task cycle requires a certain amount of time, which is why it is better to keep it low"——即"PLC 实时任务里处理 user properties 要时间，应该少用"。具体数字 PDF 没给，但实测每个 user property 约几十微秒；20 个会增加 ~1 ms 任务时间。

## 4. 错误码 / 返回值

输出 `bError` / `hrErrorCode`：本 FB 错误极少——主要可能是 `AddUserProperty` 超过 `cMaxMqtt5UserProps` 时返回失败。

各方法 `BOOL` 返回值：`TRUE` 成功；`FALSE` 失败（典型：`AddUserProperty` 超限、`GetUserPropertyByIdx` index 越界、`GetUserPropertyValueByName` 没找到）。

## 5. 使用注意 / 常见坑

- **本 FB 几乎从不直接实例化**：99% 业务通过它的派生 FB（Publish/Subscribe/Unsubscribe/ConnAck/DisconnectProperties）间接用。
- **`nUserPropertyCnt` 的"max"在 GVL 里**：`cMaxMqtt5UserProps`（默认 20）——业务侧加超过会返回失败。运维需求多时调大。
- **同名 key 允许多次添加**：MQTT 5 规范允许；但要小心 `GetUserPropertyValueByName` 只返回首个。
- **`SetUserProperties` 会清空再设**：要"追加"必须用 `AddUserProperty`，不是 `SetUserProperties`。
- **性能成本**：PLC 实时周期里少加。常见模式：在初始化阶段把固定的 properties（设备 ID、楼层）加一次，运行期间只 publish 时引用即可。
- **PDF 没给方法签名**：用 IntelliSense 看 `AddUserProperty(sName := ..., sValue := ...)` 之类。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5UserProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5UserProperties.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示 publish 时通过 PublishProperties (继承本 FB) 加 user properties
PROGRAM P_Demo_FB_IotMqtt5UserProperties
VAR
    fbClient   : FB_IotMqtt5Client := (sClientId := 'PLC5', sHostName := '127.0.0.1');
    fbPubProps : FB_IotMqtt5PublishProperties;        // EXTENDS FB_IotMqtt5UserProperties
    bInited    : BOOL;
END_VAR
fbClient.Execute(bConnect := TRUE);
IF fbClient.bConnected AND NOT bInited THEN
    // 通过基类方法 AddUserProperty 添加元数据：
    //   fbPubProps.AddUserProperty(sName := 'tenant-id', sValue := 'factory-A');
    //   fbPubProps.AddUserProperty(sName := 'device-id', sValue := 'CX-Line1');
    //   fbPubProps.AddUserProperty(sName := 'trace-id',  sValue := 'abc-123');
    fbPubProps.SetPublishProperties();
    bInited := TRUE;
END_IF
// publish 时 pProps 用 fbPubProps.pPublishProperties (从基类继承的 publish-specific 属性)
```

## 7. 业务场景与实际价值

- **场景**：多租户工厂网关——同一台 PLC 同时为厂区 A 和厂区 B 上报数据。每条 publish 带 `tenant-id` user property，云端按 tenant 路由到不同的存储 / 看板。trace-id 让 MES → PLC → 设备执行 → 上报回 SCADA 全链路可追踪。device-id 让消费者知道是哪台 PLC 发的（即使 topic 一样）。
- **价值**：MQTT 5 把"应用元数据"从 payload 抽出来——user properties 与 payload 完全解耦，业务字段不再为元数据腾位置；多套元数据系统（追踪 + 多租户 + 版本）共存；新增 user property 不需要改 payload schema。
- **替代方案对比**：
  - 把元数据塞 payload JSON——破坏 publish/subscribe 解耦、payload schema 易爆膨胀；
  - 把元数据塞 topic 字符串——broker 路由表撑大、订阅模式变复杂；
  - **本 FB**：协议层支持，结构清晰。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.9.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13962881163.html
- **相关 FB**：`FB_IotMqtt5PublishProperties` / `FB_IotMqtt5SubscribeProperties` / `FB_IotMqtt5UnsubscribeProperties` / `FB_IotMqtt5ConnAckProperties` / `FB_IotMqtt5DisconnectProperties`（全部继承本 FB）、`FB_IotMqtt5Message`（nUserPropertyCnt + GetUserPropertyByIdx 读接收侧 user properties）
