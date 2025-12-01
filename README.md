# Sitemap自动提交工具

这个工具可以自动解析网站的sitemap.xml，并将URL提交到百度搜索引擎，有助于提高网站在百度的收录速度。

## 功能特性

- 解析标准sitemap.xml格式
- 支持sitemap索引格式（包含多个子sitemap）
- 将URL保存到文件
- 自动提交到百度搜索引擎API
- 自动提交到必应搜索引擎API
- 支持命令行参数配置
- 详细的日志输出
- 使用GitHub Secrets保护敏感信息

## GitHub Secrets配置

为了安全地存储敏感信息，本工具使用GitHub Secrets。在您的仓库中需要设置以下Secrets：

1. 进入仓库的"Settings" > "Secrets and variables" > "Actions"
2. 点击"New repository secret"添加以下密钥：

- `BAIDU_TOKEN`: [您的百度站长平台token](https://ziyuan.baidu.com/site/index#/)
- `BING_API_KEY`: [您的必应站长平台API密钥](https://www.bing.com/webmasters/)
- `SITE_URL`: 您的网站URL（如：https://www.bonan.online）
- `SITEMAP_URL`: 您的sitemap URL（如：https://www.bonan.online/sitemap.xml）

## 本地使用
安装依赖

```bash
pip install -r requirements.txt
```

使用环境变量

`export BAIDU_TOKEN="YOUR_TOKEN"`

`export BING_API_KEY="YOUR_BING_API_KEY"`

`export SITE_URL="https://example.com"`

`export SITEMAP_URL="https://example.com/sitemap.xml"`

`python scripts/parse_sitemap.py --submit --verbose`

仅解析sitemap并保存URL到文件

`python parse_sitemap.py --sitemap https://example.com/sitemap.xml`

解析sitemap并提交URL到百度

`python parse_sitemap.py --sitemap https://example.com/sitemap.xml --site https://example.com --token YOUR_TOKEN --submit`

## 必应URL提交工具

### 单独使用必应提交工具

使用环境变量

`export BING_API_KEY="YOUR_BING_API_KEY"`

`export SITE_URL="https://example.com"`

`python submit_bing.py --verbose`

指定参数

`python submit_bing.py --site https://example.com --api-key YOUR_BING_API_KEY --urls-file urls.txt --verbose`

### 必应API说明

必应URL提交API使用以下格式：

```
POST /webmaster/api.svc/json/SubmitUrlbatch?apikey=YOUR_API_KEY HTTP/1.1
Content-Type: application/json; charset=utf-8
Host: ssl.bing.com

{
  "siteUrl": "http://yoursite.com",
  "urlList": [
    "http://yoursite.com/url1",
    "http://yoursite.com/url2",
    "http://yoursite.com/url3"
  ]
}
```

### 获取必应API密钥

1. 访问 [Bing Webmaster Tools](https://www.bing.com/webmasters/)
2. 登录您的微软账户
3. 添加并验证您的网站
4. 在设置中找到API密钥或生成新的API密钥

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Smartuil/AutoSEO&type=date&legend=top-left)](https://www.star-history.com/#Smartuil/AutoSEO&type=date&legend=top-left)



