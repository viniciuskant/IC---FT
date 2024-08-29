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
    # Ler o arquivo CSV
    df = pd.read_csv(input_file)

    # Inicializar uma lista para armazenar as linhas que atendem à condição
    filtered_rows = [df.iloc[0]]

    # Definir o valor mínimo inicial como o último valor da coluna 'body'
    minimo = df.iloc[len(df) - 1]["body"]

    # Iterar sobre as linhas do dataframe de trás para frente
    for i in range(len(df) - 1, -1, -1):
        if df.iloc[i]["body"] >= minimo:
            filtered_rows.append(df.iloc[i])
            minimo = df.iloc[i]["body"]

    # Reverter a lista filtrada para manter a ordem original
    filtered_rows.reverse()

    # Criar um novo dataframe com as linhas filtradas
    filtered_df = pd.DataFrame(filtered_rows)

    # Salvar o novo dataframe no arquivo de saída
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

    input_file = f"simulacao{args.simulacao}/telhado{args.telhado}/csv/Volume(cm3).csv"
    output_file = f"simulacao{args.simulacao}/telhado{args.telhado}/csv/Volume(cm3).csv"

    process_csv(input_file, output_file)


if __name__ == "__main__":
    main()
