param(
  [Parameter(Mandatory = $true)][string]$InputPath,
  [string]$OutputDir = (Join-Path $PSScriptRoot '..\data\pdf')
)
# 需要本机安装 Microsoft PowerPoint。Adobe/LibreOffice 路线未在此脚本中启用。
$InputPath = (Resolve-Path -LiteralPath $InputPath).Path
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$name = [System.IO.Path]::GetFileNameWithoutExtension($InputPath)
$pdf = Join-Path $OutputDir ($name + ".pdf")
$app = $null; $pres = $null
try {
  $app = New-Object -ComObject PowerPoint.Application
  $pres = $app.Presentations.Open($InputPath, $true, $false, $false)
  $pres.SaveAs($pdf, 32)  # ppSaveAsPDF
  $pres.Close()
  $app.Quit()
  if (Test-Path -LiteralPath $pdf) {
    $bytes = (Get-Item -LiteralPath $pdf).Length
    Write-Output ("OK`t{0}`t{1}" -f $pdf, $bytes)
  } else {
    throw "PDF 未生成"
  }
} catch {
  Write-Output ("ERR`t" + $_.Exception.Message)
  try { if ($pres) { $pres.Close() } } catch {}
  try { if ($app) { $app.Quit() } } catch {}
  exit 1
}
