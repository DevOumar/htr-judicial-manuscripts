
from jiwer import wer
import editdistance

def cer(reference, hypothesis):
    dist = editdistance.eval(reference, hypothesis)
    return dist / max(len(reference), 1)

if __name__ == "__main__":
    ref = "registre judiciaire"
    hyp = "registre judiciare"

    print("CER:", cer(ref, hyp))
    print("WER:", wer(ref, hyp))
