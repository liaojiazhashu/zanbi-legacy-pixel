# One-click 3-way backup sync: local -> server -> GitHub
# Usage: cd into project root, then run .\_sync_backup.ps1
$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Write-Output "===== Backup sync $stamp ====="

# 1. Check for changes
$changed = git status --porcelain 2>&1
if (-not $changed) {
    Write-Output "[skip] no changes, nothing to commit."
} else {
    $count = ($changed | Measure-Object).Count
    Write-Output "[1/4] $count changed file(s), staging..."
    git add -A 2>&1 | Out-Null
    Write-Output "[2/4] committing..."
    git commit -m "auto backup $stamp" 2>&1 | Select-Object -Last 2
}

# 3. Push to server
Write-Output "[3/4] pushing to server..."
git push server main 2>&1 | Select-Object -Last 3
if ($LASTEXITCODE -eq 0) { Write-Output "  server: OK" } else { Write-Output "  server: FAIL" }

# 4. Push to GitHub
Write-Output "[4/4] pushing to GitHub..."
git push origin main 2>&1 | Select-Object -Last 3
if ($LASTEXITCODE -eq 0) { Write-Output "  GitHub: OK" } else { Write-Output "  GitHub: FAIL" }

Write-Output "===== Done ====="
