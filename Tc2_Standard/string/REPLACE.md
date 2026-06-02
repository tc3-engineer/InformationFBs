# REPLACE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74421771.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_REPLACE.TcPOU`](../examples/P_Demo_REPLACE.TcPOU) |

---

## 1. 功能简述

`REPLACE` 是 **IEC 61131-3 标准字符串函数**，把 `STR1` 中**从第 `P` 个字符起的 `L` 个字符**整段替换为 `STR2`。PDF §4.8 原话："Replace L characters from STR1 with STR2 beginning with the character in the P position"。返回类型 `STRING(255)`。

注意：本函数**按位置 + 长度替换**，不是"按子串内容替换"。要把所有 `'old'` 替换成 `'new'` 需要先 `FIND` 定位再 `REPLACE`，**REPLACE 自身不做模式匹配**。这一点与许多高级语言的 `replace()` 行为不同，是工程上最大的混淆点。

它在工程中常用于：把协议帧的某段固定字段（如校验位、版本字段）替换成新值；把日志行的等级字段从 `WARN_` 改成 `ERROR`；HMI 显示前对掩码段做替换。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION REPLACE : STRING(255)
VAR_INPUT
    STR1 : STRING(255);
    STR2 : STRING(255);
    L    : INT;
    P    : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 主串（被替换段所在的源串） |
| `STR2` | `STRING(255)` | 用来替换的新内容 |
| `L` | `INT` | 要被替换掉的字符数（从 `P` 开始向后数 `L` 个字符删掉，再插入 `STR2`） |
| `P` | `INT` | 替换起点位置，**从 1 开始**计数 |

### 返回值

`STRING(255)`：替换后的新字符串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`REPLACE(STR1, STR2, L, P)` 是同步函数，单周期内返回。语义等同：先 `DELETE(STR1, L, P)` 删掉指定段，再 `INSERT` 把 `STR2` 插入到同一位置。具体步骤是：保留 `STR1` 中 `[1, P-1]` 区间的字符作为结果前缀，跳过 `[P, P+L-1]` 这 `L` 个字符（被替换掉），整段拷入 `STR2`，再追加 `STR1` 中 `[P+L, end]` 区间的剩余字符，末尾补 `0x00`。整体结果固定 `STRING(255)` 容器，超出 255 字节静默截断。

PDF §4.8 原例：`REPLACE('SUXYSI', 'K', 2, 2)` → 从第 2 字符起删 2 字符（`UX`）再插入 `K` → `'SKYSI'`。

**关键语义**：

- **按位置 + 长度替换**，不是"按内容查找替换"；
- **替换段长度可与替换内容不等**：`L` 个字符被替换成 `LEN(STR2)` 个字符，结果长度变化 `LEN(STR2) - L`；
- **`L = 0`**：等价于 `INSERT(STR1, STR2, P-1)`，仅插入不删除；
- **`STR2 = ''`**：等价于 `DELETE(STR1, L, P)`，仅删除不插入；
- **越界**：⚠️ PDF + InfoSys 未明确，禁止依赖；
- **不修改入参**。

## 4. 错误码 / 返回值

无错误码。返回值始终 `STRING(255)`。无法判断越界——调用方保证 `P >= 1`、`L >= 0`、`P + L - 1 <= LEN(STR1)`。

## 5. 使用注意 / 常见坑

- **不是字符串模式替换**：`REPLACE` 按位置工作，不是"找到所有 'old' 替换成 'new'"。要做模式替换必须先 `FIND` 再 `REPLACE`。
- **入参顺序**：`(STR1, STR2, L, P)`——主串、替换内容、长度、位置。L 在 P 前，与 `MID`、`DELETE` 一致但与 C/Python 习惯不同。
- **`P` 从 1 开始**：第 1 字符 `P = 1`，不是 0。
- **想替换全部出现**：自己写循环：`WHILE FIND(s, old) > 0 DO s := REPLACE(s, new, LEN(old), FIND(s, old)); END_WHILE;`。
- **替换内容比原段长 → 可能超 255 字节截断**：例如把 `'a'` 替换成 200 字符串，多次后会触发截断。先 `LEN()` 校验。
- **UTF-8 中文按字节算**：替换中文需按字节算 `L`，否则会拆出半个汉字。Unicode 用 `WREPLACE`。
- **配合 `FIND` 标准模式**：`REPLACE(s, 'new', LEN('old'), FIND(s, 'old'))` 替换第一次出现的 `old`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_REPLACE.TcPOU`](../examples/P_Demo_REPLACE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：日志行 'WARN_ Motor stalled' 升级为 ERROR 时，把前 5 字符 'WARN_' 替换成 'ERROR'
PROGRAM P_Demo_REPLACE
VAR
    sLog       : STRING(255) := 'WARN_ Motor stalled';
    sNewLevel  : STRING(255) := 'ERROR';
    sResult    : STRING(255);
    nReplaceLen: INT := 5;            // 'WARN_' 5 字符
    nReplacePos: INT := 1;            // 从第 1 字符开始
    bRun       : BOOL;
END_VAR

IF bRun THEN
    sResult := REPLACE(sLog, sNewLevel, nReplaceLen, nReplacePos);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：协议帧固定字段（校验段 / 版本段 / 长度段）替换为新值、日志等级升级（WARN → ERROR）、HMI 显示前掩码替换敏感字段（如密码改为 `****`）、配置串中替换默认值。
- **价值**：一次调用完成"删一段 + 插一段"两步合一，比手写 `DELETE` + `INSERT` 简洁。
- **替代方案对比**：
  - **`DELETE` + `INSERT` 两次调用**：完全等价但要写两行
  - **`LEFT` + `CONCAT` + `RIGHT` 三次调用**：能等价但 4 步
  - **`Tc2_Utilities.ReplaceAll`**：扩展版，做"全部出现替换为"的模式匹配版本
  - **本 FC**：IEC 标准、签名直观（位置+长度+新内容），按位置替换首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74421771.html
- **相关 FC**：`FIND`（先定位再替换）、`DELETE`（仅删段）、`INSERT`（仅插段）、`WREPLACE`（WSTRING 版本）
