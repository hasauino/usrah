using System;
using System.Collections;
using UnityEngine;

namespace Usrah
{
    /// <summary>نبيه's body language. Rigid parts driven by code: idle sway, blinking, talking, the roll-in.</summary>
    public class NabeehPuppet : MonoBehaviour
    {
        Transform head, eyeL, eyeR, mouth, body;
        Quaternion headStart;
        Vector3 eyeScale, mouthScale, restScale;
        float talkUntil, nextBlink;
        bool blinking;
        Renderer[] renderers;

        public void Find(Transform model)
        {
            head = RoomLife.Child(model, "head");
            eyeL = RoomLife.Child(model, "eye_l");
            eyeR = RoomLife.Child(model, "eye_r");
            mouth = RoomLife.Child(model, "mouth");
            body = RoomLife.Child(model, "body");
            headStart = head.localRotation;
            eyeScale = eyeL.localScale;
            mouthScale = mouth.localScale;
            restScale = transform.localScale;
            renderers = GetComponentsInChildren<Renderer>();
        }

        public void Talk(float seconds) => talkUntil = Time.time + seconds;

        void Update()
        {
            var t = Time.time;
            var talking = t < talkUntil;

            // Head: slow look around, with small nods while he talks
            var sway = Mathf.Sin(t * .7f) * 4f;
            var nod = talking ? Mathf.Sin(t * 7f) * 3.5f : Mathf.Sin(t * .9f) * 1.2f;
            head.localRotation = Quaternion.Euler(nod, sway, Mathf.Sin(t * .5f) * 1.5f) * headStart;

            // Mouth: opens and closes while talking
            var open = talking ? 1f + Mathf.Abs(Mathf.Sin(t * 13f)) * 1.8f : 1f;
            mouth.localScale = new Vector3(mouthScale.x, mouthScale.y, mouthScale.z * open);

            if (!blinking && t > nextBlink)
            {
                nextBlink = t + UnityEngine.Random.Range(2.2f, 5.5f);
                StartCoroutine(Blink());
            }
        }

        IEnumerator Blink()
        {
            blinking = true;
            const float duration = .14f;
            for (var e = 0f; e < duration; e += Time.deltaTime)
            {
                var open = Mathf.Abs(e / duration * 2f - 1f);
                var scale = new Vector3(eyeScale.x, eyeScale.y, eyeScale.z * Mathf.Max(.08f, open));
                eyeL.localScale = eyeR.localScale = scale;
                yield return null;
            }
            eyeL.localScale = eyeR.localScale = eyeScale;
            blinking = false;
        }

        /// <summary>A happy little hop, for tap reactions.</summary>
        public void Hop() => StartCoroutine(HopRoutine());

        IEnumerator HopRoutine()
        {
            var start = transform.position;
            const float duration = .4f;
            for (var e = 0f; e < duration; e += Time.deltaTime)
            {
                transform.position = start + Vector3.up * (Mathf.Sin(e / duration * Mathf.PI) * .07f);
                yield return null;
            }
            transform.position = start;
        }

        /// <summary>His entrance, as in the original: rolls in as a ball, hops up, and unfolds.</summary>
        public IEnumerator RollIn(Action arrived)
        {
            foreach (var r in renderers) r.enabled = false;
            var seat = transform.position;
            var ball = Instantiate(body.gameObject, null);
            ball.transform.localScale = restScale;
            foreach (var r in ball.GetComponentsInChildren<Renderer>()) r.enabled = true;
            var radius = .16f * restScale.y;
            // The ball's mesh sits at its model height, so wrap it to spin around its own centre
            var centre = new GameObject("rolling_ball").transform;
            var bounds = new Bounds(ball.transform.position, Vector3.zero);
            foreach (var r in ball.GetComponentsInChildren<Renderer>()) bounds.Encapsulate(r.bounds);
            centre.position = bounds.center;
            ball.transform.SetParent(centre, true);

            var from = new Vector3(-3.7f, radius, .9f);
            var floorEnd = new Vector3(seat.x, radius, seat.z - .62f);
            var seatCentre = seat + Vector3.up * .15f;
            const float rollTime = 1.7f, hopTime = .45f;
            for (var e = 0f; e < rollTime; e += Time.deltaTime)
            {
                var k = Mathf.SmoothStep(0f, 1f, e / rollTime);
                var at = Vector3.Lerp(from, floorEnd, k);
                at.y += Mathf.Abs(Mathf.Sin(k * Mathf.PI * 3f)) * (1f - k) * .22f;
                centre.position = at;
                centre.rotation = Quaternion.AngleAxis(-k * (floorEnd.x - from.x) / radius * Mathf.Rad2Deg, Vector3.forward);
                yield return null;
            }
            for (var e = 0f; e < hopTime; e += Time.deltaTime)
            {
                var k = e / hopTime;
                centre.position = Vector3.Lerp(floorEnd, seatCentre, k) + Vector3.up * (Mathf.Sin(k * Mathf.PI) * .35f);
                centre.Rotate(Vector3.forward, -420f * Time.deltaTime, Space.World);
                yield return null;
            }
            Destroy(centre.gameObject);

            // Unfold: springs out of the ball shape
            foreach (var r in renderers) r.enabled = true;
            const float unfold = .4f;
            for (var e = 0f; e < unfold; e += Time.deltaTime)
            {
                var k = e / unfold;
                var s = 1f + Mathf.Sin(k * Mathf.PI * 2f) * (1f - k) * .22f;
                transform.localScale = new Vector3(restScale.x * (2f - s), restScale.y * Mathf.Lerp(.4f, 1f, Mathf.Sqrt(k)) * s, restScale.z * (2f - s));
                yield return null;
            }
            transform.localScale = restScale;
            arrived?.Invoke();
        }
    }
}
