# 开始使用

在模板仓库中为一个已存在的课题目录初始化研究记录：

```bash
python3 tools/init_project.py --project /path/to/your-project
```

使用 Python 3.9 或更新版本。工具遇到同名文件会停止。已有记录的项目按 [升级指南](EVOLUTION.md) 合并。

先填 `research/STATUS.md` 的总目标、可信结论和当前唯一下一步，再把分工与权限写进 `research/PREFERENCES.md`。已有详细研究简报时，从状态卡链接到它即可。

把这一句加入课题已有的 AI 入口：“读 research/STATUS.md 和 research/PREFERENCES.md 接手，只在本轮需要时追查对应证据。”

然后从一个会改变方法选择的问题开始。[每日节奏](DAILY_WORK.md) · [交接与导出](AI_HANDOFF.md)
