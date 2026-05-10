# Tc2_Math / examples

每个 FB/FC 配套的可导入演示程序，**PLCopenXML 格式（IEC 61131-10）**，单文件、跨 IDE。

## 命名约定

- `P_Demo_<Name>.xml` — 一个 PROGRAM POU，演示该 FB/FC 的最小可运行用法

## 如何导入到 TwinCAT 3 XAE

1. 在 Solution Explorer 里**右键 PLC 项目（`<MyProject> Project` 节点）或其下任一文件夹**
2. 选 **"Import PLCopenXML..."**
3. 选中本目录下的 `.xml` 文件
4. 弹窗显示可导入对象（一个 PROGRAM）→ OK
5. POU 出现在树中（顶层或你选的文件夹下，取决于 TwinCAT 设置）

> ⚠️ 一定要**右键 PLC 项目层**（不是 Solution 层、不是 System 层），否则菜单不会出现 "Import PLCopenXML"。

## 如何运行验证

1. 编译 PLC 项目（无错误）
2. 把刚导入的 PROGRAM 加到 PlcTask 调用列表（`MAIN` 或新建任务）
   - 或在 `MAIN` 里加一行 `P_Demo_MODABS();`
3. Activate Configuration → 登录 → Run
4. 用在线写值（Write Value）切换输入变量，监视输出变量

每个 .xml 文件顶部的注释列出了该 demo 的具体验证步骤。

## 库依赖

导入前确认 PLC 项目 References 中已添加：
- **`Tc2_Math`**（本库本身）
- 凡演示中出现 `<derived name="X"/>` 的 X 类型所在的库（常见：`Tc2_System`、`Tc2_Standard`）

## 跨 IDE 兼容性

PLCopenXML 是 IEC 61131-10 标准，理论上可在 CODESYS / Siemens TIA / B&R Automation Studio 等导入。但官方文档明确：
> "PLCopenXML defines a subset of the elements known in TwinCAT. 100% compatibility is therefore not ensured."

实测注意事项：
- TwinCAT 私有 attribute（如 `{attribute 'displaymode'}`）会丢失
- 引用 `Tc2_Math` 等 TwinCAT 内置/附加库的 derived 类型不可移植到非 Beckhoff IDE
- 引用其他附加库时，导入前必须先在目标项目中已添加该库引用，否则 derived 类型解析失败

## 故障排查

| 现象 | 原因 |
|---|---|
| 菜单没有 "Import PLCopenXML" | 右键的不是 PLC 项目层 |
| 导入后 POU 不在树里 | 可能在另一个文件夹或顶层；按 Ctrl+F 搜 POU 名 |
| 编译报 "MODABS not defined" | PLC 项目缺 `Tc2_Math` 引用 |
| 导入对话框为空 | XML 格式有问题；用浏览器打开看根节点是否 `<project xmlns="http://www.plcopen.org/xml/tc6_0200">` |
