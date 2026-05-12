# HRESULTAdsErr_TO_TcEventEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION` |
| Category | `Function` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5001571211.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_HRESULTAdsErr_TO_TcEventEntry.xml`](../examples/P_Demo_HRESULTAdsErr_TO_TcEventEntry.xml) |

---

## 1. 功能简述

`HRESULTAdsErr_TO_TcEventEntry` 把一个 HRESULT 形式的 ADS 错误码（`E_HRESULTAdsErr` 枚举）转换成 `TcEventEntry`。

**返回 BOOL**：TRUE = 转换成功（要求 HRESULT facility 是 ADS_FACILITY）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    hr : E_HRESULTAdsErr;
    stEventEntry : REFERENCE TO TcEventEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hr` | `E_HRESULTAdsErr` | 要转换的 HRESULT ADS 错误码（E_HRESULTAdsErr 枚举） |
| `stEventEntry` | `REFERENCE TO TcEventEntry` | REFERENCE 输出：成功时为对应事件定义 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本函数同步执行转换并返回 `BOOL`：TRUE 表示转换成功（输出参数已填好），FALSE 表示转换失败（典型原因：事件类未知 / 错误码不属于 ADS facility）。

**典型用法**：把 ADS 调用返回的错误码统一转换为 EventLogger 可识别的事件，再通过 `FB_TcAlarm.CreateEx()` / `SendMessageEx()` 报告——把 ADS 错误纳入 EventLogger 审计体系。或反过来：把 EventLogger 收到的事件还原成 ADS 错误码做兼容旧代码处理。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 转换成功，输出参数已填好 | 继续使用输出 |
| `FALSE` | 转换失败（事件类未知或错误码不在 ADS facility 范围） | 检查输入是否合法 ADS 错误 |

## 5. 使用注意 / 常见坑

- 失败时输出参数内容**未定义**——必须先检查返回 BOOL 再读输出。
- HRESULT 转换要求 facility 码必须是 ADS_FACILITY；其他 facility 的 HRESULT 会失败。（工程经验补充）
- E_AdsErr 范围之外的整数转换可能失败——只支持枚举内的值。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HRESULTAdsErr_TO_TcEventEntry.xml`](../examples/P_Demo_HRESULTAdsErr_TO_TcEventEntry.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

EventLogger 接收到远程系统的 ADS HRESULT 错误后转 TcEventEntry 报警


把不同形式的 ADS 错误码（int / HRESULT）统一归一到 EventLogger 体系


自己解析 HRESULT facility 拆出 ADS code → 容易出错；本 FC 一句完成


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5001571211.html
- **相关**：`AdsErr_TO_TcEventEntry`, `HRESULTAdsErr_TO_TcEventEntry`, `TcEventEntry_TO_AdsErr`, `TcEventEntry_TO_HRESULTAdsErr`
