 本项目已经停止维护，请转而使用由本人开发的Obsidian插件：[obsidian-hexo-publisher](https://github.com/zhenlohuang/obsidian-hexo-publisher)

# obsidian-hexo-publisher

obsidian-hexo-publisher是一个将Obsidian笔记发布到Hexo的脚本。目前仅实现了笔记文件及其保护的附件的搬运动作，博客的发布动作需要用户通过hexo命令自行完成。

## 使用方法
需要在笔记的metadata中添加
```
publish: true
```

执行
```
python3 obsidian_to_hexo.py --obsidian /path/to/obsidian/vault --hexo /path/to/hexo
```
