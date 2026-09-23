"""
Exemplo trabalhado do Quadro 2 (Seção 5.1.3) — motif-align, TCC.

Alinha os sopranos de BWV 244.15 e BWV 244.62 (music21) com a representação
da Eq. 4, a pontuação da Eq. 7, a recorrência de Smith-Waterman (Eq. 2) com
gap linear e o critério de X-drop (Eq. 3), a partir do hit da semente inicial.
Pesos ilustrativos, não calibrados.  Testado com music21 10.5.0.
"""
import math
from music21 import corpus

ALFA, BETA, GAMA, RHO, G, X, K = 2, 1, 1, 1, 2, 5, 4


def representa(nome):
    soprano = corpus.parse(nome).parts[0].flatten().notes
    ev = [(n.pitch, float(n.quarterLength)) for n in soprano if n.isNote]
    seq = [(b[0].diatonicNoteNum - a[0].diatonicNoteNum, b[0].midi - a[0].midi, b[1] / a[1])
           for a, b in zip(ev, ev[1:])]
    return ev[0][0], seq


def s(a, b):  # Eq. 7
    return ((ALFA if a[0] == b[0] else -BETA) + (GAMA if a[1] == b[1] else 0)
            - RHO * abs(math.log2(a[2] / b[2])))


def estende_direita(A, B, i0, j0):  # Eq. 2 com gap linear + X-drop (Eq. 3)
    semente = sum(s(A[i0 + t], B[j0 + t]) for t in range(K))
    H = {(i0 + K - 1, j0 + K - 1): semente}
    melhor = (semente, i0 + K - 1, j0 + K - 1)
    for i in range(i0 + K, len(A)):
        vivo = False
        for j in range(j0 + K, len(B)):
            cand = []
            if (i - 1, j - 1) in H: cand.append(H[(i - 1, j - 1)] + s(A[i], B[j]))
            if (i - 1, j) in H: cand.append(H[(i - 1, j)] - G)
            if (i, j - 1) in H: cand.append(H[(i, j - 1)] - G)
            if not cand: continue
            v = max(cand)
            if v < melhor[0] - X: continue
            H[(i, j)] = v; vivo = True
            if v > melhor[0]: melhor = (v, i, j)
        if not vivo: break
    return semente, melhor


ancA, A = representa("bwv244.15")
ancB, B = representa("bwv244.62")
print("âncoras:", ancA.nameWithOctave, ancB.nameWithOctave, "| transposição:", ancB.midi - ancA.midi, "semitons")
print("semente:", tuple(x[0] for x in A[:K]), "| hit em B, posição 1:", tuple(x[0] for x in B[:K]) == tuple(x[0] for x in A[:K]))
semente, (escore, i, j) = estende_direita(A, B, 0, 0)
print(f"escore da semente: {semente} | escore máximo: {escore:.1f}")
print(f"cobertura: {i + 2} notas de BWV 244.15, {j + 2} notas de BWV 244.62")
