import pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence
import sys
import tqdm
from tqdm import tqdm

class AusspracheTrainer:
    def __init__(self):
        AusspracheTrainer.tsv_parsen(self)

    def detect_leading_silence(self, sound, silence_treshhold = -50, chunk_size = 10):
        trim_ms = 0
        while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_treshhold:
            trim_ms += chunk_size
        print(trim_ms)
        return trim_ms

    def match_target_amplitude(self,sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)


    def tsv_parsen(self):
        with open(r"validated.tsv", newline="", encoding="utf-8-sig") as csvfile:
            spamreader = csv.reader(csvfile, delimiter="\t", quotechar='|')
            with tqdm(total=565187) as pbar:
                for row in spamreader:
                    if row[-3] == "germany":
                        #DATEI, new Dir
                        sound = pydub.AudioSegment.from_mp3("C:\\ORDNER\\%s" % (str(row[1])))
                        normalized_sound = Aussprache_Trainer.match_target_amplitude(self, sound, -20.0)
                        # DATEI new Dir2
                        normalized_sound.export("C:\\NEWDIR\\%s.wav" % (str(row[1]).replace(".mp3", "")), format="wav")
                        sound = pydub.AudioSegment.from_file("C:\\NEUERORDNER\\%s.wav" % (str(row[1]).replace(".mp3", "")), format="wav")
                        start = Aussprache_Trainer.detect_leading_silence(self, sound)
                        end = Aussprache_Trainer.detect_leading_silence(self, sound.reverse())
                        duration = len(sound)
                        trimmed_sound = sound[start:duration - end]
                        trimmed_sound.export("C:\\NEWDIR2\\%s.wav" % (str(row[1]).replace(".mp3", "")), format="wav")
                    pbar.update((1 / gesamtlaenge))


Aussprache_Trainer()
