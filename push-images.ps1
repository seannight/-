# 镜像构建与推送脚本
param (
    [string]$Environment = "dev"
)

$VERSION = Get-Date -Format "yyyyMMdd-HHmm"        
$REGISTRY = "localhost:5000/teddy_cup"

Write-Host "===== 开始构建 $Environment 环境镜像 ====="

# 构建镜像
docker build -t ${REGISTRY}/api:${Environment}-${VERSION} -t ${REGISTRY}/api:${Environment} -f docker/${Environment}/Dockerfile.api .

# 推送镜像到本地仓库
docker push ${REGISTRY}/api:${Environment}-${VERSION}
docker push ${REGISTRY}/api:${Environment}

Write-Host "===== 镜像已推送至私有仓库 ====="      
Write-Host "镜像标签: ${Environment}-${VERSION}"   
Write-Host "镜像标签: ${Environment}"
