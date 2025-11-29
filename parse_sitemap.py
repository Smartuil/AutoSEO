#!/usr/bin/env python3
"""
Sitemap解析和百度URL提交工具
用于解析sitemap.xml并将URL提交到百度搜索引擎
"""

import requests
from bs4 import BeautifulSoup
import argparse
import sys
import os
import time
import logging
import logging.handlers
import urllib.parse
import shlex
from datetime import datetime

def setup_logging(log_file=None, verbose=False):
    """
    设置日志配置，同时输出到控制台和文件
    
    Args:
        log_file (str): 日志文件路径，如果为None则不输出到文件
        verbose (bool): 是否输出详细信息
    """
    # 创建logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO if not verbose else logging.DEBUG)
    
    # 清除已有的处理器
    logger.handlers = []
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 使用RotatingFileHandler，防止日志文件过大
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"日志将保存到文件: {log_file}")
    
    return logger

def get_sitemap_urls(sitemap_url, verbose=False):
    """
    获取sitemap中的所有URL
    
    Args:
        sitemap_url (str): sitemap的URL
        verbose (bool): 是否输出详细信息
        
    Returns:
        list: URL列表
    """
    logger = logging.getLogger(__name__)
    urls = []
    
    try:
        if verbose:
            logger.info(f"正在获取sitemap: {sitemap_url}")
            
        # 获取 sitemap.xml 内容
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()
        
        # 解析 XML
        soup = BeautifulSoup(response.content, 'xml')
        
        # 处理标准sitemap格式
        for url in soup.find_all('url'):
            loc = url.find('loc')
            if loc:
                urls.append(loc.text)
        
        # 处理sitemap索引格式
        if not urls:
            if verbose:
                logger.info("未找到URL，检查是否为sitemap索引...")
                
            for sitemap in soup.find_all('sitemap'):
                loc = sitemap.find('loc')
                if loc:
                    sitemap_child_url = loc.text
                    if verbose:
                        logger.info(f"正在处理子sitemap: {sitemap_child_url}")
                    
                    # 添加短暂延迟，避免请求过于频繁
                    time.sleep(0.5)
                    
                    try:
                        child_response = requests.get(sitemap_child_url, timeout=30)
                        child_response.raise_for_status()
                        child_soup = BeautifulSoup(child_response.content, 'xml')
                        
                        for url in child_soup.find_all('url'):
                            loc = url.find('loc')
                            if loc:
                                urls.append(loc.text)
                    except Exception as e:
                        if verbose:
                            logger.error(f"处理子sitemap出错: {sitemap_child_url}, 错误: {str(e)}")
        
        if verbose:
            logger.info(f"从sitemap中提取到 {len(urls)} 个URL")
            
        return urls
        
    except Exception as e:
        logger.error(f"解析sitemap时出错: {str(e)}")
        return []

def save_urls_to_file(urls, filename):
    """
    将URL列表保存到文件
    
    Args:
        urls (list): URL列表
        filename (str): 输出文件名
    """
    logger = logging.getLogger(__name__)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        logger.info(f"已保存 {len(urls)} 个URL到 {filename}")
        
        # 输出前5个URL用于验证
        if urls:
            logger.info("前5个URL预览:")
            for i, url in enumerate(urls[:5]):
                logger.info(f"{i+1}. {url}")
                
    except Exception as e:
        logger.error(f"保存URL到文件时出错: {str(e)}")

def submit_to_baidu(site_url, token, urls_file, verbose=False):
    """
    提交URL到百度搜索引擎
    
    Args:
        site_url (str): 网站URL
        token (str): 百度站长平台的token
        urls_file (str): 包含URL的文件路径
        verbose (bool): 是否输出详细信息
    """
    logger = logging.getLogger(__name__)
    try:
        # 验证和清理参数
        if not site_url or not token or not urls_file:
            raise ValueError("site_url、token和urls_file不能为空")
        
        # 安全地构建API URL，避免日志泄露token
        masked_token = token[:4] + "***" + token[-4:] if len(token) > 8 else "***"
        
        # 使用urllib.parse确保URL格式正确
        site_url = site_url.strip()
        if not site_url.startswith(('http://', 'https://')):
            site_url = 'https://' + site_url
            
        # 构建API URL
        params = {
            'site': site_url,
            'token': token
        }
        
        # 使用urllib.parse构建查询字符串
        query_string = urllib.parse.urlencode(params)
        api_url = f"http://data.zz.baidu.com/urls?{query_string}"
        
        if verbose:
            logger.info(f"正在提交URL到百度API (Token: {masked_token})")
            logger.info(f"站点URL: {site_url}")
            logger.info(f"API URL: {api_url.replace(token, masked_token)}")
        
        # 使用Python requests而不是curl命令，避免URL格式问题
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls_data = f.read()
        
        headers = {
            'Content-Type': 'text/plain'
        }
        
        if verbose:
            logger.info(f"提交的URL数量: {len(urls_data.split())}")
            logger.info("正在发送请求到百度API...")
            
        # 使用Python requests发送请求
        response = requests.post(api_url, data=urls_data.encode('utf-8'), headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"成功提交URL到百度: {response.text}")
        else:
            logger.error(f"提交URL到百度失败: HTTP {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
    except Exception as e:
        logger.error(f"提交URL到百度时出错: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='解析sitemap并提交URL到百度搜索引擎')
    parser.add_argument('--sitemap', 
                        default=os.environ.get('SITEMAP_URL', 'https://www.bonan.online/sitemap.xml'),
                        help='sitemap的URL')
    parser.add_argument('--output', default='urls.txt',
                        help='输出URL的文件名')
    parser.add_argument('--site', 
                        default=os.environ.get('SITE_URL', 'https://www.bonan.online'),
                        help='网站URL')
    parser.add_argument('--token', 
                        default=os.environ.get('BAIDU_TOKEN', ''),
                        help='百度站长平台的token')
    parser.add_argument('--submit', action='store_true',
                        help='是否提交URL到百度')
    parser.add_argument('--verbose', action='store_true',
                        help='输出详细信息')
    parser.add_argument('--log-file', default='logfile.log',
                        help='日志文件路径 (默认: logfile.log)')
    
    args = parser.parse_args()
    
    # 获取日志文件路径
    log_file = args.log_file
    
    # 初始化日志系统
    logger = setup_logging(log_file, args.verbose)
    
    logger.info("=" * 50)
    logger.info("Sitemap解析和百度URL提交工具启动")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 50)
    
    # 检查token是否为空
    if args.submit and not args.token:
        logger.error("提交到百度需要token，请通过--token参数或BAIDU_TOKEN环境变量提供")
        sys.exit(1)
    
    # 获取sitemap中的URL
    urls = get_sitemap_urls(args.sitemap, args.verbose)
    
    if not urls:
        logger.error("未能获取到任何URL，程序终止")
        sys.exit(1)
    
    # 保存URL到文件
    save_urls_to_file(urls, args.output)
    
    # 如果指定了提交参数，则提交到百度
    if args.submit:
        submit_to_baidu(args.site, args.token, args.output, args.verbose)
    
    logger.info("=" * 50)
    logger.info("程序执行完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
