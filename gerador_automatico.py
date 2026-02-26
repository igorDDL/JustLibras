import librosa
import json
import random

# ---------------- CONFIGURAÇÕES ----------------
ARQUIVO_MUSICA = "sons/Tetris.mp3"
ARQUIVO_MAPA = "beatmap.json"
SINAIS = ['d', 'r', 'm', 'f', 's', 'l', 'c']

# 1. TEMPO - 1.2 segundos para trocar de mão
DISTANCIA_MINIMA_MS = 1200 

# 2. CHANCE DE PAUSA: 25% de chance de o jogo "pular" uma batida propositalmente
CHANCE_DE_PAUSA = 0.25 

print("Carregando e analisando a música... Aguarde um momento.")

y, sr = librosa.load(ARQUIVO_MUSICA)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

notas_geradas = []
ultimo_tempo_salvo = 0

for tempo_segundos in beat_times:
    tempo_ms = int(tempo_segundos * 1000)
    
    if tempo_ms > 2000 and (tempo_ms - ultimo_tempo_salvo) >= DISTANCIA_MINIMA_MS:
        
        # Sorteia um número de 0.0 a 1.0. Se for MAIOR que a chance de pausa, ele cria a nota.
        if random.random() > CHANCE_DE_PAUSA:
            sinal_aleatorio = random.choice(SINAIS)
            
            notas_geradas.append({
                "tempo_alvo": tempo_ms,
                "sinal": sinal_aleatorio,
                "atingida": False
            })
        
        # Mesmo se ele tiver "pausado" ou criado a nota, atualizamos o tempo
        # Isso garante que a próxima nota só venha depois de mais 1200ms
        ultimo_tempo_salvo = tempo_ms

with open(ARQUIVO_MAPA, "w") as f:
    json.dump(notas_geradas, f, indent=4)

print(f"\n--- SUCESSO! ---")
print(f"Foram geradas {len(notas_geradas)} notas de forma mais espaçada e natural.")
print(f"Arquivo '{ARQUIVO_MAPA}' atualizado. Pode testar o jogo!")