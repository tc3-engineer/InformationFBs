# Tc2_Math / examples

每个 FB/FC 配套的可导入演示程序，**TwinCAT 3 原生 .TcPOU 格式**（XML / TcPlcObject schema），可直接拖入 XAE 的 PLC `POUs` 文件夹。

## 命名约定

- `P_Demo_<Name>.TcPOU` — 一个 PROGRAM POU，演示该 FB/FC 的最小可运行用法

## 如何导入到 TwinCAT 3 XAE

1. 在 Solution Explorer 里**右键 PLC 项目（`<MyProject> Project` 节点）或其下任一文件夹**
2. 选 **"Add → Existing Item..."**
3. 选中本目录下的 `.TcPOU` 文件
4. 弹窗显示可导入对象（一个 PROGRAM）→ OK
5. POU 出现在树中（顶层或你选的文件夹下，取决于 TwinCAT 设置）

> ⚠️ 一定要**右键 PLC 项目层**（不是 Solution 层、不是 System 层），否则菜单不会出现 "Add → Existing Item"。

## 如何运行验证

1. 编译 PLC 项目（无错误）
2. 把刚导入的 PROGRAM 加到 PlcTask 调用列表（`MAIN` 或新建任务）
   - 或在 `MAIN` 里加一行 `P_Demo_MODABS();`
3. Activate Configuration → 登录 → Run
4. 用在线写值（Write Value）切换输入变量，监视输出变量

每个 .TcPOU 文件顶部的注释列出了该 demo 的具体验证步骤。

## 库依赖

导入前确认 PLC 项目 References 中已添加：
- **`Tc2_Math`**（本库本身）
- 凡演示中出现 `<derived name="X"/>` 的 X 类型所在的库（常见：`Tc2_System`、`Tc2_Standard`）

## 为什么用 .TcPOU 而不是 PLCopenXML

之前版本本仓库给的是 PLCopenXML（IEC 61131-10）格式 `.xml` 文件，需要 XAE 走 **Import PLCopenXML** 向导。改为 TwinCAT 3 原生 `.TcPOU`（XML / `TcPlcObject` schema）后：

- 在 Solution Explorer 中直接 **Add → Existing Item** 或把 `.TcPOU` 拖入 PLC `POUs` 文件夹即可使用；
- 保留 TwinCAT 私有 attribute、`SpecialFunc`、稳定 GUID 等元数据；
- 不再经历 PLCopenXML 子集映射（官方原话：「PLCopenXML defines a subset of the elements known in TwinCAT. 100% compatibility is therefore not ensured.」）。

代价：`.TcPOU` 是 Beckhoff 私有 schema，不能像 PLCopenXML 那样导入 CODESYS / TIA / B&R 等非 Beckhoff IDE。本仓库定位是 TwinCAT 3 文档与例程，原生格式优先。


## 故障排查

| 现象 | 原因 |
|---|---|
| 菜单没有 "Add → Existing Item" | 右键的不是 PLC 项目层 |
| 导入后 POU 不在树里 | 可能在另一个文件夹或顶层；按 Ctrl+F 搜 POU 名 |
| 编译报 "MODABS not defined" | PLC 项目缺 `Tc2_Math` 引用 |
| 导入对话框为空 | XML 格式有问题；用浏览器打开看根节点是否 `<TcPlcObject Version="..." ProductVersion="...">` |
