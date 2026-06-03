# NextArray

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
| Example | [`examples/P_Demo_FB_JsonDomParser_NextArray.TcPOU`](../examples/P_Demo_FB_JsonDomParser_NextArray.TcPOU) |

---

## 1. 功能简述

把数组迭代器向后推进一位，返回下一个元素的 `SJsonAIterator`。到达数组末尾时返回值与 `ArrayEnd()` 相同。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    v : SJsonAIterator;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `v` | `SJsonAIterator` | 目标 JSON 节点的 `SJsonValue` 句柄。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

数组遍历用迭代器三件套之一。典型用法：`it := fb.ArrayBegin(arr);` 取首元素，循环里 `it := fb.NextArray(it);` 推进，条件 `it <> fb.ArrayEnd(arr)` 作循环终止判断（PDF 语义：ArrayEnd 返回的是末元素之后的位置）。迭代过程中不要对数组做 Add/Remove 操作，否则迭代器失效。本方法属 `FB_JsonDomParser` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本方法返回 `SJsonAIterator` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SJsonAIterator` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_NextArray.TcPOU`](../examples/P_Demo_FB_JsonDomParser_NextArray.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
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

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.73
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`
