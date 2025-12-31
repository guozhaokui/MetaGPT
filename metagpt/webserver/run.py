#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MetaGPT Web Server 启动脚本
用法: python -m metagpt.webserver.run
或者: python metagpt/webserver/run.py
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="MetaGPT Web Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="开启热重载模式（开发用）",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数 (默认: 1)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="日志级别 (默认: info)",
    )

    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("错误: 请先安装 uvicorn")
        print("  pip install uvicorn[standard]")
        sys.exit(1)

    print(f"""
╔══════════════════════════════════════════════════════╗
║                MetaGPT Web Server                    ║
╠══════════════════════════════════════════════════════╣
║  🌐 地址: http://{args.host}:{args.port}                      
║  📚 API文档: http://{args.host}:{args.port}/docs              
║  🔄 热重载: {'开启' if args.reload else '关闭'}                               
╚══════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "metagpt.webserver.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()

