# ストリームデータを受信し、通信メトリクスをCSVに保存するクライアントノード
import zenoh
import time
import os
import argparse
import pandas as pd
import psutil
from datetime import datetime

# Global list to store metrics data
metrics_data = []
start_time = None

def listener(sample):
    """Callback function to handle received data."""
    global start_time
    
    current_time = datetime.now()
    if start_time is None:
        start_time = current_time

    payload_size = len(sample.payload)
    
    # Check for end-of-stream signal (empty payload)
    if payload_size == 0:
        print("Client: End of stream signal received.")
        return

    # Get network I/O counters
    net_io = psutil.net_io_counters()
    
    metrics_data.append({
        'timestamp': current_time,
        'elapsed_time': (current_time - start_time).total_seconds(),
        'payload_size_bytes': payload_size,
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv,
        'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv,
    })
    
    # print(f"Client: Received chunk of size {payload_size} bytes.")

def save_metrics_to_csv(output_path):
    """Saves the collected metrics to a CSV file."""
    if not metrics_data:
        print("No metrics collected.")
        return
        
    df = pd.DataFrame(metrics_data)
    
    # Calculate throughput (bytes per second)
    df['recv_throughput_bps'] = df['bytes_recv'].diff().fillna(0) / df['elapsed_time'].diff().fillna(1)
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    df.to_csv(output_path, index=False)
    print(f"Client: Metrics saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Zenoh File Stream Client")
    parser.add_argument("--key", type=str, default="stream/data", help="Zenoh key to subscribe to.")
    parser.add_argument("--output", type=str, required=True, help="Path to save the metrics CSV file.")
    args = parser.parse_args()

    connect_endpoint = os.getenv("ZENOH_CONNECT", "tcp/localhost:7447")
    
    conf = zenoh.Config()
    conf.insert_json5(zenoh.config.CONNECT_KEY, f'["{connect_endpoint}"]')
    
    session = zenoh.open(conf)
    
    sub = session.declare_subscriber(args.key, listener)
    
    print(f"Client: Subscribed to key '{args.key}'. Waiting for data...")
    
    try:
        # Wait for the stream to finish. We detect this by checking for the EOS signal.
        # A more robust solution might involve a timeout or a specific control message.
        while True:
            # A simple check to see if the listener has received the EOS signal
            # In a real scenario, a more robust mechanism is needed.
            # For this simulation, we'll rely on KeyboardInterrupt to stop.
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClient: Stopping and saving metrics...")
    finally:
        save_metrics_to_csv(args.output)
        session.close()
        print("Client: Session closed.")

if __name__ == "__main__":
    main()
