# HalFbxExporter

## ビルド環境構築

### 入れるもの

- Visual Studio 2022
  - C++のワークロード
  - CMake 3.20以上
- FBX SDK 2020.3.4
- Python 3.11くらい
  - Pybind11

### 準備

- FBX SDKのインストール先をキャッシュ変数FBX_SDK_PATHに設定する
- Pybind11のpybind11Config.cmakeのあるディレクトリを環境変数pybind11_DIRに設定する
