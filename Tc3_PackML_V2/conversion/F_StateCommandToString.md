# F_StateCommandToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302052235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_StateCommandToString.TcPOU`](../examples/P_Demo_F_StateCommandToString.TcPOU) |

---

## 1. 功能简述

`F_StateCommandToString` 把 PackML 状态命令枚举 `E_PMLCommand` 转换为可读字符串名称。返回 STRING——如把 `ePMLCommand_Start` 转成 `'Start'`、把 `ePMLCommand_Abort` 转成 `'Abort'`、把 `ePMLCommand_Undefined` 转成 `'Undefined'`。

主要用于 HMI 显示和事件日志——枚举存数据库时一般存数值，但显示给操作员和写日志时需要可读字符串。本函数提供枚举到字符串的标准映射。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION F_StateCommandToString : STRING;
```

### VAR_INPUT

```iecst
VAR_INPUT
    eStateCommand         : E_PMLCommand;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eStateCommand` | `E_PMLCommand` | 要转换的状态命令枚举值（0=Undefined / 1=Reset / 2=Start / 3=Stop / 4=Hold / 5=Unhold / 6=Suspend / 7=Unsuspend / 8=Abort / 9=Clear）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`F_StateCommandToString` 是一个纯查表函数——根据输入枚举值返回对应的字符串名（去掉枚举前缀 `ePMLCommand_`，只留语义部分）。

**映射规则**（按 PackML V3 命令枚举）：

| 输入枚举 | 数值 | 返回字符串 |
|---|---|---|
| `ePMLCommand_Undefined` | 0 | `'Undefined'` |
| `ePMLCommand_Reset` | 1 | `'Reset'` |
| `ePMLCommand_Start` | 2 | `'Start'` |
| `ePMLCommand_Stop` | 3 | `'Stop'` |
| `ePMLCommand_Hold` | 4 | `'Hold'` |
| `ePMLCommand_Unhold` | 5 | `'Unhold'` |
| `ePMLCommand_Suspend` | 6 | `'Suspend'` |
| `ePMLCommand_Unsuspend` | 7 | `'Unsuspend'` |
| `ePMLCommand_Abort` | 8 | `'Abort'` |
| `ePMLCommand_Clear` | 9 | `'Clear'` |

⚠️ 具体字符串字面值（是否带前缀、是否全大写）PDF + InfoSys 未列原文样本，⚠️ 建议在 PLC 运行时实测一下确认。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用例**：HMI 报警日志记录"操作员在 14:30 发出 Start 命令"——`sCommandName := F_StateCommandToString(eCommand);`，再把 `sCommandName` 写入文本日志。

## 4. 错误码 / 返回值

返回 `STRING`：对应枚举值的字符串名。输入越界（如手动赋了 99）时返回值 PDF + InfoSys 未列，⚠️ 建议测试（可能返回空字符串或 'Undefined'）。

## 5. 使用注意 / 常见坑

- 默认 `STRING` 类型 80 字符长度，本函数返回的字符串都很短不会溢出。
- 与 `F_UnitModeToString` 互补——前者转命令枚举、后者转模式编号。
- 用于 HMI 显示和文本日志；数据库存数值更紧凑、显示用本函数转换。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_StateCommandToString.TcPOU`](../examples/P_Demo_F_StateCommandToString.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 报警日志要记录"操作员 14:30 发了 Start 命令"——直接显示数字 2 操作员看不懂，需要可读字符串。调本函数转换。同样用于把 PackTags 里的 CntrlCmd 数值译成文本写入历史归档。
- **价值**：枚举↔字符串的标准映射封装，应用层不必维护自己的查表，避免不同模块字符串拼写不一致（"Start" vs "start" vs "STARTING"）。
- **替代方案对比**：手写 CASE 语句——代码量大、易遗漏新加的枚举值；本函数是 Beckhoff 官方提供，跟着库版本更新自动同步。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302052235.html
- **相关**：`F_UnitModeToString`（模式编号转字符串）、`E_PMLCommand`（命令枚举）

## 9. 待确认项 (⚠️)

- 字符串具体字面值（如是否含前缀 'ePMLCommand_'）PDF + InfoSys 均未列样本，建议运行测试确认。
- 输入越界（非枚举有效值）时的返回 PDF + InfoSys 未列。
