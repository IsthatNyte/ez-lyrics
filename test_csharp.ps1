$src = @"
using System;
using System.IO;
using System.Threading.Tasks;
using Windows.Media.Control;
using Windows.Storage.Streams;

public class SmtcReader {
    public static async Task<byte[]> GetSpotifyThumbnailAsync() {
        var mgr = await GlobalSystemMediaTransportControlsSessionManager.RequestAsync();
        foreach (var sess in mgr.GetSessions()) {
            if (sess.SourceAppUserModelId.IndexOf("Spotify", StringComparison.OrdinalIgnoreCase) >= 0) {
                var props = await sess.TryGetMediaPropertiesAsync();
                if (props != null && props.Thumbnail != null) {
                    using (var stream = await props.Thumbnail.OpenReadAsync()) {
                        using (var netStream = stream.AsStreamForRead()) {
                            using (var ms = new MemoryStream()) {
                                await netStream.CopyToAsync(ms);
                                return ms.ToArray();
                            }
                        }
                    }
                }
            }
        }
        return null;
    }
}
"@

Add-Type -TypeDefinition $src -ReferencedAssemblies System.Runtime.WindowsRuntime, "C:\Windows\System32\WinMetadata\Windows.Media.winmd", "C:\Windows\System32\WinMetadata\Windows.Foundation.winmd", "C:\Windows\System32\WinMetadata\Windows.Storage.winmd"

$task = [SmtcReader]::GetSpotifyThumbnailAsync()
$task.Wait()
$res = $task.Result
if ($res) {
    Write-Host "Got bytes from Spotify SMTC:" $res.Length
    [IO.File]::WriteAllBytes("$env:TEMP\spotify_real_cover.jpg", $res)
} else {
    Write-Host "No thumbnail returned from SMTC"
}
