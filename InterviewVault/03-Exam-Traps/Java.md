---
domain: "Java"
keywords: exam-traps, interview, java
updated_at: "2026-06-07"
---

# Java — 面试陷阱

#interview-traps #java

> [!warning] 本笔记用途
> 记录 Java 领域面试中最容易踩坑、最容易混淆的知识点。
---

## JVM 垃圾回收机制

> [!danger]- 陷阱：JVM 垃圾回收机制 常见错误
> - **什么陷阱**：混淆了引用计数和可达性分析
> - **为什么容易错**：复习时评分较低
> - **正确理解**：Java使用可达性分析，GC Roots包括栈帧局部变量、静态变量等
> - **踩分回答**：请结合具体场景分析
> - [[01-Notes/...|概念笔记]]
> - [[02-Questions/...|面试问答]]

