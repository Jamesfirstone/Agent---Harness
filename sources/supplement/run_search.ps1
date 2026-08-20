param(
    [string]$OutputDir = "$PSScriptRoot/search_raw"
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$queries = @(
    [PSCustomObject]@{ id = 'q1'; text = 'LLM agent runtime policy enforcement guardrail'; arxiv = 'all:"LLM agent" AND (all:"runtime enforcement" OR all:guardrail OR all:"policy enforcement")' },
    [PSCustomObject]@{ id = 'q2'; text = 'LLM agent tool call authorization privilege control'; arxiv = 'all:"LLM agent" AND (all:"tool call" OR all:"function calling") AND (all:authorization OR all:privilege OR all:policy)' },
    [PSCustomObject]@{ id = 'q3'; text = 'language model agent execution isolation sandbox capability'; arxiv = '(all:"language model agent" OR all:"LLM agent") AND (all:isolation OR all:sandbox OR all:capability)' },
    [PSCustomObject]@{ id = 'q4'; text = 'LLM agent runtime monitoring invariant contract'; arxiv = 'all:"LLM agent" AND (all:"runtime monitoring" OR all:invariant OR all:contract)' }
)

$summary = @()

function Save-Response {
    param([string]$Database, [string]$QueryId, [string]$Url, [string]$Extension = 'json')
    $target = Join-Path $OutputDir "$Database-$QueryId.$Extension"
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -Headers @{ 'User-Agent' = 'AgentHarnessMappingStudy/1.0 (23302010052@m.fudan.edu.cn)' }
        $response.Content | Set-Content -LiteralPath $target -Encoding utf8
        $script:summary += [PSCustomObject]@{
            database = $Database
            query_id = $QueryId
            url = $Url
            status = [int]$response.StatusCode
            bytes = (Get-Item -LiteralPath $target).Length
            error = $null
        }
    }
    catch {
        $script:summary += [PSCustomObject]@{
            database = $Database
            query_id = $QueryId
            url = $Url
            status = $null
            bytes = 0
            error = $_.Exception.Message
        }
    }
}

foreach ($query in $queries) {
    $encoded = [uri]::EscapeDataString($query.text)
    $openAlex = "https://api.openalex.org/works?search=$encoded&filter=from_publication_date:2019-01-01,to_publication_date:2026-08-20,has_abstract:true&sort=relevance_score:desc&per_page=50&mailto=23302010052@m.fudan.edu.cn"
    Save-Response -Database 'openalex' -QueryId $query.id -Url $openAlex

    $crossref = "https://api.crossref.org/works?query=$encoded&filter=from-pub-date:2019-01-01,until-pub-date:2026-08-20&rows=50&select=DOI,title,author,published,container-title,type,is-referenced-by-count,URL,link&mailto=23302010052@m.fudan.edu.cn"
    Save-Response -Database 'crossref' -QueryId $query.id -Url $crossref

    $semantic = "https://api.semanticscholar.org/graph/v1/paper/search?query=$encoded&fields=paperId,externalIds,url,title,abstract,venue,year,citationCount,isOpenAccess,openAccessPdf,publicationDate,authors&limit=50&year=2019-2026"
    Save-Response -Database 'semantic-scholar' -QueryId $query.id -Url $semantic

    $arxivQuery = [uri]::EscapeDataString($query.arxiv)
    $arxiv = "https://export.arxiv.org/api/query?search_query=$arxivQuery&start=0&max_results=50&sortBy=relevance&sortOrder=descending"
    Save-Response -Database 'arxiv' -QueryId $query.id -Url $arxiv -Extension 'xml'
    Start-Sleep -Seconds 3
}

[PSCustomObject]@{
    executed_at = (Get-Date).ToString('o')
    date_range = '2019-01-01/2026-08-20'
    queries = $queries
    requests = $summary
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OutputDir 'search_execution_log.json') -Encoding utf8

$summary | Format-Table -AutoSize
