# シミュレータが正しく動作することを確認するための基本的なアプリケーション
import zenoh
import time
import os

def main():
    # Get Zenoh router endpoint from environment variable
    connect_endpoint = os.getenv("ZENOH_CONNECT", "tcp/localhost:7447")
    
    conf = zenoh.Config()
    conf.insert_json5(zenoh.config.CONNECT_KEY, f'["{connect_endpoint}"]')
    
    session = zenoh.open(conf)
    
    key = "sim/test"
    pub = session.declare_publisher(key)
    
    print(f"Publisher: Declared publisher for key expression '{key}'")
    
    counter = 0
    while True:
        message = f"Hello from publisher {counter}"
        pub.put(message)
        print(f"Publisher: Sent '{message}'")
        counter += 1
        time.sleep(2)

if __name__ == "__main__":
    main()
