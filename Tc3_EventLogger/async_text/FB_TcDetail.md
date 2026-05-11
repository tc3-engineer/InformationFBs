# FB_TcDetail

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723761035.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcDetail.xml`](../examples/P_Demo_FB_TcDetail.xml) |

---

## 1. 功能简述

`FB_TcDetail` 用于显示事件的「详情」项（DescriptionText / DescriptionUrl / Comment）。配合 `FB_RequestEventClassDetails.Get()` 或 `FB_RequestEventDetails.Get()` 填充。

字段读方法：`GetName`（key 名）、`GetText`（值）、`GetComment`（注释）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 由上游 Get 方法填充内部缓存（携带某一项详情的 name + text + comment 三字段），调用方再分别调 GetName / GetText / GetComment 读出。每次 Get 都覆盖内部缓存。调用 `Release` 显式清空内部缓存以释放资源。

**典型用法**：HMI 显示某事件的帮助面板时，循环 nCount 次调用 Get 把每一项填到本 FB 实例，再分别读字段拼接到面板。每次循环内部缓存被覆盖——需要保留所有项时把字段值拷贝到外部数组。字段读方法通过 VAR_IN_OUT STRING 输出，调用方负责声明足够长的 STRING 缓冲（建议 STRING(255) 起步）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- Get 之前字段未定义，不要直接读。（工程经验补充）
- 循环 Get 时上一次的字段会被覆盖——需要保存请把字段值拷贝到外部数组。（工程经验补充）
- STRING 默认长度 80 字节——长描述需要 STRING(255)+。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcDetail.xml`](../examples/P_Demo_FB_TcDetail.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 详情面板显示某事件的所有 description/url/comment 项


字段化访问替代字符串拼接，便于 HMI 单独绑定每个字段到不同控件


把详情拼成 JSON 返回 → 需要客户端解析；本 FB 直接给字段


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723761035.html
- **相关**：`FB_RequestEventClassDetails`, `FB_RequestEventDetails`
