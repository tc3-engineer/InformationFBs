# Unsubscribe

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_ListenerBase2` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050411915.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Unsubscribe.xml`](../examples/P_Demo_Unsubscribe.xml) |

---

## 1. 功能简述

`FB_ListenerBase2.Unsubscribe()` 取消 listener 订阅，停止接收事件回调。

调用时机：listener 实例即将销毁时（如配方切换、模块下线）；或临时停止接收事件（如调试 / 维护模式）。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用即同步生效——之后 EventLogger 不再把事件加入本 listener 的内部队列，队列中尚未处理的事件会被丢弃。Unsubscribe 之后再调 Execute 不会处理任何事件（队列为空）。

**典型用法**：FB_exit 里调一次 Unsubscribe 保证资源正确回收；模块下线（如配方切换需要清理旧模块）也应调用本方法。若需要临时停接事件可以 Unsubscribe → 业务处理 → 重新 Subscribe，但通常通过更新过滤器规则更轻量。listener 实例销毁前必须 Unsubscribe——否则 EventLogger 内部保留悬挂引用直到 PLC 重启。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 取消订阅成功 | 可销毁 listener 或重新 Subscribe |
| `ADS_E_NOTFOUND` | listener 未订阅过 | 通常无需处理 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Unsubscribe 后队列里的事件丢失——需要先 Execute 把队列清空再 Unsubscribe。
- `ADS_E_NOTFOUND` 表示"本来就没订阅"——不是真错误。
- listener 销毁前必须 Unsubscribe——否则 EventLogger 持有悬挂引用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Unsubscribe.xml`](../examples/P_Demo_Unsubscribe.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

模块下线前清理 listener 订阅


正确释放 EventLogger 资源


不 Unsubscribe 直接销毁 listener → EventLogger 留下悬挂引用，重启 PLC 才清理


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.5.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050411915.html
- **相关**：`FB_ListenerBase2.Subscribe`, `FB_ListenerBase2.Subscribe2`
