using System;
using System.Collections;
using UnityEngine;

namespace Usrah
{
    /// <summary>Small movements that make the room feel alive: tap bounces, the real clock, the cat, the door.</summary>
    public class RoomLife : MonoBehaviour
    {
        Transform hourHand, minuteHand, doorLeaf, cat;
        Quaternion hourStart, minuteStart, doorStart;
        Vector3 catScale;

        public void Find(Transform room, Transform catRoot)
        {
            hourHand = Child(room, "hand_hour");
            minuteHand = Child(room, "hand_min");
            doorLeaf = Child(room, "door_leaf");
            cat = catRoot;
            hourStart = hourHand.rotation;
            minuteStart = minuteHand.rotation;
            doorStart = doorLeaf.rotation;
            catScale = cat.localScale;
        }

        public static Transform Child(Transform root, string name)
        {
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (t.name == name) return t;
            throw new ArgumentException($"No part named {name} under {root.name}");
        }

        void Update()
        {
            var now = DateTime.Now;
            var minutes = now.Minute + now.Second / 60f;
            minuteHand.rotation = Quaternion.AngleAxis(-minutes * 6f, Vector3.forward) * minuteStart;
            hourHand.rotation = Quaternion.AngleAxis(-((now.Hour % 12) + minutes / 60f) * 30f, Vector3.forward) * hourStart;

            // The sleeping cat breathes
            var breath = 1f + Mathf.Sin(Time.time * 1.6f) * .018f;
            cat.localScale = new Vector3(catScale.x * (2f - breath), catScale.y * breath, catScale.z);
        }

        public void Bounce(Transform target) => StartCoroutine(BounceRoutine(target));

        static IEnumerator BounceRoutine(Transform target)
        {
            var start = target.localScale;
            const float duration = .42f;
            for (var t = 0f; t < duration; t += Time.deltaTime)
            {
                var k = t / duration;
                var wave = Mathf.Sin(k * Mathf.PI * 2.5f) * (1f - k);
                target.localScale = new Vector3(start.x * (1f + wave * .14f), start.y * (1f + wave * .2f), start.z * (1f + wave * .14f));
                yield return null;
            }
            target.localScale = start;
        }

        /// <summary>Swing the door open, then call back. Swing it shut with Close.</summary>
        public void OpenDoor(Action done) => StartCoroutine(Swing(doorStart, Quaternion.AngleAxis(-52f, Vector3.up) * doorStart, done));

        public void CloseDoor() => StartCoroutine(Swing(doorLeaf.rotation, doorStart, null));

        IEnumerator Swing(Quaternion from, Quaternion to, Action done)
        {
            const float duration = .5f;
            for (var t = 0f; t < duration; t += Time.deltaTime)
            {
                doorLeaf.rotation = Quaternion.Slerp(from, to, Mathf.SmoothStep(0f, 1f, t / duration));
                yield return null;
            }
            doorLeaf.rotation = to;
            done?.Invoke();
        }
    }
}
