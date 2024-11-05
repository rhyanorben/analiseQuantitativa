import sys  # Utilizada para manipular o ambiente
import pandas as pd  # Utilizado para dataframes
import matplotlib.pyplot as plt  # Utilizada para gráficos
from math import exp, factorial  # Utilizada para operações matemáticas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                             QLineEdit, QFileDialog, QMessageBox, QVBoxLayout, 
                             QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QTabWidget, QTextEdit, QCheckBox)  # Utilizado para a interface gráfica
from matplotlib.ticker import MaxNLocator  # Formatação dos gráficos

# Função para calcular a probabilidade de k gols usando a distribuição de Poisson
def poisson_probability(lambd, k):
    return (lambd ** k * exp(-lambd)) / factorial(k)  # Fórmula de Poisson para calcular a probabilidade

# Calcular a probabilidade de gols com base na média de gols
def calcular_poisson(media_gols):
    probabilities = []  # Array para armazenar as probabilidades de cada quantidade de gols
    for k in range(5):  # Calcula para 0, 1, 2, 3 e 4 gols
        probabilidade = poisson_probability(media_gols, k)  # Calcula probabilidade para k gols
        probabilities.append(probabilidade)  # Adiciona a probabilidade ao array
    return probabilities  # Retorna a lista de probabilidades

class AnalysisApp(QMainWindow):  # Classe da janela principal
    def __init__(self):  # Inicializa a classe
        super().__init__()  # Inicialização da superclasse QMainWindow
        self.setWindowTitle("Análise Under/Over Gols")  # Define o título da janela
        self.setGeometry(100, 100, 800, 600)  # Define o tamanho e posição da janela

        self.df = None  # Inicialização do DataFrame na classe
        self.rodada = None  # Inicialização da Rodada utilizada na classe
        self.teams = []  # Inicialização da lista de times

        layout = QVBoxLayout()  # Define um layout disposto em colunas verticais

        self.tab_widget = QTabWidget()  # Cria o QTabWidget para abas
        layout.addWidget(self.tab_widget)  # Adiciona o QTabWidget ao layout principal

        self.analysis_tab = QWidget()  # Cria a aba de análise
        self.info_tab = QWidget()  # Cria a aba de informações

        self.tab_widget.addTab(self.analysis_tab, "Análise")  # Adiciona a aba de análise ao QTabWidget
        self.tab_widget.addTab(self.info_tab, "Informação da Partida")  # Adiciona a aba de informação ao QTabWidget

        self.setup_analysis_tab()  # Configura os widgets da aba de análise
        self.setup_info_tab()  # Configura os widgets da aba de informação

        container = QWidget()  # Cria um container para o layout principal
        container.setLayout(layout)  # Define o layout do container
        self.setCentralWidget(container)  # Define o container como widget central da janela

    def setup_analysis_tab(self):  # Método para configurar a aba de análise
        layout = QVBoxLayout()  # Layout vertical para a aba de análise
        
        self.btn_load_file = QPushButton("Carregar Arquivo Excel", self)  # Botão para carregar arquivo
        self.btn_load_file.clicked.connect(self.load_file)  # Conecta o evento do botão ao método load_file
        layout.addWidget(self.btn_load_file)  # Adiciona o botão ao layout

        self.label_rodada = QLabel("Informe a rodada (entre 11 e 38):", self)  # Rótulo para rodada
        layout.addWidget(self.label_rodada)  # Adiciona o rótulo ao layout

        self.input_rodada = QLineEdit(self)  # Campo de texto para entrada da rodada
        layout.addWidget(self.input_rodada)  # Adiciona o campo ao layout

        self.label_team = QLabel("Selecione um time ou 'Todos' para ver todas as partidas:", self)  # Rótulo para seleção de time
        layout.addWidget(self.label_team)  # Adiciona o rótulo ao layout

        self.team_selector = QComboBox(self)  # Caixa de seleção para escolha de time
        self.team_selector.addItem("Todos")  # Adiciona a opção 'Todos' na lista
        layout.addWidget(self.team_selector)  # Adiciona a caixa de seleção ao layout

        # Caixa de seleção para marcar como rodada futura
        self.future_game_checkbox = QCheckBox("Rodada Futura", self)  # Caixa de seleção para indicar se é uma rodada futura
        self.future_game_checkbox.stateChanged.connect(self.toggle_location_selector)  # Conecta a mudança de estado ao método toggle_location_selector
        layout.addWidget(self.future_game_checkbox)  # Adiciona a caixa de seleção ao layout

        # Adiciona a caixa de seleção manual de "Casa" ou "Fora"
        self.label_location = QLabel("Selecione se o time jogará em casa ou fora:", self)  # Rótulo para o local do jogo
        layout.addWidget(self.label_location)  # Adiciona o rótulo ao layout

        self.location_selector = QComboBox(self)  # Caixa de seleção para escolher entre "Casa" e "Fora"
        self.location_selector.addItems(["Casa", "Fora"])  # Adiciona as opções "Casa" e "Fora"
        layout.addWidget(self.location_selector)  # Adiciona a caixa de seleção ao layout

        self.btn_analyze = QPushButton("Gerar Análise", self)  # Botão para gerar análise
        self.btn_analyze.clicked.connect(self.generate_analysis)  # Conecta o evento do botão ao método generate_analysis
        layout.addWidget(self.btn_analyze)  # Adiciona o botão ao layout

        self.table = QTableWidget(self)  # Tabela para exibir os dados
        layout.addWidget(self.table)  # Adiciona a tabela ao layout

        self.analysis_tab.setLayout(layout)  # Define o layout da aba de análise

        # Inicialmente, desabilita a seleção de "Casa" ou "Fora"
        self.location_selector.setEnabled(False)  # Desabilita a caixa de seleção para "Casa" ou "Fora"
        self.label_location.setEnabled(False)  # Desabilita o rótulo associado

    def toggle_location_selector(self):  # Método para habilitar/desabilitar a seleção de "Casa/Fora"
        # Habilita ou desabilita a seleção "Casa/Fora" dependendo da caixa de seleção de rodada futura
        is_future = self.future_game_checkbox.isChecked()  # Verifica se a caixa de seleção de rodada futura está marcada
        self.location_selector.setEnabled(is_future)  # Habilita a seleção de "Casa" ou "Fora" se for uma rodada futura
        self.label_location.setEnabled(is_future)  # Habilita o rótulo associado

    def setup_info_tab(self):  # Método para configurar a aba de informação
        layout = QVBoxLayout()  # Layout vertical para a aba de informação
        self.info_text = QTextEdit()  # Texto para exibir status de casa/fora
        self.info_text.setReadOnly(True)  # Define o campo como apenas leitura
        layout.addWidget(self.info_text)  # Adiciona o campo de texto ao layout
        self.info_tab.setLayout(layout)  # Define o layout da aba de informação

    def load_file(self):  # Função para carregar arquivo .xlsx
        options = QFileDialog.Options()  # Opções de configuração para a janela de diálogo
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo Excel", "", "Excel Files (*.xlsx)", options=options)  # Abre a janela para seleção de arquivo
        if file_name:  # Verifica se um arquivo foi selecionado
            try:
                self.df = pd.read_excel(file_name)  # Lê o arquivo Excel e armazena em self.df
                self.teams = sorted(set(self.df['Casa - Time'].unique()).union(set(self.df['Fora - Time'].unique())))  # Extrai todos os times únicos
                self.team_selector.addItems(self.teams)  # Adiciona os times à lista de seleção
                QMessageBox.information(self, "Sucesso", "Arquivo carregado com sucesso!")  # Exibe mensagem de sucesso
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar o arquivo: {e}")  # Exibe mensagem de erro

    def generate_analysis(self):  # Função para gerar análise
        if self.df is None:  # Verifica se o DataFrame está vazio
            QMessageBox.warning(self, "Aviso", "Por favor, carregue um arquivo primeiro.")  # Exibe aviso
            return

        try:
            self.rodada = int(self.input_rodada.text())  # Converte a rodada para inteiro
            if self.rodada < 11 or self.rodada > 38:  # Verifica se a rodada está entre 11 e 38
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Erro", "Rodada inválida. Insira um número entre 11 e 38.")  # Exibe erro de rodada inválida
            return

        selected_team = self.team_selector.currentText()  # Obtém o time selecionado

        # Verifica se é uma rodada futura
        is_future = self.future_game_checkbox.isChecked()  # Verifica se a rodada é marcada como futura

        if selected_team == "Todos":
            df_filtered = self.df[self.df['Partida'] == self.rodada]  # Filtra para mostrar todas as partidas da rodada
            self.info_text.setText("Exibindo todas as partidas da rodada.")  # Exibe mensagem na aba de informação
        elif is_future:
            # Usa seleção manual de "Casa" ou "Fora" para rodadas futuras
            location = self.location_selector.currentText()  # Obtém a seleção manual "Casa" ou "Fora"
            self.info_text.setText(f"{selected_team} jogará '{location}' na rodada {self.rodada} (configurado manualmente).")
            home_or_away = location
            df_filtered = self.df[(self.df[f"{home_or_away} - Time"] == selected_team) & (self.df['Partida'] < self.rodada)].tail(5)  # Filtra as últimas 5 partidas com base na seleção manual
        else:
            rodada_atual = self.df[self.df['Partida'] == self.rodada]  # Filtra para a rodada especificada
            if not rodada_atual[rodada_atual['Casa - Time'] == selected_team].empty:
                df_filtered = self.df[(self.df['Casa - Time'] == selected_team) & (self.df['Partida'] < self.rodada)].tail(5)
                home_or_away = 'Casa'
                self.info_text.setText(f"{selected_team} jogará em casa na rodada {self.rodada}.")
            elif not rodada_atual[rodada_atual['Fora - Time'] == selected_team].empty:
                df_filtered = self.df[(self.df['Fora - Time'] == selected_team) & (self.df['Partida'] < self.rodada)].tail(5)
                home_or_away = 'Fora'
                self.info_text.setText(f"{selected_team} jogará fora na rodada {self.rodada}.")
            else:
                self.info_text.setText("Time não encontrado na rodada especificada.")
                return

        if df_filtered.empty:
            QMessageBox.information(self, "Sem Dados", "Nenhuma partida encontrada para os critérios especificados.")  # Exibe mensagem se não há partidas
            return

        self.display_table(df_filtered)  # Exibe a tabela com os dados filtrados

        if home_or_away == 'Casa':
            adversary_goals = df_filtered['Fora - Gols']  # Define os gols do adversário para partidas em casa
        else:
            adversary_goals = df_filtered['Casa - Gols']  # Define os gols do adversário para partidas fora

        adversary_goals = adversary_goals.dropna()  # Remove valores nulos
        if adversary_goals.empty:
            QMessageBox.critical(self, "Erro", "Não há dados suficientes para calcular a média de gols sofridos pelo adversário.")  # Exibe erro se não há dados suficientes
            return

        media_gols = adversary_goals.mean()  # Calcula a média de gols sofridos
        self.plot_goals_distribution(df_filtered, selected_team, home_or_away)  # Gera gráfico de distribuição de gols
        self.plot_poisson_distribution(selected_team, media_gols)  # Gera gráfico de Poisson

    def plot_goals_distribution(self, df_filtered, selected_team, home_or_away):
        plt.figure(figsize=(10, 5))
        bar_width = 0.6

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
        plt.grid(axis='y', linestyle='--', alpha=0.5)
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
