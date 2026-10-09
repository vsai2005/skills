import unittest

from scripts.voice_profile import compare_profiles, profile_text


class VoiceProfileTests(unittest.TestCase):
    def test_profile_reports_observable_style_metrics(self):
        sample = "I don't want a long intro. Start with the answer. Then explain why it matters, and keep the example short.\n\nIf a detail is uncertain, say so."
        profile = profile_text(sample)
        self.assertGreater(profile["contractions_per_100_words"], 0)
        self.assertGreater(profile["first_person_per_100_words"], 0)
        self.assertGreater(profile["sentence_count"], 2)

    def test_compare_flags_large_style_shift(self):
        reference = profile_text("I don't want a long intro. Start with the answer. Keep it short.\n\nSay what changed and why.")
        candidate = profile_text(
            "Furthermore, the implementation demonstrates a comprehensive methodological orientation toward highly elaborated explanatory structures; "
            "therefore, the resulting communication contains substantially longer constructions and a considerably more formalized lexical register."
        )
        comparison = compare_profiles(reference, candidate)
        self.assertFalse(comparison["close_enough"])
        self.assertTrue(comparison["large_differences"])

    def test_same_text_profiles_match(self):
        text = "Start with the point. Explain the reason in one paragraph. Keep the example concrete."
        profile = profile_text(text)
        comparison = compare_profiles(profile, profile)
        self.assertTrue(comparison["close_enough"])
        self.assertEqual([], comparison["large_differences"])


if __name__ == "__main__":
    unittest.main()
