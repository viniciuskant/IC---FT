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


def plot_combined_csv(simulacao, telhado1, telhado2, file_name, output_dir):
    # Constrói o caminho completo dos arquivos de entrada de ambos telhados
    input_file1 = f"simulacao{simulacao}/{telhado1}/csv/{file_name}"
    input_file2 = f"simulacao{simulacao}/{telhado2}/csv/{file_name}"

    # Verifica se ambos os arquivos existem
    if not os.path.isfile(input_file1):
        print(f"Arquivo {input_file1} não encontrado.")
        return
    if not os.path.isfile(input_file2):
        print(f"Arquivo {input_file2} não encontrado.")
        return

    # Lê os arquivos CSV de ambos os telhados
    data1 = pd.read_csv(input_file1)
    data2 = pd.read_csv(input_file2)

    # Verifica se há pelo menos duas colunas em ambos os dataframes
    if data1.shape[1] < 2 or data2.shape[1] < 2:
        print(
            f"Os arquivos {input_file1} e {input_file2} devem ter pelo menos duas colunas."
        )
        return

    # Converte a coluna de data para datetime, considerando apenas hora e minuto, para ambos os dataframes
    data1["Hora_Minuto"] = pd.to_datetime(data1["data"], format="%H:%M")
    data2["Hora_Minuto"] = pd.to_datetime(data2["data"], format="%H:%M")

    # Ajusta o primeiro tempo para ser 0, para ambos os dataframes
    min_time1 = data1["Hora_Minuto"].min()
    data1["Hora_Minuto"] = (data1["Hora_Minuto"] - min_time1).dt.total_seconds() / 3600

    min_time2 = data2["Hora_Minuto"].min()
    data2["Hora_Minuto"] = (data2["Hora_Minuto"] - min_time2).dt.total_seconds() / 3600

    # A segunda coluna será a coluna de valores, para ambos os dataframes
    value_column_name1 = data1.columns[1]
    data1[value_column_name1] = pd.to_numeric(
        data1[value_column_name1], errors="coerce"
    )

    value_column_name2 = data2.columns[1]
    data2[value_column_name2] = pd.to_numeric(
        data2[value_column_name2], errors="coerce"
    )

    # Remove linhas com valores inválidos na segunda coluna, para ambos os dataframes
    data1.dropna(subset=[value_column_name1], inplace=True)
    data2.dropna(subset=[value_column_name2], inplace=True)

    # Ordena os dados pela coluna 'Hora_Minuto', para ambos os dataframes
    data1.sort_values(by="Hora_Minuto", inplace=True)
    data2.sort_values(by="Hora_Minuto", inplace=True)

    # Extrai o nome do arquivo para usar como rótulo do eixo y
    y_label = os.path.splitext(file_name)[0]  # Remove a extensão .csv

    # Plota os dados combinados
    plt.figure(figsize=(20, 5))
    plt.plot(
        data1["Hora_Minuto"],
        data1[value_column_name1],
        marker="o",
        label=f"Telhado {telhado1}",
    )
    plt.plot(
        data2["Hora_Minuto"],
        data2[value_column_name2],
        marker="o",
        label=f"Telhado {telhado2}",
    )

    # Define os rótulos do eixo x como HH:MM a cada 10 minutos
    max_time = max(data1["Hora_Minuto"].max(), data2["Hora_Minuto"].max())
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
    plt.legend()
    plt.xticks(rotation=45)
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
        description="Gera gráficos a partir de arquivos CSV de telhados diferentes"
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )

    args = parser.parse_args()

    simulacao_dir = f"simulacao{args.simulacao}"
    output_dir = f"simulacao{args.simulacao}/graficos"

    # Certifica-se de que o diretório de saída existe
    os.makedirs(output_dir, exist_ok=True)

    telhados = os.listdir(simulacao_dir)
    telhados = [telhado for telhado in telhados if telhado.startswith("telhado")]

    # Processa todos os arquivos CSV em cada telhado
    for telhado1 in telhados:
        for telhado2 in telhados:
            if telhado1 != telhado2:
                csv_dir1 = os.path.join(simulacao_dir, telhado1, "csv")
                csv_dir2 = os.path.join(simulacao_dir, telhado2, "csv")

                for file_name in os.listdir(csv_dir1):
                    if file_name.endswith(".csv"):
                        plot_combined_csv(
                            args.simulacao, telhado1, telhado2, file_name, output_dir
                        )
                        print(
                            f'Gráfico combinado salvo em {output_dir}/{file_name.replace(".csv", ".png")} entre {telhado1} e {telhado2}'
                        )


if __name__ == "__main__":
    main()
