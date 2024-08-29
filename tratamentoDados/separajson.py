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
import json
import os
from datetime import datetime

import jsonlines
import pytz


def split_json_by_topic_and_time(input_file, output_dir, start_datetime, end_datetime):
    # Cria um dicionário para agrupar os dados por tópico
    grouped_data = {}

    # Define o fuso horário de Londres
    london_tz = pytz.timezone("Europe/London")

    print(f"Start datetime: {start_datetime}")
    print(f"End datetime: {end_datetime}")
    print()
    print(f"Reading file: {input_file}")
    print()

    # Lê o arquivo JSON de entrada linha por linha
    with jsonlines.open(input_file) as reader:
        for item in reader:
            # Converte a string datetime do item para um objeto datetime no fuso horário de Londres
            item_time = datetime.fromisoformat(
                item["datetime"]["$date"].replace("Z", "+00:00")
            ).astimezone(london_tz)

            # Verifica se o item está dentro do intervalo de tempo especificado
            if start_datetime <= item_time <= end_datetime:
                topic = item.get("topic")
                if topic:
                    if topic not in grouped_data:
                        grouped_data[topic] = []
                    grouped_data[topic].append(item)

    # Remove o campo 'topic' do arquivo original
    for item in grouped_data.values():
        for data in item:
            if "topic" in data:
                del data["topic"]

    # Cria o diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Salva cada grupo em um arquivo JSON separado
    for topic, items in grouped_data.items():
        topic_filename = topic.replace("/", "_").replace(" ", "_") + ".json"
        output_file = os.path.join(output_dir, topic_filename)
        with open(output_file, "w") as f:
            json.dump(items, f, indent=4)
        print(f"Salvo: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Processa um arquivo JSON por tópico e intervalo de tempo"
    )
    parser.add_argument(
        "--simulacao", "-s", type=str, required=True, help="Número da simulação"
    )
    parser.add_argument(
        "--telhado", "-t", type=str, required=True, help="Número do telhado"
    )
    parser.add_argument(
        "--inicio",
        "-i",
        type=str,
        required=True,
        help="Hora de início do intervalo (formato: HH:MM)",
    )
    parser.add_argument(
        "--fim",
        "-f",
        type=str,
        required=True,
        help="Hora de fim do intervalo (formato: HH:MM)",
    )
    parser.add_argument(
        "--dia-inicio",
        type=str,
        required=True,
        help="Dia de início do intervalo (formato: YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dia-fim",
        type=str,
        required=True,
        help="Dia de fim do intervalo (formato: YYYY-MM-DD)",
    )

    args = parser.parse_args()

    input_file = f"simulacao{args.simulacao}/telhado{args.telhado}/json/Telhado{args.telhado}.json"
    output_dir = f"simulacao{args.simulacao}/telhado{args.telhado}/json"

    # Define o intervalo de tempo a partir dos argumentos de linha de comando
    start_time = args.inicio
    end_time = args.fim
    start_date = args.dia_inicio
    end_date = args.dia_fim

    # Define os fusos horários de Londres e Noronha
    london_tz = pytz.timezone("Europe/London")
    noronha_tz = pytz.timezone("America/Noronha")

    # Converte os horários de início e fim para datetime no fuso horário de Noronha
    start_datetime_sp = noronha_tz.localize(
        datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    )
    end_datetime_sp = noronha_tz.localize(
        datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
    )

    # Converte os horários de início e fim para o fuso horário de Londres
    start_datetime_ldn = start_datetime_sp.astimezone(london_tz)
    end_datetime_ldn = end_datetime_sp.astimezone(london_tz)

    split_json_by_topic_and_time(
        input_file, output_dir, start_datetime_ldn, end_datetime_ldn
    )


if __name__ == "__main__":
    main()
