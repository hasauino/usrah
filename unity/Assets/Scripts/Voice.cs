using System;
using System.Collections;
using UnityEngine;

namespace Usrah
{
    /// <summary>Plays spoken lines by key, one at a time. A new line replaces the one playing.</summary>
    public class Voice : MonoBehaviour
    {
        AudioSource source;
        Coroutine sequence;

        /// <summary>Raised with a line's key and length when it starts: for نبيه's mouth and bubble.</summary>
        public event Action<string, float> Speaking;

        void Awake()
        {
            source = gameObject.AddComponent<AudioSource>();
            source.playOnAwake = false;
            source.spatialBlend = 0f;
        }

        public float Say(string key)
        {
            if (sequence != null) { StopCoroutine(sequence); sequence = null; }
            return PlayLine(key);
        }

        /// <summary>Say several lines in order.</summary>
        public void Say(params string[] keys)
        {
            if (sequence != null) StopCoroutine(sequence);
            sequence = StartCoroutine(SayAll(keys));
        }

        public void Stop()
        {
            if (sequence != null) { StopCoroutine(sequence); sequence = null; }
            source.Stop();
        }

        float PlayLine(string key)
        {
            var clip = Resources.Load<AudioClip>("Voice/" + key);
            if (clip == null) return 0f;
            source.Stop();
            Speaking?.Invoke(key, clip.length);
            if (!Progress.SoundOn) return clip.length;
            source.clip = clip;
            source.Play();
            return clip.length;
        }

        IEnumerator SayAll(string[] keys)
        {
            foreach (var key in keys)
            {
                var length = PlayLine(key);
                yield return new WaitForSeconds(length + .15f);
            }
            sequence = null;
        }
    }
}
