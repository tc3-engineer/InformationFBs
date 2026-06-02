# TIME_TO_OTSTRUCT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35159051.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TIME_TO_OTSTRUCT.TcPOU`](../examples/P_Demo_TIME_TO_OTSTRUCT.TcPOU) |

---

## 1. 功能简述

把 `TIME`（毫秒数，最大约 49 天）按毫秒 / 秒 / 分 / 时 / 日 / 周分解为 `OTSTRUCT` 结构体。与 `OTSTRUCT_TO_TIME` 互逆。常用于 HMI 显示「运行时长 = X 周 X 天 X 时 X 分 X 秒 X 毫秒」。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION TIME_TO_OTSTRUCT : OTSTRUCT
VAR_INPUT
    TIN : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TIN` | `TIME` | 待分解的 TIME 数值 |

### 返回值

`OTSTRUCT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数对输入 `TIME`（毫秒数，最大约 49 天 = 4294967295ms）做整除取余分解：

1. 周数 = 总毫秒 / (7 × 86400000)
2. 余下 → 天数 = 余数 / 86400000
3. 余下 → 小时 = 余数 / 3600000
4. 余下 → 分钟 = 余数 / 60000
5. 余下 → 秒 = 余数 / 1000
6. 余下 → 毫秒

填入 `OTSTRUCT.byWeeks / byDays / byHours / byMinutes / bySeconds / wMilliseconds` 各字段。

注意：`TIME` 上限约 49.7 天 = 7 周左右，所以 `byWeeks` 实际最大值约 7，不会到月 / 年级别。

## 4. 错误码 / 返回值

返回类型 `OTSTRUCT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **`TIME` 上限约 49.7 天**：超出此值在 `TIME` 类型上根本无法表达，所以 `OTSTRUCT.byWeeks` 永远 ≤ 7。
- **字段类型混合**：wMilliseconds 是 `WORD`、byWeeks 等是 `BYTE`；自己构造 `OTSTRUCT` 喂给 `OTSTRUCT_TO_TIME` 时要注意类型范围。
- **典型用法：HMI 显示运行时长**：维护周期统计、生产计时器拆开为「X 天 X 小时」显示比「Y 小时」更直观。
- **与 `TIME_TO_STRING` 区别**：后者返回 「T#1d2h3m4s5ms」字符串，本 FC 返回结构体便于程序逐字段访问 / HMI 分别绑定不同输入框。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TIME_TO_OTSTRUCT.TcPOU`](../examples/P_Demo_TIME_TO_OTSTRUCT.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
otStruct := TIME_TO_OTSTRUCT(T#1d2h3m4s5ms);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：HMI 上显示「设备已连续运行 X 周 Y 天 Z 时」；或者把维修周期按多分量展开供操作员调节。
- **价值**：1 行调用完成 5 次整除取余拆分，避免手写 6 行除法 + 余数赋值。
- **替代方案对比**：用 `TIME_TO_STRING` + 字符串解析（迂回）/ 手写整除取余链（容易写错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.23
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35159051.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
