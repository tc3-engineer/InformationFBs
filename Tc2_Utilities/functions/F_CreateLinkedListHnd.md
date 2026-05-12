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
| Example | [`examples/P_Demo_F_CreateLinkedListHnd.xml`](../examples/P_Demo_F_CreateLinkedListHnd.xml) |

---

## 1. 功能简述

初始化一个链表句柄。用户先在 PLC 区分配 `T_LinkedListEntry` 数组（节点池），再调本函数把数组首址 + 字节数填入 `hList`（`T_HLINKEDLIST` 类型）。之后 `FB_LinkedListCtrl` 用此句柄做插入/删除/遍历。

跟 `F_CreateHashTableHnd` 的关系是平行——一个用哈希表，一个用链表；都是先准备节点池再 init 句柄，然后由对应 FB 操作。链表适合"顺序敏感"的场景（FIFO 报警队列、操作历史栈），哈希表适合"按 key 查"的场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pEntries  : POINTER TO T_LinkedListEntry := 0;
    cbEntries : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pEntries` | `POINTER TO T_LinkedListEntry` | `0` | 节点池数组首址（`ADR(arEntries)`）。 |
| `cbEntries` | `UDINT` | `0` | 节点池总字节数（`SIZEOF(arEntries)`，不是节点数量）。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hList  : T_HLINKEDLIST;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `hList` | `T_HLINKEDLIST` | 待初始化的链表句柄；后续由 `FB_LinkedListCtrl` 引用。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 初始化成功；`FALSE` = 参数无效（pointer 空、字节数 0、非 `T_LinkedListEntry` 整数倍）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

调用一次返回一次。函数把 `pEntries` 和 `cbEntries` 写入 `hList` 内部字段，节点数 = `cbEntries / SIZEOF(T_LinkedListEntry)`；所有节点状态初始化为"空闲"，链表初始为空（无头无尾）。

链表存储模型：池中的每个节点带 `prev` / `next` 指针；`FB_LinkedListCtrl` 插入元素时从空闲池取节点；删除时归还。所以容量上限就是节点池大小。

执行约束（和哈希表 init 类似）：
1. `pEntries <> 0`
2. `cbEntries > 0`
3. `cbEntries MOD SIZEOF(T_LinkedListEntry) = 0`
4. 节点池必须是 `VAR` 全局或 `VAR_PERSISTENT`（不能是局部）
5. 每个句柄只能 init 一次；重 init 丢已有节点

容量规划：FIFO 队列长度上限 = 节点池容量；超过时插入失败。报警历史栈 100 条够用，遥测缓冲可能要 1000+，按业务定。

跟 `T_HLINKEDLIST` 字段名 `hList` 在 PDF 表中带注释说"哈希表句柄"看似错误，实际是 PDF 复用了 hash 模板文本，按字段名以"链表句柄"理解（这是 PDF 跨表复制残留，InfoSys 一致）。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 初始化成功；`hList` 交给 `FB_LinkedListCtrl` 使用 |
| `FALSE` | 参数无效 |

## 5. 使用注意 / 常见坑

- **必须先 init 才能用 `FB_LinkedListCtrl`**：未 init 的句柄使用结果未定义。
- **节点池必须 `VAR` 全局或 `VAR_PERSISTENT`**：局部变量在函数返回后被回收，链表内部指针失效。
- **不要重复 init**：丢节点。换池子必须先空所有引用再重 init（工程经验补充）。
- **不带锁**：跨任务共享要自己 mutex；典型只在一个任务用。
- **PDF 说明里 `hList` 的描述文本误抄了哈希表**（"Hash table handle"）：实际就是链表句柄（工程经验补充，InfoSys 与 PDF 文字一致都是"Hash table handle"残留，但字段类型 `T_HLINKEDLIST` 就明示了正确语义）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateLinkedListHnd.xml`](../examples/P_Demo_F_CreateLinkedListHnd.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CreateLinkedListHnd
VAR
    arNodePool : ARRAY[0..99] OF T_LinkedListEntry;   // 100 节点上限
    hAlarmFifo : T_HLINKEDLIST;
    bInitOk    : BOOL;
    bDone      : BOOL;
END_VAR

IF NOT bDone THEN
    bInitOk := F_CreateLinkedListHnd(
        pEntries  := ADR(arNodePool),
        cbEntries := SIZEOF(arNodePool),
        hList     := hAlarmFifo);
    bDone := TRUE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：产线报警 FIFO 队列——按时间顺序保存最近 100 条报警；HMI 滚动显示、按"先进先出"裁剪。链表适合频繁尾部插入 + 头部删除。
- **价值**：相比数组手写"环形 buffer + 头尾游标"，链表语义清晰，Beckhoff 已验证的 `FB_LinkedListCtrl` 提供 add/remove/iterate；本函数是 init 一次性步骤。
- **替代方案对比**：
  - 自己实现链表：写 prev/next 维护要 50+ 行，易在边界（首/尾删）出 bug
  - 环形数组：性能更好但删除中间元素难
  - 本函数 + `FB_LinkedListCtrl`：完整链表 API、Beckhoff 验证

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.33 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35112971.html
- **相关 FB / 类型**：`FB_LinkedListCtrl`（增/删/遍历）、`T_LinkedListEntry`（节点结构）、`T_HLINKEDLIST`（句柄类型）、`F_CreateHashTableHnd`（哈希表 init，平行用法）
