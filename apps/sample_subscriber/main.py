# シミュレータが正しく動作することを確認するための基本的なアプリケーション
import zenoh
import time
import os

def listener(sample):
    print(f"Subscriber: Received '{sample.payload.decode('utf-8')}'")

def main():
    # Get Zenoh router endpoint from environment variable
    connect_endpoint = os.getenv("ZENOH_CONNECT", "tcp/localhost:7447")
    
    conf = zenoh.Config()
    conf.insert_json5(zenoh.config.CONNECT_KEY, f'["{connect_endpoint}"]')
    
    session = zenoh.open(conf)
    
    key = "sim/test"
    sub = session.declare_subscriber(key, listener)
    
    print(f"Subscriber: Declared subscriber for key expression '{key}'")
    
    # Keep the subscriber running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
