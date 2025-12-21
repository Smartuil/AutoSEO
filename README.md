# AutoSEO - Sitemap自动提交工具

这个工具可以自动解析网站的sitemap.xml，并将URL提交到百度和必应搜索引擎，有助于提高网站的收录速度。

## 功能特性

- 解析标准sitemap.xml格式
- 支持sitemap索引格式（包含多个子sitemap）
- 将URL保存到文件
- 自动提交到百度搜索引擎API
- 自动提交到必应搜索引擎API
- 支持命令行参数配置
- 详细的日志输出
- 使用GitHub Secrets保护敏感信息

## 安装依赖

```bash
pip install -r requirements.txt
```

## 工具模块

现在工具已经拆分为两个独立的脚本：

### 1. parse_sitemap.py - Sitemap解析工具
用于解析sitemap.xml文件并提取URL列表。

**使用方法：**
```bash
# 基本用法
python parse_sitemap.py

# 指定sitemap URL
python parse_sitemap.py --sitemap https://example.com/sitemap.xml

# 指定输出文件
python parse_sitemap.py --output my_urls.txt

# 显示详细信息
python parse_sitemap.py --verbose

# 自定义日志文件
python parse_sitemap.py --log-file custom.log
```

**参数说明：**
- `--sitemap`: sitemap的URL (默认: 环境变量SITEMAP_URL或https://www.bonan.online/sitemap.xml)
- `--output`: 输出URL的文件名 (默认: urls.txt)
- `--verbose`: 输出详细信息
- `--log-file`: 日志文件路径 (默认: parse_sitemap.log)

### 2. submit_baidu.py - 百度URL提交工具
专门用于将URL列表提交到百度搜索引擎。

**使用方法：**
```bash
# 基本用法 (需要设置BAIDU_TOKEN环境变量)
python submit_baidu.py

# 指定token
python submit_baidu.py --token your_baidu_token

# 指定网站URL
python submit_baidu.py --site https://example.com

# 指定URL文件
python submit_baidu.py --urls-file my_urls.txt

# 显示详细信息
python submit_baidu.py --verbose

# 随机选择20个URL提交
python submit_baidu.py --random 20

# 自定义日志文件
python submit_baidu.py --log-file submit.log
```

**参数说明：**
- `--site`: 网站URL (默认: 环境变量SITE_URL或https://www.bonan.online)
- `--token`: 百度站长平台的token (默认: 环境变量BAIDU_TOKEN)
- `--urls-file`: 包含URL的文件路径 (默认: urls.txt)
- `--verbose`: 输出详细信息
- `--random`: 随机选择N个URL提交 (默认: 10，百度每次限制10个)
- `--log-file`: 日志文件路径 (默认: submit_baidu.log)

### 3. submit_bing.py - 必应URL提交工具
专门用于将URL列表提交到必应搜索引擎。

**使用方法：**
```bash
# 使用环境变量
export BING_API_KEY="YOUR_BING_API_KEY"
export SITE_URL="https://example.com"
python submit_bing.py --verbose

# 指定参数
python submit_bing.py --site https://example.com --api-key YOUR_BING_API_KEY --urls-file urls.txt --verbose

# 随机选择50个URL提交
python submit_bing.py --random 50
```

**参数说明：**
- `--site`: 网站URL (默认: 环境变量SITE_URL或https://www.bonan.online)
- `--api-key`: 必应站长平台的API密钥 (默认: 环境变量BING_API_KEY)
- `--urls-file`: 包含URL的文件路径 (默认: urls.txt)
- `--verbose`: 输出详细信息
- `--random`: 随机选择N个URL提交 (默认: 100)
- `--log-file`: 日志文件路径 (默认: submit_bing.log)

## 完整工作流程

1. **解析sitemap**:
   ```bash
   python parse_sitemap.py --sitemap https://yoursite.com/sitemap.xml --output urls.txt
   ```

2. **提交到百度**:
   ```bash
   python submit_baidu.py --site https://yoursite.com --token your_token --urls-file urls.txt
   ```

3. **提交到必应**:
   ```bash
   python submit_bing.py --site https://yoursite.com --api-key your_bing_api_key --urls-file urls.txt
   ```

## 环境变量配置

可以通过设置环境变量来避免每次输入参数：

**Linux/Mac:**
```bash
export SITEMAP_URL=https://yoursite.com/sitemap.xml
export SITE_URL=https://yoursite.com
export BAIDU_TOKEN=your_baidu_token
export BING_API_KEY=your_bing_api_key
```

**Windows:**
```bash
set SITEMAP_URL=https://yoursite.com/sitemap.xml
set SITE_URL=https://yoursite.com
set BAIDU_TOKEN=your_baidu_token
set BING_API_KEY=your_bing_api_key
```

## GitHub Secrets配置

为了安全地存储敏感信息，本工具支持GitHub Secrets。在您的仓库中需要设置以下Secrets：

1. 进入仓库的"Settings" > "Secrets and variables" > "Actions"
2. 点击"New repository secret"添加以下密钥：

- `BAIDU_TOKEN`: [您的百度站长平台token](https://ziyuan.baidu.com/site/index#/)
- `BING_API_KEY`: [您的必应站长平台API密钥](https://www.bing.com/webmasters/)
- `SITE_URL`: 您的网站URL（如：https://www.bonan.online）
- `SITEMAP_URL`: 您的sitemap URL（如：https://www.bonan.online/sitemap.xml）

## API密钥获取

### 百度站长平台Token
1. 访问 [百度站长平台](https://ziyuan.baidu.com/site/index#/)
2. 登录您的百度账号
3. 添加并验证您的网站
4. 在"数据引入" > "链接提交"中找到您的token

### 必应API密钥
1. 访问 [Bing Webmaster Tools](https://www.bing.com/webmasters/)
2. 登录您的微软账户
3. 添加并验证您的网站
4. 在设置中找到API密钥或生成新的API密钥

## 必应API说明

必应URL提交API使用以下格式：

```http
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

## 日志文件

- `parse_sitemap.log`: sitemap解析日志
- `submit_baidu.log`: 百度提交日志
- `submit_bing.log`: 必应提交日志

两个工具都支持详细的日志记录，包括错误信息和调试信息。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Smartuil/AutoSEO&type=date&legend=top-left)](https://www.star-history.com/#Smartuil/AutoSEO&type=date&legend=top-left)