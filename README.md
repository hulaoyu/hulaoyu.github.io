# 胡天宇的小站

一个纯静态的个人站：左侧栏 + 文章流 + 分类 / 标签 / 归档，外加一个真的在训练的
MLP 交互观测台。版式参考 [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy)
的骨架（[liuzr-523.github.io](https://liuzr-523.github.io) 用的就是它），配色换成观测台
那套纸白、墨黑、朱红与青。

没有构建依赖：没有 Ruby、没有 Node、没有一个外部请求。所有页面都能离线打开。

## 目录

```text
site/
├── index.html              首页（文章列表）
├── projects.html           作品（观测台 + 这个小站）
├── categories.html         分类
├── tags.html               标签
├── archives.html           归档
├── about.html              关于
├── 404.html                404
├── feed.xml                RSS（由构建脚本生成）
├── sitemap.xml / robots.txt
├── posts/
│   ├── mlp-observatory.html
│   ├── codex-built-this.html
│   ├── keep-the-process.html
│   ├── ledger-of-25.html
│   └── single-file.html
├── mlp/index.html          MLP 观测台（单文件，可交互）
├── assets/
│   ├── css/site.css        全部样式（明暗两套变量）
│   ├── js/site.js          主题、抽屉、搜索、目录高亮、阅读进度、复制
│   ├── data/posts.js       搜索索引（构建时生成）
│   └── img/                头像、favicon、文章配图
├── content/                源文件：页面对应的 HTML 片段
│   └── posts/*.html        每篇文章 = 一段 meta + 正文
├── tools/build.py          构建脚本（只用 Python 标准库）
└── README.md
```

`content/` 是源，根目录的 HTML 是产物。日常只改 `content/`，然后重跑构建。

## 本地预览

直接双击 `index.html` 也能看：搜索索引是 `assets/data/posts.js`，没有 `fetch`，所以
`file://` 下所有功能都正常。

想要更接近线上，起一个静态服务：

```bash
python -m http.server 8000
# 然后打开 http://localhost:8000
```

## 改内容

### 写一篇新文章

1. 复制 `content/posts/single-file.html` 为 `content/posts/我的文章.html`。
2. 改开头那段 meta：

   ```html
   <!--meta
   {
     "slug": "my-post",              ← 输出文件名 posts/my-post.html
     "title": "文章标题",
     "date": "2026-12-01",           ← YYYY-MM-DD
     "categories": ["随笔"],
     "tags": ["随笔", "建站"],
     "excerpt": "一两句话的摘要，会出现在列表页和搜索结果里。",
     "pinned": false
   }
   -->
   ```

3. 往下写正文。`<h2 id="…">` / `<h3 id="…">` 会自动进右侧目录；图片用
   `%rel%assets/img/…` 开头，构建时会换成正确的相对路径。
4. 重新构建：

   ```bash
   python tools/build.py
   ```

首页、分类、标签、归档、搜索索引、RSS、站点地图都会一起更新。

### 改站名 / 简介 / 链接

都在 `tools/build.py` 顶部的 `SITE` 字典里：站名、tagline、简介、GitHub 地址、站点
URL、版权年份。改完重跑构建。

头像在 `assets/img/avatar.svg`，站点图标在 `assets/img/favicon.svg`。

### 改配色

`assets/css/site.css` 顶部两组变量：`:root[data-theme="light"]` 和
`:root[data-theme="dark"]`。主色是 `--accent`（朱红），辅色是 `--teal`（青）。

## 发布到 GitHub Pages

构建产物就是根目录里的 HTML，所以把 `site/` 里的**全部内容**（不是 `site` 文件夹
本身）上传到仓库根目录即可。

**个人站**（`https://<用户名>.github.io/`）

1. 仓库名必须是 `<用户名>.github.io`，全小写。
2. 上传后进 **Settings → Pages → Build and deployment**，Source 选
   **Deploy from a branch**，分支 `main`、目录 `/ (root)`。
3. 等一分钟访问站点。

**项目站**（`https://<用户名>.github.io/<仓库名>/`）

同样上传。站内链接全部是相对路径，可以直接用；只有两处需要按仓库名检查：

- `tools/build.py` 里的 `SITE["url"]`（影响 RSS、`sitemap.xml`、canonical、分享卡片）；
- `404.html` 由构建脚本生成，路径同样是相对的，一般不用动。

`.nojekyll` 已经放在根目录，避免 GitHub Pages 把带下划线的文件交给 Jekyll 处理。

### 发布后一直没有网址 / 一直 404

按这个顺序查，通常第一条就命中：

1. **仓库是不是私有的**。免费账号的 Pages 只对公开仓库开放。私有仓库在
   Settings → Pages 里会提示升级，也不会给出地址。改成 Public（Settings → General →
   Danger Zone → Change visibility）即可。
2. **Source 有没有真正保存**。Settings → Pages → Build and deployment → Source 必须是
   **Deploy from a branch**，分支 `main`、目录 `/ (root)`，然后点 **Save**。没点 Save
   就一直不会有地址。
3. **`index.html` 是否在仓库第一层**。如果把 `site` 文件夹整个传上去，根地址下没有
   `index.html`，页面会是 404（地址本身仍会生成，但访问的是 `/site/`）。正确做法是传
   `site/` **里面的内容**。
4. **分支名对不对**。老仓库默认分支可能是 `master`，而 Pages 选的是 `main`。两边要一致。
5. **选错成 GitHub Actions 却没有工作流**。Pages 会一直显示等待部署。要么改回分支部署，
   要么把仓库根目录的 `.github/workflows/pages.yml` 一起传上去（它能自动发布 `site/`）。
6. **账号邮箱未验证 / 组织禁用了 Pages**。这两种情况下 Pages 选项会缺失或不可保存。

地址不会立刻出现：分支部署通常 1 分钟，Actions 首次要 2–5 分钟。构建失败时去
**Actions** 标签页或仓库的 **Deployments** 看日志，比盯着 Pages 页面有效。

## 说明

- 站内没有分析脚本、没有第三方字体、没有任何外部请求。
- 搜索是本地子串匹配（标题权重最高，其次标签、正文摘要），中文不需要分词。
- 主题三态（浅色 / 深色 / 跟随系统）存在 `localStorage`，首屏用内联脚本提前定色，
  不会闪白。
- 文章内容整理自 <https://hulaoyu.github.io/> 与
  <https://hulaoyu.github.io/hulaoyu-/>，观测台是其中的单页演示。
