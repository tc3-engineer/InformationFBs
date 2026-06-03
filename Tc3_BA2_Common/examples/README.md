# Tc3_BA2_Common 例程目录

本目录包含 Tc3_BA2_Common 库全部 80 个 FB / FC / GVL 的 TwinCAT 3 原生 `.TcPOU` 演示程序。每个 `P_Demo_<Name>.TcPOU` 都遵循 CLAUDE.md 硬规则：

- 顶部三件套注释：**场景 / 价值 / 验证步骤**
- 变量名贴近工业语义（不是 `bSig1` / `var_a`）
- 单次完整调用形式（`fbX(IN := …, Q => bRunOk);`）
- 注释行数 ≥ 代码行数 1/3，解释 WHY 不复述 WHAT
- 包含被演示 FB 实例 `fb<Name> : <Name>;`，所有 `VAR_INPUT` 显式赋值

## 导入步骤

1. 在 TwinCAT 3 PLC 项目里 → 右键 **POUs** 文件夹 → **Add → Existing Item**
2. 选定本目录下的 `P_Demo_<Name>.TcPOU`
3. 在项目 References 下 → **Add library** → 选 `Tc3_BA2_Common`
4. 编译（Build）→ 登录（Login）→ 运行
5. 按例程顶部"验证"注释指引，在线写值，对照预期行为观察输出

## 完整清单

按文档目录对应（共 80 个文件）：

- **Controllers** (1)：`P_Demo_FB_BA_PIDCtrl.TcPOU`
- **I/O Terminals** (1)：`P_Demo_FB_BA_KL32xx.TcPOU`
- **Trigger** (2)：`P_Demo_FB_BA_ATrigCOV.TcPOU`、`P_Demo_FB_BA_RFTrig.TcPOU`
- **Ramps Filters** (2)：`P_Demo_FB_BA_FltrPT1.TcPOU`、`P_Demo_FB_BA_RampLmt.TcPOU`
- **Hysteresis 2P** (2)：`P_Demo_FB_BA_Swi2P.TcPOU`、`P_Demo_FB_BA_SwiHys2P.TcPOU`
- **Persistent Data** (1)：`P_Demo_FB_BA_PersistentDataHandler.TcPOU`
- **Compare** (1)：`P_Demo_F_BA_CompareVersion.TcPOU`
- **Memory** (7)：`P_Demo_F_BA_ByteCmp.TcPOU`、`P_Demo_F_BA_Cmp.TcPOU` 等
- **ClassValue** (5)：`P_Demo_F_BA_BVal.TcPOU`、`P_Demo_F_BA_RVal.TcPOU` 等
- **Date Check** (5)、**Date Convert** (10)、**Date Time** (9)、**Date Value** (3)、**Scheduler** (1)、**Trend** (2)
- **AuxiliaryCalc** (6)：`P_Demo_F_BA_RemMsTon.TcPOU` 等
- **CheckEnum** (1)、**TcLog** (11)：`P_Demo_F_BA_LogMessage.TcPOU` 至 `P_Demo_F_BA_LogMessage10.TcPOU`
- **Validation** (7)：`P_Demo_F_BA_IsUnitValid.TcPOU` 等
- **GVLs** (3)：`P_Demo_BAComn_Global.TcPOU`、`P_Demo_BAComn_Param.TcPOU`、`P_Demo_BAComn_EnumDE.TcPOU`

详见 [`../README.md`](../README.md) 主索引页（每条目对应一篇 `.md` 文档 + 一份 `.TcPOU` 例程）。

## 调试无端子 / 无硬件时

部分 FB（如 `FB_BA_KL32xx`、`FB_BA_PersistentDataHandler`）正式工作需要硬件 / 文件系统支持。开发期可：

- 手动写 IN_OUT 链接变量来模拟端子上报数据（`FB_BA_KL32xx`）
- 在测试 PC 上跑（持久数据写到 `C:\TwinCAT\3.1\Boot\PLC\Port_<port>.bootdata`，`FB_BA_PersistentDataHandler`）

每个例程的顶部"验证"注释明确列出"无硬件时怎么验"的步骤。
