# SetJsonAttribute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcMessage` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5006660363.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcMessage_SetJsonAttribute.xml`](../examples/P_Demo_FB_TcMessage_SetJsonAttribute.xml) |

---

## 1. 功能简述

`FB_TcMessage.SetJsonAttribute()` 给 message 实例附加一段 JSON 自定义属性，在事件分发到 HMI / 数据库 / 远程客户端时与标准字段一起传递。

用法与 `FB_TcAlarm.SetJsonAttribute()` 完全相同——单 STRING 参数，整段 JSON 一次性传入。适用：给消息附加批次号 / 操作员 / 配方版本等结构化上下文。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sJsonAttribute : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `STRING` | 合法 JSON 字符串（建议 STRING(255) 或更长） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sJsonAttribute : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `STRING` | 合法 JSON 字符串（建议 STRING(255) 或更长） |


## 3. 行为说明

方法签名只有一个 `VAR_IN_OUT CONSTANT sJsonAttribute : STRING`。EventLogger 把整段 JSON 存入message 的扩展属性表，下一次 `Send()` 时随事件一起广播给所有 listener 与持久化存储。重复调用本方法会**覆盖**上一次的 JSON 内容，不会做合并。

**调用时机**：在 `Send()` 之前调用，确保事件分发时 JSON 已附上。字符串必须是合法 JSON 对象或数组，否则 EventLogger 端解析失败、HMI 看不到自定义字段。VAR_IN_OUT CONSTANT 形式意味着 PLC 不复制字符串（节省栈空间），方法内部承诺不修改它——调用方仍可以正常使用同一变量。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | JSON 属性已成功写入 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 校验 JSON 格式 / 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 传入必须是**合法 JSON 整体**——`'{"a":1}'` 行；裸 `'hello'` 不合法。
- STRING 默认 80 字节往往不够，声明 `STRING(255)` 或更长。（工程经验补充）
- 调用会覆盖上次内容——要追加键得自己拼接完整 JSON。（工程经验补充）
- HMI 端要主动消费 JSON，默认只显示标准字段。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcMessage_SetJsonAttribute.xml`](../examples/P_Demo_FB_TcMessage_SetJsonAttribute.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

给配方切换 message 附加 batch id + operator name 用于 MES 审计追溯


工艺上下文直接挂在 message 上，省掉 MES 端做表关联


把字段塞进 `FB_TcArguments` → 适合标准类型不适合复杂 JSON；走外部数据库 INSERT → 阻塞 PLC 周期


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.11.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5006660363.html
- **相关**：`FB_TcMessage.Create`, `FB_TcAlarm.SetJsonAttribute`, `FB_TcEventBase.GetJsonAttribute`
