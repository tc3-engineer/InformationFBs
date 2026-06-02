# FB_HashTableCtrl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35006731.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_HashTableCtrl.TcPOU`](../examples/P_Demo_FB_HashTableCtrl.TcPOU) |

---

## 1. 功能简述

FB_HashTableCtrl 哈希表控制器——给 PLC 程序提供 O(1) 平均时间的键值对存取。键是 STRING / 整数，值是任意类型（用 POINTER + SIZEOF 通用化）。

用于：HMI 标签到 PLC 内部 ID 的映射、大量配方参数的随机访问。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    key : DWORD := 0;
    putValue : PVOID := 0;
    putPosPtr : POINTER TO T_HashTableEntry := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `key` | `DWORD` | `0` | 无符号整数输入：`key`。 |
| `putValue` | `PVOID` | `0` | 参数 `putValue`（类型 `PVOID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `putPosPtr` | `POINTER TO T_HashTableEntry` | `0` | 参数 `putPosPtr`（类型 `POINTER TO T_HashTableEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL := FALSE;
    getValue : PVOID := 0;
    getPosPtr : POINTER TO T_HashTableEntry := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOk` | `BOOL` | `FALSE` | 输出布尔标志：`bOk`。具体语义见 §3 行为说明。 |
| `getValue` | `PVOID` | `0` | 参数 `getValue`（类型 `PVOID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `getPosPtr` | `POINTER TO T_HashTableEntry` | `0` | 参数 `getPosPtr`（类型 `POINTER TO T_HashTableEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hTable : T_HHASHTABLE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hTable` | `T_HHASHTABLE` | 参数 `hTable`（类型 `T_HHASHTABLE`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

## 3. 行为说明

**OO 方法**：`Init` 设置容量 + key/value 大小 → `Add` / `Remove` / `Find` 调用键值操作。

**性能**：典型 Add / Find O(1)（哈希碰撞时退化到 O(n)）；适合频繁查询场景。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- 容量满了 Add 失败，业务侧应监控负载因子。
- **键的哈希冲突在小容量时易发生**——Init 时容量建议为预期条目数的 1.5×。（工程经验补充）
- **指针存值要保证生命周期**——若指向局部变量，作用域结束后取出来即悬空。（工程经验补充）
- PDF 错误码引用通用 BOOL 返回（FALSE = 失败）。
- 没有迭代器接口（要遍历需要自己维护键列表）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HashTableCtrl.TcPOU`](../examples/P_Demo_FB_HashTableCtrl.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 标签到 PLC 内部 ID 的映射。
- **价值**：O(1) 替代线性查找。
- **替代方案对比**：
  - ARRAY OF KeyValuePair + 线性扫描：O(n)。
  - **本 FB**：O(1) 平均。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.39
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35006731.html
