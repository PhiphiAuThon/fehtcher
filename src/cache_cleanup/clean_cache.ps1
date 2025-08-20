# Clean Python Cache Script
# Removes all __pycache__ folders and .pyc files from the project

Write-Host "🧹 Cleaning Python cache files..." -ForegroundColor Green

# Count cache folders before cleanup
$cacheFolders = Get-ChildItem -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
$pycFiles = Get-ChildItem -Recurse -File -Name "*.pyc" -ErrorAction SilentlyContinue

$totalCacheFolders = $cacheFolders.Count
$totalPycFiles = $pycFiles.Count

if ($totalCacheFolders -eq 0 -and $totalPycFiles -eq 0) {
    Write-Host "✅ No cache files found - project is already clean!" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $totalCacheFolders __pycache__ folders and $totalPycFiles .pyc files" -ForegroundColor Yellow

# Remove all __pycache__ folders
if ($totalCacheFolders -gt 0) {
    Write-Host "🗑️  Removing __pycache__ folders..." -ForegroundColor Cyan
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item -Recurse -Force $_ -ErrorAction SilentlyContinue
        Write-Host "  Removed: $_" -ForegroundColor Gray
    }
}

# Remove all .pyc files
if ($totalPycFiles -gt 0) {
    Write-Host "🗑️  Removing .pyc files..." -ForegroundColor Cyan
    Get-ChildItem -Recurse -File -Name "*.pyc" | ForEach-Object {
        Remove-Item -Force $_ -ErrorAction SilentlyContinue
        Write-Host "  Removed: $_" -ForegroundColor Gray
    }
}

Write-Host "✅ Cache cleanup completed!" -ForegroundColor Green
Write-Host "Removed $totalCacheFolders __pycache__ folders and $totalPycFiles .pyc files" -ForegroundColor Yellow
