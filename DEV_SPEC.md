<!-- Dev specification for Interview Knowledge System. -->
# Developer Specification (DEV_SPEC)

> 版本：0.3 — 开发规范文档
> 最后更新：2026-06-09

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 核心特点](#2-核心特点)
- [3. 技术选型](#3-技术选型)
- [4. 测试方案](#4-测试方案)
- [5. 系统架构与模块设计](#5-系统架构与模块设计)
- [6. 项目排期](#6-项目排期)
- [7. 可扩展性与未来展望](#7-可扩展性与未来展望)
- [8. 各模块详细规格](#8-各模块详细规格)
- [9. Skill 文件结构](#9-skill-文件结构)
- [10. 附录](#10-附录)

---

## 1. 项目概述

### 1.1 目标

构建一个面向**面试八股知识**的个人学习管理系统，帮助用户将搜集来的零散面经、笔记、PDF 等材料，系统性地转化为**结构化的知识网络**，并通过科学的学习-复习-模拟面试闭环，实现高效记忆与深度理解。

### 1.2 设计理念

> **核心定位：你的私人面试八股教练**
>
> 面试八股不是死记硬背，而是**建立概念之间的关联网络**。本系统不替代你的学习过程，而是通过结构化的知识管理 + 智能调度 + 模拟面试，让你的每一分学习时间都花在刀刃上。

#### 1️⃣ 知识网络化 (Knowledge as a Network)

将零散的知识点转化为相互关联的概念网络：
- **笔记 ↔ Q&A 双向关联**：每个知识点既有概念笔记，又有对应的面试问答
- **领域分层**：按技术领域（Java、OS、Network 等）和频率（必问/常问/冷门）组织
- **wiki-links 硬关联**：Obsidian 原生链接，可视化知识图谱

#### 2️⃣ 学习闭环 (Learn-Review-Interview Loop)

覆盖完整的学习生命周期：
- **注入 (Ingest)**：将外部材料（PDF、Word、Markdown、粘贴文本）自动分类、去重、结构化
- **学习 (Learn)**：首次接触新概念，自评掌握程度，初始化复习计划
- **复习 (Review)**：基于 SM-2 算法的间隔复习，支持多种交互模式（快速/深度/模拟面试）
- **面板 (Dashboard)**：进度可视化、薄弱分析、管理操作

#### 3️⃣ 渐进式增强 (Progressive Enhancement)

从最简单的文件管理开始，逐步叠加智能功能：
- **P0**：基础文件结构 + SM-2 复习
- **P1**：AI 辅助评估 + 多模式交互
- **P2**：可视化面板 + 薄弱分析
- **P3**：Agent 化 + MCP 生态集成

#### 4️⃣ 个人优先，开源共享 (Local-First, Open Source)

- **数据主权**：所有数据以 Markdown/JSON 文件形式存储在本地，用户完全拥有
- **Obsidian 原生**：充分利用 Obsidian 的链接、图谱、Dataview 等生态
- **开源**：代码与 Skill 定义开源，方便他人参考与扩展

### 1.3 核心价值主张

| 痛点 | 解决方案 |
|------|---------|
| 面经零散，难以系统管理 | 统一 Vault 结构，自动分类存储 |
| 学了就忘，缺乏科学复习 | SM-2 间隔重复，动态调整周期 |
| 不知道自己哪里薄弱 | 概念级追踪 + 错误笔记 + 薄弱分析 |
| 面试前没有实战演练 | 模拟面试模式，AI 追问 + 评分 |
| 不同来源格式不统一 | 多格式解析（PDF→txt→Markdown）+ 标准化输出 |

---

## 2. 核心特点

### 2.1 多源知识注入 (Multi-Source Ingestion)

支持从多种来源导入知识，统一转换为标准化的 Vault 结构：

- **PDF 文档**：通过 `pdftotext` 转为纯文本后解析，避免图片消耗大量 Token
- **Word 文档**：提取文本内容，保留标题层级
- **Markdown 文件**：直接解析，提取 frontmatter 和正文
- **粘贴文本**：用户直接粘贴的面经内容，AI 辅助提取 Q&A
- **网页链接**：通过 WebFetch 获取内容

**去重机制**：
- 基于内容哈希（SHA256）检测重复文件
- 基于概念标题相似度检测重复知识点
- 重复内容标记为 `duplicate`，提示用户合并或跳过

**草稿审核流程**：
- 新导入内容默认标记为 `status: draft`
- 用户通过面板模块审核后，才进入正式学习循环
- 避免未经校验的 AI 提取内容污染知识库

### 2.2 概念级学习追踪 (Concept-Level Tracking)

不同于传统的"题目级"追踪，本系统以**概念**为核心单位：

- **笔记 (Note)**：一个概念的知识总结（如 "JVM 垃圾回收机制"）
- **Q&A (Question)**：该概念对应的面试问答（如 "如何判断对象可以被回收？"）
- **一对多关系**：一个笔记可以关联多个 Q&A

**追踪维度**：
- 每个概念：学习次数、正确次数、最后测试日期、状态（🔴 薄弱 / 🟢 学习中 / 🔵 已掌握）
- 每个 Q&A：SM-2 调度参数（interval、ease_factor、next_review）
- 错误笔记：记录混淆点与正确理解，形成个人错题本

### 2.3 多模式复习系统 (Multi-Mode Review)

提供三种复习交互模式，适应不同场景：

| 模式 | 适用场景 | 交互深度 | Token 消耗 |
|------|---------|---------|-----------|
| **FAST** | 快速过题，检验记忆 | 仅展示问题 + 用户回答 + AI 简单评分 | 低 |
| **DEEP** | 深度理解，查漏补缺 | 展示问题 + 用户回答 + AI 详细点评 + 追问 | 中 |
| **INTERVIEW** | 模拟面试，实战演练 | 面试场景化提问 + 多轮追问 + 多维度评分 + 学习建议 | 高 |

**模式切换**：
- 全局默认模式（在配置中设置）
- 每轮复习前可临时切换
- 根据概念状态智能推荐（薄弱概念推荐 DEEP，已掌握推荐 FAST）

### 2.4 SM-2 间隔重复算法 (SM-2 Spaced Repetition)

采用经典的 SuperMemo-2 算法，科学规划复习间隔：

- **评分 5 级**：1-完全不记得 / 2-错误 / 3-部分正确 / 4-正确但犹豫 / 5-完美
- **动态间隔**：根据评分和历史表现调整下次复习时间
- **难度因子 (ease_factor)**：自动适应概念难度，难的概念复习更频繁
- **首次学习调度**：根据用户自评（1-5）设置初始间隔

### 2.5 渐进式面板 (Progressive Dashboard)

面板从简单的文本表格开始，逐步增强：

- **P0 文本面板**：Markdown 表格展示统计、待复习列表、薄弱分析
- **P1 Dataview 面板**：利用 Obsidian Dataview 插件实现动态查询和过滤
- **P2 可视化面板**：知识图谱、进度趋势图、热力图（未来扩展）

**面板内容**：
- 总体进度（总笔记数、已掌握、学习中、薄弱）
- 按频率统计（必问/常问/冷门的掌握率）
- 按领域统计（各技术领域的掌握率）
- 今日待复习列表（含直达链接）
- 薄弱概念 Top 5
- 管理命令入口

---

## 3. 技术选型

### 3.1 Obsidian 生态

本项目深度依赖 Obsidian 的以下能力：

| 功能 | Obsidian 能力 | 说明 |
|------|--------------|------|
| 文件管理 | 原生 Markdown 文件 | 所有数据以 `.md` 文件存储，用户可手动编辑 |
| 双向链接 | `[[wiki-links]]` | 笔记与 Q&A 之间的硬关联 |
| 图谱视图 | Graph View | 可视化知识网络（P2 增强） |
| 动态查询 | Dataview 插件 | 面板中的动态表格和列表（P1 增强） |
| 模板 | Templater 插件 | 新笔记/Q&A 的自动模板填充 |
| 标签系统 | `#tags` | 概念分类与过滤 |

### 3.2 Skill 架构

通过 Claude Code 的 Skill 系统实现四个核心模块：

```
用户输入 → Skill 匹配 → LLM 执行 → 文件读写 → 结果输出
```

**Skill 执行方式**：
- **纯提示词驱动**：大部分逻辑通过 Skill 提示词中的流程定义完成
- **脚本辅助**：复杂操作（如 PDF 解析、哈希计算、SM-2 计算）通过 Python 脚本实现
- **文件系统通信**：Skill 之间不直接调用，通过读写 Vault 文件交换数据

**CWD 边界**：
- 所有操作限制在当前工作目录（CWD）内
- Vault 根目录为 `InterviewVault/`，位于 CWD 下
- 不访问 CWD 外的任何文件

### 3.3 存储方案

采用**文件优先 (File-First)** 设计：

| 数据类型 | 存储格式 | 位置 | 说明 |
|---------|---------|------|------|
| 知识笔记 | Markdown | `InterviewVault/01-Notes/**/*.md` | 含 frontmatter + 正文 |
| 面试问答 | Markdown | `InterviewVault/02-Questions/**/*.md` | 含 frontmatter + 问答内容 |
| 面试陷阱 | Markdown | `InterviewVault/03-Exam-Traps/*.md` | 按领域记录易错点 |
| 会话记录 | Markdown | `InterviewVault/04-Sessions/*.md` | 复习会话日志 |
| 调度数据 | JSON | `InterviewVault/.progress/schedule.json` | SM-2 参数 |
| 统计数据 | JSON | `InterviewVault/.progress/stats.json` | 汇总统计缓存 |
| 标签注册表 | Markdown | `InterviewVault/TAG-REGISTRY.md` | 全局标签规范 |
| 配置 | YAML | `InterviewVault/config.yaml` | 用户配置 |

**JSON 文件设计原则**：
- 人类可读：格式化缩进，方便调试
- 版本控制：含 `version` 字段，支持未来迁移
- 原子写入：先写临时文件，再重命名，避免写入中断导致损坏

### 3.4 配置管理

用户级配置文件 `InterviewVault/config.yaml`：

```yaml
version: "1.0"

# 复习设置
review:
  default_mode: "DEEP"        # FAST | DEEP | INTERVIEW
  questions_per_session: 10    # 每轮复习题目数
  sm2:
    ease_factor_min: 1.3
    ease_factor_max: 3.0
    interval_max: 365

# 注入设置
ingest:
  auto_draft: true             # 新内容是否默认标记为 draft
  duplicate_threshold: 0.85    # 去重相似度阈值

# 面板设置
dashboard:
  show_weak_top_n: 5           # 薄弱概念展示数量
  show_due_preview: true       # 是否展示待复习预览

# 追踪粒度（可选双层追踪）
tracking:
  granularity: "concept"       # "concept" | "sub_topic"
  # concept:    单层追踪，按概念聚合（省 token，默认）
  # sub_topic:  双层追踪，按子知识点聚合（更精准，耗 token）

# 路径配置（高级）
paths:
  vault_root: "./InterviewVault"
  notes_dir: "01-Notes"
  questions_dir: "02-Questions"
  exam_traps_dir: "03-Exam-Traps"
  sessions_dir: "04-Sessions"
  progress_dir: ".progress"
```

---

## 4. 测试方案

### 4.1 设计理念

由于本项目以 Skill 提示词 + 文件操作为主，传统单元测试不完全适用。采用**数据一致性测试 + 效果评估**的组合方案：

### 4.2 Skill 行为测试

对每个 Skill 的关键路径定义预期行为，通过示例验证：

| Skill | 测试场景 | 预期结果 |
|-------|---------|---------|
| **ingest** | 导入一份 PDF 面经 | Vault 中新增对应笔记和 Q&A，frontmatter 正确 |
| **ingest** | 导入重复内容 | 检测到重复，不新增或标记为 duplicate |
| **learn** | 学习一个新概念 | 笔记状态更新，schedule.json 新增条目 |
| **review** | 完成一轮复习 | schedule.json 更新，stats.json 更新，Sessions 新增记录 |
| **dashboard** | 查询面板 | 输出包含正确统计数字的 Markdown 表格 |

**验证方法**：
- 准备标准测试数据（示例 PDF/Markdown 文件）
- 执行 Skill 后检查 Vault 文件状态
- 对比实际输出与预期输出

### 4.3 数据一致性测试

确保 schedule.json 和 stats.json 始终一致：

- **总题目数** = schedule.json 中条目数
- **已掌握数** = status == "mastered" 的条目数
- **今日待复习数** = next_review <= today 的条目数
- **各频率统计**之和 = 总题目数

**验证脚本**（Python）：
```python
def validate_consistency(vault_path: str) -> List[str]:
    """返回不一致项列表，空列表表示一致"""
    ...
```

### 4.4 复习效果评估

定期运行评估，验证 SM-2 算法的有效性：

- **记忆保留率**：复习时评分 >=3 的比例（目标 >=70%）
- **掌握转化率**：从 learning → mastered 的平均所需复习次数
- **薄弱点识别准确率**：dashboard 标为薄弱的概念，实际复习表现是否确实较差

---

## 5. 系统架构与模块设计

### 5.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户交互层 (User Layer)                         │
│                                                                         │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│    │  粘贴文本 │  │  导入文件 │  │  命令触发 │  │  面板查询 │              │
│    │ (面经)   │  │ (PDF/MD) │  │ (学习/复习)│  │ (进度/统计)│              │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└─────────┼─────────────┼─────────────┼─────────────┼──────────────────────┘
          │             │             │             │
          ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Skill 执行层 (Skill Layer)                       │
│                                                                         │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│    │   ingest Skill   │  │   learn Skill   │  │  review Skill   │       │
│    │                 │  │                 │  │                 │       │
│    │  1. 识别输入类型 │  │  1. 推荐知识点   │  │  1. 拉取待复习   │       │
│    │  2. 解析/提取   │  │  2. 展示内容     │  │  2. 交互问答     │       │
│    │  3. 去重检测    │  │  3. 用户自评     │  │  3. 评估打分     │       │
│    │  4. 写入 Vault  │  │  4. 初始化调度   │  │  4. 更新 SM-2    │       │
│    │                 │  │                 │  │  5. 记录会话     │       │
│    └─────────────────┘  └─────────────────┘  └─────────────────┘       │
│                                                                         │
│    ┌─────────────────────────────────────────────────────────────┐     │
│    │                    dashboard Skill                           │     │
│    │  1. 读取统计数据 → 2. 渲染面板 → 3. 处理管理命令              │     │
│    └─────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
          │             │             │             │
          ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          数据层 (Data Layer)                             │
│                                                                         │
│    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│    │  01-Notes/      │  │  02-Questions/  │  │  04-Sessions/   │       │
│    │  (知识笔记)      │  │  (面试问答)      │  │  (会话记录)      │       │
│    └─────────────────┘  └─────────────────┘  └─────────────────┘       │
│                                                                         │
│    ┌─────────────────┐  ┌─────────────────┐                            │
│    │  .progress/     │  │  config.yaml    │                            │
│    │  schedule.json  │  │  (用户配置)      │                            │
│    │  stats.json     │  │                 │                            │
│    └─────────────────┘  └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 数据流图

#### 注入流程 (Ingest)

```
用户输入 (PDF/文本/MD)
    │
    ▼
┌─────────────────┐
│  输入识别        │
│  ├── PDF → pdftotext → txt
│  ├── Word → 文本提取
│  ├── MD → 直接解析
│  └── 粘贴文本 → AI 提取
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  内容解析        │
│  ├── 提取概念笔记
│  └── 提取 Q&A 对
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  去重检测        │
│  └── 基于哈希/标题相似度
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  写入 Vault      │
│  ├── 01-Notes/     (status: draft)
│  ├── 02-Questions/ (关联笔记)
│  └── 03-Exam-Traps/ (追加陷阱条目)
└─────────────────┘
```

#### 学习流程 (Learn)

```
用户触发 "学习"
    │
    ▼
┌─────────────────┐
│  推荐算法        │
│  ├── 优先: draft 笔记
│  ├── 次优: weak 笔记
│  └── 再次: 未学习的 learning 笔记
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  展示笔记内容    │
│  └── 核心要点 + 详细笔记 + 相关 Q&A
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  用户自评 1-5   │
│  ├── 1-2 → weak, 不加入调度
│  ├── 3-5 → learning, 加入调度
│  └── 5 → 可选直接标记 mastered
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  更新数据        │
│  ├── 笔记 frontmatter (status, last_studied)
│  ├── schedule.json (新增/更新条目)
│  └── stats.json (重新计算)
└─────────────────┘
```

#### 复习流程 (Review)

```
用户触发 "复习"
    │
    ▼
┌─────────────────┐
│  拉取待复习      │
│  └── next_review <= today
│      按频率和正确率排序
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  选择交互模式    │
│  ├── FAST (快速)
│  ├── DEEP (深度)
│  └── INTERVIEW (模拟面试)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  逐个问答交互    │
│  ├── 展示问题
│  ├── 收集回答
│  ├── 评估打分 (1-5)
│  └── 点评/追问 (DEEP/INTERVIEW)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  更新调度 (SM-2) │
│  ├── interval = f(score, ease_factor)
│  ├── ease_factor = f(score)
│  └── next_review = today + interval
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  记录会话        │
│  ├── Sessions/YYYY-MM-DD_review.md
│  └── stats.json (重新计算)
└─────────────────┘
```

### 5.3 模块边界

**模块间通信方式**：仅通过文件系统，无直接调用。

| 调用方 | 读取 | 写入 | 说明 |
|--------|------|------|------|
| **ingest** | 用户输入文件 | 01-Notes/, 02-Questions/, 03-Exam-Traps/ | 创建新知识 |
| **learn** | 01-Notes/, schedule.json | schedule.json, stats.json, 01-Notes/ frontmatter | 初始化学习状态 |
| **review** | schedule.json, 02-Questions/ | schedule.json, stats.json, 04-Sessions/, 01-Notes/ | 更新复习状态 |
| **dashboard** | 全部 | stats.json, config.yaml | 只读为主，管理操作时写 |

**无循环依赖**：
- ingest → 数据层 ← learn ← review ← dashboard
- dashboard 不触发其他 Skill，只提供管理入口

---

## 6. 项目排期

### 6.1 Phase 1: 核心循环 (P0)

**目标**：实现基础的学习-复习闭环，能导入知识并进行 SM-2 复习。

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1 | Vault 目录结构 + 文件格式规范 | 目录模板、frontmatter 规范 |
| W1 | ingest Skill 基础版 | 支持粘贴文本 + Markdown 导入 |
| W2 | learn Skill 基础版 | 学习流程 + 自评 + 初始化调度 |
| W2 | review Skill 基础版 (FAST 模式) | 拉取待复习 + 简单评分 + SM-2 更新 |
| W3 | dashboard Skill 基础版 | 文本面板 + 统计计算 |
| W3 | 数据一致性验证脚本 | validate_consistency.py |

### 6.2 Phase 2: 深度交互 (P1)

**目标**：增强复习体验，支持 DEEP 和 INTERVIEW 模式。

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W4 | review Skill DEEP 模式 | AI 详细点评 + 单轮追问 |
| W5 | review Skill INTERVIEW 模式 | 面试场景 + 多轮追问 + 多维度评分 |
| W5 | ingest Skill PDF 支持 | pdftotext 集成 + PDF 解析流程 |
| W6 | 错误笔记系统 | 薄弱点自动记录 + 概念级追踪 |
| W6 | Dataview 面板增强 | dashboard.md Dataview 查询模板 |

### 6.3 Phase 3: 面板增强 (P2)

**目标**：可视化与智能分析。

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W7 | 薄弱分析算法 | 薄弱概念识别 + 推荐学习路径 |
| W7 | 复习效果评估 | 记忆保留率统计 |
| W8 | 知识图谱可视化 | Obsidian Graph View 优化 + 标签规范 |
| W8 | 配置系统 | config.yaml + 配置验证 |

### 6.4 Phase 4: 生态扩展 (P3)

**目标**：在不改变 P0-P2 基础闭环的前提下，增加可选的 MCP 生态接入与 Agent Assist 编排能力。

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W9 | Python stdio MCP Server | 将 Vault 查询、薄弱分析、待复习列表暴露为 MCP Tools/Resources |
| W10 | Agent Assist 模式 | 每日学习计划、面试冲刺计划、维护建议；写入前必须用户确认 |
| W11+ | 多人协作 (Future) | 共享题库、协作标注、权限边界设计 |

---

## 7. 可扩展性与未来展望

### 7.1 Agent 化与 MCP 集成

**目标**：将系统从“用户触发单个 Skill”增强为“Agent 主动规划 + Skill 具体执行 + Vault 统一存储”的可选生态模式。

P3 不替代现有 `ingest` / `learn` / `review` / `dashboard` Skill，而是在其上增加一层可选编排：

```text
外部 MCP Client / Agent
        ↓
MCP Server（只暴露受控工具与资源）
        ↓
Agent Assist（规划/编排层，可选）
        ↓
Skills（具体执行层）
        ↓
InterviewVault（唯一数据源）
```

**三层职责边界**：

| 层级 | 职责 | 不做什么 |
|------|------|---------|
| Agent | 读取 Vault 状态，生成每日计划、冲刺计划、维护建议，选择下一步应使用哪个 Skill | 不重写 ingest/learn/review/dashboard 的完整流程 |
| Skill | 执行具体交互：导入、学习、复习、面板管理 | 不跨模块直接调用其他 Skill |
| Vault | Markdown/JSON 文件存储，是所有模块共享的唯一事实源 | 不依赖外部数据库 |

**MCP Server**：
- 第一版采用 **Python + stdio**，面向本地 Codex / Claude Desktop / VS Code 等客户端。
- 只访问 CWD 内的 `InterviewVault/`，禁止读取 CWD 外文件。
- 默认暴露只读工具；写工具必须显式确认。
- 详细接口见 [8.5 生态扩展模块 (MCP + Agent)](#85-生态扩展模块-mcp--agent)。

**Agent Assist 模式**：
- 是可选模式，不是第五个 Skill。
- 默认只生成建议，不自动修改 Vault。
- 所有写操作（如更新 `schedule.json`、生成报告、记录复习结果）必须用户确认。
- 写操作必须记录审计日志：`InterviewVault/.progress/agent_actions.jsonl`。

**配置示例**：

```yaml
agent:
  enabled: false
  mode: "agent-assist"   # manual | agent-assist | agent-auto
  require_confirmation: true
  daily_brief: true
  max_auto_actions_per_day: 0
```

P3 第一版只实现 `agent-assist`。`agent-auto` 作为未来高级模式保留，不进入默认实现范围。

### 7.2 知识图谱可视化

**目标**：将概念之间的关联可视化，帮助用户发现知识结构中的缺口。

- **Obsidian Graph View 增强**：
  - 按掌握度着色（🔴 薄弱红色 / 🟢 学习中绿色 / 🔵 已掌握蓝色）
  - 按领域分组（Java 领域节点聚类、OS 领域节点聚类）
  - 高频概念节点放大显示
- **交互式探索**：点击节点查看详情，右键标记为已掌握/需复习

### 7.3 多人协作 (Future)

**目标**：将个人知识库扩展为团队共享题库。

- **共享题库**：支持 Git 协作，多人贡献面经和 Q&A
- **权限管理**：区分"个人笔记"和"共享题库"
- **社区标注**：对共享题库的 Q&A 进行评分和评论，筛选高质量内容

---

## 8. 各模块详细规格

### 8.1 注入模块 (ingest)

#### 8.1.1 输入类型与处理策略

| 输入类型 | 识别方式 | 处理流程 | 依赖工具 |
|---------|---------|---------|---------|
| **PDF 文件** | 扩展名 `.pdf` | `pdftotext` → `.txt` → Read → AI 提取 → 写入 Vault | `pdftotext` (poppler) |
| **Word 文档** | 扩展名 `.docx` | `python-docx` 提取文本 → AI 提取 → 写入 Vault | `python-docx` |
| **Markdown 文件** | 扩展名 `.md` | 直接解析 frontmatter + 正文 → 分类写入 Vault | 无 |
| **粘贴文本** | 用户直接输入 | AI 判断类型（笔记/Q&A/混合）→ 提取结构化内容 → 写入 Vault | 无 |
| **网页 URL** | `http://` 或 `https://` 开头 | WebFetch → 提取正文 → AI 提取 → 写入 Vault | WebFetch |

**PDF 处理详细流程**：

```
用户指定 PDF 文件路径
    │
    ▼
检查文件是否在 CWD 内（CWD 边界规则）
    │
    ▼
pdftotext "source.pdf" "/tmp/source.txt"
    │
    ▼
Read "/tmp/source.txt"
    │
    ▼
AI 分析内容结构：
├── 识别技术领域（Java/OS/Network/...）
├── 提取概念笔记（概念名称 + 核心要点）
├── 提取 Q&A 对（问题 + 参考答案 + 评分要点）
└── 标注频率（必问/常问/冷门，基于出现次数和强调程度）
    │
    ▼
去重检测：
├── 计算文件 SHA256
├── 与 .progress/ingestion_history.json 比对
└── 若重复，提示用户并跳过
    │
    ▼
生成 Vault 文件：
├── 01-Notes/{Frequency}/{Domain}/{Concept}.md
├── 02-Questions/{Frequency}/{Domain}-{Concept}.md
└── 03-Exam-Traps/{Domain}.md （追加该概念的陷阱条目）
    │
    ▼
更新 TAG-REGISTRY.md（注册新标签，若不存在则添加）
    │
    ▼
更新 ingestion_history.json
    │
    ▼
输出导入摘要
```

#### 8.1.2 去重机制

**两层去重**：

1. **文件级去重**：
   - 计算文件 SHA256 哈希
   - 查询 `ingestion_history.json`
   - 若 `status == "success"` 且 hash 匹配 → 判定为重复

2. **内容级去重**：
   - 提取概念标题
   - 与现有 Notes 的 frontmatter `concept` 字段比对
   - 使用字符串相似度（如 difflib.SequenceMatcher）
   - 若相似度 >= `duplicate_threshold` (默认 0.85) → 判定为重复

**重复处理策略**：
- 文件级重复：完全跳过，提示用户
- 内容级重复：标记为 `duplicate`，询问用户是否合并或覆盖

#### 8.1.3 AI 提取 Prompt 规范

当处理非结构化文本（PDF txt、粘贴文本）时，使用以下提取策略：

```
你是一位面试八股知识提取专家。请将以下文本中的面试知识点提取为结构化数据。

提取规则：
1. 概念笔记：每个核心概念提取为一条，包含：
   - concept: 概念名称（如 "JVM 垃圾回收机制"）
   - domain: 所属领域（如 "Java"）
   - frequency: 频率评估（必问/常问/冷门）
   - key_points: 核心要点列表（3-5 条）
   - summary: 简要总结（100 字内）

2. 面试问答：每个概念对应的面试问题提取为：
   - question: 问题原文
   - answer: 参考答案（结构化，分点）
   - scoring_points: 评分要点（面试官关注的踩分点）
   - difficulty: 难度（⭐/⭐⭐/⭐⭐⭐）

3. 面试陷阱 (Exam Traps)：每个概念提取 1-2 个常见陷阱：
   - trap_title: 陷阱标题
   - what: 具体是什么坑
   - why_confusing: 为什么容易混淆
   - correct: 正确理解
   - scoring_answer: 面试时的踩分回答

4. 标签 (Tags)：
   - 为每个概念提取 2-5 个标签
   - 格式：英文小写 kebab-case（如 jvm, garbage-collection）
   - 必须包含所属领域标签（如 java, os, network）

5. 关联关系：
   - 每个 Q&A 必须关联到一个概念笔记
   - 若文本未明确关联，根据上下文推断

6. 输出格式：
   - 仅输出结构化 JSON，不要额外解释
   - JSON 格式：{"notes": [...], "questions": [...], "traps": [...]}
```

#### 8.1.4 输出文件生成

**笔记文件 (01-Notes/{Frequency}/{Domain}/{Concept}.md)**：

```markdown
---
id: "{domain}-{concept-slug}"
concept: "{概念名称}"
frequency: "{必问|常问|冷门}"
domain: "{领域}"
sub_domain: "{子领域}"
source: ["{来源文件名}"]
tags: [{tag1}, {tag2}]
status: "draft"
last_studied: null
created_at: "{YYYY-MM-DD}"
---

# {概念名称}

#{tag1} #{tag2}

## Overview Table（一目了然）

| 项目 | 关键点 |
|------|--------|
| A    | ...    |
| B    | ...    |

> [!tip] 记忆口诀
> {AI 生成的记忆口诀或缩写}

## 核心要点

{AI 提取的核心要点}
- 使用 **bold** 标注关键术语
- 使用 `inline code` 标注技术名词

## 详细笔记

{AI 提取的详细内容}

> [!important] 面试常考
> {该概念在面试中出现频率最高的 1-2 个要点}

> [!warning] 易混淆点
> {与相近概念的区分要点}

## 面试常考模式（Exam Patterns）

| 关键词/场景 | 面试官关注点 | 踩分答案 |
|------------|-------------|---------|
| "XXX 原理" | 理解深度 | **关键术语** + 流程 |
| "XXX vs YYY" | 对比能力 | 差异点表格 |
| "什么情况下..." | 场景判断 | 触发条件列举 |

## 相关 Q&A

- [[02-Questions/{Frequency}/{Domain}-{Concept}.md#Q01]]
- [[02-Questions/{Frequency}/{Domain}-{Concept}.md#Q02]]

## 关联概念

- [[01-Notes/{Frequency}/{Domain}/{RelatedConcept}.md]]

## 面试陷阱

- [[03-Exam-Traps/{Domain}.md#{concept-slug}]]
```

**Q&A 文件 (02-Questions/{Frequency}/{Domain}-{Concept}.md)**：

```markdown
---
id: "{domain}-{concept-slug}"
concept_id: "{domain}-{concept-slug}"
frequency: "{必问|常问|冷门}"
domain: "{领域}"
total_questions: {N}
created_at: "{YYYY-MM-DD}"
---

# {概念名称} — 面试问答

#{domain-tag} #practice

## Related Concepts

- [[01-Notes/{Frequency}/{Domain}/{Concept}.md]]
- [[03-Exam-Traps/{Domain}.md#{concept-slug}]]

> [!hint]- 核心模式速查
> | 关键词 | 答案要点 |
> |--------|---------|
> | 关键词1 | **答案** |
> | 关键词2 | **答案** |

---

## Q01 — {简短标签} [recall]

**难度**：{⭐}  **频率**：{必问}

### 问题

{问题原文}

> [!answer]- 查看参考答案
> {参考答案，1-3 句话，分点列出踩分点}
>�> [!summary]- 模式总结
> {该题涉及的核心模式/口诀}

---

## Q02 — {简短标签} [application]

**难度**：{⭐⭐}  **频率**：{常问}

### 问题

{问题原文}

> [!answer]- 查看参考答案
> {参考答案}

---

## Q03 — {简短标签} [analysis]

**难度**：{⭐⭐⭐}  **频率**：{必问}

### 问题

{问题原文}

> [!answer]- 查看参考答案
> {参考答案，含对比分析}
```

**Q&A 文件规范**：

| 规则 | 说明 |
|------|------|
| **题型标签** | 每题标题后标注 `[recall]` / `[application]` / `[analysis]` |
| **题型分布** | 每份 Q&A 文件 ≥8 题：≥60% recall + ≥20% application + ≥2 analysis |
| **答案折叠** | 所有答案使用 `> [!answer]-` fold callout，默认隐藏 |
| **模式速查** | 文件开头提供 `> [!hint]-` fold，汇总该概念的高频关键词→答案 |
| **双向链接** | 必须包含 `## Related Concepts` 链接回概念笔记和 Exam Traps |
| **难度标注** | ⭐ 基础 / ⭐⭐ 进阶 / ⭐⭐⭐ 深挖 |
| **踩分点** | 参考答案中踩分点使用 **bold** 标注 |

**Exam Traps 文件 (03-Exam-Traps/{Domain}.md)**：

```markdown
---
domain: "{领域}"
keywords: exam-traps, interview, {领域}
updated_at: "{YYYY-MM-DD}"
---

# {领域} — 面试陷阱

#interview-traps #{domain-tag}

> [!warning] 本笔记用途
> 记录 {领域} 领域面试中最容易踩坑、最容易混淆的知识点。

---

## {概念名称}

> [!danger]- 陷阱：{陷阱描述}
> - **什么陷阱**：{具体是什么坑}
> - **为什么容易错**：{常见误解的原因}
> - **正确理解**：{正确的知识点}
> - **踩分回答**：{面试时应该怎么说}
> - [[01-Notes/{Frequency}/{Domain}/{Concept}.md|概念笔记]]
> - [[02-Questions/{Frequency}/{Domain}-{Concept}.md|面试问答]]

---

## {另一个概念}

...
```

**Exam Traps 生成规则**：
- 注入时自动为每个概念生成对应的陷阱条目（基于 AI 分析常见误解）
- 复习时评分 ≤2 的题目，自动追加到对应概念的陷阱条目
- 薄弱概念必须在 Exam Traps 中有对应的条目，否则 dashboard 提示补全

#### 8.1.5 导入摘要输出

```
✅ 导入完成

📄 来源：{文件名}

📚 新增笔记：{N}
  ├── 01-Notes/High-Frequency/Java/JVM-GC.md
  └── 01-Notes/High-Frequency/OS/Process-Thread.md

❓ 新增 Q&A：{M} 个问题
  ├── 02-Questions/High-Frequency/Java-JVM-GC.md (3 个问题)
  └── 02-Questions/High-Frequency/OS-Process-Thread.md (2 个问题)

⚠️ 草稿待审核：{K} 条
  请使用「面板」→「审核草稿」查看和确认

⏭️ 跳过（已存在）：{L}
```

### 8.2 学习模块 (learn)

#### 8.2.1 推荐算法

**优先级队列**：

```
推荐得分 = 基础优先级 × 频率权重 × 时间衰减

基础优先级：
- draft: 100
- weak: 80
- learning (未学过): 60
- learning (已学过): 40
- mastered: 0 (不推荐)

频率权重：
- 必问: 1.5
- 常问: 1.2
- 冷门: 1.0

时间衰减：
- last_studied 距今越久，权重越高
- 衰减公式: 1 + days_since_last_studied / 30
```

**推荐逻辑**：
1. 读取所有 Notes 的 frontmatter
2. 按上述公式计算每个笔记的推荐得分
3. 取 Top-3，展示给用户选择
4. 用户可选择"换一个"重新推荐

#### 8.2.2 展示格式

```
🎯 今日推荐 [{1/3}]: JVM 垃圾回收机制

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 必问 | Java > JVM | 从未学习
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 核心要点：

1. 可达性分析 vs 引用计数
   → 可达性分析通过 GC Roots 判断对象存活
   → 引用计数无法解决循环引用问题

2. 分代收集理论
   → 新生代（Eden/Survivor）vs 老年代
   → 不同代使用不同回收算法

3. CMS / G1 / ZGC 对比
   → CMS：低延迟，标记-清除，碎片问题
   → G1：区域化，可预测停顿时间
   → ZGC：亚毫秒停顿，染色指针

─────────────────────────────
📎 相关面试题（3 道）：
  • Q01: 如何判断对象可以被回收？
  • Q02: CMS 和 G1 的区别是什么？
  • Q03: 什么情况下会触发 Full GC？
─────────────────────────────

学习完毕后，请自评掌握程度：
[1] 完全不懂  [2] 部分理解  [3] 基本理解  [4] 很好  [5] 完美
```

#### 8.2.3 自评与调度初始化

| 自评 | 状态 | 初始间隔 | 初始 ease_factor | 加入调度 |
|------|------|---------|-----------------|---------|
| 1 | weak | - | - | 否 |
| 2 | learning | 1 天 | 2.5 | 是 |
| 3 | learning | 3 天 | 2.5 | 是 |
| 4 | learning | 6 天 | 2.5 | 是 |
| 5 | mastered | 10 天 | 2.5 | 是（但 interval 较长） |

**调度条目创建**：

为笔记关联的每个 Q&A 创建 schedule.json 条目：

```json
{
  "items": {
    "java-jvm-gc-q01": {
      "question_id": "java-jvm-gc-q01",
      "note_id": "java-jvm-gc",
      "last_reviewed": null,
      "next_review": "2026-05-26",
      "ease_factor": 2.5,
      "interval": 1,
      "consecutive_correct": 0,
      "total_attempts": 0,
      "total_correct": 0,
      "status": "learning"
    }
  }
}
```

#### 8.2.4 数据更新

学习完成后，更新以下文件：

1. **笔记 frontmatter**：
   - `status`: 根据自评更新
   - `last_studied`: 当前日期

2. **schedule.json**：
   - 新增该笔记关联的所有 Q&A 条目

3. **stats.json**：
   - 重新计算汇总统计

### 8.3 复习模块 (review)

#### 8.3.1 待复习项拉取

**拉取条件**：
- `next_review <= today`
- `status != "mastered"` 或 `interval` 已到

**排序规则**：
1. 频率优先级：必问 > 常问 > 冷门
2. 正确率：低正确率优先（薄弱优先）
3. 过期天数：越过期越优先

**每轮题目数**：
- 默认：`questions_per_session` (config.yaml 中配置，默认 10)
- 用户可临时指定（如"复习 5 题"）
- 若待复习不足，提示用户并减少题目数

#### 8.3.2 交互模式详细规格

**FAST 模式**：

```
--- Q1/10 ---
📚 Java > JVM | 必问

❓ 如何判断对象可以被回收？

💭 请回答（直接输入答案）：

> {用户回答}

✅ 评分：4/5（正确但可补充）
💡 补充：可达性分析的 GC Roots 包括栈帧局部变量、
   静态变量、JNI 引用、同步锁持有对象等

[Enter 继续下一题]
```

**DEEP 模式**：

```
--- Q1/10 ---
📚 Java > JVM | 必问

❓ 如何判断对象可以被回收？

💭 请回答：

> {用户回答}

✅ 你说对了：
  • 提到了可达性分析和引用计数两种方法
  • 正确指出了引用计数的循环引用问题

⚠️ 需要补充：
  • 可达性分析的 GC Roots 具体包括哪些？
  • 为什么 Java 选择可达性分析而非引用计数？

📖 完整参考答案：
  [详细答案...]

💡 延伸思考：
  在 G1 收集器中，可达性分析的 GC Roots 扫描
  是如何与 Remembered Set 配合工作的？

[Enter 继续下一题]
```

**INTERVIEW 模式**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎤 模拟面试 — 第 1/10 题
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

面试官：请你谈谈如何判断对象可以被回收？

💭 请回答：

> {用户回答}

─── 第 1 轮追问 ───

✅ 答得好：你正确区分了引用计数和可达性分析

💡 提示：可以从 JVM 实际实现的角度再深入一点

追问：你提到了可达性分析，那么请具体说一下，
      在 JVM 中哪些对象可以作为 GC Roots？

> {用户回答}

─── 第 2 轮追问 ───

✅ 答得好：正确列举了 GC Roots 的主要类型

💡 提示：再想想跨代引用的处理

追问：在分代收集的场景下，如果老年代对象引用了
      新生代对象，这个新生代对象还能被回收吗？
      JVM 是如何处理这种跨代引用的？

> {用户回答}

─── 追问结束 ───

📊 本题评分：

| 维度 | 分数 | 说明 |
|------|------|------|
| 准确性 | 9/10 | 概念正确，GC Roots 列举完整 |
| 深度 | 7/10 | 达到了一般水平，跨代引用部分不够深入 |
| 代码关联 | 6/10 | 未结合具体 JVM 参数或代码示例 |
| 设计思维 | 7/10 | 能对比两种方案，但缺少权衡分析 |

🏆 综合评分: 7.25/10

📖 学习建议：
  建议阅读 01-Notes/Java/JVM-GC.md 中关于
  "跨代引用与 Remembered Set" 的部分

[Enter 继续下一题]
```

#### 8.3.3 复习出题规则 (Quiz Rules)

**零提示原则 (Zero-Hint Policy)**：
- 问题描述不能暗示正确答案
- 选项描述必须中性，不含 "(Recommended)" 等暗示
- 正确答案位置必须随机化，不能固定在第一或最后

**薄弱概念追问不重样**：
- 同一薄弱概念（status == "weak"）的追问，不得重复上一轮的相同问题
- 必须换场景、换角度重新表述：
  - 上轮问 "What" → 本轮问 "How" 或 "Why"
  - 上轮问理论 → 本轮问场景/调试/对比
  - 上轮问正向 → 本轮问边界条件/异常处理

**难度动态平衡**：

| 复习场景 | 易(⭐) | 中(⭐⭐) | 难(⭐⭐⭐) |
|----------|--------|----------|----------|
| 日常复习 | 40% | 40% | 20% |
| 薄弱区训练 | 0% | 30% | 70% |
| 考前冲刺 | 20% | 50% | 30% |

**题型多样化要求**（每轮至少覆盖 3 种）：
1. **事实回忆 (Factual recall)**："HTTP 状态码 503 表示什么？"
2. **概念理解 (Conceptual)**："为什么 JVM 选择可达性分析而非引用计数？"
3. **行为预测 (Behavioral)**："如果 G1 的 Remembered Set 丢失，会发生什么？"
4. **比较区分 (Comparison)**："CMS 和 G1 在碎片处理上有什么区别？"
5. **调试场景 (Debugging)**："给定这个 GC 日志，最可能是什么问题？"

**追问设计原则 (DEEP/INTERVIEW)**：

**追问触发条件**：
- 用户回答正确但不够完整 → 追问遗漏点
- 用户回答有错误 → 先纠正错误，再问相关延伸
- 用户回答优秀 → 提升难度，问更深的问题
- 用户说"不会" → 直接给答案，不追问

**追问内容来源**：
1. **参考答案中的踩分点**：用户未提及的点
2. **常见错误**：用户可能踩的坑
3. **关联概念**：与当前概念相关的其他知识点
4. **设计取舍**：为什么这样设计，替代方案对比

**追问轮数限制**：
- DEEP：最多 1 轮追问
- INTERVIEW：最多 3 轮追问
- 用户可随时说"跳过"或"不会"结束追问

#### 8.3.4 评分规则

**FAST 模式**：
- AI 直接给出 1-5 分
- 仅展示分数和简短补充

**DEEP 模式**：
- AI 给出 1-5 分
- 展示"你说对了 / 需要补充 / 完整答案"

**INTERVIEW 模式**：
- 四个维度各 0-10 分：
  - **准确性**：事实正确性
  - **深度**：是否触及原理层面
  - **代码关联**：是否结合代码/参数/实现细节
  - **设计思维**：是否有对比、权衡、扩展思考
- 综合评分 = 四维度平均，保留一位小数

#### 8.3.5 SM-2 更新规则

**评分 → 调度更新**：

| 评分 | 含义 | interval 更新 | ease_factor 更新 | consecutive_correct |
|------|------|--------------|-----------------|-------------------|
| 5 | 完美 | × ease_factor | 不变 | +1 |
| 4 | 正确但犹豫 | × ease_factor | 不变 | +1 |
| 3 | 部分正确 | max(1, × 0.5) | × 0.8 | 重置为 0 |
| 2 | 错误 | max(1, × 0.3) | × 0.7 | 重置为 0 |
| 1 | 完全不记得 | 设为 1 | × 0.5 | 重置为 0 |

**边界条件**：
- `ease_factor` 下限 1.3，上限 3.0
- `interval` 下限 1 天，上限 365 天
- `consecutive_correct >= 5` 且 `ease_factor >= 2.5` → 可标记为 `mastered`

** mastered 状态**：
- `status` 设为 `"mastered"`
- `interval` 设为 365
- 不再主动推荐复习，但用户可手动触发

#### 8.3.6 会话记录

每次复习完成后，生成会话记录文件：

```markdown
---
date: "2026-05-25"
mode: "INTERVIEW"
total_questions: 10
completed: 10
---

# 复习会话 — 2026-05-25

## 概览

- 模式：INTERVIEW
- 题目数：10
- 平均得分：7.2/10
- 掌握：6 题（>= 7 分）
- 需加强：4 题（< 7 分）

## 详细记录

### Q1: JVM-GC-Q01 — 如何判断对象可以被回收？

- **得分**：7.25/10
- **用户回答摘要**：提到了可达性分析和引用计数，GC Roots 列举完整
- **薄弱点**：跨代引用处理不够深入
- **建议**：复习 Remembered Set 相关概念

### Q2: ...

## 更新计划

| 题目 | 下次复习 | 间隔 | ease_factor |
|------|---------|------|------------|
| JVM-GC-Q01 | 2026-05-28 | 3 天 | 2.5 |
| ... | ... | ... | ... |

## 本次薄弱概念

1. JVM 垃圾回收 — 平均得分 6.5/10 → [[01-Notes/High-Frequency/Java/JVM-GC.md]]
2. ...
```

#### 8.3.7 错误笔记系统

评分 <= 2 时，自动记录错误笔记：

在对应笔记文件末尾追加：

```markdown
### 错误笔记

**2026-05-25 — Q01**
- **问题**：如何判断对象可以被回收？
- **错误回答**：{用户回答摘要}
- **混淆点**：{AI 分析的用户误解}
- **正确理解**：{正确知识点}
- **关联概念**：[[Notes/...]]
```

### 8.4 面板模块 (dashboard)

#### 8.4.1 面板内容结构

```
📊 学习面板（更新于 2026-05-25）

═══════════════════════════════════════
📈 总体进度
═══════════════════════════════════════

📚 笔记：15 | 已学：12 | 掌握：8 | 薄弱：4 | 草稿：1
❓ 题目：45 | 已练：38 | 掌握：12 | 学习中：18 | 薄弱：8 | 草稿：7

今日待复习：5 题 ⏰
  🔴 GC-01 JVM垃圾回收 (已过期 2 天) → [[02-Questions/...]]
  🟡 PT-01 进程线程区别 (今日到期) → [[02-Questions/...]]
  ...

═══════════════════════════════════════
📊 按频率统计
═══════════════════════════════════════

| 频率 | 总数 | 已掌握 | 学习中 | 薄弱 | 正确率 |
|------|------|--------|--------|------|--------|
| 必问 | 20   | 8      | 8      | 4    | 65%    |
| 常问 | 15   | 3      | 8      | 4    | 45%    |
| 冷门 | 10   | 1      | 2      | 7    | 30%    |

═══════════════════════════════════════
📊 按领域统计
═══════════════════════════════════════

| 领域   | 笔记数 | 题目数 | 已掌握 | 正确率 | 状态 |
|--------|--------|--------|--------|--------|------|
| Java   | 12     | 30     | 8      | 62%    | 🟢 良好 |
| OS     | 8      | 15     | 2      | 38%    | 🔴 薄弱 |
| Network| 5      | 10     | 2      | 45%    | 🟡 一般 |

═══════════════════════════════════════
🔴 薄弱概念 Top 5
═══════════════════════════════════════

1. JVM 垃圾回收 (正确率 33%) → [[01-Notes/High-Frequency/Java/JVM-GC.md]]
2. CAS 原理 (正确率 40%) → [[01-Notes/...]]
3. 进程调度算法 (正确率 42%) → [[01-Notes/...]]
4. TCP 三次握手 (正确率 45%) → [[01-Notes/...]]
5. 数据库索引优化 (正确率 48%) → [[01-Notes/...]]

═══════════════════════════════════════
⚙️ 管理命令
═══════════════════════════════════════

- 标记 [题目ID] 为掌握
- 调整 [题目ID] 复习日期到 [YYYY-MM-DD]
- 审核草稿（{N} 条待审核）
- 重新计算统计
- 导出复习报告
```

#### 8.4.2 管理操作

| 命令 | 操作 | 影响文件 |
|------|------|---------|
| `标记 [ID] 为掌握` | 将题目状态设为 mastered | schedule.json |
| `调整 [ID] 日期到 [日期]` | 修改 next_review | schedule.json |
| `审核草稿` | 列出所有 draft 笔记和 Q&A，供用户确认 | 01-Notes/, 02-Questions/ |
| `重新计算统计` | 从原始数据重新生成 stats.json | stats.json |
| `导出复习报告` | 生成近期复习表现的 Markdown 报告 | 04-Sessions/report-*.md |

#### 8.4.3 统计计算

**stats.json 重新计算逻辑**：

```python
def recalculate_stats(vault_path: str) -> dict:
    """
    从原始数据重新计算所有统计指标
    """
    # 1. 读取所有 01-Notes 和 02-Questions
    notes = read_all_notes(vault_path)
    questions = read_all_questions(vault_path)
    schedule = read_schedule(vault_path)

    # 2. 计算总体统计
    total_notes = len(notes)
    total_questions = len(questions)
    mastered_notes = sum(1 for n in notes if n.status == "mastered")
    weak_notes = sum(1 for n in notes if n.status == "weak")
    learning_notes = sum(1 for n in notes if n.status == "learning")

    # 3. 计算题目统计
    mastered_q = sum(1 for q in schedule if q.status == "mastered")
    weak_q = sum(1 for q in schedule if q.status == "weak")
    learning_q = sum(1 for q in schedule if q.status == "learning")

    # 4. 计算今日待复习
    today_due = sum(1 for q in schedule if q.next_review <= today)

    # 5. 按频率统计
    by_frequency = {}
    for freq in ["必问", "常问", "冷门"]:
        fq_questions = [q for q in questions if q.frequency == freq]
        fq_schedule = [s for s in schedule if s.question_id in fq_questions]
        by_frequency[freq] = {
            "total": len(fq_questions),
            "mastered": sum(1 for s in fq_schedule if s.status == "mastered"),
        }

    # 6. 按领域统计
    by_domain = {}
    for domain in get_all_domains(notes):
        d_notes = [n for n in notes if n.domain == domain]
        d_questions = [q for q in questions if q.domain == domain]
        # ...

    # 7. 薄弱概念 Top N
    weak_concepts = []
    for note in notes:
        note_questions = [q for q in questions if q.note_id == note.id]
        note_schedule = [s for s in schedule if s.note_id == note.id]
        if note_schedule:
            correct_rate = sum(s.total_correct for s in note_schedule) / sum(s.total_attempts for s in note_schedule)
            if correct_rate < 0.6:
                weak_concepts.append({
                    "note_id": note.id,
                    "concept": note.concept,
                    "correct_rate": correct_rate
                })
    weak_concepts.sort(key=lambda x: x["correct_rate"])

    return {
        "version": "1.0",
        "last_updated": now(),
        "summary": {
            "total_notes": total_notes,
            "total_questions": total_questions,
            "mastered_notes": mastered_notes,
            "learning_notes": learning_notes,
            "weak_notes": weak_notes,
            "mastered_questions": mastered_q,
            "learning_questions": learning_q,
            "weak_questions": weak_q,
            "today_due": today_due,
            "overall_correct_rate": calculate_overall_correct_rate(schedule)
        },
        "by_frequency": by_frequency,
        "by_domain": by_domain,
        "weak_concepts": weak_concepts[:config.show_weak_top_n]
    }
```

---

### 8.5 生态扩展模块 (MCP + Agent)

> **实现优先级**：P3
> **目标**：在不改变四个核心 Skill 职责的前提下，将 Vault 查询能力暴露给 MCP Client，并提供可选的 Agent Assist 编排模式。

#### 8.5.1 设计边界

P3 是生态扩展，不是基础闭环的必需条件。用户即使完全不开启 P3，也应能继续使用 P0-P2 的全部能力。

**核心原则**：

1. **Vault 仍是唯一事实源**：MCP Server、Agent、Skill 都只通过 `InterviewVault/` 下的 Markdown/JSON 文件交换数据。
2. **Agent 不替代 Skill**：导入由 `ingest` 负责，学习由 `learn` 负责，复习由 `review` 负责，统计与管理由 `dashboard` 负责。
3. **默认只读，确认后写入**：查询、分析、计划生成可以自动执行；任何修改 Vault 的动作必须用户确认。
4. **本地优先**：P3 第一版采用 Python + stdio MCP Server，仅服务本机客户端。
5. **可审计**：所有 Agent 写操作追加记录到 `InterviewVault/.progress/agent_actions.jsonl`。

#### 8.5.2 推荐目录结构

```text
mcp_server/
├── server.py              # MCP Server 入口，stdio transport
├── tools.py               # MCP Tools 注册与参数 schema
├── resources.py           # MCP Resources 注册
├── vault_reader.py        # 只读 Vault 查询封装
├── vault_writer.py        # 确认后写入与审计日志
├── planner.py             # Agent Assist 计划生成
└── tests/
    ├── smoke_test.py      # MCP 启动与工具列表测试
    ├── contract_test.py   # Tool schema 与错误输出测试
    └── e2e_test.py        # Agent confirmed-write 流程测试
```

**与现有目录关系**：

- `.claude/skills/` 仍是 canonical Skill 目录。
- `scripts/` 继续存放跨模块通用脚本，如配置验证、一致性验证、原子写入。
- `mcp_server/` 不直接复制 Skill 流程，只封装 Vault 查询、计划生成和受控写入。

#### 8.5.3 MCP Server 规格

**技术选型**：

| 项 | 选择 |
|----|------|
| 语言 | Python |
| Transport | stdio |
| 数据范围 | `{CWD}/InterviewVault/` |
| 默认权限 | read-only |
| 写入策略 | 必须 `confirmed=true`，并写入审计日志 |

**启动方式**：

```bash
python mcp_server/server.py --vault InterviewVault
```

**CWD 安全边界**：

1. MCP Server 启动时解析 `vault_path.resolve()`。
2. 若 `vault_path` 不在 CWD 内，拒绝启动。
3. 所有工具参数中的路径、ID、URI 都必须解析到 `InterviewVault/` 内。
4. 禁止暴露任意文件读取工具。

#### 8.5.4 MCP Tools

##### Tool: `query_knowledge`

查询某个概念的笔记、相关 Q&A 和面试陷阱。

**Input Schema**：

```json
{
  "concept": "string, required, 概念名或 note_id",
  "domain": "string, optional, 领域过滤，如 Java/OS/Network",
  "include_questions": "boolean, optional, default=true",
  "include_traps": "boolean, optional, default=true"
}
```

**Output**：

```json
{
  "note": {
    "note_id": "java-jvm-gc",
    "concept": "JVM 垃圾回收机制",
    "domain": "Java",
    "frequency": "必问",
    "status": "learning",
    "file_path": "01-Notes/High-Frequency/Java/JVM-GC.md",
    "summary": "..."
  },
  "questions": [
    {
      "question_id": "java-jvm-gc-q01",
      "question": "如何判断对象可以被回收？",
      "file_path": "02-Questions/High-Frequency/Java-JVM-GC.md"
    }
  ],
  "traps": [
    {
      "title": "引用计数 vs 可达性分析",
      "file_path": "03-Exam-Traps/Java.md"
    }
  ]
}
```

**错误处理**：

| 场景 | 返回 |
|------|------|
| 找不到概念 | `not_found`，并返回相近概念候选 |
| domain 不匹配 | `domain_mismatch`，提示实际 domain |
| 文件损坏 | `parse_error`，返回损坏文件路径 |

##### Tool: `list_weak_areas`

列出当前薄弱概念，供外部客户端或 Agent 制定学习计划。

**Input Schema**：

```json
{
  "limit": "integer, optional, default=5, min=1, max=20",
  "domain": "string, optional",
  "min_attempts": "integer, optional, default=1"
}
```

**Output**：

```json
{
  "weak_areas": [
    {
      "note_id": "java-jvm-gc",
      "concept": "JVM 垃圾回收机制",
      "domain": "Java",
      "correct_rate": 0.33,
      "attempts": 6,
      "priority": "high",
      "recommended_action": "DEEP review"
    }
  ]
}
```

##### Tool: `get_due_reviews`

获取指定日期到期的复习题。

**Input Schema**：

```json
{
  "date": "string, optional, YYYY-MM-DD, default=today",
  "limit": "integer, optional, default=10, min=1, max=50",
  "include_mastered": "boolean, optional, default=false"
}
```

**Output**：

```json
{
  "date": "2026-06-09",
  "total_due": 5,
  "items": [
    {
      "question_id": "java-jvm-gc-q01",
      "note_id": "java-jvm-gc",
      "concept": "JVM 垃圾回收机制",
      "domain": "Java",
      "frequency": "必问",
      "next_review": "2026-06-09",
      "status": "learning"
    }
  ]
}
```

##### Tool: `get_learning_plan`

生成只读学习计划，不直接写入 Vault。

**Input Schema**：

```json
{
  "days": "integer, optional, default=1, min=1, max=14",
  "focus_domain": "string, optional",
  "intensity": "string, optional, enum=light|normal|intensive, default=normal"
}
```

**Output**：

```json
{
  "mode": "agent-assist",
  "days": 1,
  "plan": [
    {
      "date": "2026-06-09",
      "blocks": [
        {
          "type": "review",
          "mode": "DEEP",
          "count": 5,
          "reason": "今日到期且正确率低"
        },
        {
          "type": "learn",
          "concept": "CAS 原理",
          "reason": "Java 高频薄弱依赖概念"
        }
      ]
    }
  ],
  "writes_required": false
}
```

##### Tool: `record_review_result`

记录外部客户端完成的一次复习结果。该工具是写工具，必须确认。

**Input Schema**：

```json
{
  "question_id": "string, required",
  "score": "integer, required, min=1, max=5",
  "mode": "string, required, enum=FAST|DEEP|INTERVIEW",
  "confirmed": "boolean, required"
}
```

**行为**：

1. 若 `confirmed=false`，返回 dry-run 结果，不写文件。
2. 若 `confirmed=true`：
   - 调用 SM-2 更新逻辑。
   - 原子写入 `.progress/schedule.json`。
   - 重新计算 `.progress/stats.json`。
   - 追加审计日志到 `.progress/agent_actions.jsonl`。
3. 写入后必须运行 `validate_consistency.py`。

**Output**：

```json
{
  "written": true,
  "question_id": "java-jvm-gc-q01",
  "before": {
    "interval": 3,
    "status": "learning"
  },
  "after": {
    "interval": 7,
    "status": "learning",
    "next_review": "2026-06-16"
  },
  "audit_id": "2026-06-09T10:00:00-java-jvm-gc-q01"
}
```

#### 8.5.5 MCP Resources

MCP Resources 只读暴露 Vault 当前状态：

| Resource URI | 内容 | 来源 |
|--------------|------|------|
| `vault://stats` | 当前统计摘要 | `.progress/stats.json` |
| `vault://schedule` | 当前复习调度 | `.progress/schedule.json` |
| `vault://notes/{note_id}` | 指定概念笔记 | `01-Notes/**/*.md` |
| `vault://questions/{question_id}` | 指定问题及参考答案 | `02-Questions/**/*.md` |

**Resource 约束**：

- 返回内容应包含 `source_path`，但路径必须是相对 `InterviewVault/` 的路径。
- 不返回 CWD 外绝对路径。
- 对大文件做摘要截断，默认正文最大 8,000 字符。

#### 8.5.6 Agent Assist 模式

Agent Assist 是可选的规划/编排层，不是第五个 Skill。

**模式枚举**：

| 模式 | 行为 | P3 状态 |
|------|------|---------|
| `manual` | 完全由用户触发 Skill | 已存在 |
| `agent-assist` | Agent 主动生成计划，写入前确认 | P3 第一版 |
| `agent-auto` | Agent 可自动执行部分写操作 | Future，不默认实现 |

**配置**：

```yaml
agent:
  enabled: false
  mode: "agent-assist"   # manual | agent-assist | agent-auto
  require_confirmation: true
  daily_brief: true
  max_auto_actions_per_day: 0
```

**Agent 可执行的只读任务**：

1. **Daily Brief**：读取 due reviews、weak areas、retention，生成今日学习安排。
2. **Pre-interview Plan**：根据目标领域和剩余天数生成冲刺计划。
3. **Maintenance Check**：发现统计过期、草稿堆积、孤儿链接、标签不规范。
4. **Learning Path**：基于薄弱概念和依赖关系推荐学习顺序。

**Agent 写入前必须确认的任务**：

| 动作 | 影响文件 | 确认要求 |
|------|---------|---------|
| 记录复习结果 | `.progress/schedule.json`, `.progress/stats.json` | 必须确认 |
| 生成日报/周报 | `04-Sessions/report-*.md` | 必须确认 |
| 调整复习日期 | `.progress/schedule.json` | 必须确认 |
| 标记掌握/薄弱 | `.progress/schedule.json`, Notes frontmatter | 必须确认 |

**Agent 到 Skill 的交接格式**：

Agent 不直接执行完整 Skill 流程，而是输出可被用户确认的下一步：

```markdown
## 今日建议

1. 使用 review Skill，以 DEEP 模式复习 5 道到期题。
   - 原因：今日到期且平均正确率低于 60%
   - 建议命令：`复习 5 题，DEEP 模式`

2. 使用 learn Skill 学习 [[CAS 原理]]。
   - 原因：它是 JVM 并发相关薄弱点的前置概念
   - 建议命令：`学习 CAS 原理`
```

#### 8.5.7 写操作审计

所有 Agent 或 MCP 写工具必须追加 JSONL 审计记录：

文件：`InterviewVault/.progress/agent_actions.jsonl`

```json
{
  "timestamp": "2026-06-09T10:00:00",
  "actor": "agent-assist",
  "action": "record_review_result",
  "target": "java-jvm-gc-q01",
  "confirmed": true,
  "before": {
    "status": "learning",
    "interval": 3,
    "next_review": "2026-06-09"
  },
  "after": {
    "status": "learning",
    "interval": 7,
    "next_review": "2026-06-16"
  }
}
```

**审计规则**：

- JSONL 每行一条记录。
- 审计写入失败时，主写操作必须失败并回滚。
- 审计记录不保存完整用户回答，只保存摘要，避免敏感内容长期滞留。

#### 8.5.8 P3 测试方案

**MCP Smoke Test**：

| 测试 | 预期 |
|------|------|
| Server 启动 | stdio server 可启动，无异常 |
| Tools list | 返回 5 个工具 |
| Resources list | 返回 4 类资源 |
| `query_knowledge` | 能查询现有测试概念 |
| CWD 越界 | 传入 CWD 外路径时拒绝 |

**MCP Contract Test**：

- 每个 Tool 的 input schema 稳定。
- 缺少必填参数时返回可操作错误。
- 输出 JSON 包含固定顶层字段。
- 只读工具不修改任何 Vault 文件。

**Agent Dry-run Test**：

1. 输入 `days=1, intensity=normal`。
2. 生成每日计划。
3. 校验 `.progress/schedule.json`、`.progress/stats.json` 未发生变化。
4. 输出包含 `writes_required=false`。

**Agent Confirmed-write E2E**：

1. 调用 `record_review_result(question_id, score, mode, confirmed=false)`。
2. 校验只返回 dry-run，不写文件。
3. 调用 `record_review_result(..., confirmed=true)`。
4. 校验 schedule/stats 更新。
5. 校验 `agent_actions.jsonl` 新增一条审计记录。
6. 运行 `python scripts/validate_consistency.py InterviewVault`，必须通过。

**回归要求**：

- P3 改动不得破坏 P0-P2 的 smoke/e2e。
- MCP Server 只读工具不得产生文件 diff。
- 所有写工具必须使用原子写入。

---

## 9. Skill 文件结构

### 9.1 目录结构

```
.claude/skills/
├── ingest/
│   ├── SKILL.md              # 注入模块主 Skill
│   └── scripts/
│       ├── pdf_extract.py    # PDF → txt 提取
│       ├── dedup.py          # 去重检测
│       └── format_convert.py # 格式转换
│
├── learn/
│   ├── SKILL.md              # 学习模块主 Skill
│   └── scripts/
│       └── recommend.py      # 推荐算法
│
├── review/
│   ├── SKILL.md              # 复习模块主 Skill
│   └── scripts/
│       ├── sm2.py            # SM-2 算法实现
│       └── scoring.py        # 评分计算
│
└── dashboard/
    ├── SKILL.md              # 面板模块主 Skill
    └── scripts/
        └── stats.py          # 统计计算
```

### 9.2 各 Skill 通用格式

```markdown
---
name: {skill-name}
description: >
  {简短描述，包含触发关键词}
  触发词：{keyword1}, {keyword2}, ...
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# {Skill 名称}

## 触发条件
{触发关键词列表，支持中英文}

## CWD 边界
NEVER access files outside CWD. All vault operations within `{CWD}/InterviewVault/`.

## 前置检查
1. 检查 `InterviewVault/` 是否存在
2. 如不存在，提示用户先初始化（运行 `ingest` 导入内容）
3. 读取 `config.yaml` 获取用户配置

## 主流程
{按本章 8.x 节对应模块的详细流程实现}

## 数据读写规范
{明确该 Skill 读取和写入哪些文件}

## 错误处理
{常见错误场景及处理方式}
```

### 9.3 共享脚本规范

**Python 脚本设计原则**：
- 纯函数优先：输入确定 → 输出确定，无副作用
- 文件操作原子化：先写 `.tmp` 文件，再重命名
- 异常处理：所有文件操作包裹 try-except，失败时返回错误信息
- 日志：输出到 stderr，不污染 stdout（兼容 MCP 等场景）

**脚本接口示例**（`sm2.py`）：

```python
#!/usr/bin/env python3
"""SM-2 间隔重复算法实现"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class SM2Item:
    """SM-2 调度条目"""
    question_id: str
    note_id: str
    last_reviewed: Optional[datetime]
    next_review: datetime
    ease_factor: float
    interval: int  # 天数
    consecutive_correct: int
    total_attempts: int
    total_correct: int
    status: str  # "learning" | "weak" | "mastered"


class SM2Engine:
    """SM-2 算法引擎"""

    EASE_FACTOR_MIN = 1.3
    EASE_FACTOR_MAX = 3.0
    INTERVAL_MAX = 365

    def __init__(self, ease_factor_min: float = 1.3,
                 ease_factor_max: float = 3.0,
                 interval_max: int = 365):
        self.EASE_FACTOR_MIN = ease_factor_min
        self.EASE_FACTOR_MAX = ease_factor_max
        self.INTERVAL_MAX = interval_max

    def review(self, item: SM2Item, score: int) -> SM2Item:
        """
        执行一次复习评分，返回更新后的条目

        Args:
            item: 当前调度条目
            score: 用户评分 (1-5)

        Returns:
            更新后的 SM2Item
        """
        if score < 1 or score > 5:
            raise ValueError(f"Score must be 1-5, got {score}")

        item.total_attempts += 1
        if score >= 3:
            item.total_correct += 1
            item.consecutive_correct += 1
        else:
            item.consecutive_correct = 0

        # 更新 ease_factor
        if score < 3:
            quality_adjustment = {1: -0.5, 2: -0.3, 3: -0.2}
            item.ease_factor += quality_adjustment[score]
        # score 4,5: ease_factor 不变

        item.ease_factor = max(self.EASE_FACTOR_MIN,
                               min(self.EASE_FACTOR_MAX, item.ease_factor))

        # 更新 interval
        if score >= 3:
            if item.interval == 0:
                item.interval = 1 if score == 3 else 6 if score == 4 else 10
            else:
                item.interval = int(item.interval * item.ease_factor)
        else:
            item.interval = max(1, int(item.interval * {1: 0, 2: 0.3, 3: 0.5}[score]))

        item.interval = min(self.INTERVAL_MAX, item.interval)

        # 更新日期
        item.last_reviewed = datetime.now()
        item.next_review = item.last_reviewed + timedelta(days=item.interval)

        # 更新状态
        if item.consecutive_correct >= 5 and item.ease_factor >= 2.5:
            item.status = "mastered"
        elif score <= 2:
            item.status = "weak"
        else:
            item.status = "learning"

        return item

    def init_schedule(self, note_id: str, question_id: str,
                      self_assessment: int) -> SM2Item:
        """
        根据首次学习自评初始化调度

        Args:
            note_id: 笔记 ID
            question_id: 问题 ID
            self_assessment: 自评 (1-5)

        Returns:
            初始化的 SM2Item
        """
        intervals = {1: 0, 2: 1, 3: 3, 4: 6, 5: 10}
        interval = intervals.get(self_assessment, 1)

        now = datetime.now()
        return SM2Item(
            question_id=question_id,
            note_id=note_id,
            last_reviewed=None,
            next_review=now + timedelta(days=interval) if interval > 0 else now,
            ease_factor=2.5,
            interval=interval,
            consecutive_correct=0,
            total_attempts=0,
            total_correct=0,
            status="weak" if self_assessment <= 1 else "learning"
        )
```

---

## 10. 附录

### 10.1 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 笔记 ID | `{domain}-{concept-slug}` | `java-jvm-gc`, `os-process-thread` |
| 问题 ID | `{note-id}-q{NN}` | `java-jvm-gc-q01`, `java-jvm-gc-q02` |
| 文件名 (笔记) | `{Concept-Name}.md` | `JVM-GC.md`, `Process-Thread.md` |
| 文件名 (Q&A) | `{Domain}-{Concept}.md` | `Java-JVM-GC.md`, `OS-Process-Thread.md` |
| 领域名称 | 英文首字母大写 | `Java`, `OS`, `Network`, `Database` |
| 频率标签 | 中文 | `必问`, `常问`, `冷门` |
| 标签 | 英文小写 kebab-case | `#jvm`, `#garbage-collection`, `#concurrency` |

### 10.2 文件格式规范

**Notes frontmatter 字段**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识 |
| `concept` | string | 是 | 概念名称（人类可读） |
| `frequency` | string | 是 | `必问` / `常问` / `冷门` |
| `domain` | string | 是 | 所属领域 |
| `sub_domain` | string | 否 | 子领域 |
| `source` | string[] | 否 | 来源文件列表 |
| `tags` | string[] | 否 | 标签列表 |
| `status` | string | 是 | `draft` / `learning` / `weak` / `mastered` |
| `last_studied` | string/null | 否 | 最后学习日期 `YYYY-MM-DD` |
| `created_at` | string | 是 | 创建日期 `YYYY-MM-DD` |

**Questions frontmatter 字段**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识（对应 note ID） |
| `concept_id` | string | 是 | 关联的笔记 ID |
| `frequency` | string | 是 | 频率 |
| `domain` | string | 是 | 领域 |
| `total_questions` | int | 是 | 该文件中的问题总数 |
| `created_at` | string | 是 | 创建日期 |

**schedule.json 字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | string | 数据格式版本 |
| `last_updated` | string | 最后更新日期 (ISO 8601) |
| `items` | object | 以 question_id 为键的条目字典 |

**schedule item 字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `question_id` | string | 问题 ID |
| `note_id` | string | 关联笔记 ID |
| `last_reviewed` | string/null | 最后复习日期 `YYYY-MM-DD` |
| `next_review` | string | 下次复习日期 `YYYY-MM-DD` |
| `ease_factor` | float | 难度因子 |
| `interval` | int | 当前间隔（天） |
| `consecutive_correct` | int | 连续正确次数 |
| `total_attempts` | int | 总尝试次数 |
| `total_correct` | int | 总正确次数 |
| `status` | string | `learning` / `weak` / `mastered` |

### 10.3 Vault 初始化模板

当用户首次使用时，提供初始化命令生成标准目录结构：

```
InterviewVault/
├── 00-Dashboard/
│   └── dashboard.md               # 面板主文件（Dataview 查询）
├── 01-Notes/
│   ├── High-Frequency/
│   ├── Medium-Frequency/
│   └── Low-Frequency/
├── 02-Questions/
│   ├── High-Frequency/
│   ├── Medium-Frequency/
│   └── Low-Frequency/
├── 03-Exam-Traps/                 # 面试陷阱笔记（按领域）
├── 04-Sessions/
├── .progress/
│   ├── schedule.json
│   └── stats.json
├── TAG-REGISTRY.md                # 标签注册表
└── config.yaml
```

**初始 schedule.json**：

```json
{
  "version": "1.0",
  "last_updated": "2026-05-25T00:00:00Z",
  "items": {}
}
```

**初始 stats.json**：

```json
{
  "version": "1.0",
  "last_updated": "2026-05-25T00:00:00Z",
  "summary": {
    "total_notes": 0,
    "total_questions": 0,
    "mastered_notes": 0,
    "learning_notes": 0,
    "weak_notes": 0,
    "mastered_questions": 0,
    "learning_questions": 0,
    "weak_questions": 0,
    "today_due": 0,
    "overall_correct_rate": 0.0
  },
  "by_frequency": {
    "必问": {"total": 0, "mastered": 0},
    "常问": {"total": 0, "mastered": 0},
    "冷门": {"total": 0, "mastered": 0}
  },
  "by_domain": {},
  "weak_concepts": []
}
```

### 10.4 Tag 注册表模板 (TAG-REGISTRY.md)

```markdown
# Tag Registry

> 全局标签规范。所有标签必须来自本注册表，kebab-case 格式。
> 注入新内容时自动检查并注册新标签。

## 层级规则

| 层级 | 前缀 | 示例 | 规则 |
|------|------|------|------|
| 领域 (Domain) | 无 | `#java`, `#os`, `#network` | 每篇笔记必须带所属领域标签 |
| 子领域 (Sub) | 无 | `#jvm`, `#garbage-collection` | 细分主题，必须同时带父领域标签 |
| 题型 (Type) | `#type-` | `#type-recall`, `#type-analysis` | Q&A 文件题型标注 |
| 笔记类型 (Note) | `#note-` | `#note-concept`, `#note-trap` | 笔记分类 |
| 状态 (Status) | `#status-` | `#status-draft`, `#status-weak` | 学习状态（可选） |

## 已注册标签

| 标签 | 层级 | 说明 |
|------|------|------|
| `#java` | 领域 | Java 技术栈 |
| `#jvm` | 子领域 | JVM 子领域（必须同时带 `#java`） |
| `#garbage-collection` | 子领域 | 垃圾回收 |
| `#os` | 领域 | 操作系统 |
| `#network` | 领域 | 计算机网络 |
| `#database` | 领域 | 数据库 |
| `#interview-trap` | 笔记类型 | 面试陷阱笔记 |
| `#practice` | 笔记类型 | 练习题 |

## 注册新标签

当注入新内容产生未注册标签时：
1. 自动追加到本注册表
2. 标注 `层级` 和 `说明`
3. 标记 `[待审核]`，用户通过 dashboard → 审核标签 确认
```

### 10.5 自检清单 (Quality Checklist)

每次注入或批量更新后，运行自检确保 Vault 质量：

**结构检查**：
- [ ] 每个笔记都有完整的 YAML frontmatter（id, concept, frequency, domain, status, created_at）
- [ ] 每个笔记都有 `## Related Q&A` 和 `## Related Notes` 章节
- [ ] 每个笔记都有 `## Overview Table`
- [ ] 每个 Q&A 文件都有 `## Related Concepts` 反向链接
- [ ] 每个 Q&A 文件都有 `> [!hint]- 核心模式速查`
- [ ] 所有答案使用 `> [!answer]-` fold callout
- [ ] 所有标签来自 TAG-REGISTRY.md

**内容检查**：
- [ ] 每个概念至少关联 3 个 Q&A
- [ ] 每个 Q&A 文件 ≥8 题，题型分布达标
- [ ] 薄弱概念在 Exam Traps 中有对应条目
- [ ] Weak Areas 与 Exam Traps 双向链接
- [ ] 无孤立笔记（至少有一个 wiki-link 指向它）

**数据一致性检查**：
- [ ] schedule.json 总条目数 == stats.json total_questions
- [ ] 各 frequency 统计之和 == total_questions
- [ ] 无 `status: draft` 但 schedule 中已存在的条目

---

> **文档版本历史**
>
> | 版本 | 日期 | 说明 |
> |------|------|------|
> | 0.1 | 2026-05-25 | 初始版本，完整开发规范 |
> | 0.2 | 2026-06-05 | 新增：编号前缀目录结构、Exam Traps、Tag 注册表、Quiz Rules、笔记/Q&A 模板增强、tracking.granularity 配置、自检清单 |
