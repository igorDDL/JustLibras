import pygame
import sys
import os

# ==========================================
# 1. INICIALIZAÇÃO IMEDIATA (SPLASH SCREEN)
# ==========================================
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Just Libras - Rhythm Edition")

# Carregar uma fonte
CAMINHO_FONTE = "fontes/Limpa.ttf" 
font_loading = pygame.font.Font(CAMINHO_FONTE, 40) if os.path.exists(CAMINHO_FONTE) else pygame.font.SysFont(None, 40)

# Desenhar a tela de carregamento
screen.fill((15, 35, 70)) #Azul Escuro
texto_loading = font_loading.render("Carregando...", True, (250, 250, 250))
screen.blit(texto_loading, (WIDTH // 2 - texto_loading.get_width() // 2, HEIGHT // 2))
pygame.display.flip() 

# =======================
# 2. CARREGAMENTO PESADO
# =======================
import cv2
import mediapipe as mp
import pickle
import numpy as np
import json

MODEL_FILE = 'libras_model.pkl'
try:
    with open(MODEL_FILE, 'rb') as f:
        model_data = pickle.load(f)
    model = model_data['model']
    scaler = model_data['scaler']
    print(f"Modelo '{MODEL_FILE}' carregado com sucesso!")
except FileNotFoundError:
    print(f"Erro: Ficheiro do modelo '{MODEL_FILE}' não encontrado.")
    sys.exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# INICIALIZAÇÃO DA CÂMARA 
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
   
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmara.")
        sys.exit()

# Reajusta o tamanho da tela caso a câmara não suporte HD
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
screen = pygame.display.set_mode((WIDTH, HEIGHT))

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

font_titulo = get_font(90)
font_grande = get_font(60)
font_media = get_font(40)
font_pequena = get_font(30)

COR_AZUL_ESCURO = (15, 35, 70)
COR_AZUL_CLARO = (50, 150, 255)
COR_BRANCO = (250, 250, 250)
COR_DOURADO = (255, 200, 50)
COR_BOTAO = (25, 60, 110)
COR_BOTAO_HOVER = (40, 90, 160)

try:
    som_acerto = pygame.mixer.Sound("sons/acerto.mp3")
    som_acerto.set_volume(0.6)
except: som_acerto = None

try:
    som_falha = pygame.mixer.Sound("sons/falha.mp3")
    som_falha.set_volume(0.4)
except: som_falha = None

volume_atual = 0.5
pygame.mixer.music.set_volume(volume_atual)

# ==========================================
# 3. VARIÁVEIS DE ESTADO E PLAYLIST
# ==========================================
PLAYLIST = [
    {"titulo": "Super Mario", "audio": "sons/super_mario.mp3", "mapa": "mapas/mapa_mario.json"},
    {"titulo": "Tetris Theme", "audio": "sons/Tetris.mp3", "mapa": "mapas/mapa_tetris.json"}
]
musica_selecionada = 0 

pontos = 0
notas_acertadas = 0
total_notas = 0
feedback_cor = (0, 0, 0)
HIT_ZONE_Y = HEIGHT - 120
TEMPO_VISIVEL = 2000
JANELA_ACERTO = 400

estado_jogo = "MENU_PRINCIPAL" 
MUSICA_ATUAL = []

# ==========================================
# 4. FUNÇÕES AUXILIARES
# ==========================================
def calcular_rank(taxa):
    if taxa >= 95: return "S", COR_DOURADO 
    if taxa >= 85: return "A", (50, 220, 100)   
    if taxa >= 70: return "B", COR_AZUL_CLARO 
    if taxa >= 50: return "C", (255, 140, 0) 
    return "D", (220, 50, 50)                 

def desenhar_botao(texto, rect, hover, preenchido=True):
    cor = COR_BOTAO_HOVER if hover else COR_BOTAO
    if preenchido:
        pygame.draw.rect(screen, cor, rect, border_radius=12)
    pygame.draw.rect(screen, COR_BRANCO, rect, width=2, border_radius=12)
    
    superficie_texto = font_media.render(texto, True, COR_BRANCO)
    screen.blit(superficie_texto, (rect.centerx - superficie_texto.get_width() // 2, rect.centery - superficie_texto.get_height() // 2))

def iniciar_partida():
    global MUSICA_ATUAL, pontos, notas_acertadas, total_notas, feedback_cor
    nivel = PLAYLIST[musica_selecionada]
    try:
        with open(nivel["mapa"], "r") as f:
            MUSICA_ATUAL = json.load(f)
        total_notas = len(MUSICA_ATUAL)
    except FileNotFoundError:
        print(f"Erro: Ficheiro '{nivel['mapa']}' não encontrado.")
        sys.exit()
    
    pygame.mixer.music.load(nivel["audio"])
    pygame.mixer.music.set_volume(volume_atual)
    
    pontos = 0
    notas_acertadas = 0
    feedback_cor = (0, 0, 0)
    for nota in MUSICA_ATUAL: nota["atingida"] = False
    pygame.mixer.music.play()

# ==========================================
# 5. LOOP PRINCIPAL
# ==========================================
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # BOTÕES 
    centro_x = WIDTH // 2
    largura_btn, altura_btn = 340, 70
    btn_jogar = pygame.Rect(centro_x - largura_btn // 2, HEIGHT // 2 - 60, largura_btn, altura_btn)
    btn_instrucoes = pygame.Rect(centro_x - largura_btn // 2, HEIGHT // 2 + 30, largura_btn, altura_btn)
    btn_config = pygame.Rect(centro_x - largura_btn // 2, HEIGHT // 2 + 120, largura_btn, altura_btn)
    largura_btn_voltar, altura_btn_voltar = 260, 60
    btn_voltar = pygame.Rect(centro_x - largura_btn_voltar // 2, HEIGHT - 100, largura_btn_voltar, altura_btn_voltar)
    
    btn_iniciar_musica = pygame.Rect(centro_x - largura_btn // 2, HEIGHT // 2 + 80, largura_btn, altura_btn)
    
    btn_vol_menos = pygame.Rect(centro_x - 120, HEIGHT // 2 - 20, 60, 60)
    btn_vol_mais = pygame.Rect(centro_x + 60, HEIGHT // 2 - 20, 60, 60)
    
    texto_musica = font_grande.render(PLAYLIST[musica_selecionada]["titulo"], True, COR_AZUL_CLARO)
    btn_esq = pygame.Rect(centro_x - texto_musica.get_width() // 2 - 80, HEIGHT // 2 - 50, 60, 60)
    btn_dir = pygame.Rect(centro_x + texto_musica.get_width() // 2 + 20, HEIGHT // 2 - 50, 60, 60)

    # --- PROCESSAMENTO DE EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if estado_jogo == "MENU_PRINCIPAL":
                if btn_jogar.collidepoint(mouse_pos): estado_jogo = "SELECAO_MUSICA"
                elif btn_instrucoes.collidepoint(mouse_pos): estado_jogo = "INSTRUCOES"
                elif btn_config.collidepoint(mouse_pos): estado_jogo = "CONFIGURACOES"
            
            elif estado_jogo == "SELECAO_MUSICA":
                if btn_iniciar_musica.collidepoint(mouse_pos): 
                    iniciar_partida()
                    estado_jogo = "JOGANDO"
                elif btn_voltar.collidepoint(mouse_pos): estado_jogo = "MENU_PRINCIPAL"
                elif btn_esq.collidepoint(mouse_pos): musica_selecionada = (musica_selecionada - 1) % len(PLAYLIST)
                elif btn_dir.collidepoint(mouse_pos): musica_selecionada = (musica_selecionada + 1) % len(PLAYLIST)
            
            elif estado_jogo == "INSTRUCOES":
                if btn_voltar.collidepoint(mouse_pos): estado_jogo = "MENU_PRINCIPAL"
                
            elif estado_jogo == "CONFIGURACOES":
                if btn_voltar.collidepoint(mouse_pos): estado_jogo = "MENU_PRINCIPAL"
                elif btn_vol_menos.collidepoint(mouse_pos): 
                    volume_atual = max(0.0, volume_atual - 0.1)
                    pygame.mixer.music.set_volume(volume_atual)
                elif btn_vol_mais.collidepoint(mouse_pos): 
                    volume_atual = min(1.0, volume_atual + 0.1)
                    pygame.mixer.music.set_volume(volume_atual)
                    
            elif estado_jogo == "RESULTADOS":
                if btn_voltar.collidepoint(mouse_pos): estado_jogo = "MENU_PRINCIPAL"

    # --- PROCESSAMENTO DA CÂMARA ---
    success, image = cap.read()
    if not success: continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    image_rgb_final = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.image.frombuffer(image_rgb_final.tobytes(), (WIDTH, HEIGHT), 'RGB')
    screen.blit(frame_surface, (0, 0))

    if estado_jogo != "JOGANDO":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220) 
        overlay.fill(COR_AZUL_ESCURO)
        screen.blit(overlay, (0, 0))

    # --- RENDERIZAÇÃO DE INTERFACES ---
    if estado_jogo == "MENU_PRINCIPAL":
        titulo = font_titulo.render("JUST LIBRAS", True, COR_BRANCO)
        screen.blit(titulo, (centro_x - titulo.get_width() // 2, HEIGHT // 4 - 30))
        subtitulo = font_pequena.render("Rhythm Edition", True, COR_AZUL_CLARO)
        screen.blit(subtitulo, (centro_x - subtitulo.get_width() // 2, HEIGHT // 4 + 60))

        desenhar_botao("JOGAR", btn_jogar, btn_jogar.collidepoint(mouse_pos))
        desenhar_botao("INSTRUÇÕES", btn_instrucoes, btn_instrucoes.collidepoint(mouse_pos))
        desenhar_botao("CONFIGURAÇÕES", btn_config, btn_config.collidepoint(mouse_pos))

    elif estado_jogo == "INSTRUCOES":
        titulo = font_grande.render("COMO JOGAR", True, COR_AZUL_CLARO)
        screen.blit(titulo, (centro_x - titulo.get_width() // 2, 80))
        
        instrucoes = [
            "1. Prepara as suas mãos em frente à câmara.",
            "2. Acompanha o ritmo da música escolhida.",
            "3. Faça o sinal das letras que caírem em LIBRAS.",
            "4. Acerta o sinal quando a letra cruzar a linha inferior!"
        ]
        
        y_inicial = HEIGHT // 2 - 100
        for i, linha in enumerate(instrucoes):
            texto = font_pequena.render(linha, True, COR_BRANCO)
            screen.blit(texto, (centro_x - texto.get_width() // 2, y_inicial + (i * 60)))
            
        desenhar_botao("VOLTAR", btn_voltar, btn_voltar.collidepoint(mouse_pos), preenchido=False)

    elif estado_jogo == "CONFIGURACOES":
        titulo = font_grande.render("CONFIGURAÇÕES", True, COR_AZUL_CLARO)
        screen.blit(titulo, (centro_x - titulo.get_width() // 2, 80))
        
        texto_vol = font_media.render(f"Volume: {int(volume_atual * 100)}%", True, COR_BRANCO)
        screen.blit(texto_vol, (centro_x - texto_vol.get_width() // 2, HEIGHT // 2 - 100))
        
        desenhar_botao("-", btn_vol_menos, btn_vol_menos.collidepoint(mouse_pos))
        desenhar_botao("+", btn_vol_mais, btn_vol_mais.collidepoint(mouse_pos))
        desenhar_botao("VOLTAR", btn_voltar, btn_voltar.collidepoint(mouse_pos), preenchido=False)

    elif estado_jogo == "SELECAO_MUSICA":
        titulo = font_grande.render("ESCOLHA A FAIXA", True, COR_BRANCO)
        screen.blit(titulo, (centro_x - titulo.get_width() // 2, HEIGHT // 4))
        
        screen.blit(texto_musica, (centro_x - texto_musica.get_width() // 2, HEIGHT // 2 - 40))
        desenhar_botao("<", btn_esq, btn_esq.collidepoint(mouse_pos), preenchido=False)
        desenhar_botao(">", btn_dir, btn_dir.collidepoint(mouse_pos), preenchido=False)
        
        desenhar_botao("INICIAR", btn_iniciar_musica, btn_iniciar_musica.collidepoint(mouse_pos))
        desenhar_botao("VOLTAR", btn_voltar, btn_voltar.collidepoint(mouse_pos), preenchido=False)

    elif estado_jogo == "JOGANDO":
        tempo_atual = pygame.mixer.music.get_pos()
        if not pygame.mixer.music.get_busy() and tempo_atual == -1:
            estado_jogo = "RESULTADOS"

        prediction_text = "A Aguardar Sinal..."
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

                    prediction_text = f"Sinal: {predicted_letter.upper()} ({confidence * 100:.0f}%)"

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
                                        if som_acerto: som_acerto.play()
                                        break
                                elif tempo_atual > nota["tempo_alvo"] + JANELA_ACERTO:
                                    nota["atingida"] = True
                                    feedback_cor = (255, 0, 0)
                                    if som_falha: som_falha.play()
                except Exception as e: pass

        if tempo_atual % 500 < 50: feedback_cor = (0, 0, 0)

        pygame.draw.line(screen, COR_DOURADO, (0, HIT_ZONE_Y), (WIDTH, HIT_ZONE_Y), 4)

        for nota in MUSICA_ATUAL:
            if not nota["atingida"]:
                tempo_falta = nota["tempo_alvo"] - tempo_atual
                if -JANELA_ACERTO < tempo_falta <= TEMPO_VISIVEL:
                    progresso = 1 - (tempo_falta / TEMPO_VISIVEL)
                    nota_y = int(HIT_ZONE_Y * progresso)
                    
                    rect_nota = pygame.Rect(centro_x - 30, nota_y - 30, 60, 60)
                    pygame.draw.rect(screen, COR_AZUL_CLARO, rect_nota, border_radius=30)
                    
                    texto_nota = font_media.render(nota["sinal"].upper(), True, COR_BRANCO)
                    screen.blit(texto_nota, (centro_x - texto_nota.get_width() // 2, nota_y - texto_nota.get_height() // 2))

        painel_ui = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        painel_ui.fill((15, 35, 70, 180))
        screen.blit(painel_ui, (0, 0))
        
        texto_pontos = font_media.render(f"PONTUAÇÃO: {pontos}", True, COR_DOURADO)
        screen.blit(texto_pontos, (WIDTH - texto_pontos.get_width() - 20, 25))
        
        texto_pred = font_pequena.render(prediction_text, True, COR_BRANCO)
        screen.blit(texto_pred, (20, 25))

        if feedback_cor != (0, 0, 0):
            pygame.draw.rect(screen, feedback_cor, (0, 0, WIDTH, HEIGHT), 8)

    elif estado_jogo == "RESULTADOS":
        titulo = font_grande.render("DESEMPENHO", True, COR_BRANCO)
        screen.blit(titulo, (centro_x - titulo.get_width() // 2, 60))

        taxa_acerto = (notas_acertadas / total_notas) * 100 if total_notas > 0 else 0
        rank_letra, rank_cor = calcular_rank(taxa_acerto)
        
        texto_rank = get_font(180).render(rank_letra, True, rank_cor)
        screen.blit(texto_rank, (centro_x - texto_rank.get_width() // 2, 140))

        texto_pontos = font_media.render(f"{pontos} PONTOS", True, COR_BRANCO)
        screen.blit(texto_pontos, (centro_x - texto_pontos.get_width() // 2, 340))
        
        texto_precisao = font_pequena.render(f"Precisão: {taxa_acerto:.1f}% ({notas_acertadas}/{total_notas})", True, COR_AZUL_CLARO)
        screen.blit(texto_precisao, (centro_x - texto_precisao.get_width() // 2, 390))

        desenhar_botao("MENU PRINCIPAL", btn_voltar, btn_voltar.collidepoint(mouse_pos))

    pygame.display.flip()
    clock.tick(30)

# ==========================================
# 6. ENCERRAMENTO
# ==========================================
hands.close()
cap.release()
pygame.quit()