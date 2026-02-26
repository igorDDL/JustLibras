import cv2
import mediapipe as mp
import pickle
import numpy as np
import pygame
import sys
import json
import os

# ==========================================
# 1. INICIALIZAÇÃO DE MODELOS E MEDIAPIPE
# ==========================================
MODEL_FILE = 'libras_model.pkl'

try:
    with open(MODEL_FILE, 'rb') as f:
        model_data = pickle.load(f)
    model = model_data['model']
    scaler = model_data['scaler']
    print(f"Modelo '{MODEL_FILE}' carregado com sucesso!")
except FileNotFoundError:
    print(f"Erro: Arquivo do modelo '{MODEL_FILE}' não encontrado.")
    sys.exit()
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    sys.exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# ==========================================
# 2. CONFIGURAÇÕES DE VÍDEO E ÁUDIO
# ==========================================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    sys.exit()

WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

pygame.mixer.init()
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Just Libras - Rhythm Edition")
clock = pygame.time.Clock()

CAMINHO_FONTE = "fontes/Limpa.ttf" 
if not os.path.exists(CAMINHO_FONTE):
    def get_font(size): return pygame.font.SysFont(None, size)
else:
    def get_font(size): return pygame.font.Font(CAMINHO_FONTE, size)

font_rank_gigante = get_font(200) 
font_titulo_performance = get_font(80)
font_grande = get_font(60)
font_media = get_font(40)
font_pequena = get_font(30)

try:
    som_acerto = pygame.mixer.Sound("sons/acerto.mp3")
    som_acerto.set_volume(0.6)
except: som_acerto = None

try:
    som_falha = pygame.mixer.Sound("sons/falha.mp3")
    som_falha.set_volume(0.4)
except: som_falha = None

volume_atual = 0.5

# ==========================================
# 3. VARIÁVEIS DE ESTADO E PLAYLIST
# ==========================================
# SISTEMA DE PLAYLIST
PLAYLIST = [
    {"titulo": "Super Mario", "audio": "sons/super_mario.mp3", "mapa": "mapa_mario.json"},
    {"titulo": "Tetris Theme", "audio": "sons/Tetris.mp3", "mapa": "mapa_tetris.json"}
]
musica_selecionada = 0 # Índice da música atual na tela

pontos = 0
notas_acertadas = 0
total_notas = 0
feedback_cor = (0, 0, 0)
HIT_ZONE_Y = HEIGHT - 100
TEMPO_VISIVEL = 2000
JANELA_ACERTO = 400

estado_jogo = "MENU" 

largura_btn = 350
altura_btn = 80
botao_start = pygame.Rect(WIDTH // 2 - largura_btn // 2, HEIGHT // 2 + 50, largura_btn, altura_btn)
botao_voltar = pygame.Rect(WIDTH // 2 - largura_btn // 2, HEIGHT - 120, largura_btn, altura_btn)

MUSICA_ATUAL = []

def calcular_rank(taxa):
    if taxa >= 95: return "S", (255, 215, 0) 
    if taxa >= 85: return "A", (0, 255, 0)   
    if taxa >= 70: return "B", (0, 200, 255) 
    if taxa >= 50: return "C", (255, 165, 0) 
    return "D", (255, 0, 0)                 

def iniciar_partida():
    global MUSICA_ATUAL, pontos, notas_acertadas, total_notas, feedback_cor
    
    nivel = PLAYLIST[musica_selecionada]
    
    # Carrega o mapa específico da música escolhida
    try:
        with open(nivel["mapa"], "r") as f:
            MUSICA_ATUAL = json.load(f)
        total_notas = len(MUSICA_ATUAL)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nivel['mapa']}' não encontrado.")
        print("Certifique-se de que o arquivo existe na pasta antes de jogar esta música!")
        sys.exit()
    
    # Carrega e toca o áudio específico
    pygame.mixer.music.load(nivel["audio"])
    pygame.mixer.music.set_volume(volume_atual)
    
    pontos = 0
    notas_acertadas = 0
    feedback_cor = (0, 0, 0)
    
    for nota in MUSICA_ATUAL:
        nota["atingida"] = False
        
    pygame.mixer.music.play()

# ==========================================
# 4. LOOP PRINCIPAL
# ==========================================
running = True
while running:
    
    # Configuração dos botões de seta dinamicamente
    texto_musica_menu = font_grande.render(PLAYLIST[musica_selecionada]["titulo"], True, (0, 255, 255))
    pos_y_selecao = HEIGHT // 2 - 60
    btn_esq = pygame.Rect(WIDTH // 2 - texto_musica_menu.get_width() // 2 - 80, pos_y_selecao, 60, 60)
    btn_dir = pygame.Rect(WIDTH // 2 + texto_musica_menu.get_width() // 2 + 20, pos_y_selecao, 60, 60)

    # --- PROCESSAMENTO DE EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_UP:
                volume_atual = min(1.0, volume_atual + 0.1)
                pygame.mixer.music.set_volume(volume_atual)
            if event.key == pygame.K_DOWN:
                volume_atual = max(0.0, volume_atual - 0.1)
                pygame.mixer.music.set_volume(volume_atual)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos() 
            if estado_jogo == "MENU":
                if botao_start.collidepoint(mouse_pos): 
                    iniciar_partida()
                    estado_jogo = "JOGANDO"
                #CLIQUE NAS SETAS
                elif btn_esq.collidepoint(mouse_pos):
                    musica_selecionada = (musica_selecionada - 1) % len(PLAYLIST)
                elif btn_dir.collidepoint(mouse_pos):
                    musica_selecionada = (musica_selecionada + 1) % len(PLAYLIST)
            
            elif estado_jogo == "RESULTADOS" and botao_voltar.collidepoint(mouse_pos):
                estado_jogo = "MENU"

    # --- PROCESSAMENTO DE VISÃO COMPUTACIONAL ---
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    image_rgb_final = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.image.frombuffer(image_rgb_final.tobytes(), (WIDTH, HEIGHT), 'RGB')
    screen.blit(frame_surface, (0, 0))

    # --- MÁQUINA DE ESTADOS ---
    if estado_jogo == "MENU":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180) 
        overlay.fill((10, 10, 20)) 
        screen.blit(overlay, (0, 0))

        texto_titulo = font_titulo_performance.render("JUST LIBRAS", True, (255, 215, 0))
        screen.blit(texto_titulo, (WIDTH // 2 - texto_titulo.get_width() // 2, HEIGHT // 4))

        #DESENHAR SELETOR DE MÚSICA
        screen.blit(texto_musica_menu, (WIDTH // 2 - texto_musica_menu.get_width() // 2, pos_y_selecao + 5))
        
        texto_esq = font_grande.render("<", True, (255, 255, 255))
        texto_dir = font_grande.render(">", True, (255, 255, 255))
        
        # Efeito de hover nas setas
        mouse_pos = pygame.mouse.get_pos()
        cor_seta_esq = (0, 255, 255) if btn_esq.collidepoint(mouse_pos) else (255, 255, 255)
        cor_seta_dir = (0, 255, 255) if btn_dir.collidepoint(mouse_pos) else (255, 255, 255)

        texto_esq = font_grande.render("<", True, cor_seta_esq)
        texto_dir = font_grande.render(">", True, cor_seta_dir)

        screen.blit(texto_esq, (btn_esq.x + 10, btn_esq.y))
        screen.blit(texto_dir, (btn_dir.x + 10, btn_dir.y))

        # Botão Iniciar
        cor_btn = (0, 200, 100) if botao_start.collidepoint(mouse_pos) else (0, 150, 70)
        pygame.draw.rect(screen, cor_btn, botao_start, border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), botao_start, width=2, border_radius=20) 
        
        texto_btn = font_grande.render("INICIAR", True, (255, 255, 255))
        screen.blit(texto_btn, (botao_start.centerx - texto_btn.get_width() // 2, botao_start.centery - texto_btn.get_height() // 2))

    elif estado_jogo == "JOGANDO":
        tempo_atual = pygame.mixer.music.get_pos()
        
        if not pygame.mixer.music.get_busy() and tempo_atual == -1:
            estado_jogo = "RESULTADOS"

        prediction_text = "Nenhuma mao detectada"
        predicted_letter = ""
        confidence = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                try:
                    landmarks = hand_landmarks.landmark
                    flat_landmarks = [coord for lm in landmarks for coord in (lm.x, lm.y, lm.z)]
                    
                    data_row = np.array([flat_landmarks])
                    data_row_scaled = scaler.transform(data_row)
                    prediction = model.predict(data_row_scaled)
                    predicted_letter = prediction[0]
                    confidence = np.max(model.predict_proba(data_row_scaled))

                    prediction_text = f"Pred: {predicted_letter.upper()} ({confidence * 100:.0f}%)"

                    if confidence > 0.70:
                        for nota in MUSICA_ATUAL:
                            if not nota["atingida"]:
                                distancia_tempo = abs(nota["tempo_alvo"] - tempo_atual)
                                
                                if distancia_tempo <= JANELA_ACERTO:
                                    if predicted_letter == nota["sinal"]:
                                        pontos += 10
                                        notas_acertadas += 1
                                        nota["atingida"] = True
                                        feedback_cor = (0, 255, 0)
                                        if som_acerto:
                                            som_acerto.play()
                                        break
                                
                                elif tempo_atual > nota["tempo_alvo"] + JANELA_ACERTO:
                                    nota["atingida"] = True
                                    feedback_cor = (255, 0, 0)
                                    if som_falha:
                                        som_falha.play()
                except Exception as e:
                    pass

        if tempo_atual % 500 < 50: 
            feedback_cor = (0, 0, 0)

        pygame.draw.line(screen, (255, 215, 0), (0, HIT_ZONE_Y), (WIDTH, HIT_ZONE_Y), 5)

        for nota in MUSICA_ATUAL:
            if not nota["atingida"]:
                tempo_falta = nota["tempo_alvo"] - tempo_atual
                if -JANELA_ACERTO < tempo_falta <= TEMPO_VISIVEL:
                    progresso = 1 - (tempo_falta / TEMPO_VISIVEL)
                    nota_y = int(HIT_ZONE_Y * progresso)
                    texto_nota = font_grande.render(nota["sinal"].upper(), True, (0, 255, 255))
                    screen.blit(texto_nota, (WIDTH // 2 - texto_nota.get_width() // 2, nota_y - texto_nota.get_height() // 2))

        texto_pontos = font_media.render(f"Pontos: {pontos}", True, (0, 255, 0))
        screen.blit(texto_pontos, (WIDTH - 200, 30))
        texto_pred = font_pequena.render(prediction_text, True, (255, 255, 255))
        screen.blit(texto_pred, (10, HEIGHT - 40))

        if feedback_cor != (0, 0, 0):
            pygame.draw.rect(screen, feedback_cor, (0, 0, WIDTH, HEIGHT), 10)

    elif estado_jogo == "RESULTADOS":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220) 
        overlay.fill((10, 10, 25)) 
        screen.blit(overlay, (0, 0))

        texto_fim = font_titulo_performance.render("PERFORMANCE", True, (255, 255, 255))
        screen.blit(texto_fim, (WIDTH // 2 - texto_fim.get_width() // 2, 60))

        taxa_acerto = (notas_acertadas / total_notas) * 100 if total_notas > 0 else 0
        rank_letra, rank_cor = calcular_rank(taxa_acerto)
        
        texto_rank = font_rank_gigante.render(rank_letra, True, rank_cor)
        pos_y_rank = HEIGHT // 2 - texto_rank.get_height() // 2 - 20
        screen.blit(texto_rank, (WIDTH // 2 - texto_rank.get_width() // 2, pos_y_rank))

        cor_estatistica = (220, 220, 220) 
        
        texto_pontos_finais = font_grande.render(f"{pontos} PONTOS", True, (0, 255, 0))
        pos_y_pontos = pos_y_rank + texto_rank.get_height() + 20
        screen.blit(texto_pontos_finais, (WIDTH // 2 - texto_pontos_finais.get_width() // 2, pos_y_pontos))

        pos_y_detalhes = pos_y_pontos + texto_pontos_finais.get_height() + 15
        
        texto_detalhes_acertos = font_media.render(f"Notas: {notas_acertadas} / {total_notas}", True, cor_estatistica)
        texto_detalhes_precisao = font_media.render(f"Precisão: {taxa_acerto:.1f}%", True, cor_estatistica)
        
        screen.blit(texto_detalhes_acertos, (WIDTH // 2 - texto_detalhes_acertos.get_width() // 2, pos_y_detalhes))
        screen.blit(texto_detalhes_precisao, (WIDTH // 2 - texto_detalhes_precisao.get_width() // 2, pos_y_detalhes + texto_detalhes_acertos.get_height() + 5))

        mouse_pos = pygame.mouse.get_pos()
        cor_btn_voltar = (50, 50, 70) if botao_voltar.collidepoint(mouse_pos) else (30, 30, 50)
        pygame.draw.rect(screen, cor_btn_voltar, botao_voltar, border_radius=20)
        pygame.draw.rect(screen, rank_cor, botao_voltar, width=3, border_radius=20) 
        
        texto_btn_voltar = font_media.render("MENU PRINCIPAL", True, (255, 255, 255))
        screen.blit(texto_btn_voltar, (botao_voltar.centerx - texto_btn_voltar.get_width() // 2, botao_voltar.centery - texto_btn_voltar.get_height() // 2))

    texto_volume = font_pequena.render(f"Vol: {int(volume_atual * 100)}%", True, (150, 150, 150))
    screen.blit(texto_volume, (10, 10))

    pygame.display.flip()
    clock.tick(30)

hands.close()
cap.release()
pygame.quit()