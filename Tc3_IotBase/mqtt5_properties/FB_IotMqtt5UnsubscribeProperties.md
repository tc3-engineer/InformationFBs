# FB_IotMqtt5UnsubscribeProperties

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT5 Properties` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13971628683.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqtt5UnsubscribeProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5UnsubscribeProperties.TcPOU) |

---

## 1. 功能简述

`FB_IotMqtt5UnsubscribeProperties` 是 MQTT 5 客户端**调 Unsubscribe 时附带 properties** 的容器功能块。`EXTENDS FB_IotMqtt5UserProperties`——所以本 FB 的主要"内容"就是 user properties。

MQTT 5 协议为 UNSUBSCRIBE 报文只定义了一种 properties：**User Properties**。除此之外没有其他 unsubscribe-specific 字段——所以本 FB 本身没有新增字段，只是给 unsubscribe 调用专门提供一个"properties 入口"。

业务侧的典型用法：声明 `fbUnsubProps : FB_IotMqtt5UnsubscribeProperties;` → 通过基类方法添加 user properties → `SetUnsubscribeProperties()` → 把 `pUnsubscribeProperties` 传给 `fbClient.Unsubscribe(..., pProps := ...)`。

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

### VAR_IN_OUT

无。

### Property

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `pUnsubscribeProperties` | `POINTER TO MqttUnsubscribeProperties` | Get | 内部 properties 结构指针——传给 `fbClient.Unsubscribe` 的 `pProps` 参数 |

外加从 `FB_IotMqtt5UserProperties` 继承的属性：`nUserPropertyCnt`（user properties 个数）。

### Method

| 方法 | 用途 |
|---|---|
| `SetUnsubscribeProperties` | 把当前 user properties 写入内部 `MqttUnsubscribeProperties` 结构 |

外加从 `FB_IotMqtt5UserProperties` 继承的方法：`AddUserProperty` / `ClearUserProperties` / `GetUserPropertyByIdx` / `GetUserPropertyValueByName` / `SetUserProperties`。

PDF 仅列方法名 / 用途，具体签名见 InfoSys topic 13971628683 或 IntelliSense。

## 3. 行为说明

**典型使用流**：
1. `fbUnsubProps.AddUserProperty(sName := 'reason', sValue := 'shutdown');`（继承自基类）
2. `fbUnsubProps.SetUnsubscribeProperties();`
3. `fbClient.Unsubscribe(sTopic := 'plc/v5/L1/cmd', pProps := fbUnsubProps.pUnsubscribeProperties);`

**为什么 unsubscribe 还要带 user properties**：MQTT 5 把"消息流元数据"扩展到所有报文——unsubscribe 时附 properties 让 broker 端能记录"为什么取消订阅"（停业务 / 切换实例 / 维护重启），用于运维审计或动态路由调整。多数业务场景**不需要**这些 user properties——直接 `fbClient.Unsubscribe(sTopic := ..., pProps := 0)` 即可。

**broker 处理 unsubscribe properties 的语义**：MQTT 5 规范 §3.10.2 只说 broker MUST 接受 user properties；具体怎么用没规定。生产 broker（EMQX / HiveMQ）一般会写入访问日志 + 触发 plugin 钩子供运维系统消费。

**与 `pUnsubscribeProperties` 的访问**：和其他 properties FB 一致——`pUnsubscribeProperties` 是 property 不带括号，返回内部结构地址。

**没 properties 时直接传 0**：unsubscribe 不带任何元数据的场景占绝大多数——`fbClient.Unsubscribe(sTopic := 'plc/v5/L1/cmd', pProps := 0)`，连 `FB_IotMqtt5UnsubscribeProperties` 实例都不用声明。

## 4. 错误码 / 返回值

输出 `bError` / `hrErrorCode`：本 FB 自身错误极少；broker 拒 UNSUBSCRIBE 由 `fbClient.bError` / UNSUBACK reason code 反映。

## 5. 使用注意 / 常见坑

- **多数场景不需要本 FB**：unsubscribe 不带 user properties 用 `pProps := 0` 即可。
- **本 FB 唯一用途**：给 UNSUBSCRIBE 附 user properties——主要是运维审计需求。
- **`AddUserProperty` 是基类方法**：用 IntelliSense 看签名（继承自 `FB_IotMqtt5UserProperties`）。
- **`SetUnsubscribeProperties` 必须调**：否则 driver 拿不到 properties。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqtt5UnsubscribeProperties.TcPOU`](../examples/P_Demo_FB_IotMqtt5UnsubscribeProperties.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_IotMqtt5UnsubscribeProperties
VAR
    fbClient     : FB_IotMqtt5Client := (sClientId := 'PLC5', sHostName := '127.0.0.1');
    fbUnsubProps : FB_IotMqtt5UnsubscribeProperties;
    bWantUnsub   : BOOL;
    fbTrigUnsub  : R_TRIG;
END_VAR
fbClient.Execute(bConnect := TRUE);
fbTrigUnsub(CLK := bWantUnsub);
IF fbTrigUnsub.Q THEN
    // 附 user property 让运维知道为什么取消订阅
    //   fbUnsubProps.AddUserProperty(sName := 'reason', sValue := 'maintenance');
    fbUnsubProps.SetUnsubscribeProperties();
    fbClient.Unsubscribe(sTopic := 'plc/v5/L1/cmd',
                         pProps := fbUnsubProps.pUnsubscribeProperties);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：PLC 运维：动态切换业务模式时（如从生产模式切到调试模式）取消对部分 topic 的订阅；维护重启前主动取消所有订阅。给 unsubscribe 附 `reason=mode-switch` / `reason=maintenance` 的 user property，broker 端日志记录原因便于事后审计；运维监控系统能据此触发"产线进入维护"通知。
- **价值**：MQTT 5 把 user properties 扩展到所有报文（CONNECT/PUBLISH/SUBSCRIBE/UNSUBSCRIBE/DISCONNECT）——unsubscribe 也能带"原因"元数据，运维链路 vs 业务链路完全分离。
- **替代方案对比**：
  - MQTT 3——UNSUBSCRIBE 报文只能带 topic，没有元数据；运维要"为什么这台 PLC 突然不订阅了"只能查 PLC 日志；
  - 用单独的"运维 topic" publish 状态变更——耦合应用层，规模化后管理麻烦；
  - **本 FB**：协议层原生支持 unsubscribe 元数据。
- **何时不用本 FB**：99% 业务场景——直接 `fbClient.Unsubscribe(sTopic := ..., pProps := 0)` 就够了。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.2.9.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/13971628683.html
- **相关 FB**：`FB_IotMqtt5Client.Unsubscribe`（消费 `pProps`）、`FB_IotMqtt5UserProperties`（基类，本 FB 主要内容来自这里）、`FB_IotMqtt5SubscribeProperties`（订阅侧对偶）
