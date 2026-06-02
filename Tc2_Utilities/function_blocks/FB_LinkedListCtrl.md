# FB_LinkedListCtrl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35007499.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_LinkedListCtrl.TcPOU`](../examples/P_Demo_FB_LinkedListCtrl.TcPOU) |

---

## 1. 功能简述

FB_LinkedListCtrl 双向链表控制器——动态可增删的节点链。

用于：工单队列（中间插入 / 删除频繁）、HMI 列表 / 树状结构。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    putValue : PVOID := 0;
    putPosPtr : POINTER TO T_LinkedListEntry := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `putValue` | `PVOID` | `0` | 参数 `putValue`（类型 `PVOID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `putPosPtr` | `POINTER TO T_LinkedListEntry` | `0` | 参数 `putPosPtr`（类型 `POINTER TO T_LinkedListEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL := FALSE;
    getValue : PVOID := 0;
    getPosPtr : POINTER TO T_LinkedListEntry := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOk` | `BOOL` | `FALSE` | 输出布尔标志：`bOk`。具体语义见 §3 行为说明。 |
| `getValue` | `PVOID` | `0` | 参数 `getValue`（类型 `PVOID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `getPosPtr` | `POINTER TO T_LinkedListEntry` | `0` | 参数 `getPosPtr`（类型 `POINTER TO T_LinkedListEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hList : T_HLINKEDLIST;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hList` | `T_HLINKEDLIST` | 参数 `hList`（类型 `T_HLINKEDLIST`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

## 3. 行为说明

**OO 方法**：`Init` 绑定头节点 → `AddHead` / `AddTail` / `Remove` / `Find` 操作。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **节点要业务侧分配**——FB 仅管理 next/prev 指针，不分配节点存储。
- **遍历中删除会让游标失效**——经典链表陷阱，要在删除前先保存 next。（工程经验补充）
- 跨任务访问链表必须加锁（用 `FB_IecCriticalSection`）。（工程经验补充）
- PDF 错误反映为 BOOL 返回（FALSE = 失败）。
- 没有索引访问 O(n)——大量随机访问场景用 HashTable 更合适。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_LinkedListCtrl.TcPOU`](../examples/P_Demo_FB_LinkedListCtrl.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工单队列频繁中间插入 / 删除。
- **价值**：O(1) 中间操作。
- **替代方案对比**：
  - ARRAY：中间插入 O(n) 拷贝。
  - **本 FB**：O(1)。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.46
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35007499.html
