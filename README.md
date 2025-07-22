# Zenoh Docker Simulator

Zenohを用いたネットワークシステム検証向けのDockerシミュレーション環境です。

## 概要

本シミュレータは、多数のZenohノードが通信する状況を、ローカルマシンのDockerコンテナ上で再現します。
これにより、分散アプリケーションのプロトタイピング、パフォーマンス評価、耐障害性テストなどを効率的に行うことができます。

## 主な特徴

- **設定ファイルベースの環境構築**: `config.yaml` にシミュレーションの構成（ノード数、ネットワークトポロジ、実行アプリケーションなど）を記述するだけで、環境を自動で構築します。
- **スケーラブルなシミュレーション**: 数個から数百個のノードまで、スケーラブルなシミュレーションが可能です。
- **現実的なネットワーク模倣**: コンテナ間の通信に対して、遅延やパケットロスといったネットワーク障害を擬似的に再現する機能を提供します（将来的な実装）。
- **拡張性**: 各ノードで実行するアプリケーションは自由にカスタマイズ可能であり、様々なユースケースに対応できます。

[システムデザイン](docs/SYSTEM_DESIGN.md)

## インストール

前提条件:
- Docker
- Docker Compose
- Python 3.8+
- OS: Linux, Windows

セットアップ手順:
```bash
# 1. リポジトリをクローンします
git clone <repository_url>
cd zenoh_docker_simulator

# 2. Pythonの依存関係をインストールします
pip install -r requirements.txt
```

## 使い方

1. **設定ファイルの準備**:
   `config.yaml.example` をコピーして `config.yaml` を作成し、シミュレーション内容に合わせて編集します。

   ```bash
   cp config.yaml.example config.yaml
   ```

2. **シミュレーションの実行**:
   メインスクリプトを実行すると、`config.yaml` の内容に基づいてDockerコンテナ群が起動し、シミュレーションが開始されます。

   ```bash
    # To start the simulation, first copy the example config and install dependencies:
    cp config.yaml.example config.yaml

    # (Python仮想環境を使う場合)
    python -v venv z_docker_sim
    . z_docker_sim/bin/activate
    pip install -r requirements.txt

    # Then, run the main script:
    python main.py
   ```

3. **シミュレーションの停止**:
   シミュレーションを停止し、関連するDockerリソースをクリーンアップするには、`Ctrl+C` でスクリプトを中断するか、以下のコマンドを実行します。

   ```bash
   python main.py --cleanup
   ```

## ディレクトリ構成

```
.
├── README.md
├── config.yaml.example  # 設定ファイルの見本
├── main.py              # メインスクリプト
├── requirements.txt     # Python依存パッケージ
├── docker/              # Docker関連ファイル
│   ├── Dockerfile           # アプリケーション用Dockerfile
│   └── docker-compose.yaml  # シミュレーション環境定義
└── apps/                # ノードで実行するアプリケーション
    └── ...
```

## 今後の展望

- ネットワーク障害シミュレーション機能の強化
- トラフィック収集、パフォーマンス測定ツールの追加
- リアルタイムでのシミュレーション状況可視化ツールとの連携
- 様々なアプリケーションシナリオに対応するサンプルコードの拡充

## 貢献

バグ報告、機能追加の提案、プルリクエストを歓迎します。
