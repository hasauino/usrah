using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

namespace Usrah
{
    /// <summary>حروف وأرقام: letters and numbers, each with a learning card and games.</summary>
    public class LettersScreen
    {
        const int QuizRounds = 5;
        static readonly string[] CountingToys = { "apple", "duck", "star", "ball", "fish", "flower", "butterfly", "lemon", "bird", "frog" };

        readonly VisualElement root;
        readonly Voice voice;
        readonly Action close;
        VisualElement page;
        int quizRound, quizScore, attemptId;

        public LettersScreen(VisualElement parent, Voice voice, Action close)
        {
            this.voice = voice;
            this.close = close;
            root = Ui.Box("screen", parent);
            ShowMenu();
        }

        public void Remove() => root.RemoveFromHierarchy();

        // A page with the standard top bar: a way home, and a way back when there is one
        VisualElement NewPage(Action back)
        {
            attemptId++;
            root.Clear();
            page = Ui.Box("page", root);
            var bar = Ui.Box("topbar", page);
            Ui.IconButton(IconKind.Home, "home-button", () => { voice.Stop(); close(); }, bar);
            if (back != null) Ui.IconButton(IconKind.Previous, "back-button", () => { voice.Stop(); back(); }, bar);
            Ui.Box("spacer", bar);
            var stars = Ui.Box("stars-pill", bar);
            stars.Add(new Icon(IconKind.Star) { name = "star-icon", pickingMode = PickingMode.Ignore });
            Ui.Text(Content.Digits(Progress.Stars), "stars-count", stars);
            return page;
        }

        void ShowMenu()
        {
            var body = Ui.Box("menu", NewPage(null));
            var letters = Ui.Tap("menu-card card-letters", ShowLetterGrid, body);
            Ui.Text("أ ب ت", "menu-glyphs", letters);
            Ui.Text(Content.T("letters"), "menu-title", letters);
            var numbers = Ui.Tap("menu-card card-numbers", ShowNumberBoard, body);
            Ui.Text($"{Content.Digits(1)} {Content.Digits(2)} {Content.Digits(3)}", "menu-glyphs", numbers);
            Ui.Text(Content.T("numbers"), "menu-title", numbers);
        }

        // ---- Letters ----

        void ShowLetterGrid()
        {
            var body = NewPage(ShowMenu);
            var grid = Ui.Box("letter-grid", body);
            for (var i = 0; i < Content.Letters.Length; i++)
            {
                var index = i;
                var tile = Ui.Tap("letter-tile", () => ShowLetterCard(index), grid, Content.Letters[i].letter);
                tile.style.backgroundColor = Ui.ColorOf(Ui.Palette[i % Ui.Palette.Length]);
            }
            var play = Ui.Tap("play-button", StartLetterQuiz, body);
            play.Add(new Icon(IconKind.Play) { name = "play-icon", pickingMode = PickingMode.Ignore });
            Ui.Text(Content.T("play"), "play-label", play);
            voice.Say("pick_letter");
        }

        void ShowLetterCard(int index)
        {
            var item = Content.Letters[index];
            var body = NewPage(ShowLetterGrid);
            var card = Ui.Box("letter-card", body);

            var text = Ui.Box("card-text", card);
            Ui.Text(item.letter, "big-letter", text);
            var word = Ui.Text(Content.WordWithFirstLetterHighlighted(item.word), "big-word", text);
            word.enableRichText = true;
            Ui.Picture(Content.Picture(item.image), "card-picture", card);

            var tools = Ui.Box("card-tools", body);
            if (index > 0) Ui.IconButton(IconKind.Previous, "nav-button", () => ShowLetterCard(index - 1), tools);
            else Ui.Box("nav-gap", tools);
            Ui.IconButton(IconKind.Speaker, "speak-button", () => voice.Say($"letter_{index}", $"word_{index}"), tools);
            if (index < Content.Letters.Length - 1) Ui.IconButton(IconKind.Next, "nav-button", () => ShowLetterCard(index + 1), tools);
            else Ui.Box("nav-gap", tools);

            voice.Say($"letter_{index}", $"word_{index}");
        }

        void StartLetterQuiz()
        {
            quizRound = 0;
            quizScore = 0;
            NextLetterQuestion();
        }

        void NextLetterQuestion()
        {
            if (quizRound >= QuizRounds) { ShowReward(ShowLetterGrid); return; }
            quizRound++;
            var answer = UnityEngine.Random.Range(0, Content.Letters.Length);
            var item = Content.Letters[answer];

            var body = NewPage(ShowLetterGrid);
            Rounds(body);
            var quiz = Ui.Box("quiz", body);
            var options = Ui.Box("quiz-options", quiz);
            Ui.Picture(Content.Picture(item.image), "quiz-picture", quiz);

            var choices = Choices(answer, Content.Letters.Length, 3);
            var firstTry = true;
            foreach (var choice in choices)
            {
                var index = choice;
                Button tile = null;
                tile = Ui.Tap("answer-tile", () =>
                {
                    if (index == answer)
                    {
                        if (firstTry) quizScore++;
                        Correct(tile, new[] { $"word_{answer}", $"praise_{UnityEngine.Random.Range(0, 4)}" }, NextLetterQuestion, 2.3f, options);
                    }
                    else
                    {
                        firstTry = false;
                        Wrong(tile);
                    }
                }, options, Content.Letters[index].letter);
                tile.style.backgroundColor = Ui.ColorOf(Ui.Palette[index % Ui.Palette.Length]);
            }
            voice.Say("first_letter", $"word_{answer}");
        }

        // ---- Numbers ----

        void ShowNumberBoard()
        {
            var body = NewPage(ShowMenu);
            var grid = Ui.Box("number-grid", body);
            for (var n = 1; n <= 10; n++)
            {
                var value = n;
                var tile = Ui.Tap("number-tile", () => ShowNumberCard(value), grid, Content.Digits(n));
                tile.style.backgroundColor = Ui.ColorOf(Ui.Palette[n % Ui.Palette.Length]);
            }
            var games = Ui.Box("game-row", body);
            GameButton(games, "count", StartCounting);
            GameButton(games, "add_title", () => StartSums(true));
            GameButton(games, "sub_title", () => StartSums(false));
            voice.Say("pick_number");
        }

        static void GameButton(VisualElement parent, string title, Action action)
        {
            var play = Ui.Tap("play-button", action, parent);
            play.Add(new Icon(IconKind.Play) { name = "play-icon", pickingMode = PickingMode.Ignore });
            Ui.Text(Content.T(title), "play-label", play);
        }

        void ShowNumberCard(int value)
        {
            var body = NewPage(ShowNumberBoard);
            var card = Ui.Box("number-card", body);
            Ui.Text(Content.Digits(value), "big-letter", card);
            var toys = Ui.Box("toy-row", card);
            var picture = Content.Picture(CountingToys[value - 1]);
            var token = attemptId;
            // Toys arrive one at a time as they're counted
            for (var i = 1; i <= value; i++)
            {
                var count = i;
                Ui.After(body, count * .7f - .4f, () =>
                {
                    if (token != attemptId) return;
                    Ui.Picture(picture, "toy pop", toys);
                    voice.Say($"number_{count}");
                });
            }
            var tools = Ui.Box("card-tools", body);
            if (value > 1) Ui.IconButton(IconKind.Previous, "nav-button", () => ShowNumberCard(value - 1), tools);
            else Ui.Box("nav-gap", tools);
            Ui.IconButton(IconKind.Speaker, "speak-button", () => voice.Say($"number_{value}"), tools);
            if (value < 10) Ui.IconButton(IconKind.Next, "nav-button", () => ShowNumberCard(value + 1), tools);
            else Ui.Box("nav-gap", tools);
        }

        void StartCounting()
        {
            quizRound = 0;
            quizScore = 0;
            NextCountQuestion();
        }

        void NextCountQuestion()
        {
            if (quizRound >= QuizRounds) { ShowReward(ShowNumberBoard); return; }
            quizRound++;
            var answer = UnityEngine.Random.Range(1, 11);
            var body = NewPage(ShowNumberBoard);
            Rounds(body);
            var quiz = Ui.Box("quiz", body);
            var options = Ui.Box("quiz-options", quiz);
            var toys = Ui.Box("toy-row toy-row-quiz", quiz);
            var picture = Content.Picture(CountingToys[UnityEngine.Random.Range(0, CountingToys.Length)]);
            for (var i = 0; i < answer; i++) Ui.Picture(picture, "toy", toys);
            NumberOptions(options, answer, NextCountQuestion);
            voice.Say("how_many");
        }

        void StartSums(bool add)
        {
            quizRound = 0;
            quizScore = 0;
            NextSum(add);
        }

        void NextSum(bool add)
        {
            if (quizRound >= QuizRounds) { ShowReward(ShowNumberBoard); return; }
            quizRound++;
            int a, b, answer;
            if (add)
            {
                a = UnityEngine.Random.Range(1, 6);
                b = UnityEngine.Random.Range(1, 6);
                answer = a + b;
            }
            else
            {
                a = UnityEngine.Random.Range(2, 8);
                b = UnityEngine.Random.Range(1, a);
                answer = a - b;
            }
            var body = NewPage(ShowNumberBoard);
            Rounds(body);
            var quiz = Ui.Box("quiz", body);
            var options = Ui.Box("quiz-options", quiz);
            var sum = Ui.Box("sum", quiz);
            var picture = Content.Picture(CountingToys[UnityEngine.Random.Range(0, CountingToys.Length)]);
            SumGroup(sum, a, picture);
            Ui.Text(add ? "+" : "−", "sum-sign", sum);
            SumGroup(sum, b, picture);
            NumberOptions(options, answer, () => NextSum(add));
            voice.Say(add ? "add" : "subtract");
        }

        static void SumGroup(VisualElement parent, int count, Texture2D picture)
        {
            var group = Ui.Box("sum-group", parent);
            Ui.Text(Content.Digits(count), "sum-digit", group);
            var toys = Ui.Box("toy-row toy-row-sum", group);
            for (var i = 0; i < count; i++) Ui.Picture(picture, "toy", toys);
        }

        void NumberOptions(VisualElement options, int answer, Action next)
        {
            var firstTry = true;
            foreach (var value in Choices(answer - 1, 10, 3).Select(i => i + 1))
            {
                Button tile = null;
                var number = value;
                tile = Ui.Tap("answer-tile", () =>
                {
                    if (number == answer)
                    {
                        if (firstTry) quizScore++;
                        Correct(tile, new[] { $"number_{answer}", $"praise_{UnityEngine.Random.Range(0, 4)}" }, next, 2f, options);
                    }
                    else
                    {
                        firstTry = false;
                        Wrong(tile);
                    }
                }, options, Content.Digits(number));
                tile.style.backgroundColor = Ui.ColorOf(Ui.Palette[number % Ui.Palette.Length]);
            }
        }

        // ---- Shared game feel ----

        void Rounds(VisualElement body)
        {
            var dots = Ui.Box("round-dots", body);
            for (var i = 1; i <= QuizRounds; i++) Ui.Box(i < quizRound ? "dot dot-done" : i == quizRound ? "dot dot-now" : "dot", dots);
        }

        static List<int> Choices(int answer, int range, int count)
        {
            var picks = new List<int> { answer };
            while (picks.Count < count)
            {
                var other = UnityEngine.Random.Range(0, range);
                if (!picks.Contains(other)) picks.Add(other);
            }
            return picks.OrderBy(_ => UnityEngine.Random.value).ToList();
        }

        // Wrong answers fade away with a gentle prompt. No buzzer, as in the original.
        void Wrong(Button tile)
        {
            tile.SetEnabled(false);
            tile.AddToClassList("answer-gone");
            voice.Say("try_again");
        }

        void Correct(Button tile, string[] lines, Action next, float wait, VisualElement options)
        {
            foreach (var other in options.Children()) other.SetEnabled(false);
            tile.SetEnabled(true);
            tile.pickingMode = PickingMode.Ignore;
            tile.AddToClassList("answer-right");
            voice.Say(lines);
            var token = attemptId;
            Ui.After(root, wait, () => { if (token == attemptId) next(); });
        }

        void ShowReward(Action done)
        {
            Progress.Stars += quizScore;
            var body = NewPage(done);
            var reward = Ui.Box("reward", body);
            Ui.Picture(Content.Portrait("nabeeh"), "reward-nabeeh pop", reward);
            var stars = Ui.Box("reward-stars", reward);
            for (var i = 0; i < Mathf.Max(quizScore, 1); i++)
            {
                var star = new Icon(IconKind.Star) { pickingMode = PickingMode.Ignore };
                star.AddToClassList("reward-star");
                star.AddToClassList("pop");
                stars.Add(star);
            }
            Ui.IconButton(IconKind.Next, "nav-button", done, reward);
            voice.Say("well_done");
        }
    }
}
