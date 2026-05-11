# CONCAT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74411019.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_CONCAT.xml`](../examples/P_Demo_CONCAT.xml) |

---

## 1. 功能简述

`CONCAT` 是 **IEC 61131-3 标准字符串函数**之一，实现**两个 STRING 的首尾拼接**：返回 `STR1` 的全部字符后紧接 `STR2` 的全部字符所组成的新字符串。两个入参与返回值均为 `STRING(255)`。

它是 Tc2_Standard 库 `String functions` 章节最基础的工具：拼接报警文本、组装文件路径、生成日志前缀等场景几乎都会先调一次 `CONCAT`。和 IEC 扩展的 `+` 操作符（`s1 + s2`）等价，但显式调用更利于代码评审和搜索。

工程中需要嵌套拼接 3 个以上字符串时，可以连续套用 `CONCAT(CONCAT(a, b), c)`，但每一层都会复制 255 字节，性能敏感场合更应该用 `MEMCPY` 或 `Tc2_Utilities` 的扩展字符串函数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION CONCAT : STRING(255)
VAR_INPUT
     STR1 : STRING(255);
     STR2 : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 拼接结果的**前段**字符串。`CONCAT('Mr.','Smith')` → `STR1='Mr.'` 出现在结果开头 |
| `STR2` | `STRING(255)` | 拼接结果的**后段**字符串。会按字面追加到 `STR1` 末尾，不插入任何分隔符 |

### 返回值

`STRING(255)`：`STR1` 与 `STR2` 顺序拼接后的新字符串。返回缓冲固定为 255 字节，超过该长度的尾部字符被截断。

### VAR_OUTPUT / VAR_IN_OUT

无。`CONCAT` 是 FUNCTION，没有 FB 实例数据，每次调用相互独立。

## 3. 行为说明

`CONCAT(STR1, STR2)` 在一个 PLC 周期内同步完成：

1. 把 `STR1` 的有效字符（直到第一个 `0x00` 结束符之前）逐字节复制进返回缓冲；
2. 紧跟着把 `STR2` 的有效字符逐字节追加进去，**不插入空格、换行或任何分隔符**；
3. 在拼接后的字符末尾补 `0x00` 结束符；
4. 若 `STR1` 长度 + `STR2` 长度 > 255，则结果在第 255 字节处被截断（IEC 行为，**不抛错也不告警**）。

举例：`CONCAT('SUSI', 'WILLI')` → `'SUSIWILLI'`（PDF §4.1 原例）。

**关键语义**：

- 同步 FC：每次调用立即返回结果，**无 `bBusy` / `bDone` 状态**；
- **截断不告警**：超 255 字节的尾部丢失只能由调用方先用 `LEN()` 校验，FB 自己不会报错；
- **空串合法**：`CONCAT('','abc')` → `'abc'`，`CONCAT('abc','')` → `'abc'`；
- **不修改入参**：`STR1` / `STR2` 是值传入，函数返回新字符串，原变量保持不变。

InfoSys topic 74411019 与 PDF §4.1 文本一致，仅举例无额外行为补充。

## 4. 错误码 / 返回值

`CONCAT` 不返回错误码。**返回值就是拼接后的 STRING(255)**，没有失败语义：

- 入参为空串 → 返回另一侧的内容（可能为空串）；
- 入参合计长度 > 255 → 返回**前 255 字节**，调用方无法从返回值判断是否发生过截断；
- 入参未初始化（声明后未赋值） → 视为空串处理（STRING 类型默认初值为 `''`）。

工程上若需要识别"是否被截断"，必须自己写 `IF LEN(STR1) + LEN(STR2) > 255 THEN ...`。

## 5. 使用注意 / 常见坑

- **STRING(255) 是上限不是固定长度**：返回值容器是 255 字节，但若调用方接收变量是 `STRING(80)`，赋值会再截断一次到 80 字节。一律用 `STRING(255)` 或更大的容器接收，避免双重截断。（工程经验补充）
- **拼接超长 → 静默截断**：超 255 字节没有任何错误提示，调试时最容易踩。性能允许时调用前手动 `IF LEN(STR1)+LEN(STR2)>255 THEN`。（工程经验补充）
- **多次嵌套性能不佳**：`CONCAT(CONCAT(CONCAT(a,b),c),d)` 实际复制了 a+a+a+a 字节。3 段以上推荐用 `Tc2_Utilities.CONCAT2` / `CONCAT3` 等扩展，或先 `MEMCPY` 再补 `0x00`。
- **不要传 WSTRING**：本函数只处理 `STRING`（单字节 ANSI）。Unicode 文本必须用 `WCONCAT`，否则编译失败或得到乱码。
- **运行时分隔符**：常见需求"用 `,` 把字段拼起来"——本函数不带分隔符，必须自己写 `CONCAT(CONCAT(s1,','),s2)`。
- **`+` 操作符等价**：`s1 + s2 + s3` 在 TwinCAT 中和 `CONCAT(CONCAT(s1,s2),s3)` 完全等价。看个人风格选择，但 `+` 行更短、`CONCAT` 更利于代码 grep。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CONCAT.xml`](../examples/P_Demo_CONCAT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：报警系统组装报警文本——前缀（报警等级）+ 详细原因，输出到 HMI
PROGRAM P_Demo_CONCAT
VAR
    sAlarmPrefix : STRING(255) := 'ALARM: ';   // 固定前缀
    sAlarmReason : STRING(255) := 'Motor 1 overcurrent';
    sAlarmText   : STRING(255);                // 拼接后的完整报警文本
    bGenerate    : BOOL;                        // 触发一次拼接
END_VAR

IF bGenerate THEN
    sAlarmText := CONCAT(sAlarmPrefix, sAlarmReason);
    bGenerate := FALSE;   // 单次触发，自动复位
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：组装报警文本（前缀+原因）、生成日志文件名（日期+模块名+后缀）、把设备 ID 与状态码拼接成 HMI 状态栏文字、把 IP 段和最后一节拼成完整 IP 串。
- **价值**：一行代码完成首尾拼接，不必自己写循环逐字节复制，也不必关心 `0x00` 结束符位置。配合 `+` 操作符可以做到 `s := 'TAG[' + nIdx + ']:' + sValue;` 这种类 C 写法。
- **替代方案对比**：
  - **`+` 操作符**：完全等价，更短，适合临时拼接
  - **`Tc2_Utilities.CONCAT2 / CONCAT3 / CONCAT4`**：一次拼接 3-4 段，省去嵌套
  - **`SPRINTF` / 格式化函数**：需要数字格式化（前导零、小数位数）时用这个，纯字符串拼接用 `CONCAT` 更轻量
  - **本 FC**：IEC 标准、零依赖、所有 PLC 平台兼容，**默认首选**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74411019.html
- **相关 FC**：`INSERT`（在指定位置插入子串）、`REPLACE`（替换子串）、`WCONCAT`（WSTRING 版本）、`LEN`（先查长度避免截断）
