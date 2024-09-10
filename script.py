import sys #Utilizada para manipular o ambiente
import pandas as pd #Utilizado para os dataframes
import matplotlib.pyplot as plt #Utilizada pra gráficos
from math import exp, factorial #Utilizada para operações matemáticas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                             QLineEdit, QFileDialog, QMessageBox, QVBoxLayout, 
                             QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox) #Utilizado para a interface
from matplotlib.ticker import MaxNLocator #Formatação dos gráficos

# Função para calcular a probabilidade de k gols usando a distribuição de Poisson
def poisson_probability(lambd, k):
    return (lambd ** k * exp(-lambd)) / factorial(k)
    #Lambd = Média de ocorrências no período (no intervalo de 5 jogos, nesse caso)
    #k = Número de gols que o time que será calculado a probabilidade de ocorrer.

# Calcular a probabilidade de gols com base na média de gols
def calcular_poisson(media_gols):
    probabilities = [] #Array para armazenar as probabilidades por qtd de gols
    for k in range(5):  # Calcula para 0, 1, 2, 3, 4 gols
        probabilidade = poisson_probability(media_gols, k) #Utiliza a média de gols nos últimos jogos e k para calcular para 0, 1, 2, 3 e 4 gols 
        probabilities.append(probabilidade) #Adiciona a probabilidade na array de probabilidades criada anteriormente
    return probabilities

class AnalysisApp(QMainWindow): #Classe de criação da janela principal da interface
    def __init__(self): #Dá inicio a classe
        super().__init__() #Utilizado super().__init__() para não precisar dar nenhum parâmetro de inicio a classe
        self.setWindowTitle("Análise Under/Over Gols") #Título da janela do app
        self.setGeometry(100, 100, 800, 600) #Tamanho da interface

        self.df = None #Inicialização do DataFrame na classe
        self.rodada = None #Inicialização da Rodada utilizada na classe
        self.teams = [] #Time(s) a ser analisado

        layout = QVBoxLayout() #Define um layout disposto em colunas vertiicas

        self.btn_load_file = QPushButton("Carregar Arquivo Excel", self) #Botão para adicionar arquivo Excel
        self.btn_load_file.clicked.connect(self.load_file) #Conecta o evento de clique de botão ao método de load_file
        layout.addWidget(self.btn_load_file) #Widget para aparecer o botão na interface

        self.label_rodada = QLabel("Informe a rodada (entre 11 e 38):", self) #Label para informar a rodada solicitada
        layout.addWidget(self.label_rodada) #Widget para aparecer na interface

        self.input_rodada = QLineEdit(self) #Função para editar a rodada solicitada análise
        layout.addWidget(self.input_rodada) #Widget para aparecer na tela

        self.label_team = QLabel("Selecione um time ou 'Todos' para ver todas as partidas:", self) #Cria um rótulo para guiar o usuário sobre o propósito do campo de seleção.
        layout.addWidget(self.label_team) #Widget para mostrar na tela

        self.team_selector = QComboBox(self) #Cria uma caixa de seleção (dropdown) para que o usuário escolha uma opção.
        self.team_selector.addItem("Todos") #Adiciona a opção "Todos" à lista de opções da caixa de seleção.
        layout.addWidget(self.team_selector) #Coloca os widgets (rótulo e caixa de seleção) na interface gráfica.

        self.btn_analyze = QPushButton("Gerar Análise", self) #Botão para gerar análise
        self.btn_analyze.clicked.connect(self.generate_analysis) #Conecta, ao clicar, o botão a função generate_analysis
        layout.addWidget(self.btn_analyze) #Adiciona a tela o Widget do botão

        self.table = QTableWidget(self) #Cria uma tabela onde serão exibidos os dados (número de colunas e linhas será definido posteriormente).
        layout.addWidget(self.table) #Adiciona a tabela a interface, permitindo que ela seja exibida

        container = QWidget() #Cria um container para os widgets
        container.setLayout(layout) #Seta o layout criado anteriormente ao container
        self.setCentralWidget(container) #Centraliza o container, com todos os widgets, na janela principal

    def load_file(self): #Função para carregar arquivo .xlsx
        options = QFileDialog.Options() #Cria uma variável options que armazena as opções de configuração para a janela de diálogo de seleção de arquivos.
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo Excel", "", "Excel Files (*.xlsx)", options=options) #Abre uma janela para o usuário selecionar um arquivo Excel (.xlsx). O caminho completo do arquivo selecionado é armazenado na variável file_name. O segundo valor retornado (que não é necessário) é descartado usando _.
        if file_name: #Verifica se o usuário selecionou um arquivo. Se o caminho do arquivo estiver vazio (o usuário cancelou a operação), o bloco de código dentro do if não será executado.
            try:
                self.df = pd.read_excel(file_name) #Lê o arquivo Excel selecionado e armazena os dados em um DataFrame do pandas, que é acessível através do atributo self.df. Isso carrega o conteúdo do arquivo para a aplicação.
                self.teams = sorted(set(self.df['Casa - Time'].unique()).union(set(self.df['Fora - Time'].unique()))) #Extrai todos os times de forma única que estão no arquivo, na coluna 'Casa - Time' e 'Fora - Time'
                self.team_selector.addItems(self.teams) #Adiciona os times ao team_selector do layout principal
                QMessageBox.information(self, "Sucesso", "Arquivo carregado com sucesso!") #Ao concluir o carregamento do arquivo, apresenta a mensagem de sucesso.
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar o arquivo: {e}") #Caso ocorra algum erro no Try/Except, apresenta o erro.

    def generate_analysis(self): #Função para gerar análise
        if self.df is None: #Se o DataFrame estiver vazio, solicitá que importe um arquivo primeiro.
            QMessageBox.warning(self, "Aviso", "Por favor, carregue um arquivo primeiro.")
            return

        try:
            self.rodada = int(self.input_rodada.text()) #Adiciona a rodada a classe AnalysisApp criada anteriormente
            if self.rodada < 11 or self.rodada > 38: #Verifica se a rodada seleciona atende os requisitos da 11 a 38 
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Erro", "Rodada inválida. Insira um número entre 11 e 38.") #Apresenta um erro caso não atenda os requisitos.
            return

        selected_team = self.team_selector.currentText() #Adiciona o time selecionado a classe AnalysisApp criada anteriomente.

        if selected_team == "Todos":
            df_filtered = self.df[self.df['Partida'] == self.rodada]
        else:
            rodada_atual = self.df[self.df['Partida'] == self.rodada]
            if rodada_atual.empty:
                QMessageBox.information(self, "Sem Dados", "Nenhuma partida encontrada para a rodada especificada.")
                return

            if not rodada_atual[rodada_atual['Casa - Time'] == selected_team].empty:
                df_filtered = self.df[(self.df['Casa - Time'] == selected_team) & (self.df['Partida'] < self.rodada)].tail(5)
                home_or_away = 'Casa'
            elif not rodada_atual[rodada_atual['Fora - Time'] == selected_team].empty:
                df_filtered = self.df[(self.df['Fora - Time'] == selected_team) & (self.df['Partida'] < self.rodada)].tail(5)
                home_or_away = 'Fora'
            else:
                QMessageBox.information(self, "Sem Dados", "Time não encontrado na rodada especificada.")
                return

        if df_filtered.empty:
            QMessageBox.information(self, "Sem Dados", "Nenhuma partida encontrada para os critérios especificados.")
            return

        self.display_table(df_filtered)

        # Cálculo da média de gols sofridos pelo adversário
        if home_or_away == 'Casa':
            adversary_goals = df_filtered['Fora - Gols']
        else:
            adversary_goals = df_filtered['Casa - Gols']

        adversary_goals = adversary_goals.dropna()
        if adversary_goals.empty:
            QMessageBox.critical(self, "Erro", "Não há dados suficientes para calcular a média de gols sofridos pelo adversário.")
            return

        media_gols = adversary_goals.mean()

        #Geração Gráfico de gols marcados pelo time analisado
        self.plot_goals_distribution(df_filtered, selected_team, home_or_away)
        # Geração do gráfico de Poisson
        self.plot_poisson_distribution(selected_team, media_gols)

    def plot_goals_distribution(self, df_filtered, selected_team, home_or_away):
        plt.figure(figsize=(10, 5))
        bar_width = 0.6  # Define a largura das barras para criar mais espaçamento

        if home_or_away == 'Casa':
            df_filtered['Casa - Gols'].plot(kind='hist', bins=range(0, df_filtered['Casa - Gols'].max() + 2), 
                                            color='skyblue', alpha=0.7, width=bar_width)
            plt.xlabel("Gols Marcados em Casa")
            plt.title(f"Distribuição de Gols em Casa para {selected_team} nas Últimas 5 Partidas")
        else:
            df_filtered['Fora - Gols'].plot(kind='hist', bins=range(0, df_filtered['Fora - Gols'].max() + 2), 
                                            color='salmon', alpha=0.7, width=bar_width)
            plt.xlabel("Gols Marcados Fora")
            plt.title(f"Distribuição de Gols Fora para {selected_team} nas Últimas 5 Partidas")

        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.ylabel("Frequência (Número de Partidas)")
        plt.grid(axis='y', linestyle='--', alpha=0.5)  # Adiciona linhas de grade leves para melhorar a visualização
        plt.show()

    def plot_poisson_distribution(self, selected_team, media_gols):
        try:
            probabilities = calcular_poisson(media_gols)

            def my_autopct(pct):
                return f'{pct:.1f}%'

            plt.figure(figsize=(10, 5))
            plt.pie(probabilities, 
                    labels=[f'{i} gols' for i, _ in enumerate(probabilities)],
                    autopct=my_autopct,
                    startangle=140, 
                    colors=plt.cm.Paired(range(len(probabilities))))
            plt.title(f"Distribuição de Probabilidades de Gols para {selected_team} (Poisson)")
            plt.show()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar gráfico de distribuição de Poisson: {e}")

    def display_table(self, df):
        df_filtered = df[['Partida', 'Casa - Time', 'Fora - Time', 'Casa - Gols', 'Fora - Gols']]
        self.table.setRowCount(df_filtered.shape[0])
        self.table.setColumnCount(df_filtered.shape[1])
        self.table.setHorizontalHeaderLabels(df_filtered.columns)

        for i in range(df_filtered.shape[0]):
            for j in range(df_filtered.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(df_filtered.iat[i, j])))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalysisApp()
    window.show()
    sys.exit(app.exec_())
