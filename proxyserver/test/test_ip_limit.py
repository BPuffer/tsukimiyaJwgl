import unittest
import asyncio
import time
import aiohttp
import redis
from unittest import IsolatedAsyncioTestCase

# 测试配置
BASE_URL = "http://localhost:20081"
TEST_MYIP = "192.168.1.100"  # 测试用的固定IP
HEADERS = {"X-Real-IP": TEST_MYIP}

class TestIPLimit(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """在每个测试前重置该IP的计数器"""
        await self.reset_ip_counter()
    
    async def reset_ip_counter(self):
        """异步重置测试IP的计数器"""
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._reset_redis)
        except Exception as e:
            print(f"重置计数器失败: {e}")
    
    def _reset_redis(self):
        """同步的Redis重置操作"""
        r = redis.Redis(host='localhost', port=6379, db=0)
        minute_key = f"rate_limit_minute:{TEST_MYIP}"
        hour_key = f"rate_limit_hour:{TEST_MYIP}"
        r.delete(minute_key, hour_key)
        print(f"重置计数器: {minute_key}, {hour_key}")

    async def make_request(self, session, url):
        """发送异步请求并返回状态码"""
        async with session.get(url, headers=HEADERS) as response:
            return response.status

    async def test_minute_limit(self):
        """测试每分钟限制(60次)"""
        print("> test_minute_limit")
        async with aiohttp.ClientSession() as session:
            # 发送60次请求 - 应该都成功
            starttime = time.time()
            tasks = [self.make_request(session, f"{BASE_URL}/api/server") 
                     for _ in range(60)]
            results = await asyncio.gather(*tasks)
            
            for i, status in enumerate(results, 1):
                self.assertNotEqual(status, 429, f"第 {i} 次请求意外被限制")
            
            endtime = time.time()
            self.assertLess(endtime - starttime, 60, "超过60s的测试失去意义")
            
            # 第61次请求 - 应该被限制
            status = await self.make_request(session, f"{BASE_URL}/api/server")
            self.assertEqual(status, 429, "第61次请求未被限制")
            
            # 等待1分钟后重试 - 应该解除限制
            waittime = 60 - (time.time() - starttime) + 2
            print(f"等待中……({waittime:.1f}s)")
            await asyncio.sleep(waittime)
            
            status = await self.make_request(session, f"{BASE_URL}/api/server")
            self.assertNotEqual(status, 429, "等待1分钟后请求仍被限制")

    async def test_mixed_routes(self):
        """测试不同路径的请求都计入限制"""
        print("> test_mixed_routes")
        urls = [
            f"{BASE_URL}/api/server",
            f"{BASE_URL}/proxy/",
            f"{BASE_URL}/proxy/example.com"
        ]
        
        async with aiohttp.ClientSession() as session:
            # 发送59次请求到不同路径
            starttime = time.time()
            tasks = []
            for i in range(20):
                tasks.append(self.make_request(session, urls[0]))
                tasks.append(self.make_request(session, urls[1]))
                if i != 0:  # 第一次循环不发第三条
                    tasks.append(self.make_request(session, urls[2]))
            
            results = await asyncio.gather(*tasks)
            
            for status in results:
                self.assertNotEqual(status, 429, "请求意外被限制")
            
            # 第60次请求 - 应该成功
            status = await self.make_request(session, urls[0])
            self.assertNotEqual(status, 429, "第60次请求被限制")
            
            endtime = time.time()
            self.assertLess(endtime - starttime, 60, "超过60s的测试失去意义")
            
            # 第61次请求 - 应该被限制
            status = await self.make_request(session, urls[1])
            self.assertEqual(status, 429, "第61次请求未被限制")

if __name__ == '__main__':
    unittest.main()