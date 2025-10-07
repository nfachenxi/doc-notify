#!/bin/bash
# 文档更新通知服务部署脚本
# 适用于 Debian/Ubuntu 系统

set -e

echo "================================"
echo "文档更新通知服务 - 部署脚本"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 root 权限运行此脚本${NC}"
    echo "使用: sudo bash deploy.sh"
    exit 1
fi

# 获取当前目录
CURRENT_DIR=$(pwd)
SERVICE_NAME="doc-notify"

echo -e "${YELLOW}[1/7] 检查系统环境...${NC}"
# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}未找到 Python3，正在安装...${NC}"
    apt update
    apt install -y python3 python3-pip python3-venv
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"

echo -e "${YELLOW}[2/7] 创建虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

echo -e "${YELLOW}[3/7] 安装依赖包...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ 依赖包安装完成${NC}"

echo -e "${YELLOW}[4/7] 创建日志目录...${NC}"
mkdir -p logs
touch logs/access.log
touch logs/error.log
echo -e "${GREEN}✓ 日志目录创建完成${NC}"

echo -e "${YELLOW}[5/7] 配置 systemd 服务...${NC}"
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Document Update Notification Service
After=network.target

[Service]
Type=notify
User=$(logname 2>/dev/null || echo $SUDO_USER)
WorkingDirectory=${CURRENT_DIR}
Environment="PATH=${CURRENT_DIR}/venv/bin"
ExecStart=${CURRENT_DIR}/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile ${CURRENT_DIR}/logs/access.log --error-logfile ${CURRENT_DIR}/logs/error.log app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ systemd 服务配置完成${NC}"

echo -e "${YELLOW}[6/7] 启动服务...${NC}"
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

# 等待服务启动
sleep 2

if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✓ 服务启动成功${NC}"
else
    echo -e "${RED}✗ 服务启动失败，请检查日志${NC}"
    systemctl status ${SERVICE_NAME}
    exit 1
fi

echo -e "${YELLOW}[7/7] 配置防火墙（可选）...${NC}"
if command -v ufw &> /dev/null; then
    read -p "是否开放 5000 端口？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ufw allow 5000/tcp
        echo -e "${GREEN}✓ 防火墙规则已添加${NC}"
    fi
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "服务状态: systemctl status ${SERVICE_NAME}"
echo "查看日志: tail -f logs/access.log"
echo "重启服务: systemctl restart ${SERVICE_NAME}"
echo "停止服务: systemctl stop ${SERVICE_NAME}"
echo ""
echo "本地访问地址: http://127.0.0.1:5000"
echo ""
echo -e "${YELLOW}⚠️  重要提示:${NC}"
echo "1. 请编辑 config.yaml 配置文件，添加您的 webhook 地址"
echo "2. 服务已在本地 5000 端口启动，请在 1Panel 中配置反向代理"
echo "3. 在 1Panel 中配置反向代理时，目标地址填写: http://127.0.0.1:5000"
echo "4. 建议在 1Panel 中同时配置 HTTPS 证书"
echo ""
echo -e "${GREEN}1Panel 反向代理配置参考:${NC}"
echo "  - 域名: notice.nfasystem.top"
echo "  - 代理地址: http://127.0.0.1:5000"
echo "  - 启用 HTTPS: 是"
echo "  - 传递真实 IP: 是"
echo ""
