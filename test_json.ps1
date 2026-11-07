$obj = @{
    title = "test"
    artist = "artist"
    album = "album"
    status = "Playing"
    pos = 12.34
    dur = 180.5
}
$json = ($obj | ConvertTo-Json -Compress)
Write-Host $json
