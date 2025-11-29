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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_sitemap_urls(sitemap_url, verbose=False):
    """
    获取sitemap中的所有URL
    
    Args:
        sitemap_url (str): sitemap的URL
        verbose (bool): 是否输出详细信息
        
    Returns:
        list: URL列表
    """
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
    try:
        # 安全地构建API URL，避免日志泄露token
        masked_token = token[:4] + "***" + token[-4:] if len(token) > 8 else "***"
        api_url = f"http://data.zz.baidu.com/urls?site={site_url}&token={token}"
        
        if verbose:
            logger.info(f"正在提交URL到百度API (Token: {masked_token})")
            
        # 使用curl命令提交
        command = f'curl -H \'Content-Type:text/plain\' --data-binary @{urls_file} "{api_url}"'
        
        if verbose:
            # 在日志中隐藏token
            safe_command = command.replace(token, masked_token)
            logger.info(f"执行命令: {safe_command}")
            
        result = os.system(command)
        
        if verbose:
            logger.info(f"命令执行结果: {result}")
            
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
    
    args = parser.parse_args()
    
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

if __name__ == "__main__":
    main()
