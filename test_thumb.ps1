Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
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
$op = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
$mgr = Await-Async $op ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])
foreach ($sess in $mgr.GetSessions()) {
    if ($sess.SourceAppUserModelId -like "*Spotify*") {
        $propsOp = $sess.TryGetMediaPropertiesAsync()
        $props = Await-Async $propsOp ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
        Write-Host "Spotify Title:" $props.Title
        if ($props.Thumbnail) {
            $stOp = $props.Thumbnail.OpenReadAsync()
            $stream = Await-Async $stOp ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
            $netStream = [System.IO.WindowsRuntimeStreamExtensions]::AsStream($stream)
            $ms = New-Object System.IO.MemoryStream
            $netStream.CopyTo($ms)
            $bytes = $ms.ToArray()
            Write-Host ("SUCCESS! READ BYTES FROM SPOTIFY SMTC: " + $bytes.Length)
            if ($bytes.Length -gt 0) {
                $b64 = [Convert]::ToBase64String($bytes)
                Write-Host ("B64 prefix: " + $b64.Substring(0, 50))
            }
        }
    }
}
