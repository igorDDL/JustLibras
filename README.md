# 🤟 Just Libras: Rhythm Edition

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Visão_Computacional-red?style=for-the-badge&logo=opencv)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-Machine_Learning-orange?style=for-the-badge&logo=scikit-learn)
![Pygame](https://img.shields.io/badge/Pygame-Game_Engine-green?style=for-the-badge)

## 📌 Sobre o Projeto
**Just Libras** é uma aplicação interativa que une o conceito de jogos de ritmo (como *Guitar Hero* ou *Just Dance*) com o reconhecimento de imagem em tempo real. O objetivo do projeto é gamificar o aprendizado e a prática da Língua Brasileira de Sinais (Libras). 

Em vez de pressionar botões, o jogador utiliza a webcam para realizar os sinais correspondentes às letras que caem na tela no ritmo da música. O sistema captura os *landmarks* (pontos de articulação) das mãos e utiliza um modelo de Machine Learning para classificar o sinal instantaneamente, garantindo uma jogabilidade fluida e responsiva.

---

## 🚀 Arquitetura e Tecnologias

O projeto foi construído utilizando uma stack focada em processamento de dados e visão computacional:

* **MediaPipe (Google):** Extração de 21 marcos (landmarks) 3D da mão do usuário em tempo real.
* **OpenCV:** Captura e processamento primário dos frames da webcam.
* **Scikit-Learn:** Criação do pipeline de Machine Learning (`StandardScaler` + `RandomForestClassifier`) para classificar as coordenadas extraídas em letras do alfabeto.
* **Pygame:** Gerenciamento do loop principal do jogo, renderização da Interface Gráfica (UI), sistema de estados (Menu/Jogo/Resultados) e engine de áudio.
* **Librosa:** Processamento digital de sinais (DSP) para detecção automatizada de *beats* e BPM dos arquivos de áudio.

---

## 📂 Estrutura de Arquivos do Projeto

A lógica da aplicação está dividida em módulos independentes para facilitar a manutenção e o pipeline de dados:

* `main.py`: O núcleo do jogo. Integra a inferência do modelo, a captura de vídeo e a engine do Pygame.
* `treinar.py`: Ferramenta de coleta de dados. Extrai coordenadas da mão via webcam e salva em um dataset CSV.
* `train_model.py`: Pipeline de Machine Learning. Carrega o CSV, divide em bases de treino/teste, treina o modelo Random Forest e exporta o binário (`.pkl`).
* `gerador_automatico.py`: Script de automação que analisa um `.mp3` e gera um *beatmap* jogável em JSON baseado nas batidas da música.
* `mapeador.py`: Ferramenta de *Level Design* manual para gravação de *beatmaps* através de inputs de teclado.

---
