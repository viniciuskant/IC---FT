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
import numpy as np
import pandas as pd


def process_csv(
    simulacao, telhado, file_name, curves_output_dir, derivatives_output_dir
):
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
    data["Hora_Minuto"] = (
        data["Hora_Minuto"] - min_time
    ).dt.total_seconds() / 3600  # Converte para minutos

    # A segunda coluna será a coluna de valores
    value_column_name = data.columns[1]
    data[value_column_name] = pd.to_numeric(data[value_column_name], errors="coerce")

    # Remove linhas com valores inválidos na segunda coluna
    data.dropna(subset=[value_column_name], inplace=True)

    # Ordena os dados pela coluna 'Hora_Minuto'
    data.sort_values(by="Hora_Minuto", inplace=True)

    # Ajusta e deriva os dados
    times = data["Hora_Minuto"].values
    values = data[value_column_name].values

    # Fit a polynomial to the data
    degree = 5
    coeffs = np.polyfit(times, values, degree)
    poly = np.poly1d(coeffs)

    # Compute the derivative of the polynomial
    derivative = np.polyder(poly)

    # Generate points for plotting the fitted curve and its derivative
    times_fit = np.linspace(min(times), max(times), 500)
    values_fit = poly(times_fit)
    derivative_fit = derivative(times_fit)

    # Plot the data and the fitted curve
    plt.figure(figsize=(20, 5))
    plt.plot(times, values, "bo", label="Original Data")
    plt.plot(times_fit, values_fit, "r-", label="Fitted Curve")

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

    plt.xlabel("Time (minutes since start)")
    plt.ylabel("Water Level (cm)")
    plt.legend()
    plt.title("Water Level and Fitted Curve")
    plt.grid(True)
    fitted_curve_output_path = os.path.join(
        curves_output_dir, file_name.replace(".csv", "_fitted_curve.png")
    )
    plt.savefig(fitted_curve_output_path)
    plt.close()

    # Plot the derivative
    plt.figure(figsize=(20, 5))
    plt.plot(times_fit, derivative_fit, "g--", label="Derivative")
    plt.xticks(
        ticks=ticks_hours, labels=x_labels, rotation=45
    )  # Adiciona os rótulos ao gráfico da derivada
    plt.xlabel("Time (minutes since start)")
    plt.ylabel("Derivative of Water Level (cm/min)")
    plt.legend()
    plt.title("Derivative of Water Level")
    plt.grid(True)
    derivative_output_path = os.path.join(
        derivatives_output_dir, file_name.replace(".csv", "_derivative.png")
    )
    plt.savefig(derivative_output_path)
    plt.close()

    return fitted_curve_output_path, derivative_output_path


def main():
    parser = argparse.ArgumentParser(
        description="Processa arquivos CSV para gerar gráficos de derivadas"
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )
    parser.add_argument(
        "--telhado", "-t", type=str, required=True, help="Número do telhado"
    )

    args = parser.parse_args()

    input_dir = f"simulacao{args.simulacao}/telhado{args.telhado}/csv/"
    base_output_dir = (
        f"simulacao{args.simulacao}/telhado{args.telhado}/graficos-derivadas"
    )
    curves_output_dir = os.path.join(base_output_dir, "curvas")
    derivatives_output_dir = os.path.join(base_output_dir, "derivadas")

    # Certifica-se de que os diretórios de saída existem
    os.makedirs(curves_output_dir, exist_ok=True)
    os.makedirs(derivatives_output_dir, exist_ok=True)

    # Processa todos os arquivos CSV na pasta de entrada
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            outputs = process_csv(
                args.simulacao,
                args.telhado,
                file_name,
                curves_output_dir,
                derivatives_output_dir,
            )
            print(f"Gráficos salvos em {outputs}")


if __name__ == "__main__":
    main()
