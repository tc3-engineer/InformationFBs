# FB_EnumStringNumbers

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34988171.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnumStringNumbers.xml`](../examples/P_Demo_FB_EnumStringNumbers.xml) |

---

## 1. 功能简述

FB_EnumStringNumbers 枚举一段字符串里所有可解析为数字的子串。用于解析自由格式输入（操作员输入 `'5, 10, 15'` 取出 5 / 10 / 15）。

也用于解析 HMI 上传的多值字段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSearch : T_MaxString;
    eCmd : E_EnumCmdType := eEnumCmd_First;
    eType : E_NumGroupTypes := eNumGroup_Float;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSearch` | `T_MaxString` | - | 参数 `sSearch`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `eCmd` | `E_EnumCmdType` | `eEnumCmd_First` | 参数 `eCmd`（类型 `E_EnumCmdType`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `eType` | `E_NumGroupTypes` | `eNumGroup_Float` | 参数 `eType`（类型 `E_NumGroupTypes`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    sNumber : T_MaxString;
    nPos : INT;
    bEOS : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNumber` | `T_MaxString` | 参数 `sNumber`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nPos` | `INT` | 有符号整数输出：`nPos`。 |
| `bEOS` | `BOOL` | 输出布尔标志：`bEOS`。具体语义见 §3 行为说明。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿启动 / 取下一个。每次返回一个数字。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **仅整数 / 浮点字面量**——表达式（`5+3`）不会展开。
- 分隔符宽松（空白 / `,` / `;`）；具体规则参考 PDF / InfoSys。（工程经验补充）
- 超长数字会被截断为输出类型上限（典型 LREAL）。（工程经验补充）
- PDF 未列错误码。
- 空输入返回 0 条，业务侧应预检不要把 0 当作错。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnumStringNumbers.xml`](../examples/P_Demo_FB_EnumStringNumbers.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：操作员输入 `5, 10, 15` 取出多个数。
- **价值**：替代自写字符串分割 + 转数字。
- **替代方案对比**：
  - 自写 split：边界条件多。
  - **本 FB**：库提供。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34988171.html
