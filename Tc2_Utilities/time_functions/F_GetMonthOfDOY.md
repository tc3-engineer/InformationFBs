# F_GetMonthOfDOY

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35120651.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetMonthOfDOY.TcPOU`](../examples/P_Demo_F_GetMonthOfDOY.TcPOU) |

---

## 1. 功能简述

把「年内第几天」反查到月份。例如：2009 年第 60 天 → 3 月。返回 0 = 参数错误，1 ~ 12 = 月份。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION F_GetMonthOfDOY : WORD
VAR_INPUT
    wYear : WORD;
    wDOY : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `wYear` | `WORD` | 年份（0 ~ 2999） |
| `wDOY` | `WORD` | 年内第几天（1 ~ 366） |

### 返回值

`WORD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按累加各月天数 + 闰年判定做反向定位。返回的是该 DOY 所在的月份号（1 = January ... 12 = December）。

闰年判定与 `F_YearIsLeapYear` / `F_GetDOYOfYearMonthDay` 一致。普通年 DOY 范围 1 ~ 365，闰年 1 ~ 366；超出范围返回 0。

与 `F_GetDOYOfYearMonthDay` 互逆——前者(年, 月, 日) → DOY，本 FC (年, DOY) → 月份。


注意：与 `F_GetDOYOfYearMonthDay` 配合可实现紧凑日期压缩——存档时把(年, 月, 日)折叠成(年, DOY)节省 1 字段；读取时再展开。气象 / 农业 / 太阳能模型领域 DOY 是国际通用的天序号，本 FC 是从存档反查回月份的标准入口。

## 4. 错误码 / 返回值

返回类型 `WORD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **只返回月，不返回该月第几天**：若需(月, 日)需配合 `F_GetMonthOfDOY` + 自己计算 day = DOY - sum(前面月天数)。
- **返回 0 表示参数错**：DOY = 0 或闰年 DOY > 366 / 平年 DOY > 365 都返回 0。
- **与 `F_GetDOYOfYearMonthDay` 配套使用**：DOY 是紧凑表示，存档省空间；查询时反查回月份显示。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetMonthOfDOY.TcPOU`](../examples/P_Demo_F_GetMonthOfDOY.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
wMonth := F_GetMonthOfDOY(2009, 60);   // 期望 3（3 月 1 日）
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：气象 / 农业领域常用 DOY 表示日期（如太阳辐射模型），从数据库读出 DOY 后用本 FC 转月份做月度统计或可视化。
- **价值**：1 行反查避免手写 12 个月累计减法 + 闰年判定。
- **替代方案对比**：手写累计减法（容易写错闰年）/ 用 `DT_TO_SYSTEMTIME` 反推（需先把 DOY 转 DT，多步）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35120651.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
