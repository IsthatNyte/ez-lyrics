import subprocess
import time
import json

ps_worker = """
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1

function Await-Async($asyncOp, $type) {
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

while ($line = [Console]::ReadLine()) {
    if ($line -eq "QUIT") { break }
    if ($line.StartsWith("SEEK ")) {
        $sec = [double]($line.Substring(5))
        $sess = $mgr.GetCurrentSession()
        if ($sess) {
            $ticks = [long]($sec * 10000000)
            $seekOp = $sess.TryChangePlaybackPositionAsync($ticks)
            Await-Async $seekOp ([bool]) | Out-Null
        }
        Write-Host "OK"
        continue
    }
    if ($line -eq "TOGGLE") {
        $sess = $mgr.GetCurrentSession()
        if ($sess) {
            $togOp = $sess.TryTogglePlayPauseAsync()
            Await-Async $togOp ([bool]) | Out-Null
        }
        Write-Host "OK"
        continue
    }

    # Default GET status
    $s = $null
    foreach ($item in $mgr.GetSessions()) {
        if ($item.SourceAppUserModelId -like "*Spotify*") {
            $s = $item
            break
        }
    }
    if (-not $s) { $s = $mgr.GetCurrentSession() }

    if ($s) {
        $timeline = $s.GetTimelineProperties()
        $playback = $s.GetPlaybackInfo()
        $props = Await-Async ($s.TryGetMediaPropertiesAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
        $obj = @{
            title = $props.Title
            artist = $props.Artist
            pos = [Math]::Round($timeline.Position.TotalSeconds, 2)
            dur = [Math]::Round($timeline.EndTime.TotalSeconds, 2)
            status = $playback.PlaybackStatus.ToString()
        }
        $json = $obj | ConvertTo-Json -Compress
        Write-Host $json
    } else {
        Write-Host "{}"
    }
}
"""

with open("spotify_bridge.ps1", "w", encoding="utf-8") as f:
    f.write(ps_worker)

proc = subprocess.Popen(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "spotify_bridge.ps1"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    bufsize=1
)

for _ in range(3):
    proc.stdin.write("GET\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    print("Bridge reply:", line.strip())
    time.sleep(0.5)

proc.stdin.write("QUIT\n")
proc.stdin.flush()
proc.kill()
