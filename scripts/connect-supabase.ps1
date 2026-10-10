param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]{20}$')]
    [string]$ProjectRef
)

$ErrorActionPreference = 'Stop'
$serverName = 'supabase-kawteam'
$serverUrl = "https://mcp.supabase.com/mcp?project_ref=$ProjectRef&features=database,debugging,development,functions,docs"

Get-Command codex -ErrorAction Stop | Out-Null
& codex mcp add $serverName --url $serverUrl
if ($LASTEXITCODE -ne 0) { throw 'Could not configure the project-scoped MCP server.' }

Write-Host 'Sign in as shazwan1512alt@gmail.com and authorise the organisation containing KawTeam.'
Write-Host 'This connection enables project read/write tools. It does not enable paid database branches.'
& codex mcp login $serverName
if ($LASTEXITCODE -ne 0) { throw 'Supabase authorisation did not complete.' }

Write-Host 'Authentication completed. Reload Codex so the project tools become available.'
Write-Host 'Then ask Codex to verify the project URL and list its tables before applying migrations.'
