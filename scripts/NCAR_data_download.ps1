$base = "https://data.eol.ucar.edu/pub/download/data/maros120846/" <# change this to the URL from NCAR #>
$out = "$env:USERPROFILE\Downloads\EOL_maros120846" <# change this to your download location #>

New-Item -ItemType Directory -Force -Path $out | Out-Null

$page = Invoke-WebRequest -Uri $base

$files = $page.Links |
    Where-Object { $_.href -and $_.href -notmatch "/$" -and $_.href -ne "../" } |
    Select-Object -ExpandProperty href -Unique

foreach ($file in $files) {
    $url = [System.Uri]::new([System.Uri]$base, $file).AbsoluteUri
    $name = Split-Path ([System.Uri]::UnescapeDataString($file)) -Leaf
    $dest = Join-Path $out $name

    if (Test-Path $dest) {
        Write-Host "Skipping existing file: $name"
        continue
    }

    Write-Host "Downloading: $name"
    Invoke-WebRequest -Uri $url -OutFile $dest
}

Write-Host "Done. Files saved to $out"