using System;
using System.Collections;
using System.Globalization;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace Usrah
{
    /// <summary>The game's top level: the home room, its hotspots, and opening screens over it.</summary>
    [RequireComponent(typeof(UIDocument))]
    public class App : MonoBehaviour
    {
        static readonly string[] HijriMonths =
        {
            "محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
            "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة",
        };

        public Transform room, nabeeh, cat;

        Camera cam;
        Voice voice;
        RoomLife life;
        NabeehPuppet puppet;
        VisualElement ui, hud, bubble;
        Label bubbleText, hudStars;
        VisualElement avatar;
        Action closeScreen;
        bool ready;
        IVisualElementScheduledItem bubbleTimer;

        void Awake()
        {
            Content.Load();
            cam = Camera.main;
            voice = gameObject.AddComponent<Voice>();
            life = gameObject.AddComponent<RoomLife>();
            life.Find(room, cat);
            puppet = nabeeh.gameObject.AddComponent<NabeehPuppet>();
            puppet.Find(nabeeh);
            voice.Speaking += (key, seconds) =>
            {
                if (closeScreen != null || !ready) return;
                puppet.Talk(seconds);
                Bubble(Content.T(key), seconds + .5f);
            };
        }

        void OnEnable()
        {
            ui = GetComponent<UIDocument>().rootVisualElement;
            ui.styleSheets.Add(Resources.Load<StyleSheet>("UI/usrah"));
            ui.AddToClassList("app");
            ui.languageDirection = LanguageDirection.RTL;
            ui.style.unityTextGenerator = TextGeneratorType.Advanced;
            BuildHud();
            ShowTitle();
        }

        // ---- Start: browsers only allow sound after a tap, so the game opens with a play button ----

        void ShowTitle()
        {
            hud.style.display = DisplayStyle.None;
            var title = Ui.Box("title-screen", ui);
            Ui.Text("برامج الأسرة", "title-text", title);
            var play = Ui.IconButton(IconKind.Play, "title-play", null, title);
            play.clicked += () =>
            {
                title.RemoveFromHierarchy();
                hud.style.display = DisplayStyle.Flex;
                StartCoroutine(Begin());
            };
        }

        IEnumerator Begin()
        {
            yield return puppet.RollIn(null);
            ready = true;
            voice.Say("greeting", "hint_letters");
        }

        // ---- Heads-up: who's playing and how many stars, plus نبيه's speech bubble ----

        void BuildHud()
        {
            hud = Ui.Box("hud", ui);
            hud.pickingMode = PickingMode.Ignore;
            var pill = Ui.Box("profile-pill", hud);
            pill.pickingMode = PickingMode.Ignore;
            avatar = Ui.Box("profile-mini", pill);
            avatar.pickingMode = PickingMode.Ignore;
            pill.Add(new Icon(IconKind.Star) { name = "star-icon", pickingMode = PickingMode.Ignore });
            hudStars = Ui.Text("", "stars-count", pill);
            bubble = Ui.Box("bubble", hud);
            bubble.pickingMode = PickingMode.Ignore;
            bubbleText = Ui.Text("", "bubble-text", bubble);
            Ui.Box("bubble-tail", bubble).pickingMode = PickingMode.Ignore;
            bubble.style.opacity = 0f;
            RefreshHud();
        }

        void RefreshHud()
        {
            avatar.style.backgroundImage = new StyleBackground(Content.Portrait(Progress.Avatars[Progress.Profile]));
            hudStars.text = Content.Digits(Progress.Stars);
        }

        void Bubble(string text, float seconds)
        {
            bubbleText.text = text;
            bubble.style.opacity = 1f;
            bubbleTimer?.Pause();
            bubbleTimer = bubble.schedule.Execute(() => bubble.style.opacity = 0f);
            bubbleTimer.ExecuteLater((long)(seconds * 1000));
        }

        // ---- Tapping the room ----

        void Update()
        {
            if (!ready || closeScreen != null || Pointer.current == null) return;
            // On release, so the finger isn't still down on whatever screen this tap opens
            if (!Pointer.current.press.wasReleasedThisFrame) return;
            var ray = cam.ScreenPointToRay(Pointer.current.position.ReadValue());
            if (!Physics.Raycast(ray, out var hit, 30f)) return;
            var hotspot = hit.collider.GetComponentInParent<Hotspot>();
            if (hotspot != null) Tapped(hotspot);
        }

        void Tapped(Hotspot spot)
        {
            if (spot.id != "nabeeh" && spot.id != "door") life.Bounce(spot.transform);
            switch (spot.id)
            {
                case "letter_cube":
                    OpenLetters();
                    break;
                case "nabeeh":
                    puppet.Hop();
                    voice.Say("greeting");
                    break;
                case "family_photo":
                    Open(parent => ProfileScreen.Show(parent, voice, CloseScreen));
                    break;
                case "door":
                    life.OpenDoor(() => Open(parent => ParentScreen.Show(parent, CloseScreen), life.CloseDoor));
                    break;
                case "clock":
                    Bubble(DateTime.Now.ToString("h:mm", CultureInfo.InvariantCulture), 3f);
                    break;
                case "calendar":
                    Bubble(HijriDate(), 4f);
                    break;
                case "camel_toy": Soon("animals"); break;
                case "abacus": Soon("math"); break;
                case "calligraphy": Soon("prayer"); break;
                case "trophy": Soon("quiz"); break;
                case "big_ben": Soon("words"); break;
                case "console": Soon("submarine"); break;
            }
        }

        void Soon(string title)
        {
            voice.Say("soon");
            Bubble($"{Content.T(title)}: {Content.T("soon_tag")}", 3.2f);
        }

        static string HijriDate()
        {
            var calendar = new UmAlQuraCalendar();
            var now = DateTime.Now;
            return $"{Content.Digits(calendar.GetDayOfMonth(now))} {HijriMonths[calendar.GetMonth(now) - 1]}";
        }

        // ---- Screens over the room. The 3D camera sleeps behind them, to save battery. ----

        void OpenLetters()
        {
            LettersScreen screen = null;
            ShowScreen(() => screen.Remove(), null);
            screen = new LettersScreen(ui, voice, CloseScreen);
        }

        void Open(Func<VisualElement, VisualElement> build, Action closed = null)
        {
            VisualElement element = null;
            ShowScreen(() => element.RemoveFromHierarchy(), closed);
            element = build(ui);
        }

        void ShowScreen(Action remove, Action closed)
        {
            bubble.style.opacity = 0f;
            hud.style.display = DisplayStyle.None;
            voice.Stop();
            cam.enabled = false;
            closeScreen = () =>
            {
                remove();
                closed?.Invoke();
            };
        }

        void CloseScreen()
        {
            voice.Stop();
            closeScreen?.Invoke();
            cam.enabled = true;
            hud.style.display = DisplayStyle.Flex;
            RefreshHud();
            // Wait a frame so the tap that closed the screen doesn't also land in the room
            StartCoroutine(ClearScreenNextFrame());
        }

        IEnumerator ClearScreenNextFrame()
        {
            yield return null;
            closeScreen = null;
        }
    }
}
