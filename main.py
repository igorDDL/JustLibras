import cv2
import mediapipe as mp
import pickle  #carregar o modelo treinado
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

#Configurações do MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

#Inicializar a Webcam 
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera.")
    exit()

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
                
                prediction_text = f"Letra: {predicted_letter.upper()} ({confidence * 100:.1f}%)"
            
            except Exception as e:
                # print(f"Erro na predição: {e}") # Descomente para debug
                pass

    cv2.putText(image_bgr, prediction_text, 
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                1.5, (0, 255, 0), 3, cv2.LINE_AA)
    
    cv2.putText(image_bgr, 'Pressione "q" para sair', 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('Just Libras - IA', image_bgr)

    #Sair do loop
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

#Limpeza
hands.close()
cap.release()
cv2.destroyAllWindows()
print('Sessão finalizada.')