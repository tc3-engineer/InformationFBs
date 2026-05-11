# stLibVersion_Tc2_Standard

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74426251.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_Standard.xml`](../examples/P_Demo_stLibVersion_Tc2_Standard.xml) |

---

## 1. 功能简述

`stLibVersion_Tc2_Standard` 是 `Tc2_Standard` 库的**版本号全局常量**。它的类型是 `ST_LibVersion`（定义在 `Tc2_System` 库中），由 TwinCAT 编译器在加载库时自动填入当前库的主版本 / 次版本 / 构建号 / 修订号 / 字符串描述。读取它可以在运行时确认 PLC 工程引用的是哪个版本的 `Tc2_Standard`。

按 Beckhoff 的版本管理惯例，**所有 Beckhoff 库都暴露同名模式的全局常量** `stLibVersion_<LibName>`，例如 `stLibVersion_Tc2_System`、`stLibVersion_Tc3_EventLogger`。读取它们再配合 `Tc2_System.F_CmpLibVersion` 即可在 PLC 工程启动时做"最低库版本"校验，避免在 TwinCAT 版本切换、库手动覆盖等情况下使用了不兼容的旧版本。

PDF §6.1 说明本库仅声明该全局常量，**TwinCAT 2 风格的 `LibVersion_xxx.QueryLibraryVersion()` 接口已不再支持**。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_Standard : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_Standard` | `ST_LibVersion` | `Tc2_Standard` 库的版本号；只读，由编译器加载库时填充 |

### VAR_OUTPUT / VAR_IN_OUT

不适用（全局常量，无 IO 接口）。`ST_LibVersion` 结构体的具体字段（iMajor / iMinor / iBuild / iRevision / sVersion 等）定义在 `Tc2_System` 库的 `ST_LibVersion` 文档里，本库不重述。

## 3. 行为说明

该常量在 PLC 工程加载库时被编译器自动设置，运行时**只读不可写**：试图给它赋值会编译报错。工程上典型用法是在 PLC 启动逻辑里读一次本常量，调用 `Tc2_System.F_CmpLibVersion` 与业务要求的最低版本做比较，若版本不达标则把控制器置入 fault 状态并报警。这能在 TwinCAT 版本升级、第三方库手动替换、克隆工程切换目标平台等场景中提早暴露不兼容问题，避免运行到一半才发现某个 FC 行为变了。

另外可以在 PLC project 的 References → `Tc2_Standard` 上右键 "Properties" 静态查看版本，无需登录运行；但运行时读取常量是唯一**能被 PLC 业务逻辑感知**的方式。`F_CmpLibVersion` 提供大于等于 / 等于 / 小于等多种比较模式，能精细到 build / revision 级别。

## 4. 错误码 / 返回值

无（常量声明，无返回值，无错误码）。结构体的字段读取行为以 `Tc2_System.ST_LibVersion` 为准。

## 5. 使用注意 / 常见坑

- **类型来自 `Tc2_System`**：使用 `ST_LibVersion` 必须确保 PLC 工程已引用 `Tc2_System`，否则编译报错 "Type 'ST_LibVersion' not found"。
- **运行时校验最低版本**：标准模式
  ```iecst
  IF NOT F_CmpLibVersion(
      stLibVersion := stLibVersion_Tc2_Standard,
      iMajor := 1, iMinor := 3, iBuild := 4, iRevision := 0,
      nCmpType := E_CmpLibVersion.GreaterOrEqual
  ) THEN
      // 业务侧把系统置 fault 并报警
  END_IF;
  ```
  推荐放在 `MAIN` 程序的初始化段或专用的版本检查 POU 里。（工程经验补充）
- **常量值在编译时确定**：工程编译后版本就锁定了，运行中无法热切换库。要切换版本必须重编重下载。
- **TwinCAT 2 接口不可用**：旧风格 `LibVersion_Tc2_Standard.QueryLibraryVersion()` 在 TwinCAT 3 已废弃。
- **复制到本地变量便于在线监视**：直接 monitor 全局常量在某些 XAE 版本下显示不友好，工程上常 `stMyVer := stLibVersion_Tc2_Standard;` 把它复制到本地变量再 monitor。（工程经验补充）
- **跨库版本检查批量化**：一个工程可能引用 10+ 个 Beckhoff 库，建议建一个 `FB_CheckLibVersions` 把所有 `stLibVersion_*` 集中校验一次，比散落在各 POU 里好维护。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_Standard.xml`](../examples/P_Demo_stLibVersion_Tc2_Standard.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：工程启动校验 Tc2_Standard 库至少 1.3.4，否则报警
PROGRAM P_Demo_stLibVersion_Tc2_Standard
VAR
    stMyVer : ST_LibVersion;
    bOk     : BOOL;
END_VAR

stMyVer := stLibVersion_Tc2_Standard;
bOk := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_Standard,
    iMajor := 1, iMinor := 3, iBuild := 4, iRevision := 0,
    nCmpType := E_CmpLibVersion.GreaterOrEqual);
```

## 7. 业务场景与实际价值

- **场景**：工程启动校验所有引用库的最低版本、TwinCAT 版本升级后兼容性自检、克隆工程切换 PLC 目标时的版本守卫、MES 端记录 PLC 当前用的库版本以便故障复盘。
- **价值**：把"库版本对不对"从"靠工程师记得"变成"程序自动检查"，避免因库版本回退导致某个 FC 行为异常的隐蔽故障。
- **替代方案对比**：
  - **References → Properties 查看**：静态查看，无法被业务逻辑感知，运行中切了库不会触发任何动作
  - **手写宏 / 字符串字面量记版本**：必须人工同步，容易和实际不一致
  - **本常量 + `F_CmpLibVersion`**：编译器自动维护、运行时可读、自动比较，**版本管理最佳实践**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74426251.html
- **相关 DUT / FC**：`Tc2_System.ST_LibVersion`（结构体定义）、`Tc2_System.F_CmpLibVersion`（版本比较）、`Tc2_System.E_CmpLibVersion`（比较模式枚举）、其它库的同名常量 `stLibVersion_<LibName>`
