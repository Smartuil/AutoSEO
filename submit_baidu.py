#!/usr/bin/env python3
"""
百度URL提交工具
专门用于将URL列表提交到百度搜索引擎
"""

import requests
import argparse
import sys
import os
import logging
import logging.handlers
import urllib.parse
import random
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

def submit_to_baidu(site_url, token, urls_file, verbose=False, random_count=0):
    """
    提交URL到百度搜索引擎
    
    Args:
        site_url (str): 网站URL
        token (str): 百度站长平台的token
        urls_file (str): 包含URL的文件路径
        verbose (bool): 是否输出详细信息
        random_count (int): 随机选择的URL数量，0表示不启用随机选择
    """
    logger = logging.getLogger(__name__)
    try:
        # 验证和清理参数
        if not site_url or not token or not urls_file:
            raise ValueError("site_url、token和urls_file不能为空")
        
        # 检查URL文件是否存在
        if not os.path.exists(urls_file):
            raise FileNotFoundError(f"URL文件不存在: {urls_file}")
        
        # 安全地构建API URL，避免日志泄露token
        masked_token = token[:4] + "***" + token[-4:] if len(token) > 8 else "***"
        
        # 处理site_url，百度API需要不带协议的域名格式
        site_url = site_url.strip()
        # 移除协议头
        if site_url.startswith('https://'):
            site_url = site_url[8:]
        elif site_url.startswith('http://'):
            site_url = site_url[7:]
        # 移除末尾斜杠
        site_url = site_url.rstrip('/')
            
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
        
        # 读取URL文件
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls_data = f.read().strip()
        
        if not urls_data:
            logger.warning("URL文件为空，没有URL可以提交")
            return
        
        # 解析URL列表
        urls_list = [url.strip() for url in urls_data.split('\n') if url.strip()]
        
        # 如果启用随机选择，从URL列表中随机选择指定数量
        if random_count > 0:
            original_count = len(urls_list)
            if original_count > random_count:
                urls_list = random.sample(urls_list, random_count)
                logger.info(f"随机选择模式: 从 {original_count} 个URL中随机选择了 {random_count} 个")
            else:
                logger.info(f"随机选择模式: URL总数({original_count})不超过{random_count}个，将全部提交")
        
        # 重新组装URL数据
        urls_data = '\n'.join(urls_list)
        
        headers = {
            'Content-Type': 'text/plain'
        }
        
        url_count = len(urls_list)
        if verbose:
            logger.info(f"提交的URL数量: {url_count}")
            logger.info("正在发送请求到百度API...")
            logger.info(f"请求URL: {api_url.replace(token, masked_token)}")
            logger.info(f"请求头: {headers}")
            logger.info(f"请求体 (URLs):\n{urls_data}")
            
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
    parser = argparse.ArgumentParser(description='提交URL到百度搜索引擎')
    parser.add_argument('--site', 
                        default=os.environ.get('SITE_URL', 'https://www.bonan.online'),
                        help='网站URL')
    parser.add_argument('--token', 
                        default=os.environ.get('BAIDU_TOKEN', ''),
                        help='百度站长平台的token')
    parser.add_argument('--urls-file', default='urls.txt',
                        help='包含URL的文件路径')
    parser.add_argument('--verbose', action='store_true',
                        help='输出详细信息')
    parser.add_argument('--random', type=int, default=10, metavar='N',
                        help='随机选择N个URL提交（默认: 10）')
    parser.add_argument('--log-file', default='submit_baidu.log',
                        help='日志文件路径 (默认: submit_baidu.log)')
    
    args = parser.parse_args()
    
    # 获取日志文件路径
    log_file = args.log_file
    
    # 初始化日志系统
    logger = setup_logging(log_file, args.verbose)
    
    logger.info("=" * 50)
    logger.info("百度URL提交工具启动")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 50)
    
    # 检查token是否为空
    if not args.token:
        logger.error("提交到百度需要token，请通过--token参数或BAIDU_TOKEN环境变量提供")
        sys.exit(1)
    
    # 提交URL到百度
    submit_to_baidu(args.site, args.token, args.urls_file, args.verbose, args.random)
    
    logger.info("=" * 50)
    logger.info("程序执行完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()