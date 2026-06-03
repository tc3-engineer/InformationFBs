# BACnet_Param

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `GVL` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319275659.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_BACnet_Param.TcPOU`](../examples/P_Demo_BACnet_Param.TcPOU) |

---

## 1. 功能简述

库级"项目参数"集合（CONSTANT），可在 XAE 的"PLC → 库实例 → BACnet_Param → Parameter dialog"对话框里按项目调整，TwinCAT 会把这些参数当做 PLC 配置变量处理（声明为 `CONSTANT` 的变量在 TwinCAT 中称为「参数」）。典型可调内容包括：动态对象预分配池容量 `nPool_AV` / `nPool_BV` / `nPool_View` 等、Multistate 对象的状态文本最大长度（默认 40 字符）、DPAD（数据点寻址）名/描述/事件文本的分隔符配置、命令优先级槽位绑定关系等。**每次"激活配置"或 Reset Origin + 重启 PLC 后这些参数才生效**（PDF §5.2.3）。

## 2. 接口定义

> PDF §5.2.3 仅给出 GVL 的用途说明 + 调整方法说明，未列具体字段（字段太多 PDF 不一一枚举）。下表整理 PDF 正文中提到的几类参数。

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_GLOBAL CONSTANT` 区，参数项请在 XAE 的 BACnet_Param Parameter Dialog 中查看完整列表。下表为 PDF 中显式提到的几类。

### 关键参数（按 PDF §5.2.3、§6.1.2、§6.2.10、§8.3 提及）

| 名称示例 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nPoolAV`（与 `nPoolBV` / `nPoolMV` / `nPoolView` 等同族） | `UDINT` | 0（即不预分配） | 对应类型对象的预分配池容量；`FB_BACnet_DynObjectManager` 创建对象时优先用池而非 `__NEW`，节省 router memory（PDF §8.3 示例：`fPoolAV := 42`） |
| `nMultistateTextLength` | `UDINT` | 40 | Multistate / Binary 对象的状态文本属性最大长度；扩到 60 等更大值需在此处调（PDF §5.2.3 例子） |
| `eDPADTreeItemName` | 枚举 | `eSymbolName` | DPAD 在 System Manager 树形中显示哪个属性作为节点名：`eSymbolName`（PLC 符号名）、`eObjectName`（BACnet 对象名）、`eDescription`（描述）三选一（PDF §6.2.10） |
| DPAD 分隔符（Object Name / Description / Event Message Texts 各一组） | `STRING` 等 | — | 用 `\/` 操作符做 DPAD 拼接时这些参数指定运行时实际替换的字符串（PDF §6.2.10） |
| 5P 命令优先级槽位绑定 | `BYTE` | 见下表 | `_5P` 后缀 FB 实际占用的 5 个优先级槽位号（PDF §6.1.2 列出默认值） |

**`_5P` 默认优先级映射表**（PDF §6.1.2 / §6.2.1）：

| 优先级类别 | 默认槽位号 |
|---|---|
| Life-Safety | 1 |
| Critical Equipment Control | 5 |
| Minimum on/off times | 6（BACnet 标准强制，不可改） |
| Manual Local Operator | 7（本地可视化） |
| Manual operator | 8（BMS） |
| Program (PLC) | 15 |

## 3. 行为说明

`VAR_GLOBAL CONSTANT` 在 TwinCAT 中叫"参数"：可在 PLC 项目"Parameter Lists"视图里看到，亦可右键库实例打开"Parameter dialog"在"Value (Editable)"列改值。**改完后需"Activate configuration"或对运行中的 PLC 做"Reset Origin + 重启"才生效**（PDF §5.2.3 顶部明示）。原始默认值保留在库仓库中——只要把 `Tc3_BACnetRev14` 库从项目里移除再重新加入，所有 BACnet_Param 即恢复出厂默认。本 GVL 的参数是**项目级一次性配置**，运行时不要尝试用 PLC 程序写它们（CONSTANT 由编译器锁定）。

`nPoolAV` 等池容量参数影响 router memory 占用模型：预分配池在 PLC 启动时一次性占用，比反复 `__NEW` 节省（但若实际用量低于池容量，是浪费）；项目里如有"动态对象数大致固定"的工况，把对应 `nPool_XX` 调到上限是最优做法（PDF §8.3）。`nMultistateTextLength` 把 multistate 对象的 `aStateText` 数组每元素最大长度从默认 40 扩到更长 — 大型 BMS 经常需要 60+ 字符的描述。

## 4. 错误码 / 返回值

GVL 自身无错误码。参数错配（如设备 router memory 不足时把 `nPoolAV` 设过大）会导致 PLC 启动期失败、`BACnet_Globals.DefaultServer` 拒绝继续初始化（PDF §6.5）。

## 5. 使用注意 / 常见坑

- **改参数必须重新激活配置或 Reset Origin**：PDF §5.2.3 顶部明示这点；运行时改了不生效不要怀疑库 bug。
- **恢复默认值的方法**：把 `Tc3_BACnetRev14` 库从项目移除再加回去 — PDF §5.2.3 推荐做法；不要试图手工把所有参数挨个改回。
- **`nPool_XX` 是双刃剑**：预分配池节省 `__NEW` 调用次数，但启动期一次性占用 router memory；项目里实际动态对象数远低于池容量时是浪费。
- **`nMultistateTextLength` 扩大后所有 multistate 对象都涨内存**：不要为单一对象的需求把全局值改得过大；优先方案是把那个 multistate 对象做拆分。
- **5P 优先级槽位号映射避开 16**：BACnet 标准 16 是默认/最低优先级，给 5P 用会导致 BACnet 客户端写入与 PLC 程序写入互踩。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BACnet_Param.TcPOU`](../examples/P_Demo_BACnet_Param.TcPOU)

```iecst
PROGRAM P_Demo_BACnet_Param
VAR
    sParamReadme : STRING := 'BACnet_Param 参数在 XAE 中调整：右键库实例 → Parameter dialog → 改 Value (Editable) → Activate Configuration。';
END_VAR

;
```

## 7. 业务场景与实际价值

- **场景**：项目里要把 100 个动态 Analog Value 预分配（避免上电后反复 `__NEW`，提升启动速度），同时项目里某些 multistate 选项的文本超过 40 字符。
- **价值**：在 XAE 一个对话框里把 `nPoolAV := 100; nMultistateTextLength := 60;` 改完激活，全项目生效；不需要改任何 PLC 代码。
- **替代方案对比**：
  - 不改池容量，让库在动态创建时反复 `__NEW`：能做但 PLC 启动慢、运行期 router memory 碎片化
  - 自己写常量替代：失去 XAE Parameter dialog 这层 UI
  - **本 GVL**：官方推荐，跟 XAE 工具集成最好

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §5.2.3、§6.1.2（5P 优先级）、§6.2.10（DPAD 显示模式）、§8.3（对象池）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319275659.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 GVL**：`BACnet_Globals`、`Version`
