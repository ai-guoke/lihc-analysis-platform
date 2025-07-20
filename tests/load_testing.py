"""
Load Testing and Performance Benchmarking for LIHC Platform
Comprehensive testing of system performance under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
import json
import random
import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import psutil
import requests
import io
from datetime import datetime


@dataclass
class LoadTestResult:
    """Load test result data class"""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_95: float
    percentile_99: float
    requests_per_second: float
    errors: List[str]


class LoadTester:
    """Performance load testing for LIHC Platform APIs"""
    
    def __init__(self, base_url: str = "http://localhost:8050"):
        self.base_url = base_url
        self.access_token = None
        self.test_results = []
        
    async def authenticate(self, username: str = None, password: str = None):
        """Authenticate and get access token"""
        # Use environment variables for test credentials
        import os
        test_username = username or os.getenv("TEST_USERNAME", "admin")
        test_password = password or os.getenv("TEST_PASSWORD", "test_password_123")
        
        async with aiohttp.ClientSession() as session:
            login_data = {
                "username": test_username,
                "password": test_password
            }
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    return True
                return False
    
    async def make_request(self, 
                          session: aiohttp.ClientSession, 
                          method: str, 
                          endpoint: str, 
                          **kwargs) -> Tuple[int, float, str]:
        """Make an individual request and measure response time"""
        headers = kwargs.get('headers', {})
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        kwargs['headers'] = headers
        
        start_time = time.time()
        try:
            async with session.request(method, f"{self.base_url}{endpoint}", **kwargs) as response:
                await response.read()  # Ensure response is fully read
                end_time = time.time()
                return response.status, end_time - start_time, ""
        except Exception as e:
            end_time = time.time()
            return 0, end_time - start_time, str(e)
    
    async def run_concurrent_requests(self, 
                                    method: str, 
                                    endpoint: str, 
                                    num_requests: int, 
                                    concurrent_users: int,
                                    **kwargs) -> LoadTestResult:
        """Run concurrent requests and collect performance metrics"""
        
        async def worker(session, semaphore):
            async with semaphore:
                return await self.make_request(session, method, endpoint, **kwargs)
        
        semaphore = asyncio.Semaphore(concurrent_users)
        
        start_time = time.time()
        errors = []
        response_times = []
        status_codes = []
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=concurrent_users * 2),
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            tasks = [worker(session, semaphore) for _ in range(num_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                status_codes.append(0)
                response_times.append(0)
            else:
                status_code, response_time, error = result
                status_codes.append(status_code)
                response_times.append(response_time)
                if error:
                    errors.append(error)
        
        # Calculate metrics
        successful_requests = sum(1 for code in status_codes if 200 <= code < 300)
        failed_requests = num_requests - successful_requests
        
        valid_response_times = [t for t in response_times if t > 0]
        
        if valid_response_times:
            avg_response_time = statistics.mean(valid_response_times)
            min_response_time = min(valid_response_times)
            max_response_time = max(valid_response_times)
            percentile_95 = statistics.quantiles(valid_response_times, n=20)[18]  # 95th percentile
            percentile_99 = statistics.quantiles(valid_response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = 0
            percentile_95 = percentile_99 = 0
        
        requests_per_second = num_requests / total_time if total_time > 0 else 0
        
        return LoadTestResult(
            test_name=f"{method} {endpoint}",
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            requests_per_second=requests_per_second,
            errors=errors[:10]  # Keep only first 10 errors
        )
    
    async def test_health_endpoint(self, num_requests: int = 100, concurrent_users: int = 10):
        """Test health endpoint performance"""
        print(f"Testing health endpoint with {num_requests} requests, {concurrent_users} concurrent users...")
        result = await self.run_concurrent_requests(
            "GET", "/health", num_requests, concurrent_users
        )
        self.test_results.append(result)
        return result
    
    async def test_api_health_endpoint(self, num_requests: int = 100, concurrent_users: int = 10):
        """Test API health endpoint performance"""
        print(f"Testing API health endpoint with {num_requests} requests, {concurrent_users} concurrent users...")
        result = await self.run_concurrent_requests(
            "GET", "/api/v1/health", num_requests, concurrent_users
        )
        self.test_results.append(result)
        return result
    
    async def test_datasets_endpoint(self, num_requests: int = 50, concurrent_users: int = 5):
        """Test datasets listing endpoint performance"""
        print(f"Testing datasets endpoint with {num_requests} requests, {concurrent_users} concurrent users...")
        result = await self.run_concurrent_requests(
            "GET", "/api/v1/datasets", num_requests, concurrent_users
        )
        self.test_results.append(result)
        return result
    
    async def test_analyses_endpoint(self, num_requests: int = 50, concurrent_users: int = 5):
        """Test analyses listing endpoint performance"""
        print(f"Testing analyses endpoint with {num_requests} requests, {concurrent_users} concurrent users...")
        result = await self.run_concurrent_requests(
            "GET", "/api/v1/analyses", num_requests, concurrent_users
        )
        self.test_results.append(result)
        return result
    
    def create_test_dataset(self) -> bytes:
        """Create a test dataset for upload testing"""
        # Generate random gene expression data
        genes = [f"GENE{i:04d}" for i in range(100)]
        samples = [f"SAMPLE{i:03d}" for i in range(50)]
        
        data = {gene: [random.uniform(0, 10) for _ in samples] for gene in genes}
        df = pd.DataFrame(data, index=samples)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer)
        return csv_buffer.getvalue().encode('utf-8')
    
    async def test_dataset_upload(self, num_uploads: int = 10, concurrent_users: int = 2):
        """Test dataset upload performance"""
        print(f"Testing dataset upload with {num_uploads} uploads, {concurrent_users} concurrent users...")
        
        test_data = self.create_test_dataset()
        
        async def upload_dataset(session, semaphore, upload_id):
            async with semaphore:
                data = aiohttp.FormData()
                data.add_field('file', test_data, filename=f'test_data_{upload_id}.csv', content_type='text/csv')
                data.add_field('name', f'Load Test Dataset {upload_id}')
                data.add_field('description', f'Dataset for load testing {upload_id}')
                data.add_field('data_type', 'rna_seq')
                
                headers = {'Authorization': f'Bearer {self.access_token}'}
                
                return await self.make_request(
                    session, "POST", "/api/v1/datasets/upload", 
                    data=data, headers=headers
                )
        
        semaphore = asyncio.Semaphore(concurrent_users)
        start_time = time.time()
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=concurrent_users * 2),
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout for uploads
        ) as session:
            tasks = [upload_dataset(session, semaphore, i) for i in range(num_uploads)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Process results
        successful_uploads = 0
        failed_uploads = 0
        response_times = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_uploads += 1
                errors.append(str(result))
            else:
                status_code, response_time, error = result
                response_times.append(response_time)
                if 200 <= status_code < 300:
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                if error:
                    errors.append(error)
        
        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        result = LoadTestResult(
            test_name="POST /api/v1/datasets/upload",
            total_requests=num_uploads,
            successful_requests=successful_uploads,
            failed_requests=failed_uploads,
            total_time=total_time,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_95=0,  # Not calculated for small samples
            percentile_99=0,
            requests_per_second=num_uploads / total_time if total_time > 0 else 0,
            errors=errors[:5]
        )
        
        self.test_results.append(result)
        return result
    
    async def stress_test(self, duration_seconds: int = 60):
        """Run stress test for specified duration"""
        print(f"Running stress test for {duration_seconds} seconds...")
        
        start_time = time.time()
        request_count = 0
        errors = []
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration_seconds:
                # Mix of different endpoint calls
                endpoints = [
                    ("GET", "/health"),
                    ("GET", "/api/v1/health"),
                    ("GET", "/api/v1/datasets"),
                    ("GET", "/api/v1/analyses")
                ]
                
                method, endpoint = random.choice(endpoints)
                
                try:
                    status_code, response_time, error = await self.make_request(
                        session, method, endpoint
                    )
                    request_count += 1
                    if error:
                        errors.append(error)
                except Exception as e:
                    errors.append(str(e))
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
        
        total_time = time.time() - start_time
        
        result = LoadTestResult(
            test_name="Stress Test",
            total_requests=request_count,
            successful_requests=request_count - len(errors),
            failed_requests=len(errors),
            total_time=total_time,
            avg_response_time=0,  # Not calculated in stress test
            min_response_time=0,
            max_response_time=0,
            percentile_95=0,
            percentile_99=0,
            requests_per_second=request_count / total_time if total_time > 0 else 0,
            errors=errors[:10]
        )
        
        self.test_results.append(result)
        return result
    
    def monitor_system_resources(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Monitor system resources during testing"""
        print(f"Monitoring system resources for {duration_seconds} seconds...")
        
        cpu_percentages = []
        memory_percentages = []
        disk_usage_percentages = []
        network_stats = []
        
        start_time = time.time()
        initial_network = psutil.net_io_counters()
        
        while time.time() - start_time < duration_seconds:
            cpu_percentages.append(psutil.cpu_percent(interval=1))
            memory_percentages.append(psutil.virtual_memory().percent)
            disk_usage_percentages.append(psutil.disk_usage('/').percent)
            network_stats.append(psutil.net_io_counters())
        
        final_network = psutil.net_io_counters()
        
        return {
            "cpu_usage": {
                "average": statistics.mean(cpu_percentages),
                "max": max(cpu_percentages),
                "min": min(cpu_percentages)
            },
            "memory_usage": {
                "average": statistics.mean(memory_percentages),
                "max": max(memory_percentages),
                "min": min(memory_percentages)
            },
            "disk_usage": {
                "average": statistics.mean(disk_usage_percentages),
                "max": max(disk_usage_percentages),
                "min": min(disk_usage_percentages)
            },
            "network": {
                "bytes_sent": final_network.bytes_sent - initial_network.bytes_sent,
                "bytes_recv": final_network.bytes_recv - initial_network.bytes_recv,
                "packets_sent": final_network.packets_sent - initial_network.packets_sent,
                "packets_recv": final_network.packets_recv - initial_network.packets_recv
            }
        }
    
    async def run_comprehensive_load_test(self):
        """Run comprehensive load testing suite"""
        print("Starting comprehensive load testing suite...")
        print("=" * 60)
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed!")
            return
        print("✅ Authentication successful")
        
        # Test scenarios with increasing load
        test_scenarios = [
            # Light load
            ("Light Load", [
                (self.test_health_endpoint, 50, 5),
                (self.test_api_health_endpoint, 50, 5),
                (self.test_datasets_endpoint, 25, 3),
                (self.test_analyses_endpoint, 25, 3)
            ]),
            
            # Medium load
            ("Medium Load", [
                (self.test_health_endpoint, 200, 20),
                (self.test_api_health_endpoint, 200, 20),
                (self.test_datasets_endpoint, 100, 10),
                (self.test_analyses_endpoint, 100, 10),
                (self.test_dataset_upload, 5, 2)
            ]),
            
            # Heavy load
            ("Heavy Load", [
                (self.test_health_endpoint, 500, 50),
                (self.test_api_health_endpoint, 500, 50),
                (self.test_datasets_endpoint, 200, 20),
                (self.test_analyses_endpoint, 200, 20),
                (self.test_dataset_upload, 10, 3)
            ])
        ]
        
        for scenario_name, tests in test_scenarios:
            print(f"\n🔄 Running {scenario_name} tests...")
            
            # Monitor system resources during testing
            monitoring_task = asyncio.create_task(
                asyncio.to_thread(self.monitor_system_resources, 120)
            )
            
            # Run tests
            for test_func, *args in tests:
                try:
                    result = await test_func(*args)
                    print(f"✅ {result.test_name}: {result.requests_per_second:.2f} req/s")
                except Exception as e:
                    print(f"❌ {test_func.__name__}: {str(e)}")
            
            # Get system resource usage
            try:
                system_stats = await monitoring_task
                print(f"📊 System Usage - CPU: {system_stats['cpu_usage']['average']:.1f}%, "
                      f"Memory: {system_stats['memory_usage']['average']:.1f}%")
            except:
                pass
        
        # Run stress test
        print(f"\n🔥 Running stress test...")
        await self.stress_test(60)
        
        print("\n📈 Load testing completed!")
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        report = {
            "summary": {
                "total_tests": len(self.test_results),
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "cpu_count": multiprocessing.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total // (1024**3),
                    "python_version": psutil.__version__
                }
            },
            "test_results": [],
            "performance_analysis": {}
        }
        
        # Add individual test results
        for result in self.test_results:
            report["test_results"].append(asdict(result))
        
        # Calculate overall performance metrics
        total_requests = sum(r.total_requests for r in self.test_results)
        total_successful = sum(r.successful_requests for r in self.test_results)
        total_failed = sum(r.failed_requests for r in self.test_results)
        
        avg_rps = statistics.mean([r.requests_per_second for r in self.test_results if r.requests_per_second > 0])
        max_rps = max([r.requests_per_second for r in self.test_results if r.requests_per_second > 0], default=0)
        
        avg_response_times = [r.avg_response_time for r in self.test_results if r.avg_response_time > 0]
        overall_avg_response = statistics.mean(avg_response_times) if avg_response_times else 0
        
        report["performance_analysis"] = {
            "total_requests": total_requests,
            "success_rate": (total_successful / total_requests * 100) if total_requests > 0 else 0,
            "failure_rate": (total_failed / total_requests * 100) if total_requests > 0 else 0,
            "average_rps": avg_rps,
            "peak_rps": max_rps,
            "overall_avg_response_time": overall_avg_response
        }
        
        # Performance recommendations
        recommendations = []
        if avg_rps < 50:
            recommendations.append("Consider optimizing API endpoints for better throughput")
        if overall_avg_response > 1.0:
            recommendations.append("Average response time is high, investigate bottlenecks")
        if total_failed / total_requests > 0.05:
            recommendations.append("High failure rate detected, check error handling")
        
        report["recommendations"] = recommendations
        
        return report
    
    def save_report(self, filename: str = None):
        """Save performance report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Performance report saved to {filename}")
        return filename
    
    def print_summary(self):
        """Print a summary of test results"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("🚀 LIHC Platform Load Test Summary")
        print("="*60)
        
        perf = report["performance_analysis"]
        print(f"Total Requests: {perf['total_requests']}")
        print(f"Success Rate: {perf['success_rate']:.2f}%")
        print(f"Average RPS: {perf['average_rps']:.2f}")
        print(f"Peak RPS: {perf['peak_rps']:.2f}")
        print(f"Avg Response Time: {perf['overall_avg_response_time']:.3f}s")
        
        print(f"\n📊 Individual Test Results:")
        print("-" * 60)
        for result in self.test_results:
            status = "✅" if result.failed_requests == 0 else "⚠️"
            print(f"{status} {result.test_name:<30} | {result.requests_per_second:>8.2f} req/s | {result.avg_response_time:>8.3f}s avg")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"{i}. {rec}")


async def main():
    """Main function to run load tests"""
    print("🚀 LIHC Platform Load Testing Suite")
    print("="*50)
    
    # Initialize load tester
    tester = LoadTester()
    
    # Run comprehensive load tests
    await tester.run_comprehensive_load_test()
    
    # Print summary and save report
    tester.print_summary()
    tester.save_report()


if __name__ == "__main__":
    asyncio.run(main())