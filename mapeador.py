import pygame
import json
import sys

pygame.init()
pygame.mixer.init()

# ---------------- CONFIGURAÇÕES ----------------
ARQUIVO_MUSICA = "sons/Tetris.mp3"
ARQUIVO_MAPA = "beatmap.json"

# Teclas que o script vai reconhecer e salvar
TECLAS_VALIDAS = {
    pygame.K_d: "d",
    pygame.K_r: "r",
    pygame.K_m: "m",
    pygame.K_f: "f",
    pygame.K_s: "s",
    pygame.K_l: "l",
    pygame.K_c: "c",
}

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Just Libras - Criador de Beatmap")
font = pygame.font.SysFont(None, 48)

notas_gravadas = []

print("=== CRIADOR DE BEATMAP ===")
print("1. Pressione ESPAÇO para começar a música.")
print("2. Pressione as teclas (D, R, M, F, S, L, C) no ritmo da música.")
print("3. Feche a janela para salvar e sair.")

rodando = True
gravando = False

while rodando:
    screen.fill((30, 30, 30))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not gravando:
                pygame.mixer.music.load(ARQUIVO_MUSICA)
                pygame.mixer.music.play()
                gravando = True
                print("Gravando! Aperte as teclas no ritmo!")
                
            # Se estiver gravando e apertou uma tecla válida
            if gravando and event.key in TECLAS_VALIDAS:
                tempo_atual = pygame.mixer.music.get_pos()
                letra = TECLAS_VALIDAS[event.key]
                
                # Salva o exato milissegundo em que você apertou a tecla
                notas_gravadas.append({
                    "tempo_alvo": tempo_atual,
                    "sinal": letra,
                    "atingida": False
                })
                print(f"Nota salva: {letra.upper()} em {tempo_atual}ms")

    # Desenhar textos na tela
    if not gravando:
        texto = font.render("Aperte ESPAÇO para iniciar", True, (255, 255, 255))
    else:
        tempo = pygame.mixer.music.get_pos()
        texto = font.render(f"Gravando... Tempo: {tempo}ms", True, (0, 255, 0))
        
    texto_qtd = font.render(f"Notas gravadas: {len(notas_gravadas)}", True, (200, 200, 200))
    
    screen.blit(texto, (50, 150))
    screen.blit(texto_qtd, (50, 220))
    
    pygame.display.flip()

pygame.quit()

# Quando a janela fecha, salva tudo num arquivo JSON
if notas_gravadas:
    with open(ARQUIVO_MAPA, "w") as f:
        json.dump(notas_gravadas, f, indent=4)
    print(f"\nSucesso! {len(notas_gravadas)} notas foram salvas no arquivo '{ARQUIVO_MAPA}'.")
else:
    print("\nNenhuma nota foi gravada.")