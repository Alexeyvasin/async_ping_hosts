import asyncio
import aioping
import pythonping

list_for_ping = list()
with open('for_ping.txt', 'r') as for_ping:
    for ip in for_ping:
        ip = ip.strip()
        if len(ip.split('.')) < 4:
            ip = f'192.{ip}'
        list_for_ping.append(ip)


async def do_ping(host):
    try:

        delay = await aioping.ping(host,timeout=5) * 1000
        print(f"Ping {host} response in %s ms" % delay)

    except TimeoutError:
        print(f" {host} Timed out")
        with open('not_pinged_hosts.txt', 'a') as f_not_pinged:
            f_not_pinged.write(f'{host}\n')


coroutin_list = []
for ip in list_for_ping:
    coroutin_list.append(do_ping(ip))

print(*coroutin_list)


async def main():
    await asyncio.gather(*coroutin_list)


asyncio.run(main())
