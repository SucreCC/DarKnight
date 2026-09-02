# DarKnight Node Scripts

## darknight-node.sh

安装与管理 DarKnight Node：

```bash
sudo bash scripts/darknight-node.sh install
sudo bash scripts/darknight-node.sh install --name darknight-node2
sudo bash scripts/darknight-node.sh install-script
darknight-node help
sudo darknight-node core-update
```

## darknight.sh

由旧面板安装脚本品牌化而来的资产文件。  
**当前主面板请使用 `E:\kai\DarKnight` 的 docker compose 部署**，不要把本脚本当作官方主面板安装入口。

如需仅安装命令包装：

```bash
sudo bash scripts/darknight.sh install-script
```

## install_latest_xray.sh

从 [XTLS/Xray-core](https://github.com/XTLS/Xray-core) 安装最新 Xray，供 Dockerfile 与手动环境使用：

```bash
sudo bash scripts/install_latest_xray.sh
```
