param(
    [string]$InputWorkbook = "C:\Users\laptop\Desktop\staar_first3_demo\Blooket\Grade3_ELAR_STAAR_Blooket_Import.xlsx",
    [string]$OutputCsv = "C:\Users\laptop\Desktop\staar_first3_demo\Blooket\Grade3_ELAR_STAAR_Blooket_Import.csv",
    [switch]$IncludeBannerRow
)

$ErrorActionPreference = "Stop"

$outputDirectory = Split-Path -Path $OutputCsv -Parent
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-SharedStringValue {
    param(
        [Parameter(Mandatory = $true)]
        [System.Xml.XmlElement]$SharedStringItem
    )

    return ([string]$SharedStringItem.InnerText -replace "\r\n|\r|\n", " ").Trim()
}

function Get-CellPlainText {
    param(
        [Parameter(Mandatory = $true)]
        [System.Xml.XmlElement]$Cell,
        [AllowEmptyCollection()]
        [string[]]$SharedStrings = @()
    )

    $value = switch ([string]$Cell.t) {
        "s" {
            if ($Cell.v) { $SharedStrings[[int]$Cell.v] } else { "" }
            break
        }
        "inlineStr" {
            if ($Cell.is.t) {
                [string]$Cell.is.t.'#text'
            }
            elseif ($Cell.is.r) {
                (($Cell.is.r | ForEach-Object { $_.t.'#text' }) -join "")
            }
            else {
                ""
            }
            break
        }
        default {
            if ($Cell.v) { [string]$Cell.v } else { "" }
        }
    }

    return ([string]$value -replace "\r\n|\r|\n", " ").Trim()
}

function Convert-ToCsvField {
    param(
        [AllowNull()]
        [string]$Value
    )

    $text = if ($null -eq $Value) { "" } else { $Value }
    '"' + ($text -replace '"', '""') + '"'
}

$zip = [System.IO.Compression.ZipFile]::OpenRead($InputWorkbook)

try {
    $sharedStrings = @()

    $sharedEntry = $zip.Entries | Where-Object { $_.FullName -eq "xl/sharedStrings.xml" }
    if ($sharedEntry) {
        $sharedReader = New-Object System.IO.StreamReader($sharedEntry.Open())
        try {
            [xml]$sharedXml = $sharedReader.ReadToEnd()
        }
        finally {
            $sharedReader.Close()
        }

        $sharedNs = New-Object System.Xml.XmlNamespaceManager -ArgumentList $sharedXml.NameTable
        $sharedNs.AddNamespace("x", "http://schemas.openxmlformats.org/spreadsheetml/2006/main")
        $sharedStrings = @(
            $sharedXml.SelectNodes("//x:sst/x:si", $sharedNs) | ForEach-Object {
                Get-SharedStringValue -SharedStringItem $_
            }
        )
    }

    $sheetEntry = $zip.Entries | Where-Object { $_.FullName -eq "xl/worksheets/sheet1.xml" }
    if (-not $sheetEntry) {
        throw "Could not find sheet1.xml in $InputWorkbook"
    }

    $sheetReader = New-Object System.IO.StreamReader($sheetEntry.Open())
    try {
        [xml]$sheetXml = $sheetReader.ReadToEnd()
    }
    finally {
        $sheetReader.Close()
    }

    $sheetNs = New-Object System.Xml.XmlNamespaceManager -ArgumentList $sheetXml.NameTable
    $sheetNs.AddNamespace("x", "http://schemas.openxmlformats.org/spreadsheetml/2006/main")

    $rows = @($sheetXml.SelectNodes("//x:sheetData/x:row", $sheetNs))
    $columnLetters = @("A", "B", "C", "D", "E", "F", "G", "H")
    $csvLines = New-Object System.Collections.Generic.List[string]

    foreach ($row in $rows) {
        $rowNumber = [int]$row.r
        if (-not $IncludeBannerRow -and $rowNumber -eq 1) {
            continue
        }

        $values = @()
        foreach ($column in $columnLetters) {
            $cell = $row.SelectSingleNode("x:c[@r='$column$rowNumber']", $sheetNs)
            if ($cell) {
                $values += Get-CellPlainText -Cell $cell -SharedStrings $sharedStrings
            }
            else {
                $values += ""
            }
        }

        $hasContent = $values | Where-Object { $_ -ne "" }
        if (-not $hasContent) {
            continue
        }

        $csvLines.Add(($values | ForEach-Object { Convert-ToCsvField $_ }) -join ",")
    }

    [System.IO.File]::WriteAllLines($OutputCsv, $csvLines, [System.Text.UTF8Encoding]::new($false))

    Write-Output "Created: $OutputCsv"
    Write-Output "Row count: $($csvLines.Count)"
}
finally {
    $zip.Dispose()
}
