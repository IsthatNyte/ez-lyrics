using System;
using System.Threading.Tasks;
using Windows.Media.Control;

public class MediaChecker {
    public static async Task<string> GetSpotifyTimeline() {
        try {
            var mgr = await GlobalSystemMediaTransportControlsSessionManager.RequestAsync();
            var sessions = mgr.GetSessions();
            foreach (var s in sessions) {
                var modelId = s.SourceAppUserModelId ?? "";
                if (modelId.ToLower().Contains("spotify")) {
                    var timeline = s.GetTimelineProperties();
                    var playback = s.GetPlaybackInfo();
                    var media = await s.TryGetMediaPropertiesAsync();
                    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}",
                        media.Title,
                        media.Artist,
                        timeline.Position.TotalSeconds,
                        timeline.EndTime.TotalSeconds,
                        playback.PlaybackStatus,
                        s.SourceAppUserModelId
                    );
                }
            }
            return "NO_SPOTIFY";
        } catch (Exception ex) {
            return "ERROR: " + ex.Message;
        }
    }
}
