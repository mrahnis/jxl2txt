<#
    Generate CLI help files from Click online help.
    These will get picked up by Sphinx.
 #>

$main = "jxl2txt"
$commands = @(
    "convert",
    "info"
)

$dst = "$($PSScriptRoot)\..\docs\source\cli"

& $main --help | Out-File $(Join-Path $dst cli.${main}.txt)

ForEach ($command in $commands)
{
    Write-Host "Writing help for $command"
    $path = Join-Path $dst cli.${command}.txt
    & $main ${command} --help | Out-File $path
}
