def get_proxy_lst(proxy_path):
    proxy_lst = []
    file = open(proxy_path, 'r')
    for line in file:
        proxy_lst.append(str(line[:-1])) #[:-1] to remove \n at end of line
    return proxy_lst

proxy_lst = get_proxy_lst('Proxies')
print(proxy_lst)