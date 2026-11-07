import subprocess

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
$op = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
$mgr = Await-Async $op ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])

if ($mgr) {
    foreach ($s in $mgr.GetSessions()) {
        if ($s.SourceAppUserModelId -like "*Spotify*") {
            Write-Host "Found Spotify Session!"
            Write-Host "Has TryTogglePlayPauseAsync:" ($s | Get-Member -Name TryTogglePlayPauseAsync | Measure-Object).Count
            Write-Host "Has TryChangePlaybackPositionAsync:" ($s | Get-Member -Name TryChangePlaybackPositionAsync | Measure-Object).Count
            break
        }
    }
}
"""

with open("test_control.ps1", "w", encoding="utf-8") as f:
    f.write(ps_code)

res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "test_control.ps1"], capture_output=True, text=True)
print("CONTROL TEST:", res.stdout)
