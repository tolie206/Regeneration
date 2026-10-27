param([string]$BindAddress = "", [int]$Port = 47520, [int]$Players = 16)
$ErrorActionPreference = 'Stop'
if (-not $BindAddress) {
  $addresses = @(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' -and $_.AddressState -eq 'Preferred' } | Select-Object -ExpandProperty IPAddress -Unique)
  if ($addresses.Count -eq 1) { $BindAddress = $addresses[0] }
  else { Write-Host ('LAN IPv4: ' + ($addresses -join ', ')); throw 'Chọn IPv4 của Wi-Fi: .\Start-LAN.ps1 -BindAddress 192.168.x.x' }
}
if ($BindAddress -notmatch '^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)') { throw 'Bản thử nghiệm chỉ cho phép localhost hoặc IPv4 LAN riêng.' }
if ($Port -lt 1024 -or $Port -gt 65535 -or $Players -lt 2 -or $Players -gt 16) { throw 'Port 1024..65535, số người thử nghiệm 2..16.' }
$exe = Join-Path $PSScriptRoot 'mugoat-server.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw 'Thiếu mugoat-server.exe trong thư mục này.' }
$env:MUGOAT_BIND = $BindAddress
Write-Host "Mugoat Online LAN: $($BindAddress):$Port / phòng roleplay"
Write-Host 'iPhone cùng Wi-Fi, cho phép Local Network trong iOS. Ctrl+C để dừng.'
Write-Host 'Script không tạo luật firewall, không mở cổng router. Đây chưa phải server RP public.'
& $exe $Port $Players
