using UnityEngine;

namespace Usrah
{
    /// <summary>Everything saved, on this device only. No accounts, nothing leaves the device.</summary>
    public static class Progress
    {
        public static readonly string[] Avatars = { "sara", "yusuf", "nabeeh", "cat" };

        public static int Profile
        {
            get => PlayerPrefs.GetInt("profile", 0);
            set { PlayerPrefs.SetInt("profile", value); PlayerPrefs.Save(); }
        }

        public static int Stars
        {
            get => PlayerPrefs.GetInt($"stars_{Profile}", 0);
            set { PlayerPrefs.SetInt($"stars_{Profile}", value); PlayerPrefs.Save(); }
        }

        public static int StarsFor(int profile) => PlayerPrefs.GetInt($"stars_{profile}", 0);

        public static bool EasternDigits
        {
            get => PlayerPrefs.GetInt("eastern_digits", 1) == 1;
            set { PlayerPrefs.SetInt("eastern_digits", value ? 1 : 0); PlayerPrefs.Save(); }
        }

        public static bool SoundOn
        {
            get => PlayerPrefs.GetInt("sound", 1) == 1;
            set { PlayerPrefs.SetInt("sound", value ? 1 : 0); PlayerPrefs.Save(); }
        }

        public static void Reset()
        {
            for (var i = 0; i < Avatars.Length; i++) PlayerPrefs.DeleteKey($"stars_{i}");
            PlayerPrefs.Save();
        }
    }
}
