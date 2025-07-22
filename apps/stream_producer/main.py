# 指定された動画ファイルなどをストリーミングするプロデューサーノード
import zenoh
import time
import os
import argparse

def stream_file(session, key, file_path, chunk_size=65536):
    """Reads a file and streams it in chunks over Zenoh."""
    try:
        with open(file_path, 'rb') as f:
            publisher = session.declare_publisher(key)
            print(f"Producer: Starting to stream file '{file_path}' on key '{key}'")
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    print("Producer: End of file reached. Stopping stream.")
                    # Send an empty message to signal the end of the stream
                    publisher.put(b'')
                    break
                publisher.put(chunk)
                # Small delay to avoid overwhelming the network
                time.sleep(0.01)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Zenoh File Stream Producer")
    parser.add_argument("--file", type=str, required=True, help="Path to the file to stream.")
    parser.add_argument("--key", type=str, default="stream/data", help="Zenoh key to publish on.")
    args = parser.parse_args()

    connect_endpoint = os.getenv("ZENOH_CONNECT", "tcp/localhost:7447")
    
    conf = zenoh.Config()
    conf.insert_json5(zenoh.config.CONNECT_KEY, f'["{connect_endpoint}"]')
    
    session = zenoh.open(conf)
    
    stream_file(session, args.key, args.file)
    
    session.close()
    print("Producer: Session closed.")

if __name__ == "__main__":
    main()
