import asyncio
import aioping
import itertools

# import pythonping

list_for_ping = list()
with open('for_ping.txt', 'r') as for_ping:
    for ip in for_ping:
        ip = ip.strip()

        if len(octets := ip.split('.')) < 4:
            ip = f'192.{ip}'

        octets_ranges = list()
        for octet in octets:
            if len(octet_range := octet.split('-')) == 2:
                octets_range = tuple(oct for oct in range(int(octet_range[0].strip()), int(octet_range[-1].strip())))
                octets_ranges.append(octets_range)
            else:
                octets_ranges.append((octet,))
                print(ip)
        print(octets_ranges)

        # разворачиваем все комбинации
        for combo in itertools.product(*octets_ranges):
            list_for_ping.append(".".join(str(combo)))

        # try:
        #     list_for_ping.append(ip)
        # except socket.gaierror:
        #     pass


async def do_ping(host):
    try:

        delay = await aioping.ping(host, timeout=5) * 1000
        print(f"Ping {host} response in %s ms" % delay)

    except TimeoutError:
        print(f" {host} Timed out")
        with open('not_pinged_hosts.txt', 'a') as f_not_pinged:
            f_not_pinged.write(f'{host}\n')


coroutin_list = (do_ping(ip) for ip in list_for_ping)


# for ip in list_for_ping:
#     coroutin_list.append(do_ping(ip))

# print(coroutin_list)
def for_sort_ip(host: str) -> int:
    """
    Функция для передачи в функцию сортировки в качестве ключа. (sorted(list_IPs, key = for_sort_ip)
    Правильно сортирует ip-адрес.
    :param host: Str (Ip- адрес)
    :return: int (Число, соответствующее входящему IP-адресу)
    """
    sections = host.strip().split('.')
    num_for_sort = ''
    for num in sections:
        while len(num) < 3:
            num = f'0{num}'
        num_for_sort = f'{num_for_sort}{num}'
    return int(num_for_sort)


def sort_non_pinged_hosts(file):
    non_sorted = set()
    with open(file, 'r') as f_handle:
        for line in f_handle:
            non_sorted.add(line.strip())
    yes_sorted = sorted(non_sorted, key=for_sort_ip)
    with open('not_pinged_hosts.txt', 'w') as f_handle:
        for host in yes_sorted:
            f_handle.write(f'{host}\n')


async def main():
    await asyncio.gather(*coroutin_list)
    sort_non_pinged_hosts('not_pinged_hosts.txt')


asyncio.run(main())
