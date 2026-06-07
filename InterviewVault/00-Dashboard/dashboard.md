---
tags: [dashboard, meta]
---

# 📊 学习面板

> 本文件由 dashboard Skill 动态更新。
> 使用 Obsidian Dataview 插件可获得更佳体验。

---

## 一、总体进度

```dataview
TABLE
  concept AS 概念,
  status AS 状态,
  choice(status = "mastered", "🔵", choice(status = "learning", "🟢", choice(status = "weak", "🔴", "⚪"))) AS 徽章,
  frequency AS 频率,
  domain AS 领域
FROM "01-Notes"
SORT
  choice(status = "draft", 0, choice(status = "weak", 1, choice(status = "learning", 2, 3))) ASC,
  frequency DESC
```

---

## 二、今日待复习

```dataview
TABLE
  concept AS 概念,
  choice(next_review < date(today), "🔴 已过期", "🟡 今日到期") AS 状态,
  next_review AS 复习日,
  interval AS 间隔,
  ease_factor AS 难度
FROM json(".progress/schedule.json")
WHERE next_review <= date(today)
  AND status != "mastered"
SORT next_review ASC, ease_factor ASC
```

---

## 三、按频率统计

| 频率 | 笔记数 | 题目数 | 已掌握 | 学习中 | 薄弱 |
|------|--------|--------|--------|--------|------|
| 🔴 必问 | `=length(filter(this.file.inlinks, (x) => x.frequency = "必问"))` | — | — | — | — |
| 🟡 常问 | `=length(filter(this.file.inlinks, (x) => x.frequency = "常问"))` | — | — | — | — |
| 🔵 冷门 | `=length(filter(this.file.inlinks, (x) => x.frequency = "冷门"))` | — | — | — | — |

> 💡 上述表格需配合 DataviewJS 使用，或运行 dashboard Skill 获取精确统计。

---

## 四、按领域统计

```dataview
TABLE
  length(rows) AS 笔记数,
  filter(rows, (r) => r.status = "mastered") AS 已掌握
FROM "01-Notes"
GROUP BY domain AS 领域
```

---

## 五、薄弱概念

```dataview
TABLE
  concept AS 概念,
  domain AS 领域,
  frequency AS 频率,
  file.mtime AS 最后更新
FROM "01-Notes"
WHERE status = "weak"
SORT file.mtime DESC
LIMIT 10
```

---

## 六、草稿待审核

```dataview
TABLE
  concept AS 概念,
  domain AS 领域,
  frequency AS 频率,
  created_at AS 创建日期
FROM "01-Notes"
WHERE status = "draft"
SORT created_at ASC
```

---

## 七、最近复习会话

```dataview
TABLE
  mode AS 模式,
  total_questions AS 题目数,
  completed AS 完成数,
  file.ctime AS 日期
FROM "04-Sessions"
SORT file.ctime DESC
LIMIT 5
```

---

## 八、管理操作

点击执行以下命令（需在 Claude Code 中输入）：

- `重新计算统计` → 从原始数据重新生成 stats.json
- `审核草稿` → 列出所有 draft 笔记供确认
- `导出复习报告` → 生成近期复习表现报告

---

## 九、快速链接

| 目录 | 说明 |
|------|------|
| [[01-Notes/High-Frequency/\|📚 高频笔记]] | 必问概念知识库 |
| [[01-Notes/Medium-Frequency/\|📚 中频笔记]] | 常问概念知识库 |
| [[02-Questions/High-Frequency/\|❓ 高频题库]] | 必问面试题 |
| [[03-Exam-Traps/\|⚠️ 面试陷阱]] | 易错点汇总 |
| [[04-Sessions/\|📝 复习记录]] | 历史会话 |
