# F_CreateHashTableHnd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35111435.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateHashTableHnd.xml`](../examples/P_Demo_F_CreateHashTableHnd.xml) |

---

## 1. 功能简述

初始化一个哈希表句柄。用户先在 PLC 区分配一段 `T_HashTableEntry` 数组（条目存储区），再调本函数把数组首址 + 字节大小填入 `hTable`（`T_HHASHTABLE` 类型句柄），后续 `FB_HashTableCtrl` 用此句柄做查/增/删。

句柄一辈子只需要 init 一次（一般放 `INIT_VAR` 步骤或上电首扫描）。不调本函数直接用 `FB_HashTableCtrl` 会报错（句柄无效）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pEntries   : POINTER TO T_HashTableEntry := 0;
    cbEntries  : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pEntries` | `POINTER TO T_HashTableEntry` | `0` | 哈希表条目数组首址（`ADR(arEntries)`）。 |
| `cbEntries` | `UDINT` | `0` | 条目数组的总字节数（`SIZEOF(arEntries)`，不是条目数量）。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hTable : T_HHASHTABLE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `hTable` | `T_HHASHTABLE` | 待初始化的哈希表句柄；初始化后由 `FB_HashTableCtrl` 引用。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 初始化成功，`FALSE` = 失败（指针空、字节数 0、字节数非 `T_HashTableEntry` 整数倍等）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

调用一次返回一次。函数把 `pEntries` 和 `cbEntries` 写入 `hTable` 内部字段，并把条目数（= `cbEntries / SIZEOF(T_HashTableEntry)`）作为表容量；条目内部状态字段初始化为"空槽"。

执行成功条件（全部满足才返回 TRUE）：
1. `pEntries <> 0`（已分配存储区）
2. `cbEntries > 0`
3. `cbEntries MOD SIZEOF(T_HashTableEntry) = 0`（不能多出半个条目）

初始化顺序约束：
- **必须先调本函数再用 `FB_HashTableCtrl`**：调用顺序反了 → FB_HashTableCtrl 行为未定义（错误码或越界访问）。
- **运行中不可重 init**：会丢已有条目；要换条目区先停所有访问操作再重 init。
- **句柄只对当前任务有效**：跨任务共享需要自己加互斥；本函数不带锁。

容量规划：哈希表负载因子高（条目数接近容量）时碰撞多、性能下降。PDF 建议预留 30%-50% 空闲槽位。具体规模看应用，从几十条到几千条都可（受可分配内存限制）。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 初始化成功，`hTable` 可交给 `FB_HashTableCtrl` |
| `FALSE` | 参数无效（指针空 / 字节数 0 / 非整数倍） |

## 5. 使用注意 / 常见坑

- **传 `SIZEOF(arEntries)` 不是 `LEN`**：要传字节数；条目数由函数内部除算。
- **存储区不能是局部变量**：必须是 `VAR` 全局或 `VAR_PERSISTENT`，否则函数返回后存储区被栈帧销毁，FB 操作时崩溃。
- **不能 init 两次**：第二次 init 会丢上次的条目（工程经验补充）。
- **配合 `FB_HashTableCtrl` 才有意义**：本函数只准备数据结构，真正的 add/search/delete 由 FB 完成。
- **不带锁，跨任务用要自己 mutex**：典型只在一个 PLC 任务内使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateHashTableHnd.xml`](../examples/P_Demo_F_CreateHashTableHnd.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CreateHashTableHnd
VAR
    arEntries : ARRAY[0..127] OF T_HashTableEntry;   // 容量 128 条
    hTable    : T_HHASHTABLE;
    bInitOk   : BOOL;
    bDone     : BOOL;                                 // 仅上电首扫初始化一次
END_VAR

IF NOT bDone THEN
    bInitOk := F_CreateHashTableHnd(
        pEntries  := ADR(arEntries),
        cbEntries := SIZEOF(arEntries),
        hTable    := hTable);
    bDone := TRUE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：MES 把 1000 个物料号下发到 PLC，PLC 用哈希表 O(1) 查表得物料属性；如果用线性 `FOR` 找，单次查询 O(N) 在 1000 条规模时一个周期跑不完。
- **价值**：哈希表把"按 ID 查工艺参数"压到常数时间；本函数是其使用前的一次性 init，必不可少。
- **替代方案对比**：
  - 不用哈希、用线性数组：N=1000 时单查 O(N) 耗时，多查叠加会超 PLC 周期
  - 自己实现哈希：要写哈希函数、碰撞处理、扩容；30 分钟变 3 天
  - 本函数 + `FB_HashTableCtrl`：成熟、Beckhoff 验证、容量预定即可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.32 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35111435.html
- **相关 FB / 类型**：`FB_HashTableCtrl`（增/查/删/遍历）、`T_HashTableEntry`（条目结构）、`T_HHASHTABLE`（句柄类型）、`F_GenerateHashValue`（独立计算哈希）
