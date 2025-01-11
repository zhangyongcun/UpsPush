#!/usr/bin/env python3
import hid
import time
import requests
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SantakUPS:
    def __init__(self):
        # Check required environment variables
        required_vars = ['VENDOR_ID', 'PRODUCT_ID', 'BARK_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"错误: 缺少必要的环境变量: {', '.join(missing_vars)}")
            print("请确保已正确配置 .env 文件")
            sys.exit(1)

        try:
            self.VENDOR_ID = int(os.getenv('VENDOR_ID'), 16)
            self.PRODUCT_ID = int(os.getenv('PRODUCT_ID'), 16)
        except ValueError as e:
            print("错误: VENDOR_ID 或 PRODUCT_ID 格式不正确")
            sys.exit(1)

        self.device = None
        self.bark_url = os.getenv('BARK_URL')
        self.bark_volume = int(os.getenv('BARK_VOLUME', '5'))
        self.last_power_state = True  # True表示有市电
        self.last_read_success = True  # 用于跟踪上次读取状态是否成功
        
    def send_bark_notification(self, message, level="critical", continuous_ring=False):
        try:
            url = f"{self.bark_url}/{message}"
            params = {
                "level": level,
                "volume": self.bark_volume
            }
            if continuous_ring:
                params["call"] = "1"
                
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                print(f"告警发送成功: {message}")
            else:
                print(f"告警发送失败: {response.status_code}")
        except Exception as e:
            print(f"发送告警失败: {str(e)}")

    def connect(self):
        try:
            self.device = hid.device()
            self.device.open(self.VENDOR_ID, self.PRODUCT_ID)
            self.device.set_nonblocking(1)
            return True
        except Exception as e:
            print(f"连接错误: {str(e)}")
            return False

    def read_status(self):
        try:
            data = self.device.get_feature_report(1, 8)
            if data:
                self.last_read_success = True  # 标记读取成功
                return self.parse_status(data)
            self.last_read_success = False  # 标记读取失败
            return None
        except Exception as e:
            print(f"读取状态错误: {str(e)}")
            self.last_read_success = False  # 标记读取失败
            return None

    def parse_status(self, data):
        if not data:
            return None

        status = {
            'ac_present': bool(data[1] & 0x01),
            'battery_low': bool(data[1] & 0x02),
            'charging': bool(data[1] & 0x08),
            'discharging': bool(data[1] & 0x20),
            'overload': bool(data[1] & 0x40),
            'raw_data': ' '.join([f'{x:02x}' for x in data])
        }
        return status

    def check_and_notify(self, status):
        # 检查是否无法读取数据
        if not self.last_read_success:
            if self.last_read_success != False:  # 只在状态变化时发送通知
                self.send_bark_notification("UPS警告：无法读取UPS数据！", level="critical")
            return

        if status is None:
            return
        
        current_power_state = status['ac_present']
        
        # 如果电源状态发生变化
        if current_power_state != self.last_power_state:
            if not current_power_state:  # 停电
                self.send_bark_notification("UPS警告：检测到停电！", continuous_ring=True)
            else:  # 来电
                self.send_bark_notification("UPS通知：市电已恢复", level="active")
            
            self.last_power_state = current_power_state

        # 如果电池电量低，额外发送警告
        if status['battery_low'] and not status['ac_present']:
            self.send_bark_notification("UPS警告：电池电量低！", continuous_ring=True)

    def disconnect(self):
        if self.device:
            self.device.close()

def main():
    ups = SantakUPS()
    
    print("正在连接UPS设备...")
    if not ups.connect():
        print("无法连接到UPS设备")
        ups.send_bark_notification("UPS警告：无法连接到UPS设备！", level="critical")
        return

    print("UPS设备连接成功！开始监控...")
    
    try:
        while True:
            status = ups.read_status()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print("\n" + "="*50)
            print(f"状态更新时间: {current_time}")
            
            if status:
                print(f"市电状态: {'正常' if status['ac_present'] else '断开'}")
                print(f"电池状态: {'电量低' if status['battery_low'] else '正常'}")
                print(f"充电状态: {'正在充电' if status['charging'] else '未充电'}")
                print(f"放电状态: {'正在放电' if status['discharging'] else '未放电'}")
                print(f"负载状态: {'过载' if status['overload'] else '正常'}")
                print(f"原始数据: {status['raw_data']}")
            else:
                print("无法读取UPS状态")
            
            # 检查是否需要发送通知
            ups.check_and_notify(status)
            
            time.sleep(2)  # 每2秒更新一次
            
    except KeyboardInterrupt:
        print("\n停止监控...")
    finally:
        ups.disconnect()
        print("已断开UPS连接")

if __name__ == "__main__":
    main()
