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
import glob
import os

import pandas as pd


def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)
    escoamento_rows = []

    # Definir o raio do cilindro em cm
    raio = 30
    area_seccao = 3.14 * (raio**2)  # π * r^2

    # Iterar sobre as linhas do dataframe para calcular o escoamento
    for i in range(1, len(df)):
        nivel_anterior = df.iloc[i]["body"]
        nivel_atual = df.iloc[i - 1]["body"]
        diferenca_nivel = nivel_atual - nivel_anterior

        # Diferença de tempo em segundos
        tempo_anterior = pd.to_datetime(df.iloc[i]["data"])
        tempo_atual = pd.to_datetime(df.iloc[i - 1]["data"])
        diferenca_tempo = ((tempo_atual - tempo_anterior).total_seconds()) / 60

        escoamento = (diferenca_nivel * area_seccao) / diferenca_tempo

        escoamento_rows.append({"data": df.iloc[i]["data"], "body": escoamento})

    # Criar um novo dataframe com os resultados do escoamento
    escoamento_df = pd.DataFrame(escoamento_rows)

    # Salvar o novo dataframe no arquivo de saída
    escoamento_df.to_csv(output_file, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Processa arquivos CSV de níveis de água e calcula o escoamento."
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )
    parser.add_argument(
        "--telhado", "-t", type=str, required=True, help="Número do telhado"
    )

    args = parser.parse_args()

    input_pattern = (
        f"simulacao{args.simulacao}/telhado{args.telhado}/csv/*NivelAgua*.csv"
    )
    output_dir = f"simulacao{args.simulacao}/telhado{args.telhado}/csv/"

    # Encontrar todos os arquivos que correspondem ao padrão
    input_files = glob.glob(input_pattern)

    # Processar cada arquivo encontrado
    for input_file in input_files:
        output_file = os.path.join(
            output_dir, f"EscoamentoPy_{os.path.basename(input_file)}"
        )
        process_csv(input_file, output_file)


if __name__ == "__main__":
    main()
