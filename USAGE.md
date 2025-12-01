# AutoSEO 工具使用说明

## 功能拆分

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

# 自定义日志文件
python submit_baidu.py --log-file submit.log
```

**参数说明：**
- `--site`: 网站URL (默认: 环境变量SITE_URL或https://www.bonan.online)
- `--token`: 百度站长平台的token (默认: 环境变量BAIDU_TOKEN)
- `--urls-file`: 包含URL的文件路径 (默认: urls.txt)
- `--verbose`: 输出详细信息
- `--log-file`: 日志文件路径 (默认: submit_baidu.log)

## 工作流程

1. **解析sitemap**:
   ```bash
   python parse_sitemap.py --sitemap https://yoursite.com/sitemap.xml --output urls.txt
   ```

2. **提交到百度**:
   ```bash
   python submit_baidu.py --site https://yoursite.com --token your_token --urls-file urls.txt
   ```

## 环境变量

可以通过设置环境变量来避免每次输入参数：

```bash
# Windows
set SITEMAP_URL=https://yoursite.com/sitemap.xml
set SITE_URL=https://yoursite.com
set BAIDU_TOKEN=your_baidu_token

# Linux/Mac
export SITEMAP_URL=https://yoursite.com/sitemap.xml
export SITE_URL=https://yoursite.com
export BAIDU_TOKEN=your_baidu_token
```

## 日志文件

- `parse_sitemap.log`: sitemap解析日志
- `submit_baidu.log`: 百度提交日志

两个工具都支持详细的日志记录，包括错误信息和调试信息。