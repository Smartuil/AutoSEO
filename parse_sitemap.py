#!/usr/bin/env python3
"""
Sitemap解析工具
用于解析sitemap.xml并提取URL列表
"""

import requests
from bs4 import BeautifulSoup
import argparse
import sys
import os
import time
import logging
import logging.handlers

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



def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='解析sitemap并提取URL列表')
    parser.add_argument('--sitemap', 
                        default=os.environ.get('SITEMAP_URL', 'https://www.bonan.online/sitemap.xml'),
                        help='sitemap的URL')
    parser.add_argument('--output', default='urls.txt',
                        help='输出URL的文件名')
    parser.add_argument('--verbose', action='store_true',
                        help='输出详细信息')
    parser.add_argument('--log-file', default='parse_sitemap.log',
                        help='日志文件路径 (默认: parse_sitemap.log)')
    
    args = parser.parse_args()
    
    # 获取日志文件路径
    log_file = args.log_file
    
    # 初始化日志系统
    logger = setup_logging(log_file, args.verbose)
    
    logger.info("=" * 50)
    logger.info("Sitemap解析工具启动")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 50)
    
    # 获取sitemap中的URL
    urls = get_sitemap_urls(args.sitemap, args.verbose)
    
    if not urls:
        logger.error("未能获取到任何URL，程序终止")
        sys.exit(1)
    
    # 保存URL到文件
    save_urls_to_file(urls, args.output)
    
    logger.info("=" * 50)
    logger.info("程序执行完成")
    logger.info(f"URL列表已保存到: {args.output}")
    logger.info("如需提交到百度，请使用: python submit_baidu.py --urls-file urls.txt")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
