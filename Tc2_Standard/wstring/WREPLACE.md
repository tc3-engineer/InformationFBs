# WREPLACE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260777227.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WREPLACE.TcPOU`](../examples/P_Demo_WREPLACE.TcPOU) |

---

## 1. 功能简述

`WREPLACE` 是 **IEC 61131-3 标准字符串函数 `REPLACE` 的 WSTRING 版本**，把 WSTRING 字符串 `STR1` 中**从第 `P` 个字符起的 `L` 个字符**整段替换为 `STR2`。PDF §5.8 原话："Replace L characters from STR1 with STR2 beginning with the Pth character"。返回类型 `WSTRING(255)`。

与 `REPLACE` 的关键区别：所有位置和长度按 UCS-2 字符（2 字节单元）计数。**按位置 + 长度替换**，不是"按子串内容替换"。要把所有 `"旧"` 替换成 `"新"` 必须先 `WFIND` 定位再 `WREPLACE`，自身不做模式匹配。

工程上常用：把中文协议帧的某段固定字段（如版本字段）替换成新值、把中文日志等级从 "警告" 改成 "错误"、HMI 显示前对中文敏感字段做掩码。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WREPLACE : WSTRING(255)
VAR_INPUT
    STR1  :  WSTRING(255);
    STR2  :  WSTRING(255);
    L     :  INT;
    P     :  INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 主串 |
| `STR2` | `WSTRING(255)` | 用来替换的新内容 |
| `L` | `INT` | 要被替换掉的**字符数** |
| `P` | `INT` | 替换起点位置，**从 1 开始**计数 |

### 返回值

`WSTRING(255)`：替换后的新字符串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WREPLACE(STR1, STR2, L, P)` 是同步函数，单周期内立即返回。语义等同：先 `WDELETE(STR1, L, P)` 删掉指定段，再 `WINSERT` 把 `STR2` 插入到同一位置。具体步骤是：保留 `STR1` 中 `[1, P-1]` 字符区间作为结果前缀，跳过 `[P, P+L-1]` 这 `L` 个字符，整段拷入 `STR2`，再追加 `STR1` 中 `[P+L, end]` 区间，末尾补 `0x0000`。所有索引和长度都按 UCS-2 字符算。结果固定 `WSTRING(255)` 容器，超出 255 字符静默截断。

PDF §5.8 原例 ST 形式：`WREPLACE("SUXYSI", "K", 2, 2)` → 从第 2 字符起删 2 字符（`UX`）再插入 `K` → `"SKYSI"`。（PDF §5.8 IL 段的注释 `*Ergebnis ist "SKYSI"*` 与 ST 段一致，但 IL 段的写法 `WREPLACE "XY",2` 漏列 P 参数是 PDF 印刷不全；以 ST 写法为准。）

**关键语义**：

- **按位置 + 长度替换**，不是"按内容查找替换"；
- 替换段长度可与新内容不等（结果长度变化 `WLEN(STR2) - L`）；
- `L = 0` → 仅插入；`STR2 = ""` → 仅删除；
- 越界 ⚠️ 未规范；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回 `WSTRING(255)`。

## 5. 使用注意 / 常见坑

- **不是模式替换**：按位置工作。要替换所有出现必须配合 `WFIND` 写循环。
- **入参顺序**：`(STR1, STR2, L, P)`——主串、新内容、长度、位置。
- **`P` 从 1 开始**；
- **按字符不按字节**：替换 1 个汉字传 `L := 1`；
- **替换内容比原段长 → 可能超 255 字符截断**：先 `WLEN()` 校验；
- **WSTRING 字面量双引号**；
- **配合 `WFIND` 标准模式**：`s := WREPLACE(s, "新", WLEN("旧"), WFIND(s, "旧"));`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WREPLACE.TcPOU`](../examples/P_Demo_WREPLACE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：中文日志 "警告 电机异常" 升级为 "错误"，把前 2 字 "警告" 换成 "错误"
PROGRAM P_Demo_WREPLACE
VAR
    sLog       : WSTRING(255) := "警告 电机异常";
    sNewLevel  : WSTRING(255) := "错误";
    sResult    : WSTRING(255);
    nReplaceLen: INT := 2;
    nReplacePos: INT := 1;
    bUpgrade   : BOOL;
END_VAR

IF bUpgrade THEN
    sResult := WREPLACE(sLog, sNewLevel, nReplaceLen, nReplacePos);
    bUpgrade := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：中文日志等级升级（"警告" → "错误"）、协议固定字段替换为新值、HMI 显示前对中文敏感字段掩码（"密码"段替换为 "****"）。
- **价值**：UCS-2 安全。按字符替换不会拆出半个汉字。
- **替代方案对比**：
  - **`REPLACE` + UTF-8 STRING**：能存中文但按字节算位置长度
  - **`WDELETE + WINSERT` 两步**：完全等价但要写两行
  - **`Tc2_Utilities` 扩展**：有按内容查找替换的版本
  - **本 FC**：IEC 标准、Unicode 安全、签名直观

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260777227.html
- **相关 FC**：`REPLACE`（STRING 版本）、`WFIND`（先定位再替换）、`WDELETE`（仅删段）、`WINSERT`（仅插段）
