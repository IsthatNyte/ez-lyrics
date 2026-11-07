Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | ? { 
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
} | Select-Object -First 1

function Await-Async($asyncOp, $type) {
    if (-not $asyncOp) { return $null }
    $m = $asTaskGeneric.MakeGenericMethod($type)
    $task = $m.Invoke($null, @($asyncOp))
    $task.Wait()
    return $task.Result
}

[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties, Windows.Media, ContentType=WindowsRuntime] | Out-Null

$op = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
$mgr = Await-Async $op ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Get-SpotifySession {
    if (-not $mgr) { return $null }
    foreach ($item in $mgr.GetSessions()) {
        if ($item.SourceAppUserModelId -like "*Spotify*") {
            return $item
        }
    }
    return $mgr.GetCurrentSession()
}

$sess = Get-SpotifySession
if ($sess) {
    $propsOp = $sess.TryGetMediaPropertiesAsync()
    $props = Await-Async $propsOp ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
    $infoOp = $sess.GetPlaybackInfo()
    $timeline = $sess.GetTimelineProperties()

    $title = if ($props) { $props.Title } else { "" }
    $artist = if ($props) { $props.Artist } else { "" }
    $album = if ($props) { $props.AlbumTitle } else { "" }
    $status = if ($infoOp) { $infoOp.PlaybackStatus.ToString() } else { "Closed" }

    $pos = 0.0
    $dur = 0.0
    if ($timeline) {
        $dur = $timeline.EndTime.TotalSeconds
        $pos = $timeline.Position.TotalSeconds
    }

    $obj = @{
        title = $title
        artist = $artist
        album = $album
        status = $status
        pos = [math]::Round([double]$pos, 2)
        dur = [math]::Round([double]$dur, 2)
    }
    Write-Host ($obj | ConvertTo-Json -Compress)
} else {
    Write-Host "{}"
}
