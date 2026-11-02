using System;
using System.Collections.Generic;
using UnityEngine;

namespace Usrah
{
    /// <summary>All Arabic content, read from Resources/Content/letters.json. No strings live in code.</summary>
    public static class Content
    {
        [Serializable] public class Letter { public string letter, name, word, image; }
        [Serializable] class Line { public string key = "", text = ""; }
        [Serializable] class File { public Letter[] letters = null; public string[] numbers = null; public Line[] lines = null, ui = null; }

        public static Letter[] Letters { get; private set; }
        static readonly Dictionary<string, string> Text = new();

        public static void Load()
        {
            var file = JsonUtility.FromJson<File>(Resources.Load<TextAsset>("Content/letters").text);
            Letters = file.letters;
            foreach (var line in file.lines) Text[line.key] = line.text;
            foreach (var line in file.ui) Text[line.key] = line.text;
        }

        public static string T(string key) => Text.TryGetValue(key, out var value) ? value : key;

        /// <summary>A number in the digits the parent chose: ١٢٣ by default, or 123.</summary>
        public static string Digits(int value)
        {
            var text = value.ToString();
            if (!Progress.EasternDigits) return text;
            var result = new char[text.Length];
            for (var i = 0; i < text.Length; i++)
                result[i] = char.IsDigit(text[i]) ? (char)('٠' + (text[i] - '0')) : text[i];
            return new string(result);
        }

        /// <summary>The word with its first letter and that letter's marks in the highlight colour.</summary>
        public static string WordWithFirstLetterHighlighted(string word)
        {
            var end = 1;
            while (end < word.Length && word[end] >= 'ً' && word[end] <= 'ْ') end++;
            return $"<color=#D9413D>{word.Substring(0, end)}</color>{word.Substring(end)}";
        }

        public static Texture2D Picture(string name) => Resources.Load<Texture2D>("Words/" + name);
        public static Texture2D Portrait(string name) => Resources.Load<Texture2D>("Portraits/" + name);
    }
}
