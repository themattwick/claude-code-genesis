<#
.SYNOPSIS
    Makes the brain skills in this clone available in EVERY project, without copying them.

.DESCRIPTION
    The README's install route copies skills into one project's .claude/skills/.
    That is fine for one project and wrong for a machine you work on every day:
    each copy drifts, and "what changed in this skill?" stops having an answer.

    This script links instead of copying. Every brain skill in ~/.claude/skills
    becomes a junction into this clone, so:

      - the skill is available in every project on the machine
      - there is ONE copy of it, and it is this git working tree
      - `git pull` here updates the skill everywhere at once

    It also registers the two compaction hooks in ~/.claude/settings.json. Those
    are shell commands and hold absolute paths, so they point at this clone.

.NOTES
    Safe to re-run. It refuses to replace a real directory that differs from the
    clone, so a locally-modified skill is never silently thrown away.

    After it finishes, verify with:
        python .claude\skills\brain-ops\scripts\test_hooks.py
#>
[CmdletBinding()]
param(
    # Skip the hook registration and only link the skills.
    [switch]$SkipHooks
)

$ErrorActionPreference = 'Stop'

$klon = $PSScriptRoot
$zrodlo = Join-Path $klon '.claude\skills'
$cel = Join-Path $env:USERPROFILE '.claude\skills'
$ustawienia = Join-Path $env:USERPROFILE '.claude\settings.json'

if (-not (Test-Path $zrodlo)) { throw "Not a claude-code-genesis clone: $zrodlo is missing." }
if (-not (Test-Path $cel)) { New-Item -ItemType Directory -Path $cel -Force | Out-Null }

$skille = Get-ChildItem $zrodlo -Directory | Where-Object { $_.Name -like 'brain*' }
if (-not $skille) { throw "No brain* skills found in $zrodlo." }

foreach ($s in $skille) {
    $link = Join-Path $cel $s.Name
    $istnieje = Test-Path $link

    if ($istnieje) {
        $item = Get-Item $link -Force
        $jestLinkiem = $null -ne $item.LinkType

        if (-not $jestLinkiem) {
            # A real directory. Replace it only if it is byte-identical to the clone —
            # otherwise it carries local edits and throwing it away would lose them.
            $rozne = Compare-Object `
                (Get-ChildItem $link -Recurse -File | Get-FileHash | Select-Object -ExpandProperty Hash) `
                (Get-ChildItem $s.FullName -Recurse -File | Get-FileHash | Select-Object -ExpandProperty Hash)
            if ($rozne) {
                Write-Warning "$($s.Name): local copy DIFFERS from the clone — left untouched. Merge it by hand, then re-run."
                continue
            }
        }
        if ($jestLinkiem) {
            # .Delete() removes the link itself. Remove-Item -Recurse would follow it
            # into the clone and delete the real files — never use it on a junction.
            (Get-Item $link -Force).Delete()
        } else {
            Remove-Item $link -Recurse -Force
        }
    }

    New-Item -ItemType Junction -Path $link -Target $s.FullName | Out-Null
    Write-Host ("linked  {0,-14} -> {1}" -f $s.Name, $s.FullName)
}

if ($SkipHooks) { Write-Host "`nHooks left alone (-SkipHooks)."; return }

$skrypty = Join-Path $zrodlo 'brain-ops\scripts'
$hooki = @{
    PreCompact   = @{ plik = 'precompact_checkpoint.py'; matcher = 'manual|auto'; timeout = 20 }
    SessionStart = @{ plik = 'sessionstart_dokoncz_checkpoint.py'; matcher = 'compact'; timeout = 10 }
}

if (Test-Path $ustawienia) {
    Copy-Item $ustawienia "$ustawienia.bak" -Force
    $cfg = Get-Content $ustawienia -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    $cfg = [pscustomobject]@{}
}
if (-not $cfg.PSObject.Properties['hooks']) {
    $cfg | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{})
}

foreach ($ev in $hooki.Keys) {
    $h = $hooki[$ev]
    $sciezka = Join-Path $skrypty $h.plik
    if (-not (Test-Path $sciezka)) { throw "Missing hook script: $sciezka" }

    $wpis = @(
        [pscustomobject]@{
            matcher = $h.matcher
            hooks   = @([pscustomobject]@{
                    type    = 'command'
                    command = ('python "{0}"' -f $sciezka)
                    timeout = $h.timeout
                })
        })

    if ($cfg.hooks.PSObject.Properties[$ev]) { $cfg.hooks.$ev = $wpis }
    else { $cfg.hooks | Add-Member -NotePropertyName $ev -NotePropertyValue $wpis }
    Write-Host ("hook    {0,-14} -> {1}" -f $ev, $sciezka)
}

# NOT Set-Content -Encoding UTF8: in Windows PowerShell 5.1 that writes a BOM, and a
# BOM makes settings.json unreadable to strict JSON parsers (Python's json.load raises
# on it). Caught by test_hooks.py, which reads the file the same way a tool would.
[System.IO.File]::WriteAllText($ustawienia, ($cfg | ConvertTo-Json -Depth 20),
    (New-Object System.Text.UTF8Encoding($false)))
Write-Host "`nsettings.json updated (backup: $ustawienia.bak)"
Write-Host "Now verify the EFFECT, not that the script ran:"
$test = Join-Path $skrypty 'test_hooks.py'
Write-Host ('    python "{0}"' -f $test)
