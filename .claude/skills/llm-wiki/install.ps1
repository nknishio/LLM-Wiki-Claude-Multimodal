# llm-wiki installer (Windows / PowerShell).
# Installs uv if missing, then installs the `llm-wiki` CLI as an isolated
# uv tool. No system binaries (no markitdown / poppler / pandoc) -- every
# dependency is a pure-Python wheel.
$ErrorActionPreference = "Stop"

$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "==> installing uv"
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Write-Host "==> installing llm-wiki CLI from $SkillDir"
uv tool install --force "$SkillDir"

Write-Host "==> verifying"
llm-wiki doctor
Write-Host ""
Write-Host "Done. 'llm-wiki' is on your PATH (via uv tool). Try: llm-wiki --version"
