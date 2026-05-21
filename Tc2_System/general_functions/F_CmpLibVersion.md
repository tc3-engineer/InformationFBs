# F_CmpLibVersion

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31006219.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CmpLibVersion.xml`](../examples/P_Demo_F_CmpLibVersion.xml) |

---

## 1. 功能简述

F_CmpLibVersion 把当前安装的库版本（通过 `stLibVersion_<libname>` 全局常量传入）与代码中要求的最小版本（major / minor / build / revision 四元组）做比较，返回 `-1` / `0` / `+1` 表示『装的版本低于 / 等于 / 高于』要求版本。用于库级版本守门：在工程编译期或运行启动时检查依赖库版本，避免因下层库降级导致接口不兼容的隐蔽 bug。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stVersion : ST_LibVersion;
    iMajor : UINT;
    iMinor : UINT;
    iBuild : UINT;
    iRevision : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stVersion` | `ST_LibVersion` | 目标库的版本常量，按 `stLibVersion_<libname>` 命名传入（类型 `ST_LibVersion`）。 |
| `iMajor` | `UINT` | 要求的 major 主版本号。 |
| `iMinor` | `UINT` | 要求的 minor 次版本号。 |
| `iBuild` | `UINT` | 要求的 build 构建号。 |
| `iRevision` | `UINT` | 要求的 revision 修订号。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回值语义**：

- `-1`：当前库版本低于要求版本，应当告警或拒绝启动；
- ` 0`：当前库版本恰好等于要求版本；
- `+1`：当前库版本高于要求版本，通常仍兼容。

**版本比较顺序**：按字典序——先比 major，相等再比 minor，再 build，最后 revision。任一位较高即返回 +1，较低返回 -1。

**输入约束**：`stVersion` 必须传入对应库的 `stLibVersion_<libname>`，跨库混用没意义。

**典型用法**：在 PLC `INIT` 任务或 `FB_init` 中检查依赖，不满足时设置全局错误标志拒绝启动 MAIN 任务，避免后续逻辑跑在错误的库版本上。

## 4. 错误码 / 返回值

本函数返回 `DINT`：

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `-1` | 装的版本低于要求 | 告警 / 拒绝启动 |
| `0`  | 装的版本恰好等于要求 | 视业务需要继续或告警 |
| `+1` | 装的版本高于要求 | 通常兼容，继续 |

## 5. 使用注意 / 常见坑

- **版本号比较不区分 release / debug**：本函数只比四元组数字，不关心库的内部构建标识。
- **不能比较跨库**：`stLibVersion_Tc2_System` 不能用本函数对照 `stLibVersion_Tc2_Math` 的要求。
- **库未引用时编译错误**：`stLibVersion_<libname>` 是常量，库未被工程引用时编译期就报错，不是运行期错误。（工程经验补充）
- **`>= 0` 才算满足要求**：忘了取 `>= 0` 而只判 `= 0` 会拒绝高版本，反而是常见 bug。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CmpLibVersion.xml`](../examples/P_Demo_F_CmpLibVersion.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：集成商交付前的版本守门：MAIN 启动时校验 Tc2_System ≥ 3.3.8.0，低版本直接置位 bSystemBlocked 拒绝运行 MAIN，避免依赖新 API 但库没升级的隐蔽崩溃。
- **价值**：替代『先跑起来出错再查依赖』的低效方式，编译 + 启动时显式守门。
- **替代方案对比**：
  - 检查 `stLibVersion.iMajor` 等字段手写比较：能用但要写 4 个 `IF` 分支，易写反。
  - 不检查：风险大，库降级后逻辑可能挂在不可预测的地方。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31006219.html
- **相关 FB / FC**：`stLibVersion_Tc2_System`
