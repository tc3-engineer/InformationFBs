# OTSTRUCT_TO_TIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35146763.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_OTSTRUCT_TO_TIME.TcPOU`](../examples/P_Demo_OTSTRUCT_TO_TIME.TcPOU) |

---

## 1. 功能简述

把 `OTSTRUCT`（按毫秒 / 秒 / 分 / 时 / 日 / 周分解的结构体）合并回 `TIME` 数值。`OTSTRUCT` 字段：wMilliseconds、bySeconds、byMinutes、byHours、byDays、byWeeks。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION OTSTRUCT_TO_TIME : TIME
VAR_INPUT
    OTIN : OTSTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `OTIN` | `OTSTRUCT` | 按毫秒 / 秒 / 分 / 时 / 日 / 周分解的时间结构体 |

### 返回值

`TIME` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

`OTSTRUCT` 用于把 `TIME`（毫秒数）按周 / 天 / 时 / 分 / 秒 / 毫秒分量展开方便人读 / HMI 显示；本 FC 是反向操作，把这些分量按 7×24×60×60×1000 / 24×60×60×1000 / 60×60×1000 / 60×1000 / 1000 / 1 加权求和回毫秒，赋给 `TIME`。

与 `TIME_TO_OTSTRUCT` 互逆。

`TIME` 类型本质是 `DWORD` 表示的毫秒数（最大约 49 天）。如果 `OTSTRUCT` 各字段之和超过 49 天，结果会溢出。无错误码。

## 4. 错误码 / 返回值

返回类型 `TIME`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **`TIME` 上限约 49.7 天**：`OTSTRUCT.byWeeks > 7` 就可能溢出。
- **字段类型不一致**：`wMilliseconds` 是 `WORD`、`bySeconds`...`byWeeks` 是 `BYTE`；编辑结构体时不要超过 `BYTE` 上限 255。
- **无错误码**：超界输入直接得到错误的 `TIME` 值。
- **典型用法：HMI 编辑时间值**：HMI 上让操作员分别填 hours / minutes / seconds，再用本 FC 拼装成 PLC 用的 `TIME` 类型。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_OTSTRUCT_TO_TIME.TcPOU`](../examples/P_Demo_OTSTRUCT_TO_TIME.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
tDelay := OTSTRUCT_TO_TIME(otStruct);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：HMI 上「设置烘干时间」让操作员分别拨「2 小时 30 分 0 秒」三个轮子，PLC 程序需要把这三个字段汇总成单一 `TIME` 喂给定时器 FB。
- **价值**：1 行调用完成多字段汇总，避免手写 `BYTE_TO_TIME(byHours) * 3600000 + ...` 6 项相乘相加。
- **替代方案对比**：手写 6 项乘加（容易写错权重）/ 用 6 个 INT 然后 `INT_TO_TIME`（更啰嗦）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.16
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35146763.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
