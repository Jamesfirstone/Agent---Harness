param(
    [string]$Manifest = "$PSScriptRoot\selected_repositories.json",
    [string]$Destination = "$PSScriptRoot\..\..\repos\supplement"
)

$ErrorActionPreference = "Continue"
$repositories = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$log = [System.Collections.Generic.List[object]]::new()

foreach ($repository in $repositories) {
    $target = Join-Path $Destination $repository.id
    if (Test-Path -LiteralPath (Join-Path $target ".git")) {
        $commit = git -C $target rev-parse HEAD
        $log.Add([pscustomobject]@{id=$repository.id; category=$repository.category; status="existing"; url=$repository.url; commit=$commit; error=$null})
        continue
    }
    git clone --depth 1 --filter=blob:none $repository.url $target 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -eq 0) {
        $commit = git -C $target rev-parse HEAD
        $log.Add([pscustomobject]@{id=$repository.id; category=$repository.category; status="cloned"; url=$repository.url; commit=$commit; error=$null})
    } else {
        $log.Add([pscustomobject]@{id=$repository.id; category=$repository.category; status="failed"; url=$repository.url; commit=$null; error="git clone exit code $LASTEXITCODE"})
    }
}

$logPath = Join-Path $Destination "clone_log.json"
$log | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $logPath -Encoding utf8
$log | Format-Table -AutoSize
$failureCount = @($log | Where-Object status -eq "failed").Count
if ($failureCount -gt 0) { exit 2 }
