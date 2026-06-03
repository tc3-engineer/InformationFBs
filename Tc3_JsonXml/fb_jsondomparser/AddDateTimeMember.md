# AddDateTimeMember

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
| Example | [`examples/P_Demo_FB_JsonDomParser_AddDateTimeMember.TcPOU`](../examples/P_Demo_FB_JsonDomParser_AddDateTimeMember.TcPOU) |

---

## 1. 功能简述

在 JSON 对象节点下增加一个键值对成员，值类型为 DateTime。通过键名（`key` 参数）和具体值（`value` 参数）写入 JSON DOM 文档；返回新增成员的 `SJsonValue` 句柄。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    v : SJsonValue;
    value : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `v` | `SJsonValue` | 目标 JSON 节点的 `SJsonValue` 句柄。 |
| `value` | `DATE_AND_TIME` | 回调传入的值；类型与回调方法名后缀对应。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    member : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `member` | `STRING` | 新增成员的键名（VAR_IN_OUT，调用方传入字符串）。 |


## 3. 行为说明

在对象节点下增加一个键值对成员，效果等价于 JavaScript 的 `obj[key] = value`。如果同名 key 已存在，本方法会再追加一个同名 member（PDF 强调：不去重），若需要先检查再写请用 `HasMember()` + `FindMember()` 组合或用 `SetXxx` 在已有节点上覆盖。调用前对象节点必须已存在；返回新增成员的 `SJsonValue` 句柄。

## 4. 错误码 / 返回值

本方法返回 `SJsonValue` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SJsonValue` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。
- 本方法不会去重——同名 key 多次 Add 会得到多个同名 member；要覆盖原值请用 `FindMember()` + `Set<Type>()` 或 `RemoveMemberByName()` + `Add*Member()`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_AddDateTimeMember.TcPOU`](../examples/P_Demo_FB_JsonDomParser_AddDateTimeMember.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：组装 JSON 报文时往对象里加 DateTime 类型的字段（如批次号、温度采样值、报警码等）。
- **价值**：单次调用即写键值对，无需自己组字符串避免转义问题。
- **替代方案对比**：手写 STRING 拼 `'"key":' + value` → 大量转义和分隔符出错；用 SAX writer → 适合流式构造但随机插入字段不便。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`, `SetDateTime`, `FindMember`
