from urllib.parse import urlparse
from requests import Session
import urllib3
urllib3.disable_warnings()
import kawaiitb.autoload

testurl = 'https://authserver.yku.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.yku.edu.cn%2Fsso.jsp'
testproxyurl = 'http://localhost:5000'

PROXY_URL = '192.168.43.88:5000'  # 代理域名

def proxy_to(url):
    """
    URL转换函数，将目标URL转换为代理URL格式
    示例: https://e.cn/path -> https://proxy.cn/e.cn/path
    """
    if not url:
        return ''
    
    parsed = urlparse(url)
    proxy_path = f"{PROXY_URL}/{parsed.netloc}{parsed.path if parsed.path else ''}"
    if parsed.query:
        proxy_path += f"?{parsed.query}"
    if parsed.fragment:
        proxy_path += f"#{parsed.fragment}"
    
    scheme_prefix = parsed.scheme + "://" if parsed.scheme else "https://"
    scheme_prefix = "http://"
    return f"{scheme_prefix}{proxy_path}"

sessA = Session()
sessA.verify = False

print("="*30)
print("测试直接发送请求")
print("="*30)
print("第一次请求")
resp1 = sessA.get(testurl, allow_redirects=False)
# 现在，sessA发送请求，能设置关于authserver.yku.edu.cn的JSESSIONID
print(f"{resp1.cookies=}")
print("第二次请求")
resp2 = sessA.get(testurl, allow_redirects=False)
# 再次请求authserver.yku.edu.cn，能正确携带JSESSIONID，即不会再次设置
print(f"{resp2.cookies=}")



sessB = Session()
sessB.verify = False

print("="*30)
print("测试通过代理发送请求")
print("="*30)
print("第一次请求")
resp1 = sessB.get(proxy_to(testurl), allow_redirects=False)
# 现在，sessB通过代理发送请求，应当能设置关于authserver.yku.edu.cn的JSESSIONID
print(f"{resp1.cookies=}")
resp2 = sessB.get(proxy_to(testurl), allow_redirects=False)
print("第二次请求")
# 再次请求authserver.yku.edu.cn，应当能正确携带JSESSIONID，即不会再次设置
print(f"{resp2.cookies=}")

