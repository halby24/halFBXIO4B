# ReSaveFbx

## 概要

FBXファイルを再保存するだけのツールです。
BlenderなどでエクスポートしたFBXファイルをSDKからエクスポートしたものに置き換えたい場合などに使用します。

## 使い方

コマンドラインでツールを起動し、FBXファイルを指定してください。
ファイルは上書き保存されます。

```bash
ReSaveFbx.exe <FBXファイル>
```

## ライセンス

MIT License

このソフトウェアには一部FBX SDKのサンプルコードが含まれますが、FBX SDKのライセンスに基づき同様にMIT Licenseによって提供されます。

## ビルド方法

Windows以外は未確認です。頑張ってください。

### 用意するもの

- Visual Studio 2022
- FBX SDK 2020.3.4

### 手順

1. variables.cmake.sampleを複製し、variables.cmakeを作成します。
1. (FBX SDKを異なる場所にインストールした場合) variables.cmakeにFBX SDKのパスを記述します。
1. CMakeでビルドします。
