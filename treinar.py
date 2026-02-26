import cv2
import mediapipe as mp
import csv  
import os   #verificar se o arquivo existe
import numpy as np

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

#Configurações para Coleta de Dados 
DATA_FILE = 'libras_data.csv'

# Letras que queremos coletar (notas musicais)
LETTERS_TO_COLLECT = ['d', 'r', 'm', 'f', 's', 'l', 'c']

# Criar o cabeçalho do arquivo CSV se ele não existir
num_landmarks = 21
# Colunas: 'label' + 'x0', 'y0', 'z0', 'x1', 'y1', 'z1', ...
header = ['label']
for i in range(num_landmarks):
    header += [f'x{i}', f'y{i}', f'z{i}']

# 'a' = append (adicionar ao final do arquivo)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        print(f"Arquivo {DATA_FILE} criado com cabeçalho.")


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

print('Iniciando captura... Pressione as teclas (d, r, m, f, s, l, c) para salvar dados.')
print('Pressione "q" para sair.')

last_saved_letter = ""
while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    image_rgb.flags.writeable = False
    results = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Captura da tecla pressionada
    key = cv2.waitKey(5) & 0xFF

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image_bgr,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS)
            
            #LÓGICA DE COLETA DE DADOS 
            
            #Checar se a tecla pressionada é uma das letras
            if key != 255 and chr(key) in LETTERS_TO_COLLECT:
                label = chr(key)
                landmarks = hand_landmarks.landmark
                data_row = [label]
                flat_landmarks = []
                for lm in landmarks:
                    flat_landmarks.extend([lm.x, lm.y, lm.z])
                
                data_row.extend(flat_landmarks)
                
                #Salvar a linha no arquivo CSV
                with open(DATA_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(data_row)
                    
                print(f"Coletado! Amostra para a letra: {label}")
                last_saved_letter = label

    #feedback visual
    cv2.putText(image_bgr, f"Pressione (d,r,m,f,s,l,c) para salvar.", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(image_bgr, f"Ultima Salva: {last_saved_letter.upper()}", 
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Coletor de Dados - Pressione "q" para sair', image_bgr)

    # Sair do loop
    if key == ord('q'):
        break

# Limpeza
hands.close()
cap.release()
cv2.destroyAllWindows()
print('Coleta finalizada.')
print(f"Dados salvos em: {DATA_FILE}")