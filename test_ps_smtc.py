import subprocess
import json

ps_code = """
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1

function Await-Async($asyncOp, $type) {
    $m = $asTaskGeneric.MakeGenericMethod($type)
    $task = $m.Invoke($null, @($asyncOp))
    $task.Wait()
    return $task.Result
}

[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Control.GlobalSystemMediaTransportControlsSession, Windows.Media, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties, Windows.Media, ContentType=WindowsRuntime] | Out-Null

$op = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
$mgr = Await-Async $op ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])

if ($mgr) {
    $sessions = $mgr.GetSessions()
    $targetSession = $null
    foreach ($s in $sessions) {
        if ($s.SourceAppUserModelId -like "*Spotify*") {
            $targetSession = $s
            break
        }
    }
    if (-not $targetSession) {
        $targetSession = $mgr.GetCurrentSession()
    }

    if ($targetSession) {
        $timeline = $targetSession.GetTimelineProperties()
        $playback = $targetSession.GetPlaybackInfo()
        $propOp = $targetSession.TryGetMediaPropertiesAsync()
        $props = Await-Async $propOp ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
        
        $obj = @{
            title = $props.Title
            artist = $props.Artist
            pos = $timeline.Position.TotalSeconds
            dur = $timeline.EndTime.TotalSeconds
            status = $playback.PlaybackStatus.ToString()
            app = $targetSession.SourceAppUserModelId
        }
        $obj | ConvertTo-Json -Compress
    } else {
        Write-Output "null"
    }
}
"""

with open("get_smtc.ps1", "w", encoding="utf-8") as f:
    f.write(ps_code)

res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "get_smtc.ps1"], capture_output=True, text=True)
print("PS STDOUT:", res.stdout)
print("PS STDERR:", res.stderr)
