# F_CreateLinkedListHnd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35112971.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateLinkedListHnd.TcPOU`](../examples/P_Demo_F_CreateLinkedListHnd.TcPOU) |

---

## 1. 功能简述

初始化双向链表句柄——`F_CreateHashTableHnd` 的链表版本；与 `FB_LinkedListCtrl` 配合实现 O(1) 头尾插入 / O(N) 顺序遍历。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pEntries  : POINTER TO T_LinkedListEntry := 0;
    cbEntries : UDINT := 0;
END_VAR
VAR_IN_OUT
    hList  : T_HLINKEDLIST;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pEntries` | `POINTER TO T_LinkedListEntry` | 0 | 链表条目数组首元素地址。 |
| `cbEntries` | `UDINT` | 0 | 数组字节大小。 |

### VAR_IN_OUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `hList` | `T_HLINKEDLIST` | 要初始化的双向链表句柄。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出，部分参数同时被 VAR_IN_OUT 修改）。

## 3. 行为说明

函数无状态、立即返回。语义同 `F_CreateHashTableHnd`，但容器是双向链表：每个 `T_LinkedListEntry` 含 prev / next / payload 三字段。**`pEntries` 是 PLC 静态分配的条目池**——链表插入时从未用槽位取一个、链接到链表中；删除时把槽位回收到 free list。**适用场景与哈希表互补**：哈希表 O(1) 查找但不保序；链表保序、按位置访问 O(N) 但插入删除 O(1)。日志缓冲、FIFO 队列、最近访问列表等用链表。

## 4. 错误码 / 返回值

返回 `BOOL`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **只在 PLC 启动时调用一次**——重复调用会清空链表。
- **`pEntries` 必须是静态分配的数组**——不动态分配。
- **容量 = `cbEntries / SIZEOF(T_LinkedListEntry)`**。
- **`T_LinkedListEntry`** 含 prev / next 双向链接 + payload 字段。
- **配套 `FB_LinkedListCtrl`** 提供 InsertHead / InsertTail / Remove / GetNext 等方法。
- 返回 `FALSE` 时 `hList` 不可使用。
- **Vs `FB_FifoBufferCtrl`**（如果库有）：FIFO 更简单但只支持先进先出；链表更灵活但 API 复杂。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateLinkedListHnd.TcPOU`](../examples/P_Demo_F_CreateLinkedListHnd.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：报警历史记录的环形缓冲：最近 100 条报警按时序入链表，超过 100 自动剔除最早一条。
- **价值**：替代手写 ARRAY + head/tail 索引环形缓冲——本函数提供库支持的双向链表数据结构。
- **替代方案对比**：`FB_LinkedListCtrl`：业务操作 API；`F_CreateHashTableHnd`：哈希表（O(1) 查找）；自写环形缓冲：可读性差。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.33 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35112971.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
