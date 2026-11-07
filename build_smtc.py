import subprocess

code = '''using System;
using System.Threading.Tasks;
using Windows.Media.Control;

class Program {
    static void Main() {
        try {
            var task = WindowsRuntimeSystemExtensions.AsTask(GlobalSystemMediaTransportControlsSessionManager.RequestAsync());
            task.Wait();
            var mgr = task.Result;
            var sessions = mgr.GetSessions();
            foreach (var s in sessions) {
                var modelId = s.SourceAppUserModelId ?? "";
                if (modelId.ToLower().Contains("spotify")) {
                    var timeline = s.GetTimelineProperties();
                    var playback = s.GetPlaybackInfo();
                    var mediaTask = WindowsRuntimeSystemExtensions.AsTask(s.TryGetMediaPropertiesAsync());
                    mediaTask.Wait();
                    var media = mediaTask.Result;
                    string t = (media.Title ?? "").Replace("\\"", " ");
                    string a = (media.Artist ?? "").Replace("\\"", " ");
                    Console.WriteLine("JSON:{\\"title\\":\\"" + t + "\\",\\"artist\\":\\"" + a + "\\",\\"pos\\":" + timeline.Position.TotalSeconds + ",\\"dur\\":" + timeline.EndTime.TotalSeconds + ",\\"status\\":\\"" + playback.PlaybackStatus + "\\",\\"app\\":\\"" + modelId + "\\"}");
                    return;
                }
            }
            // If not found in sessions, try current session
            var session = mgr.GetCurrentSession();
            if (session != null) {
                var timeline = session.GetTimelineProperties();
                var playback = session.GetPlaybackInfo();
                var mediaTask = WindowsRuntimeSystemExtensions.AsTask(session.TryGetMediaPropertiesAsync());
                mediaTask.Wait();
                var media = mediaTask.Result;
                string t = (media.Title ?? "").Replace("\\"", " ");
                string a = (media.Artist ?? "").Replace("\\"", " ");
                Console.WriteLine("JSON:{\\"title\\":\\"" + t + "\\",\\"artist\\":\\"" + a + "\\",\\"pos\\":" + timeline.Position.TotalSeconds + ",\\"dur\\":" + timeline.EndTime.TotalSeconds + ",\\"status\\":\\"" + playback.PlaybackStatus + "\\",\\"app\\":\\"" + session.SourceAppUserModelId + "\\"}");
            } else {
                Console.WriteLine("JSON:null");
            }
        } catch (Exception ex) {
            Console.WriteLine("ERR:" + ex.ToString());
        }
    }
}
'''

with open("smtc_test.cs", "w", encoding="utf-8") as f:
    f.write(code)

cmd = [
    r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    "/target:exe",
    "/out:smtc_reader.exe",
    r"/r:C:\Windows\System32\WinMetadata\Windows.Foundation.winmd",
    r"/r:C:\Windows\System32\WinMetadata\Windows.Media.winmd",
    r"/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Runtime.dll",
    r"/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Runtime.WindowsRuntime.dll",
    "smtc_test.cs"
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
if res.returncode == 0:
    run_res = subprocess.run(["smtc_reader.exe"], capture_output=True, text=True)
    print("Execution output:", run_res.stdout)
else:
    print("Output:", res.stdout)
