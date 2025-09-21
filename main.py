import asyncio
import itertools
import time

import aioping

MAX_CONCURRENT_PINGS = 200


def print_to_files(pinged, not_pinged):
    with open('pinged.txt', 'w') as f_pinged, open('not_pinged.txt', 'w') as f_not_pinged:
        for host in pinged:
            f_pinged.write(f"{host}\n")
        for host in not_pinged:
            f_not_pinged.write(f"{host}\n")


def load_ips(filename: str) -> list[str]:
    """
    Загружает список IP-адресов из файла.
    Поддерживает диапазоны в формате 192.168.1-2.1-3
    """
    ips = []
    with open(filename, 'r') as for_ping:
        for ip in for_ping:
            ip = ip.strip()
            if not ip:
                continue

            # добавляем "192." если только 3 октета
            if len(octets := ip.split('.')) < 4:
                ip = f'192.{ip}'
                octets = ip.split('.')

            octets_ranges = []
            for octet in octets:
                if '-' in octet:
                    start, end = map(int, octet.split('-'))
                    octets_ranges.append([str(i) for i in range(start, end + 1)])
                else:
                    octets_ranges.append([octet])

            # генерируем все комбинации
            for combo in itertools.product(*octets_ranges):
                ips.append(".".join(combo))

    return ips


async def do_ping(host: str, pinged, non_pinged, sem: asyncio.Semaphore):
    """Асинхронный пинг одного хоста с ограничением семафора"""
    async with sem:
        try:
            delay = await aioping.ping(host, timeout=5) * 1000
            pinged.append(host)
            print(f"Ping {host} response in {delay:.2f} ms")
        except TimeoutError:
            non_pinged.append(host)
            print(f"{host} Timed out")


def for_sort_ip(host: str) -> int:
    """Ключ сортировки IP"""
    sections = host.strip().split('.')
    num_for_sort = ''
    for num in sections:
        while len(num) < 3:
            num = f'0{num}'
        num_for_sort += num
    return int(num_for_sort)


# def sort_non_pinged_hosts(file: str):
#     """Сортировка списка непингующихся хостов"""
#     try:
#         with open(file, 'r') as f_handle:
#             non_sorted = {line.strip() for line in f_handle if line.strip()}
#         yes_sorted = sorted(non_sorted, key=for_sort_ip)
#         with open(file, 'w') as f_handle:
#             for num, host in enumerate(yes_sorted):
#                 f_handle.write(f'{num + 1}) {host}\n')
#     except FileNotFoundError:
#         pass


async def main():
    pinged = list()
    non_pinged = list()
    ips = load_ips('for_ping.txt')

    # # очищаем файл непингованных хостов перед запуском
    # open('not_pinged_hosts.txt', 'w').close()

    # создаём семафор — ограничение на количество параллельных задач
    sem = asyncio.Semaphore(MAX_CONCURRENT_PINGS)  # 🔧 можно менять (например, 200, 500)

    tasks = (do_ping(ip, pinged, non_pinged, sem) for ip in ips)
    await asyncio.gather(*tasks)

    # sort_non_pinged_hosts('not_pinged_hosts.txt')
    pinged.sort(key=for_sort_ip)
    non_pinged.sort(key=for_sort_ip)
    # print(pinged)
    # print(non_pinged)
    print_to_files(pinged, non_pinged)
    print()
    await asyncio.sleep(1)



if __name__ == "__main__":
    asyncio.run(main())
    input('Для закрытия консоли - нажми Энтэр!')
