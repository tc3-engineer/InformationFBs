# GUID_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35275147.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_GUID_TO_STRING.xml`](../examples/P_Demo_GUID_TO_STRING.xml) |

---

## 1. 功能简述

把结构化 `GUID` 变量转成无花括号的 GUID 字符串（`'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'`），36 字符。`GUID_TO_REGSTRING` 是带花括号的版本（38 字符）。

适合纯展示 / 日志输出场景；和 Windows 注册表对接用 `GUID_TO_REGSTRING`。反向是 `STRING_TO_GUID`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stIn : GUID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `stIn` | `GUID` | — | 待转换的 GUID 结构。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING` | 36 字符的 GUID 字符串（无花括号）。全零 GUID 返回 `'00000000-0000-0000-0000-000000000000'`。 |

### VAR_OUTPUT

无。

## 3. 行为说明

格式与 `GUID_TO_REGSTRING` 几乎相同，只是去掉首末两个花括号，结果固定 36 字符的形式 `'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'`。各段对应：`stIn.Data1`（4 字节）展开为 8 个十六进制大写字符；`stIn.Data2`（2 字节）展开为 4 个；`stIn.Data3`（2 字节）展开为 4 个；`stIn.Data4[0..1]`（2 字节）展开为 4 个；`stIn.Data4[2..7]`（6 字节）展开为 12 个；各段之间用连字符 `-` 分隔。

实现属性：函数永远成功（任意 GUID 都能转，PDF 不列错误码）；hex 字母按 GUID 文本规范输出大写（如需小写自行调 `F_ToLCase`）；全零 GUID 输出 `'00000000-0000-0000-0000-000000000000'`，可作为"未分配"标志被检测；输出严格符合 RFC 4122，可直接用于日志、HTTP 请求头、JSON 消息字段、数据库 `UNIQUEIDENTIFIER` 字段等场景，跨平台 GUID 互通无需再处理。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| 36 字符字符串 | 永远成功，无错误码 |

## 5. 使用注意 / 常见坑

- **目标变量至少 `STRING(36)`**：默认 `STRING(80)` 都够。
- **大写 hex**：标准 GUID 文本规范，无需修改。
- **空 GUID 检查**：可直接和 `'00000000-0000-0000-0000-000000000000'` 字面对比（也可用 `GuidsEqualByVal(g, gZeroConst)`）。
- **要写注册表 / WMI 用 `GUID_TO_REGSTRING`**：注册表期望带花括号。
- **与 ADS 通讯传递 GUID**：通常直接传 `GUID` 结构，不必转字符串再传（性能更好）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GUID_TO_STRING.xml`](../examples/P_Demo_GUID_TO_STRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GUID_TO_STRING
VAR
    gSessionId : GUID;
    sSessionId : STRING(36);
END_VAR

sSessionId := GUID_TO_STRING(stIn := gSessionId);
```

## 7. 业务场景与实际价值

- **场景**：每次产线启动生成一个 session GUID（追踪本次生产批次），写入诊断日志和 MES 报告字段。
- **价值**：标准 GUID 文本格式可直接被 MES / 数据库识别为 UNIQUEIDENTIFIER；不必自创格式。
- **替代方案对比**：
  - 自定义格式：MES 不识别，要写转换器
  - `GUID_TO_REGSTRING`：含花括号，数据库字段会嫌弃
  - 本函数：业界 RFC 4122 标准格式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.45 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35275147.html
- **相关函数 / 类型**：`GUID_TO_REGSTRING`（带花括号）、`STRING_TO_GUID`（反向）、`REGSTRING_TO_GUID`、`GuidsEqualByVal`、`GUID`（结构）
