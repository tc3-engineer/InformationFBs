# OnEndObject

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `ITcJsonSaxHandler` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219229195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ITcJsonSaxHandler_OnEndObject.TcPOU`](../examples/P_Demo_ITcJsonSaxHandler_OnEndObject.TcPOU) |

---

## 1. 功能简述

SAX 解析回调：扫描到 对象结束 `}` 时被调用，调用方业务代码可在此读取本次 token 内容并选择继续（返回 `S_OK`）或终止（返回 `S_FALSE`）解析。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法不应在业务代码里直接调用，而是由 SAX 解析器在扫描到对应 JSON token 时回调。实现者读取入参值并执行业务逻辑（如把值写入目标变量、过滤特定 key、累积统计等），然后返回 `HRESULT`：`S_OK` 继续扫描下一个 token；`S_FALSE` 立刻终止扫描并让上层的 `Parse()` / `ParseValues()` 返回。实现时注意：回调被反复调用，避免在内部做长耗时操作；也避免在回调里修改 SAX 解析器的输入字符串。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 `TRUE` 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` (0) | 操作成功，继续 | 继续下一步 |
| `S_FALSE` (1) | 在 SAX 回调里表示「请求终止解析」 | 让 `Parse()` 立即返回 |
| 其他 (E_*) | 操作失败 | 参考 PDF 第 7 章 ADS Return Codes 表 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`ITcJsonSaxHandler`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ITcJsonSaxHandler_OnEndObject.TcPOU`](../examples/P_Demo_ITcJsonSaxHandler_OnEndObject.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：SAX 解析到 EndObject 时业务代码的处理入口，常见用法包括只关心特定字段、做事件过滤、统计 token 数等。
- **价值**：实现该回调让业务关注点和 SAX 解析器解耦，不必自己维护扫描器状态机。
- **替代方案对比**：使用 DOM 解析全文再遍历 → 大文档内存占用大；自写 token 扫描 → 复杂、易错。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §5.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219229195.html
- **相关 FB / FC**：`ITcJsonSaxHandler`
