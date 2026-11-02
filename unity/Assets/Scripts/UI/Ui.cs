using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace Usrah
{
    /// <summary>Building blocks shared by every screen: big tap targets, icons, palette.</summary>
    public static class Ui
    {
        public static readonly string[] Palette =
            { "#D9413D", "#2F9C95", "#3D7BD9", "#E9843A", "#7A5FA8", "#58A649", "#D9734E" };

        public static Color ColorOf(string hex)
        {
            ColorUtility.TryParseHtmlString(hex, out var color);
            return color;
        }

        public static VisualElement Box(string classes, VisualElement parent = null)
        {
            var box = new VisualElement();
            foreach (var c in classes.Split(' ')) box.AddToClassList(c);
            parent?.Add(box);
            return box;
        }

        public static Label Text(string text, string classes, VisualElement parent = null)
        {
            var label = new Label(text);
            foreach (var c in classes.Split(' ')) label.AddToClassList(c);
            label.pickingMode = PickingMode.Ignore;
            parent?.Add(label);
            return label;
        }

        public static Button Tap(string classes, Action action, VisualElement parent = null, string text = "")
        {
            var button = new Button(action) { text = text };
            button.AddToClassList("tap");
            foreach (var c in classes.Split(' ')) button.AddToClassList(c);
            parent?.Add(button);
            return button;
        }

        public static VisualElement Picture(Texture2D texture, string classes, VisualElement parent = null)
        {
            var box = Box(classes, parent);
            box.style.backgroundImage = new StyleBackground(texture);
            box.pickingMode = PickingMode.Ignore;
            return box;
        }

        /// <summary>Icon-only round button, so children who can't read yet can use it.</summary>
        public static Button IconButton(IconKind kind, string classes, Action action, VisualElement parent = null)
        {
            var button = Tap("icon-button " + classes, action, parent);
            var icon = new Icon(kind) { pickingMode = PickingMode.Ignore };
            icon.AddToClassList("icon");
            button.Add(icon);
            return button;
        }

        /// <summary>Run after a delay, on the element's scheduler, so it stops if the screen goes away.</summary>
        public static void After(VisualElement element, float seconds, Action action) =>
            element.schedule.Execute(action).ExecuteLater((long)(seconds * 1000));
    }

    public enum IconKind { Home, Speaker, Next, Previous, Play, Star }

    /// <summary>Crisp vector icons drawn in code.</summary>
    public class Icon : VisualElement
    {
        readonly IconKind kind;

        public Icon(IconKind kind)
        {
            this.kind = kind;
            generateVisualContent += Draw;
        }

        void Draw(MeshGenerationContext context)
        {
            var p = context.painter2D;
            var size = Mathf.Min(contentRect.width, contentRect.height);
            if (size <= 0f) return;
            Vector2 At(float x, float y) => new(x * size, y * size);
            var color = kind == IconKind.Star ? Ui.ColorOf("#F4C542") : Color.white;
            p.fillColor = color;
            p.strokeColor = color;
            p.lineJoin = LineJoin.Round;
            p.lineCap = LineCap.Round;
            p.BeginPath();
            switch (kind)
            {
                case IconKind.Home:
                    Poly(p, At(.5f, .1f), At(.95f, .52f), At(.8f, .52f), At(.8f, .9f), At(.58f, .9f), At(.58f, .62f),
                        At(.42f, .62f), At(.42f, .9f), At(.2f, .9f), At(.2f, .52f), At(.05f, .52f));
                    p.Fill();
                    break;
                case IconKind.Speaker:
                    Poly(p, At(.12f, .38f), At(.3f, .38f), At(.54f, .16f), At(.54f, .84f), At(.3f, .62f), At(.12f, .62f));
                    p.Fill();
                    p.lineWidth = size * .08f;
                    p.BeginPath();
                    p.Arc(At(.5f, .5f), size * .22f, -50f, 50f);
                    p.Stroke();
                    p.BeginPath();
                    p.Arc(At(.5f, .5f), size * .38f, -50f, 50f);
                    p.Stroke();
                    break;
                case IconKind.Next: // Reading runs right to left, so "next" points left
                    Poly(p, At(.68f, .12f), At(.68f, .88f), At(.2f, .5f));
                    p.Fill();
                    break;
                case IconKind.Previous:
                    Poly(p, At(.32f, .12f), At(.32f, .88f), At(.8f, .5f));
                    p.Fill();
                    break;
                case IconKind.Play:
                    Poly(p, At(.28f, .12f), At(.28f, .88f), At(.88f, .5f));
                    p.Fill();
                    break;
                case IconKind.Star:
                    var points = new Vector2[10];
                    for (var i = 0; i < 10; i++)
                    {
                        var a = -Mathf.PI / 2f + i * Mathf.PI / 5f;
                        var r = i % 2 == 0 ? .48f : .22f;
                        points[i] = At(.5f + Mathf.Cos(a) * r, .52f + Mathf.Sin(a) * r);
                    }
                    Poly(p, points);
                    p.Fill();
                    break;
            }
        }

        static void Poly(Painter2D p, params Vector2[] points)
        {
            p.MoveTo(points[0]);
            for (var i = 1; i < points.Length; i++) p.LineTo(points[i]);
            p.ClosePath();
        }
    }
}
