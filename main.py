import cv2
import mediapipe as mp
import pickle
import numpy as np

MODEL_FILE = 'libras_model.pkl'

try:
    with open(MODEL_FILE, 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    scaler = model_data['scaler']
    print(f"Modelo '{MODEL_FILE}' carregado com sucesso!")

except FileNotFoundError:
    print(f"Erro: Arquivo do modelo '{MODEL_FILE}' não encontrado.")
    print("Por favor, execute o script 'train_model.py' primeiro.")
    exit()
except Exception as e:
    print(f"Erro ao carregar o modelo: {e}")
    exit()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

MUSICA_ATUAL = ['d', 'r', 'm', 'f', 's', 'l', 'c', 's', 'f', 'm', 'r', 'd']
indice_nota_atual = 0
pontos = 0
feedback_cor = (0, 0, 0)
contador_acerto = 0
TEMPO_PARA_ACERTAR = 10

print('Iniciando predição... Pressione "q" para sair.')

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image_rgb.flags.writeable = False
    results = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    prediction_text = ""

    if indice_nota_atual < len(MUSICA_ATUAL):
        letra_alvo = MUSICA_ATUAL[indice_nota_atual]
    else:
        letra_alvo = "FIM!"

    cv2.putText(image_bgr, f"FAÇA: {letra_alvo.upper()}",
                (int(image_bgr.shape[1] / 2) - 100, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

    cv2.putText(image_bgr, f"Pontos: {pontos}",
                (image_bgr.shape[1] - 200, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image_bgr,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS)
            try:
                landmarks = hand_landmarks.landmark
                flat_landmarks = []
                for lm in landmarks:
                    flat_landmarks.extend([lm.x, lm.y, lm.z])

                data_row = np.array([flat_landmarks])

                data_row_scaled = scaler.transform(data_row)

                prediction = model.predict(data_row_scaled)

                predicted_letter = prediction[0]

                confidence = np.max(model.predict_proba(data_row_scaled))

                prediction_text = f"Pred: {predicted_letter.upper()} ({confidence * 100:.0f}%)"

                if predicted_letter == letra_alvo and confidence > 0.9:
                    contador_acerto += 1
                    feedback_cor = (0, 255, 0)

                    if contador_acerto >= TEMPO_PARA_ACERTAR:
                        pontos += 10
                        indice_nota_atual += 1
                        contador_acerto = 0
                else:
                    contador_acerto = 0
                    feedback_cor = (0, 0, 255)

            except Exception as e:
                contador_acerto = 0
                feedback_cor = (0, 0, 0)
                pass
    else:
        contador_acerto = 0
        feedback_cor = (0, 0, 0)

    cv2.putText(image_bgr, prediction_text,
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(image_bgr, 'Pressione "q" para sair',
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.rectangle(image_bgr, (0, 0), (image_bgr.shape[1], image_bgr.shape[0]),
                  feedback_cor, 10)

    cv2.imshow('Just Libras - IA', image_bgr)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
print('Sessão finalizada.')