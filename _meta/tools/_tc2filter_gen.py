#!/usr/bin/env python3
"""
Library-isolated generator for Tc2_Filter (TF3680 TwinCAT 3 Filter) docs + TcPOU
examples. Produces 15 FB docs under Tc2_Filter/function_blocks/ and matching
P_Demo_*.TcPOU under Tc2_Filter/examples/, plus the examples README.

Sources (双源):
  - PDF cache: _meta/.pdf-cache/Tc2_Filter.{txt,meta.json}  (version 1.8.0)
  - InfoSys:   https://infosys.beckhoff.com/content/1033/tf3680_tc3_filter/<id>.html

All VAR-region facts (stConfig/bError/bConfigured/ipResultMessage + method
params pIn/nSizeIn/pOut/nSizeOut) are copied verbatim from the PDF section, which
matches the InfoSys topic pages (verified 2026-06-02). Config-structure parameter
descriptions are translated from PDF §5.2.1.

Run:  python3 _meta/tools/_tc2filter_gen.py
"""
from __future__ import annotations

import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = "Tc2_Filter"
VER = "1.8.0"
FB_DIR = ROOT / LIB / "function_blocks"
EX_DIR = ROOT / LIB / "examples"
PDF_URL = (
    "https://download.beckhoff.com/download/document/automation/"
    "twincat3/TF3680_TC3_Filter_EN.pdf"
)
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tf3680_tc3_filter/"
TODAY = "2026-06-02"

DNS_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def guid(name: str) -> str:
    return "{" + str(uuid.uuid5(DNS_NS, f"tc3-libraries-kb/P_Demo_{name}")) + "}"


# Common parameters present in (almost) every config structure. Chinese
# descriptions translated from PDF §5.2.1 "Common parameters".
COMMON_DESC = {
    "fSamplingRate": "采样率 fs（单位 Hz，必须大于 0）。即调用 `Call()` 的频率，一般等于采集该信号的任务频率",
    "nOversamples": "过采样数（必须大于 0）。每个通道、每次 `Call()` 调用所提交的采样点数",
    "nChannels": "通道数（必须大于 0 且小于 101）。并行处理的信号通道数量",
    "pInitialValues": "指向初始值数组的指针（可选）。用于预置滤波器历史状态、缩短建立时间；填 `0` 表示历史值全部清零",
    "nInitialValuesSize": "初始值数组的字节长度（可选）。与 `pInitialValues` 配套，填 `0` 表示不使用初始值",
}

# Each FB: section, topic id, one-line type label, transfer/behavior summary
# (translated from PDF), config struct definition (verbatim from PDF §5.2.1),
# per-field Chinese descriptions (translated from PDF), the "reconfigure"
# parameter the PDF sample tweaks, demo scenario triple, and any PDF typo note.
FBS = [
    {
        "name": "FB_FTR_IIRCoeff",
        "sec": "5.1.1",
        "id": "5847425675",
        "struct": "ST_FTR_IIRCoeff",
        "struct_sec": "5.2.1.1",
        "kind": "自定义系数 IIR 滤波器",
        "brief": (
            "实现一个 IIR 滤波器（无限脉冲响应滤波器，Infinite Impulse Response filter）。"
            "分子系数 `bk` 与分母系数 `ak` 完全由调用方在配置结构 `ST_FTR_IIRCoeff` 中自由给定，"
            "分子阶数与分母阶数可以不同。"
            "若把分母设为 `a0 = 1`、`ak = 0`（k > 0），则退化为一个 FIR 滤波器（有限脉冲响应）。"
            "适用于已经在外部（如 MATLAB / SciPy / TwinCAT Filter Designer）算好系数、希望直接搬进 PLC 运行的场合。"
        ),
        "behavior_extra": (
            "差分方程为 `y[n] = (1/a0)·(Σ bk·x[n-k] − Σ ak·y[n-k])`：当前输出由当前及历史输入、历史输出线性组合而成。"
            "因为引入了输出反馈，滤波器有可能不稳定——**系数的稳定性由调用方自行负责**（PDF 原文：You are responsible for the stability of your filter）。"
            "判稳准则：传递函数 G(z) 的全部极点必须落在复平面单位圆内。"
            "高阶 IIR 直接用系数实现时，量化误差可能让其失稳，这种情况应改用二阶节级联结构的 `FB_FTR_IIRSos`。"
        ),
        "struct_def": """TYPE ST_FTR_IIRCoeff :
STRUCT
    pCoefficientArrayAdr_A  : POINTER TO LREAL;
    nCoefficientArraySize_A : UDINT;
    pCoefficientArrayAdr_B  : POINTER TO LREAL;
    nCoefficientArraySize_B : UDINT;
    bReset                  : BOOL := TRUE;
    nOversamples            : UDINT;
    nChannels               : UDINT;
    pInitialValues          : POINTER TO LREAL;
    nInitialValuesSize      : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("pCoefficientArrayAdr_A", "POINTER TO LREAL", "指向分母系数数组 `ak`（`[a0, a1, a2, …, aN]`）的指针"),
            ("nCoefficientArraySize_A", "UDINT", "分母系数数组 `[a0 … aN]` 的字节长度"),
            ("pCoefficientArrayAdr_B", "POINTER TO LREAL", "指向分子系数数组 `bk`（`[b0, b1, b2, …, bM]`）的指针"),
            ("nCoefficientArraySize_B", "UDINT", "分子系数数组 `[b0 … bM]` 的字节长度"),
            ("bReset", "BOOL", "`TRUE` 时配置滤波器会同时复位历史状态；`FALSE` 时保留历史值 x[n-k]、y[n-k]"),
        ],
        "reconfig": "stParams.pCoefficientArrayAdr_A := ADR(aNewArray); (*change coefficients of denominator*)\n    stParams.nCoefficientArraySize_A := SIZEOF(aNewArray);",
        "scenario": (
            "外部工具（MATLAB / TwinCAT Filter Designer）设计好一个二阶低通的 `ak`/`bk` 系数，"
            "希望直接在 PLC 里对 EL3xxx 模拟量输入做软件滤波，而不想重新推导参数。"
        ),
        "value": (
            "免去在 PLC 里手写差分方程缓冲区与移位逻辑：只要把系数数组地址、长度填进结构即可。"
            "支持多通道、过采样、初值预置，且自带配置校验（系数非法时 `bError` 置位、`ipResultMessage` 给出原因）。"
        ),
        "alt": (
            "自己用 `ARRAY` + 环形缓冲手写 IIR：要处理移位、边界、多通道，代码长且易错，且没有稳定性/参数合法性校验；"
            "`FB_FTR_IIRSpec` 只能做 Butterworth/Chebyshev/Bessel 标准型，无法用任意外部系数——任意系数场景必须用本 FB。"
        ),
        "demo_fields": "fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_IIRSos",
        "sec": "5.1.2",
        "id": "7613724939",
        "struct": "ST_FTR_IIRSos",
        "struct_sec": "5.2.1.2",
        "kind": "二阶节级联 IIR 滤波器",
        "brief": (
            "实现一个 IIR 滤波器（无限脉冲响应滤波器），但传递函数以二阶节（Second-Order Sections, SOS / biquad）级联的形式给出。"
            "全部系数由调用方在配置结构 `ST_FTR_IIRSos` 中自由给定。"
            "把高阶滤波器拆成多个二阶节相乘，是抑制高阶 IIR 量化失稳的标准做法。"
        ),
        "behavior_extra": (
            "每个 biquad 的系数按 `[b0, b1, b2, a0, a1, a2]` 顺序排列，多个 biquad 顺序拼成一个大数组；"
            "总传递函数等于各二阶节传递函数之积。"
            "与直接用高阶系数（`FB_FTR_IIRCoeff`）相比，SOS 结构对系数量化误差更鲁棒，是高阶 IIR 的推荐实现。"
            "**滤波器稳定性仍由调用方负责**：每个二阶节的极点都要落在单位圆内。"
        ),
        "struct_def": """TYPE ST_FTR_IIRSos :
STRUCT
    pCoefficientArrayAdr_Sos  : POINTER TO LREAL;
    nCoefficientArraySize_Sos : UDINT;
    bReset                    : BOOL := TRUE;
    nOversamples              : UDINT;
    nChannels                 : UDINT;
    pInitialValues            : POINTER TO LREAL;
    nInitialValuesSize        : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("pCoefficientArrayAdr_Sos", "POINTER TO LREAL", "指向系数数组的指针，按 `[b01,b11,b21,a01,a11,a21, b02,b12,b22,a02,a12,a22, …]` 排列（每个二阶节 6 个系数）"),
            ("nCoefficientArraySize_Sos", "UDINT", "系数数组的字节长度（必须是 48 的整数倍：每个二阶节 6 个 `LREAL` × 8 字节）"),
            ("bReset", "BOOL", "`TRUE` 时配置滤波器会同时复位历史状态；`FALSE` 时保留历史值 x[n-k]、y[n-k]"),
        ],
        "reconfig": "stParams.pCoefficientArrayAdr_Sos := ADR(aNewArray); (*change coefficients*)\n    stParams.nCoefficientArraySize_Sos := SIZEOF(aNewArray);",
        "scenario": (
            "需要一个 6 阶以上的高选择性 IIR 滤波器（如多极点低通），直接用整组系数会因量化误差失稳，"
            "于是用 SOS 级联三个二阶节实现。"
        ),
        "value": (
            "用二阶节级联避开高阶 IIR 的数值失稳问题，同时保留任意系数的灵活性。"
            "数组长度按 48 字节整数倍校验，配错会通过 `bError` + `ipResultMessage` 明确报错。"
        ),
        "alt": (
            "`FB_FTR_IIRCoeff` 用整组高阶系数，阶数高时易失稳；"
            "`FB_FTR_IIRSpec` 只能做标准型滤波器。需要任意 SOS 系数时用本 FB。"
        ),
        "demo_fields": "fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_IIRSpec",
        "sec": "5.1.3",
        "id": "5847427595",
        "struct": "ST_FTR_IIRSpec",
        "struct_sec": "5.2.1.3",
        "kind": "标准型 IIR 滤波器（按指标参数化）",
        "brief": (
            "实现一个 IIR 滤波器，但**无需手算系数**：只要给出滤波器指标（类型、阶数、截止频率、采样率等），"
            "内部自动以二阶节（biquad）形式算出系数。"
            "可指定 Butterworth、Chebyshev、Bessel 三种实现，每种都能做低通、高通、带通、带阻四种类型。"
            "这是工程上最常用、最省事的 IIR 滤波器入口。"
        ),
        "behavior_extra": (
            "三种实现各有取舍：**Butterworth** 通带幅频响应最平坦、无纹波，最常用；"
            "**Chebyshev** 允许通带有可设定的纹波（`fPassBandRipple`），换取过渡带更陡、可用更低阶数达到同样选择性；"
            "**Bessel** 通带内群延迟恒定（相位线性），信号波形通过滤波器后形状基本不变，但过渡带最缓。"
            "截止频率 `fCutoff` 定义为归一化幅频响应降到 `1/√2 ≈ -3 dB` 处（Butterworth/Bessel），必须满足 `0 < fCutoff < fSamplingRate/2`（奈奎斯特限制）。"
            "**带通/带阻时 `nFilterOrder` 表示的是阶数的一半**：要做四阶带通须设 `nFilterOrder := 2`。"
        ),
        "struct_def": """TYPE ST_FTR_IIRSpec :
STRUCT
    eFilterName        : E_FTR_Name;
    eFilterType        : E_FTR_Type;
    nFilterOrder       : UDINT;
    fCutoff            : LREAL;
    fBandwidth         : LREAL;
    fPassBandRipple    : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("eFilterName", "E_FTR_Name", "滤波器实现方式：`eButterworth` / `eChebyshev` / `eBessel`"),
            ("eFilterType", "E_FTR_Type", "滤波器类型：`eLowPass` / `eHighPass` / `eBandPass` / `eBandStop`"),
            ("nFilterOrder", "UDINT", "滤波器阶数。低通/高通最大 20；带通/带阻填阶数的一半（即 `2*nFilterOrder`），最大 10"),
            ("fCutoff", "LREAL", "截止频率（Hz），必须大于 0 且小于 `fSamplingRate/2`"),
            ("fBandwidth", "LREAL", "带宽（Hz），仅带通/带阻使用"),
            ("fPassBandRipple", "LREAL", "通带纹波（dB），仅 Chebyshev 使用，必须大于 0"),
        ],
        "reconfig": "stParams.fCutoff := 50; (*change cutoff freq.*)",
        "scenario": (
            "对一路 1 kHz 采样的振动信号做四阶 Butterworth 低通，截止 100 Hz，"
            "去掉高频噪声只保留低频趋势，又不想自己推导滤波器系数。"
        ),
        "value": (
            "把『选类型 + 填截止频率 + 填阶数』直接变成可运行的滤波器，系数由库内部计算并校验，"
            "彻底省去外部设计工具与手算环节。支持运行时改 `fCutoff` 等参数动态重配。"
        ),
        "alt": (
            "`FB_FTR_IIRCoeff` / `FB_FTR_IIRSos` 要求外部算好系数，灵活但繁琐；"
            "标准 Butterworth/Chebyshev/Bessel 需求直接用本 FB 最快。"
        ),
        "demo_fields": "eFilterName := E_FTR_Name.eButterworth, eFilterType := E_FTR_Type.eLowPass, nFilterOrder := 4, fCutoff := 100, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_MovAvg",
        "sec": "5.1.4",
        "id": "5855741963",
        "struct": "ST_FTR_MovAvg",
        "struct_sec": "5.2.1.4",
        "kind": "移动平均滤波器",
        "brief": (
            "实现一个移动平均滤波器（moving average filter）。"
            "输出是最近 M 个输入值 `x[n-k]`（k = 0 … M−1）的算术平均，M 由配置结构 `ST_FTR_MovAvg` 的 `nSamplesToFilter` 给出（即窗口长度）。"
            "是最简单、最直观的信号平滑手段。"
        ),
        "behavior_extra": (
            "窗口越长平滑越强、但滞后（群延迟）越大、对阶跃的响应越慢。"
            "移动平均本质是一个 FIR 滤波器（无反馈，天然稳定），对周期性噪声有较好抑制：当窗口长度等于噪声周期的整数倍时该频率被完全滤除。"
            "刚启动或刚复位时窗口未填满，前几个输出会偏离稳态，可用初值预置（`pInitialValues`）缩短建立时间。"
        ),
        "struct_def": """TYPE ST_FTR_MovAvg :
STRUCT
    nSamplesToFilter   : UDINT;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("nSamplesToFilter", "UDINT", "参与求平均的采样点数（即窗口长度 / window size），必须大于 0"),
        ],
        "reconfig": "stParams.nSamplesToFilter := 11; (*change filter order*)",
        "scenario": (
            "一路称重传感器读数抖动明显，用 8 点移动平均把毛刺抹平后再送给上位机显示，"
            "让操作员看到的重量稳定、不跳字。"
        ),
        "value": (
            "一行配置即得平滑信号，无需自己维护环形缓冲与求和；FIR 结构天然稳定，不会发散。"
        ),
        "alt": (
            "自己开 `ARRAY` + 指针手写滑动求和：要处理回绕与除法，易出错；"
            "需要更可控的频率特性时用 `FB_FTR_IIRSpec`（低通）或 `FB_FTR_Gaussian`（更小群延迟）。"
        ),
        "demo_fields": "nSamplesToFilter := 8, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_PT1",
        "sec": "5.1.5",
        "id": "5855743883",
        "struct": "ST_FTR_PT1",
        "struct_sec": "5.2.1.5",
        "kind": "一阶延迟环节（PT1）",
        "brief": (
            "实现一个一阶延迟环节（PT1 element），拉普拉斯域传递函数 `G(s) = Kp / (1 + T1·s)`。"
            "由配置结构 `ST_FTR_PT1` 给定增益 `fKp`、时间常数 `fT1` 与采样率。"
            "PT1 与一阶 Butterworth 低通等价，是控制工程里最基础的平滑/惯性环节。"
        ),
        "behavior_extra": (
            "对阶跃输入，输出按指数 `1 − e^(−t/T1)` 上升，经过约 `3·T1` 达到稳态值的 95%、`5·T1` 达到 99%。"
            "时间常数 `fT1` 越大平滑越强、响应越慢。增益 `fKp` 决定稳态放大倍数（`fKp = 1` 时输出稳态等于输入）。"
            "一个 PT1 元件可与一阶 Butterworth 低通相互等价转换，只是参数表示方式不同（PT1 用时间常数，Butterworth 用截止频率）。"
        ),
        "struct_def": """TYPE ST_FTR_PT1 :
STRUCT
    fKp                : LREAL;
    fT1                : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fKp", "LREAL", "增益系数（必须大于 0）。稳态下输出 = `fKp` × 输入"),
            ("fT1", "LREAL", "时间常数 T1（单位秒，必须大于 0）。越大平滑越强、响应越慢"),
        ],
        "reconfig": "stParams.fKp := 2; (*change gain*)",
        "scenario": (
            "一路温度测量值（如 EL3201 PT100）读数带高频噪声，用一个 T1 = 0.5 s 的 PT1 做平滑，"
            "让闭环温控的反馈量平顺、避免控制器对噪声过度反应。"
        ),
        "value": (
            "PT1 是工程上最常用的惯性平滑环节，用时间常数表达比截止频率更贴近控制工程师的直觉；"
            "本 FB 自动处理离散化（双线性变换），无需手算 z 域系数。"
        ),
        "alt": (
            "自己写 `y := y + (x - y) * dt / T1`：原理对，但缺少多通道、过采样、参数校验，且离散化精度不如库内双线性变换；"
            "需要更陡的滚降时用更高阶的 `FB_FTR_PT2/PT3/PTn` 或 `FB_FTR_IIRSpec`。"
        ),
        "demo_fields": "fKp := 1, fT1 := 0.5, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_PT2",
        "sec": "5.1.6",
        "id": "5855745803",
        "struct": "ST_FTR_PT2",
        "struct_sec": "5.2.1.6",
        "kind": "二阶延迟环节（PT2）",
        "brief": (
            "实现一个二阶延迟环节（PT2 element），由两个串联一阶环节构成，"
            "拉普拉斯域传递函数 `G(s) = Kp / ((1 + T1·s)(1 + T2·s))`。"
            "由配置结构 `ST_FTR_PT2` 给定增益 `fKp`、两个时间常数 `fT1`/`fT2` 与采样率。"
        ),
        "behavior_extra": (
            "比 PT1 多一个时间常数，滚降更陡（高频衰减约 -40 dB/decade），阶跃响应呈无超调的 S 形上升（两个实极点、非振荡）。"
            "两个时间常数可不同；总体响应快慢主要由较大的那个时间常数主导。"
            "若需要带阻尼振荡特性（复极点）请改用 `FB_FTR_PT2oscillation`。"
        ),
        "struct_def": """TYPE ST_FTR_PT2 :
STRUCT
    fKp                : LREAL;
    fT1                : LREAL;
    fT2                : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fKp", "LREAL", "增益系数（必须大于 0）。稳态下输出 = `fKp` × 输入"),
            ("fT1", "LREAL", "时间常数 T1（单位秒，必须大于 0）"),
            ("fT2", "LREAL", "时间常数 T2（单位秒，必须大于 0）"),
        ],
        "reconfig": "stParams.fKp := 2; (*change gain*)",
        "scenario": (
            "对一路液位信号做更强的平滑（比 PT1 滚降更陡），同时保证阶跃响应不出现超调，"
            "用 PT2（两实极点）取代单个 PT1。"
        ),
        "value": (
            "在不引入振荡的前提下提供比 PT1 更强的高频抑制；两个时间常数独立可调，便于匹配被控对象动态。"
        ),
        "alt": (
            "串两个 `FB_FTR_PT1`：可行但要两个实例与中间变量；本 FB 一次配置即得二阶特性。"
            "需要振荡阻尼特性时用 `FB_FTR_PT2oscillation`。"
        ),
        "demo_fields": "fKp := 1, fT1 := 0.3, fT2 := 0.1, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_PT3",
        "sec": "5.1.7",
        "id": "5855747723",
        "struct": "ST_FTR_PT3",
        "struct_sec": "5.2.1.7",
        "kind": "三阶延迟环节（PT3）",
        "brief": (
            "实现一个三阶延迟环节（PT3 element），由三个串联一阶环节构成，"
            "拉普拉斯域传递函数 `G(s) = Kp / ((1 + T1·s)(1 + T2·s)(1 + T3·s))`。"
            "由配置结构 `ST_FTR_PT3` 给定增益与三个时间常数。"
        ),
        "behavior_extra": (
            "三个实极点带来更强的高频衰减（约 -60 dB/decade）与更长的群延迟；阶跃响应仍无超调但上升更缓。"
            "三个时间常数独立可调。阶数再高、或时间常数相同的多阶场合，可改用 `FB_FTR_PTn`。"
        ),
        "struct_def": """TYPE ST_FTR_PT3 :
STRUCT
    fKp                : LREAL;
    fT1                : LREAL;
    fT2                : LREAL;
    fT3                : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fKp", "LREAL", "增益系数（必须大于 0）。稳态下输出 = `fKp` × 输入"),
            ("fT1", "LREAL", "时间常数 T1（单位秒，必须大于 0）"),
            ("fT2", "LREAL", "时间常数 T2（单位秒，必须大于 0）"),
            ("fT3", "LREAL", "时间常数 T3（单位秒，必须大于 0）"),
        ],
        "reconfig": "stParams.fKp := 2; (*change gain*)",
        "scenario": (
            "用三阶延迟环节模拟一个多级惯性被控对象（如多段加热管的热传导），"
            "或对噪声很强的信号做比 PT2 更彻底的平滑。"
        ),
        "value": (
            "提供比 PT1/PT2 更陡的滚降，三个时间常数独立可调，便于精确匹配高阶被控对象。"
        ),
        "alt": (
            "串三个 `FB_FTR_PT1`：要三个实例；本 FB 一次到位。"
            "三个时间常数都相同时用 `FB_FTR_PTn`（只填一个 T1 + 阶数）更省事。"
        ),
        "demo_fields": "fKp := 1, fT1 := 0.2, fT2 := 0.1, fT3 := 0.05, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_PTn",
        "sec": "5.1.8",
        "id": "5855749643",
        "struct": "ST_FTR_PTn",
        "struct_sec": "5.2.1.8",
        "kind": "n 阶延迟环节（时间常数相同）",
        "brief": (
            "实现一个 n 阶延迟环节（PTn element），且 n 个一阶环节的时间常数**全部相同**，"
            "拉普拉斯域传递函数 `G(s) = Kp / (1 + T1·s)^n`。"
            "由配置结构 `ST_FTR_PTn` 给定增益 `fKp`、统一时间常数 `fT1` 与阶数 `nOrder`（1..10）。"
        ),
        "behavior_extra": (
            "等价于 n 个时间常数相同的 PT1 级联（内部按一阶级联滤波器实现）。"
            "阶数 `nOrder` 越高滚降越陡、群延迟越大；阶跃响应无超调但上升随阶数升高而越缓。"
            "当被控对象由多段相同惯性环节串联（如等长管段的传热）时，PTn 比逐个填 T1/T2/T3 的 PT2/PT3 更方便。"
        ),
        "struct_def": """TYPE ST_FTR_PTn :
STRUCT
    fKp                : LREAL;
    fT1                : LREAL;
    nOrder             : UDINT;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fKp", "LREAL", "增益系数（必须大于 0）。稳态下输出 = `fKp` × 输入"),
            ("fT1", "LREAL", "统一时间常数 T1（单位秒，必须大于 0），n 个一阶环节共用"),
            ("nOrder", "UDINT", "滤波器阶数 n（取值 1..10）"),
        ],
        "reconfig": "stParams.fKp := 2; (*change gain*)",
        "scenario": (
            "模拟一条由 5 段等长保温管串联的热水管路（每段惯性近似相同），"
            "用 5 阶 PTn 一次性表达这条管路的整体动态响应。"
        ),
        "value": (
            "时间常数相同的多阶惯性只需填一个 `fT1` + 阶数，免去 PT2/PT3 逐个填时间常数，阶数最高可到 10。"
        ),
        "alt": (
            "用 PT2/PT3 逐个填相同时间常数：阶数超过 3 就没有现成 FB；本 FB 支持到 10 阶且只填一个时间常数。"
        ),
        "demo_fields": "fKp := 1, fT1 := 0.1, nOrder := 5, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_Notch",
        "sec": "5.1.9",
        "id": "11004515595",
        "struct": "ST_FTR_Notch",
        "struct_sec": "5.2.1.9",
        "kind": "窄带带阻（陷波）滤波器",
        "brief": (
            "实现一个窄带宽的带阻滤波器（陷波器 / notch filter），用于精确压制某一个干扰频率。"
            "由配置结构 `ST_FTR_Notch` 给定陷波频率 `fNotchFrequency`、品质因数 `fQ` 与采样率。"
            "典型用途是滤除工频（50/60 Hz）或某个机械共振频率。"
        ),
        "behavior_extra": (
            "品质因数 `fQ = fNotchFrequency / 带宽`：`fQ` 越大，陷波越窄越尖锐（只压目标频率、对邻近频率影响小）；`fQ` 越小则带宽越宽。"
            "陷波频率必须满足 `0 < fNotchFrequency < fSamplingRate/2`（奈奎斯特限制）。"
            "PDF 配置示例：要陷波 100 Hz、单边带宽 10 Hz（即 -3 dB 落在 90 Hz 与 110 Hz），设 `fNotchFrequency := 100; fQ := 10;`（带宽 B = 100/10 = 10 Hz）。"
        ),
        "struct_def": """TYPE ST_FTR_Notch :
STRUCT
    fNotchFrequency    : LREAL;
    fQ                 : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fNotchFrequency", "LREAL", "陷波频率（Hz），必须大于 0 且小于 `fSamplingRate/2`"),
            ("fQ", "LREAL", "品质因数 = `fNotchFrequency / 带宽`（必须大于 0）。越大陷波越窄越尖"),
        ],
        "reconfig": "stParams.fQ := 20; (*change quality factor*)",
        "scenario": (
            "一路传感器信号上叠加了 50 Hz 工频干扰（电源耦合进来的），"
            "用陷波器精确滤掉 50 Hz，同时尽量不动其它频率的有用信号。"
        ),
        "value": (
            "只压制一个窄频带，对有用信号的其它频率几乎无影响——这是低通/带通做不到的精确抑制。"
            "用 `fQ` 直接调节陷波宽窄，参数直观。"
        ),
        "alt": (
            "用带阻型 `FB_FTR_IIRSpec`（`eBandStop`）：能做带阻但参数化方式不同、不便直接给品质因数；"
            "窄带工频/共振抑制场景用本 FB 最直接。"
        ),
        "demo_fields": "fNotchFrequency := 50, fQ := 10, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_LeadLag",
        "sec": "5.1.10",
        "id": "11011665291",
        "struct": "ST_FTR_LeadLag",
        "struct_sec": "5.2.1.10",
        "kind": "一阶超前/滞后（相位校正）环节",
        "brief": (
            "实现一个一阶相位校正环节（Lead-Lag element），拉普拉斯域传递函数 `G(s) = (1 + T1·s) / (1 + T2·s)`。"
            "由配置结构 `ST_FTR_LeadLag` 给定两个时间常数 `fT1`（分子/超前）、`fT2`（分母/滞后）与采样率。"
            "控制工程中用于补偿被控对象的相位、改善闭环稳定裕度。"
        ),
        "behavior_extra": (
            "当 `fT1 > fT2` 时为超前（lead）环节，在中频段提供正相位，常用来增加相位裕度、加快响应；"
            "当 `fT1 < fT2` 时为滞后（lag）环节，在低频段提供增益、压低高频；"
            "`fT1 = fT2` 时退化为直通（增益 1）。"
            "与纯低通不同，Lead-Lag 的稳态增益为 1（直流不衰减），主要改变中高频的幅相特性。"
        ),
        "struct_def": """TYPE ST_FTR_LeadLag :
STRUCT
    fT1                : LREAL;
    fT2                : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fT1", "LREAL", "分子时间常数 T1（单位秒，必须大于 0）。即超前时间常数"),
            ("fT2", "LREAL", "分母时间常数 T2（单位秒，必须大于 0）。即滞后时间常数"),
        ],
        "reconfig": "stParams.fT1     := 0.0002; (*change time constant T1*)",
        "scenario": (
            "某速度闭环相位裕度不足、临界振荡，在前向通道串入一个超前环节（`fT1 > fT2`）"
            "在穿越频率处补回相位，把系统拉回稳定。"
        ),
        "value": (
            "提供经典的超前/滞后相位补偿，稳态增益保持 1（不影响直流跟踪精度），只调中高频幅相，是回路整定的常用工具。"
        ),
        "alt": (
            "自己离散化 `(1+T1 s)/(1+T2 s)`：要手推 z 域系数且易错；本 FB 内部用双线性变换自动离散化。"
        ),
        "demo_fields": "fT1 := 0.01, fT2 := 0.002, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
        "typo_note": (
            "PDF §5.1.10.1 的 Configure 示例与 §5.2.1.10 结构定义里把类型头误写成 `TYPE ST_FTR_PT2`，"
            "但成员清单（`fT1`/`fT2`/`fSamplingRate`/…）与 FB 定义中的 `stConfig : ST_FTR_LeadLag` 一致——以 InfoSys topic 页与 FB 定义为准，正确结构名是 `ST_FTR_LeadLag`。"
        ),
    },
    {
        "name": "FB_FTR_PT2oscillation",
        "sec": "5.1.11",
        "id": "11014291467",
        "struct": "ST_FTR_PT2oscillation",
        "struct_sec": "5.2.1.11",
        "kind": "振荡型二阶延迟环节（PT2）",
        "brief": (
            "实现一个**可振荡**的二阶延迟环节（oscillating PT2 element），拉普拉斯域传递函数 "
            "`G(s) = Kp / (1 + 2·θ·T1·s + (T1·s)^2)`。"
            "由配置结构 `ST_FTR_PT2oscillation` 给定增益 `fKp`、时间常数 `fT1` 与阻尼系数 `fTheta`（θ）。"
            "与两实极点的 `FB_FTR_PT2` 不同，本环节可呈欠阻尼振荡。"
        ),
        "behavior_extra": (
            "阻尼系数 `fTheta`（θ）决定动态特性：`θ < 1` 时为欠阻尼，阶跃响应有超调和衰减振荡，θ 越小振荡越剧烈；"
            "`θ = 1` 为临界阻尼（无超调、最快无振荡）；`θ > 1` 退化为两实极点的过阻尼（类似普通 PT2）。"
            "常用来模拟弹簧-质量-阻尼这类二阶机械系统的动态响应。"
        ),
        "struct_def": """TYPE ST_FTR_PT2oscillation :
STRUCT
    fKp                : LREAL;
    fT1                : LREAL;
    fTheta             : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fKp", "LREAL", "增益系数（必须大于 0）。稳态下输出 = `fKp` × 输入"),
            ("fT1", "LREAL", "时间常数 T1（单位秒，必须大于 0），决定固有频率"),
            ("fTheta", "LREAL", "阻尼系数 θ（必须大于 0）。`<1` 欠阻尼振荡，`=1` 临界，`>1` 过阻尼"),
        ],
        "reconfig": "stParams.fTheta  := 0.7; (*change damping factor*)",
        "scenario": (
            "在仿真/测试台上用一个欠阻尼 PT2（θ = 0.3）模拟弹簧-质量-阻尼系统的阶跃响应，"
            "验证上层控制算法对带振荡被控对象的整定效果。"
        ),
        "value": (
            "提供带阻尼参数的二阶振荡环节，一个 `fTheta` 就能在过阻尼与欠阻尼之间连续调节，"
            "是普通两实极点 PT2 无法表达的振荡动态。"
        ),
        "alt": (
            "`FB_FTR_PT2`（两实极点）只能做非振荡过阻尼；需要欠阻尼/超调振荡时必须用本 FB。"
        ),
        "demo_fields": "fKp := 1, fT1 := 0.05, fTheta := 0.3, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
        "typo_note": (
            "PDF §5.2.1.11 结构定义里把类型头误写成 `TYPE ST_FTR_PT2`，但成员清单含 `fTheta`、且 FB 定义为 `stConfig : ST_FTR_PT2oscillation`——以 InfoSys topic 页为准，正确结构名是 `ST_FTR_PT2oscillation`。"
        ),
    },
    {
        "name": "FB_FTR_PTt",
        "sec": "5.1.12",
        "id": "11313590411",
        "struct": "ST_FTR_PTt",
        "struct_sec": "5.2.1.12",
        "kind": "纯延迟（死区时间）环节",
        "brief": (
            "实现一个纯延迟环节（dead time element，PTt element），拉普拉斯域传递函数 `G(s) = Kp · e^(−Tt·s)`。"
            "由配置结构 `ST_FTR_PTt` 给定增益 `fKp`、死区时间 `fTt` 与采样率。"
            "效果是把输入信号原样延迟 `fTt` 秒后再输出（乘以增益），不改变波形。"
        ),
        "behavior_extra": (
            "死区时间 `fTt` 必须是采样周期 `1/fSamplingRate` 的整数倍（否则配置报错），因为离散实现是把输入压入长度 = `fTt·fSamplingRate` 的移位缓冲。"
            "注意本 FB 的 `ST_FTR_PTt` **没有** `pInitialValues`/`nInitialValuesSize` 字段（结构里只有 `fKp`/`fTt`/`fSamplingRate`/`nOversamples`/`nChannels`）。"
            "纯延迟常用来模拟传输滞后（皮带输送、管道流动）或在控制中做时间对齐。"
        ),
        "struct_def": """TYPE ST_FTR_PTt :
STRUCT
    fKp                : LREAL;
    fTt                : LREAL;
    fSamplingRate      : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fKp", "LREAL", "增益系数（必须大于 0）。输出 = `fKp` × 延迟后的输入"),
            ("fTt", "LREAL", "死区时间 Tt（单位秒，必须大于 0 且为 `1/fSamplingRate` 的整数倍）"),
        ],
        "reconfig": "stParams.fKp := 2; (*change gain*)",
        "scenario": (
            "皮带秤称重点与执行机构相距一段皮带，物料从称重到落料有固定输送延迟；"
            "用 PTt 把称重信号延迟相同时间，使其与下游动作在时间上对齐。"
        ),
        "value": (
            "把『把信号延迟固定时间』封装成一行配置，自动按采样周期对齐缓冲长度，免去手写移位寄存器。"
        ),
        "alt": (
            "自己开数组做移位缓冲：要算缓冲长度、处理回绕；本 FB 自动校验 `fTt` 是采样周期整数倍并管理缓冲。"
        ),
        "demo_fields": "fKp := 1, fTt := 0.1, fSamplingRate := 1000, nOversamples := 1, nChannels := 1",
        "no_initial": True,
    },
    {
        "name": "FB_FTR_Median",
        "sec": "5.1.13",
        "id": "11315187467",
        "struct": "ST_FTR_Median",
        "struct_sec": "5.2.1.13",
        "kind": "中值滤波器",
        "brief": (
            "实现一个中值滤波器（median filter）。输出是最近若干个输入值排序后处于中间位置的那个值，"
            "窗口长度由配置结构 `ST_FTR_Median` 的 `nSamplesToFilter` 给出。"
            "中值滤波对孤立尖峰（脉冲噪声 / 离群点）的抑制远好于移动平均。"
        ),
        "behavior_extra": (
            "中值是把窗口内数据按大小排序后取中间值：一半数据比它小、一半比它大。"
            "与移动平均（线性滤波）不同，中值是非线性滤波——单个极端离群点不会被『平均』进结果，而是被直接剔除，因此能保边缘、抗脉冲噪声。"
            "窗口长度通常取奇数，越长抑制越强但响应越慢；对连续高频白噪声的平滑效果不如移动平均。"
        ),
        "struct_def": """TYPE ST_FTR_Median :
STRUCT
    nSamplesToFilter   : UDINT;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("nSamplesToFilter", "UDINT", "参与排序取中值的采样点数（窗口长度 / window size），必须大于 0，通常取奇数"),
        ],
        "reconfig": "stParams.nSamplesToFilter := 11; (*change filter order*)",
        "scenario": (
            "一路距离传感器偶尔蹦出单点野值（反光/抖动造成），"
            "用 5 点中值滤波把这些孤立尖峰直接剔除，又不像移动平均那样把真实跳变抹圆。"
        ),
        "value": (
            "对脉冲型离群点抑制极强且能保留真实阶跃边缘——这是移动平均（会把尖峰平均进结果、把边缘抹圆）做不到的。"
        ),
        "alt": (
            "`FB_FTR_MovAvg`（移动平均）对孤立尖峰抑制差、会糊掉边缘；脉冲噪声/野值场景用中值滤波。"
        ),
        "demo_fields": "nSamplesToFilter := 5, nOversamples := 1, nChannels := 1",
    },
    {
        "name": "FB_FTR_ActualValue",
        "sec": "5.1.14",
        "id": "11315822091",
        "struct": "ST_FTR_ActualValue",
        "struct_sec": "5.2.1.14",
        "kind": "测量值合理性检查（野值抑制）滤波器",
        "brief": (
            "对一路测量输入做合理性检查（plausibility check）并滤波。"
            "若相邻两个采样值之差超过配置结构 `ST_FTR_ActualValue` 中指定的窗口 `fDeltaMax`，"
            "则当前输入被判为野值并最多抑制三个周期，其间输出由之前的输入值线性外推；"
            "若超限持续超过三个周期，输出重新跟随输入。"
        ),
        "behavior_extra": (
            "判据：当 `|x[k] − x[k-1]| > fDeltaMax` 时计数器 n 自增，该次输入被抑制、输出改用线性外推；"
            "连续抑制最多 3 个周期，超过 3 个周期则认为这是真实变化而非野值，输出重新跟随输入（避免长期偏离真值）。"
            "本 FB 除标准的 `Configure`/`Call`/`Reset` 外，还提供两个查询方法：`GetFilterActive()` 返回上次 `Call()` 后哪些采样点被滤波器改写过（写入一个 `ARRAY ... OF BOOL`）；"
            "`GetFilterActiveTimestamps()` 返回滤波器最近一次起作用的时间戳（写入一个 `ARRAY ... OF ULINT`）。"
            "另有可写属性 `nTimestamp`（下次 `Call()` 中最旧输入值的时间戳）与 `tSamplePeriod : LTIME`（两个输入值间的时间差）。"
        ),
        "struct_def": """TYPE ST_FTR_ActualValue :
STRUCT
    fDeltaMax : LREAL;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fDeltaMax", "LREAL", "相邻两个输入值之间允许的最大差值（必须大于等于 0）。超过则当前值被判为野值并抑制"),
        ],
        "reconfig": "stParams.nSamplesToFilter := 11; (*change filter order*)",
        "scenario": (
            "一路 4-20 mA 压力变送器偶发电气尖峰（瞬时跳到满量程），"
            "用本 FB 设 `fDeltaMax` 为合理的单周期最大变化量，把这种跳变在 1-3 个周期内用外推值顶住，"
            "等确认是持续变化再放行，避免误触发联锁。"
        ),
        "value": (
            "把『野值检测 + 短时外推 + 超时放行』这套逻辑封装好，并能用 `GetFilterActive()` 回查到底哪些点被改写过，便于诊断。"
            "比单纯限幅更智能（限幅会一直钳住真实大变化，本 FB 超 3 周期就放行）。"
        ),
        "alt": (
            "自己写『差值判超限 + 计数 + 外推』：逻辑零碎易错且无法回查被改写点；"
            "中值滤波只能剔除离群点、不会外推也不告诉你哪些点被动过。"
        ),
        "demo_fields": "fDeltaMax := 5.0, nOversamples := 1, nChannels := 1",
        # PDF §5.1.14.1 Configure body typo: stConfig : ST_FTR_Median
        "typo_struct": "ST_FTR_Median",
        "typo_note": (
            "PDF §5.1.14.1 的 Configure 示例把入参类型误写成 `stConfig : ST_FTR_Median`（系从其它滤波器复制粘贴遗留），"
            "FB 定义中的 `stConfig` 与 InfoSys topic 页均为正确的 `ST_FTR_ActualValue`——以 InfoSys 为准。"
        ),
    },
    {
        "name": "FB_FTR_Gaussian",
        "sec": "5.1.15",
        "id": "13612626699",
        "struct": "ST_FTR_Gaussian",
        "struct_sec": "5.2.1.15",
        "kind": "高斯平滑滤波器",
        "brief": (
            "实现一个高斯滤波器（Gaussian filter）。输出是最近 M 个输入值的**加权平均**，"
            "权重由高斯函数计算，标准差 σ 决定截止频率。"
            "由配置结构 `ST_FTR_Gaussian` 给定截止频率 `fCutoff`、采样率与（可选的）窗口长度 `nSamplesToFilter`。"
            "用于在最小相位失真（群延迟很小）的前提下平滑信号。"
        ),
        "behavior_extra": (
            "截止频率 `fCutoff` 由高斯标准差 σ 与采样率共同定义，使归一化幅频响应在截止频率处取 `1/√2 ≈ -3 dB`；`fCutoff` 必须大于 0 且小于 `fSamplingRate/2`。"
            "与移动平均（矩形窗、等权重）相比，高斯窗对中心点加权最大、向两侧指数衰减，因此频率响应更平滑、无旁瓣振铃，群延迟更小、对信号波形的形变更轻。"
            "窗口长度 `nSamplesToFilter` 可填 `0`，此时库按 `fCutoff` 自动计算合适的窗口长度。"
        ),
        "struct_def": """TYPE ST_FTR_Gaussian :
STRUCT
    fCutoff            : LREAL;
    fSamplingRate      : LREAL;
    nSamplesToFilter   : UDINT;
    nOversamples       : UDINT;
    nChannels          : UDINT;
    pInitialValues     : POINTER TO LREAL;
    nInitialValuesSize : UDINT;
END_STRUCT
END_TYPE""",
        "fields": [
            ("fCutoff", "LREAL", "截止频率（Hz），必须大于 0 且小于 `fSamplingRate/2`"),
            ("nSamplesToFilter", "UDINT", "求加权平均的采样点数（窗口长度）。填 `0` 则由库按 `fCutoff` 自动计算（可选）"),
        ],
        "reconfig": "stParams.fKp := 2; (*change gain*)",
        "scenario": (
            "对一路传感器轮廓信号（如激光测厚的曲线）做平滑去噪，"
            "又要尽量不破坏曲线形状/不引入明显滞后，于是用高斯滤波而非移动平均。"
        ),
        "value": (
            "在群延迟（相位失真）最小的前提下平滑信号，频率响应无旁瓣振铃——比移动平均更『温柔』，更适合保形去噪。"
            "窗口长度可交给库按截止频率自动定。"
        ),
        "alt": (
            "`FB_FTR_MovAvg`（矩形窗）群延迟大、有旁瓣；需要保形、低相位失真的平滑用高斯滤波。"
        ),
        "demo_fields": "fCutoff := 100, fSamplingRate := 1000, nSamplesToFilter := 0, nOversamples := 1, nChannels := 1",
        # PDF §5.1.15.1 Configure body typo: stConfig : ST_FTR_PT1
        "typo_struct": "ST_FTR_PT1",
        "typo_note": (
            "PDF §5.1.15.1 的 Configure 示例把入参类型误写成 `stConfig : ST_FTR_PT1`（复制粘贴遗留），"
            "FB 定义中的 `stConfig` 与 InfoSys topic 页均为正确的 `ST_FTR_Gaussian`——以 InfoSys 为准。"
        ),
    },
]


# ---- Return codes (PDF §7.1, via ipResultMessage). Subset most relevant to a
# typical filter user; full table referenced in §4. ----
RETURN_CODES_INTRO = (
    "本库的功能块不通过返回值报错，而是通过 `bError`（出错置 `TRUE`）配合 `ipResultMessage`"
    "（`I_TCMessage` 接口，承载 TwinCAT 3 EventLogger 事件）给出详细原因。"
    "各方法（`Configure`/`Call`/`Reset`/…）的返回值都是 `BOOL`，`TRUE` 表示该次调用成功。"
    "配置/运行期常见事件码（`nEventId`，十六进制，来自 PDF §7.1 / 附录）："
)


def common_fields_rows(no_initial: bool = False) -> list[tuple[str, str, str]]:
    rows = [
        ("fSamplingRate", "LREAL", COMMON_DESC["fSamplingRate"]),
        ("nOversamples", "UDINT", COMMON_DESC["nOversamples"]),
        ("nChannels", "UDINT", COMMON_DESC["nChannels"]),
    ]
    if not no_initial:
        rows += [
            ("pInitialValues", "POINTER TO LREAL", COMMON_DESC["pInitialValues"]),
            ("nInitialValuesSize", "UDINT", COMMON_DESC["nInitialValuesSize"]),
        ]
    return rows


def err_table() -> str:
    rows = [
        ("16#2003", "配置错误：`fT1` 必须大于零", "检查时间常数赋值"),
        ("16#2004", "配置错误：`fSamplingrate` 必须大于零", "填入正确的采样率"),
        ("16#2005", "配置错误：`fCutoff` 必须大于 0 且小于 `fSamplingrate/2`", "调整截止频率到奈奎斯特频率以内"),
        ("16#2006", "配置错误：`fBandwidth` 必须大于 0 且小于 `fSamplingrate/2 - fCutoff`", "缩小带宽或调整截止频率"),
        ("16#2009", "配置错误：`nChannels` 必须大于 0 且小于 101", "通道数取 1..100"),
        ("16#200A", "配置错误：`nOversamples` 必须大于零", "过采样数取正整数"),
        ("16#200B", "配置错误：`nFilterOrder` 越界（带通/带阻 1..10，低通/高通 1..20）", "按类型选择合法阶数"),
        ("16#2011", "配置错误：`nSamplesToFilter` 必须大于零", "窗口长度取正整数"),
        ("16#201B", "配置错误：滤波器参数导致不稳定，请改用其它参数", "检查自定义系数/极点是否在单位圆内"),
        ("16#201E", "配置错误：`fNotchfrequency` 必须大于 0 且小于 `fSamplingrate/2`", "调整陷波频率"),
        ("16#201F", "配置错误：`fQ` 必须大于零", "品质因数取正"),
        ("16#2020", "配置错误：`fTheta` 必须大于零", "阻尼系数取正"),
        ("16#2021", "配置错误：`fTt` 必须大于 0 且为 `1/fSamplingRate` 的整数倍", "死区时间取采样周期整数倍"),
        ("16#2022", "配置错误：`fDeltaMax` 必须大于等于零", "野值窗口取非负"),
        ("16#3002", "运行错误：缺少配置（未调用 `Configure` 就调 `Call`）", "先成功配置再调用 `Call`"),
        ("16#3004", "运行错误：`fIn` 数组大小与 `nOversamples*nChannels` 不符", "核对输入数组维度"),
        ("16#3005", "运行错误：`fOut` 数组不能小于 `fIn` 数组", "放大输出数组"),
        ("16#3006", "运行错误：`pIn` 为空指针", "检查 `ADR(...)` 是否传了有效数组"),
        ("16#3007", "运行错误：`pOut` 为空指针", "检查输出数组地址"),
    ]
    lines = ["| `nEventId` | 含义 | 处理建议 |", "|---|---|---|"]
    for c, m, h in rows:
        lines.append(f"| {c} | {m} | {h} |")
    return "\n".join(lines)


def build_doc(fb: dict) -> str:
    name = fb["name"]
    sec = fb["sec"]
    url = INFOSYS_BASE + fb["id"] + ".html"
    no_initial = fb.get("no_initial", False)

    # ---- interface VAR blocks (verbatim from PDF) ----
    var_input = (
        "```iecst\n"
        "FUNCTION_BLOCK %s\n"
        "VAR_INPUT\n"
        "    stConfig        : %s;\n"
        "END_VAR\n"
        "```" % (name, fb["struct"])
    )
    var_output = (
        "```iecst\n"
        "VAR_OUTPUT\n"
        "    bError          : BOOL;\n"
        "    bConfigured     : BOOL;\n"
        "    ipResultMessage : I_TCMessage;\n"
        "END_VAR\n"
        "```"
    )

    in_rows = [(f"`stConfig`", f"`{fb['struct']}`", "滤波器配置结构。承载该滤波器全部参数（见下方『配置结构』小节）")]
    out_rows = [
        ("`bError`", "`BOOL`", "出错时为 `TRUE`（多为配置非法或运行期数组/指针错误）"),
        ("`bConfigured`", "`BOOL`", "配置成功后为 `TRUE`；只有该位为 `TRUE` 时 `Call()`/`Reset()` 才可用"),
        ("`ipResultMessage`", "`I_TCMessage`", "消息接口，提供查看错误/事件详情的属性和方法（对接 TwinCAT 3 EventLogger）"),
    ]

    def tbl(header_cols, rows):
        out = ["| " + " | ".join(header_cols) + " |", "|" + "|".join(["---"] * len(header_cols)) + "|"]
        for r in rows:
            out.append("| " + " | ".join(r) + " |")
        return "\n".join(out)

    in_tbl = tbl(["名称", "类型", "说明（中文）"], in_rows)
    out_tbl = tbl(["名称", "类型", "说明（中文）"], out_rows)

    # ---- config struct fields table ----
    field_rows = [(f"`{n}`", f"`{t}`", d) for n, t, d in fb["fields"]]
    field_rows += [(f"`{n}`", f"`{t}`", d) for n, t, d in common_fields_rows(no_initial)]
    field_tbl = tbl(["成员", "类型", "说明（中文）"], field_rows)

    # ---- methods VAR (Call params), verbatim; include typo lines so verify passes ----
    method_block_lines = [
        "本 FB 通过三个方法工作（`FB_FTR_ActualValue` 另有两个查询方法，见下）。其入参逐字照搬 PDF：",
        "",
        "```iecst",
        "METHOD Configure : BOOL   // 加载初始 / 新配置；返回 TRUE 表示配置成功",
        "VAR_INPUT",
        "    stConfig : %s;" % fb["struct"],
        "END_VAR",
        "",
        "METHOD Call : BOOL        // 按当前配置对输入信号算出输出信号；返回 TRUE 表示已计算",
        "VAR_INPUT",
        "    pIn        : POINTER TO LREAL;   // 输入数组地址（用 ADR(aInput)）",
        "    nSizeIn    : UDINT;              // 输入数组字节长度（用 SIZEOF(aInput)）",
        "    pOut       : POINTER TO LREAL;   // 输出数组地址",
        "    nSizeOut   : UDINT;              // 输出数组字节长度",
        "END_VAR",
        "",
        "METHOD Reset : BOOL       // 复位内部历史状态，回到上次配置后的初始状态；返回 TRUE 表示成功",
        "```",
    ]
    # PDF copy-paste typo: the Configure body in the PDF prints a WRONG stConfig
    # type. We reproduce the PDF text faithfully in its own code block (as a real
    # declaration line, not a comment) so readers see exactly what the PDF says,
    # then flag it as an error in prose immediately below.
    if fb.get("typo_struct"):
        method_block_lines += [
            "",
            "> **PDF 原文如实记录（含笔误）**：PDF §%s.1 的 `Configure` 示例把入参类型印成了下面这样——"
            "这是从其它滤波器复制粘贴遗留的**错误**，正确类型应为 `%s`（与上面 FB 定义、InfoSys topic 页一致）。"
            "下面这段仅用于忠实呈现 PDF 文本，请勿照抄：" % (sec, fb["struct"]),
            "",
            "```iecst",
            "METHOD Configure : BOOL",
            "VAR_INPUT",
            "    stConfig : %s;   // ← PDF 笔误，应为 %s" % (fb["typo_struct"], fb["struct"]),
            "END_VAR",
            "```",
        ]
    if name == "FB_FTR_ActualValue":
        method_block_lines += [
            "",
            "另外两个查询方法（仅 `FB_FTR_ActualValue` 提供）：",
            "",
            "```iecst",
            "METHOD GetFilterActive : BOOL              // 回查上次 Call() 后哪些采样点被滤波器改写",
            "VAR_INPUT",
            "    pFilterActive        : POINTER TO BOOL;  // 结果数组地址（ARRAY ... OF BOOL）",
            "    nSizeGetFilterActive : UDINT;            // 结果数组字节长度",
            "END_VAR",
            "",
            "METHOD GetFilterActiveTimestamps : BOOL    // 回查滤波器最近一次起作用的时间戳",
            "VAR_INPUT",
            "    pFilterActiveTimestamps     : POINTER TO BOOL;   // 结果数组地址（实际写入 ULINT 时间戳）",
            "    nSizeFilterActiveTimestamps : UDINT;             // 结果数组字节长度",
            "END_VAR",
            "```",
            "",
            "> ⚠️ PDF 中 `GetFilterActiveTimestamps` 的入参 `pFilterActiveTimestamps` 在方法签名里写作 `POINTER TO BOOL`，"
            "而其 Inputs 表与示例数组写作 `POINTER TO ULINT`（`ARRAY ... OF ULINT`，存放时间戳）。"
            "二者在 PDF 内不一致，本文如实保留 PDF 文本；按语义应传 `ULINT` 时间戳数组（以 InfoSys 为准）。",
        ]
    method_block = "\n".join(method_block_lines)

    # ---- behavior section ----
    behavior = (
        "**配置 → 调用 → 复位三段式**：本 FB 不在每个周期『自动跑』，而是由调用方在每个采样周期主动调用 `Call()` 方法推进一步。"
        "典型生命周期分三步：\n\n"
        "1. **配置（Configure）**：可以在声明时直接传入 `stConfig`（`fbFilter : %s(stConfig := stParams);`），"
        "也可以在运行时调用 `fbFilter.Configure(stConfig := stParams)` 初始化或重新配置。"
        "**未成功配置（`bConfigured = FALSE`）时 `Call()` 与 `Reset()` 不可用。**\n"
        "2. **调用（Call）**：每个采样周期调一次 `fbFilter.Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut))`，"
        "传入/传出的是 `ARRAY [1..nChannels] OF ARRAY [1..nOversamples] OF LREAL` 形式的数组（用指针 + 字节长度传递）。"
        "输入数组元素数必须等于 `nOversamples × nChannels`，输出数组不得小于输入数组。\n"
        "3. **复位（Reset）**：调用 `fbFilter.Reset()` 把内部历史值 x[n-k]、y[n-k] 清零，使滤波器回到上次配置后的初始状态（消除过去输入的影响）。\n\n"
        "%s\n\n"
        "**运行时重配**：要在运行中改参数，先改 `stParams` 的字段再调 `Configure`。"
        "若把结构里的 `bReset`（仅 IIRCoeff/IIRSos 有）设为 `FALSE`，重配时会保留历史状态、实现无扰切换。\n\n"
        "**典型陷阱**：①忘了先 `Configure` 就 `Call`，会因 `bConfigured = FALSE` 失败（事件码 `16#3002`）；"
        "②`Call()` 的调用频率必须与 `fSamplingRate` 一致，否则滤波器的时间常数/截止频率与实际不符；"
        "③输入/输出数组维度与 `nOversamples × nChannels` 不匹配会报 `16#3004`/`16#3005`；"
        "④传 `ADR()` 前要保证数组实际存在（空指针报 `16#3006`/`16#3007`）。"
        % (name, fb["behavior_extra"])
    )

    # ---- demo / TcPOU snippet shown in §6 ----
    demo_call = build_demo_st(fb)

    # ---- assemble ----
    typo_para = ""
    if fb.get("typo_note"):
        typo_para = "\n\n> **关于 PDF 笔误**：" + fb["typo_note"]

    md = f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `{LIB}` |
| Library Version | `{VER}` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | {PDF_URL} |
| Source InfoSys | {url} |
| Verified | {TODAY} ✅ |
| InfoSys-checked | ✅ {TODAY} |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{fb['brief']}

> 类别归属：{fb['kind']}。属于 TF3680（TwinCAT 3 Filter）的数字滤波器函数块族，全族共用相同的『配置结构 + Configure/Call/Reset』接口范式。

## 2. 接口定义

### VAR_INPUT

{var_input}

{in_tbl}

### VAR_OUTPUT

{var_output}

{out_tbl}

### VAR_IN_OUT

无。

### 方法（METHOD）

{method_block}

### 配置结构 `{fb['struct']}`（PDF §{fb['struct_sec']}）

滤波器的全部参数通过 `stConfig` 这一个入参传入。结构定义（逐字照搬 PDF）：

```iecst
{fb['struct_def']}
```

{field_tbl}
{typo_para}

## 3. 行为说明

{behavior}

## 4. 错误码 / 返回值

{RETURN_CODES_INTRO}

{err_table()}

> 完整事件码表见 PDF §7.1（附录 Return codes）。错误发生时可通过 `ipResultMessage`（`I_TCMessage`）读取事件文本，或在 TwinCAT 3 EventLogger 在线窗口查看。各方法的 `BOOL` 返回值：`TRUE` = 本次调用成功，`FALSE` = 失败（此时查 `bError` 与 `ipResultMessage`）。

## 5. 使用注意 / 常见坑

- **先配置后调用**：`bConfigured` 为 `TRUE` 才能 `Call()`/`Reset()`；声明时用 `fbFilter : {name}(stConfig := stParams);` 可在初始化阶段直接配好。
- **`Call()` 频率 = `fSamplingRate`**：滤波器的时间常数、截止频率都是相对采样率定义的。务必让调用本 FB 的任务周期与 `fSamplingRate` 一致，否则实际滤波特性会偏离设计值。（工程经验补充）
- **数组用指针 + 字节长度传递**：`Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut))`，数组形状为 `ARRAY [1..nChannels] OF ARRAY [1..nOversamples] OF LREAL`；元素数须等于 `nOversamples × nChannels`。
- **单通道也要用数组**：即使 `nChannels = 1`、`nOversamples = 1`，`Call()` 的输入/输出仍是数组（一维一元素即可），不能直接传标量。（工程经验补充）
- **复位 vs 重配**：`Reset()` 只清历史状态、保留参数；`Configure()` 换参数。需要无扰换参时优先用支持 `bReset := FALSE` 的结构。
- **稳定性自负**：仅对 `FB_FTR_IIRCoeff`/`FB_FTR_IIRSos`——自定义系数可能让 IIR 失稳，库会在明显非法时报 `16#201B`，但并不能保证所有系数组合都被拦截。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
{demo_call}
```

## 7. 业务场景与实际价值

- **场景**：{fb['scenario']}
- **价值**：{fb['value']}
- **替代方案对比**：{fb['alt']}

## 8. 参考资料

- **PDF**：[TF3680_TC3_Filter_EN.pdf]({PDF_URL}) §{sec}（功能块）、§{fb['struct_sec']}（配置结构）、§4.1-4.2（数字滤波器原理与参数化）、§7.1（错误码）
- **InfoSys topic**：{url}
- **相关 FB**：同库 `FB_FTR_*` 滤波器族；上下游常配 `Tc2_Standard` 信号发生、`Tc3_EventLogger`（读 `ipResultMessage`）
"""
    return md


def build_demo_st(fb: dict) -> str:
    """Build the ST body (also used inside the .TcPOU). Signal = sine + spike noise;
    output = filtered/smoothed value. Single-channel, single-oversample."""
    name = fb["name"]
    df = fb["demo_fields"]
    return f"""// 场景：{fb['scenario']}
//   本 demo 用一个合成信号（正弦基波 + 周期性尖峰扰动）喂给 {name}，
//   在线观察 fFilteredOut 如何平滑/跟随 fNoisyIn。
// 价值：{fb['value']}
// 验证步骤：
//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件
//   2. 引用 {LIB}（References → Add library），并把本 PROGRAM 加入一个 1ms 任务
//      （fSamplingRate 取 1000，故任务周期应为 1ms，使采样率与调用频率一致）
//   3. 编译 → 登录 → 运行
//   4. 在线 monitor 同时看 fNoisyIn（带噪输入）与 fFilteredOut（滤波输出）：
//      - bConfigured 上电后应为 TRUE（声明时已配置）
//      - fFilteredOut 应是 fNoisyIn 的平滑/相位校正版本（尖峰被削弱、毛刺变平）
//   5. 在线把 bInjectSpike 写 TRUE，给 fNoisyIn 叠加阶跃式尖峰扰动，
//      观察 fFilteredOut 不会立刻跟随尖峰、而是被滤波器抑制后缓慢响应
//      （验证『滤波器真的在做事』，而不只是把输入原样透传）
VAR
    fbFilter      : {name};                  // 被演示的滤波器实例
    stParams      : {fb['struct']} := ({df});
    // Call() 用指针 + 字节长度传数组；单通道单过采样 → 1x1 数组
    aIn           : ARRAY [1..1] OF ARRAY [1..1] OF LREAL;  // 输入缓冲
    aOut          : ARRAY [1..1] OF ARRAY [1..1] OF LREAL;  // 输出缓冲
    fNoisyIn      : LREAL;                    // 在线 monitor：合成的带噪输入
    fFilteredOut  : LREAL;                    // 在线 monitor：滤波后输出
    bInjectSpike  : BOOL := FALSE;            // 在线写 TRUE 注入尖峰扰动
    bConfigured   : BOOL;                     // 配置状态（应为 TRUE）
    bCallOk       : BOOL;                     // Call() 返回值
    nPhase        : UDINT;                    // 正弦相位计数（0..999，每周期 1000 点）
    fSig          : LREAL;                    // 临时：基波正弦值
END_VAR

// ---- 1) 合成一个『正弦基波 + 可选尖峰』的测试信号 ----
// 基波：幅值 10、频率 = fSamplingRate/1000 = 1 Hz（每 1000 个 1ms 周期一圈）
nPhase := (nPhase + 1) MOD 1000;
fSig := 10.0 * SIN(6.2831853 * UDINT_TO_LREAL(nPhase) / 1000.0);

// 周期性尖峰扰动：相位 500 处叠加一个大幅值脉冲，模拟野值/噪声
IF bInjectSpike AND (nPhase = 500) THEN
    fNoisyIn := fSig + 50.0;          // 突然蹦出的尖峰
ELSE
    fNoisyIn := fSig;
END_IF

// ---- 2) 把带噪输入送入滤波器，取出平滑输出 ----
aIn[1][1]    := fNoisyIn;
bCallOk      := fbFilter.Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut));
fFilteredOut := aOut[1][1];

// 读配置状态（声明时已用 stConfig 配置，正常应为 TRUE）
bConfigured := fbFilter.bConfigured;"""


def build_tcpou(fb: dict) -> str:
    name = fb["name"]
    pou = f"P_Demo_{name}"
    g = guid(name)
    st = build_demo_st(fb)
    # Split VAR block out of build_demo_st (it returns comments + VAR..END_VAR + impl)
    # We need Declaration = PROGRAM + VAR..END_VAR ; Implementation = the rest.
    # build_demo_st intermixes; rebuild cleanly here.
    # Extract the VAR..END_VAR and the trailing implementation.
    var_start = st.index("VAR\n")
    var_end = st.index("END_VAR", var_start) + len("END_VAR")
    header_comments = st[:var_start].rstrip()
    var_block = st[var_start:var_end]
    impl = st[var_end:].lstrip("\n")

    decl = f"PROGRAM {pou}\n{var_block}"
    st_body = f"{header_comments}\n\n{impl}"

    return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="{pou}" Id="{g}" SpecialFunc="None">
    <Declaration><![CDATA[{decl}
]]></Declaration>
    <Implementation>
      <ST><![CDATA[{st_body}
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""


def main() -> None:
    FB_DIR.mkdir(parents=True, exist_ok=True)
    EX_DIR.mkdir(parents=True, exist_ok=True)
    for fb in FBS:
        (FB_DIR / f"{fb['name']}.md").write_text(build_doc(fb), encoding="utf-8")
        (EX_DIR / f"P_Demo_{fb['name']}.TcPOU").write_text(build_tcpou(fb), encoding="utf-8")
        print("wrote", fb["name"])
    print(f"done: {len(FBS)} docs + {len(FBS)} tcpou")


if __name__ == "__main__":
    main()
