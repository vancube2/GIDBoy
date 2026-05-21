# Apply GIDBoy fix bundle and push to GitHub
$bundle = Join-Path $PSScriptRoot "gidboy-fix.bundle"
if (-not (Test-Path $bundle)) {
    Write-Error "Bundle not found: $bundle"
    exit 1
}

$repo = Join-Path $PSScriptRoot ".git"
Set-Location $PSScriptRoot

git bundle unbundle $bundle
if ($LASTEXITCODE -ne 0) { exit 1 }

# The bundle contains main branch commits. Merge them into local main.
$bundleHead = git bundle list-heads $bundle | Select-String "main" | ForEach-Object { $_.ToString().Split()[0] }
if ($bundleHead) {
    git fetch $bundle main:main-temp
    git checkout main
    git merge main-temp --no-edit
    git branch -d main-temp
    git push origin main
    Write-Host "Pushed successfully!"
} else {
    Write-Error "Could not find main branch in bundle"
    exit 1
}
