param (
    [switch]$Restore,
    [string]$BackupPath
)

# 创建备份目录
$backupDir = "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -Path $backupDir -ItemType Directory
    Write-Host "✅ 已创建备份目录: $backupDir"
}

# 如果指定了还原选项
if ($Restore) {
    if (-not $BackupPath) {
        Write-Host "❌ 错误: 还原操作需要指定备份文件路径"
        Write-Host "示例: .\scripts\backup-data.ps1 -Restore -BackupPath .\backups\data_20250320.zip"
        exit 1
    }

    if (-not (Test-Path $BackupPath)) {
        Write-Host "❌ 错误: 备份文件不存在: $BackupPath"
        exit 1
    }

    # 创建还原目录
    $restoreDir = "data_restored"
    if (Test-Path $restoreDir) {
        Remove-Item -Path $restoreDir -Recurse -Force
    }
    
    Write-Host "正在还原数据..."
    Expand-Archive -Path $BackupPath -DestinationPath $restoreDir
    
    Write-Host "✅ 数据已还原到: $restoreDir"
    Write-Host "请手动将需要的文件复制到data目录"
} else {
    # 创建备份
    $date = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$backupDir\data_$date.zip"
    
    # 检查data目录是否存在
    if (-not (Test-Path "data")) {
        Write-Host "❌ 错误: data目录不存在"
        exit 1
    }
    
    Write-Host "正在备份数据..."
    Compress-Archive -Path "data\*" -DestinationPath $backupFile -Force
    
    Write-Host "✅ 数据已备份到: $backupFile"
} 