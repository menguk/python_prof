from .. log_analyzer  import parse_log, generate_report

def test_parse_log():
    test_log_file = 'test_log.txt'
    with open(test_log_file, 'w') as f:
        f.write('1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n')
    log_data = parse_log(test_log_file)
    assert '/api/v2/banner/16852664' in log_data


def test_generate_report():
    # Подготавливаем тестовые данные для отчета
    log_data = {'url1': [1.2, 3.4], 'url2': [5.6, 7.8]}
    report_size = 2

    # Проверяем, что функция generate_report корректно генерирует отчет
    report = generate_report(log_data, report_size)
    assert 'url1' in report
