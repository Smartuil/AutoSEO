#!/usr/bin/env python3
"""
必应URL提交工具
专门用于将URL列表提交到必应搜索引擎
"""

import requests
import argparse
import sys
import os
import logging
import logging.handlers
import json
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

def submit_to_bing(site_url, api_key, urls_file, verbose=False):
    """
    提交URL到必应搜索引擎
    
    Args:
        site_url (str): 网站URL
        api_key (str): 必应站长平台的API密钥
        urls_file (str): 包含URL的文件路径
        verbose (bool): 是否输出详细信息
    """
    logger = logging.getLogger(__name__)
    try:
        # 验证和清理参数
        if not site_url or not api_key or not urls_file:
            raise ValueError("site_url、api_key和urls_file不能为空")
        
        # 检查URL文件是否存在
        if not os.path.exists(urls_file):
            raise FileNotFoundError(f"URL文件不存在: {urls_file}")
        
        # 安全地处理API密钥，避免日志泄露
        masked_key = api_key[:4] + "***" + api_key[-4:] if len(api_key) > 8 else "***"
        
        # 确保site_url格式正确
        site_url = site_url.strip()
        if not site_url.startswith(('http://', 'https://')):
            site_url = 'https://' + site_url
            
        # 构建API URL
        api_url = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}"
        
        if verbose:
            logger.info(f"正在提交URL到必应API (API Key: {masked_key})")
            logger.info(f"站点URL: {site_url}")
            logger.info(f"API URL: {api_url.replace(api_key, masked_key)}")
        
        # 读取URL文件
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            logger.warning("URL文件为空，没有URL可以提交")
            return
        
        # 构建请求数据
        request_data = {
            "siteUrl": site_url,
            "urlList": urls
        }
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        if verbose:
            logger.info(f"提交的URL数量: {len(urls)}")
            logger.info("正在发送请求到必应API...")
            if verbose:
                logger.debug(f"请求体: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
            
        # 发送POST请求
        response = requests.post(api_url, 
                               data=json.dumps(request_data, ensure_ascii=False).encode('utf-8'), 
                               headers=headers, 
                               timeout=30)
        
        if response.status_code == 200:
            logger.info(f"成功提交URL到必应: {response.text}")
        else:
            logger.error(f"提交URL到必应失败: HTTP {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
    except Exception as e:
        logger.error(f"提交URL到必应时出错: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='提交URL到必应搜索引擎')
    parser.add_argument('--site', 
                        default=os.environ.get('SITE_URL', 'https://www.bonan.online'),
                        help='网站URL')
    parser.add_argument('--api-key', 
                        default=os.environ.get('BING_API_KEY', ''),
                        help='必应站长平台的API密钥')
    parser.add_argument('--urls-file', default='urls.txt',
                        help='包含URL的文件路径')
    parser.add_argument('--verbose', action='store_true',
                        help='输出详细信息')
    parser.add_argument('--log-file', default='submit_bing.log',
                        help='日志文件路径 (默认: submit_bing.log)')
    
    args = parser.parse_args()
    
    # 获取日志文件路径
    log_file = args.log_file
    
    # 初始化日志系统
    logger = setup_logging(log_file, args.verbose)
    
    logger.info("=" * 50)
    logger.info("必应URL提交工具启动")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 50)
    
    # 检查API密钥是否为空
    if not args.api_key:
        logger.error("提交到必应需要API密钥，请通过--api-key参数或BING_API_KEY环境变量提供")
        sys.exit(1)
    
    # 提交URL到必应
    submit_to_bing(args.site, args.api_key, args.urls_file, args.verbose)
    
    logger.info("=" * 50)
    logger.info("程序执行完成")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()