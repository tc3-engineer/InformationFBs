# FB_BACnet_DynObjectManager

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Dynamic Object Manager` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/14456739083.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BACnet_DynObjectManager.TcPOU`](../examples/P_Demo_FB_BACnet_DynObjectManager.TcPOU) |

---

## 1. 功能简述

提供在 PLC 运行时**动态创建 / 删除 BACnet 对象**的能力。典型场景：本机暴露给 BMS 的 BACnet 对象数量在编译期不固定（来自配置文件、HMI 配置界面、或第三方数据源），需要在运行时按需 `__NEW` 出 `FB_BACnet_AV` / `FB_BACnet_BV` / `FB_BACnet_View` 等对象实例并加入 BACnet 服务数据库。本 FB 取代了"静态在变量区声明对象数组"的传统做法，给项目带来真正的动态对象池。**使用本 FB 需要在编译器选项中启用 `DynamicCreation` pragma**（PDF §8 第一段警示）。

## 2. 接口定义

> PDF §8.1–§8.6 用一组完整示例展示本 FB，未单独列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表整理 PDF 示例中确认存在的引脚 / 属性 / 方法。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_INPUT`；行为通过实例化时的构造参数 `(bCycleObjects := ..., bAutoFinishInit := ...)` 配置。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_OUTPUT`；状态通过 `Ready` / `CreatedObjects` 等成员变量暴露。

### VAR_IN_OUT

无。

### 关键属性 / 构造参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bCycleObjects` | `BOOL` | `FALSE` | 设为 `TRUE` 时本 FB 内部自动循环调用所有已创建对象（典型用法）；设 `FALSE` 时调用方需对每个动态对象手工 `DynView^();` 调用 |
| `bAutoFinishInit` | `BOOL` | `TRUE` | 默认创建对象几个周期后库自动结束初始化；设 `FALSE` 时调用方需手工调 `FinishInit()` 结束初始化（适用于"等配置文件读完再开始注册"场景） |
| `Ready` | `BOOL` | — | 本 FB 启动并 ready 接受 CreateObject 时为 `TRUE`；首次调用必须等 `Ready` 才能 `CreateObject` |
| `CreatedObjects` | `UDINT` | — | 当前已创建的对象总数；`> 0` 表示有动态对象在工作 |

### 方法

| 方法 | 用途 | 参数（按 PDF §8.4 / §8.6 示例） |
|---|---|---|
| `CreateObject(pInst, eObjType, nInstId, sObjectName, sDescription, iParent)` | 创建一个标准对象类型实例（库内置的 25 种 BACnet 对象） | `pInst : POINTER TO <FB_BACnet_*>`（接收新实例指针）、`eObjType : E_BACnet_CreateObjType`（枚举）、`nInstId : UDINT`（实例号，传 `BACnet_Globals.nBACnetInstId_Auto` 让库自动分配）、`sObjectName / sDescription : STRING`、`iParent : LREAL/POINTER`（父 View 或 0） → 返回 `BOOL` 成功标志 |
| `CreateObjectEx(pInst, nInstId, sObjectName, sDescription, iParent)` | 创建"自定义 FB"类型（来自用户自己写的 BACnet 对象子类）；调用方需先 `pInst := __NEW(FB_BACnet_BV_Event);` 再传入 | `pInst : POINTER TO 自定义 FB 类型`、其余参数与 `CreateObject` 同 → 返回 `BOOL` |
| `DeleteObject(pInst)` | 删除一个动态对象 | `pInst : POINTER TO FB_BACnet_*` |
| `RemoveObjectEx(pInst)` | 删除一个 "CreateObjectEx" 创建的自定义对象；调用方接着需 `__DELETE(pInst);` 释放内存 | `pInst : POINTER TO 自定义 FB 类型` |
| `Reset()` | 一次性清空所有由本 manager 创建的对象 | 无参数 |
| `FinishInit()` | `bAutoFinishInit = FALSE` 时由用户手工触发"完成初始化"，让 supplement 开始接收 BACnet 请求 | 无参数 |

⚠️ PDF + InfoSys 未在本 FB 节列出 `CreateObject` / `CreateObjectEx` 各参数的精确类型。InfoSys 在线主题（链接见 §8）给出详细签名。

## 3. 行为说明

工作流（按 PDF §8.2 / §8.4 状态机）：
1. 在 PROGRAM 的 VAR 区声明 `fbDynObject : FB_BACnet_DynObjectManager := (bCycleObjects := TRUE);` 并每周期调用一次 `fbDynObject();`
2. 等到 `fbDynObject.Ready = TRUE`（首次启动会延后几个周期）；
3. 在外部事件（HMI 按钮、配置文件读完、第三方数据到达）触发时调用 `fbDynObject.CreateObject(...)` 创建对象，函数返回 `TRUE` 表示成功，新对象的指针写入第 1 个参数；
4. 创建后立刻可以设属性，例如 `DynAV01^.eUnit := E_BA_Unit.eTemperature_DegreesCelsius;`，BACnet supplement 在几个周期后把对象注册进数据库；
5. 删除时调 `fbDynObject.DeleteObject(pInst)` 或一次性 `fbDynObject.Reset()` 清掉全部；
6. `bCycleObjects := TRUE` 时已创建对象**只能**由本 manager 调度（用户代码不能再 `pInst^();` 否则重复调用），`bCycleObjects := FALSE` 时用户必须每周期对每个对象手动 `pInst^();`。

**`bAutoFinishInit` 用途**：默认 `TRUE` 时库会在 `CreateObject` 后几个周期自动结束初始化、让对象上线；如果你要从配置文件批量读对象（耗时几百毫秒），希望"全部读完再让 BMS 看到"以避免半成品状态，就把 `bAutoFinishInit` 设 `FALSE`，最后用 `fbDynObject.FinishInit();` 一次性提交。

**FB_exit 释放**：用户用 `__NEW + CreateObjectEx` 创建的"自定义子类"必须在 PLC 程序终止前调 `RemoveObjectEx + __DELETE` 释放内存（PDF §8.6 示例），否则会泄漏 router memory。Tc3_BACnetRev14 库内置的对象类型由 `Reset()` 自动释放，无需手工 `__DELETE`。

## 4. 错误码 / 返回值

`CreateObject` / `CreateObjectEx`：返回 `BOOL`，`TRUE` = 创建成功（包括 router memory 充足、实例号未冲突、父节点有效），`FALSE` = 失败（最常见 router memory 占用 ≥60% 时库强制拒绝以保护其它功能，PDF §6.5；次常见是实例号冲突——`nInstId` 已被静态对象占用）。

`DeleteObject` / `RemoveObjectEx` / `Reset` / `FinishInit`：无显式返回（PDF 示例未读返回值），失败现象表现为对象仍可访问或 BMS 端仍可见。

⚠️ PDF / InfoSys 在本 FB 节未列具体错误码常量。

## 5. 使用注意 / 常见坑

- **必须开 `DynamicCreation` pragma**：PDF §8 顶部明确指出"使用本特性需在编译器设置中启用 `DynamicCreation` pragma"，否则 `__NEW` 不可用、本 FB 退化为不能创建新实例。
- **动态对象实例号必须唯一**：PDF §8.3 强调"object instance numbers must be unique"；使用 `BACnet_Globals.nBACnetInstId_Auto` 让库自动分配是最稳妥的做法。
- **`bCycleObjects` 不能两边都开**：要么由 manager 内部循环（`TRUE`）调用所有对象、要么用户代码手动循环（`FALSE`）；都开会导致每周期被调度两次，BACnet 视为重复对象访问错误。
- **预定义池 (`nPool_<TYPE>`)**：PDF §8.3 推荐若知道动态对象大致数量，把 `BACnet_Param.nPoolAV` 等设到上限，库优先用池而非 `__NEW`，比反复 `__NEW` 更节省 router memory。
- **自定义子类需要 `FB_exit`**：PDF §8.6 反复强调使用 `__NEW + CreateObjectEx` 时必须实现 `FB_exit` 来手工 `__DELETE`，否则下次 OnlineChange 会泄漏 router memory；本 FB 自身的库内置类型由 manager 自动处理。
- **`Ready = TRUE` 前不能创建**：第一次 PLC 启动后本 FB 需要几个周期完成初始化；过早 `CreateObject` 会失败，必须用 `IF fbDynObject.Ready THEN ... END_IF` 围住调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BACnet_DynObjectManager.TcPOU`](../examples/P_Demo_FB_BACnet_DynObjectManager.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_DynObjectManager
VAR
    fbDynObject  : FB_BACnet_DynObjectManager := (bCycleObjects := TRUE);
    bCreate      : BOOL;
    bDelete      : BOOL;
    DynView      : POINTER TO FB_BACnet_View;
    DynAV01      : POINTER TO FB_BACnet_AV;
END_VAR

fbDynObject();
IF fbDynObject.Ready THEN
    IF bCreate THEN
        bCreate := FALSE;
        IF fbDynObject.CreateObject(DynView,
                E_BACnet_CreateObjType.eStructuredView,
                BACnet_Globals.nBACnetInstId_Auto,
                'DynamicView', 'Dynamic View', 0) THEN
            ;
        END_IF
        IF fbDynObject.CreateObject(DynAV01,
                E_BACnet_CreateObjType.eAnalogValue,
                BACnet_Globals.nBACnetInstId_Auto,
                '\/DynAV01', '\/Dynamic AV 1', DynView) THEN
            DynAV01^.eUnit := E_BA_Unit.eTemperature_DegreesCelsius;
        END_IF
    END_IF
    IF bDelete THEN
        bDelete := FALSE;
        fbDynObject.Reset();
    END_IF
END_IF
```

## 7. 业务场景与实际价值

- **场景**：客户的 BMS 项目中 BACnet 对象数量来自 SQLite 配置文件，每个建筑不一样（200 ~ 2000 不等）。如果在 PLC 变量区静态声明，必须按上限分配数组 + 每次新建筑都要改 PLC 程序 + 配置激活停一次机。改用本 FB 后：PLC 程序与楼栋无关，启动期从配置文件读对象清单后动态创建即可。
- **价值**：把"BACnet 对象池"从编译期静态变成运行时动态，大幅减少跨项目工程量；同时支持本地 HMI 用户在 SCADA 上"加一个虚拟点"的需求。
- **替代方案对比**：
  - 在变量区按上限预声明 `ARRAY[0..1999] OF FB_BACnet_AV`：能用但 router memory 浪费严重（PDF §6.5 估算每对象 20 KB → 1999×20 KB ≈ 40 MB 即使未使用也占用）
  - 用 `Tc2_DMX` / `Tc3_JsonXml` 解析配置文件后再生成 PLC 代码：能做但需离线工具链 + 改 PLC 后必须重新激活
  - **本 FB**：仓库内置、零外部工具、纯在线创建

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §8.1 ~ §8.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/14456739083.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 FB / FC**：`FB_BACnet_Server`（接收动态对象的服务器）、`FB_BACnet_AV` / `FB_BACnet_BV` / `FB_BACnet_View`（动态创建的对象类型）
