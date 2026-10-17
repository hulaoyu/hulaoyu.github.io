# 我的个人网站

一个由 AI Agent **Codex** 协助构建的静态个人网站。内容围绕三件事展开：

1. 当前使用的 AI Agent：Codex
2. 用它做的事：编写这个个人网站
3. 取得的效果：快速、便捷地完成了任务

## 文件结构

```text
.
├── index.html    # 页面结构
├── styles.css    # 视觉与响应式样式
├── script.js     # 菜单与滚动动效
└── README.md     # 说明文档
```

## 本地预览

直接用浏览器打开 `index.html` 即可查看。也可以使用任意静态服务器：

```bash
python -m http.server 8000
```

然后访问 <http://localhost:8000>。

## 部署到 GitHub Pages

1. 新建一个 GitHub 仓库，例如 `my-personal-site`。
2. 将本目录中的文件推送到仓库。
3. 在仓库页面打开 **Settings → Pages**。
4. 在 **Source** 中选择 `Deploy from a branch`，分支选择 `main`，目录选择 `/ (root)`。
5. 保存后，GitHub 会提供一个类似 `https://<用户名>.github.io/my-personal-site/` 的访问地址。

## 个性化修改

- 站点标题与副标题在 `index.html` 的 `<title>` 和首屏 `<h1>` 中。
- GitHub 链接目前指向 <https://github.com>，请替换为你自己的仓库地址（页面中所有 `https://github.com` 均可替换）。
- 主色、字体等样式集中在 `styles.css` 顶部的 `:root` 变量中。
