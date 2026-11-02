using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace Usrah
{
    /// <summary>Who is playing: up to four local profiles shown as characters. No typing, no accounts.</summary>
    public static class ProfileScreen
    {
        public static VisualElement Show(VisualElement parent, Voice voice, Action close)
        {
            var root = Ui.Box("screen", parent);
            var grid = Ui.Box("profile-grid", root);
            for (var i = 0; i < Progress.Avatars.Length; i++)
            {
                var index = i;
                var card = Ui.Tap("profile-card", () =>
                {
                    Progress.Profile = index;
                    close();
                }, grid);
                if (i == Progress.Profile) card.AddToClassList("profile-now");
                Ui.Picture(Content.Portrait(Progress.Avatars[i]), "profile-face", card);
                var stars = Ui.Box("stars-pill", card);
                stars.Add(new Icon(IconKind.Star) { name = "star-icon", pickingMode = PickingMode.Ignore });
                Ui.Text(Content.Digits(Progress.StarsFor(i)), "stars-count", stars);
            }
            voice.Say("who_plays");
            return root;
        }
    }

    /// <summary>Behind the door: a gate children won't pass by accident, then the parents' settings.</summary>
    public static class ParentScreen
    {
        const float HoldSeconds = 3f;

        public static VisualElement Show(VisualElement parent, Action close)
        {
            var root = Ui.Box("screen", parent);
            ShowGate(root, close);
            return root;
        }

        static void ShowGate(VisualElement root, Action close)
        {
            root.Clear();
            var gate = Ui.Box("gate", root);
            Ui.IconButton(IconKind.Home, "home-button gate-home", close, gate);
            Ui.Text(Content.T("hold"), "gate-text", gate);
            var hold = Ui.Box("hold-button", gate);
            var fill = Ui.Box("hold-fill", hold);
            fill.pickingMode = PickingMode.Ignore;
            IVisualElementScheduledItem timer = null;
            var started = 0f;
            hold.RegisterCallback<PointerDownEvent>(_ =>
            {
                started = Time.realtimeSinceStartup;
                timer = hold.schedule.Execute(() =>
                {
                    var k = (Time.realtimeSinceStartup - started) / HoldSeconds;
                    fill.style.width = Length.Percent(Mathf.Clamp01(k) * 100f);
                    if (k >= 1f)
                    {
                        timer.Pause();
                        ShowSettings(root, close);
                    }
                }).Every(30);
            });
            void Cancel()
            {
                timer?.Pause();
                fill.style.width = Length.Percent(0f);
            }
            hold.RegisterCallback<PointerUpEvent>(_ => Cancel());
            hold.RegisterCallback<PointerLeaveEvent>(_ => Cancel());
        }

        static void ShowSettings(VisualElement root, Action close)
        {
            root.Clear();
            var panel = Ui.Box("settings", root);
            Ui.IconButton(IconKind.Home, "home-button gate-home", close, panel);
            Ui.Text(Content.T("parents"), "settings-title", panel);

            var digits = Ui.Box("setting-row", panel);
            Ui.Text(Content.T("numerals"), "setting-label", digits);
            Button digitButton = null;
            string DigitsText() => Progress.EasternDigits ? "١٢٣" : "123";
            digitButton = Ui.Tap("setting-value", () =>
            {
                Progress.EasternDigits = !Progress.EasternDigits;
                digitButton.text = DigitsText();
            }, digits, DigitsText());

            var sound = Ui.Box("setting-row", panel);
            Ui.Text(Content.T("sound"), "setting-label", sound);
            Button soundButton = null;
            string SoundText() => Content.T(Progress.SoundOn ? "on" : "off");
            soundButton = Ui.Tap("setting-value", () =>
            {
                Progress.SoundOn = !Progress.SoundOn;
                soundButton.text = SoundText();
            }, sound, SoundText());

            var reset = Ui.Box("setting-row", panel);
            Ui.Text(Content.T("reset"), "setting-label", reset);
            Button resetButton = null;
            resetButton = Ui.Tap("setting-value", () =>
            {
                Progress.Reset();
                resetButton.text = Content.Digits(0);
                resetButton.SetEnabled(false);
            }, reset, Content.T("reset"));
        }
    }
}
