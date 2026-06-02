# F_LTrim

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35126795.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_LTrim.TcPOU`](../examples/P_Demo_F_LTrim.TcPOU) |

---

## 1. 功能简述

对字符串做去除前导空格操作并返回新串。把 `in` 开头连续的 ASCII 空格字符（0x20）全部移除，返回截断后的子串。

内部按字节扫描 `in`（`T_MaxString` 即 `STRING(255)`）并按规则生成结果。结果同样是 `T_MaxString` 类型，PLC 周期内安全可重入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in  : T_MaxString;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_MaxString` | — | 待处理的字符串（最长 255 字节）。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 去除前导空格后的字符串。空串入空串出。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

从左到右扫描 `in`，跳过开头连续的空格字符（ASCII 0x20），从第一个非空格字符开始拷贝其余内容到返回串。中间空格、尾部空格**保留不变**。输入空串 `''` 返回 `''`；输入全是空格的字符串返回 `''`。

时间复杂度 O(N)；N 为字符串长度。注意只去 ASCII 空格 `0x20`，**不去** `Tab (0x09)` / 换行 `0x0A` / 回车 `0x0D`——如需更激进的清洗需自行 `REPLACE` 或多次调用其他函数。

## 4. 错误码 / 返回值

返回 `T_MaxString`，无错误码、无 `bError`、无 `HRESULT`。空输入返回空串；任意有效字符串输入恒返回非异常的字符串。

## 5. 使用注意 / 常见坑

- **只去 ASCII 空格 0x20**：Tab (0x09) / 换行 (0x0A) / 回车 (0x0D) 不被去除。需要完全清洗用 `REPLACE` 先替换或多函数链。
- **不影响中间 / 尾部空格**：`F_LTrim(' a b ')` 得 `'a b '`；若要全部 trim 用 `F_RTrim(F_LTrim(s))`。
- **结果是 T_MaxString**：赋给较短局部 `STRING(20)` 时多余部分按目标长度截断。
- **空串输入返回空串**：可放心串联调用而不必前置判空。
- **不修改入参**：本函数不是 `VAR_IN_OUT`；`in` 仍保持原值，必须用返回值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_LTrim.TcPOU`](../examples/P_Demo_F_LTrim.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_LTrim
VAR
    sRawInput  : T_MaxString := '   sensor_id_42  ';  // 模拟 HMI/串口收到的原始串
    sCleaned   : T_MaxString;                  // 处理后的结果
END_VAR

// 单行调用：把脏数据清洗成可比较的规范串
sCleaned := F_LTrim(sRawInput);

```

## 7. 业务场景与实际价值

- **场景**：从 HMI / 串口 / 文件 / Modbus ASCII 读到的字符串可能含前导；统一处理后再与查表 / 命令字 / 配方名比较，能避免「看起来一样实际不等」的 bug。
- **价值**：替代手写循环 + 状态变量；一行调用搞定单字符串处理，便于阅读和单测。
- **替代方案对比**：
  - 手写 `WHILE` 循环扫描：能做但 10 行左右、易越界
  - `DELETE` / `INSERT` 等 IEC 标准字符串函数组合：3-5 行，仍不够干净
  - **本函数**：一行、PDF 给出 4 组边界用例验证（含空串、纯空格）

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.38 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35126795.html
- **相关函数**：`F_LTrim` / `F_RTrim`（成对 trim）、`F_ToLCase` / `F_ToUCase`（大小写）、IEC `FIND` / `REPLACE` / `LEN` / `LEFT` / `RIGHT`
