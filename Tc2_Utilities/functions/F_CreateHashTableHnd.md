# F_CreateHashTableHnd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35112395.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateHashTableHnd.TcPOU`](../examples/P_Demo_F_CreateHashTableHnd.TcPOU) |

---

## 1. 功能简述

初始化哈希表句柄——把 PLC 静态分配的 `T_HashTableEntry` 数组绑定到 `T_HHASHTABLE` 句柄，使 `FB_HashTableCtrl` 能对其增删查改。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pEntries   : POINTER TO T_HashTableEntry := 0;
    cbEntries  : UDINT := 0;
END_VAR
VAR_IN_OUT
    hTable : T_HHASHTABLE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pEntries` | `POINTER TO T_HashTableEntry` | 0 | 哈希表条目数组的首元素地址；`ADR(arr[0])`。 |
| `cbEntries` | `UDINT` | 0 | 数组的字节总大小；`SIZEOF(arr)`。 |

### VAR_IN_OUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `hTable` | `T_HHASHTABLE` | 要初始化的哈希表句柄；后续 `FB_HashTableCtrl` 通过它访问该表。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出，部分参数同时被 VAR_IN_OUT 修改）。

## 3. 行为说明

函数无状态、立即返回。算法：把 `pEntries` / `cbEntries` 写入 `hTable` 的内部字段（条目数组指针 + 总字节数 + 当前用量等），并清零内部链表索引。**只需调用一次**（启动初始化），之后由 `FB_HashTableCtrl.Insert/Find/Remove` 方法访问。返回 `TRUE` 表示初始化成功；`FALSE` 表示参数错误（数组为 0 / 字节数与 `T_HashTableEntry` 数组不匹配 / 字节数不整除条目大小等）。**生产环境的典型架构**：静态 `ARRAY[0..N-1] OF T_HashTableEntry`（设计期定容量）→ `F_CreateHashTableHnd` 初始化 → 业务用 `FB_HashTableCtrl` 操作。详细使用方法见 PDF 7.2.3（Example: Hash table FB_HashTableCtrl）。

## 4. 错误码 / 返回值

返回 `BOOL`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **只在 PLC 启动时调用一次**——重复调用会清空哈希表内容。
- **`pEntries` 必须指向 PLC 静态分配的数组**——`Tc2_Utilities` 的哈希表不动态分配内存，所有条目槽位由用户预分配。
- `cbEntries = SIZEOF(arr)` 必须精确——`SIZEOF` 也包括 array header（无），= 元素个数 × `SIZEOF(T_HashTableEntry)`。
- **容量 = `cbEntries / SIZEOF(T_HashTableEntry)`**——预估业务最大条目数，预留 30% 余量。
- `T_HashTableEntry` 详细字段见 PDF / InfoSys 类型文档；含 key/value/next-link 三个字段。
- **配套 `FB_HashTableCtrl`**：业务接口；其内部对 `hTable` 操作。
- 返回 `FALSE` 时 `hTable` 处于未初始化状态，不可使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateHashTableHnd.TcPOU`](../examples/P_Demo_F_CreateHashTableHnd.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：工业 OPC 标签字典：~1000 个 OPC 节点名 → 内部地址的映射；启动时一次 `F_CreateHashTableHnd`，运行时 O(1) 查找。
- **价值**：替代线性扫描 / 自写哈希函数；标准库提供哈希查找语义（平均 O(1)），用于大 dict 替代 `ARRAY OF STRUCT` 的 O(N) 顺序查找。
- **替代方案对比**：`FB_HashTableCtrl`：业务操作 API；`F_CreateLinkedListHnd`：双向链表替代；线性扫描：O(N) 易写但慢。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.32 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35112395.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
