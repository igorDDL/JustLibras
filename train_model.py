import pandas as pd
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import StandardScaler 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.metrics import accuracy_score 


DATA_FILE = 'libras_data.csv'

# Ler o arquivo CSV para um DataFrame do pandas
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    print(f"Erro: Arquivo {DATA_FILE} não encontrado.")
    print("Por favor, execute o script de coleta de dados primeiro.")
    exit()

if df.empty:
    print(f"Erro: O arquivo {DATA_FILE} está vazio.")
    print("Por favor, colete mais dados.")
    exit()

print(f"Dados carregados! Total de {len(df)} amostras.")
print("Contagem de amostras por letra:")
print(df['label'].value_counts())

X = df.drop('label', axis=1) 

y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nDados divididos: {len(X_train)} para treino, {len(X_test)} para teste.")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nIniciando treinamento do modelo (RandomForestClassifier)...")

model = RandomForestClassifier(n_estimators=100, random_state=42)

#treinamento
model.fit(X_train_scaled, y_train)

print("Treinamento concluído!")

#Testar o Modelo
y_pred = model.predict(X_test_scaled)

#Calcular a precisão
accuracy = accuracy_score(y_test, y_pred)

print("\n--- Avaliação do Modelo ---")
print(f"Acurácia nos dados de teste: {accuracy * 100:.2f}%")

if accuracy < 0.8:
    print("Acurácia está um pouco baixa. Considere coletar mais dados!")
elif accuracy < 0.95:
    print("Bom trabalho! O modelo está aprendendo bem.")
else:
    print("Excelente! Acurácia muito alta. O modelo está ótimo!")

#Salvar o Modelo Treinado
model_data = {
    'model': model,
    'scaler': scaler
}

MODEL_FILE = 'libras_model.pkl'

# 'wb' = write binary
with open(MODEL_FILE, 'wb') as f:
    pickle.dump(model_data, f)

print(f"\nModelo e Scaler salvos com sucesso em: {MODEL_FILE}")
print("Próximo passo: Integrar este modelo no seu script da webcam!")