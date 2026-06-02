# LREAL_TO_FMTSTR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35143691.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LREAL_TO_FMTSTR.TcPOU`](../examples/P_Demo_LREAL_TO_FMTSTR.TcPOU) |

---

## 1. 功能简述

把 LREAL 格式化为 `[-]dddd.dddd` 字符串，可控小数位数与四舍五入；特殊值显示为 `'#INF'` / `'-#INF'` / `'#QNAN'` / `'#OVF'`。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : LREAL;
    iPrecision : INT;
    bRound : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `LREAL` | — | 要格式化的浮点数。 |
| `iPrecision` | `INT` | — | 小数位数；0 = 不显示小数。 |
| `bRound` | `BOOL` | — | `TRUE` = 按精度四舍五入；`FALSE` = 截断。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(510)` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：按 `iPrecision` 指定的小数位数把 `in` 格式化为定点字符串：`iPrecision = 0` → 整数串（无小数点）；`iPrecision > 0` → `整数.iPrecision位小数`。`bRound = TRUE` 时**末位 ≥5 进位**；`= FALSE` 时直接截断。**特殊值处理**：正无穷返回 `'#INF'`、负无穷 `'-#INF'`、NaN 返回 `'#QNAN'` 或 `'-#QNAN'`、结果超过 STRING(510) 上限返回 `'#OVF'` 或 `'-#OVF'`。**LREAL 实际有效数字 ~15-16 位**——`iPrecision > 15` 时尾位是噪声。

## 4. 错误码 / 返回值

返回 `STRING(510)`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **`#INF` / `#QNAN` / `#OVF` 是字符串而不是数值**——业务侧用 `IF s[0] = '#' OR (s[0] = '-' AND s[1] = '#') THEN error END_IF;` 判错。
- **有效数字限 ~15-16 位**——超过 `iPrecision = 15` 末位是浮点误差噪声。
- **`bRound = FALSE`** 时直接截断（不向零截还是向负无穷截 ⚠️ PDF 未明确，建议默认 TRUE）。
- **`iPrecision = 0`** 时整数显示（无小数点）。
- **`iPrecision` 必须 ≤ 总长度限制**——`STRING(510)` 是上限。
- **反向 `FMTSTR_TO_LREAL` 不存在**——回灌请用 `STRING_TO_LREAL`（标准函数）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LREAL_TO_FMTSTR.TcPOU`](../examples/P_Demo_LREAL_TO_FMTSTR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 显示温度 / 压力等模拟量——按工程量精度（如 2 位小数）格式化为字符串。
- **价值**：替代手写整数取整 + 余数 + 拼接的繁琐代码；本函数 1 调用 + 自带 NaN/INF 处理。
- **替代方案对比**：`FB_FormatString` + `%f`：printf 风格；`REAL_TO_STRING`：基本但无精度控制。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.51 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35143691.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
