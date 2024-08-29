# Tratamento de Dados - Um exemplo de projeto Python
# Copyright (C) 2024 Vinicius Patriarca Miranda Miguel

# Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral GNU como publicada pela Free Software
# Foundation, tanto a versão 3 da Licença, como (a seu critério) qualquer versão posterior.

# Este programa é distribuído na esperança de que seja útil,
# mas SEM NENHUMA GARANTIA; sem mesmo a garantia implícita de
# COMERCIABILIDADE ou ADEQUAÇÃO A UM DETERMINADO FIM. Veja a
# Licença Pública Geral GNU para mais detalhes.

# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_csv(simulacao, telhado, file_name, output_dir):
    # Constrói o caminho completo do arquivo de entrada
    input_file = f"simulacao{simulacao}/telhado{telhado}/csv/{file_name}"

    # Lê o arquivo CSV
    data = pd.read_csv(input_file)

    # Verifica se há pelo menos duas colunas
    if data.shape[1] < 2:
        print(f"O arquivo {input_file} deve ter pelo menos duas colunas.")
        return

    # Converte a coluna de data para datetime, considerando apenas hora e minuto
    data["Hora_Minuto"] = pd.to_datetime(data["data"], format="%H:%M")

    # Ajusta o primeiro tempo para ser 0
    min_time = data["Hora_Minuto"].min()
    data["Hora_Minuto"] = (data["Hora_Minuto"] - min_time).dt.total_seconds() / 3600

    # A segunda coluna será a coluna de valores
    value_column_name = data.columns[1]
    data[value_column_name] = pd.to_numeric(data[value_column_name], errors="coerce")

    # Remove linhas com valores inválidos na segunda coluna
    data.dropna(subset=[value_column_name], inplace=True)

    # Ordena os dados pela coluna 'Hora_Minuto'
    data.sort_values(by="Hora_Minuto", inplace=True)

    # Extrai o nome do arquivo para usar como rótulo do eixo y
    y_label = os.path.splitext(file_name)[0]  # Remove a extensão .csv

    # Plota os dados
    plt.figure(figsize=(20, 5))
    plt.plot(data["Hora_Minuto"], data[value_column_name], marker="o")

    # Define os rótulos do eixo x como HH:MM a cada 10 minutos
    max_time = data["Hora_Minuto"].max()
    if pd.isna(max_time):
        print(f"Não foi possível determinar o máximo tempo válido em {file_name}.")
        return

    max_time_minutes = max_time * 60  # Converte para minutos
    interval = 10  # Intervalo de 10 minutos para os ticks
    ticks = range(
        0, int(max_time_minutes) + interval, interval
    )  # Cria ticks a cada 10 minutos
    x_labels = [f"{tick//60:02d}:{tick%60:02d}" for tick in ticks]
    ticks_hours = [
        tick / 60 for tick in ticks
    ]  # Converte ticks de volta para horas decimais

    plt.xticks(ticks=ticks_hours, labels=x_labels, rotation=45)

    plt.xlabel("Tempo (Horas:Minutos)")
    plt.ylabel(y_label)  # Usa o nome do arquivo como rótulo do eixo y
    plt.title(f"Gráfico de Hora vs {y_label}")
    plt.grid(True)
    plt.tight_layout()

    # Ajusta a distância entre as marcações no eixo x
    ax = plt.gca()
    ax.set_xticks(ticks_hours)

    # Salva o gráfico no caminho de saída
    output_path = os.path.join(output_dir, file_name.replace(".csv", ".png"))
    plt.savefig(output_path)
    plt.close()

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Gera gráficos a partir de arquivos CSV"
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )
    parser.add_argument(
        "--telhado", "-t", type=str, required=True, help="Número do telhado"
    )

    args = parser.parse_args()

    input_dir = f"simulacao{args.simulacao}/telhado{args.telhado}/csv/"
    output_dir = f"simulacao{args.simulacao}/telhado{args.telhado}/graficos"

    # Certifica-se de que o diretório de saída existe
    os.makedirs(output_dir, exist_ok=True)

    # Processa todos os arquivos CSV na pasta de entrada
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            plot_csv(args.simulacao, args.telhado, file_name, output_dir)
            print(f'Gráfico salvo em {output_dir}/{file_name.replace(".csv", ".png")}')


if __name__ == "__main__":
    main()
