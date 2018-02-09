def get_proxy_lst(proxy_path):
    proxy_lst = []
    file = open(proxy_path, 'r')
    for line in file:
        cleaned_line = str(line[:-1]) #[:-1] to remove \n at end of line
        new_string = cleaned_line[-17:] + '@' + cleaned_line[:-18]
        proxy_lst.append(new_string)
    return proxy_lst

#proxy_lst = get_proxy_lst('Proxies')
#print(proxy_lst)

'''import urllib2

proxy = urllib2.ProxyHandler({'https': 'https://mthyge11:an2loper@82.211.50.204:80'})
# proxy = urllib2.ProxyHandler({'http': 'http://username:password@proxyurl:proxyport'})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)
    
conn = urllib2.urlopen('http://expressvpn.com/what-is-my-ip')
return_str = conn.read()
print return_str
'''