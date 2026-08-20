param(
    [string]$Manifest = "$PSScriptRoot\selected_papers.json",
    [string]$Destination = "$PSScriptRoot\..\..\papers\supplement"
)

$ErrorActionPreference = "Stop"
$papers = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$log = [System.Collections.Generic.List[object]]::new()

foreach ($paper in $papers) {
    $target = Join-Path $Destination ($paper.id + ".pdf")
    $urls = @($paper.url)
    if ($paper.fallback_url) { $urls += $paper.fallback_url }
    $success = $false
    $errorText = $null
    foreach ($url in $urls) {
        try {
            Invoke-WebRequest -Uri $url -OutFile $target -MaximumRedirection 8 -Headers @{"User-Agent"="Mozilla/5.0 research-archiver/1.0"}
            $head = [System.IO.File]::ReadAllBytes($target)[0..4]
            $signature = [System.Text.Encoding]::ASCII.GetString($head)
            if ($signature -ne "%PDF-") { throw "Downloaded response is not a PDF ($signature)" }
            $success = $true
            $log.Add([pscustomobject]@{id=$paper.id; status="downloaded"; url=$url; path=$target; error=$null})
            break
        } catch {
            $errorText = $_.Exception.Message
            if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
        }
    }
    if (-not $success) {
        $log.Add([pscustomobject]@{id=$paper.id; status="failed"; url=($urls -join " | "); path=$target; error=$errorText})
    }
}

$logPath = Join-Path $Destination "download_log.json"
$log | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $logPath -Encoding utf8
$log | Format-Table -AutoSize
if (($log | Where-Object status -eq "failed").Count -gt 0) { exit 2 }
