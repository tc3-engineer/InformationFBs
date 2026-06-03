# PushbackCopyValue

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
| Example | [`examples/P_Demo_FB_JsonDomParser_PushbackCopyValue.TcPOU`](../examples/P_Demo_FB_JsonDomParser_PushbackCopyValue.TcPOU) |

---

## 1. 功能简述

在 JSON 数组末尾追加一个 Copy 类型的元素值。返回新元素的 `SJsonValue` 句柄。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    v : SJsonValue;
    json : SJsonValue;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `v` | `SJsonValue` | 目标 JSON 节点的 `SJsonValue` 句柄。 |
| `json` | `SJsonValue` | 源 JSON 节点 `SJsonValue`；操作的输入。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

在数组节点末尾追加一个元素，效果等价于 JavaScript 的 `arr.push(value)`。调用前数组节点必须已存在（`SetArray()` 或解析得到的数组节点），否则方法返回无效句柄。频繁 Push 会导致 router 内存扩张，长时间运行建议改用 `FB_JsonDynDomParser`。本方法属 `FB_JsonDomParser` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本方法返回 `SJsonValue` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SJsonValue` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。
- 数组节点必须已存在（用 `SetArray()` / `Add*Member()` 创建）才能 Push，否则返回无效句柄。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_PushbackCopyValue.TcPOU`](../examples/P_Demo_FB_JsonDomParser_PushbackCopyValue.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：循环把采样数据加入 JSON 数组（如 1 秒采 10 次温度，组成 10 元素数组上报）。
- **价值**：按位 append 比每次重建数组高效。
- **替代方案对比**：GetDocument + 字符串拼接重做数组 → 大数组时性能拉胯。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.78
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`, `ArrayBegin`, `ClearArray`
