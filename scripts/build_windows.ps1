param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path.TrimEnd('\')
$buildRoot = Join-Path $projectRoot "build"
$distRoot = Join-Path $projectRoot "dist"
$bundleDir = Join-Path $distRoot "TypingSurvivor"
$zipFile = Join-Path $distRoot "TypingSurvivor-test-Windows.zip"

# PyInstaller puede reemplazar builds anteriores: limita sus destinos al proyecto.
foreach ($target in @($buildRoot, $distRoot, $bundleDir, $zipFile)) {
    $fullPath = [System.IO.Path]::GetFullPath($target)
    if (-not $fullPath.StartsWith(
        "$projectRoot\", [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Destino fuera del proyecto: $fullPath"
    }
}

Push-Location $projectRoot
try {
    & $Python -m PyInstaller `
        --noconfirm --onedir --windowed `
        --name TypingSurvivor `
        --distpath $distRoot --workpath $buildRoot --specpath $buildRoot `
        --add-data "$(Join-Path $projectRoot 'assets'):assets" `
        --add-data "$(Join-Path $projectRoot 'data'):data" `
        main.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller no pudo generar el ejecutable."
    }

    Copy-Item -LiteralPath (Join-Path $projectRoot "docs\GUIA_TESTERS.md") `
        -Destination (Join-Path $bundleDir "LEEME_TESTERS.md")
    Compress-Archive -LiteralPath $bundleDir -DestinationPath $zipFile -Force

    $hash = (Get-FileHash -LiteralPath $zipFile -Algorithm SHA256).Hash
    Set-Content -LiteralPath "$zipFile.sha256.txt" -Value "$hash  TypingSurvivor-test-Windows.zip"
    Write-Output "Paquete listo: $zipFile"
    Write-Output "SHA-256: $hash"
}
finally {
    Pop-Location
}
