#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip'
#                      [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for"
#                     "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import os
import re
import heapq
import argparse
import json
import logging
import shutil
import gzip
from datetime import datetime
from collections import defaultdict

# настройка логирования

logging.basicConfig(level=logging.DEBUG, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

log_pattern = re.compile(
    r'^(?P<remote_addr>\S+) \S+  \S+ \[(?P<time_local>.*?)\] \"(?P<request>.*?)\" '
    r'(?P<status>\d+) \d+ \"(?P<http_referer>.*?)\" \"(?P<http_user_agent>.*?)\" '
    r'\".*?\" \"(?P<http_X_REQUEST_ID>.*?)\" \"(?P<http_X_RB_USER>.*?)\" (?P<request_time>.*?)$'
)
processed_logs_file = 'processed_logs.txt'


def extract_gz(gz_file):
    logging.info(f"file {gz_file} is opened for extract")
    output_file = os.path.splitext(gz_file)[0]  # Удаляем расширение .gz
    with gzip.open(gz_file, "rb") as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            return output_file


def read_config(config_file):
    try:
        with open(config_file) as f:
            config_from_file = json.load(f)
    except FileNotFoundError:
        logging.error(f"Конфиг файл '{config_file}' не найден")
        exit(1)
    except json.JSONDecodeError:
        logging.error(f" Ошибка парсинга конфиг файла '{config_file}'")
        exit(1)
    return config_from_file


def merge_config(default_config, file_config):
    merged_config = default_config.copy()
    merged_config.update(file_config)
    return merged_config


def log_processed_file(log_file, report_file):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(processed_logs_file, 'w') as f:
        f.write(f'{timestamp}: Processed {log_file} -> Generated {report_file}\n')


def log_generator(file):
    try:
        with open(file, "r") as f:
            for log_line in f:
                yield log_line
    except FileNotFoundError:
        logging.error("Не найден файл для парсинга")


def parse_log(file):
    log_data = defaultdict(list)
    for log_line in log_generator(file):
        match = log_pattern.match(log_line)
        if match:
            log_entry = match.groupdict()
            request_parts = log_entry['request'].split()
            if len(request_parts) > 1:
                # берём только адрес "GET /api/v2/banner/17461445 HTTP/1.1"
                url = log_entry['request'].split()[1]
            else:
                url = 'Empty'
            request_time = float(log_entry['request_time'])
            log_data[url].append(request_time)
        else:
            logging.info("Совпадений с шаблоном для парсинга не найдено")
    return log_data


def generate_report(log_data, report_size):
    total_entries = len(log_data)
    sorted_urls = heapq.nlargest(report_size, log_data, key=lambda x: sum(log_data[x]) / len(log_data[x]))

    with open('report_template.html', 'r') as file:
        template = file.read()
    report = template
    table_rows = ""
    for url in sorted_urls:
        request_times = log_data[url]
        count = len(request_times)
        time_sum = sum(request_times)
        time_avg = time_sum / count
        time_max = max(request_times)
        time_med = sorted(request_times)[count // 2] if count % 2 == 1 else\
            (sorted(request_times)[count // 2 - 1] + sorted(request_times)[count // 2]) / 2
        count_percentage = count / total_entries * 100
        time_percentage = time_sum / sum([sum(times) for times in log_data.values()]) * 100

        table_rows += f"""
            <tr>
                <td><a href="{url}">{url}</a></td>
                <td>{count}</td>
                <td>{count_percentage:.2f}%</td>
                <td>{time_avg:.2f}</td>
                <td>{time_percentage:.2f}%</td>
                <td>{time_sum:.4f}</td>
                <td>{time_max:.3f}</td>
                <td>{time_med:.3f}</td>
            </tr>
        """

    report = report.replace('$TABLE_ROWS', table_rows)

    return report


def save_report(report, report_dir, processed_log_file):
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    report_file = os.path.join(report_dir, f"report-{os.path.basename(processed_log_file)}.html")
    with open(report_file, 'w') as file:
        file.write(report)
    print(f'Report saved to: {report_file}')
    logging.info(f'Файл успешно обработан и отчет  {report_file} сгенерирован.')
    return report_file


def find_latest_log_file(log_dir):
    log_files = []
    pattern = r'nginx-access-ui\.log-\d{8}'  # Шаблон для поиска файлов вида nginx-access-ui.log-YYYYMMDD
    for file in os.listdir(log_dir):
        if file.startswith('nginx-access-ui.log') and re.match(pattern, file) and not (file.endswith(".gz")):
            log_files.append(os.path.join(log_dir, file))
        elif file.startswith('nginx-access-ui.log') and file.endswith(".gz"):
            extract_file = extract_gz(os.path.join(log_dir, file))
            log_files.append(extract_file)
        else:
            logging.error(f'В директории {log_dir} нет файлов нужного формата')
            exit(1)
    latest_log_file = max(log_files, key=os.path.getctime)
    return latest_log_file


def main(config_file):
    default_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log"
    }
    file_config = read_config(config_file)
    config = merge_config(default_config, file_config)
    log_dir = config['LOG_DIR']
    latest_log_file = find_latest_log_file(log_dir)
    logging.debug(f"Обрабатываемый лог. файл {latest_log_file}")
    report_dir = config['REPORT_DIR']
    report_file = os.path.join(report_dir, f"report-{os.path.basename(latest_log_file)}.html")
    logging.debug(f" Файл отчета: report-{os.path.basename(latest_log_file)}.html")

    if os.path.exists(report_file):
        logging.debug(f"Отчет для файла {latest_log_file} уже существует: {report_file}")
        exit(0)
    else:
        log_data = parse_log(latest_log_file)
        report_size = config['REPORT_SIZE']
        processed_log_file = latest_log_file
        report = generate_report(log_data, report_size)
        save_report(report, report_dir, processed_log_file)
    # Записываем информацию о обработанном лог-файле и отчете
    log_processed_file(latest_log_file, report_file)


if __name__ == "__main__":
    # Create parser arguments
    print("парсинг логов, подробности в py_log.log")
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    # Get arguments from command line
    args = parser.parse_args()
    main(args.config)
