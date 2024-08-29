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
import csv
import json
import os
from datetime import datetime


def json_to_csv(input_file, output_file):
    # Lê o arquivo JSON de entrada
    with open(input_file, "r") as f:
        data = json.load(f)

    # Abre o arquivo CSV para escrita
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["data", "body"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escreve o cabeçalho no arquivo CSV
        writer.writeheader()

        # Itera sobre cada objeto no JSON e escreve no CSV
        for item in data:
            datetime_str = item["datetime"]["$date"]
            body = item["body"]

            # Formata a data e extrai componentes
            dt = datetime.fromisoformat(
                datetime_str[:-1]
            )  # Remove o 'Z' do final e converte para datetime

            hour_minute = f"{dt.hour}:{dt.minute:02d}"  # Formato H.MM com minutos sempre em dois dígitos

            # Escreve a linha no arquivo CSV
            writer.writerow({"data": hour_minute, "body": body})


def process_folder(input_folder, output_folder):
    # Verifica se o diretório de saída existe, senão cria
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Itera sobre todos os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file = os.path.join(input_folder, filename)

            # Cria o nome do arquivo de saída CSV baseado no nome do arquivo JSON
            output_file = os.path.join(
                output_folder, os.path.splitext(filename)[0] + ".csv"
            )

            # Converte o JSON para CSV
            try:
                json_to_csv(input_file, output_file)
                print(f"Arquivo CSV criado: {output_file}")
            except json.JSONDecodeError as e:
                print(f"Erro ao processar {input_file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Converte arquivos JSON em CSV por simulação e telhado"
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )
    parser.add_argument(
        "--telhado", "-t", type=str, required=True, help="Número do telhado"
    )

    args = parser.parse_args()

    input_folder = f"simulacao{args.simulacao}/telhado{args.telhado}/json"
    output_folder = f"simulacao{args.simulacao}/telhado{args.telhado}/csv"

    process_folder(input_folder, output_folder)


if __name__ == "__main__":
    main()
