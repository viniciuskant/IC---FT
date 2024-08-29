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

import pandas as pd


def process_csv(input_file, output_file):
    # Configurar pandas para exibir todas as colunas e linhas
    # pd.set_option('display.max_rows', None)  # Mostra todas as linhas
    # pd.set_option('display.max_columns', None)  # Mostra todas as colunas
    # pd.set_option('display.width', None)  # Ajusta a largura de exibição para acomodar todas as colunas

    # Ler o arquivo CSV
    df = pd.read_csv(input_file)

    # Converter a coluna 'data' para datetime, especificando o formato
    df["data"] = pd.to_datetime(df["data"], format="%H:%M")

    # Ordenar o DataFrame pela coluna 'data'
    df = df.sort_values(by="data")
    print(df)  # Imprime o DataFrame completo

    # Inicializar uma lista para armazenar as linhas que atendem à condição
    filtered_rows = []

    # Definir o valor mínimo inicial como o primeiro valor da coluna 'body' após a ordenação
    minimo = df.iloc[0]["body"]

    # Iterar sobre as linhas do dataframe
    for i in range(len(df)):
        if df.iloc[i]["body"] >= minimo:
            filtered_rows.append(df.iloc[i])
            minimo = df.iloc[i]["body"]  # Atualiza o valor mínimo

    # Criar um novo DataFrame com as linhas filtradas
    filtered_df = pd.DataFrame(filtered_rows)

    # Salvar o novo DataFrame no arquivo de saída
    filtered_df.to_csv(output_file, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Processa um arquivo CSV e remove linhas onde o body é menor que o body anterior."
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )
    parser.add_argument(
        "--telhado", "-t", type=str, required=True, help="Número do telhado"
    )

    args = parser.parse_args()

    input_file = (
        f"simulacao{args.simulacao}/telhado{args.telhado}/csv/NivelAgua(cm).csv"
    )
    output_file = f"simulacao{args.simulacao}/telhado{args.telhado}/csv/NivelAguaCorrigido(cm).csv"

    process_csv(input_file, output_file)


if __name__ == "__main__":
    main()
