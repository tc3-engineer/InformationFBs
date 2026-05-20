# GUID_TO_REGSTRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934082955.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_GUID_TO_REGSTRING.xml`](../examples/P_Demo_GUID_TO_REGSTRING.xml) |

---

## 1. 功能简述

把结构化的 `GUID`（128 位）变量转成带花括号的注册表风格字符串（如 `'{12345678-1234-1234-1234-123456789ABC}'`），长度固定 38 字符（含两个花括号 + 32 hex 字符 + 4 个连字符）。

这是 Windows 注册表 / COM 框架对 GUID 的规范字面表示；当 PLC 端要把 GUID 写到注册表项、日志、HMI 显示或匹配 Windows 端记录的 GUID 字符串时用本函数。无花括号的版本是 `GUID_TO_STRING`，反向是 `REGSTRING_TO_GUID`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : GUID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `GUID` | — | 待转换的 GUID 结构（128 位，含 `Data1` `Data2` `Data3` `Data4` 字段）。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(38)` | 带花括号的 GUID 字符串。全零 GUID 返回 `'{00000000-0000-0000-0000-000000000000}'`。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数按 RFC 4122 文本格式把 GUID 输出为带花括号的字符串 `'{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}'`，各段对应 `in.Data1`（4 字节）、`in.Data2`（2 字节）、`in.Data3`（2 字节）、`in.Data4[0..7]`（8 字节）的十六进制大写表示，长度固定 38 字符（含两个花括号、32 个 hex 字符、4 个连字符）。

实现属性：函数永远成功（PDF 不列错误码），任意 `GUID` 输入都能转；hex 字母按注册表习惯输出大写（需要小写时调用方自行用 `F_ToLCase` 转换）。全零 GUID 输出 `'{00000000-0000-0000-0000-000000000000}'`，调用方可据此判断 GUID 是否已被赋值。`Data1` / `Data2` / `Data3` 按主机字节序的"逻辑数值"输出，不是按内存字节直接列，因此 PLC 端与 Windows 端字符串完全一致，可直接互通。

与 `GUID_TO_STRING` 唯一区别：本函数加花括号；其他完全相同。注册表 / Group Policy / ProgID 场合用本函数；纯日志展示用 `GUID_TO_STRING` 即可。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `'{...}'` | 38 字符的注册表 GUID 字符串（永远成功） |

## 5. 使用注意 / 常见坑

- **结果固定 38 字符**：包含花括号；存到 `STRING(36)` 会截断（少了花括号），建议存 `STRING(38)` 或更大。
- **大写 hex**：要小写自己 `F_ToLCase`。
- **`'{00000000-...}'` 表示空 GUID**：业务侧用此模式判"已初始化"。
- **与 Windows 注册表对齐**：写 RegEdit / WMI 时用此格式；纯日志用 `GUID_TO_STRING` 省 2 个字符。
- **不要用 `CONCAT('{', GUID_TO_STRING(g), '}')` 替代**：性能更差且没节省什么（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GUID_TO_REGSTRING.xml`](../examples/P_Demo_GUID_TO_REGSTRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GUID_TO_REGSTRING
VAR
    gMachineId : GUID;                 // 128 位机器唯一 ID
    sRegString : STRING(38);           // 注册表风格输出
END_VAR

sRegString := GUID_TO_REGSTRING(in := gMachineId);
// 若 gMachineId 未赋值，sRegString = '{00000000-0000-0000-0000-000000000000}'
```

## 7. 业务场景与实际价值

- **场景**：工业 PC 启动时从 BIOS / dongle 读取机器唯一 ID（GUID），写到 Windows 注册表项 `HKLM\SOFTWARE\Plant\MachineId` 供其他服务读取；注册表存的就是带花括号的字符串。
- **价值**：单调用直接得到规范格式串；不用先做 `GUID_TO_STRING` 再 `CONCAT` 花括号。
- **替代方案对比**：
  - `CONCAT('{', GUID_TO_STRING(g), '}')`：可行但绕
  - 手写按 `GUID` 字段拼字符串：30+ 行十六进制格式化
  - 本函数：一行得到 RegEdit 兼容格式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.44 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934082955.html
- **相关函数 / 类型**：`GUID_TO_STRING`（无花括号版）、`REGSTRING_TO_GUID`（反向解析）、`STRING_TO_GUID`、`GuidsEqualByVal`、`GUID`（128 位结构）
