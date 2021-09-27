import pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence
import sys

# --- NICHT ALLE FUNKTIONEN WURDEN VERWENDET, ES WURD NICHT ON SILENCE GESPLITTET! --- #
class Aussprache_Trainer:

    def init(self):
        sound = pydub.AudioSegment.from_mp3(r"C:\Users\LuisP\OneDrive\Desktop\common_voice_de_22192947.mp3")
        normalized_sound = Aussprache_Trainer.match_target_amplitude(self, sound, -20.0)
        normalized_sound.export("normalizedAudio.wav", format="wav")

        start = Aussprache_Trainer.detect_leading_silence(self, sound)
        end = Aussprache_Trainer.detect_leading_silence(self, sound.reverse())
        duration = len(sound)
        trimmed_sound = sound[start:duration - end]
        trimmed_sound.export("normalizedAudio2.wav", format="wav")
        Aussprache_Trainer.test(self)

    def detect_leading_silence(self, sound, silence_treshhold = -50, chunk_size = 10):
        trim_ms = 0
        while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_treshhold:
            trim_ms += chunk_size
        print(trim_ms)
        return trim_ms
    #https://stackoverflow.com/questions/37725416/pydub-combine-split-on-silence-with-minimum-length-file-size
    def test(self):
        sound_file = AudioSegment.from_wav("normalizedAudio2.wav")
        audio_chunks = split_on_silence(sound_file,
        # must be silent for at least half a second
        min_silence_len=450,
        # consider it silent if quieter than -16 dBFS
        silence_thresh=-16,

        keep_silence=300
        )

        for i, chunk in enumerate(audio_chunks):

            out_file = r"C:\Users\LuisP\PycharmProjects\pythonProject\splitaudio\chunk{0}.wav".format(i)
            print("exporting", out_file)
            chunk.export(out_file, format="wav")


    def match_target_amplitude(self,sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

Aussprache_Trainer()
