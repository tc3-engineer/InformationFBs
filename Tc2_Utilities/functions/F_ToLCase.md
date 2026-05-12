# F_ToLCase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35131403.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ToLCase.xml`](../examples/P_Demo_F_ToLCase.xml) |

---

## 1. 功能简述

对字符串做全字符转小写操作并返回新串。把字符串中的大写字母转为小写。默认按 Windows code page 1252 (Latin-1)，可通过 `GLOBAL_SBCS_TABLE` 切到 CP1250（中欧）。

内部按字节扫描 `in`（`T_MaxString` 即 `STRING(255)`）并按规则生成结果。结果同样是 `T_MaxString` 类型，PLC 周期内安全可重入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : T_MaxString;
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
| `T_MaxString` | 全字符转小写后的字符串。空串入空串出。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

逐字符扫描 `in`，把其中的大写字母按当前字符集表转为对应小写字母，其他字符（数字、标点、空格、控制字符）原样保留。默认使用 **Windows code page 1252 Latin-1 (SBCS)** 字符集表，能处理英文字母 A-Z 与常用西欧扩展字符（Ä → ä、Ö → ö、Ü → ü 等）。

通过修改全局变量 `GLOBAL_SBCS_TABLE := eSBCS_CentralEuropean` 可切到 Windows code page 1250 中欧字符集，能正确处理波兰语 / 捷克语 / 匈牙利语字符（Ą → ą、Ę → ę、Ś → ś、Ć → ć、Ż → ż、Ź → ź、Ł → ł、Ó → ó 等）。

特殊字符：`ß` 在 CP1252 中已是小写形，保留不变。本函数**逐字节**扫描，对多字节字符集（UTF-8 / 中文 GBK）不支持，结果会乱码；中文场景必须改用 `WSTRING` + Tc3 字符串库。

## 4. 错误码 / 返回值

返回 `T_MaxString`，无错误码、无 `bError`、无 `HRESULT`。空输入返回空串；任意有效字符串输入恒返回非异常的字符串。

## 5. 使用注意 / 常见坑

- **依赖 GLOBAL_SBCS_TABLE 全局**：默认 CP1252；处理波兰语 / 捷克语等中欧文字前必须先 `GLOBAL_SBCS_TABLE := eSBCS_CentralEuropean`。
- **不支持 UTF-8**：多字节字符（如中文）按单字节大小写处理，结果乱码。中文字符串请走 `WSTRING` + Tc3 字符串库。
- **ß 字符**：CP1252 没有大写 ß，PDF 示例保留 ß 不变。
- **结果是 T_MaxString 不是 STRING**：赋给短局部变量按目标长度截断。
- **不修改入参**：必须接返回值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ToLCase.xml`](../examples/P_Demo_F_ToLCase.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_ToLCase
VAR
    sRawInput  : T_MaxString := 'WP_ALFA_2026';  // 模拟 HMI/串口收到的原始串
    sCleaned   : T_MaxString;                  // 处理后的结果
END_VAR

// 单行调用：把脏数据清洗成可比较的规范串
sCleaned := F_ToLCase(sRawInput);

```

## 7. 业务场景与实际价值

- **场景**：从 HMI / 串口 / 文件 / Modbus ASCII 读到的字符串可能含大小写不一致；统一处理后再与查表 / 命令字 / 配方名比较，能避免「看起来一样实际不等」的 bug。
- **价值**：替代手写循环 + 状态变量；一行调用搞定单字符串处理，便于阅读和单测。
- **替代方案对比**：
  - 手写 `WHILE` 循环扫描：能做但 10 行左右、易越界
  - `DELETE` / `INSERT` 等 IEC 标准字符串函数组合：3-5 行，仍不够干净
  - **本函数**：一行、PDF 给出 4 组边界用例验证（含空串、纯空格）

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.42 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35131403.html
- **相关函数**：`F_LTrim` / `F_RTrim`（成对 trim）、`F_ToLCase` / `F_ToUCase`（大小写）、IEC `FIND` / `REPLACE` / `LEN` / `LEFT` / `RIGHT`
