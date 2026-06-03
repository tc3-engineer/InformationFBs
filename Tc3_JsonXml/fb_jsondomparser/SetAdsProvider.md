# SetAdsProvider

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonDomParser` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonDomParser_SetAdsProvider.TcPOU`](../examples/P_Demo_FB_JsonDomParser_SetAdsProvider.TcPOU) |

---

## 1. 功能简述

配置 ADS provider（netID + port），让本 FB 通过指定的 ADS 路径访问目标 PLC 的符号信息。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    oid : OTCID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `oid` | `OTCID` | 通过 `OID(…)` 取得的对象 ID（`OTCID`）；用于 SetAdsProvider 关联其他 TwinCAT 对象。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

把本 FB 关联到指定的 ADS provider（目标 PLC 的 AMS NetID + 端口）。调用后，本 FB 的符号读写（如 `FB_JsonReadWriteDataType` 的方法）会通过指定 ADS 路径访问目标 PLC 的符号表；未调时默认走本地 PLC（NetID 空、端口 = 851）。用法：跨控制器读符号时，先 `SetAdsProvider(<远端 PLC NetID>, 851)` 再调业务方法。本方法属 `FB_JsonDomParser` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_SetAdsProvider.TcPOU`](../examples/P_Demo_FB_JsonDomParser_SetAdsProvider.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：在 `FB_JsonDomParser` 的工作流程里完成一个具体子操作；通常配合本 FB 的其他方法组合使用。
- **价值**：作为 `FB_JsonDomParser` API 的一部分提供标准化能力，业务代码无需自实现。
- **替代方案对比**：自己写实现 → 与本库类型/接口不互通；用其他库 → 与 TwinCAT 工程内现有 JSON/XML 流程脱节。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.96
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`, `AddAdsProviderMember`, `GetAdsProvider`
