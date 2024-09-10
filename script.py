import sys
import pandas as pd
import matplotlib.pyplot as plt
from math import exp, factorial
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                             QLineEdit, QFileDialog, QMessageBox, QVBoxLayout, 
                             QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PyQt5.QtCore import Qt
from matplotlib.ticker import MaxNLocator

# Função para calcular a probabilidade de k gols usando a distribuição de Poisson
def poisson_probability(lambd, k):
    return (lambd ** k * exp(-lambd)) / factorial(k)

# Calcular a probabilidade de gols com base na média de gols
def calcular_poisson(media_gols):
    probabilities = []
    for k in range(5):  # Calcula para 0, 1, 2, 3, 4 gols
        probabilidade = poisson_probability(media_gols, k)
        probabilities.append(probabilidade)
    return probabilities

class AnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análise Quantitativa de Rodadas")
        self.setGeometry(100, 100, 800, 600)

        self.df = None
        self.rodada = None
        self.teams = []

        layout = QVBoxLayout()

        self.btn_load_file = QPushButton("Carregar Arquivo Excel", self)
        self.btn_load_file.clicked.connect(self.load_file)
        layout.addWidget(self.btn_load_file)

        self.label_rodada = QLabel("Informe a rodada (entre 11 e 38):", self)
        layout.addWidget(self.label_rodada)

        self.input_rodada = QLineEdit(self)
        layout.addWidget(self.input_rodada)

        self.label_team = QLabel("Selecione um time ou 'Todos' para ver todas as partidas:", self)
        layout.addWidget(self.label_team)

        self.team_selector = QComboBox(self)
        self.team_selector.addItem("Todos")
        layout.addWidget(self.team_selector)

        self.btn_analyze = QPushButton("Gerar Análise", self)
        self.btn_analyze.clicked.connect(self.generate_analysis)
        layout.addWidget(self.btn_analyze)

        self.table = QTableWidget(self)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo Excel", "", "Excel Files (*.xlsx)", options=options)
        if file_name:
            try:
                self.df = pd.read_excel(file_name)
                self.teams = sorted(set(self.df['Casa - Time'].unique()).union(set(self.df['Fora - Time'].unique())))
                self.team_selector.addItems(self.teams)
                QMessageBox.information(self, "Sucesso", "Arquivo carregado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar o arquivo: {e}")

    def generate_analysis(self):
        if self.df is None:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue um arquivo primeiro.")
            return

        try:
            self.rodada = int(self.input_rodada.text())
            if self.rodada < 11 or self.rodada > 38:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Erro", "Rodada inválida. Insira um número entre 11 e 38.")
            return

        selected_team = self.team_selector.currentText()

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
            plt.figure(figsize=(10, 5))
            plt.pie(probabilities, labels=[f'{i} gols: {p:.1%}' for i, p in enumerate(probabilities)],
                    autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired(range(len(probabilities))))
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
